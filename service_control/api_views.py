"""
Views API para o app service_control
"""

from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import City, Person, PersonsAdresses, PersonsContacts, PersonType
from products.models import TemporaryProduct

from .models import ServiceOrder, ServiceOrderItem, ServiceOrderPhase
from .serializers import (
    FrontendServiceOrderUpdateSerializer,
    ServiceOrderClientSerializer,
    ServiceOrderDetailSerializer,
    ServiceOrderListByPhaseSerializer,
    ServiceOrderMarkPaidSerializer,
    ServiceOrderRefuseSerializer,
    ServiceOrderSerializer,
)


@extend_schema(
    tags=["service-orders"],
    summary="Criar ordem de serviço",
    description="Cria uma nova ordem de serviço no sistema",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "cliente_nome": {"type": "string", "description": "Nome do cliente"},
                "telefone": {"type": "string", "description": "Telefone do cliente"},
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Email do cliente (opcional)",
                },
                "cpf": {"type": "string", "description": "CPF do cliente"},
                "atendente": {"type": "string", "description": "Nome do atendente"},
                "origem": {"type": "string", "description": "Origem do pedido"},
                "data_evento": {
                    "type": "string",
                    "format": "date",
                    "description": "Data do evento",
                },
                "tipo_servico": {
                    "type": "string",
                    "description": "Tipo de serviço (Aluguel/Compra)",
                },
                "evento": {"type": "string", "description": "Tipo de evento"},
                "papel_evento": {"type": "string", "description": "Papel no evento"},
                "endereco": {
                    "type": "object",
                    "properties": {
                        "cep": {"type": "string"},
                        "rua": {"type": "string"},
                        "numero": {"type": "string"},
                        "bairro": {"type": "string"},
                        "cidade": {"type": "string"},
                    },
                },
            },
            "required": [
                "cliente_nome",
                "telefone",
                "cpf",
                "atendente",
                "origem",
                "data_evento",
                "tipo_servico",
                "evento",
                "papel_evento",
            ],
        }
    },
    responses={
        201: {
            "description": "Ordem de serviço criada com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "order_id": {"type": "integer"},
                "service_order": {"$ref": "#/components/schemas/ServiceOrder"},
            },
        },
        400: {"description": "Dados inválidos"},
        500: {"description": "Erro interno do servidor"},
    },
)
class ServiceOrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Criar nova ordem de serviço"""
        try:
            # Extrair dados da requisição
            order_data = {
                "cliente": request.data.get("cliente_nome"),
                "telefone": request.data.get("telefone"),
                "email": request.data.get("email", ""),
                "cpf": request.data.get("cpf", "").replace(".", "").replace("-", ""),
                "atendente": request.data.get("atendente"),
                "origem": request.data.get("origem"),
                "data_evento": request.data.get("data_evento"),
                "tipo_servico": request.data.get("tipo_servico"),
                "evento": request.data.get("evento"),
                "papel_evento": request.data.get("papel_evento"),
                "endereco": {
                    "cep": request.data.get("endereco", {}).get("cep"),
                    "rua": request.data.get("endereco", {}).get("rua"),
                    "numero": request.data.get("endereco", {}).get("numero"),
                    "bairro": request.data.get("endereco", {}).get("bairro"),
                    "cidade": request.data.get("endereco", {}).get("cidade"),
                },
            }

            # Validações
            if len(order_data["cpf"]) != 11:
                return Response(
                    {"error": "CPF Inválido"}, status=status.HTTP_400_BAD_REQUEST
                )

            if not all(
                [order_data["cpf"], order_data["telefone"], order_data["cliente"]]
            ):
                return Response(
                    {"error": "Dados do cliente incompletos"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Buscar ou criar cidade
            city_obj = None
            cidade_nome = order_data["endereco"].get("cidade")
            if cidade_nome:
                try:
                    city_obj = City.objects.get(name__iexact=cidade_nome.upper())
                except City.DoesNotExist:
                    return Response(
                        {"error": "Cidade não encontrada"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Buscar ou criar cliente
            pt, _ = PersonType.objects.get_or_create(type="CLIENTE")
            person, _ = Person.objects.get_or_create(
                cpf=order_data["cpf"],
                defaults={
                    "name": order_data["cliente"].upper(),
                    "person_type": pt,
                    "created_by": request.user,
                },
            )

            # Criar contato (verificando duplicatas)
            email = order_data["email"]
            telefone = order_data["telefone"]

            # Verificar se já existe outro cliente com o mesmo email
            if email:
                existing_contact_with_email = (
                    PersonsContacts.objects.filter(email=email)
                    .exclude(person=person)
                    .first()
                )

                if existing_contact_with_email:
                    return Response(
                        {"error": f"Já existe um cliente com o email '{email}'"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Verificar se já existe outro cliente com o mesmo telefone
            if telefone:
                existing_contact_with_phone = (
                    PersonsContacts.objects.filter(phone=telefone)
                    .exclude(person=person)
                    .first()
                )

                if existing_contact_with_phone:
                    return Response(
                        {"error": f"Já existe um cliente com o telefone '{telefone}'"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Se não existe duplicata, criar contato
            PersonsContacts.objects.get_or_create(
                phone=telefone,
                person=person,
                defaults={"email": email, "created_by": request.user},
            )

            # Criar endereço se cidade for informada
            if city_obj:
                PersonsAdresses.objects.get_or_create(
                    person=person,
                    street=order_data["endereco"]["rua"],
                    number=order_data["endereco"]["numero"],
                    cep=order_data["endereco"]["cep"],
                    neighborhood=order_data["endereco"]["bairro"],
                    city=city_obj,
                    defaults={"created_by": request.user},
                )

            # Buscar funcionário
            employee = Person.objects.filter(name=order_data["atendente"]).first()
            if not employee:
                return Response(
                    {"error": "Funcionário não encontrado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Buscar fase pendente
            service_order_phase = ServiceOrderPhase.objects.filter(
                name="PENDENTE"
            ).first()

            # Criar ordem de serviço
            service_order = ServiceOrder.objects.create(
                renter=person,
                employee=employee,
                attendant=request.user.person,
                order_date=timezone.now().date(),
                event_date=order_data["data_evento"],
                occasion=order_data["evento"].upper(),
                renter_role=order_data["papel_evento"].upper(),
                purchase=True if order_data["tipo_servico"] == "Compra" else False,
                came_from=order_data["origem"].upper(),
                service_order_phase=service_order_phase,
            )

            return Response(
                {
                    "success": True,
                    "message": "OS criada com sucesso",
                    "order_id": service_order.id,
                    "service_order": ServiceOrderSerializer(service_order).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao criar OS: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Atualizar ordem de serviço",
    description="Atualiza uma ordem de serviço existente com dados completos do frontend",
    request=FrontendServiceOrderUpdateSerializer,
    responses={
        200: {
            "description": "Ordem de serviço atualizada com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "service_order": {"$ref": "#/components/schemas/ServiceOrder"},
            },
        },
        404: {"description": "Ordem de serviço não encontrada"},
        500: {"description": "Erro interno do servidor"},
    },
)
class ServiceOrderUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FrontendServiceOrderUpdateSerializer

    def put(self, request, order_id):
        """Atualizar ordem de serviço com dados do frontend"""
        try:
            service_order = get_object_or_404(ServiceOrder, id=order_id)

            # Validar dados com o serializer
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            # Processar dados da ordem de serviço
            if "ordem_servico" in data:
                os_data = data["ordem_servico"]

                # Atualizar datas
                if "data_evento" in os_data:
                    service_order.event_date = os_data["data_evento"]
                if "data_retirada" in os_data:
                    service_order.retirada_date = os_data["data_retirada"]

                # Atualizar informações básicas
                if "ocasiao" in os_data:
                    service_order.occasion = os_data["ocasiao"].upper()
                if "modalidade" in os_data:
                    modalidade = os_data["modalidade"]
                    if modalidade == "Compra":
                        service_order.purchase = True
                    elif modalidade == "Aluguel":
                        service_order.purchase = False
                    elif modalidade == "Aluguel + Venda":
                        service_order.purchase = False  # Mantém como aluguel

                    # Salvar modalidade no campo específico
                    service_order.service_type = modalidade

                # Atualizar pagamento
                if "pagamento" in os_data:
                    pagamento = os_data["pagamento"]
                    if "total" in pagamento:
                        service_order.total_value = pagamento["total"]
                    if "sinal" in pagamento:
                        service_order.advance_payment = pagamento["sinal"]
                    if "restante" in pagamento:
                        service_order.remaining_payment = pagamento["restante"]

            # Processar dados do cliente
            if "cliente" in data:
                cliente_data = data["cliente"]

                # Buscar ou criar cliente
                cpf_limpo = cliente_data["cpf"].replace(".", "").replace("-", "")
                person, created = Person.objects.get_or_create(
                    cpf=cpf_limpo,
                    defaults={
                        "name": cliente_data["nome"].upper(),
                        "person_type": PersonType.objects.get_or_create(type="CLIENTE")[
                            0
                        ],
                        "created_by": request.user,
                    },
                )

                if not created:
                    # Atualizar nome se mudou
                    if person.name != cliente_data["nome"].upper():
                        person.name = cliente_data["nome"].upper()
                        person.save()

                service_order.renter = person

                # Processar contatos
                if "contatos" in cliente_data:
                    contatos = cliente_data["contatos"]
                    if contatos:
                        # Pegar apenas o último contato da lista
                        contato = contatos[-1]

                        if contato["tipo"] == "telefone":
                            # Verificar se contato já existe
                            existing_contact = PersonsContacts.objects.filter(
                                phone=contato["valor"],
                                person=person,
                            ).first()

                            # Só criar se não existir
                            if not existing_contact:
                                # Remover contatos antigos do cliente
                                PersonsContacts.objects.filter(person=person).delete()

                                # Criar novo contato
                                PersonsContacts.objects.create(
                                    phone=contato["valor"],
                                    person=person,
                                    created_by=request.user,
                                )

                # Processar endereços
                if "enderecos" in cliente_data:
                    # Manter apenas o endereço mais recente (último da lista)
                    enderecos = cliente_data["enderecos"]
                    if enderecos:
                        # Pegar apenas o último endereço da lista
                        endereco = enderecos[-1]

                        # Buscar cidade
                        city, _ = City.objects.get_or_create(
                            name=endereco["cidade"].upper(),
                            defaults={
                                "code": "00000",
                                "uf": "SP",
                                "created_by": request.user,
                            },
                        )

                        # Verificar se endereço já existe
                        existing_address = PersonsAdresses.objects.filter(
                            person=person,
                            street=endereco["rua"],
                            number=endereco["numero"],
                            cep=endereco["cep"],
                            neighborhood=endereco["bairro"],
                            city=city,
                        ).first()

                        # Só criar se não existir
                        if not existing_address:
                            # Remover endereços antigos do cliente
                            PersonsAdresses.objects.filter(person=person).delete()

                            # Criar novo endereço
                            PersonsAdresses.objects.create(
                                person=person,
                                street=endereco["rua"],
                                number=endereco["numero"],
                                cep=endereco["cep"],
                                neighborhood=endereco["bairro"],
                                city=city,
                                created_by=request.user,
                            )

            # Remover itens existentes
            service_order.items.all().delete()

            # Processar itens (roupas)
            if "ordem_servico" in data and "itens" in data["ordem_servico"]:
                for item in data["ordem_servico"]["itens"]:
                    # Tratar campos vazios convertendo para None
                    def clean_field(value):
                        return value if value and value.strip() else None

                    temp_product = TemporaryProduct.objects.create(
                        product_type=item["tipo"],
                        size=clean_field(item.get("numero")),
                        sleeve_length=clean_field(item.get("manga")),
                        color=clean_field(item.get("cor")),
                        brand=clean_field(item.get("marca")),
                        description=clean_field(item.get("extras")),
                        venda=item.get("venda", False),
                        created_by=request.user,
                    )

                    # Criar item da OS
                    ServiceOrderItem.objects.create(
                        service_order=service_order,
                        temporary_product=temp_product,
                        adjustment_needed=bool(clean_field(item.get("ajuste"))),
                        adjustment_notes=clean_field(item.get("ajuste")),
                        created_by=request.user,
                    )

            # Processar acessórios
            if "ordem_servico" in data and "acessorios" in data["ordem_servico"]:
                for acessorio in data["ordem_servico"]["acessorios"]:
                    # Tratar campos vazios convertendo para None
                    def clean_field(value):
                        return value if value and value.strip() else None

                    temp_product = TemporaryProduct.objects.create(
                        product_type=acessorio["tipo"],
                        color=clean_field(acessorio.get("cor")),
                        brand=clean_field(acessorio.get("marca")),
                        description=clean_field(acessorio.get("descricao")),
                        extensor=acessorio.get("extensor", False),
                        venda=acessorio.get("venda", False),
                        created_by=request.user,
                    )

                    # Criar item da OS
                    ServiceOrderItem.objects.create(
                        service_order=service_order,
                        temporary_product=temp_product,
                        created_by=request.user,
                    )

            service_order.save()
            service_order.update(request.user)

            return Response(
                {
                    "success": True,
                    "message": "OS atualizada com sucesso",
                    "service_order": ServiceOrderSerializer(service_order).data,
                }
            )

        except ServiceOrder.DoesNotExist:
            return Response(
                {"error": "Ordem de serviço não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao atualizar OS: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Lista de ordens de serviço",
    description="Retorna a lista de ordens de serviço com filtros opcionais",
    parameters=[
        OpenApiParameter(
            name="phase",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filtrar por fase da ordem de serviço",
            required=False,
        )
    ],
    responses={200: ServiceOrderSerializer(many=True)},
)
class ServiceOrderListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderSerializer

    def get_queryset(self):
        queryset = ServiceOrder.objects.select_related(
            "renter", "employee", "attendant", "service_order_phase"
        ).prefetch_related("items")

        # Filtros
        phase = self.request.GET.get("phase")
        if phase:
            queryset = queryset.filter(service_order_phase__name__icontains=phase)

        return queryset


@extend_schema(
    tags=["service-orders"],
    summary="Detalhes da ordem de serviço",
    description="Retorna os detalhes completos de uma ordem de serviço",
    responses={
        200: ServiceOrderSerializer,
        404: {"description": "Ordem de serviço não encontrada"},
    },
)
class ServiceOrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderDetailSerializer

    def get(self, request, order_id):
        """Detalhes de uma ordem de serviço"""
        try:
            service_order = (
                ServiceOrder.objects.select_related(
                    "renter", "employee", "attendant", "service_order_phase"
                )
                .prefetch_related("items")
                .get(id=order_id)
            )

            return Response(ServiceOrderSerializer(service_order).data)

        except ServiceOrder.DoesNotExist:
            return Response(
                {"error": "Ordem de serviço não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Marcar ordem de serviço como paga",
    description="Marca uma ordem de serviço como paga, alterando sua fase",
    responses={
        200: {
            "description": "Ordem de serviço marcada como paga",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
            },
        },
        404: {"description": "Ordem de serviço não encontrada"},
    },
)
class ServiceOrderMarkPaidAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderMarkPaidSerializer

    def post(self, request, order_id):
        """Marcar ordem de serviço como paga"""
        try:
            service_order = get_object_or_404(ServiceOrder, id=order_id)

            # Buscar fase "AGUARDANDO PAGAMENTO"
            paid_phase = ServiceOrderPhase.objects.filter(
                name="AGUARDANDO PAGAMENTO"
            ).first()
            if paid_phase:
                service_order.service_order_phase = paid_phase
                service_order.save()

            return Response({"success": True, "message": "OS marcada como paga"})

        except ServiceOrder.DoesNotExist:
            return Response(
                {"error": "Ordem de serviço não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Recusar ordem de serviço",
    description="Recusa uma ordem de serviço, alterando sua fase para RECUSADA",
    responses={
        200: {
            "description": "Ordem de serviço recusada",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
            },
        },
        404: {"description": "Ordem de serviço não encontrada"},
    },
)
class ServiceOrderRefuseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderRefuseSerializer

    def post(self, request, order_id):
        """Recusar ordem de serviço"""
        try:
            service_order = get_object_or_404(ServiceOrder, id=order_id)
            justification = request.data.get("justification", "").strip()

            # Justificativa obrigatória
            if not justification:
                return Response(
                    {"error": "Justificativa é obrigatória para recusa."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Buscar fase "RECUSADA"
            refused_phase = ServiceOrderPhase.objects.filter(name="RECUSADA").first()
            if not refused_phase:
                return Response(
                    {"error": "Fase 'RECUSADA' não encontrada."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Permissão: só atendente responsável ou administrador pode recusar OS pendente
            user_person = getattr(request.user, "person", None)
            is_admin = user_person and user_person.person_type.type == "ADMINISTRADOR"
            is_employee = (
                user_person
                and service_order.employee
                and user_person.id == service_order.employee.id
            )
            is_pending = (
                service_order.service_order_phase
                and service_order.service_order_phase.name == "PENDENTE"
            )
            if is_pending and not (is_admin or is_employee):
                return Response(
                    {
                        "error": "Apenas o atendente responsável ou um administrador pode recusar uma OS pendente."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Recusar OS
            service_order.service_order_phase = refused_phase
            service_order.justification_refusal = justification
            service_order.save()

            return Response({"success": True, "message": "OS recusada"})

        except ServiceOrder.DoesNotExist:
            return Response(
                {"error": "Ordem de serviço não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao recusar OS: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Dashboard de ordens de serviço",
    description="Retorna métricas e estatísticas das ordens de serviço",
    responses={
        200: {
            "description": "Métricas das ordens de serviço",
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "object",
                    "properties": {
                        "pendentes": {"type": "integer"},
                        "aguardando_pagamento": {"type": "integer"},
                        "concluidas": {"type": "integer"},
                        "em_atraso": {"type": "integer"},
                        "recusadas": {"type": "integer"},
                    },
                },
                "em_atraso": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
                "hoje": {"type": "object", "additionalProperties": {"type": "integer"}},
                "proximos_10_dias": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
            },
        },
        500: {"description": "Erro interno do servidor"},
    },
)
class ServiceOrderDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Dashboard com métricas das ordens de serviço"""
        try:
            # Executar função de avanço de fases
            from .views import advance_service_order_phases

            advance_service_order_phases()

            # Buscar fases
            pending_phase = ServiceOrderPhase.objects.filter(name="PENDENTE").first()
            awaiting_payment_phase = ServiceOrderPhase.objects.filter(
                name="AGUARDANDO PAGAMENTO"
            ).first()
            finished_phase = ServiceOrderPhase.objects.filter(name="CONCLUÍDO").first()
            overdue_phase = ServiceOrderPhase.objects.filter(name="EM ATRASO").first()
            refused_phase = ServiceOrderPhase.objects.filter(name="RECUSADA").first()

            # Métricas por fase
            metrics = {
                "pendentes": (
                    ServiceOrder.objects.filter(
                        service_order_phase=pending_phase
                    ).count()
                    if pending_phase
                    else 0
                ),
                "aguardando_pagamento": (
                    ServiceOrder.objects.filter(
                        service_order_phase=awaiting_payment_phase
                    ).count()
                    if awaiting_payment_phase
                    else 0
                ),
                "concluidas": (
                    ServiceOrder.objects.filter(
                        service_order_phase=finished_phase
                    ).count()
                    if finished_phase
                    else 0
                ),
                "em_atraso": (
                    ServiceOrder.objects.filter(
                        service_order_phase=overdue_phase
                    ).count()
                    if overdue_phase
                    else 0
                ),
                "recusadas": (
                    ServiceOrder.objects.filter(
                        service_order_phase=refused_phase
                    ).count()
                    if refused_phase
                    else 0
                ),
            }

            # OS em atraso
            em_atraso = {}
            if overdue_phase:
                overdue_orders = ServiceOrder.objects.filter(
                    service_order_phase=overdue_phase
                )
                for order in overdue_orders:
                    tipo = order.tipo_evento()
                    em_atraso[tipo] = em_atraso.get(tipo, 0) + 1

            # OS de hoje
            hoje = {}
            today = timezone.now().date()
            today_orders = (
                ServiceOrder.objects.filter(prova_date=today)
                | ServiceOrder.objects.filter(retirada_date=today)
                | ServiceOrder.objects.filter(devolucao_date=today)
            )
            for order in today_orders:
                if (
                    order.service_order_phase
                    and order.service_order_phase.name not in ["CONCLUÍDO", "RECUSADA"]
                ):
                    tipo = order.tipo_evento()
                    hoje[tipo] = hoje.get(tipo, 0) + 1

            # OS próximos 10 dias
            proximos_10_dias = {}
            in_10_days = today + timedelta(days=10)
            upcoming_orders = ServiceOrder.objects.filter(
                devolucao_date__gt=today, devolucao_date__lte=in_10_days
            )
            for order in upcoming_orders:
                if (
                    order.service_order_phase
                    and order.service_order_phase.name not in ["CONCLUÍDO", "RECUSADA"]
                ):
                    tipo = order.tipo_evento()
                    proximos_10_dias[tipo] = proximos_10_dias.get(tipo, 0) + 1

            return Response(
                {
                    "metrics": metrics,
                    "em_atraso": em_atraso,
                    "hoje": hoje,
                    "proximos_10_dias": proximos_10_dias,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao gerar dashboard: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Listar ordens de serviço por fase",
    description="Retorna a lista de ordens de serviço filtradas por fase específica com dados completos do cliente",
    responses={
        200: ServiceOrderListByPhaseSerializer(many=True),
        404: {"description": "Fase não encontrada"},
        500: {"description": "Erro interno do servidor"},
    },
)
class ServiceOrderListByPhaseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderListByPhaseSerializer

    def get(self, request, phase_name):
        """Listar ordens de serviço por fase com dados completos do cliente"""
        try:
            phase = ServiceOrderPhase.objects.filter(name__icontains=phase_name).first()
            if not phase:
                return Response(
                    {"error": "Fase não encontrada"}, status=status.HTTP_404_NOT_FOUND
                )

            orders = ServiceOrder.objects.filter(
                service_order_phase=phase
            ).select_related("renter", "employee", "attendant", "renter__person_type")

            data = []
            for order in orders:
                # Dados do cliente
                client_data = {
                    "id": order.renter.id,
                    "name": order.renter.name,
                    "cpf": order.renter.cpf,
                    "person_type": (
                        {
                            "id": order.renter.person_type.id,
                            "type": order.renter.person_type.type,
                        }
                        if order.renter.person_type
                        else None
                    ),
                }

                # Contatos do cliente (apenas o mais recente)
                contact = order.renter.contacts.order_by("-date_created").first()
                client_data["contacts"] = []
                if contact:
                    client_data["contacts"].append(
                        {
                            "id": contact.id,
                            "email": contact.email,
                            "phone": contact.phone,
                        }
                    )

                # Endereços do cliente (apenas o mais recente)
                address = order.renter.personsadresses_set.order_by(
                    "-date_created"
                ).first()
                client_data["addresses"] = []
                if address:
                    city_data = None
                    if address.city:
                        city_data = {
                            "id": address.city.id,
                            "name": address.city.name,
                            "uf": address.city.uf,
                        }

                    client_data["addresses"].append(
                        {
                            "id": address.id,
                            "cep": address.cep,
                            "rua": address.street,
                            "numero": address.number,
                            "bairro": address.neighborhood,
                            "cidade": city_data,
                        }
                    )

                # Dados da OS
                order_data = {
                    "id": order.id,
                    "event_date": order.event_date,
                    "occasion": order.occasion,
                    "total_value": order.total_value,
                    "advance_payment": order.advance_payment,
                    "remaining_payment": order.remaining_payment,
                    "employee_name": order.employee.name if order.employee else "",
                    "attendant_name": order.attendant.name if order.attendant else "",
                    "order_date": order.order_date,
                    "prova_date": order.prova_date,
                    "retirada_date": order.retirada_date,
                    "devolucao_date": order.devolucao_date,
                    "client": client_data,
                }

                data.append(order_data)

            return Response(data)

        except Exception as e:
            return Response(
                {"error": f"Erro ao listar OS: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Dados do cliente da ordem de serviço",
    description="Retorna os dados completos do cliente de uma ordem de serviço",
    responses={
        200: ServiceOrderClientSerializer,
        404: {"description": "Ordem de serviço não encontrada"},
    },
)
class ServiceOrderClientAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderClientSerializer

    def get(self, request, order_id):
        """Buscar dados do cliente de uma ordem de serviço"""
        try:
            service_order = get_object_or_404(ServiceOrder, id=order_id)
            person = service_order.renter

            # Buscar contato mais recente baseado em date_created
            contact = person.contacts.order_by("-date_created").first()

            # Buscar endereço mais recente baseado em date_created
            address = person.personsadresses_set.order_by("-date_created").first()

            data = {
                "id": person.id,
                "name": person.name,
                "cpf": person.cpf,
                "email": contact.email if contact else "",
                "phone": contact.phone if contact else "",
                "address": (
                    {
                        "street": address.street if address else "",
                        "number": address.number if address else "",
                        "neighborhood": address.neighborhood if address else "",
                        "city": address.city.name if address else "",
                        "cep": address.cep if address else "",
                    }
                    if address
                    else None
                ),
            }

            return Response(data)

        except ServiceOrder.DoesNotExist:
            return Response(
                {"error": "Ordem de serviço não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Triagem/Pré-OS (criação por recepção)",
    description="Permite que um usuário do tipo RECEPÇÃO crie uma pré-ordem de serviço (OS) pendente, associando um atendente responsável.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "cliente_nome": {"type": "string", "description": "Nome do cliente"},
                "telefone": {"type": "string", "description": "Telefone do cliente"},
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Email do cliente (opcional)",
                },
                "cpf": {"type": "string", "description": "CPF do cliente"},
                "atendente_id": {
                    "type": "integer",
                    "description": "ID do atendente responsável",
                },
                "origem": {"type": "string", "description": "Origem do pedido"},
                "data_evento": {
                    "type": "string",
                    "format": "date",
                    "description": "Data do evento",
                },
                "tipo_servico": {
                    "type": "string",
                    "description": "Tipo de serviço (Aluguel/Compra)",
                },
                "evento": {"type": "string", "description": "Tipo de evento"},
                "papel_evento": {"type": "string", "description": "Papel no evento"},
                "endereco": {
                    "type": "object",
                    "properties": {
                        "cep": {"type": "string"},
                        "rua": {"type": "string"},
                        "numero": {"type": "string"},
                        "bairro": {"type": "string"},
                        "cidade": {"type": "string"},
                    },
                },
            },
            "required": [
                "cliente_nome",
                "telefone",
                "cpf",
                "atendente_id",
                "origem",
                "data_evento",
                "tipo_servico",
                "evento",
                "papel_evento",
            ],
        }
    },
    responses={
        201: {
            "description": "Pré-ordem de serviço criada com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "order_id": {"type": "integer"},
                "service_order": {"$ref": "#/components/schemas/ServiceOrder"},
            },
        },
        400: {"description": "Dados inválidos"},
        403: {"description": "Permissão negada"},
        500: {"description": "Erro interno do servidor"},
    },
)
class ServiceOrderPreTriageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Criação de pré-ordem de serviço pela recepção ou administrador"""
        try:
            # Verifica se o usuário é do tipo RECEPÇÃO ou ADMINISTRADOR
            if not hasattr(
                request.user, "person"
            ) or request.user.person.person_type.type not in [
                "RECEPÇÃO",
                "ADMINISTRADOR",
            ]:
                return Response(
                    {
                        "error": "Apenas usuários do tipo RECEPÇÃO ou ADMINISTRADOR podem criar pré-OS."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            data = request.data
            cpf = data.get("cpf", "").replace(".", "").replace("-", "")
            if len(cpf) != 11:
                return Response(
                    {"error": "CPF inválido."}, status=status.HTTP_400_BAD_REQUEST
                )

            # Buscar ou criar cliente
            pt, _ = PersonType.objects.get_or_create(type="CLIENTE")
            person, _ = Person.objects.get_or_create(
                cpf=cpf,
                defaults={
                    "name": data.get("cliente_nome", "").upper(),
                    "person_type": pt,
                    "created_by": request.user,
                },
            )
            # Criar contato se não existir (verificando duplicatas)
            email = data.get("email", "")
            telefone = data.get("telefone")

            # Verificar se já existe outro cliente com o mesmo email
            if email:
                existing_contact_with_email = (
                    PersonsContacts.objects.filter(email=email)
                    .exclude(person=person)
                    .first()
                )

                if existing_contact_with_email:
                    return Response(
                        {"error": f"Já existe um cliente com o email '{email}'"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Verificar se já existe outro cliente com o mesmo telefone
            if telefone:
                existing_contact_with_phone = (
                    PersonsContacts.objects.filter(phone=telefone)
                    .exclude(person=person)
                    .first()
                )

                if existing_contact_with_phone:
                    return Response(
                        {"error": f"Já existe um cliente com o telefone '{telefone}'"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Se não existe duplicata, criar contato
            PersonsContacts.objects.get_or_create(
                phone=telefone,
                person=person,
                defaults={"email": email, "created_by": request.user},
            )
            # Criar endereço se cidade for informada
            endereco = data.get("endereco", {})
            cidade_nome = endereco.get("cidade")
            if cidade_nome:
                city_obj = City.objects.filter(name__iexact=cidade_nome.upper()).first()
                if city_obj:
                    PersonsAdresses.objects.get_or_create(
                        person=person,
                        street=endereco.get("rua"),
                        number=endereco.get("numero"),
                        cep=endereco.get("cep"),
                        neighborhood=endereco.get("bairro"),
                        city=city_obj,
                        defaults={"created_by": request.user},
                    )
            # Buscar atendente
            atendente_id = data.get("atendente_id")
            atendente = Person.objects.filter(
                id=atendente_id, person_type__type="ATENDENTE"
            ).first()
            if not atendente:
                return Response(
                    {"error": "Atendente não encontrado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Buscar fase pendente
            service_order_phase = ServiceOrderPhase.objects.filter(
                name="PENDENTE"
            ).first()
            # Criar pré-ordem de serviço
            service_order = ServiceOrder.objects.create(
                renter=person,
                employee=atendente,
                attendant=request.user.person,
                order_date=timezone.now().date(),
                event_date=data.get("data_evento"),
                occasion=data.get("evento", "").upper(),
                renter_role=data.get("papel_evento", "").upper(),
                purchase=True if data.get("tipo_servico") == "Compra" else False,
                came_from=data.get("origem", "").upper(),
                service_order_phase=service_order_phase,
            )
            return Response(
                {
                    "success": True,
                    "message": "Pré-OS criada com sucesso",
                    "order_id": service_order.id,
                    "service_order": ServiceOrderSerializer(service_order).data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao criar pré-OS: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

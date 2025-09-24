"""
Views API para o app service_control
"""

from datetime import date, timedelta

from django.db import models
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

from .models import (
    Event,
    EventParticipant,
    ServiceOrder,
    ServiceOrderItem,
    ServiceOrderPhase,
)
from .serializers import (
    EventAddParticipantsSerializer,
    EventCreateSerializer,
    EventLinkServiceOrderSerializer,
    EventSerializer,
    EventStatusSerializer,
    FrontendServiceOrderUpdateSerializer,
    ServiceOrderClientSerializer,
    ServiceOrderDashboardResponseSerializer,
    ServiceOrderDetailSerializer,
    ServiceOrderListByPhaseSerializer,
    ServiceOrderMarkPaidSerializer,
    ServiceOrderMarkRetrievedSerializer,
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
            email = order_data.get("email", "").strip()
            telefone = order_data["telefone"]

            # Tratar email vazio como None para evitar constraint unique
            if not email:
                email = None

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
                order_date=date.today(),
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
                if "data_devolucao" in os_data:
                    service_order.devolucao_date = os_data["data_devolucao"]

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
                        """Limpa campos vazios convertendo para None"""
                        if value is None:
                            return None
                        if isinstance(value, str):
                            cleaned = value.strip() if value.strip() else None
                            return cleaned
                        return value

                    # Criar produto temporário com campos básicos
                    numero_value = clean_field(item.get("numero"))
                    print(
                        f"DEBUG ITEM: Criando produto temporário - tipo: {item['tipo']}, numero: '{item.get('numero')}' -> limpo: '{numero_value}'"
                    )

                    temp_product = TemporaryProduct.objects.create(
                        product_type=item["tipo"],
                        size=numero_value,  # ✅ Campo "numero" mapeia para "size" no banco
                        sleeve_length=clean_field(item.get("manga")),
                        color=clean_field(item.get("cor")),
                        brand=clean_field(item.get("marca")),
                        description=clean_field(item.get("extras")),
                        venda=item.get("venda", False),
                        created_by=request.user,
                    )

                    print(
                        f"DEBUG ITEM: Produto temporário criado com ID: {temp_product.id}, size salvo: '{temp_product.size}'"
                    )

                    # Campos específicos para calça
                    if item["tipo"] == "calca":
                        temp_product.waist_size = clean_field(item.get("cintura"))
                        temp_product.leg_length = clean_field(item.get("perna"))
                        temp_product.ajuste_cintura = clean_field(
                            item.get("ajuste_cintura")
                        )
                        temp_product.ajuste_comprimento = clean_field(
                            item.get("ajuste_comprimento")
                        )
                        temp_product.save()

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
                        """Limpa campos vazios convertendo para None"""
                        if value is None:
                            return None
                        if isinstance(value, str):
                            cleaned = value.strip() if value.strip() else None
                            return cleaned
                        return value

                    numero_value = clean_field(acessorio.get("numero"))
                    print(
                        f"DEBUG ACESSORIO: Criando produto temporário - tipo: {acessorio['tipo']}, numero: '{acessorio.get('numero')}' -> limpo: '{numero_value}'"
                    )

                    temp_product = TemporaryProduct.objects.create(
                        product_type=acessorio["tipo"],
                        size=numero_value,  # ✅ Campo "numero" mapeia para "size" no banco
                        color=clean_field(acessorio.get("cor")),
                        brand=clean_field(acessorio.get("marca")),
                        description=clean_field(acessorio.get("descricao")),
                        extensor=acessorio.get("extensor", False),
                        venda=acessorio.get("venda", False),
                        created_by=request.user,
                    )

                    print(
                        f"DEBUG ACESSORIO: Produto temporário criado com ID: {temp_product.id}, size salvo: '{temp_product.size}'"
                    )

                    # Criar item da OS
                    ServiceOrderItem.objects.create(
                        service_order=service_order,
                        temporary_product=temp_product,
                        created_by=request.user,
                    )

            service_order.save()

            # Mover automaticamente para AGUARDANDO_RETIRADA após atualização
            aguardando_retirada_phase = ServiceOrderPhase.objects.filter(
                name="AGUARDANDO_RETIRADA"
            ).first()

            if aguardando_retirada_phase and service_order.service_order_phase:
                # Só mover se não estiver já em AGUARDANDO_RETIRADA ou fases finais
                current_phase_name = service_order.service_order_phase.name
                if current_phase_name not in [
                    "AGUARDANDO_RETIRADA",
                    "AGUARDANDO_DEVOLUCAO",
                    "FINALIZADO",
                    "RECUSADA",
                ]:
                    service_order.service_order_phase = aguardando_retirada_phase
                    service_order.save()
                    print(
                        f"OS {service_order.id} movida automaticamente para AGUARDANDO_RETIRADA após atualização"
                    )

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
    description="Marca uma ordem de serviço como paga, alterando sua fase para FINALIZADO e registrando a data de devolução",
    responses={
        200: {
            "description": "Ordem de serviço marcada como paga e finalizada",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "data_devolvido": {"type": "string", "format": "date-time"},
            },
        },
        404: {"description": "Ordem de serviço não encontrada"},
        400: {"description": "OS não pode ser marcada como paga"},
        500: {"description": "Erro interno do servidor"},
    },
)
class ServiceOrderMarkPaidAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderMarkPaidSerializer

    def post(self, request, order_id):
        """Marcar ordem de serviço como paga e concluída"""
        try:
            service_order = get_object_or_404(ServiceOrder, id=order_id)

            # Verificar se a OS pode ser marcada como paga
            if not service_order.service_order_phase:
                return Response(
                    {"error": "OS não possui fase definida."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verificar se já está finalizada
            if service_order.service_order_phase.name == "FINALIZADO":
                return Response(
                    {"error": "OS já está finalizada."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verificar se está na fase AGUARDANDO_DEVOLUCAO
            if service_order.service_order_phase.name != "AGUARDANDO_DEVOLUCAO":
                return Response(
                    {
                        "error": "OS deve estar na fase AGUARDANDO_DEVOLUCAO para ser marcada como paga."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Buscar ou criar fase "FINALIZADO"
            finalizado_phase, created = ServiceOrderPhase.objects.get_or_create(
                name="FINALIZADO", defaults={"created_by": request.user}
            )

            # Verificar permissões
            user_person = getattr(request.user, "person", None)
            is_admin = user_person and user_person.person_type.type == "ADMINISTRADOR"
            is_employee = (
                user_person
                and service_order.employee
                and user_person.id == service_order.employee.id
            )
            is_attendant = (
                user_person
                and service_order.attendant
                and user_person.id == service_order.attendant.id
            )

            if not (is_admin or is_employee or is_attendant):
                return Response(
                    {
                        "error": "Apenas o atendente responsável, recepcionista ou um administrador pode marcar uma OS como paga."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Marcar como paga e finalizada
            service_order.service_order_phase = finalizado_phase
            service_order.data_devolvido = timezone.now()
            service_order.save()

            return Response(
                {
                    "success": True,
                    "message": "OS marcada como paga e finalizada com sucesso",
                    "data_devolvido": service_order.data_devolvido,
                }
            )

        except ServiceOrder.DoesNotExist:
            return Response(
                {"error": "Ordem de serviço não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao marcar OS como paga: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Recusar ordem de serviço",
    description="Recusa uma ordem de serviço, alterando sua fase para RECUSADA. Apenas OS nas fases PENDENTE ou AGUARDANDO_RETIRADA, ou OS sem fase definida (recusadas na triagem) podem ser recusadas. Requer justificativa obrigatória.",
    responses={
        200: {
            "description": "Ordem de serviço recusada",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
            },
        },
        400: {
            "description": "OS não pode ser recusada na fase atual ou justificativa não fornecida"
        },
        403: {
            "description": "Permissão negada - apenas atendente responsável, administrador ou usuários de triagem"
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
            justification = request.data.get("justification_refusal", "").strip()

            # Justificativa obrigatória
            if not justification:
                return Response(
                    {"error": "Justificativa é obrigatória para recusa."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Buscar ou criar fase "RECUSADA"
            refused_phase, created = ServiceOrderPhase.objects.get_or_create(
                name="RECUSADA", defaults={"created_by": request.user}
            )

            # Verificar se a OS pode ser recusada
            current_phase = service_order.service_order_phase
            allowed_phases = ["PENDENTE", "AGUARDANDO_RETIRADA"]

            # Permitir recusar OS sem fase (caso de OS recusadas na triagem)
            if current_phase and current_phase.name not in allowed_phases:
                return Response(
                    {
                        "error": f"OS não pode ser recusada na fase atual ({current_phase.name}). Apenas fases {', '.join(allowed_phases)} ou OS sem fase definida podem ser recusadas."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Permissão: só atendente responsável ou administrador pode recusar OS
            user_person = getattr(request.user, "person", None)
            is_admin = user_person and user_person.person_type.type == "ADMINISTRADOR"
            is_employee = (
                user_person
                and service_order.employee
                and user_person.id == service_order.employee.id
            )

            # Permitir recusar se for admin OU se for atendente responsável OU se a OS não tem atendente (caso de triagem)
            if not (is_admin or is_employee or not service_order.employee):
                return Response(
                    {
                        "error": "Apenas o atendente responsável, um administrador, ou usuários autorizados para triagem podem recusar uma OS."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Recusar OS
            service_order.service_order_phase = refused_phase
            service_order.justification_refusal = justification
            service_order.cancel(request.user)  # Atualiza date_canceled e canceled_by

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
    summary="Marcar ordem de serviço como retirada",
    description="Marca uma ordem de serviço como retirada, alterando sua fase para AGUARDANDO_DEVOLUCAO e registrando a data de retirada",
    responses={
        200: {
            "description": "Ordem de serviço marcada como retirada",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
            },
        },
        404: {"description": "Ordem de serviço não encontrada"},
        400: {"description": "OS não pode ser marcada como retirada"},
        500: {"description": "Erro interno do servidor"},
    },
)
class ServiceOrderMarkRetrievedAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderMarkRetrievedSerializer

    def post(self, request, order_id):
        """Marcar ordem de serviço como retirada"""
        try:
            service_order = get_object_or_404(ServiceOrder, id=order_id)

            # Verificar se a OS pode ser marcada como retirada
            if not service_order.service_order_phase:
                return Response(
                    {"error": "OS não possui fase definida."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verificar se já está na fase AGUARDANDO_DEVOLUCAO
            if service_order.service_order_phase.name == "AGUARDANDO_DEVOLUCAO":
                return Response(
                    {"error": "OS já está aguardando devolução."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verificar se já está finalizada
            if service_order.service_order_phase.name == "FINALIZADO":
                return Response(
                    {"error": "OS já está finalizada."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verificar se está na fase AGUARDANDO_RETIRADA
            if service_order.service_order_phase.name != "AGUARDANDO_RETIRADA":
                return Response(
                    {
                        "error": "OS deve estar na fase AGUARDANDO_RETIRADA para ser marcada como retirada."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Buscar ou criar fase "AGUARDANDO_DEVOLUCAO"
            aguardando_devolucao_phase, created = (
                ServiceOrderPhase.objects.get_or_create(
                    name="AGUARDANDO_DEVOLUCAO", defaults={"created_by": request.user}
                )
            )

            # Verificar permissões
            user_person = getattr(request.user, "person", None)
            is_admin = user_person and user_person.person_type.type == "ADMINISTRADOR"
            is_employee = (
                user_person
                and service_order.employee
                and user_person.id == service_order.employee.id
            )
            is_attendant = (
                user_person
                and service_order.attendant
                and user_person.id == service_order.attendant.id
            )

            if not (is_admin or is_employee or is_attendant):
                return Response(
                    {
                        "error": "Apenas o atendente responsável, recepcionista ou um administrador pode marcar uma OS como retirada."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Marcar como retirada
            service_order.service_order_phase = aguardando_devolucao_phase
            service_order.data_retirado = timezone.now()
            service_order.save()

            return Response(
                {
                    "success": True,
                    "message": "OS marcada como retirada com sucesso",
                    "data_retirado": service_order.data_retirado,
                }
            )

        except ServiceOrder.DoesNotExist:
            return Response(
                {"error": "Ordem de serviço não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao marcar OS como retirada: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["service-orders"],
    summary="Dashboard de ordens de serviço",
    description="Retorna métricas e estatísticas das ordens de serviço com status e resultados financeiros",
    responses={
        200: ServiceOrderDashboardResponseSerializer,
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
            refused_phase = ServiceOrderPhase.objects.filter(name="RECUSADA").first()
            # aguardando_retirada_phase = ServiceOrderPhase.objects.filter(
            #     name="AGUARDANDO_RETIRADA"
            # ).first()
            # aguardando_devolucao_phase = ServiceOrderPhase.objects.filter(
            #     name="AGUARDANDO_DEVOLUCAO"
            # ).first()
            finished_phase = ServiceOrderPhase.objects.filter(name="FINALIZADO").first()

            today = date.today()
            in_10_days = today + timedelta(days=10)

            # Status - Contadores por tipo e período
            status = {
                "em_atraso": {"provas": 0, "retiradas": 0, "devolucoes": 0},
                "hoje": {"provas": 0, "retiradas": 0, "devolucoes": 0},
                "proximos_10_dias": {"provas": 0, "retiradas": 0, "devolucoes": 0},
            }

            # OS em atraso (RECUSADA)
            if refused_phase:
                status["em_atraso"]["provas"] = ServiceOrder.objects.filter(
                    service_order_phase=refused_phase, order_date__isnull=False
                ).count()

                status["em_atraso"]["retiradas"] = ServiceOrder.objects.filter(
                    service_order_phase=refused_phase, retirada_date__isnull=False
                ).count()

                status["em_atraso"]["devolucoes"] = ServiceOrder.objects.filter(
                    service_order_phase=refused_phase, devolucao_date__isnull=False
                ).count()

            # OS de hoje
            status["hoje"]["provas"] = ServiceOrder.objects.filter(
                order_date=today,
                service_order_phase__name__in=[
                    "PENDENTE",
                    "AGUARDANDO_RETIRADA",
                    "AGUARDANDO_DEVOLUCAO",
                ],
            ).count()

            status["hoje"]["retiradas"] = ServiceOrder.objects.filter(
                retirada_date=today,
                service_order_phase__name__in=[
                    "PENDENTE",
                    "AGUARDANDO_RETIRADA",
                    "AGUARDANDO_DEVOLUCAO",
                ],
            ).count()

            status["hoje"]["devolucoes"] = ServiceOrder.objects.filter(
                devolucao_date=today,
                service_order_phase__name__in=[
                    "PENDENTE",
                    "AGUARDANDO_RETIRADA",
                    "AGUARDANDO_DEVOLUCAO",
                ],
            ).count()

            # OS próximos 10 dias
            # Contar provas
            provas_proximas = ServiceOrder.objects.filter(
                order_date__gt=today,
                order_date__lte=in_10_days,
                service_order_phase__name__in=[
                    "PENDENTE",
                    "AGUARDANDO_RETIRADA",
                    "AGUARDANDO_DEVOLUCAO",
                ],
            ).count()

            # Contar retiradas
            retiradas_proximas = ServiceOrder.objects.filter(
                order_date__gt=today,
                order_date__lte=in_10_days,
                service_order_phase__name__in=[
                    "PENDENTE",
                    "AGUARDANDO_RETIRADA",
                    "AGUARDANDO_DEVOLUCAO",
                ],
            ).count()

            # Contar devoluções
            devolucoes_proximas = ServiceOrder.objects.filter(
                devolucao_date__gt=today,
                devolucao_date__lte=in_10_days,
                service_order_phase__name__in=[
                    "PENDENTE",
                    "AGUARDANDO_RETIRADA",
                    "AGUARDANDO_DEVOLUCAO",
                ],
            ).count()

            status["proximos_10_dias"]["provas"] = provas_proximas
            status["proximos_10_dias"]["retiradas"] = retiradas_proximas
            status["proximos_10_dias"]["devolucoes"] = devolucoes_proximas

            # Resultados financeiros
            resultados = {
                "dia": {
                    "total_pedidos": 0.00,
                    "total_recebido": 0.00,
                    "numero_pedidos": 0,
                },
                "semana": {
                    "total_pedidos": 0.00,
                    "total_recebido": 0.00,
                    "numero_pedidos": 0,
                },
                "mes": {
                    "total_pedidos": 0.00,
                    "total_recebido": 0.00,
                    "numero_pedidos": 0,
                },
            }

            # Calcular totais do dia
            today_orders = ServiceOrder.objects.filter(
                models.Q(order_date=today)
                | models.Q(retirada_date=today)
                | models.Q(devolucao_date=today)
            ).distinct()

            for order in today_orders:
                if order.total_value:
                    resultados["dia"]["total_pedidos"] += float(order.total_value)
                    resultados["dia"]["numero_pedidos"] += 1

                resultados["dia"]["total_recebido"] += float(order.advance_payment)

                if order.service_order_phase == finished_phase and order.total_value:
                    resultados["dia"]["total_recebido"] += float(order.advance_payment)
                    resultados["dia"]["total_recebido"] += float(order.total_value)

            # Calcular totais da semana
            week_start = today - timedelta(days=today.weekday())
            week_orders = ServiceOrder.objects.filter(
                models.Q(order_date__gte=week_start, order_date__lte=today)
                | models.Q(retirada_date__gte=week_start, retirada_date__lte=today)
                | models.Q(devolucao_date__gte=week_start, devolucao_date__lte=today)
            ).distinct()

            for order in week_orders:
                if order.total_value:
                    resultados["semana"]["total_pedidos"] += float(order.total_value)
                    resultados["semana"]["numero_pedidos"] += 1

                resultados["dia"]["total_recebido"] += float(order.advance_payment)

                if order.service_order_phase == finished_phase and order.total_value:
                    resultados["semana"]["total_recebido"] += float(order.total_value)

            # Calcular totais do mês
            month_start = today.replace(day=1)
            month_orders = ServiceOrder.objects.filter(
                models.Q(order_date__gte=month_start, order_date__lte=today)
                | models.Q(retirada_date__gte=month_start, retirada_date__lte=today)
                | models.Q(devolucao_date__gte=month_start, devolucao_date__lte=today)
            ).distinct()

            for order in month_orders:
                if order.total_value:
                    resultados["mes"]["total_pedidos"] += float(order.total_value)
                    resultados["mes"]["numero_pedidos"] += 1

                resultados["mes"]["total_recebido"] += float(order.advance_payment)

                if order.service_order_phase == finished_phase and order.total_value:
                    resultados["mes"]["total_recebido"] += float(order.total_value)

            return Response({"status": status, "resultados": resultados})

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
            today = date.today()

            # Função para mover automaticamente para RECUSADA quem passou da data do evento
            def move_to_refused_if_event_passed():
                refused_phase = ServiceOrderPhase.objects.filter(
                    name="RECUSADA"
                ).first()
                if not refused_phase:
                    return

                # Buscar OS que passaram da data do evento e não foram retiradas
                overdue_orders = ServiceOrder.objects.filter(
                    event_date__lt=today,
                    data_retirado__isnull=True,  # Não foi retirada
                    service_order_phase__name__in=[
                        "PENDENTE",
                        "AGUARDANDO_DEVOLUCAO",
                        "FINALIZADO",
                        "AGUARDANDO_RETIRADA",
                    ],
                ).exclude(service_order_phase__name="RECUSADA")

                for order in overdue_orders:
                    order.service_order_phase = refused_phase
                    order.justification_refusal = "Cliente não retirou o produto"
                    order.save()
                    print(
                        f"OS {order.id} movida automaticamente para RECUSADA - Cliente não retirou o produto"
                    )

            # Executar verificação automática
            move_to_refused_if_event_passed()

            phase = ServiceOrderPhase.objects.filter(name__icontains=phase_name).first()
            if not phase:
                return Response(
                    {"error": "Fase não encontrada"}, status=status.HTTP_404_NOT_FOUND
                )

            # Filtrar orders baseado na fase
            if phase.name == "ATRASADO":
                # Fase ATRASADO:
                # 1. OS em AGUARDANDO_DEVOLUCAO cuja data_devolucao já passou mas evento ainda não passou
                # 2. OS em AGUARDANDO_RETIRADA cuja data_retirada já passou mas evento ainda não passou
                # 3. OS em AGUARDANDO_DEVOLUCAO que não foram devolvidas e evento já passou
                aguardando_devolucao_phase = ServiceOrderPhase.objects.filter(
                    name="AGUARDANDO_DEVOLUCAO"
                ).first()
                aguardando_retirada_phase = ServiceOrderPhase.objects.filter(
                    name="AGUARDANDO_RETIRADA"
                ).first()

                orders = (
                    ServiceOrder.objects.filter(
                        models.Q(
                            service_order_phase=aguardando_devolucao_phase,
                            devolucao_date__lt=today,  # Passou da data de devolução
                            event_date__gt=today,  # Evento ainda não passou
                        )
                        | models.Q(
                            service_order_phase=aguardando_retirada_phase,
                            retirada_date__lt=today,  # Passou da data de retirada
                            event_date__gt=today,  # Evento ainda não passou
                        )
                        | models.Q(
                            service_order_phase=aguardando_devolucao_phase,
                            data_devolvido__isnull=True,  # Não foi devolvida
                            event_date__lt=today,  # Evento já passou
                        )
                    )
                    .select_related(
                        "renter", "employee", "attendant", "renter__person_type"
                    )
                    .prefetch_related("items__temporary_product", "items__product")
                )

            elif phase.name == "AGUARDANDO_DEVOLUCAO":
                # Fase AGUARDANDO_DEVOLUCAO: apenas as que ainda respeitam a data de devolução
                # E que não estão atrasadas (evento ainda não passou)
                orders = (
                    ServiceOrder.objects.filter(
                        service_order_phase=phase,
                        devolucao_date__gte=today,  # Ainda não passou da data de devolução
                        event_date__gt=today,  # Evento ainda não passou
                    )
                    .select_related(
                        "renter", "employee", "attendant", "renter__person_type"
                    )
                    .prefetch_related("items__temporary_product", "items__product")
                )

            elif phase.name == "AGUARDANDO_RETIRADA":
                # Fase AGUARDANDO_RETIRADA: apenas as que ainda respeitam a data de retirada
                # E que não estão atrasadas (evento ainda não passou)
                orders = (
                    ServiceOrder.objects.filter(
                        service_order_phase=phase,
                        retirada_date__gte=today,  # Ainda não passou da data de retirada
                        event_date__gt=today,  # Evento ainda não passou
                    )
                    .select_related(
                        "renter", "employee", "attendant", "renter__person_type"
                    )
                    .prefetch_related("items__temporary_product", "items__product")
                )

            else:
                # Outras fases: comportamento normal
                orders = (
                    ServiceOrder.objects.filter(service_order_phase=phase)
                    .select_related(
                        "renter", "employee", "attendant", "renter__person_type"
                    )
                    .prefetch_related("items__temporary_product", "items__product")
                )

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
                    "justification_refusal": order.justification_refusal,
                }

                # Calcular justificativa do atraso para fase ATRASADO
                if phase.name == "ATRASADO":
                    # Para fase ATRASADO, determinar a justificativa baseada nas datas
                    if (
                        order.devolucao_date
                        and order.devolucao_date < today
                        and order.event_date > today
                    ):
                        order_data["justificativa_atraso"] = (
                            "Cliente ainda não devolveu"
                        )
                    elif (
                        order.retirada_date
                        and order.retirada_date < today
                        and order.event_date > today
                    ):
                        order_data["justificativa_atraso"] = "Cliente não retirou"
                    elif order.data_devolvido is None and order.event_date < today:
                        order_data["justificativa_atraso"] = (
                            "Cliente ainda não devolveu (evento passou)"
                        )
                    else:
                        order_data["justificativa_atraso"] = None
                else:
                    order_data["justificativa_atraso"] = None

                # Dados do cliente no formato esperado pelo frontend
                cliente_data = {
                    "nome": order.renter.name,
                    "cpf": order.renter.cpf,
                    "contatos": [],
                    "enderecos": [],
                }

                # Contatos do cliente
                if contact:
                    if contact.email:
                        cliente_data["contatos"].append(
                            {"tipo": "email", "valor": contact.email}
                        )
                    if contact.phone:
                        cliente_data["contatos"].append(
                            {"tipo": "telefone", "valor": contact.phone}
                        )

                # Endereços do cliente
                if address:
                    cliente_data["enderecos"].append(
                        {
                            "cep": address.cep,
                            "rua": address.street,
                            "numero": address.number,
                            "bairro": address.neighborhood,
                            "cidade": address.city.name if address.city else "",
                        }
                    )

                # Processar itens da OS
                itens = []
                acessorios = []

                for item in order.items.all():
                    # Determinar se é produto temporário ou produto real
                    temp_product = item.temporary_product
                    product = item.product

                    if temp_product:
                        # Produto temporário
                        if temp_product.product_type in [
                            "paleto",
                            "camisa",
                            "calca",
                            "colete",
                        ]:
                            # Item de roupa
                            item_data = {
                                "tipo": temp_product.product_type,
                                "cor": temp_product.color or "",
                                "extras": temp_product.extras
                                or temp_product.description
                                or "",
                                "venda": temp_product.venda or False,
                                "extensor": False,  # Extensor só para passante
                            }

                            # Campos específicos por tipo
                            if temp_product.product_type in ["paleto", "camisa"]:
                                item_data.update(
                                    {
                                        "numero": temp_product.size
                                        or "",  # ✅ Campo "numero" retorna o "size" do banco
                                        "manga": temp_product.sleeve_length or "",
                                        "marca": temp_product.brand or "",
                                        "ajuste": item.adjustment_notes or "",
                                    }
                                )
                            elif temp_product.product_type == "calca":
                                item_data.update(
                                    {
                                        "numero": temp_product.size,
                                        "cintura": temp_product.waist_size or "",
                                        "perna": temp_product.leg_length or "",
                                        "marca": temp_product.brand or "",
                                        "ajuste_cintura": temp_product.ajuste_cintura
                                        or "",
                                        "ajuste_comprimento": temp_product.ajuste_comprimento
                                        or "",
                                    }
                                )
                            elif temp_product.product_type == "colete":
                                item_data.update({"marca": temp_product.brand or ""})

                            print(
                                f"DEBUG ITEM: Retornando item - tipo: {item_data['tipo']}, numero: '{item_data.get('numero', '')}'"
                            )
                            itens.append(item_data)
                        else:
                            # Acessório
                            acessorio_data = {
                                "tipo": temp_product.product_type,
                                "numero": temp_product.size
                                or "",  # ✅ Campo "numero" retorna o "size" do banco
                                "cor": temp_product.color or "",
                                "descricao": temp_product.description or "",
                                "marca": temp_product.brand or "",
                                "extensor": temp_product.extensor or False,
                                "venda": temp_product.venda or False,
                            }
                            print(
                                f"DEBUG ACESSORIO: Retornando acessório - tipo: {acessorio_data['tipo']}, numero: '{acessorio_data['numero']}'"
                            )
                            acessorios.append(acessorio_data)

                    elif product:
                        # Produto real do estoque
                        if product.tipo.lower() in [
                            "paleto",
                            "camisa",
                            "calça",
                            "colete",
                        ]:
                            # Item de roupa
                            item_data = {
                                "tipo": product.tipo.lower(),
                                "cor": product.cor or "",
                                "extras": product.nome_produto or "",
                                "venda": False,  # Produtos do estoque não são vendidos
                                "extensor": False,
                            }

                            # Campos específicos por tipo
                            if product.tipo.lower() in ["paleto", "camisa"]:
                                item_data.update(
                                    {
                                        "numero": (
                                            str(product.tamanho)
                                            if product.tamanho
                                            else ""
                                        ),  # ✅ Campo "numero" retorna o "tamanho" do produto do estoque
                                        "manga": "",
                                        "marca": product.marca or "",
                                        "ajuste": item.adjustment_notes or "",
                                    }
                                )
                            elif product.tipo.lower() == "calça":
                                item_data.update(
                                    {
                                        "numero": (
                                            str(product.tamanho)
                                            if product.tamanho
                                            else ""
                                        ),  # ✅ Campo "numero" retorna o "tamanho" do produto do estoque
                                        "cintura": "",
                                        "perna": "",
                                        "marca": product.marca or "",
                                        "ajuste_cintura": "",
                                        "ajuste_comprimento": "",
                                    }
                                )
                            elif product.tipo.lower() == "colete":
                                item_data.update({"marca": product.marca or ""})

                            itens.append(item_data)
                        else:
                            # Acessório
                            acessorio_data = {
                                "tipo": product.tipo.lower(),
                                "numero": (
                                    str(product.tamanho) if product.tamanho else ""
                                ),  # ✅ Campo "numero" retorna o "tamanho" do produto do estoque
                                "cor": product.cor or "",
                                "descricao": product.nome_produto or "",
                                "marca": product.marca or "",
                                "extensor": False,  # Produtos do estoque não têm extensor
                                "venda": False,
                            }
                            acessorios.append(acessorio_data)

                # Dados da ordem de serviço no formato esperado pelo frontend
                ordem_servico_data = {
                    "data_pedido": order.order_date,
                    "data_evento": order.event_date,
                    "data_retirada": order.retirada_date,
                    "data_devolucao": order.devolucao_date,
                    "ocasiao": order.occasion,
                    "modalidade": order.service_type or "Aluguel",
                    "itens": itens,
                    "acessorios": acessorios,
                    "pagamento": {
                        "total": float(order.total_value) if order.total_value else 0,
                        "sinal": (
                            float(order.advance_payment) if order.advance_payment else 0
                        ),
                        "restante": (
                            float(order.remaining_payment)
                            if order.remaining_payment
                            else 0
                        ),
                    },
                }

                # Adicionar dados completos ao response
                order_data.update(
                    {"cliente": cliente_data, "ordem_servico": ordem_servico_data}
                )

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
            email = data.get("email", "").strip()
            telefone = data.get("telefone")

            # Tratar email vazio como None para evitar constraint unique
            if not email:
                email = None

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
                order_date=date.today(),
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


class EventCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["events"],
        summary="Criar evento",
        description="Cria um novo evento com nome, descrição opcional e data",
        request=EventCreateSerializer,
        responses={201: EventSerializer},
    )
    def post(self, request):
        serializer = EventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data["name"].upper()
        description = serializer.validated_data.get("description", "")
        event_date = serializer.validated_data.get("event_date")

        event = Event.objects.create(
            name=name,
            description=description,
            event_date=event_date,
            created_by=request.user,
        )

        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)


class EventAddParticipantsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["events"],
        summary="Adicionar pessoas a um evento",
        request=EventAddParticipantsSerializer,
        responses={200: EventSerializer},
    )
    def post(self, request, event_id: int):
        event = get_object_or_404(Event, id=event_id)
        serializer = EventAddParticipantsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participant_ids = serializer.validated_data["participant_ids"]

        existing_person_ids = set(
            EventParticipant.objects.filter(event=event).values_list(
                "person_id", flat=True
            )
        )

        people = Person.objects.filter(id__in=participant_ids).exclude(
            id__in=existing_person_ids
        )
        EventParticipant.objects.bulk_create(
            [EventParticipant(event=event, person=p) for p in people]
        )

        event.refresh_from_db()
        return Response(EventSerializer(event).data, status=status.HTTP_200_OK)


class EventOpenListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["events"],
        summary="Listar eventos com OS em andamento",
        responses={200: EventSerializer(many=True)},
    )
    def get(self, request):
        finalizadas = ["FINALIZADO", "RECUSADA"]
        eventos_ids = (
            ServiceOrder.objects.filter(
                event__isnull=False,
                service_order_phase__isnull=False,
                date_canceled__isnull=True,
            )
            .exclude(service_order_phase__name__in=finalizadas)
            .values_list("event_id", flat=True)
            .distinct()
        )
        eventos = Event.objects.filter(id__in=eventos_ids)
        return Response(EventSerializer(eventos, many=True).data)


class EventLinkServiceOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["events"],
        summary="Vincular ordem de serviço a evento",
        description="Vincula uma ordem de serviço existente a um evento através dos IDs",
        request=EventLinkServiceOrderSerializer,
        responses={
            200: {
                "description": "Ordem de serviço vinculada com sucesso",
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "service_order_id": {"type": "integer"},
                    "event_id": {"type": "integer"},
                },
            },
            404: {"description": "Ordem de serviço ou evento não encontrado"},
            400: {"description": "Dados inválidos"},
        },
    )
    def post(self, request):
        """Vincular ordem de serviço a um evento"""
        try:
            serializer = EventLinkServiceOrderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            service_order_id = serializer.validated_data["service_order_id"]
            event_id = serializer.validated_data["event_id"]

            # Verificar se a ordem de serviço existe
            service_order = get_object_or_404(ServiceOrder, id=service_order_id)

            # Verificar se o evento existe
            event = get_object_or_404(Event, id=event_id)

            # Vincular a ordem de serviço ao evento
            service_order.event = event
            service_order.save()

            return Response(
                {
                    "success": True,
                    "message": f"OS {service_order_id} vinculada ao evento '{event.name}' com sucesso",
                    "service_order_id": service_order_id,
                    "event_id": event_id,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao vincular OS ao evento: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EventListWithStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["events"],
        summary="Listar eventos com status",
        description="Lista todos os eventos com contagem de ordens de serviço e status calculado",
        responses={200: EventStatusSerializer(many=True)},
    )
    def get(self, request):
        """Listar eventos com contagem de OS e status"""
        try:
            from datetime import date

            today = date.today()

            # Buscar todos os eventos
            events = Event.objects.all().order_by("-date_created")

            result_data = []

            for event in events:
                # Contar ordens de serviço vinculadas ao evento
                service_orders = ServiceOrder.objects.filter(event=event)
                service_orders_count = service_orders.count()

                # Calcular status do evento
                status_evento = self._calculate_event_status(
                    event, service_orders, today
                )

                event_data = {
                    "id": event.id,
                    "name": event.name,
                    "description": event.description or "",
                    "event_date": event.event_date,
                    "service_orders_count": service_orders_count,
                    "status": status_evento,
                    "date_created": event.date_created,
                    "date_updated": event.date_updated,
                }

                result_data.append(event_data)

            return Response(result_data)

        except Exception as e:
            return Response(
                {"error": f"Erro ao listar eventos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _calculate_event_status(self, event, service_orders, today):
        """Calcula o status do evento baseado nas ordens de serviço"""

        # Se não tem data do evento definida, não podemos calcular status
        if not event.event_date:
            return "SEM DATA"

        # Se o evento ainda não passou da data
        if event.event_date >= today:
            return "AGENDADO"

        # Evento já passou da data
        if service_orders.count() == 0:
            # Evento passou da data e não possui nenhuma OS vinculada
            return "CANCELADO"

        # Verificar status das OS vinculadas
        os_finalizadas = service_orders.filter(
            service_order_phase__name="FINALIZADO"
        ).count()

        os_em_andamento = service_orders.filter(
            service_order_phase__name__in=[
                "PENDENTE",
                "AGUARDANDO_RETIRADA",
                "AGUARDANDO_DEVOLUCAO",
            ]
        ).count()

        # Se todas as OS foram finalizadas
        if os_finalizadas == service_orders.count():
            return "FINALIZADO"

        # Se ainda há OS em andamento após a data do evento
        if os_em_andamento > 0:
            return "POSSUI PENDÊNCIAS"

        # Caso geral - evento passou e tem OS mas não finalizadas corretamente
        return "CANCELADO"

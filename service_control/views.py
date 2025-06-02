import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import datetime, now
from django.views.decorators.http import require_GET, require_POST

from accounts.models import City, Person, PersonsAdresses, PersonsContacts, PersonType
from products.models import TemporaryProduct

from .models import ServiceOrder, ServiceOrderItem, ServiceOrderPhase

# def service_control_view(request, id):
#     return render(request, "service_control.html", context={"user": request.user})


def service_control_view(request, id):
    service_order = get_object_or_404(ServiceOrder, id=id)

    # Verifica se a OS está na fase "PENDENTE"
    if (
        not service_order.service_order_phase
        or service_order.service_order_phase.name.upper() != "PENDENTE"
    ):
        return redirect("os_view")  # Redireciona para a listagem se não for pendente

    return render(
        request,
        "service_control.html",
        {
            "user": request.user,
            "order_id": id,
        },
    )


@require_POST
@login_required
def create_pre_service_order(request):
    payload = json.loads(request.body)

    order_data = {
        "cliente": payload.get("cliente_nome"),
        "telefone": payload.get("telefone"),
        "cpf": payload.get("cpf").replace(".", "").replace("-", ""),
        "atendente": payload.get("atendente"),
        "origem": payload.get("origem"),
        "data_evento": payload.get("data_evento"),
        "tipo_servico": payload.get("tipo_servico"),
        "evento": payload.get("evento"),
        "papel_evento": payload.get("papel_evento"),
        "endereco": {
            "cep": payload.get("endereco", {}).get("cep"),
            "rua": payload.get("endereco", {}).get("rua"),
            "numero": payload.get("endereco", {}).get("numero"),
            "bairro": payload.get("endereco", {}).get("bairro"),
            "cidade": payload.get("endereco", {}).get("cidade"),
        },
    }

    if len(order_data["cpf"]) != 11:
        return JsonResponse({"error": "CPF Inválido"}, status=400)

    if not all([order_data["cpf"], order_data["telefone"], order_data["cliente"]]):
        return JsonResponse({"error": "Dados do cliente incompletos"}, status=400)

    try:
        city_obj = City.objects.get(
            name__iexact=order_data["endereco"]["cidade"].upper()
        )
    except City.DoesNotExist:
        return JsonResponse({"error": "Cidade não encontrada"}, status=400)

    pt, _ = PersonType.objects.get_or_create(type="CLIENTE")

    person, _ = Person.objects.get_or_create(
        cpf=order_data["cpf"],
        defaults={
            "name": order_data["cliente"].upper(),
            "person_type": pt,
            "created_by": request.user,
        },
    )

    PersonsContacts.objects.get_or_create(
        phone=order_data["telefone"],
        person=person,
        defaults={"created_by": request.user},
    )

    PersonsAdresses.objects.get_or_create(
        person=person,
        street=order_data["endereco"]["rua"],
        number=order_data["endereco"]["numero"],
        cep=order_data["endereco"]["cep"],
        neighborhood=order_data["endereco"]["bairro"],
        city=city_obj,
        defaults={"created_by": request.user},
    )

    employee = Person.objects.filter(name=order_data["atendente"]).first()

    if not employee:
        return JsonResponse({"error": "Funcionário não encontrado."}, status=400)

    service_order_phase = ServiceOrderPhase.objects.filter(name="PENDENTE").first()

    ServiceOrder.objects.create(
        renter=person,
        employee=employee,
        attendant=request.user.person,
        order_date=now().date(),
        event_date=order_data["data_evento"],
        occasion=order_data["evento"].upper(),
        renter_role=order_data["papel_evento"].upper(),
        purchase=True if order_data["tipo_servico"] == "Compra" else False,
        came_from=order_data["origem"].upper(),
        service_order_phase=service_order_phase,
    )

    return JsonResponse({"message": "OS criada com sucesso"})


@require_POST
@login_required
def update_service_order(request):
    # 1. Decodifica JSON
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    # 2. Valida order_id
    order_id = payload.get("order_id")
    if not order_id:
        return JsonResponse({"error": "ID da OS não informado"}, status=400)

    # 3. Busca a OS ou 404
    service_order = get_object_or_404(ServiceOrder, id=order_id)

    # 4. Atualiza dados de pagamento e fase
    service_order.total_value = payload.get("total_value", 0)
    service_order.advance_payment = payload.get("advance_payment", 0)
    service_order.remaining_payment = payload.get("remaining_payment", 0)
    service_order.payment_method = payload.get("payment_method")
    service_order.observations = payload.get("observations", "")

    due_date = payload.get("due_date")
    if due_date:
        try:
            service_order.max_payment_date = datetime.strptime(
                due_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            return JsonResponse({"error": "Data de pagamento inválida"}, status=400)

    if float(payload.get("remaining_payment", 0)) == 0:
        phase_name = "CONCLUÍDO"
    else:
        phase_name = "FINALIZADO"

    try:
        phase = ServiceOrderPhase.objects.get(name__iexact=phase_name)
        service_order.service_order_phase = phase
    except ServiceOrderPhase.DoesNotExist:
        return JsonResponse(
            {
                "error": f"Fase '{phase_name}' não encontrada no sistema. Verifique se está cadastrada corretamente."
            },
            status=400,
        )

    # 5. Ajuste_needed se qualquer item requerer
    items_data = payload.get("items", [])
    service_order.adjustment_needed = any(
        item.get("adjustment_needed") for item in items_data
    )

    service_order.save()

    # 6. Limpamos itens antigos e recriamos
    service_order.items.all().delete()
    seen = set()

    for it in items_data:
        key = (
            it.get("product_type"),
            it.get("size"),
            it.get("sleeve_length"),
            it.get("leg_length"),
            it.get("waist_size"),
            it.get("collar_size"),
            it.get("color"),  # AGORA é a string do nome da cor
            it.get("brand"),
            it.get("fabric"),
            it.get("description"),
            bool(it.get("adjustment_needed")),
            it.get("adjustment_value"),
            it.get("adjustment_notes"),
        )
        if key in seen:
            continue
        seen.add(key)

        temp, _ = TemporaryProduct.objects.get_or_create(
            product_type=it.get("product_type"),
            size=it.get("size"),
            sleeve_length=it.get("sleeve_length"),
            leg_length=it.get("leg_length"),
            waist_size=it.get("waist_size"),
            collar_size=it.get("collar_size"),
            color=it.get("color") or "",  # salva exatamente a string
            brand=it.get("brand"),
            fabric=it.get("fabric"),
            description=it.get("description"),
            defaults={"created_by": request.user},
        )

        ServiceOrderItem.objects.create(
            service_order=service_order,
            temporary_product=temp,
            adjustment_needed=it.get("adjustment_needed", False),
            adjustment_value=it.get("adjustment_value"),
            adjustment_notes=it.get("adjustment_notes"),
            created_by=request.user,
        )

    return JsonResponse(
        {"message": "OS atualizada com sucesso", "order_id": service_order.id}
    )


@login_required
def pre_register_view(request):
    """
    Exibe o formulário de triagem de cliente.
    """
    return render(
        request,
        "pre_register.html",
        {
            "user": request.user,
        },
    )


@require_GET
@login_required
def list_pending_service_orders(request):
    try:
        # Busca a fase "PENDENTE" ou retorna 404 se não existir
        pending_phase = ServiceOrderPhase.objects.get(name="PENDENTE")

        # Query para buscar as OS pendentes com informações relacionadas
        orders = (
            ServiceOrder.objects.filter(service_order_phase=pending_phase)
            .select_related("renter", "employee", "attendant", "service_order_phase")
            .order_by("-order_date")
        )

        # Serializa os dados para o frontend
        orders_data = []
        for order in orders:
            orders_data.append(
                {
                    "id": order.id,
                    "cliente": order.renter.name if order.renter else "",
                    "cpf": order.renter.cpf if order.renter else "",
                    "telefone": (
                        order.renter.phone if hasattr(order.renter, "phone") else ""
                    ),
                    "atendente": order.employee.name if order.employee else "",
                    "data_ordem": order.order_date.strftime("%d/%m/%Y"),
                    "data_evento": (
                        order.event_date.strftime("%d/%m/%Y")
                        if order.event_date
                        else ""
                    ),
                    "ocasiao": order.occasion,
                    "origem": order.came_from,
                    "tipo_servico": "Compra" if order.purchase else "Aluguel",
                    "fase": order.service_order_phase.name,
                }
            )

        return JsonResponse({"data": orders_data}, safe=False)

    except ServiceOrderPhase.DoesNotExist:
        return JsonResponse({"error": "Fase PENDENTE não encontrada"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# views.py


@require_GET
@login_required
def list_awaiting_payment_service_orders(request):
    """
    Retorna JSON com as OS na fase "AGUARDANDO PGTO", tratando possíveis tuplas
    em campos numéricos e usando __str__() para TemporaryProduct.
    """
    try:
        phase = ServiceOrderPhase.objects.get(name__iexact="FINALIZADO")
    except ServiceOrderPhase.DoesNotExist:
        return JsonResponse({"error": "Fase FINALIZADO não encontrada"}, status=404)

    orders = (
        ServiceOrder.objects.filter(service_order_phase=phase)
        .select_related("renter", "employee", "attendant", "service_order_phase")
        .prefetch_related(
            "items__product", "items__temporary_product", "items__color_catalogue"
        )
        .order_by("-order_date")
    )

    def safe_float(val):
        # Se vier como tupla/lista, pega o primeiro elemento
        if isinstance(val, (tuple, list)):
            val = val[0] if val else 0
        try:
            return float(val or 0)
        except (TypeError, ValueError):
            return 0.0

    data = []
    for order in orders:
        itens = []
        for item in order.items.all():
            if item.product:
                nome = item.product.name
            elif item.temporary_product:
                nome = str(item.temporary_product)
            else:
                nome = "Produto não definido"

            itens.append(
                {
                    "produto": nome,
                    "cor": item.temporary_product.color,
                    "ajuste": bool(item.adjustment_needed),
                    "valor_ajuste": safe_float(item.adjustment_value),
                    "obs_ajuste": item.adjustment_notes or "",
                }
            )

        data.append(
            {
                "id": order.id,
                "cliente": order.renter.name if order.renter else "",
                "cpf": order.renter.cpf if order.renter else "",
                "telefone": getattr(order.renter, "phone", ""),
                "atendente": order.employee.name if order.employee else "",
                "data_ordem": order.order_date.strftime("%d/%m/%Y"),
                "data_evento": (
                    order.event_date.strftime("%d/%m/%Y") if order.event_date else ""
                ),
                "ocasiao": order.occasion,
                "origem": order.came_from,
                "tipo_servico": "Compra" if order.purchase else "Aluguel",
                "fase": order.service_order_phase.name,
                "valor_total": safe_float(order.total_value),
                "valor_pago": safe_float(order.advance_payment),
                "valor_faltando": safe_float(order.remaining_payment),
                "metodo_pagamento": order.payment_method or "",
                "itens": itens,
            }
        )

    return JsonResponse({"data": data}, safe=False)


@login_required
def os_view(request):
    """
    Exibe o formulário de triagem de cliente.
    """
    return render(
        request,
        "os_list.html",
        {
            "user": request.user,
        },
    )


@require_GET
@login_required
def get_service_order_client(request, id):
    # Busca a OS ou retorna 404
    order = get_object_or_404(ServiceOrder, id=id)
    # Cliente (renter) da OS
    person = order.renter

    # Telefones cadastrados
    phones = list(
        PersonsContacts.objects.filter(person=person).values_list("phone", flat=True)
    )

    # Endereços cadastrados
    addresses = []
    for addr in PersonsAdresses.objects.filter(person=person):
        addresses.append(
            {
                "cep": addr.cep,
                "rua": addr.street,
                "numero": addr.number,
                "bairro": addr.neighborhood,
                "cidade": addr.city.name,
            }
        )

    # Monta payload
    payload = {
        "order_id": order.id,
        "id": person.id,
        "nome": person.name,
        "cpf": person.cpf,
        "telefones": phones,
        "enderecos": addresses,
    }

    return JsonResponse({"data": payload})


@require_POST
@login_required
def mark_service_order_paid(request, id):
    try:
        so = get_object_or_404(ServiceOrder, id=id)
        phase = ServiceOrderPhase.objects.get(name__iexact="CONCLUÍDO")
        so.service_order_phase = phase
        so.save()
        return JsonResponse({"message": "OS marcada como paga"})
    except ServiceOrderPhase.DoesNotExist:
        return JsonResponse({"error": "Fase CONCLUÍDA não encontrada"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_GET
@login_required
def list_finished_service_orders(request):
    """
    Retorna JSON com as OS na fase "CONCLUÍDO", tratando possíveis tuplas
    em campos numéricos e usando __str__() para TemporaryProduct.
    """
    try:
        phase = ServiceOrderPhase.objects.get(name__iexact="CONCLUÍDO")
    except ServiceOrderPhase.DoesNotExist:
        return JsonResponse({"error": "Fase CONCLUÍDO não encontrada"}, status=404)

    orders = (
        ServiceOrder.objects.filter(service_order_phase=phase)
        .select_related("renter", "employee", "attendant", "service_order_phase")
        .prefetch_related(
            "items__product", "items__temporary_product", "items__color_catalogue"
        )
        .order_by("-order_date")
    )

    def safe_float(val):
        # Se vier como tupla/lista, pega o primeiro elemento
        if isinstance(val, (tuple, list)):
            val = val[0] if val else 0
        try:
            return float(val or 0)
        except (TypeError, ValueError):
            return 0.0

    data = []
    for order in orders:
        itens = []
        for item in order.items.all():
            if item.product:
                nome = item.product.name
            elif item.temporary_product:
                nome = str(item.temporary_product)
            else:
                nome = "Produto não definido"

            itens.append(
                {
                    "produto": nome,
                    "cor": item.temporary_product.color,
                    "ajuste": bool(item.adjustment_needed),
                    "valor_ajuste": safe_float(item.adjustment_value),
                    "obs_ajuste": item.adjustment_notes or "",
                }
            )

        data.append(
            {
                "id": order.id,
                "cliente": order.renter.name if order.renter else "",
                "cpf": order.renter.cpf if order.renter else "",
                "telefone": getattr(order.renter, "phone", ""),
                "atendente": order.employee.name if order.employee else "",
                "data_ordem": order.order_date.strftime("%d/%m/%Y"),
                "data_evento": (
                    order.event_date.strftime("%d/%m/%Y") if order.event_date else ""
                ),
                "ocasiao": order.occasion,
                "origem": order.came_from,
                "tipo_servico": "Compra" if order.purchase else "Aluguel",
                "fase": order.service_order_phase.name,
                "valor_total": safe_float(order.total_value),
                "valor_pago": safe_float(order.advance_payment),
                "valor_faltando": safe_float(order.remaining_payment),
                "metodo_pagamento": order.payment_method or "",
                "itens": itens,
            }
        )

    return JsonResponse({"data": data}, safe=False)


@require_POST
@login_required
def refuse_service_order(request, id):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    so = get_object_or_404(ServiceOrder, id=id)

    justification = payload.get("justification_refusal", "").strip()
    so.justification_refusal = justification or None

    # Cria ou obtém fase "RECUSADA"
    phase, _ = ServiceOrderPhase.objects.get_or_create(
        name="RECUSADA", defaults={"created_by": request.user}
    )
    so.service_order_phase = phase
    so.save()

    return JsonResponse({"message": "OS marcada como recusada"})


@require_GET
@login_required
def list_overdue_service_orders(request):
    today = timezone.now().date()
    overdue_orders = (
        ServiceOrder.objects.filter(
            service_order_phase__name="Finalizado", max_payment_date__lt=today
        )
        .select_related("renter", "attendant")
        .prefetch_related("items")
    )

    data = []
    for os in overdue_orders:
        items = []
        for item in os.items.all():
            items.append(
                {
                    "produto": (
                        item.product.name
                        if item.product
                        else item.temporary_product.name
                    ),
                    "cor": item.color_catalogue.name if item.color_catalogue else "",
                    "ajuste": item.adjustment_needed,
                    "valor_ajuste": item.adjustment_value or 0,
                    "obs_ajuste": item.adjustment_notes or "",
                }
            )
        data.append(
            {
                "id": os.id,
                "cliente": os.renter.name,
                "cpf": os.renter.document,
                "telefone": os.renter.phone,
                "atendente": os.attendant.name if os.attendant else "",
                "data_ordem": os.order_date.strftime("%d/%m/%Y"),
                "data_evento": os.event_date.strftime("%d/%m/%Y"),
                "ocasiao": os.occasion,
                "origem": os.came_from or "",
                "tipo_servico": "Compra" if os.purchase else "Locação",
                "valor_total": float(os.total_value or 0),
                "valor_pago": float(os.advance_payment or 0),
                "valor_faltando": float(os.remaining_payment or 0),
                "metodo_pagamento": os.payment_method or "",
                "itens": items,
            }
        )
    return JsonResponse({"data": data})


@require_GET
@login_required
def list_refused_service_orders(request):
    refused_orders = ServiceOrder.objects.filter(
        justification_refusal__isnull=False
    ).select_related("renter", "attendant", "employee")

    data = []
    for os in refused_orders:
        data.append(
            {
                "id": os.id,
                "cliente": os.renter.name,
                "cpf": os.renter.cpf,
                # 'telefone': os.renter.,
                "data_ordem": os.order_date.strftime("%d/%m/%Y"),
                "data_evento": os.event_date.strftime("%d/%m/%Y"),
                "atendente": os.attendant.name if os.attendant else "",
                "recepcionista": os.employee.name if os.employee else "",
                "justificativa": os.justification_refusal,
                "tipo_servico": "Compra" if os.purchase else "Locação",
                "origem": os.came_from or "",
            }
        )
    return JsonResponse({"data": data})

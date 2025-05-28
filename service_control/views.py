import json
from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django.views.decorators.http import require_GET, require_POST

from accounts.models import City, Person, PersonsAdresses, PersonsContacts, PersonType
from products.models import TemporaryProduct

from .models import ServiceOrder, ServiceOrderItem, ServiceOrderPhase

# def service_control_view(request, id):
#     return render(request, "service_control.html", context={"user": request.user})


def service_control_view(request, id):
    return render(
        request,
        "service_control.html",
        {
            "user": request.user,
            "order_id": id,  # <— adiciona o ID da OS
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
def create_service_order(request):
    try:
        payload = json.loads(request.body)

        # --- 1. Dados do cliente ---
        cli = payload.get("cliente", {})
        nome = cli.get("nome")
        cpf = cli.get("cpf")
        telefone = cli.get("telefone")
        cep = cli.get("cep")
        rua = cli.get("rua")
        numero = cli.get("numero")
        bairro = cli.get("bairro")
        cidade_nome = cli.get("cidade")

        if not all([nome, cpf, cidade_nome]):
            return JsonResponse({"error": "Dados do cliente incompletos"}, status=400)

        # valida cidade
        try:
            city_obj = City.objects.get(name__iexact=cidade_nome)
        except City.DoesNotExist:
            return JsonResponse({"error": "Cidade não encontrada"}, status=400)

        # tipo CUSTOMER
        pt, _ = PersonType.objects.get_or_create(type="CLIENTE")

        # Pessoa (por CPF)
        person, _ = Person.objects.get_or_create(
            cpf=cpf,
            defaults={
                "name": nome,
                "person_type": pt,
                "created_by": request.user,
            },
        )

        # Contato (por telefone + pessoa)
        PersonsContacts.objects.get_or_create(
            phone=telefone, person=person, defaults={"created_by": request.user}
        )

        # Endereço (único por todos os campos + pessoa)
        PersonsAdresses.objects.get_or_create(
            person=person,
            street=rua,
            number=numero,
            cep=cep,
            neighborhood=bairro,
            city=city_obj,
            defaults={"created_by": request.user},
        )

        # --- 2. Dados da OS ---
        od_str = payload.get("order_date")
        ev_str = payload.get("event_date")
        occasion = payload.get("occasion")
        purchase = payload.get("purchase", False)
        if not all([od_str, ev_str, occasion]):
            return JsonResponse({"error": "Dados da OS incompletos"}, status=400)

        order_date = datetime.strptime(od_str, "%Y-%m-%d").date()
        event_date = datetime.strptime(ev_str, "%Y-%m-%d").date()

        total_value = payload.get("total_value", 0)
        advance_payment = payload.get("advance_payment", 0)
        remaining_payment = payload.get("remaining_payment", 0)
        observations = payload.get("observations", "")

        items = payload.get("items", [])

        # se qualquer item requer ajuste, marcamos a OS como adjustment_needed
        has_adjustments = any(item.get("adjustment_needed", False) for item in items)

        service_order = ServiceOrder.objects.create(
            renter=person,
            order_date=order_date,
            event_date=event_date,
            occasion=occasion,
            total_value=total_value,
            advance_payment=advance_payment,
            remaining_payment=remaining_payment,
            purchase=purchase,
            adjustment_needed=has_adjustments,
            observations=observations,
            created_by=request.user,
        )

        # --- 3. Itens da OS ---
        seen = set()
        for it in items:
            key = (
                it.get("product_type"),
                it.get("size"),
                it.get("sleeve_length"),
                it.get("leg_length"),
                it.get("waist_size"),
                it.get("collar_size"),
                it.get("color"),
                it.get("brand"),  # novo
                it.get("fabric"),  # novo
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
                color=it.get("color"),
                brand=it.get("brand"),  # novo
                fabric=it.get("fabric"),  # novo
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
            {"order_id": service_order.id, "message": "OS criada com sucesso"}
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def list_service_orders(request):
    """
    Lista as Ordens de Serviço no formato esperado pelo AgGrid.
    """
    orders = ServiceOrder.objects.select_related("renter", "created_by").all()

    data = []
    for os in orders:
        cliente = os.renter.name
        responsavel = os.created_by.get_full_name() or os.created_by.username

        data.append(
            {
                "id": os.id,
                "cliente": cliente,
                "responsavel": responsavel,
                "order_date": os.order_date.strftime("%Y-%m-%d"),
                "event_date": os.event_date.strftime("%Y-%m-%d"),
                "valor_total": float(os.total_value),
                "valor_sinal": float(os.advance_payment),
                "valor_restante": float(os.remaining_payment),
                "atrasada": os.event_date < date.today(),
            }
        )

    return JsonResponse(data, safe=False)


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


# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_GET

# from .models import ServiceOrder
# from accounts.models import PersonsContacts, PersonsAdresses


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
        "id": person.id,
        "nome": person.name,
        "cpf": person.cpf,
        "telefones": phones,
        "enderecos": addresses,
    }

    return JsonResponse({"data": payload})

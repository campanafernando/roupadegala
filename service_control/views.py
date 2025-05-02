import json

from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from accounts.models import Person

# from products.models import TemporaryProduct
# from service_control.models import ServiceOrder


def service_control_view(request):
    return render(request, "service_control.html", context={"user": request.user})


import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.models import City, Person, PersonsAdresses, PersonsContacts, PersonType
from products.models import TemporaryProduct

from .models import ServiceOrder, ServiceOrderItem


@require_POST
@login_required
def create_service_order(request):
    """
    Cria em uma única requisição:
      1. Pessoa (único por CPF)
      2. Contato (único por telefone/pessoa)
      3. Endereço (único por todos os campos/pessoa)
      4. ServiceOrder (sem dados de endereço — agora exclusivos de Person)
      5. ServiceOrderItem + TemporaryProduct (evita duplicados na mesma payload)
    Espera JSON com:
      - cliente: {
          nome, cpf, telefone,
          cep, rua, numero, bairro, cidade
        }
      - order_date (YYYY-MM-DD)
      - event_date (YYYY-MM-DD)
      - occasion (string)
      - purchase (boolean)        ← novo campo no modelo ServiceOrder
      - total_value (decimal)
      - advance_payment (decimal)
      - remaining_payment (decimal)
      - observations (string, opcional)
      - items: [
          {
            product_type, size, sleeve_length, leg_length,
            waist_size, collar_size, color, description,
            adjustment_needed (bool),
            adjustment_value (int),
            adjustment_notes (str)
          }, …
        ]
    """
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
        pt, _ = PersonType.objects.get_or_create(type="CUSTOMER")

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

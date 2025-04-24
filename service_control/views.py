import json

from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from accounts.models import Person

# from products.models import TemporaryProduct
# from service_control.models import ServiceOrder


def service_control_view(request):
    return render(request, "service_control.html", context={"user": request.user})


def service_order_create(request):
    if request.method == "POST":
        # Lógica para salvar OS + items com TemporaryProduct
        ...
        return redirect("service_order_list")


# def service_order_list(request):
#     orders = ServiceOrder.objects.select_related('renter').all()
#     orders_data = [
#         {
#             'id': o.id,
#             'renter_name': o.renter.name,
#             'event_date': o.event_date.strftime("%d/%m/%Y"),
#             'city': o.city,
#             'contact_phone': o.contact_phone,
#             'total_value': str(o.total_value),
#             'advance_payment': str(o.advance_payment),
#             'remaining_payment': str(o.remaining_payment)
#         }
#         for o in orders
#     ]

#     context = {
#         "persons": Person.objects.all(),
#         "temporary_products": TemporaryProduct.objects.all(),
#         "service_orders": json.dumps(orders_data)
#     }
#     return render(request, "service_control/service_orders.html", context)

"""
URL configuration for roupadegala project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from accounts.views import (
    city_search,
    employee_redirect_view,
    get_client_by_cpf,
    list_employees,
    login_view,
    logout_view,
    register_client,
    register_employee_view,
    register_view,
    toggle_employee_status,
)
from products.views import (
    generate_product_qr,
    list_colors,
    product_dashboard,
    update_product_stock,
)
from service_control.views import (
    create_pre_service_order,
    get_service_order_client,
    list_awaiting_payment_service_orders,
    list_finished_service_orders,
    list_overdue_service_orders,
    list_pending_service_orders,
    list_refused_service_orders,
    mark_service_order_paid,
    os_view,
    pre_register_view,
    refuse_service_order,
    service_control_view,
    update_service_order,
)

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", login_view, name="login"),
    path("registro/", register_view, name="register"),
    path("api/register_client/", register_client, name="register_client"),
    path("logout/", logout_view, name="logout"),
    path("city-search/", city_search, name="city_search"),
    path("list-colors/", list_colors, name="list_colors"),
    path("os/<int:id>/", service_control_view, name="service_control"),
    path("update-os/", update_service_order, name="update_service_order"),
    # path("list-os/", service_order_list, name="service_order_list"),
    path("estoque/", product_dashboard, name="product_dashboard"),
    path(
        "products/<int:product_id>/generate_qr/",
        generate_product_qr,
        name="generate_product_qr",
    ),
    path("update-stock/", update_product_stock, name="update_product_stock"),
    path("funcionarios/", employee_redirect_view, name="employee_redirect"),
    path(
        "funcionarios/api/registrar/", register_employee_view, name="employees_register"
    ),
    path("funcionarios/api/listar/", list_employees, name="list_employees"),
    path(
        "funcionarios/api/toggle_status/",
        toggle_employee_status,
        name="toggle_employee_status",
    ),
    path("triagem/", pre_register_view, name="pre_register"),
    path("clientes/buscar/", get_client_by_cpf, name="get_client_by_cpf"),
    path(
        "ordem-de-servico/api/criar-pre/",
        create_pre_service_order,
        name="create_pre_service_order",
    ),
    path(
        "ordem-de-servico/api/listar-pendentes/",
        list_pending_service_orders,
        name="list_pending_service_orders",
    ),
    path(
        "ordem-de-servico/api/listar-aguardando-pagamento/",
        list_awaiting_payment_service_orders,
        name="list_awaiting_payment_service_orders",
    ),
    path("os/", os_view, name="os_view"),
    path("os/<int:id>/cliente/", get_service_order_client, name="get_os_cliente"),
    path(
        "os/<int:id>/mark_paid/",
        mark_service_order_paid,
        name="mark_service_order_paid",
    ),
    path(
        "os/concluidas/",
        list_finished_service_orders,
        name="list_finished_service_orders",
    ),
    path("os/<int:id>/recusar/", refuse_service_order, name="refuse_service_order"),
    path(
        "os/atrasadas/", list_overdue_service_orders, name="list_overdue_service_orders"
    ),
    path(
        "os/recusadas/", list_refused_service_orders, name="list_refused_service_orders"
    ),
]

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
    login_view,
    logout_view,
    register_client,
    register_view,
)
from products.views import (
    generate_product_qr,
    list_colors,
    product_dashboard,
    update_product_stock,
)
from service_control.views import service_control_view, service_order_create

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", login_view, name="login"),
    path("registro/", register_view, name="register"),
    path("api/register_client/", register_client, name="register_client"),
    path("logout/", logout_view, name="logout"),
    path("city-search/", city_search, name="city_search"),
    path("list-colors/", list_colors, name="list_colors"),
    path("os/", service_control_view, name="service_control"),
    path("create-os/", service_order_create, name="service_order_create"),
    # path("list-os/", service_order_list, name="service_order_list"),
    path("estoque/", product_dashboard, name="product_dashboard"),
    path(
        "products/<int:product_id>/generate_qr/",
        generate_product_qr,
        name="generate_product_qr",
    ),
    path("funcionarios/", employee_redirect_view, name="employee_redirect"),
    path("update-stock/", update_product_stock, name="update_product_stock"),
]

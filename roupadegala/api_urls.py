"""
URLs da API REST para o projeto RoupadeGala
"""

from django.urls import include, path

urlpatterns = [
    path("v1/", include("accounts.api_urls")),
    path("v1/", include("products.api_urls")),
    path("v1/", include("service_control.api_urls")),
]

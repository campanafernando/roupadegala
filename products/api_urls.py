"""
URLs da API para o app products
"""

from django.urls import path, include
from .api_views import (
    CatalogListAPIView,
    ColorListAPIView,
    ProductDashboardAPIView,
    ProductListAPIView,
    ProductQRCodeAPIView,
    ProductStockUpdateAPIView,
    ProductUpdateAPIView,
    TemporaryProductCreateAPIView,
    ColorWithIntensityListAPIView,
)

urlpatterns = [
    # Dashboard e estatísticas
    path(
        "products/dashboard/",
        ProductDashboardAPIView.as_view(),
        name="api_product_dashboard",
    ),
    # Produtos
    path("products/", ProductListAPIView.as_view(), name="api_product_list"),
    path(
        "products/<int:product_id>/update/",
        ProductUpdateAPIView.as_view(),
        name="api_product_update",
    ),
    path(
        "products/stock/update/",
        ProductStockUpdateAPIView.as_view(),
        name="api_product_stock_update",
    ),
    path(
        "products/<int:product_id>/qr-code/",
        ProductQRCodeAPIView.as_view(),
        name="api_product_qr_code",
    ),
    # Cores
    path("colors/", ColorListAPIView.as_view(), name="api_color_list"),
    path(
        "colors-intensities/",
        ColorWithIntensityListAPIView.as_view(),
        name="api_color_with_intensity_list",
    ),
    path('colors-with-intensities/', ColorWithIntensityListAPIView.as_view(), name='colors-with-intensities'),
    # Produtos temporários
    path(
        "temporary-products/create/",
        TemporaryProductCreateAPIView.as_view(),
        name="api_temporary_product_create",
    ),
    # Catálogos
    path("catalogs/", CatalogListAPIView.as_view(), name="api_catalog_list"),
]

"""
URLs da API para o app products
"""

from django.urls import path

from .api_views import ColorWithIntensityListAPIView  # ADICIONADO
from .api_views import (
    BrandListAPIView,
    CatalogListAPIView,
    ColorListAPIView,
    ProductDashboardAPIView,
    ProductListAPIView,
    ProductQRCodeAPIView,
    ProductStockUpdateAPIView,
    ProductUpdateAPIView,
    TemporaryProductCreateAPIView,
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
    # Marcas
    path("brands/", BrandListAPIView.as_view(), name="api_brand_list"),
    # Produtos temporários
    path(
        "temporary-products/create/",
        TemporaryProductCreateAPIView.as_view(),
        name="api_temporary_product_create",
    ),
    # Catálogos
    path("catalogs/", CatalogListAPIView.as_view(), name="api_catalog_list"),
]

"""
URLs da API REST para o projeto RoupadeGala
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from products.api_views import BrandViewSet, ColorCatalogueViewSet, ColorIntensityViewSet, BrandListNoPaginationAPIView

router = DefaultRouter()
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'color-catalogues', ColorCatalogueViewSet, basename='color-catalogue')
router.register(r'color-intensities', ColorIntensityViewSet, basename='color-intensity')

urlpatterns = [
    path("v1/", include("accounts.api_urls")),
    path("v1/brands/no-pagination/", BrandListNoPaginationAPIView.as_view(), name="api_brand_list_no_pagination"),
    path("v1/", include(router.urls)),
    path("v1/", include("products.api_urls")),
    path("v1/", include("service_control.api_urls")),
]

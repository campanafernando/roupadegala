"""
URLs da API para o app service_control
"""

from django.urls import path

from .api_views import (
    ServiceOrderClientAPIView,
    ServiceOrderCreateAPIView,
    ServiceOrderDashboardAPIView,
    ServiceOrderDetailAPIView,
    ServiceOrderListAPIView,
    ServiceOrderListByPhaseAPIView,
    ServiceOrderMarkPaidAPIView,
    ServiceOrderRefuseAPIView,
    ServiceOrderUpdateAPIView,
)

urlpatterns = [
    # Dashboard e métricas
    path(
        "service-orders/dashboard/",
        ServiceOrderDashboardAPIView.as_view(),
        name="api_service_order_dashboard",
    ),
    # Ordens de serviço
    path(
        "service-orders/",
        ServiceOrderListAPIView.as_view(),
        name="api_service_order_list",
    ),
    path(
        "service-orders/create/",
        ServiceOrderCreateAPIView.as_view(),
        name="api_service_order_create",
    ),
    path(
        "service-orders/<int:order_id>/",
        ServiceOrderDetailAPIView.as_view(),
        name="api_service_order_detail",
    ),
    path(
        "service-orders/<int:order_id>/update/",
        ServiceOrderUpdateAPIView.as_view(),
        name="api_service_order_update",
    ),
    path(
        "service-orders/<int:order_id>/mark-paid/",
        ServiceOrderMarkPaidAPIView.as_view(),
        name="api_service_order_mark_paid",
    ),
    path(
        "service-orders/<int:order_id>/refuse/",
        ServiceOrderRefuseAPIView.as_view(),
        name="api_service_order_refuse",
    ),
    path(
        "service-orders/<int:order_id>/client/",
        ServiceOrderClientAPIView.as_view(),
        name="api_service_order_client",
    ),
    # Listagem por fase
    path(
        "service-orders/phase/<str:phase_name>/",
        ServiceOrderListByPhaseAPIView.as_view(),
        name="api_service_order_by_phase",
    ),
]

# =============================================================================
# ARQUIVO LIMPO - MIGRAÇÃO PARA API REST COMPLETA
# =============================================================================
#
# Todas as views legadas foram removidas e migradas para api_views.py
#
# Views removidas:
# - product_dashboard() -> ProductDashboardAPIView
# - update_product_stock() -> ProductStockUpdateAPIView
# - generate_product_qr() -> ProductQRCodeAPIView
# - list_colors() -> ColorListAPIView
#
# Todas as funcionalidades agora estão disponíveis via API REST:
# - /api/v1/products/dashboard/
# - /api/v1/products/
# - /api/v1/products/create/
# - /api/v1/products/{id}/update/
# - /api/v1/products/stock/update/
# - /api/v1/products/{id}/qr-code/
# - /api/v1/colors/
# - /api/v1/temporary-products/create/
# - /api/v1/catalogs/
#
# Documentação completa: /api/docs/
# =============================================================================

# =============================================================================
# ARQUIVO LIMPO - MIGRAÇÃO PARA API REST COMPLETA
# =============================================================================
#
# Todas as views legadas foram removidas e migradas para api_views.py
#
# Views removidas:
# - login_view() -> LoginAPIView
# - register_view() -> RegisterAPIView
# - logout_view() -> (não necessário em API REST)
# - city_search() -> CitySearchAPIView
# - employee_redirect_view() -> (removido - não necessário)
# - register_employee_view() -> EmployeeRegisterAPIView
# - list_employees() -> EmployeeListAPIView
# - toggle_employee_status() -> EmployeeToggleStatusAPIView
# - password_reset_view() -> PasswordResetAPIView
# - password_reset_done_view() -> (removido - não necessário)
# - password_reset_error_view() -> (removido - não necessário)
# - register_client() -> ClientRegisterAPIView
# - get_client_by_cpf() -> ClientSearchAPIView
# - EmployeeRegisterAPIView() -> (já em api_views.py)
#
# Todas as funcionalidades agora estão disponíveis via API REST:
# - /api/v1/auth/login/
# - /api/v1/auth/register/
# - /api/v1/auth/password-reset/
# - /api/v1/cities/search/
# - /api/v1/employees/register/
# - /api/v1/employees/list/
# - /api/v1/employees/toggle-status/
# - /api/v1/clients/register/
# - /api/v1/clients/search/
#
# Documentação completa: /api/docs/
# =============================================================================

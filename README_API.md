# API REST - Roupa de Gala

Esta documentação descreve a API REST implementada para o sistema Roupa de Gala, que substitui a arquitetura anterior baseada em templates.

## 🚀 Migração Completa

A migração estrutural foi realizada com sucesso, convertendo todos os endpoints existentes para uma arquitetura REST API usando Django REST Framework (DRF).

### Principais Mudanças

1. **Arquitetura REST**: Todos os endpoints agora seguem padrões REST
2. **DRF APIView**: Conversão de views baseadas em templates para APIView
3. **Documentação Swagger**: Implementação completa com drf-spectacular
4. **Autenticação por Token**: Suporte a autenticação via token
5. **CORS**: Configurado para permitir requisições cross-origin

## 📚 Documentação Interativa

### Swagger UI
Acesse a documentação interativa da API em:
```
http://localhost:8000/api/docs/
```

### ReDoc
Documentação alternativa em:
```
http://localhost:8000/api/redoc/
```

### Schema OpenAPI
Schema da API em formato JSON:
```
http://localhost:8000/api/schema/
```

## 🔐 Autenticação

A API suporta dois tipos de autenticação:

1. **Session Authentication**: Para compatibilidade com o sistema existente
2. **Token Authentication**: Para aplicações frontend/mobile

### Login
```bash
POST /api/v1/auth/login/
{
    "username": "12345678901",
    "password": "senha123"
}
```

### Registro
```bash
POST /api/v1/auth/register/
{
    "username": "usuario123",
    "password": "senha123",
    "password_confirm": "senha123",
    "name": "João Silva",
    "cpf": "12345678901",
    "email": "joao@email.com",
    "phone": "(11) 99999-9999"
}
```

## 📋 Endpoints Principais

### Autenticação (`/api/v1/auth/`)
- `POST /login/` - Login de usuário
- `POST /register/` - Registro de usuário
- `POST /password-reset/` - Reset de senha

### Contas (`/api/v1/accounts/`)
- `GET /cities/search/` - Busca de cidades
- `POST /employees/register/` - Registro de funcionário
- `GET /employees/list/` - Lista de funcionários
- `POST /employees/toggle-status/` - Ativar/desativar funcionário
- `POST /clients/register/` - Registro de cliente
- `GET /clients/search/` - Busca cliente por CPF

### Produtos (`/api/v1/products/`)
- `GET /dashboard/` - Dashboard de produtos
- `GET /` - Lista de produtos
- `POST /create/` - Criar produto
- `PUT /{id}/update/` - Atualizar produto
- `POST /stock/update/` - Atualizar estoque
- `GET /{id}/qr-code/` - Gerar QR Code
- `GET /colors/` - Lista de cores
- `POST /temporary-products/create/` - Criar produto temporário
- `GET /catalogs/` - Lista de catálogos

### Ordens de Serviço (`/api/v1/service-orders/`)
- `GET /dashboard/` - Dashboard de OS
- `GET /` - Lista de ordens de serviço
- `POST /create/` - Criar ordem de serviço
- `GET /{id}/` - Detalhes da OS
- `PUT /{id}/update/` - Atualizar OS
- `POST /{id}/mark-paid/` - Marcar como paga
- `POST /{id}/refuse/` - Recusar OS
- `GET /{id}/client/` - Dados do cliente
- `GET /phase/{phase_name}/` - Listar por fase

## 🔄 Compatibilidade

### URLs Legadas Mantidas
Para garantir compatibilidade durante a transição, todas as URLs antigas foram mantidas:

- `/api/register_client/`
- `/api/v1/os/`
- `/funcionarios/api/`
- `/city-search/`
- `/list-colors/`
- E todas as outras URLs existentes

### Migração Gradual
A migração pode ser feita gradualmente:
1. Manter o frontend atual funcionando com as URLs legadas
2. Desenvolver novo frontend consumindo a API REST
3. Remover URLs legadas após confirmação de funcionamento

## 🛠️ Configuração

### Dependências Adicionadas
```python
# requirements.txt
djangorestframework==3.15.2
djangorestframework-simplejwt==5.5.0
drf-spectacular==0.28.0
django-cors-headers==4.7.0
```

### Configurações DRF
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

## 📊 Estrutura de Resposta

### Resposta Padrão
```json
{
    "success": true,
    "message": "Operação realizada com sucesso",
    "data": {...}
}
```

### Resposta de Erro
```json
{
    "error": "Descrição do erro",
    "details": {...}
}
```

### Paginação
```json
{
    "count": 100,
    "next": "http://api.example.org/accounts/?page=4",
    "previous": "http://api.example.org/accounts/?page=2",
    "results": [...]
}
```

## 🧪 Testes

### Exemplo de Uso com curl
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "12345678901", "password": "senha123"}'

# Listar produtos (com token)
curl -X GET http://localhost:8000/api/v1/products/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"

# Criar ordem de serviço
curl -X POST http://localhost:8000/api/v1/service-orders/create/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "João Silva",
    "telefone": "(11) 99999-9999",
    "cpf": "12345678901",
    "atendente": "Maria Santos",
    "origem": "Site",
    "data_evento": "2024-12-25",
    "tipo_servico": "Aluguel",
    "evento": "Casamento",
    "papel_evento": "Noivo"
  }'
```

## 🚀 Próximos Passos

1. **Frontend Moderno**: Desenvolver interface usando React/Vue.js
2. **Mobile App**: Criar aplicativo mobile consumindo a API
3. **Webhooks**: Implementar notificações em tempo real
4. **Cache**: Adicionar cache para melhorar performance
5. **Rate Limiting**: Implementar limitação de requisições
6. **Logs**: Sistema de logs estruturados
7. **Monitoramento**: Métricas e alertas

## 📞 Suporte

Para dúvidas ou problemas com a API:
- Email: suporte@roupadegala.com
- Documentação: `/api/docs/`
- Schema: `/api/schema/`

---

**Status**: ✅ Migração Completa
**Versão**: 1.0.0
**Data**: Dezembro 2024

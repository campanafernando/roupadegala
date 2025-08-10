# Exemplo de Uso da API de Atualização de OS

## Endpoint
```
PUT /api/service-orders/{order_id}/update/
```

## Payload Exemplo

```json
{
  "ordem_servico": {
    "data_pedido": "2024-06-01",
    "data_evento": "2024-06-10",
    "data_retirada": "2024-06-08",
    "ocasiao": "Casamento",
    "modalidade": "Aluguel",
    "itens": [
      {
        "tipo": "paleto",
        "numero": "44",
        "cor": "Azul",
        "manga": "32",
        "marca": "Aramis",
        "ajuste": "2",
        "extras": "Botão dourado"
      },
      {
        "tipo": "camisa",
        "numero": "M",
        "cor": "Branca",
        "manga": "32",
        "marca": "Dudalina",
        "ajuste": "1",
        "extras": ""
      },
      {
        "tipo": "calca",
        "numero": "40",
        "cor": "Preta",
        "cintura": "90",
        "perna": "100",
        "marca": "Aramis",
        "ajuste_cintura": "2",
        "ajuste_comprimento": "3",
        "extras": ""
      }
    ],
    "acessorios": [
      {
        "tipo": "suspensorio",
        "cor": "Preto"
      },
      {
        "tipo": "passante",
        "cor": "Prata",
        "extensor": true
      },
      {
        "tipo": "lenco",
        "cor": "Branco"
      },
      {
        "tipo": "gravata",
        "cor": "Vermelha",
        "descricao": "Lisa",
        "marca": "Pierre Cardin"
      },
      {
        "tipo": "cinto",
        "cor": "Preto",
        "marca": "Aramis"
      },
      {
        "tipo": "sapato",
        "numero": "42",
        "cor": "Preto",
        "descricao": "Verniz",
        "marca": "Ferracini"
      },
      {
        "tipo": "colete",
        "cor": "Cinza",
        "descricao": "Liso"
      }
    ],
    "pagamento": {
      "total": 500.00,
      "sinal": 100.00,
      "restante": 400.00
    }
  },
  "cliente": {
    "nome": "João da Silva",
    "cpf": "123.456.789-00",
    "contatos": [
      {
        "tipo": "telefone",
        "valor": "+5511999999999"
      }
    ],
    "enderecos": [
      {
        "cep": "12345-678",
        "rua": "Rua das Flores",
        "numero": "123",
        "bairro": "Centro",
        "cidade": "São Paulo"
      }
    ]
  }
}
```

## Resposta de Sucesso

```json
{
  "success": true,
  "message": "OS atualizada com sucesso",
  "service_order": {
    "id": 1,
    "event_date": "2024-06-10",
    "occasion": "CASAMENTO",
    "total_value": "500.00",
    "advance_payment": "100.00",
    "remaining_payment": "400.00",
    "renter": {
      "id": 1,
      "name": "JOÃO DA SILVA",
      "cpf": "12345678900"
    },
    "items": [
      {
        "id": 1,
        "temporary_product": {
          "id": 1,
          "product_type": "paleto",
          "size": "44",
          "color": "Azul",
          "brand": "Aramis",
          "extras": "Botão dourado"
        }
      }
    ]
  }
}
```

## Validações Automáticas

O serializer agora valida automaticamente:

- ✅ **Campos obrigatórios**: `data_evento`, `ocasiao`, `modalidade`, `pagamento`
- ✅ **Tipos de dados**: Datas, números decimais, strings
- ✅ **Choices**: `modalidade` deve ser "Aluguel" ou "Compra"
- ✅ **Campos opcionais**: Todos os outros campos são opcionais
- ✅ **Estrutura aninhada**: Validação completa da estrutura do payload

## Benefícios da Implementação

1. **Validação Automática**: O serializer valida todos os dados antes do processamento
2. **Documentação Clara**: Swagger/OpenAPI mostra exatamente o que esperar
3. **Facilita Integração**: Estrutura idêntica ao que o frontend enviará
4. **Tratamento de Erros**: Mensagens de erro claras para campos inválidos
5. **Flexibilidade**: Campos opcionais permitem payloads parciais

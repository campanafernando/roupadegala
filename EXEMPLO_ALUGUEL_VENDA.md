# Exemplo de Payload - Modalidade "Aluguel + Venda"

## 🎯 **Nova Modalidade Implementada**

A API agora suporta a modalidade **"Aluguel + Venda"** além das modalidades existentes.

## 📋 **Modalidades Disponíveis:**

1. **"Aluguel"** - Serviço de aluguel tradicional
2. **"Compra"** - Venda direta
3. **"Aluguel + Venda"** - **NOVA** - Combinação de aluguel com opção de compra

## ✅ **Exemplo de Payload com "Aluguel + Venda":**

```json
{
  "ordem_servico": {
    "data_pedido": "2024-06-01",
    "data_evento": "2024-06-10",
    "data_retirada": "2024-06-08",
    "ocasiao": "Casamento",
    "modalidade": "Aluguel + Venda",
    "itens": [
      {
        "tipo": "paleto",
        "numero": "44",
        "cor": "Azul",
        "manga": "32",
        "marca": "Aramis",
        "ajuste": "",
        "extras": ""
      },
      {
        "tipo": "camisa",
        "numero": "M",
        "cor": "Branca",
        "manga": "32",
        "marca": "Dudalina",
        "ajuste": "",
        "extras": ""
      }
    ],
    "acessorios": [
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

## 🔧 **Processamento da Modalidade:**

### **Lógica Implementada:**
```python
if modalidade == "Compra":
    service_order.purchase = True
elif modalidade == "Aluguel":
    service_order.purchase = False
elif modalidade == "Aluguel + Venda":
    service_order.purchase = False  # Mantém como aluguel

# Salvar modalidade no campo específico
service_order.service_type = modalidade
```

### **Comportamento:**
- ✅ **"Aluguel"** → `purchase = False`, `service_type = "Aluguel"`
- ✅ **"Compra"** → `purchase = True`, `service_type = "Compra"`
- ✅ **"Aluguel + Venda"** → `purchase = False`, `service_type = "Aluguel + Venda"`

## 🎯 **Benefícios:**

1. **✅ Flexibilidade**: Suporta modalidade híbrida
2. **✅ Rastreabilidade**: Modalidade salva nas observações
3. **✅ Compatibilidade**: Mantém lógica existente
4. **✅ Extensibilidade**: Fácil adicionar novas modalidades
5. **✅ Documentação**: Swagger atualizado automaticamente

## 🚀 **Resultado:**

A API agora suporta **3 modalidades** e está pronta para processar pedidos de "Aluguel + Venda" com total flexibilidade!

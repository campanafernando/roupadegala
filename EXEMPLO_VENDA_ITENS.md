# Exemplo de Payload com Campo Venda

## 🎯 **Campo `venda` Implementado**

A API agora suporta o campo `venda` para indicar se cada item/acessório foi vendido.

## ✅ **Exemplo de Payload Completo:**

```json
{
    "ordem_servico": {
        "data_pedido": "2025-07-27",
        "data_evento": "2025-08-07",
        "data_retirada": "2025-08-09",
        "ocasiao": "TESTE NOVA OS ATT ",
        "modalidade": "Aluguel + Venda",
        "itens": [
            {
                "tipo": "paleto",
                "numero": "42",
                "cor": "AZUL BEBE OPACO",
                "manga": "22",
                "marca": "3",
                "ajuste": "",
                "extras": "",
                "venda": true
            },
            {
                "tipo": "camisa",
                "numero": "EXG",
                "cor": "AZUL BRILHO",
                "manga": "69",
                "marca": "37",
                "ajuste": "",
                "extras": "gordão",
                "venda": true
            },
            {
                "tipo": "calca",
                "numero": "70",
                "cor": "AZUL ACETINADO",
                "cintura": "33",
                "perna": "46",
                "marca": "33",
                "ajuste_cintura": "",
                "ajuste_comprimento": "36",
                "extras": "",
                "venda": true
            }
        ],
        "acessorios": [
            {
                "tipo": "suspensorio",
                "cor": "AZUL FOSCO",
                "venda": false
            },
            {
                "tipo": "sapato",
                "numero": "42",
                "cor": "AZUL ACETINADO",
                "descricao": "",
                "marca": "21",
                "venda": true
            }
        ],
        "pagamento": {
            "total": 3123.32,
            "sinal": 1231.23,
            "restante": 1892.09
        }
    },
    "cliente": {
        "nome": "FOI O NICHOLAS",
        "cpf": "36500196040",
        "contatos": [
            {
                "tipo": "telefone",
                "valor": "5534995656961"
            }
        ],
        "enderecos": [
            {
                "cep": "38400652",
                "rua": "Rua Santa Catarina",
                "numero": "123",
                "bairro": "Brasil",
                "cidade": "UBERLÂNDIA"
            }
        ]
    }
}
```

## 🔧 **Implementação:**

### **1. Model TemporaryProduct:**
```python
venda = models.BooleanField(
    default=False,
    null=True,
    blank=True,
    help_text="Indica se o item foi vendido"
)
```

### **2. Serializers:**
```python
# FrontendOrderItemSerializer
venda = serializers.BooleanField(
    required=False,
    default=False,
    help_text="Indica se o item foi vendido"
)

# FrontendAccessorySerializer
venda = serializers.BooleanField(
    required=False,
    default=False,
    help_text="Indica se o acessório foi vendido"
)
```

### **3. Processamento na View:**
```python
# Para itens
temp_product = TemporaryProduct.objects.create(
    # ... outros campos
    venda=item.get("venda", False),
    created_by=request.user,
)

# Para acessórios
temp_product = TemporaryProduct.objects.create(
    # ... outros campos
    venda=acessorio.get("venda", False),
    created_by=request.user,
)
```

## 📋 **Comportamento:**

| **Campo `venda`** | **Salvo no Banco** | **Descrição** |
|------------------|-------------------|---------------|
| `true` | `True` | Item foi vendido |
| `false` | `False` | Item não foi vendido |
| Ausente | `False` | Padrão para não vendido |

## 🎯 **Benefícios:**

1. **✅ Rastreabilidade**: Saber quais itens foram vendidos
2. **✅ Relatórios**: Fácil gerar relatórios de vendas
3. **✅ Controle**: Distinguir aluguel de venda por item
4. **✅ Flexibilidade**: Cada item pode ter status diferente
5. **✅ Compatibilidade**: Campo opcional, não quebra payloads antigos

## 🚀 **Resultado:**

A API agora captura e salva a informação de venda para cada item/acessório, facilitando a listagem e relatórios posteriores!

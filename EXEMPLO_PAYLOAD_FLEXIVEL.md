# Exemplo de Payload Flexível - Campos Vazios Aceitos

## ✅ Payload que Funciona Agora

```json
{
  "ordem_servico": {
    "data_pedido": "2024-06-01",
    "data_evento": "2024-06-10",
    "data_retirada": "2024-06-08",
    "ocasiao": "Casamento",
    "modalidade": "Aluguel", // ou "Compra" ou "Aluguel + Venda"
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
      },
      {
        "tipo": "calca",
        "numero": "40",
        "cor": "Preta",
        "cintura": "90",
        "perna": "100",
        "marca": "Aramis",
        "ajuste_cintura": "",
        "ajuste_comprimento": "",
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
        "numero": "41",
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

## 🔧 **Tratamentos Implementados**

### **1. Serializer Flexível:**
- ✅ `allow_blank=True`: Aceita strings vazias
- ✅ `allow_null=True`: Aceita valores null
- ✅ `required=False`: Campos opcionais

### **2. Função de Limpeza na View:**
```python
def clean_field(value):
    return value if value and value.strip() else None
```

### **3. Campos Tratados:**
- ✅ `numero` → `size`
- ✅ `cor` → `color`
- ✅ `manga` → `sleeve_length`
- ✅ `marca` → `brand`
- ✅ `ajuste` → `adjustment_notes`
- ✅ `extras` → `description`
- ✅ `cintura` → `waist_size`
- ✅ `perna` → `leg_length`
- ✅ `ajuste_cintura` → `waist_adjustment`
- ✅ `ajuste_comprimento` → `length_adjustment`

### **4. Comportamento:**
- **String vazia `""`** → Salva como `NULL` no banco
- **String com espaços `"   "`** → Salva como `NULL` no banco
- **String válida `"Azul"`** → Salva normalmente
- **Campo ausente** → Salva como `NULL` no banco

## 🎯 **Benefícios:**

1. **Flexibilidade Total**: Frontend pode enviar campos vazios
2. **Dados Limpos**: Campos vazios são convertidos para NULL
3. **Validação Suave**: Não gera erros para campos em branco
4. **Compatibilidade**: Funciona com diferentes formatos de dados
5. **Facilita Desenvolvimento**: Frontend pode implementar validações gradualmente

## 🚀 **Resultado:**

Agora o payload com campos vazios será aceito e processado corretamente, salvando `NULL` no banco de dados para campos em branco!

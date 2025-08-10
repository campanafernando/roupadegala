# 📏 Campo de Tamanho para Sapatos e Acessórios

## 🎯 **Objetivo**

Adicionar suporte ao campo `numero` (tamanho) para acessórios como sapatos, permitindo que sejam salvos e retornados corretamente na listagem de ordens de serviço.

## 🔧 **Implementação Realizada**

### **1. Serializer de Acessórios Atualizado**

O `FrontendAccessorySerializer` agora inclui o campo `numero`:

```python
class FrontendAccessorySerializer(serializers.Serializer):
    """Serializer para acessórios do payload do frontend"""

    tipo = serializers.CharField(help_text="Tipo do acessório")
    numero = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Número/tamanho do acessório",
    )
    cor = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, help_text="Cor do acessório"
    )
    # ... outros campos
```

### **2. Processamento na View Atualizado**

A view `ServiceOrderUpdateAPIView` agora processa o campo `numero` dos acessórios:

```python
# Processar acessórios
for acessorio in data["ordem_servico"]["acessorios"]:
    temp_product = TemporaryProduct.objects.create(
        product_type=acessorio["tipo"],
        size=clean_field(acessorio.get("numero")),  # ✅ Campo adicionado
        color=clean_field(acessorio.get("cor")),
        brand=clean_field(acessorio.get("marca")),
        # ... outros campos
    )
```

### **3. Modelo TemporaryProduct**

O campo `size` já existia no modelo e agora é preenchido corretamente:

```python
class TemporaryProduct(BaseModel):
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    size = models.CharField(max_length=10, null=True, blank=True)  # ✅ Para tamanho
    # ... outros campos
```

## 📋 **Como Usar**

### **Exemplo de Payload para Sapato:**

```json
{
  "ordem_servico": {
    "acessorios": [
      {
        "tipo": "sapato",
        "numero": "42",
        "cor": "Preto",
        "marca": "Ferracini",
        "descricao": "Verniz",
        "venda": false
      }
    ]
  }
}
```

### **Exemplo de Payload para Outros Acessórios com Tamanho:**

```json
{
  "ordem_servico": {
    "acessorios": [
      {
        "tipo": "cinto",
        "numero": "L",
        "cor": "Marrom",
        "marca": "Aramis"
      },
      {
        "tipo": "suspensorio",
        "numero": "M",
        "cor": "Azul"
      }
    ]
  }
}
```

## 🔄 **Fluxo de Dados**

1. **Frontend envia**: Campo `numero` no acessório
2. **Serializer valida**: Campo opcional, pode ser vazio ou nulo
3. **View processa**: Salva no campo `size` do `TemporaryProduct`
4. **API retorna**: Campo `size` incluído na listagem através do `ServiceOrderSerializer`

## 📊 **Campos Retornados na Listagem**

```json
{
  "service_order": {
    "items": [
      {
        "temporary_product": {
          "id": 1,
          "product_type": "sapato",
          "size": "42",           // ✅ Tamanho do sapato
          "color": "Preto",
          "brand": "Ferracini",
          "description": "Verniz"
        }
      }
    ]
  }
}
```

## 🎯 **Tipos de Acessórios que Suportam Tamanho**

- **Sapatos**: Tamanho numérico (38, 39, 40, 41, 42, etc.)
- **Cintos**: Tamanho alfabético (S, M, L, XL)
- **Suspensórios**: Tamanho alfabético (S, M, L, XL)
- **Outros**: Qualquer acessório que precise de tamanho

## ✅ **Benefícios da Implementação**

1. **Tamanho de Sapato**: Agora sapatos podem ter tamanho específico
2. **Flexibilidade**: Qualquer acessório pode ter tamanho
3. **Consistência**: Mesmo padrão usado para itens de roupa
4. **Rastreabilidade**: Tamanho salvo e retornado corretamente
5. **Compatibilidade**: Não quebra implementações existentes

## 🔍 **Validações**

- **Campo opcional**: Pode ser omitido
- **Valor vazio**: Convertido para `null` no banco
- **Tipo de dados**: Sempre string
- **Tamanho máximo**: 10 caracteres (definido no modelo)

## 🚀 **Próximos Passos**

1. **Testar**: Verificar se o campo está sendo salvo corretamente
2. **Validar**: Confirmar se está sendo retornado na listagem
3. **Documentar**: Atualizar documentação da API
4. **Frontend**: Atualizar interface para incluir campo de tamanho

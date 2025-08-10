# Validações da Importação de Produtos via Excel

## 📋 **Campos Obrigatórios**

A API agora valida rigorosamente os seguintes campos obrigatórios:

| Campo | Descrição | Validação |
|-------|-----------|-----------|
| **Tipo** | Tipo do produto (Paletó, Calça, Colete) | Não pode estar vazio, ser "nan" ou nulo |
| **ID** | ID único do produto | Não pode estar vazio, ser "nan" ou nulo |
| **Nome do produto** | Nome descritivo do produto | Não pode estar vazio, ser "nan" ou nulo |
| **Marca** | Marca/fabricante do produto | Não pode estar vazio, ser "nan" ou nulo |
| **Material** | Composição do material | Não pode estar vazio, ser "nan" ou nulo |
| **Cor** | Cor principal do produto | Não pode estar vazio, ser "nan" ou nulo |
| **Intensidade de cor** | Intensidade da cor (Fosco, Acetinado) | Não pode estar vazio, ser "nan" ou nulo |
| **Tamanho** | Tamanho numérico do produto | Deve ser um número válido > 0, não pode ser "nan" |

## 🔍 **Campos Opcionais**

Os seguintes campos são opcionais e podem ser "nan" ou vazios:

| Campo | Descrição | Tratamento |
|-------|-----------|------------|
| **Padronagem** | Padrão do tecido | Se "nan", salva como string vazia |
| **Botões** | Tipo de botões (Um, Duplo) | Se "nan", salva como None |
| **Lapela** | Tipo de lapela (Bico, Shale) | Se "nan", salva como None |
| **Foto** | Caminho para a foto | Se "nan", ignora o processamento |

## ✅ **Validações Implementadas**

### 1. **Validação de Campos Obrigatórios**
```python
def _validate_required_field(self, value, field_name, row_index):
    """Valida se um campo obrigatório está preenchido e não é 'nan'"""
    if pd.isna(value) or str(value).strip() == "" or str(value).strip().lower() == "nan":
        raise ValueError(f"Linha {row_index + 2}: Campo '{field_name}' é obrigatório e não pode estar vazio ou 'nan'")
    return str(value).strip()
```

### 2. **Validação Específica do Campo Tamanho**
```python
def _validate_tamanho_field(self, value, row_index):
    """Valida se o campo tamanho é um número válido"""
    if pd.isna(value) or str(value).strip() == "" or str(value).strip().lower() == "nan":
        raise ValueError(f"Linha {row_index + 2}: Campo 'Tamanho' é obrigatório e não pode estar vazio ou 'nan'")

    try:
        tamanho = float(value)
        if tamanho <= 0:
            raise ValueError(f"Linha {row_index + 2}: Campo 'Tamanho' deve ser um número maior que zero")
        return tamanho
    except (ValueError, TypeError):
        raise ValueError(f"Linha {row_index + 2}: Campo 'Tamanho' deve ser um número válido")
```

### 3. **Validação de Colunas do Excel**
```python
required_columns = [
    "Tipo",
    "ID",
    "Nome do produto",
    "Marca",
    "Material",
    "Cor",
    "Intensidade de cor",
    "Tamanho",
]
```

## 🚫 **Casos Rejeitados**

### **Campos Obrigatórios Vazios ou "nan"**
- ❌ `"Tipo": ""` → **REJEITADO**
- ❌ `"Tipo": "nan"` → **REJEITADO**
- ❌ `"Tipo": null` → **REJEITADO**

### **Tamanho Inválido**
- ❌ `"Tamanho": "nan"` → **REJEITADO**
- ❌ `"Tamanho": 0` → **REJEITADO**
- ❌ `"Tamanho": -1` → **REJEITADO**
- ❌ `"Tamanho": "abc"` → **REJEITADO**

### **Colunas Ausentes**
- ❌ Arquivo sem coluna "Tamanho" → **REJEITADO**
- ❌ Arquivo sem coluna "Cor" → **REJEITADO**

## ✅ **Casos Aceitos**

### **Dados Válidos**
```excel
Tipo        | ID      | Nome do produto | Marca        | Material              | Cor           | Intensidade de cor | Tamanho
Paletó      | P000001 | Paletó Azul     | Turco Sivis  | Poliviscose/Elastano | Azul Celeste  | Fosco             | 48.00
```

### **Campos Opcionais com "nan"**
```excel
Botões      | Lapela
nan         | nan
```
→ **ACEITO** (salva como None)

## 📊 **Resposta da API**

### **Sucesso com Erros**
```json
{
    "success": true,
    "message": "Processamento concluído. 5 produtos criados, 3 atualizados",
    "products_created": 5,
    "products_updated": 3,
    "errors": [
        "Linha 16: Campo 'Tipo' é obrigatório e não pode estar vazio ou 'nan'",
        "Linha 17: Campo 'Tamanho' deve ser um número maior que zero"
    ]
}
```

### **Erro de Validação**
```json
{
    "error": "Colunas obrigatórias não encontradas: Tamanho"
}
```

## 🧪 **Testes Implementados**

O arquivo `products/test_excel_import.py` contém testes abrangentes para:

1. **Validação de campos obrigatórios vazios**
2. **Rejeição de valores 'nan' em campos obrigatórios**
3. **Validação específica do campo tamanho**
4. **Importação de dados válidos**
5. **Tratamento de campos opcionais com 'nan'**
6. **Detecção de colunas obrigatórias ausentes**
7. **Validação de tamanho zero**

## 🔧 **Como Executar os Testes**

```bash
# Executar todos os testes de validação
python3 manage.py test products.test_excel_import -v 2

# Executar teste específico
python3 manage.py test products.test_excel_import.ExcelImportValidationTest.test_nan_values_validation
```

## 📝 **Exemplo de Uso no Frontend**

```javascript
// Exemplo de upload de arquivo Excel
const formData = new FormData();
formData.append('excel_file', excelFile);

const response = await fetch('/api/v1/products/stock/update/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`
    },
    body: formData
});

const result = await response.json();

if (result.success) {
    console.log(`Produtos criados: ${result.products_created}`);
    console.log(`Produtos atualizados: ${result.products_updated}`);

    if (result.errors.length > 0) {
        console.log('Erros encontrados:', result.errors);
    }
} else {
    console.error('Erro na importação:', result.error);
}
```

## 🎯 **Benefícios das Validações**

1. **Qualidade dos Dados**: Garante que apenas produtos válidos sejam salvos
2. **Prevenção de Erros**: Evita produtos com dados incompletos ou inválidos
3. **Feedback Claro**: Mensagens de erro específicas indicam exatamente o problema
4. **Consistência**: Padroniza o tratamento de campos obrigatórios vs. opcionais
5. **Auditoria**: Rastreia exatamente quais linhas tiveram problemas

---

**Status**: ✅ Implementado e Testado
**Versão**: 2.0.0
**Data**: Janeiro 2025

from rest_framework import serializers

from .models import (
    Brand,
    Button,
    Color,
    ColorCatalogue,
    ColorIntensity,
    Fabric,
    Lapel,
    Model,
    Pattern,
    Product,
    ProductType,
    TemporaryProduct,
)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class FabricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fabric
        fields = "__all__"


class ColorIntensitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorIntensity
        fields = "__all__"


class ColorCatalogueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorCatalogue
        fields = "__all__"


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class PatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pattern
        fields = "__all__"


class ButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Button
        fields = "__all__"


class LapelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lapel
        fields = "__all__"


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = "__all__"


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    # Campos relacionados para facilitar a visualização
    product_type_name = serializers.CharField(
        source="product_type.description", read_only=True
    )
    brand_name = serializers.CharField(source="brand.description", read_only=True)
    fabric_name = serializers.CharField(source="fabric.description", read_only=True)
    color_name = serializers.CharField(source="color.color.description", read_only=True)
    color_intensity_name = serializers.CharField(
        source="color.color_intensity.description", read_only=True
    )
    pattern_name = serializers.CharField(source="pattern.description", read_only=True)
    button_name = serializers.CharField(source="button.description", read_only=True)
    lapel_name = serializers.CharField(source="lapel.description", read_only=True)
    model_name = serializers.CharField(source="model.description", read_only=True)

    # Campos para compatibilidade com Excel
    tipo = serializers.CharField(source="product_type.description", read_only=True)
    excel_id = serializers.CharField(source="label_code", read_only=True)
    nome_do_produto = serializers.CharField(source="model.description", read_only=True)
    marca = serializers.CharField(source="brand.description", read_only=True)
    material = serializers.CharField(source="fabric.description", read_only=True)
    cor = serializers.CharField(source="color.color.description", read_only=True)
    intensidade_de_cor = serializers.CharField(
        source="color.color_intensity.description", read_only=True
    )
    padronagem = serializers.CharField(source="pattern.description", read_only=True)
    botoes = serializers.CharField(source="button.description", read_only=True)
    lapela = serializers.CharField(source="lapel.description", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "label_code",
            "on_stock",
            "date_created",
            "date_updated",
            "product_type",
            "brand",
            "fabric",
            "color",
            "pattern",
            "button",
            "lapel",
            "model",
            "product_type_name",
            "brand_name",
            "fabric_name",
            "color_name",
            "color_intensity_name",
            "pattern_name",
            "button_name",
            "lapel_name",
            "model_name",
            # Campos para compatibilidade com Excel
            "tipo",
            "excel_id",
            "nome_do_produto",
            "marca",
            "material",
            "cor",
            "intensidade_de_cor",
            "padronagem",
            "botoes",
            "lapela",
        ]


class TemporaryProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryProduct
        fields = "__all__"


# Serializers adicionais para corrigir erros do Swagger


class CatalogListSerializer(serializers.Serializer):
    """Serializer para listagem de catálogos"""

    pass


class ProductUpdateSerializer(serializers.Serializer):
    """Serializer para atualização de produtos"""

    product_type = serializers.IntegerField(help_text="ID do tipo de produto")
    brand = serializers.IntegerField(help_text="ID da marca")
    fabric = serializers.IntegerField(help_text="ID do tecido")
    color_catalogue = serializers.IntegerField(help_text="ID do catálogo de cores")
    color_intensity = serializers.IntegerField(help_text="ID da intensidade da cor")
    pattern = serializers.IntegerField(required=False, help_text="ID do padrão")
    button = serializers.IntegerField(required=False, help_text="ID do botão")
    lapel = serializers.IntegerField(required=False, help_text="ID da lapela")
    model = serializers.IntegerField(required=False, help_text="ID do modelo")
    on_stock = serializers.BooleanField(help_text="Disponível em estoque")


class ProductStockUpdateSerializer(serializers.Serializer):
    """Serializer para atualização de estoque"""

    product_id = serializers.IntegerField(help_text="ID do produto")
    on_stock = serializers.BooleanField(help_text="Disponível em estoque")
    canceled = serializers.BooleanField(required=False, help_text="Produto cancelado")


class TemporaryProductCreateSerializer(serializers.Serializer):
    """Serializer para criação de produtos temporários"""

    product_type = serializers.CharField(help_text="Tipo do produto")
    size = serializers.CharField(required=False, help_text="Tamanho")
    sleeve_length = serializers.CharField(
        required=False, help_text="Comprimento da manga"
    )
    leg_length = serializers.CharField(required=False, help_text="Comprimento da perna")
    waist_size = serializers.CharField(required=False, help_text="Tamanho da cintura")
    collar_size = serializers.CharField(
        required=False, help_text="Tamanho do colarinho"
    )
    color = serializers.CharField(help_text="Cor do produto")
    brand = serializers.CharField(required=False, help_text="Marca")
    fabric = serializers.CharField(required=False, help_text="Tecido")
    description = serializers.CharField(required=False, help_text="Descrição adicional")


class ProductExcelImportSerializer(serializers.Serializer):
    """Serializer para importação de produtos via Excel"""

    tipo = serializers.CharField(help_text="Tipo do produto (Paletó, Calça, Colete)")
    id = serializers.CharField(help_text="ID do produto (será usado como label_code)")
    nome_do_produto = serializers.CharField(help_text="Nome do produto")
    marca = serializers.CharField(help_text="Marca do produto")
    material = serializers.CharField(help_text="Material do produto")
    cor = serializers.CharField(help_text="Cor do produto")
    intensidade_de_cor = serializers.CharField(help_text="Intensidade da cor")
    padronagem = serializers.CharField(help_text="Padronagem do produto")
    botoes = serializers.CharField(
        required=False, allow_blank=True, help_text="Tipo de botões"
    )
    lapela = serializers.CharField(
        required=False, allow_blank=True, help_text="Tipo de lapela"
    )
    tamanho = serializers.FloatField(help_text="Tamanho do produto")
    foto = serializers.CharField(
        required=False, allow_blank=True, help_text="Campo para foto"
    )

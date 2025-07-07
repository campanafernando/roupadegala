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
    class Meta:
        model = Product
        fields = "__all__"


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

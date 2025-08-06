import base64
import os

from django.db import models

from accounts.models import BaseModel


# Modelos de catálogo de produtos
class Brand(BaseModel):
    description = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.description


class Fabric(BaseModel):
    description = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.description


class ColorIntensity(BaseModel):
    description = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "products_color_intensity"

    def __str__(self):
        return self.description


class ColorCatalogue(BaseModel):
    description = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "products_color_catalogue"

    def __str__(self):
        return self.description


class Color(BaseModel):
    color = models.ForeignKey(ColorCatalogue, on_delete=models.CASCADE)
    color_intensity = models.ForeignKey(ColorIntensity, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("color", "color_intensity")

    def __str__(self):
        return f"{self.color.description} - {self.color_intensity.description}"


class Pattern(BaseModel):
    description = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.description


class Button(BaseModel):
    description = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.description


class Lapel(BaseModel):
    description = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.description


class Model(BaseModel):
    description = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.description


class ProductType(BaseModel):
    description = models.CharField(max_length=100, unique=True)
    acronym = models.CharField(max_length=5, unique=True)

    class Meta:
        db_table = "products_type"

    def __str__(self):
        return self.description


# Produto real do estoque - ADAPTADO PARA SER COERENTE COM A PLANILHA EXCEL
class Product(BaseModel):
    # Campos principais da planilha
    tipo = models.CharField(
        max_length=50, help_text="Tipo do produto (Paletó, Calça, Colete)", default=""
    )
    id_produto = models.CharField(
        max_length=20,
        unique=True,
        help_text="ID único do produto (ex: P000001)",
        default="",
    )
    nome_produto = models.CharField(
        max_length=255, help_text="Nome descritivo do produto", default=""
    )
    marca = models.CharField(
        max_length=100, help_text="Marca/fabricante do produto", default=""
    )
    material = models.CharField(
        max_length=255, help_text="Composição do material", default=""
    )
    cor = models.CharField(
        max_length=100, help_text="Cor principal do produto", default=""
    )
    intensidade_cor = models.CharField(
        max_length=100, help_text="Intensidade da cor (Fosco, Acetinado)", default=""
    )
    padronagem = models.CharField(
        max_length=100, help_text="Padrão do tecido", default=""
    )
    botoes = models.CharField(
        max_length=50, blank=True, null=True, help_text="Tipo de botões (Um, Duplo)"
    )
    lapela = models.CharField(
        max_length=50, blank=True, null=True, help_text="Tipo de lapela (Bico, Shale)"
    )
    tamanho = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Tamanho numérico", default=0.00
    )
    foto_base64 = models.TextField(
        blank=True, null=True, help_text="Foto do produto em base64"
    )

    class Meta:
        db_table = "products"

    def __str__(self):
        return f"{self.tipo} - {self.id_produto} - {self.nome_produto}"

    def save_photo_from_file(self, file_path):
        """
        Salva uma foto do produto convertendo arquivo para base64
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                    self.foto_base64 = encoded_string
                    self.save()
                return True
            return False
        except Exception as e:
            print(f"Erro ao salvar foto: {e}")
            return False

    def save_photo_from_base64(self, base64_string):
        """
        Salva uma foto do produto diretamente em base64
        """
        try:
            self.foto_base64 = base64_string
            self.save()
            return True
        except Exception as e:
            print(f"Erro ao salvar foto base64: {e}")
            return False

    def get_photo_base64(self):
        """
        Retorna a foto em base64 se existir
        """
        return self.foto_base64 if self.foto_base64 else None


# Produto temporário (flexível para OS)
class TemporaryProduct(BaseModel):
    PRODUCT_TYPE_CHOICES = [
        ("paleto", "Paletó"),
        ("calca", "Calça"),
        ("camisa", "Camisa"),
        ("colete", "Colete"),
        ("gravata", "Gravata"),
        ("sapato", "Sapato"),
        ("suspensorio", "Suspensório"),
        ("cinto", "Cinto"),
        ("lenco", "Lenço"),
        ("passante", "Passante"),
    ]

    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    size = models.CharField(max_length=10, null=True, blank=True)
    sleeve_length = models.CharField(max_length=10, null=True, blank=True)
    leg_length = models.CharField(max_length=10, null=True, blank=True)
    waist_size = models.CharField(max_length=10, null=True, blank=True)
    collar_size = models.CharField(max_length=10, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    fabric = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    # Novos campos para acessórios
    extensor = models.BooleanField(default=False, null=True, blank=True)
    extras = models.CharField(max_length=255, null=True, blank=True)
    # Campo para indicar se foi vendido
    venda = models.BooleanField(
        default=False, null=True, blank=True, help_text="Indica se o item foi vendido"
    )

    class Meta:
        db_table = "temporary_products"

    def __str__(self):
        return f"{self.product_type} - {self.size}"

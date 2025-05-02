from django.db import models

from accounts.models import BaseModel


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
        return f"{self.description} - {self.color_intensity.description}"


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


class Product(BaseModel):
    product_type = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, related_name="products"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, related_name="products_by_brand"
    )
    fabric = models.ForeignKey(
        Fabric, on_delete=models.SET_NULL, null=True, related_name="products_by_fabric"
    )
    color = models.ForeignKey(
        Color, on_delete=models.SET_NULL, null=True, related_name="products_by_color"
    )
    pattern = models.ForeignKey(
        Pattern,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products_by_pattern",
    )
    button = models.ForeignKey(
        Button,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products_by_button",
    )
    lapel = models.ForeignKey(
        Lapel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products_by_lapel",
    )
    model = models.ForeignKey(
        Model,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products_by_model",
    )
    label_code = models.CharField(max_length=255, unique=True, blank=True)
    on_stock = models.BooleanField(default=True)

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.product_type.acronym

    def save(self, *args, **kwargs):
        if not self.label_code:
            count = (
                Product.objects.filter(
                    product_type=self.product_type, brand=self.brand, color=self.color
                ).count()
                + 1
            )

            sequencial = str(count).zfill(4)  # preenche com zeros à esquerda
            product_type_id = str(self.product_type.id)
            brand_id = str(self.brand.id if self.brand else 0)
            color_id = str(self.color.id if self.color else 0)

            self.label_code = f"{sequencial}.{product_type_id}{brand_id}{color_id}"

        super().save(*args, **kwargs)


class TemporaryProduct(BaseModel):
    PRODUCT_TYPE_CHOICES = [
        ("Paleto", "Paletó"),
        ("Calca", "Calça"),
        ("Camisa", "Camisa"),
        ("Colete", "Colete"),
        ("Gravata", "Gravata"),
        ("Sapato", "Sapato"),
        ("Suspensorio", "Suspensório"),
        ("Cinto", "Cinto"),
        ("Lenco", "Lenço"),
    ]

    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    size = models.CharField(max_length=10, null=True, blank=True)
    sleeve_length = models.CharField(max_length=10, null=True, blank=True)
    leg_length = models.CharField(max_length=10, null=True, blank=True)
    waist_size = models.CharField(max_length=10, null=True, blank=True)
    collar_size = models.CharField(max_length=10, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "temporary_products"

    def __str__(self):
        return f"{self.product_type} - {self.size}"

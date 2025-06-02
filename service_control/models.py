from django.db import models

from accounts.models import BaseModel, Person
from products.models import ColorCatalogue, Product, TemporaryProduct


class ServiceOrderPhase(BaseModel):
    name = models.CharField(max_length=20)


class ServiceOrder(BaseModel):
    renter = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="service_orders"
    )
    employee = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="employee_service_orders",
        null=True,
    )
    attendant = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="attendant_service_orders",
        null=True,
    )
    order_date = models.DateField()
    event_date = models.DateField()
    occasion = models.CharField(max_length=255)
    renter_role = models.CharField(max_length=255, null=True)
    total_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True
    )
    advance_payment = (
        models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True),
    )
    remaining_payment = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True
    )
    max_payment_date = models.DateField(null=True, default=None)
    payment_method = models.CharField(max_length=255, null=True)
    adjustment_needed = models.BooleanField(default=None, null=True)
    came_from = models.CharField(max_length=255, default=None, null=True)
    purchase = models.BooleanField(default=False)
    observations = models.TextField(null=True, blank=True)
    service_order_phase = models.ForeignKey(
        ServiceOrderPhase, on_delete=models.SET_NULL, null=True
    )
    justification_refusal = models.TextField(null=True, blank=True, default=None)

    class Meta:
        db_table = "service_orders"

    def __str__(self):
        return f"OS {self.id} - {self.renter.name}"


class ServiceOrderItem(BaseModel):
    service_order = models.ForeignKey(
        ServiceOrder, related_name="items", on_delete=models.CASCADE
    )
    temporary_product = models.ForeignKey(
        TemporaryProduct,
        related_name="order_items",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    product = models.ForeignKey(
        Product,
        related_name="order_items",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    color_catalogue = models.ForeignKey(
        ColorCatalogue,
        related_name="order_items",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    adjustment_needed = models.BooleanField(default=False)
    adjustment_value = models.IntegerField(null=True)
    adjustment_notes = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "service_order_items"

    def __str__(self):
        prod_desc = self.product if self.product else self.temporary_product
        return f"{self.service_order.id} - {prod_desc}"

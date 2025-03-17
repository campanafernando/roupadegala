from django.db import models
from accounts.models import BaseModel
from django.contrib.auth.models import User


# class ServiceOrder(BaseModel):
#     order_date = models.DateField()
#     return_date = models.DateField()
#     suit_measure = models.IntegerField()
#     shirt_measure = models.IntegerField()
#     pants_measure = models.IntegerField()
#     occasion = models.CharField(max_length=255) 

#     renter = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="renter_%(class)s")

#     class Meta:
#         db_table = "service_order"  

#     def __str__(self):
#         return f"{self.nome} ({self.person_type.nome})" 
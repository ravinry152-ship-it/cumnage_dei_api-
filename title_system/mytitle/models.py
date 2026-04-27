from django.db import models
from django.contrib.auth.models import User

class CreateSystem(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='system')
    name = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CRUD(models.Model):
    id = models.AutoField(primary_key=True)
    system = models.ForeignKey(CreateSystem, on_delete=models.CASCADE, related_name='data_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200) 
    price = models.DecimalField(max_digits=30, decimal_places=2)
    village = models.CharField(max_length=200) 

    def __str__(self):
        return self.name
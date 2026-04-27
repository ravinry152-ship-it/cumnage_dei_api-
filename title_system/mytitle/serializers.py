from rest_framework import serializers
from .models import CreateSystem , CRUD

class CreateSystemSerializer(serializers.ModelSerializer):
    class Meta :
        model = CreateSystem
        fields = ['id', 'name', 'created_at']

class CRUDSerializer(serializers.ModelSerializer):
    class Meta :
        model = CRUD
        fields = ['id', 'name', 'price', 'village']
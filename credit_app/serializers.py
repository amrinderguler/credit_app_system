# import serializer from rest_framework
from rest_framework import serializers

# import model from models.py
from .models import *

class CustomerSerializers(serializers.ModelSerializer):
	# specify model and fields
	class Meta:
		model = Customer
		fields = '__all__'


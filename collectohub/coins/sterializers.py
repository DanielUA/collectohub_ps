from rest_framework import serializers
from .models import *

class CoinsSerializer1(serializers.ModelSerializer):
    country = serializers.StringRelatedField()
    class Meta:
        model = Coin
        fields = ['country', 'denomination', 'year', 'id']

class CoinsSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = "__all__"

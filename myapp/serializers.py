from rest_framework import serializers

class PriceInfoSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=20, decimal_places=10)
    liquidity = serializers.DecimalField(max_digits=20, decimal_places=10)

class TokenOverviewSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=20, decimal_places=10)
    symbol = serializers.CharField(max_length=100)
    decimals = serializers.IntegerField()
    lastTradeUnixTime = serializers.IntegerField()
    liquidity = serializers.DecimalField(max_digits=20, decimal_places=10)
    supply = serializers.DecimalField(max_digits=20, decimal_places=10)

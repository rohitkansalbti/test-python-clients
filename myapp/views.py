from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status

from .serializers import PriceInfoSerializer, TokenOverviewSerializer
from clients.dexscreener import DexScreenerClient
from clients.birdeye import BirdEyeClient

class DexPricesView(APIView):
    def get(self, request, *args, **kwargs):
        token_addresses = request.query_params.getlist('token_addresses')
        if not token_addresses:
            raise ValidationError("token_addresses query parameter is required")
        
        client = DexScreenerClient()
        try:
            prices = client.fetch_prices_dex(token_addresses)
            serializer = PriceInfoSerializer(prices.values(), many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DexTokenOverviewView(APIView):
    def get(self, request, address, *args, **kwargs):
        client = DexScreenerClient()
        try:
            overview = client.fetch_token_overview(address)
            serializer = TokenOverviewSerializer(overview)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BirdPricesView(APIView):
    def get(self, request, *args, **kwargs):
        token_addresses = request.query_params.getlist('token_addresses')
        if not token_addresses:
            raise ValidationError("token_addresses query parameter is required")
        
        client = BirdEyeClient()
        try:
            prices = client.fetch_prices(token_addresses)
            serializer = PriceInfoSerializer(prices.values(), many=True)
            return Response(serializer.data)
            return prices
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BirdTokenOverviewView(APIView):
    def get(self, request, address, *args, **kwargs):
        client = BirdEyeClient()
        try:
            overview = client.fetch_token_overview(address)
            serializer = TokenOverviewSerializer(overview)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

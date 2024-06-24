import requests
from decimal import Decimal
from typing import Any, Dict, List
import urllib.parse


from clients.common import PriceInfo, TokenOverview
from clients.custom_exceptions import InvalidSolanaAddress, InvalidTokens, NoPositionsError
# from utils.helpers import is_solana_address
# from vars.constants import SOL_MINT

class BirdEyeClient:
    """
    Handler class to assist with all calls to BirdEye API
    """

    @property
    def _headers(self):
        return {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": '5d264e2d492447d5ab323e',
        }

    def _make_api_call(self, method: str, query_url: str, *args, **kwargs) -> requests.Response:
        method_upper = method.upper()
        if method_upper == "GET":
            query_method = requests.get
        elif method_upper == "POST":
            query_method = requests.post
        else:
            raise ValueError(f'Unrecognised method "{method}" passed for query - {query_url}')
        
        resp = query_method(query_url, *args, headers=self._headers, **kwargs)
        return resp

    def fetch_prices(self, token_addresses: List[str]) -> Dict[str, PriceInfo]:
        """
        For a list of tokens fetches their prices
        via multi-price API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[str, PriceInfo[Decimal, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity

        Raises:
            NoPositionsError: Raise if no tokens are provided
            InvalidToken: Raised if the API call was unsuccessful
        """
        token_addresses_str = ','.join(token_addresses)
        encoded_token_addresses_str = urllib.parse.quote(token_addresses_str)
        query_url = f"https://public-api.birdeye.so/defi/price?address={encoded_token_addresses_str}"

        resp = self._make_api_call("GET", query_url)
        
        if resp.status_code != 200:
            raise InvalidTokens(f"Failed to fetch prices: {resp.status_code}")
        resp = self._make_api_call("GET", query_url)
        resp.raise_for_status()
        return resp.json()


    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via multi-price API ensuring each token has a price

        Args:
            address (str): A token address for which to fetch overview

        Returns:
            dict[str, float | str]: Overview with a lot of token information I don't understand

        Raises:
            InvalidSolanaAddress: Raise if invalid solana address is passed
            InvalidToken: Raised if the API call was unsuccessful
       """


        if not is_solana_address(address):
            raise InvalidSolanaAddress(f"Invalid Solana address: {address}")

        query_url = f"https://public-api.birdeye.so/public/overview/{address}"
        resp = self._make_api_call("GET", query_url)
        self._validate_response(resp)

        data = resp.json()

        if 'price' not in data or 'symbol' not in data or 'decimals' not in data:
            raise InvalidTokens(f"Invalid token data received for address: {address}")

        return TokenOverview(
            price=Decimal(data['price']),
            symbol=data['symbol'],
            decimals=int(data['decimals']),
            lastTradeUnixTime=int(data.get('lastTradeUnixTime', 0)),
            liquidity=Decimal(data.get('liquidity', 0)),
            supply=Decimal(data.get('supply', 0))
        )
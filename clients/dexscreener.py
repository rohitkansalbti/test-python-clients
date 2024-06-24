"""
Client for DexScreener APIs
"""

from decimal import Decimal
from typing import Any, List, Dict
import urllib.parse

import requests

from clients.common import PriceInfo, TokenOverview
from clients.custom_exceptions import InvalidSolanaAddress, InvalidTokens, NoPositionsError
# from utils.helpers import is_solana_address
# from vars.constants import SOL_MINT


class DexScreenerClient:
    """
    Handler class to assist with all calls to DexScreener API
    """

    @staticmethod
    def _validate_token_address(token_address: str):
        """
        Validates token address to be a valid solana address

        Args:
            token_address (str): Token address to validate

        Returns:
            None: If token address is valid

        Raises:
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """
        if not token_address:
            raise NoPositionsError("Token address is empty")
        if not is_solana_address(token_address):
            raise InvalidSolanaAddress(f"Invalid Solana address: {token_address}")



    def _validate_token_addresses(self, token_addresses: List[str]):
        """
        Validates token addresses to be a valid solana address

        Args:
            token_addresses (list[str]): Token addresses to validate

        Returns:
            None: If token addresses are valid

        Raises:
            NoPositionsError: If token addresses are empty
            InvalidSolanaAddress: If any token address is not a valid solana address
        """
        if not token_addresses:
            raise NoPositionsError("Token addresses are empty")
        for address in token_addresses:
            self._validate_token_address(address)


    @staticmethod
    def _validate_response(resp: requests.Response):
        """
        Validates response from API to be 200

        Args:
            resp (requests.Response): Response from API

        Returns:
            None: If response is 200

        Raises:
            InvalidTokens: If response is not 200
        """
        if resp.status_code == 200:
            return None
        else:
            raise InvalidTokens()

    def _call_api(self, token_address: str) -> Dict[str, Any]:
        """
        Calls DexScreener API for a single token

        Args:
            token_address (str): Token address for which to fetch data

        Returns:
            dict[str, Any]: JSON response from API

        Raises:
            InvalidTokens: If response is not 200
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """

        self._validate_token_address(token_address)
        encoded_token_addresses_str = urllib.parse.quote(token_address)
        url = f"https://api.dexscreener.com/latest/dex/tokens/{encoded_token_addresses_str}"
        resp = requests.get(url)
        self._validate_response(resp)
        return resp.json()


    def _call_api_bulk(self, token_addresses: List[str]) -> Dict[str, Any]:
        """
        Calls DexScreener API for multiple tokens

        Args:
            token_addresses (list[str]): Token addresses for which to fetch data

        Returns:
            dict[str, Any]: JSON response from API

        Raises:
            InvalidTokens: If response is not 200
            NoPositionsError: If token addresses are empty
            InvalidSolanaAddress: If any token address is not a valid solana address
        """

        self._validate_token_addresses(token_addresses)
        url = f"https://api.dexscreener.com/latest/dex/tokens?address={','.join(token_addresses)}"
        resp = requests.get(url)
        self._validate_response(resp)
        return resp.json()

    def fetch_prices_dex(self, token_addresses: List[str]) -> Dict[str, PriceInfo]:
        """
        For a list of tokens fetches their prices
        via multi API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[Decimal, PriceInfo[str, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity in Decimal

        """
        data = self._call_api_bulk(token_addresses)
        prices = {}
        for token in data.get("tokens", []):
            address = token["address"]
            price_usd = Decimal(token["price"]["usd"])
            liquidity_usd = Decimal(token["liquidity"]["usd"])
            prices[address] = PriceInfo(price=price_usd, liquidity=liquidity_usd)
        return prices



    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via Dex API ensuring each token has a price

        Args:
        address (str): A token address for which to fetch overview

        Returns:
        TokenOverview: Overview with a lot of token information I don't understand
        """
        data = self._call_api(address)
        token_info = data.get("token", {})
        return TokenOverview(
            price=Decimal(token_info["price"]["usd"]),
            symbol=token_info.get("symbol", ""),
            decimals=int(token_info.get("decimals", 0)),
            lastTradeUnixTime=int(token_info.get("lastTradeUnixTime", 0)),
            liquidity=Decimal(token_info["liquidity"]["usd"]),
            supply=Decimal(token_info.get("supply", 0)),
        )

    @staticmethod
    def find_largest_pool_with_sol(token_pairs, address):
        max_entry = {}
        max_liquidity_usd = -1

        for entry in token_pairs:
            # Check if the baseToken address matches the specified address
            if entry.get("baseToken", {}).get("address") == address and entry["quoteToken"]["address"] == SOL_MINT:
                liquidity_usd = float(entry.get("liquidity", {}).get("usd", 0))
                if liquidity_usd > max_liquidity_usd:
                    max_liquidity_usd = liquidity_usd
                    max_entry = entry
        return max_entry

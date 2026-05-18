import hashlib
import hmac
import logging
import os
import time
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class BinanceAPIError(Exception):
    def __init__(self, status_code: int, error_code: int, error_msg: str):
        self.status_code = status_code
        self.error_code = error_code
        self.error_msg = error_msg
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return f"BinanceAPIError [HTTP {self.status_code}] code={self.error_code}: {self.error_msg}"

class NetworkError(Exception):
    def __init__(self, original_message: str):
        self.original_message = original_message
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return f"NetworkError: {self.original_message}"

class BinanceClient:
    BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self):
        """
        Initializes the BinanceClient by loading API credentials from environment variables.
        Raises EnvironmentError if credentials are missing.
        """
        load_dotenv()
        self.api_key = os.environ.get("BINANCE_TESTNET_API_KEY")
        self.api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise EnvironmentError(
                "Missing Binance API credentials. Please set BINANCE_TESTNET_API_KEY "
                "and BINANCE_TESTNET_API_SECRET environment variables."
            )

    def _get_timestamp(self) -> int:
        """
        Returns the current UTC timestamp in milliseconds.
        """
        return int(time.time() * 1000)

    def _sign(self, params: dict) -> str:
        """
        Generates HMAC-SHA256 signature for the given parameters using the API secret.
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _build_headers(self) -> dict:
        """
        Returns the headers required for Binance API requests.
        """
        return {
            "X-MBX-APIKEY": self.api_key
        }

    def new_order(self, **params) -> dict:
        """
        Sends a POST request to create a new order on Binance Futures Testnet.

        Args:
            **params: The order parameters.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            BinanceAPIError: On Binance-side HTTP errors.
            NetworkError: On request failures.
        """
        url = f"{self.BASE_URL}/fapi/v1/order"

        payload = dict(params)
        payload["timestamp"] = self._get_timestamp()
        payload["recvWindow"] = 5000

        payload["signature"] = self._sign(payload)

        headers = self._build_headers()

        safe_payload = dict(payload)
        safe_payload.pop("signature", None)
        logger.debug(f"Sending order request: POST {url} params={safe_payload}")

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()

            resp_json = response.json()
            truncated_resp = str(resp_json)[:200] + "..." if len(str(resp_json)) > 200 else str(resp_json)
            logger.debug(f"Order response: {truncated_resp}")

            return resp_json
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_code = error_data.get("code", -1)
                error_msg = error_data.get("msg", "Unknown error")
            except Exception:
                error_code = -1
                error_msg = e.response.text

            logger.error(f"BinanceAPIError: HTTP {e.response.status_code} code={error_code} msg={error_msg}")
            raise BinanceAPIError(e.response.status_code, error_code, error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"NetworkError: {str(e)}")
            raise NetworkError(str(e))

    def get_exchange_info(self) -> dict:
        """
        Sends a GET request to retrieve exchange information. No auth required.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            NetworkError: On request failures.
            BinanceAPIError: On unexpected API errors.
        """
        url = f"{self.BASE_URL}/fapi/v1/exchangeInfo"
        logger.debug(f"Fetching exchange info: GET {url}")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            resp_json = response.json()
            logger.debug("Exchange info fetched successfully.")
            return resp_json
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_code = error_data.get("code", -1)
                error_msg = error_data.get("msg", "Unknown error")
            except Exception:
                error_code = -1
                error_msg = e.response.text
            logger.error(f"BinanceAPIError: HTTP {e.response.status_code} code={error_code} msg={error_msg}")
            raise BinanceAPIError(e.response.status_code, error_code, error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"NetworkError: {str(e)}")
            raise NetworkError(str(e))

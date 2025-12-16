"""
Base API client with common functionality.
"""

import time
import logging
from typing import Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Base API client with retry logic and error handling."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        retry_attempts: int = 3,
    ):
        """
        Initialize base API client.

        Args:
            base_url: Base URL for the API
            api_key: API authentication key
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.retry_attempts = retry_attempts

        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_headers(self) -> dict[str, str]:
        """
        Get default headers for API requests.

        Returns:
            dict: HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Amazon-Private-Label-Analyzer/1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON payload for POST requests
            headers: Additional headers

        Returns:
            dict: API response data

        Raises:
            requests.exceptions.RequestException: On request failure
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            logger.error(f"Response: {e.response.text if e.response else 'N/A'}")
            raise

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error occurred: {e}")
            raise

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error occurred: {e}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error occurred: {e}")
            raise

    def get(
        self, endpoint: str, params: Optional[dict] = None, **kwargs
    ) -> dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        json_data: Optional[dict] = None,
        params: Optional[dict] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make POST request."""
        return self._make_request(
            "POST", endpoint, params=params, json_data=json_data, **kwargs
        )

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

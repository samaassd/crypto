"""Base connector module for cryptocurrency exchanges.

This module provides the abstract base class for all exchange connectors,
defining the interface that all concrete implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Abstract base class for exchange connectors.

    Defines the interface that all cryptocurrency exchange connectors must
    implement. This class handles common functionality and enforces a
    consistent API across different exchange implementations.

    Attributes:
        exchange_name (str): The name of the exchange this connector connects to.
        api_key (str): The API key for authentication with the exchange.
        api_secret (str): The API secret for authentication with the exchange.
        timeout (int): Request timeout in seconds.
        rate_limit (int): Minimum milliseconds between API requests.
    """

    def __init__(
        self,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        timeout: int = 30,
        rate_limit: int = 100,
    ) -> None:
        """Initialize the base connector.

        Args:
            exchange_name (str): Name of the exchange.
            api_key (str): API key for authentication.
            api_secret (str): API secret for authentication.
            timeout (int, optional): Request timeout in seconds. Defaults to 30.
            rate_limit (int, optional): Minimum milliseconds between requests.
                Defaults to 100.

        Raises:
            ValueError: If exchange_name, api_key, or api_secret are empty.
        """
        if not exchange_name:
            raise ValueError("exchange_name cannot be empty")
        if not api_key:
            raise ValueError("api_key cannot be empty")
        if not api_secret:
            raise ValueError("api_secret cannot be empty")

        self.exchange_name: str = exchange_name
        self.api_key: str = api_key
        self.api_secret: str = api_secret
        self.timeout: int = timeout
        self.rate_limit: int = rate_limit
        self._last_request_time: Optional[datetime] = None

        logger.info(f"Initialized connector for {exchange_name}")

    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch ticker information for a trading pair.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USD').

        Returns:
            Dict[str, Any]: Ticker data including price, volume, and timestamps.
                Expected keys: 'symbol', 'last', 'bid', 'ask', 'volume', 'timestamp'.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
            ConnectionError: If unable to connect to the exchange.
            ValueError: If the symbol is invalid.
        """
        pass

    @abstractmethod
    def get_order_book(
        self, symbol: str, limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Fetch the order book for a trading pair.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USD').
            limit (int, optional): Maximum number of orders to return.
                Defaults to None (no limit).

        Returns:
            Dict[str, Any]: Order book data with 'bids' and 'asks' lists.
                Each entry is a list [price, quantity].

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
            ConnectionError: If unable to connect to the exchange.
            ValueError: If the symbol or limit is invalid.
        """
        pass

    @abstractmethod
    def get_trades(
        self, symbol: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fetch recent trades for a trading pair.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USD').
            limit (int, optional): Maximum number of trades to return.
                Defaults to None (no limit).

        Returns:
            List[Dict[str, Any]]: List of trades with keys: 'id', 'symbol',
                'timestamp', 'datetime', 'price', 'amount', 'side'.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
            ConnectionError: If unable to connect to the exchange.
            ValueError: If the symbol or limit is invalid.
        """
        pass

    @abstractmethod
    def get_balance(self) -> Dict[str, Dict[str, float]]:
        """Fetch account balance and available funds.

        Returns:
            Dict[str, Dict[str, float]]: Balance information with structure:
                {
                    'currency': {
                        'free': float,
                        'used': float,
                        'total': float
                    }
                }

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
            ConnectionError: If unable to connect to the exchange.
            PermissionError: If API key lacks required permissions.
        """
        pass

    @abstractmethod
    def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create an order on the exchange.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USD').
            order_type (str): Order type ('limit', 'market', etc.).
            side (str): Order side ('buy' or 'sell').
            amount (float): Amount of the base asset to trade.
            price (float, optional): Price per unit (required for limit orders).
                Defaults to None.
            **kwargs (Any): Additional exchange-specific parameters.

        Returns:
            Dict[str, Any]: Order confirmation with keys: 'id', 'symbol',
                'type', 'side', 'price', 'amount', 'timestamp', 'status'.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
            ConnectionError: If unable to connect to the exchange.
            ValueError: If parameters are invalid.
            PermissionError: If API key lacks required permissions.
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an existing order.

        Args:
            order_id (str): The unique order identifier.
            symbol (str, optional): Trading pair symbol. Required by some exchanges.
                Defaults to None.

        Returns:
            Dict[str, Any]: Cancelled order details with keys: 'id', 'symbol',
                'status', 'timestamp'.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
            ConnectionError: If unable to connect to the exchange.
            ValueError: If order_id is invalid or not found.
            PermissionError: If API key lacks required permissions.
        """
        pass

    @abstractmethod
    def get_order_status(
        self, order_id: str, symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the status of an order.

        Args:
            order_id (str): The unique order identifier.
            symbol (str, optional): Trading pair symbol. Required by some exchanges.
                Defaults to None.

        Returns:
            Dict[str, Any]: Order status with keys: 'id', 'symbol', 'status',
                'filled', 'amount', 'remaining', 'timestamp'.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
            ConnectionError: If unable to connect to the exchange.
            ValueError: If order_id is invalid or not found.
            PermissionError: If API key lacks required permissions.
        """
        pass

    def validate_symbol(self, symbol: str) -> bool:
        """Validate the format of a trading pair symbol.

        Args:
            symbol (str): Trading pair symbol to validate.

        Returns:
            bool: True if symbol is valid, False otherwise.
        """
        if not isinstance(symbol, str):
            return False
        if len(symbol) < 3:
            return False
        if '/' not in symbol:
            logger.warning(f"Symbol {symbol} does not contain '/' separator")
            return False
        return True

    def validate_amount(self, amount: float) -> bool:
        """Validate that an amount is positive.

        Args:
            amount (float): Amount to validate.

        Returns:
            bool: True if amount is positive, False otherwise.
        """
        if not isinstance(amount, (int, float)):
            return False
        return amount > 0

    def validate_price(self, price: float) -> bool:
        """Validate that a price is positive.

        Args:
            price (float): Price to validate.

        Returns:
            bool: True if price is positive, False otherwise.
        """
        if not isinstance(price, (int, float)):
            return False
        return price > 0

    def validate_side(self, side: str) -> bool:
        """Validate order side.

        Args:
            side (str): Order side to validate ('buy' or 'sell').

        Returns:
            bool: True if side is valid, False otherwise.
        """
        return isinstance(side, str) and side.lower() in ('buy', 'sell')

    def validate_order_type(self, order_type: str) -> bool:
        """Validate order type.

        Args:
            order_type (str): Order type to validate.

        Returns:
            bool: True if order type is valid, False otherwise.
        """
        valid_types = {'limit', 'market', 'stop', 'stop_limit'}
        return isinstance(order_type, str) and order_type.lower() in valid_types

    def __repr__(self) -> str:
        """Return string representation of the connector.

        Returns:
            str: String representation showing exchange name and status.
        """
        return f"{self.__class__.__name__}(exchange='{self.exchange_name}')"

    def __str__(self) -> str:
        """Return user-friendly string representation.

        Returns:
            str: User-friendly string showing exchange name.
        """
        return f"{self.exchange_name} Connector"

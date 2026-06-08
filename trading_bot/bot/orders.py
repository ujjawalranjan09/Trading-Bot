import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

def format_decimal(value: float) -> str:
    """
    Format a decimal value to string for Binance API.
    Prevents scientific notation and removes trailing zeros.
    """
    return f"{value:.8f}".rstrip("0").rstrip(".")

@dataclass
class OrderResult:
    order_id: int
    symbol: str
    side: str
    order_type: str
    status: str
    orig_qty: str
    executed_qty: str
    avg_price: str
    price: str
    raw_response: dict

    def summary(self) -> str:
        return (
            f"Order {self.order_id} ({self.status})\n"
            f"Symbol: {self.symbol} | Side: {self.side} | Type: {self.order_type}\n"
            f"Qty: {self.executed_qty}/{self.orig_qty} | Price: {self.price} | AvgPrice: {self.avg_price}"
        )

def _parse_order_response(response: dict) -> OrderResult:
    return OrderResult(
        order_id=response.get("orderId", 0),
        symbol=response.get("symbol", ""),
        side=response.get("side", ""),
        order_type=response.get("type", ""),
        status=response.get("status", ""),
        orig_qty=response.get("origQty", "0"),
        executed_qty=response.get("executedQty", "0"),
        avg_price=response.get("avgPrice", "0"),
        price=response.get("price", "0"),
        raw_response=response
    )

def place_market_order(client, symbol: str, side: str, quantity: float) -> OrderResult:
    """
    Places a MARKET order.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": format_decimal(quantity)
    }
    logger.info(f"Placing MARKET order: {params}")
    try:
        response = client.new_order(**params)
        result = _parse_order_response(response)
        logger.info(f"MARKET order successful: OrderID {result.order_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to place MARKET order: {str(e)}")
        raise

def place_limit_order(client, symbol: str, side: str, quantity: float, price: float) -> OrderResult:
    """
    Places a LIMIT order.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": format_decimal(quantity),
        "price": format_decimal(price)
    }
    logger.info(f"Placing LIMIT order: {params}")
    try:
        response = client.new_order(**params)
        result = _parse_order_response(response)
        logger.info(f"LIMIT order successful: OrderID {result.order_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to place LIMIT order: {str(e)}")
        raise

def place_stop_market_order(client, symbol: str, side: str, quantity: float, stop_price: float) -> OrderResult:
    """
    Places a STOP_MARKET order.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP_MARKET",
        "quantity": format_decimal(quantity),
        "stopPrice": format_decimal(stop_price)
    }
    logger.info(f"Placing STOP_MARKET order: {params}")
    try:
        response = client.new_order(**params)
        result = _parse_order_response(response)
        logger.info(f"STOP_MARKET order successful: OrderID {result.order_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to place STOP_MARKET order: {str(e)}")
        raise

def place_stop_limit_order(client, symbol: str, side: str, quantity: float, price: float, stop_price: float) -> OrderResult:
    """
    Places a STOP_LIMIT order.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP_LIMIT",
        "timeInForce": "GTC",
        "quantity": format_decimal(quantity),
        "price": format_decimal(price),
        "stopPrice": format_decimal(stop_price)
    }
    logger.info(f"Placing STOP_LIMIT order: {params}")
    try:
        response = client.new_order(**params)
        result = _parse_order_response(response)
        logger.info(f"STOP_LIMIT order successful: OrderID {result.order_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to place STOP_LIMIT order: {str(e)}")
        raise

def place_order(client, order_type: str, symbol: str, side: str, quantity: float, price: float | None = None, stop_price: float | None = None) -> OrderResult:
    """
    Routes the order request to the correct order placement function based on order_type.
    """
    if order_type == "MARKET":
        return place_market_order(client, symbol, side, quantity)
    elif order_type == "LIMIT":
        if price is None:
            raise ValueError("LIMIT order requires 'price'")
        return place_limit_order(client, symbol, side, quantity, price)
    elif order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValueError("STOP_MARKET order requires 'stop_price'")
        return place_stop_market_order(client, symbol, side, quantity, stop_price)
    elif order_type == "STOP_LIMIT":
        if price is None:
            raise ValueError("STOP_LIMIT order requires 'price'")
        if stop_price is None:
            raise ValueError("STOP_LIMIT order requires 'stop_price'")
        return place_stop_limit_order(client, symbol, side, quantity, price, stop_price)
    else:
        raise ValueError(f"Unsupported order type: {order_type}")

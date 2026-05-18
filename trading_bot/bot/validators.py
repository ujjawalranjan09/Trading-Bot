import re

def validate_symbol(symbol: str) -> str:
    """
    Validate that the symbol ends in USDT and matches uppercase format.
    """
    symbol = symbol.upper()
    if not re.match(r"^[A-Z]{2,10}USDT$", symbol):
        raise ValueError(f"Invalid symbol '{symbol}'. Must end with 'USDT' and be 2-10 uppercase letters.")
    return symbol

def validate_side(side: str) -> str:
    """
    Validate that side is BUY or SELL.
    """
    side = side.upper()
    if side not in ["BUY", "SELL"]:
        raise ValueError(f"Invalid side '{side}'. Must be 'BUY' or 'SELL'.")
    return side

def validate_order_type(order_type: str) -> str:
    """
    Validate that order type is MARKET, LIMIT, or STOP_MARKET.
    """
    order_type = order_type.upper()
    if order_type not in ["MARKET", "LIMIT", "STOP_MARKET"]:
        raise ValueError(f"Invalid order type '{order_type}'. Must be 'MARKET', 'LIMIT', or 'STOP_MARKET'.")
    return order_type

def validate_quantity(quantity: str | float, min_qty: float = 0.001) -> float:
    """
    Validate that quantity is a positive number greater than or equal to min_qty.
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a number.")

    if qty < min_qty:
        raise ValueError(f"Quantity {qty} is too low. Minimum allowed is {min_qty}.")
    return qty

def validate_price(price: str | float | None, order_type: str) -> float | None:
    """
    Validate that LIMIT orders have a valid price.
    """
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("LIMIT orders require a price.")
        try:
            p = float(price)
            if p <= 0:
                raise ValueError(f"Price {p} must be greater than 0.")
            return p
        except (ValueError, TypeError):
            raise ValueError(f"Invalid price '{price}'. Must be a number.")
    return None

def validate_stop_price(stop_price: str | float | None, order_type: str) -> float | None:
    """
    Validate that STOP_MARKET orders have a valid stop_price.
    """
    if order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValueError("STOP_MARKET orders require a stop_price.")
        try:
            sp = float(stop_price)
            if sp <= 0:
                raise ValueError(f"Stop price {sp} must be greater than 0.")
            return sp
        except (ValueError, TypeError):
            raise ValueError(f"Invalid stop_price '{stop_price}'. Must be a number.")
    return None

def validate_all(symbol: str, side: str, order_type: str, quantity: str | float, price: str | float | None = None, stop_price: str | float | None = None) -> dict:
    """
    Collect all validation errors and raise them together in one ValueError.
    Returns the fully validated and parsed values.
    """
    errors = []

    validated = {}

    try:
        validated["symbol"] = validate_symbol(symbol)
    except ValueError as e:
        errors.append(str(e))

    try:
        validated["side"] = validate_side(side)
    except ValueError as e:
        errors.append(str(e))

    try:
        validated["order_type"] = validate_order_type(order_type)
    except ValueError as e:
        errors.append(str(e))

    try:
        validated["quantity"] = validate_quantity(quantity)
    except ValueError as e:
        errors.append(str(e))

    try:
        ot = validated.get("order_type", order_type.upper() if isinstance(order_type, str) else order_type)
        validated["price"] = validate_price(price, ot)
    except ValueError as e:
        errors.append(str(e))

    try:
        ot = validated.get("order_type", order_type.upper() if isinstance(order_type, str) else order_type)
        validated["stop_price"] = validate_stop_price(stop_price, ot)
    except ValueError as e:
        errors.append(str(e))

    if errors:
        error_msg = "Validation failed:\n- " + "\n- ".join(errors)
        raise ValueError(error_msg)

    return validated

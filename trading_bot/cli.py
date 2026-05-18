import logging
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bot.client import BinanceAPIError, BinanceClient, NetworkError
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import validate_all

app = typer.Typer(name="trading-bot", help="Binance Futures Testnet Trading Bot")
console = Console()

@app.command()
def place(
    symbol: str = typer.Argument(..., help="Trading pair symbol (e.g., BTCUSDT)"),
    side: str = typer.Argument(..., help="Order side (BUY or SELL)"),
    order_type: str = typer.Argument(..., help="Order type (MARKET, LIMIT, STOP_MARKET)"),
    quantity: float = typer.Option(..., "--qty", "-q", help="Order quantity"),
    price: float = typer.Option(None, "--price", "-p", help="Order price (required for LIMIT)"),
    stop_price: float = typer.Option(None, "--stop-price", "-s", help="Stop price (required for STOP_MARKET)"),
    log_file: str = typer.Option("logs/trading_bot.log", "--log-file", help="Path to log file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose/debug logging"),
):
    """
    Place a new order on Binance Futures Testnet.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(log_file=log_file, log_level=log_level, console_level=log_level)

    request_summary = (
        f"[bold]Symbol:[/bold] {symbol.upper()}\n"
        f"[bold]Side:[/bold] {side.upper()}\n"
        f"[bold]Type:[/bold] {order_type.upper()}\n"
        f"[bold]Quantity:[/bold] {quantity}"
    )
    if price is not None:
        request_summary += f"\n[bold]Price:[/bold] {price}"
    if stop_price is not None:
        request_summary += f"\n[bold]Stop Price:[/bold] {stop_price}"

    console.print(Panel(request_summary, title="Order Request Summary", border_style="blue"))

    try:
        validated = validate_all(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValueError as e:
        console.print(f"[bold red]Validation Error:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    try:
        client = BinanceClient()
    except EnvironmentError as e:
        console.print(f"[bold red]Environment Error:[/bold red] {e}")
        raise typer.Exit(code=4)

    try:
        result = place_order(
            client=client,
            order_type=validated["order_type"],
            symbol=validated["symbol"],
            side=validated["side"],
            quantity=validated["quantity"],
            price=validated["price"],
            stop_price=validated["stop_price"],
        )

        success_msg = f"[bold green]Order Placed Successfully![/bold green]\n\n{result.summary()}"
        console.print(Panel(success_msg, title="Success", border_style="green"))

    except BinanceAPIError as e:
        console.print(f"[bold red]Binance API Error:[/bold red] {e}")
        raise typer.Exit(code=2)
    except NetworkError as e:
        console.print(f"[bold red]Network Error:[/bold red] {e}")
        raise typer.Exit(code=3)
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
        raise typer.Exit(code=5)

@app.command()
def info():
    """
    Get exchange information (shows first 5 symbols).
    """
    setup_logging(console_level=logging.WARNING) # Mute normal logs for purely informational output
    try:
        client = BinanceClient()
        data = client.get_exchange_info()

        symbols = data.get("symbols", [])[:5]

        table = Table(title="Binance Futures Testnet - First 5 Symbols")
        table.add_column("Symbol", justify="left", style="cyan", no_wrap=True)
        table.add_column("Status", justify="left", style="magenta")
        table.add_column("Base Asset", justify="left", style="green")
        table.add_column("Quote Asset", justify="left", style="yellow")

        for sym in symbols:
            table.add_row(
                sym.get("symbol", "N/A"),
                sym.get("status", "N/A"),
                sym.get("baseAsset", "N/A"),
                sym.get("quoteAsset", "N/A")
            )

        console.print(table)

    except EnvironmentError as e:
        console.print(f"[bold red]Environment Error:[/bold red] {e}")
        raise typer.Exit(code=4)
    except BinanceAPIError as e:
        console.print(f"[bold red]Binance API Error:[/bold red] {e}")
        raise typer.Exit(code=2)
    except NetworkError as e:
        console.print(f"[bold red]Network Error:[/bold red] {e}")
        raise typer.Exit(code=3)

if __name__ == "__main__":
    app()

import logging
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text

from bot.client import BinanceAPIError, BinanceClient, NetworkError
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import validate_all

app = typer.Typer(name="trading-bot", help="Binance Futures Testnet Trading Bot")
console = Console()

@app.command()
def place(
    symbol: str = typer.Argument(None, help="Trading pair symbol (e.g., BTCUSDT)"),
    side: str = typer.Argument(None, help="Order side (BUY or SELL)"),
    order_type: str = typer.Argument(None, help="Order type (MARKET, LIMIT, STOP_MARKET, STOP_LIMIT)"),
    quantity: float = typer.Option(None, "--qty", "-q", help="Order quantity"),
    price: float = typer.Option(None, "--price", "-p", help="Order price (required for LIMIT/STOP_LIMIT)"),
    stop_price: float = typer.Option(None, "--stop-price", "-s", help="Stop price (required for STOP_MARKET/STOP_LIMIT)"),
    log_file: str = typer.Option("logs/trading_bot.log", "--log-file", help="Path to log file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose/debug logging"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Run in interactive mode"),
):
    """
    Place a new order on Binance Futures Testnet.
    Use --interactive flag for guided prompts.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(log_file=log_file, log_level=log_level, console_level=log_level)

    if interactive:
        # Interactive mode
        symbol = Prompt.ask("Enter symbol (e.g., BTCUSDT)", default="BTCUSDT").upper()
        side = Prompt.ask("Enter order side", choices=["BUY", "SELL"], default="BUY").upper()
        
        console.print("\nAvailable order types:")
        table = Table(show_lines=False)
        table.add_column("Type", style="cyan")
        table.add_column("Description")
        table.add_row("MARKET", "Immediate execution at best price")
        table.add_row("LIMIT", "Execute at specified price or better")
        table.add_row("STOP_MARKET", "Market order triggered by stop price")
        table.add_row("STOP_LIMIT", "Limit order triggered by stop price")
        console.print(table)
        
        order_type = Prompt.ask("Enter order type", choices=["MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT"], default="MARKET").upper()
        
        quantity = Prompt.ask("Enter quantity", default="0.001", console=console)
        try:
            quantity = float(quantity)
        except ValueError:
            console.print("[bold red]Error: Quantity must be a number[/bold red]")
            raise typer.Exit(code=1)
        
        price = None
        stop_price = None
        
        if order_type in ("LIMIT", "STOP_LIMIT"):
            price = Prompt.ask("Enter price", console=console)
            try:
                price = float(price)
            except ValueError:
                console.print("[bold red]Error: Price must be a number[/bold red]")
                raise typer.Exit(code=1)
        
        if order_type in ("STOP_MARKET", "STOP_LIMIT"):
            stop_price = Prompt.ask("Enter stop price", console=console)
            try:
                stop_price = float(stop_price)
            except ValueError:
                console.print("[bold red]Error: Stop price must be a number[/bold red]")
                raise typer.Exit(code=1)
        
        # Confirm before placing
        console.print("\n[bold]Please confirm your order:[/bold]")
        confirm_text = f"Symbol: [cyan]{symbol}[/cyan] | Side: [magenta]{side}[/magenta]\n"
        confirm_text += f"Type: [green]{order_type}[/green] | Qty: [yellow]{quantity}[/yellow]\n"
        if price:
            confirm_text += f"Price: [yellow]{price}[/yellow]\n"
        if stop_price:
            confirm_text += f"Stop Price: [yellow]{stop_price}[/yellow]\n"
        console.print(confirm_text)
        
        if not Confirm.ask("Do you want to place this order?"):
            console.print("[bold yellow]Order cancelled by user[/bold yellow]")
            raise typer.Exit(code=0)
    
    # Validate inputs
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

    # Build request summary using validated values
    request_summary = (
        f"[bold]Symbol:[/bold] {validated['symbol']}\n"
        f"[bold]Side:[/bold] {validated['side']}\n"
        f"[bold]Type:[/bold] {validated['order_type']}\n"
        f"[bold]Quantity:[/bold] {validated['quantity']}"
    )
    if validated.get("price") is not None:
        request_summary += f"\n[bold]Price:[/bold] {validated['price']}"
    if validated.get("stop_price") is not None:
        request_summary += f"\n[bold]Stop Price:[/bold] {validated['stop_price']}"

    console.print(Panel(request_summary, title="Order Request Summary", border_style="blue"))

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

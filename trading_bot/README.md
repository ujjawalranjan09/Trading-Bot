# Binance Futures Testnet Trading Bot

## Overview
A Python 3.10+ CLI trading bot for placing MARKET, LIMIT, and STOP_MARKET orders on the Binance Futures Testnet. Features clean input validation, robust error handling, and colorful terminal output.

## Prerequisites
- Python 3.10 or higher
- Binance Futures Testnet API Key and Secret

## Setup Steps
1. Clone or download the project folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables:
   Copy `.env.example` to `.env` and insert your Testnet credentials.
   ```bash
   cp .env.example .env
   # Edit .env and add BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET
   ```

## How to Run — Examples

1. **View Exchange Info**
   ```bash
   python cli.py info
   ```

2. **Place a MARKET BUY Order**
   ```bash
   python cli.py place BTCUSDT BUY MARKET --qty 0.001
   ```

3. **Place a LIMIT SELL Order**
   ```bash
   python cli.py place ETHUSDT SELL LIMIT --qty 0.01 --price 3000
   ```

4. **Place a STOP_MARKET BUY Order (Bonus Feature)**
   ```bash
   python cli.py place BNBUSDT BUY STOP_MARKET --qty 0.1 --stop-price 500
   ```

5. **Place an order with Debug logging enabled**
   ```bash
   python cli.py place BTCUSDT BUY MARKET --qty 0.001 -v
   ```

## Output Format
The CLI uses Rich panels to display an **Order Request Summary** followed by either a green **Success** panel containing the executed order's details (Symbol, Side, Type, Qty, Price, etc.), or a red **Error** message in case of failure.

## Log Files
By default, the bot writes rotating logs to `logs/trading_bot.log`. You can specify a different log file with the `--log-file` flag. Logs capture API requests, signing events, HTTP calls, and parsing steps.

## Project Structure
```text
trading_bot/
  bot/
    __init__.py
    client.py
    orders.py
    validators.py
    logging_config.py
  cli.py
  README.md
  requirements.txt
  .env.example
  logs/
```

## Error Handling
The CLI exits with specific status codes depending on the type of error encountered:

| Exit Code | Description | Example Condition |
|-----------|-------------|-------------------|
| 0         | Success     | Order successfully placed. |
| 1         | Validation  | Invalid symbol format, negative quantity, missing price for LIMIT. |
| 2         | Binance API | Binance returns a 400 Bad Request (e.g. invalid signature, insufficient margin). |
| 3         | Network     | Connection timeouts or DNS failures. |
| 4         | Environment | Missing `.env` variables for API Key or Secret. |

## Assumptions & Known Limitations
- The bot exclusively connects to the Testnet (`https://testnet.binancefuture.com`).
- The `timeInForce` parameter for LIMIT orders is hardcoded to `GTC` (Good Till Canceled).
- `recvWindow` is fixed at 5000ms.

## Bonus Feature
The bot includes a fully working `STOP_MARKET` implementation! You can place trailing stops or conditional entries by providing the `--stop-price` (or `-s`) parameter alongside a `STOP_MARKET` type.

# 🚀 Binance Futures Testnet Trading Bot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Typer](https://img.shields.io/badge/CLI-Typer-0A66C2?logo=python)](https://typer.tiangolo.com/)
[![Rich](https://img.shields.io/badge/Terminal-Rich-FF6F00)](https://rich.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A clean, robust, and user-friendly **CLI trading bot** for placing orders on **Binance Futures Testnet**. Built with Python, featuring beautiful terminal output, strong validation, and comprehensive error handling.

> **⚠️ For educational and testing purposes only.** This bot connects exclusively to Binance Futures Testnet.

---

## 🔍 Overview

This project provides a command-line interface to interact with Binance Futures Testnet. It supports:

- **MARKET** orders
- **LIMIT** orders  
- **STOP_MARKET** orders

The bot includes input validation, clear error messages with color-coded output using Rich, structured logging, and a modular codebase.

---

## ✨ Features

- 🚀 Place MARKET, LIMIT, and STOP_MARKET orders via simple CLI commands
- 🎯 Strong input validation with helpful error messages
- 🌀 Beautiful terminal UI with Rich panels and tables
- 📋 Detailed logging with rotating log files
- 🔒 Secure handling of API credentials via environment variables
- 🛡️ Robust error handling for validation, API, and network issues
- 🔄 Modular and extensible code structure

---

## 🛠️ Tech Stack

| Component       | Technology                  |
|-----------------|-----------------------------|
| **Language**    | Python 3.10+                |
| **CLI**         | Typer                       |
| **Terminal UI** | Rich                        |
| **Exchange**    | Binance Futures Testnet API |
| **Logging**     | Python logging + RotatingFileHandler |

---

## 📥 Installation

### 1. Clone the repository

```bash
git clone https://github.com/ujjawalranjan09/Trading-Bot.git
cd Trading-Bot
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Binance Futures **Testnet** API credentials:

```env
BINANCE_TESTNET_API_KEY=your_testnet_api_key
BINANCE_TESTNET_API_SECRET=your_testnet_api_secret
```

> Get Testnet API keys from: https://testnet.binancefuture.com

---

## 🚀 Usage

### View Exchange Information

```bash
python -m trading_bot.cli info
```

### Place Orders

**Market Order (Buy):**
```bash
python -m trading_bot.cli place BTCUSDT BUY MARKET --qty 0.001
```

**Limit Order (Sell):**
```bash
python -m trading_bot.cli place ETHUSDT SELL LIMIT --qty 0.01 --price 3000
```

**Stop Market Order:**
```bash
python -m trading_bot.cli place BNBUSDT BUY STOP_MARKET --qty 0.1 --stop-price 500
```

**Verbose logging:**
```bash
python -m trading_bot.cli place BTCUSDT BUY MARKET --qty 0.001 -v
```

---

## 📁 Project Structure

```text
Trading-Bot/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .gitignore
├── trading_bot/
│   ├── cli.py
│   ├── bot/
│   │   ├── client.py
│   │   ├── orders.py
│   │   ├── validators.py
│   │   └── logging_config.py
│   └── __init__.py
├── logs/
└── venv/ (ignored)
```

---

## ⚠️ Important Disclaimer

**This is a testnet trading bot only.**

- It uses **Binance Futures Testnet** and does **not** place real orders with real money.
- Trading involves substantial risk of loss. Never trade with money you cannot afford to lose.
- This project is intended **for educational and learning purposes**.
- The author is not responsible for any financial losses or damages.
- Always test thoroughly on testnet before considering any live trading strategies.

---

## 🔧 Configuration

All sensitive configuration is handled through environment variables. See `.env.example` for the required variables.

---

## 📋 Logging

Logs are written to `logs/trading_bot.log` by default (with rotation). You can change the log file location using the `--log-file` flag.

---

## 🛠️ Error Handling

The bot uses specific exit codes for different error types:

| Exit Code | Type          | Description                     |
|-----------|---------------|---------------------------------|
| 0         | Success       | Order placed successfully       |
| 1         | Validation    | Invalid input parameters        |
| 2         | Binance API   | API returned an error           |
| 3         | Network       | Connection or timeout issues    |
| 4         | Environment   | Missing API keys in .env        |
| 5         | Unexpected    | Unknown error occurred          |

---

## 🚧 Future Improvements

- Add more order types (TAKE_PROFIT, TRAILING_STOP, etc.)
- Implement strategy modules (e.g., grid, DCA, momentum)
- Add backtesting support
- Web dashboard / Streamlit interface
- Docker support
- Better position and risk management features

---

## 👋 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

> Built with ❤️ by [Ujjawal Ranjan](https://github.com/ujjawalranjan09)

import argparse
import logging
import uvicorn
import asyncio
from currency_service.updater import Updater
from currency_service.config import AppConfig, parse_debug
from currency_service.storage import BalanceStorage
from currency_service.rates.cbr import CBRRateAPI
from currency_service import api

def main():
    run_app()

def parse_args() -> AppConfig:
    parser = argparse.ArgumentParser(description="Currency Service")

    parser.add_argument("--rub", type=float, help="Initial RUB amount")
    parser.add_argument("--usd", type=float, help="Initial USD amount")
    parser.add_argument("--eur", type=float, help="Initial EUR amount")

    parser.add_argument("--period", type=int, required=True, help="Update period in minutes")
    parser.add_argument("--debug", type=str, help="Enable debug output (1, true, yes, etc.)")
    parser.add_argument("--api", action="store_true", help="Run as FastAPI server")

    args = parser.parse_args()

    currencies = {}
    if args.rub is not None:
        currencies["rub"] = args.rub
    if args.usd is not None:
        currencies["usd"] = args.usd
    if args.eur is not None:
        currencies["eur"] = args.eur

    debug = parse_debug(args.debug)

    return AppConfig(
        currencies=currencies,
        period=args.period,
        debug=debug,
        api=args.api
    )

def run_app():
    config = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("🚀 Starting Currency Service")
    logging.debug(f"Parsed config: {config}")

    storage = BalanceStorage(currencies=list(config.currencies.keys()), initial_amounts=config.currencies)
    rate_api = CBRRateAPI()

    api.storage = storage
    api.api = rate_api
    api.debug = config.debug
    api.supported_currencies = list(config.currencies.keys())

    if config.api:
        logging.info("🟢 Запуск FastAPI сервера на http://127.0.0.1:8000")
        uvicorn.run("currency_service.api:app", host="127.0.0.1", port=8000, reload=config.debug)
    else:
        logging.info("⚙️ Запуск CLI режима")
        period_sec = config.period * 60
        updater = Updater(api=rate_api, storage=storage, period_seconds=period_sec)

        try:
            asyncio.run(updater.start())
        except KeyboardInterrupt:
            logging.info("⏹️ Остановка по Ctrl+C")

if __name__ == "__main__":
    run_app()

import httpx
from .base import BaseRateAPI

class CBRRateAPI(BaseRateAPI):
    URL = "https://www.cbr-xml-daily.ru/daily_json.js"

    async def fetch_rates(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.URL)
            response.raise_for_status()
            data = response.json()

        # Извлекаем курсы валют (ЦБ даёт курсы в рублях за 1 единицу валюты)
        rates = data.get("Valute", {})

        usd_rate = rates.get("USD", {}).get("Value")
        eur_rate = rates.get("EUR", {}).get("Value")

        # Рубль базовая валюьа — курс 1
        return {
            "rub": 1.0,
            "usd": usd_rate,
            "eur": eur_rate,
        }

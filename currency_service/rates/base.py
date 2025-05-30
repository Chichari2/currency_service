from abc import ABC, abstractmethod

class BaseRateAPI(ABC):
    @abstractmethod
    async def fetch_rates(self) -> dict:
        """
        Асинхронно получить актуальные курсы валют.
        Возвращает словарь вида:
        {
          "usd": float,
          "eur": float,
          "rub": float
        }
        """
        pass

    def get_currencies(self) -> list:
        """
        Возвращает список валют, которые поддерживает этот API.
        """
        return ["usd", "eur", "rub"]

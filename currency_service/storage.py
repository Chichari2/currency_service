import asyncio
from typing import Dict, List

class BalanceStorage:
    def __init__(self, currencies: List[str], initial_amounts: Dict[str, float]):
        self._balances = {currency.lower(): 0.0 for currency in currencies}
        # Обновим начальными значениями, если есть
        for currency, amount in initial_amounts.items():
            currency = currency.lower()
            if currency in self._balances:
                self._balances[currency] = amount
        self._lock = asyncio.Lock()

    async def get(self, currency: str) -> float:
        currency = currency.lower()
        async with self._lock:
            return self._balances.get(currency, 0.0)

    async def set(self, currency: str, amount: float):
        currency = currency.lower()
        async with self._lock:
            if currency in self._balances:
                self._balances[currency] = amount

    async def modify(self, changes: Dict[str, float]):
        async with self._lock:
            for currency, delta in changes.items():
                c = currency.lower()
                if c in self._balances:
                    self._balances[c] += delta

    async def get_all(self) -> Dict[str, float]:
        async with self._lock:
            return dict(self._balances)  # возвращаем копию

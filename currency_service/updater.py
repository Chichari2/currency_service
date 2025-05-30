import asyncio
import logging

class Updater:
    def __init__(self, api, storage, period_seconds: int, logger=None):
        self.api = api
        self.storage = storage
        self.period = period_seconds
        self.logger = logger or logging.getLogger(__name__)

        self._last_rates = None
        self._last_balances = None

    async def start(self):
        while True:
            try:
                rates = await self.api.fetch_rates()
                balances = await self.storage.get_all()

                changed = False
                if self._last_rates != rates or self._last_balances != balances:
                    changed = True

                if changed:
                    self._last_rates = rates
                    self._last_balances = balances
                    self._print_summary(rates, balances)

            except Exception as e:
                self.logger.error(f"Ошибка при обновлении курсов: {e}")

            await asyncio.sleep(self.period)

    def _print_summary(self, rates, balances):
        rub = balances.get("rub", 0)
        usd = balances.get("usd", 0)
        eur = balances.get("eur", 0)

        rub_usd = rates["usd"] / rates["rub"] if rates["rub"] else 0
        rub_eur = rates["eur"] / rates["rub"] if rates["rub"] else 0
        usd_eur = rates["usd"] / rates["eur"] if rates["eur"] else 0

        total_rub = rub + usd * rub_usd + eur * rub_eur
        total_usd = rub / rub_usd + usd + eur * usd_eur
        total_eur = rub / rub_eur + usd / usd_eur + eur

        lines = [
            f"rub: {rub}",
            f"usd: {usd}",
            f"eur: {eur}",
            f"rub-usd: {rub_usd:.2f}",
            f"rub-eur: {rub_eur:.2f}",
            f"usd-eur: {usd_eur:.2f}",
            f"sum: {total_rub:.2f} rub / {total_usd:.2f} usd / {total_eur:.2f} eur",
        ]

        summary = "\n".join(lines)
        self.logger.info(f"\n{summary}\n")

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Extra
from currency_service.storage import BalanceStorage
from currency_service.rates.cbr import CBRRateAPI
import logging

app = FastAPI()
logger = logging.getLogger("currency_service_api")

storage: BalanceStorage | None = None
api: CBRRateAPI | None = None
debug = False
supported_currencies: list[str] = []

class AmountSet(BaseModel):
    class Config:
        extra = Extra.allow  # принимаем любые поля

class ModifyAmount(BaseModel):
    class Config:
        extra = Extra.allow

@app.middleware("http")
async def log_requests(request: Request, call_next):
    if debug:
        logger.debug(f"Request: {request.method} {request.url}")
        body = await request.body()
        logger.debug(f"Request body: {body.decode() if body else '<empty>'}")

    response = await call_next(request)

    if debug:
        content = b""
        async for chunk in response.body_iterator:
            content += chunk
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {content.decode()}")
        return JSONResponse(content=content.decode(), status_code=response.status_code, headers=dict(response.headers))

    return response

def get_storage():
    if storage is None:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    return storage

def get_api():
    if api is None:
        raise HTTPException(status_code=500, detail="API not initialized")
    return api

def init_app(
    _storage: BalanceStorage,
    _api: CBRRateAPI,
    currencies: list[str],
    enable_debug: bool = False
):
    global storage, api, supported_currencies, debug
    storage = _storage
    api = _api
    supported_currencies = currencies
    debug = enable_debug

#  Общая сума
@app.get("/amount/get")
async def get_amount(
    storage: BalanceStorage = Depends(get_storage),
    api_client: CBRRateAPI = Depends(get_api)
):
    balances = await storage.get_all()
    rates = await api_client.fetch_rates()

    lines = []
    for cur in supported_currencies:
        val = balances.get(cur, 0)
        lines.append(f"{cur}: {val}")

    for i, cur1 in enumerate(supported_currencies):
        for cur2 in supported_currencies[i+1:]:
            r = rates.get(cur1, 0) / rates.get(cur2, 1)
            lines.append(f"{cur1}-{cur2}: {r:.2f}")

    totals = []
    for target in supported_currencies:
        tot = sum(
            balances.get(cur, 0) * (rates.get(cur, 0) / rates.get(target, 1))
            for cur in supported_currencies
        )
        totals.append(f"{tot:.2f} {target}")

    text_response = "\n".join(lines) + "\n\nsum: " + " / ".join(totals)
    return PlainTextResponse(text_response)

#  Отдельная валюта
@app.get("/{currency}/get")
async def get_currency_amount(
    currency: str,
    storage: BalanceStorage = Depends(get_storage)
):
    cur = currency.lower()
    if cur not in supported_currencies:
        raise HTTPException(status_code=404, detail="Currency not supported")
    value = await storage.get(cur)
    return {"name": cur.upper(), "value": value}

# 3) Установка
@app.post("/amount/set")
async def set_amount(data: AmountSet, storage: BalanceStorage = Depends(get_storage)):
    payload = data.model_dump()
    updated = False
    for cur, val in payload.items():
        if cur in supported_currencies:
            await storage.set(cur, val)
            updated = True

    if not updated:
        raise HTTPException(status_code=400, detail="No valid currency values provided")
    return {"status": "success"}

#  Модификация
@app.post("/modify")
async def modify_amount(data: ModifyAmount, storage: BalanceStorage = Depends(get_storage)):
    payload = data.model_dump()
    changes = {cur: payload[cur] for cur in payload if cur in supported_currencies}
    if not changes:
        raise HTTPException(status_code=400, detail="No valid currency modifications provided")

    await storage.modify(changes)
    return {"status": "success"}


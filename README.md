# 📊 Currency Service

Асинхронный Python-сервис для отслеживания валютных курсов и управления балансами. Реализован в виде CLI-программы с возможностью запуска REST API.

## 🛠 Стек

- Python 3.8–3.11  
- FastAPI  
- httpx  
- asyncio  
- argparse  
- pydantic  
- uvicorn  
- pytest  

## 🚀 Возможности

- 🔁 Периодическое получение курсов RUB, USD, EUR с сайта ЦБ РФ
- 🔧 CLI-интерфейс с параметрами:
  - `--rub`, `--usd`, `--eur` — начальные балансы
  - `--period` — интервал обновления курсов в минутах
  - `--debug` — уровень логирования (`1`, `true`, `y`, `yes` и т.д.)
  - `--api` — запуск REST API вместо CLI
- 🌐 REST API:
  - Получение балансов
  - Установка и модификация значений
  - Вывод пересчитанных сумм
- 📦 Чистая архитектура и поддержка расширения источников курсов

## 📦 Установка

```bash
git clone https://github.com/yourname/currency_service.git
cd currency_service
poetry install
```

## 🧪 Пример CLI-запуска

```bash
poetry run currency_service --rub 1000 --usd 200 --eur 50 --period 1
```

Сервис будет обновлять курсы каждую минуту и выводить состояние, если курс или балансы изменились.

## 🌐 Запуск API-сервера

```bash
poetry run currency_service --rub 1000 --usd 200 --eur 50 --period 1 --api
```

Сервер будет доступен по адресу: `http://127.0.0.1:8000`

## 📚 Примеры запросов

### Получить баланс по валюте

```bash
curl http://127.0.0.1:8000/usd/get
```

### Общий отчёт

```bash
curl http://127.0.0.1:8000/amount/get
```

### Установить новые балансы

```bash
curl -X POST http://127.0.0.1:8000/amount/set \
     -H "Content-Type: application/json" \
     -d '{"usd": 500, "eur": 100}'
```

### Изменить текущие значения

```bash
curl -X POST http://127.0.0.1:8000/modify \
     -H "Content-Type: application/json" \
     -d '{"usd": 25, "rub": -300}'
```

## ✅ Тестирование

```bash
poetry run pytest --cov=currency_service --cov-report=term-missing
```

Покрытие охватывает:
- Все REST-маршруты
- CLI запуск и аргументы
- Изменение и получение балансов

## 📂 Структура проекта

```
currency_service/
├── __main__.py              # Запуск через `python -m currency_service`
├── main.py                  # CLI и точка входа
├── api.py                   # FastAPI маршруты
├── config.py                # Аргументы и настройки
├── storage.py               # Асинхронное хранилище валют
├── updater.py               # Обновление курсов и вывод состояния
└── rates/
    ├── base.py              # Абстрактный API курсов
    └── cbr.py               # Реализация для ЦБ РФ

tests/
├── test_api.py              # FastAPI тесты с заглушками
└── test_cli.py              # Проверка CLI и `--help`

pyproject.toml               # Poetry + зависимости
README.md                    # Документация
poetry.lock                  # Lock-файл Poetry
```

## 🧠 Автор

Artem Vologdin  
Python Backend Developer

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union, cast

import requests
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.apilayer.com/exchangerates_data/latest"


def load_transactions(file_path: Union[str, Path]) -> List[Dict]:
    """Загружает транзакции из JSON-файла. Если файл не найден или некорректен, возвращает []."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def convert_to_rub(transaction: Dict[str, Any]) -> float:
    """Конвертирует сумму транзакции в рубли по текущему курсу."""
    amount = float(cast(float, transaction.get("amount", 0)))
    currency = transaction.get("currency", "RUB").upper()

    if currency == "RUB":
        return float(amount)

    # Запрос к API для получения курса
    response = requests.get(
        BASE_URL,
        params={"base": currency, "symbols": "RUB"},
        headers={"apikey": API_KEY}
    )
    response.raise_for_status()
    rate = cast(float, response.json()["rates"]["RUB"])
    return amount * rate

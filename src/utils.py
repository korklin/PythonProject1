import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union, cast

import requests
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.apilayer.com/exchangerates_data/convert"


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
    """Конвертирует сумму транзакции в рубли через API."""
    amount = transaction.get("amount", 0)
    currency = transaction.get("currency", "RUB").upper()

    if currency == "RUB":
        return float(amount)

    try:
        response = requests.get(
            BASE_URL,
            params={
                "to": "RUB",
                "from": currency,
                "amount": amount
            },
            headers={"apikey": API_KEY},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        return float(result["result"])  # Ключ "result" содержит итоговую сумму
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Ошибка конвертации: {e}")
        return 0.0

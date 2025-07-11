import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

import requests
from dotenv import load_dotenv


# Настройка логирования
def setup_logging() -> None:
    """Настройка конфигурации логирования"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)  # Создаем папку logs, если её нет

    log_file = logs_dir / f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w"),  # 'w' для перезаписи при каждом запуске
            logging.StreamHandler(),
        ],
    )


setup_logging()
logger = logging.getLogger(__name__)


load_dotenv()  # Загружаем переменные из .env

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.apilayer.com/exchangerates_data/convert"


def load_transactions(file_path: Union[str, Path]) -> List[Dict]:
    """Загружает транзакции из JSON-файла с логированием. Если файл не найден или некорректен, возвращает []."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                logger.info(f"Успешно загружено {len(data)} транзакций из {file_path}")
                return data
            logger.warning(f"Файл {file_path} не содержит список транзакций")
            return []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Ошибка загрузки транзакций: {e}")
        return []


def convert_to_rub(transaction: Dict[str, Any]) -> float:
    """Конвертирует сумму транзакции в рубли через API с логированием."""
    try:
        amount = transaction.get("amount", 0)
        currency = transaction.get("currency", "RUB").upper()

        if currency == "RUB":
            logger.debug(f"Конвертация не требуется (RUB): {amount}")
            return float(amount)

        logger.info(f"Запрос конвертации: {amount} {currency} -> RUB")

        response = requests.get(
            BASE_URL, params={"to": "RUB", "from": currency, "amount": amount}, headers={"apikey": API_KEY}, timeout=10
        )
        response.raise_for_status()
        result = response.json()
        converted = float(result["result"])
        logger.info(f"Успешная конвертация:{amount} {currency} = {converted} RUB")
        return converted
    except requests.RequestException as e:
        logger.error(f"Ошибка API при конвертации: {e}")
    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка обработки данных конвертации: {e}")
    except Exception as e:
        logger.critical(f"Неожиданная ошибка при конвертации: {e}")
    return 0.0

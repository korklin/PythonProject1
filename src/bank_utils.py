import re
from collections import Counter
from typing import Dict, List


def process_bank_search(transactions: List[Dict], search: str) -> List[Dict]:
    """
    Поиск транзакций по заданной строке в описании.

    Аргументы:
    - transactions: список транзакций (словарей)
    - search: строка для поиска

    Возвращает:
    - Список транзакций, в которых поле description содержит строку поиска (без учета регистра)
    """
    if not search:
        return transactions

    pattern = re.compile(re.escape(search), re.IGNORECASE)
    return [t for t in transactions if isinstance(t.get("description"), str) and pattern.search(t["description"])]


def process_bank_operations(transactions: List[Dict], categories: List[str]) -> Dict[str, int]:
    """
    Подсчет количества транзакций, относящихся к указанным категориям,
    с использованием Counter.

    Аргументы:
    - transactions: список транзакций (словарей)
    - categories: список категорий (ключевых слов для поиска в description)

    Возвращает:
    - Словарь {категория: количество}
    """
    counter: Counter[str] = Counter()

    for transaction in transactions:
        description = transaction.get("description", "")
        if not isinstance(description, str):
            continue
        description = description.lower()
        for category in categories:
            if category.lower() in description:
                counter[category.lower()] += 1

    return {category: counter.get(category.lower(), 0) for category in categories}

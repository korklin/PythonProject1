from src.processing import sort_by_date
from tests.conftest import transactions


def filter_by_currency(transactions: list, currency: str) -> iter:
    """Фильтрует транзакции по валюте и возвращает итератор."""
    for transaction in transactions:
        if transaction["operationAmount"]["currency"]["code"] == currency:
            yield transaction


# sorted_result = sorted(filter_by_currency(transactions, 'UDS'), key=lambda x: x['date'], revers=True)


def transaction_descriptions(transactions: list) -> iter:
    """Принимает список словарей с транзакциями и возвращает описание каждой операции по очереди."""
    for transaction in transactions:
        description = transaction["description"]
        yield description

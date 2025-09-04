from typing import Iterator, List, Dict, Any, Generator, Iterable


def filter_by_currency(transactions: Iterable[Dict[str, Any]], currency: str) -> Iterator[Dict[str, Any]]:
    """Фильтрует транзакции по валюте и возвращает итератор."""
    for transaction in transactions:
        if transaction["operationAmount"]["currency"]["code"] == currency:
            yield transaction


def transaction_descriptions(transactions: list) -> Generator[str, None, None]:
    """Принимает список словарей с транзакциями и возвращает описание каждой операции по очереди."""
    for transaction in transactions:
        description = transaction["description"]
        yield description


def card_number_generator(start: int = 1, end: int = 9999_9999_9999_9999) -> Generator[str, None, None]:
    """
    Генератор номеров банковских карт в формате XXXX XXXX XXXX XXXX.

    Args:
        start: начальный номер (от 1 до 9999999999999999)
        end: конечный номер (от start до 9999999999999999)

    Yields:
        Строки с номерами карт в заданном диапазоне

    Raises:
        ValueError: если параметры вне допустимого диапазона
    """
    # Проверка корректности входных параметров
    if not isinstance(start, int) or not isinstance(end, int):
        raise TypeError("Параметры должны быть целыми числами")

    if start < 1 or end > 9999_9999_9999_9999:
        raise ValueError(
            f"Диапазон должен быть: 1 ≤ start ≤ end ≤ 9999999999999999. " f"Получено: start={start}, end={end}"
        )

    if start > end:
        raise ValueError(f"Начальное значение ({start}) больше конечного ({end})")

    # Генерация номеров
    current = start
    while current <= end:
        yield f"{current:016d}"[:4] + " " + f"{current:016d}"[4:8] + " " + f"{current:016d}"[
            8:12
        ] + " " + f"{current:016d}"[12:16]
        current += 1

import pytest

from typing import Iterator, List, Dict, Any, Generator, Iterable
from src.generators import filter_by_currency
from src.generators import transaction_descriptions
from src.generators import card_number_generator
from tests.conftest import transactions
from collections.abc import Iterator

# Блок проверок функции filter_by_currency()

def test_correct_structure(transactions: Iterable[Dict[str, Any]] ) -> None:
    """Проверка работы с реальной структурой транзакций."""
    filtered = filter_by_currency(transactions, "USD")
    result: List[Dict[str, Any]] = list(filtered)
    assert len(result) == 3
    assert all(t["operationAmount"]["currency"]["code"] == "USD" for t in result)


def test_next_usage(transactions: Iterable[Dict[str, Any]]) -> None:
    """Тест пошагового получения транзакций через next()."""
    filtered = filter_by_currency(transactions, "USD")
    assert next(filtered)["id"] == 939719570
    assert next(filtered)["id"] == 142264268
    assert next(filtered)["id"] == 895315941
    with pytest.raises(StopIteration):
        next(filtered)  # Итератор завершен


def test_filters_usd_transactions(transactions: Iterable[Dict[str, Any]]) -> None:
    """Тест фильтрации USD транзакций"""
    filtered = filter_by_currency(transactions, "USD")
    result = list(filtered)
    assert len(result) == 3
    assert all(t["operationAmount"]["currency"]["code"] == "USD" for t in result)
    assert result[0]["id"] == 939719570
    assert result[1]["id"] == 142264268
    assert result[2]["id"] == 895315941


def test_filters_eur_transactions(transactions: Iterable[Dict[str, Any]]) -> None:
    """Тест фильтрации RUB транзакций"""
    filtered = filter_by_currency(transactions, "RUB")
    result = list(filtered)
    assert len(result) == 2
    assert result[0]["id"] == 873106923
    assert result[1]["id"] == 594226727


def test_empty_result_for_nonexistent_currency(transactions: Iterable[Dict[str, Any]]) -> None:
    """Тест пустого результата для несуществующей валюты"""
    filtered = filter_by_currency(transactions, "GBP")
    assert next(filtered, None) is None


def test_empty_input() -> None:
    """Тест обработки пустого списка транзакций"""
    data: list[dict[str, Any]] = []
    filtered = filter_by_currency(data, "USD")
    assert next(filtered, None) is None


def test_returns_iterator_1(transactions: Iterable[Dict[str, Any]]) -> None:
    """Тест, что функция возвращает итератор"""
    filtered = filter_by_currency(transactions, "USD")
    assert isinstance(filtered, Iterator)
    assert not isinstance(filtered, list)


def test_lazy_iteration_1(transactions: Iterable[Dict[str, Any]]) -> None:
    """Тест ленивой обработки (генератор не должен обрабатывать весь список сразу)"""
    filtered = filter_by_currency(transactions, "USD")
    first = next(filtered)
    assert first["id"] == 939719570
    second = next(filtered)
    assert second["id"] == 142264268
    third = next(filtered)
    assert third["id"] == 895315941
    with pytest.raises(StopIteration):
        next(filtered)


@pytest.mark.parametrize(
    "currency,expected_ids",
    [
        ("USD", [939719570, 142264268, 895315941]),
        ("RUB", [873106923, 594226727]),
        ("GBP", []),
    ],
)
def test_parametrized_currency(currency: str, expected_ids: List[int], transactions: Iterable[Dict[str, Any]]) -> None:
    """Параметризованный тест для разных валют"""
    filtered = filter_by_currency(transactions, currency)
    result_ids = [t["id"] for t in filtered]
    assert result_ids == expected_ids


# Блок проверок функции transaction_descriptions()


def test_returns_correct_descriptions_in_order(transactions: List[Dict[str, Any]]) -> None:
    """Проверяет корректность и порядок возвращаемых описаний"""
    gen = transaction_descriptions(transactions)
    assert next(gen) == "Перевод организации"
    assert next(gen) == "Перевод со счета на счет"
    assert next(gen) == "Перевод со счета на счет"
    assert next(gen) == "Перевод с карты на карту"
    assert next(gen) == "Перевод организации"


def test_returns_iterator_2(transactions: List[Dict[str, Any]]) -> None:
    """Проверяет, что возвращается именно генератор"""
    gen = transaction_descriptions(transactions)
    assert isinstance(gen, Iterator)
    assert not isinstance(gen, list)


def test_handles_empty_list() -> None:
    """Проверяет работу с пустым списком транзакций"""
    gen = transaction_descriptions([])
    with pytest.raises(StopIteration):
        next(gen)


def test_handles_single_transaction(transactions: List[Dict[str, Any]]) -> None:
    """Проверяет работу с одной транзакцией"""
    single_transaction = [transactions[0]]
    gen = transaction_descriptions(single_transaction)
    assert next(gen) == "Перевод организации"
    with pytest.raises(StopIteration):
        next(gen)


@pytest.mark.parametrize(
    "indices,expected",
    [
        ([0], ["Перевод организации"]),
        ([1, 3], ["Перевод со счета на счет", "Перевод с карты на карту"]),
        ([0, 1, 4], ["Перевод организации", "Перевод со счета на счет", "Перевод организации"]),
    ],
)
def test_parametrized(indices: List[int], expected: List[str], transactions: List[Dict[str, Any]]) -> None:
    """Параметризованный тест разных комбинаций транзакций"""
    test_data = [transactions[i] for i in indices]
    gen = transaction_descriptions(test_data)
    for expect in expected:
        assert next(gen) == expect
    with pytest.raises(StopIteration):
        next(gen)


def test_lazy_iteration_2(transactions: List[Dict[str, Any]]) -> None:
    """Проверяет ленивую обработку (по одному элементу)"""
    gen = transaction_descriptions(transactions)
    first = next(gen)
    assert first == "Перевод организации"
    # Генератор должен сохранять состояние
    second = next(gen)
    assert second == "Перевод со счета на счет"


# Блок проверок функции card_number_generator()


def test_generator_basic() -> None:
    """Проверка базовой работы генератора"""
    gen = card_number_generator(1, 3)
    assert next(gen) == "0000 0000 0000 0001"
    assert next(gen) == "0000 0000 0000 0002"
    assert next(gen) == "0000 0000 0000 0003"
    with pytest.raises(StopIteration):
        next(gen)


def test_invalid_ranges() -> None:
    """Проверка обработки некорректных диапазонов"""
    # start < 1
    with pytest.raises(ValueError):
        list(card_number_generator(0, 5))

    # end > максимума
    with pytest.raises(ValueError):
        list(card_number_generator(1, 10000_0000_0000_0000))

    # start > end
    with pytest.raises(ValueError):
        list(card_number_generator(10, 5))

    # Не числа
    with pytest.raises(TypeError):
        list(card_number_generator("1", "5")) # type: ignore[arg-type]


def test_edge_cases() -> None:
    """Проверка граничных значений"""
    # Первый номер
    gen = card_number_generator(1, 1)
    assert next(gen) == "0000 0000 0000 0001"

    # Последний номер
    gen = card_number_generator(9999_9999_9999_9999, 9999_9999_9999_9999)
    assert next(gen) == "9999 9999 9999 9999"


def test_format() -> None:
    """Проверка формата вывода"""
    gen = card_number_generator(1234_5678_9012_3456, 1234_5678_9012_3456)
    num = next(gen)
    assert len(num) == 19  # 16 цифр + 3 пробела
    assert num.count(" ") == 3
    assert num == "1234 5678 9012 3456"


def test_is_iterator() -> None:
    """Проверка типа возвращаемого значения"""
    gen = card_number_generator(1, 5)
    assert isinstance(gen, Iterator)
    assert not isinstance(gen, list)

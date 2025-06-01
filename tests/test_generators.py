import pytest

from src.generators import filter_by_currency
from tests.conftest import transactions
from collections.abc import Iterator


def test_correct_structure(transactions):
    """Проверка работы с реальной структурой транзакций."""
    filtered = filter_by_currency(transactions, "USD")
    result = list(filtered)
    assert len(result) == 3
    assert all(t["operationAmount"]["currency"]["name"] == "USD" for t in result)


def test_next_usage(transactions):
    """Тест пошагового получения транзакций через next()."""
    filtered = filter_by_currency(transactions, "USD")
    assert next(filtered)["id"] == 939719570
    assert next(filtered)["id"] == 142264268
    assert next(filtered)["id"] == 895315941
    with pytest.raises(StopIteration):
        next(filtered)  # Итератор завершен


def test_filters_usd_transactions(transactions):
    """Тест фильтрации USD транзакций"""
    filtered = filter_by_currency(transactions, "USD")
    result = list(filtered)
    assert len(result) == 3
    assert all(t["operationAmount"]["currency"]["code"] == "USD" for t in result)
    assert result[0]["id"] == 939719570
    assert result[1]["id"] == 142264268
    assert result[2]["id"] == 895315941


def test_filters_eur_transactions(transactions):
    """Тест фильтрации RUB транзакций"""
    filtered = filter_by_currency(transactions, "RUB")
    result = list(filtered)
    assert len(result) == 2
    assert result[0]["id"] == 873106923
    assert result[1]["id"] == 594226727


def test_empty_result_for_nonexistent_currency(transactions):
    """Тест пустого результата для несуществующей валюты"""
    filtered = filter_by_currency(transactions, "GBP")
    assert next(filtered, None) is None


def test_empty_input():
    """Тест обработки пустого списка транзакций"""
    filtered = filter_by_currency([], "USD")
    assert next(filtered, None) is None


def test_returns_iterator(transactions):
    """Тест, что функция возвращает итератор"""
    filtered = filter_by_currency(transactions, "USD")
    assert isinstance(filtered, Iterator)
    assert not isinstance(filtered, list)


def test_lazy_iteration(transactions):
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
def test_parametrized(currency, expected_ids, transactions):
    """Параметризованный тест для разных валют"""
    filtered = filter_by_currency(transactions, currency)
    result_ids = [t["id"] for t in filtered]
    assert result_ids == expected_ids

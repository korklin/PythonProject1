from typing import Dict, List, Any

import pytest

from src.bank_utils import process_bank_operations, process_bank_search


@pytest.fixture
def sample_transactions() -> List[Dict]:
    return [
        {"id": 1, "description": "Перевод с карты на карту"},
        {"id": 2, "description": "Перевод организации"},
        {"id": 3, "description": "Открытие вклада"},
        {"id": 4, "description": "Перевод со счета на счет"},
        {"id": 5, "description": None},  # Для теста на None
        {"id": 6, "description": 12345},  # Для теста на нестроковое значение
        {"id": 7, "description": "Перевод с карты на счет"},
    ]


# Тесты для process_bank_search
def test_process_bank_search_basic(sample_transactions: list[dict]) -> None:
    result = process_bank_search(sample_transactions, "перевод")
    assert len(result) == 4
    assert all("Перевод" in t["description"] for t in result)


def test_process_bank_search_case_insensitive(sample_transactions: list[dict]) -> None:
    result = process_bank_search(sample_transactions, "ПЕРЕВОД")
    assert len(result) == 4


def test_process_bank_search_exact_phrase(sample_transactions: list[dict]) -> None:
    result = process_bank_search(sample_transactions, "карты на карту")
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_process_bank_search_no_matches(sample_transactions: list[dict]) -> None:
    result = process_bank_search(sample_transactions, "кредит")
    assert len(result) == 0
    assert result == []


def test_process_bank_search_empty_search(sample_transactions: list[dict]) -> None:
    result = process_bank_search(sample_transactions, "")
    assert len(result) == len(sample_transactions)
    assert result == sample_transactions


def test_process_bank_search_non_string_descriptions(sample_transactions: list[dict]) -> None:
    result = process_bank_search(sample_transactions, "12345")
    assert len(result) == 0


# Тесты для process_bank_operations
def test_process_bank_operations_basic(sample_transactions: list[dict]) -> None:
    categories = ["перевод", "вклад"]
    result = process_bank_operations(sample_transactions, categories)
    assert result == {"перевод": 4, "вклад": 1}


def test_process_bank_operations_case_insensitive(sample_transactions: list[dict]) -> None:
    categories = ["ПЕРЕВОД", "ВКЛАД"]
    result = process_bank_operations(sample_transactions, categories)
    assert result == {"ПЕРЕВОД": 4, "ВКЛАД": 1}


def test_process_bank_operations_multiple_matches(sample_transactions: list[dict]) -> None:
    # Одна транзакция может попадать в несколько категорий
    categories = ["карты", "счет"]
    result = process_bank_operations(sample_transactions, categories)
    assert result == {"карты": 2, "счет": 2}


def test_process_bank_operations_empty_categories(sample_transactions: list[dict]) -> None:
    result = process_bank_operations(sample_transactions, [])
    assert result == {}


def test_process_bank_operations_no_matches(sample_transactions: list[dict]) -> None:
    result = process_bank_operations(sample_transactions, ["кредит"])
    assert result == {"кредит": 0}


def test_process_bank_operations_non_string_descriptions(sample_transactions: list[dict]) -> None:
    result = process_bank_operations(sample_transactions, ["12345"])
    assert result == {"12345": 0}


def test_process_bank_search_missing_description_key() -> None:
    transactions:list[dict[Any, Any]] = [{"id": 1}, {"id": 2, "description": "Перевод"}]
    result = process_bank_search(transactions, "перевод")
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_process_bank_search_numeric_description() -> None:
    transactions = [{"id": 1, "description": 123}]
    result = process_bank_search(transactions, "123")
    assert result == []  # нестроковые игнорируются


@pytest.mark.parametrize(
    "transactions, search, expected_ids",
    [
        (
            [
                {"id": 1, "description": "Оплата услуг связи"},
                {"id": 2, "description": "Перевод на карту"},
                {"id": 3, "description": "оплата Интернета"},
            ],
            "оплата",
            [1, 3]
        ),
        (
            [
                {"id": 4, "description": "Пополнение счета"},
                {"id": 5, "description": "Снятие наличных"},
            ],
            "перевод",
            []
        ),
        (
            [
                {"id": 6, "description": None},
                {"id": 7},  # нет description
                {"id": 8, "description": "Перевод с карты"},
            ],
            "перевод",
            [8]
        )
    ]
)
def test_process_bank_search_parametrized(transactions: List[Dict[str, str]], search: str, expected_ids: List[int]) -> None:
    result = process_bank_search(transactions, search)
    result_ids = [t["id"] for t in result]
    assert result_ids == expected_ids


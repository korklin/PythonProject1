import pytest
from bank_utils import process_bank_search, process_bank_operations

# Фикстура с операциями

@pytest.fixture
def real_transactions():
    return [
        {"description": "Перевод с карты на карту"},
        {"description": "Перевод со счета на счет"},
        {"description": "Перевод организации"},
        {"description": "Открытие вклада"},
    ]


# Тесты для process_bank_search

def test_search_translation_card_to_card(real_transactions):
    result = process_bank_search(real_transactions, "карты на карту")
    assert len(result) == 4
    for tx in result:
        assert "карты на карту" in tx["description"].lower()

def test_search_account_to_account(real_transactions):
    result = process_bank_search(real_transactions, "счета на счет")
    assert len(result) == 3

def test_search_by_keyword_organization(real_transactions):
    result = process_bank_search(real_transactions, "организации")
    assert len(result) == 1
    assert result[0]["description"] == "Перевод организации"

def test_search_open_deposit(real_transactions):
    result = process_bank_search(real_transactions, "вклада")
    assert len(result) == 1
    assert result[0]["description"] == "Открытие вклада"

def test_search_no_matches(real_transactions):
    result = process_bank_search(real_transactions, "ипотека")
    assert result == []


# Тесты для process_bank_operations

def test_operations_count_by_keywords(real_transactions):
    categories = ["карты", "счета", "организации", "вклада"]
    result = process_bank_operations(real_transactions, categories)

    assert result == {
        "карты": 4,
        "счета": 3,
        "организации": 1,
        "вклада": 1
    }

def test_operations_case_insensitive(real_transactions):
    result = process_bank_operations(real_transactions, ["ОрГаНиЗаЦии"])
    assert result == {"ОрГаНиЗаЦии": 1}

def test_operations_no_match(real_transactions):
    result = process_bank_operations(real_transactions, ["ипотека"])
    assert result == {}

def test_operations_partial_word_match(real_transactions):
    result = process_bank_operations(real_transactions, ["перевод"])
    assert result == {"перевод": 7}  # 7 из 9 описаний содержат "Перевод"

def test_operations_empty_categories(real_transactions):
    result = process_bank_operations(real_transactions, [])
    assert result == {}

def test_operations_empty_transactions():
    result = process_bank_operations([], ["вклада"])
    assert result == {}
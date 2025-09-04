import pytest

from src.masks import get_mask_account, get_mask_card_number
from src.widget import get_date, mask_account_card


# ----- Корректные данные -----
@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        # Тесты для карт
        ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
        ("Visa Classic 6831982476737658", "Visa Classic 6831 98** **** 7658"),
        ("MasterCard 7158300734726758", "MasterCard 7158 30** **** 6758"),
        ("Visa Platinum 8990922113665229", "Visa Platinum 8990 92** **** 5229"),
        ("Visa Gold 5999414228426353", "Visa Gold 5999 41** **** 6353"),
        # Тесты для счетов
        ("Счет 64686473678894779589", "Счет **9589"),
        ("Счет 35383033474447895560", "Счет **5560"),
        ("счет 73654108430135874305", "Счет **4305"),  # Проверка регистра
    ],
)
def test_valid_masking(input_data: str, expected_output: str) -> None:
    """Проверка корректного маскирования для разных типов платежей"""
    assert mask_account_card(input_data) == expected_output


# ----- Некорректные данные -----
@pytest.mark.parametrize(
    "invalid_input, error_message",
    [
        # Ошибки для карт
        ("Visa 123456789012345", "Номер карты должен содержать 16 цифр"),  # 15 цифр
        ("Mastercard abcdefghijklmnop", "Номер карты должен содержать 16 цифр"),  # буквы
        # Ошибки для счетов
        ("Счет 123", "Номер счета слишком короткий"),  # <20 цифр
        ("Счет abcdefghij", "Номер счета слишком короткий"),  # нет цифр
        # Общие ошибки
        ("", "Номер карты должен содержать 16 цифр"),  # пустая строка
        ("Just Text", "Номер карты должен содержать 16 цифр"),  # нет цифр вообще
        ],
)
def test_invalid_input_number(invalid_input: str, error_message: str) -> None:
    """Проверка обработки некорректных данных"""
    with pytest.raises((ValueError, AttributeError)) as exc_info:
        mask_account_card(invalid_input)
    assert error_message in str(exc_info.value)


# ----- Граничные случаи -----
def test_exact_length() -> None:
    """Проверка граничных значений длины"""
    # Для карты (ровно 16 цифр)
    assert mask_account_card("Card 1234567890123456") == "Card 1234 56** **** 3456"

    # Для счёта (ровно 20 цифр)
    assert mask_account_card("Счет 12345678901234567890") == "Счет **7890"


# Корректные данные
@pytest.mark.parametrize(
    "input_date, expected_output",
    [
        ("2024-03-11T02:26:18.671407", "11.03.2024"),  # Обычная дата
        ("1999-12-31T23:59:59.999999", "31.12.1999"),  # Граничный случай (последний день года)
        ("0001-01-01T00:00:00.000000", "01.01.0001"),  # Минимальная дата
    ],
)
def test_correct_date_conversion(input_date: str, expected_output: str) -> None:
    """Проверка корректного преобразования даты."""
    assert get_date(input_date) == expected_output


# Некорректные данные (должны вызывать ошибки)
@pytest.mark.parametrize(
    "invalid_input",
    [
        "2024-03-11",  # Нет 'T' и времени
        "2024/03/11T02:26:18",  # Неправильный разделитель даты
        "not-a-date",  # Нечисловая строка
        "",  # Пустая строка
    ],
)
def test_invalid_input_date(invalid_input: str) -> None:
    """Проверка, что функция падает с ошибкой на некорректных данных."""
    with pytest.raises((IndexError, ValueError)):
        get_date(invalid_input)
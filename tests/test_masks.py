import pytest

from src.masks import get_mask_account, get_mask_card_number


# Корректные данные (разные форматы номера карты)
@pytest.mark.parametrize(
    "input_card, expected_output",
    [
        ("1234567890123456", "1234 56** **** 3456"),  # Стандартный ввод
        ("1234-5678-9012-3456", "1234 56** **** 3456"),  # С разделителями
        (" 1234 5678 9012 3456 ", "1234 56** **** 3456"),  # С пробелами
        ("1234💀5678🐉9012_3456", "1234 56** **** 3456"),  # С нестандартными символами
    ],
)
def test_valid_card_masking(input_card, expected_output):
    """Проверка маскирования для валидных номеров карт."""
    assert get_mask_card_number(input_card) == expected_output


# Некорректные данные (должны вызывать ValueError)
@pytest.mark.parametrize(
    "invalid_input, error_message",
    [
        ("123456789012345", "Номер карты должен содержать 16 цифр"),  # 15 цифр
        ("12345678901234567", "Номер карты должен содержать 16 цифр"),  # 17 цифр
        ("", "Номер карты должен содержать 16 цифр"),  # Пустая строка
        ("abcd567890123456", "Номер карты должен содержать 16 цифр"),  # Буквы вместо цифр
    ],
)
def test_invalid_card_input(invalid_input, error_message):
    """Проверка, что функция вызывает ValueError при неверных данных."""
    with pytest.raises(ValueError) as exc_info:
        get_mask_card_number(invalid_input)
    assert error_message in str(exc_info.value)


# Проверка, что функция не падает на None (опционально)
def test_none_input():
    """Проверка реакции на None (ожидаем ValueError)."""
    with pytest.raises(ValueError):
        get_mask_card_number(None)


# Корректные данные (разные форматы номера счёта)
@pytest.mark.parametrize(
    "input_account, expected_output",
    [
        ("12340000005600007890", "**7890"),  # Стандартный ввод (20 цифр)
        ("1234 0000 0056 0000 7890", "**7890"),  # С пробелами
        ("1234-0000-0056-0000-7890", "**7890"),  # С разделителями
        ("💳1234🐉00000056000078_90", "**7890"),  # С нестандартными символами
    ],
)
def test_valid_account_masking(input_account, expected_output):
    """Проверка маскирования для валидных номеров счёта."""
    assert get_mask_account(input_account) == expected_output


# Некорректные данные (должны вызывать ValueError)
@pytest.mark.parametrize(
    "invalid_input, error_message",
    [
        ("123", "Номер счёта должен содержать минимум 20 цифр"),  # 3 цифры
        ("", "Номер счёта должен содержать минимум 20 цифр"),  # Пустая строка
        ("abc567890", "Номер счёта должен содержать минимум 20 цифр"),  # Буквы вместо цифр
    ],
)
def test_invalid_account_input(invalid_input, error_message):
    """Проверка, что функция вызывает ValueError при неверных данных."""
    with pytest.raises(ValueError) as exc_info:
        get_mask_account(invalid_input)
    assert error_message in str(exc_info.value)


# Проверка на None (опционально)
def test_none_input():
    """Проверка реакции на None (ожидаем ValueError)."""
    with pytest.raises(ValueError):
        get_mask_account(None)
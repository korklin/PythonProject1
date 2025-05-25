import pytest

from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card
from tests.conftest import data_base_date, data_base


# Корректные данные (разные форматы номера карты)
@pytest.mark.parametrize('input_card, expected_output', [
    ('1234567890123456', '1234 56** **** 3456'),  # Стандартный ввод
    ('1234-5678-9012-3456', '1234 56** **** 3456'),  # С разделителями
    (' 1234 5678 9012 3456 ', '1234 56** **** 3456'),  # С пробелами
    ('1234💀5678🐉9012_3456', '1234 56** **** 3456'),  # С нестандартными символами
])
def test_valid_card_masking(input_card, expected_output):
    """Проверка маскирования для валидных номеров карт."""
    assert get_mask_card_number(input_card) == expected_output

# Некорректные данные (должны вызывать ValueError)
@pytest.mark.parametrize('invalid_input, error_message', [
    ('123456789012345', 'Номер карты должен содержать 16 цифр'),  # 15 цифр
    ('12345678901234567', 'Номер карты должен содержать 16 цифр'),  # 17 цифр
    ('', 'Номер карты должен содержать 16 цифр'),  # Пустая строка
    ('abcd567890123456', 'Номер карты должен содержать 16 цифр'),  # Буквы вместо цифр
])
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
@pytest.mark.parametrize("input_account, expected_output", [
    ("1234567890", "**7890"),  # Стандартный ввод (10 цифр)
    ("1234", "**1234"),  # Минимальная длина (4 цифры)
    ("12 34 56 78 90", "**7890"),  # С пробелами
    ("1234-5678-90", "**7890"),  # С разделителями
    ("💳1234🐉5678_90", "**7890"),  # С нестандартными символами
])
def test_valid_account_masking(input_account, expected_output):
    """Проверка маскирования для валидных номеров счёта."""
    assert get_mask_account(input_account) == expected_output

# Некорректные данные (должны вызывать ValueError)
@pytest.mark.parametrize("invalid_input, error_message", [
    ("123", "Номер счёта должен содержать минимум 4 цифры"),  # 3 цифры
    ("", "Номер счёта должен содержать минимум 4 цифры"),  # Пустая строка
    ("abc567890", "Номер счёта должен содержать минимум 4 цифры"),  # Буквы вместо цифр
])
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



# ----- Корректные данные -----
@pytest.mark.parametrize('input_data, expected_output', [
    # Тесты для карт
    ('Maestro 1596837868705199', 'Maestro 159683 78** **** 5199'),
    ('Visa Classic 6831982476737658', 'Visa Classic 683198 24** **** 7658'),
    ('MasterCard 7158300734726758', 'MasterCard 715830 07** **** 6758'),
    ('Visa Platinum 8990922113665229', 'Visa Platinum 899092 21** **** 5229'),
    ('Visa Gold 5999414228426353', 'Visa Gold 599941 42** **** 6353'),

    # Тесты для счетов
    ('Счет 64686473678894779589', 'Счет **9589'),
    ('Счет 35383033474447895560', 'Счет **5560'),
    ('cчет 73654108430135874305', 'Счет **4305'),  # Проверка регистра
])
def test_valid_masking(input_data, expected_output):
    """Проверка корректного маскирования для разных типов платежей"""
    assert mask_account_card(input_data) == expected_output


# ----- Некорректные данные -----
@pytest.mark.parametrize('invalid_input, error_message', [
    # Ошибки для карт
    ('Visa 123456789012345', 'Номер карты должен содержать 16 цифр'),  # 15 цифр
    ('Mastercard abcdefghijklmnop', 'Номер карты должен содержать 16 цифр'),  # буквы

    # Ошибки для счетов
    ('Счет 123', 'Номер счета слишком короткий'),  # <20 цифр
    ('Счет abcdefghij', 'Номер счета слишком короткий'),  # нет цифр

    # Общие ошибки
    ('', 'Нет цифр в номере'),  # пустая строка
    ('Just Text', 'Нет цифр в номере'),  # нет цифр вообще
    (None, 'argument of type', 'NoneType')  # None
])

def test_invalid_input(invalid_input, error_message):
    """Проверка обработки некорректных данных"""
    with pytest.raises((ValueError, AttributeError)) as exc_info:
        mask_account_card(invalid_input)
    assert error_message in str(exc_info.value)


# ----- Граничные случаи -----
def test_exact_length():
    """Проверка граничных значений длины"""
    # Для карты (ровно 16 цифр)
    assert mask_account_card('Card 1234567890123456') == 'Card 123456 78** **** 3456'

    # Для счёта (ровно 20 цифр)
    assert mask_account_card('Счет 12345678901234567890') == 'Счет **7890'


# Корректные данные
@pytest.mark.parametrize('input_date, expected_output', [
    ('2024-03-11T02:26:18.671407', '11.03.2024'),  # Обычная дата
    ('1999-12-31T23:59:59.999999', '31.12.1999'),  # Граничный случай (последний день года)
    ('0001-01-01T00:00:00.000000', '01.01.0001'),  # Минимальная дата
])
def test_correct_date_conversion(input_date, expected_output):
    """Проверка корректного преобразования даты."""
    assert get_date(input_date) == expected_output

def test_get_date(input_date, expected_output):
    assert get_date(input_date) == expected_output

# Некорректные данные (должны вызывать ошибки)
@pytest.mark.parametrize('invalid_input', [
    '2024-03-11',                 # Нет 'T' и времени
    '2024/03/11T02:26:18',        # Неправильный разделитель даты
    'not-a-date',                 # Нечисловая строка
    '',                           # Пустая строка
])
def test_invalid_input(invalid_input):
    """Проверка, что функция падает с ошибкой на некорректных данных."""
    with pytest.raises((IndexError, ValueError)):
        get_date(invalid_input)


def test_filter_by_state(data_base: list, state: str = 'EXECUTED'):
    #Тест на фильстрацию по 'EXECUTED'
    assert filter_by_state(data_base, 'EXECUTED') == [{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
            {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}]
    #Тест на фильтрацию по 'CANCELED'
    assert filter_by_state(data_base, 'CANCELED') == [{'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
            {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}]


#Тест на пустой результат, если нет подходящих
def test_filter_by_state_empty(data_base):
    assert filter_by_state(data_base, 'UNKNOWN_STATE') == []


#Параметризированный тест для разных значений
@pytest.mark.parametrize('state, expected_ids', [('EXECUTED', [41428829, 939719570]), ('CANCELED', [594226727, 615064591]), ('UNKNOWN_STATE', [])])
def test_filter_by_state_parametrized(state, expected_ids, data_base):
    assert [item['id'] for item in filter_by_state(data_base, state)] == expected_ids

#Тест на сортировку по убыванию
def test_sort_by_date(data_base_date, data_base):
    assert [item['id'] for item in sort_by_date(data_base)] == [41428829, 615064591, 594226727, 939719570]


#Тест на сортировку по возрастанию
def test_sort_by_date_rev(data_base_date, data_base):
    assert [item['id'] for item in sort_by_date(data_base, False)] == [939719570, 594226727, 615064591, 41428829]

#Тест на одинаковые даты
def test_sort_by_date_similar(data_base_date):
    ids = [item ['id'] for item in sort_by_date(data_base_date, sort_by=True)]
    index_41428829 = ids.index(41428829)
    index_41428830 = ids.index(41428830)
    assert index_41428829 < index_41428830, 'Сортировка нарушила порядок одинаковых дат!'

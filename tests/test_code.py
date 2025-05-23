import pytest

from src.processing import filter_by_state, sort_by_date
from tests.conftest import data_base_date, data_base, data_base_execute


#def test_get_mask_card_number(card_number: str):



#def test_get_mask_account(account_number: str):




#def test_mask_account_card(payment: str):




#def test_get_date(date_str: str):



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
def test_sort_by_date(data_base_date):
    assert [item['id'] for item in sort_by_date(data_base)] == [41428829, 615064591, 594226727, 939719570]


#Тест на сортировку по возрастанию
def test_sort_by_date(data_base_date):
    assert [item['id'] for item in sort_by_date(data_base, False)] == [939719570, 594226727, 615064591, 41428829]

#Тест на одинаковые даты
def test_sort_by_date(data_base_date):
    ids = [item ['id'] for item in sort_by_date(data_base_date, sort_by=True)]
    index_41428829 = ids.index(41428829)
    index_41428830 = ids.index(41428830)
    assert index_41428829 < index_41428830, 'Сортировка нарушила порядок одинаковых дат!'

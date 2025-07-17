import pytest
from unittest.mock import mock_open, patch, MagicMock
from datetime import datetime
from src.main import filter_transactions_by_status, sort_transactions, filter_rub, read_csv_transactions, read_xlsx_transactions, process_transactions
from io import StringIO


CSV_CONTENT = "id;date;amount;currency_name;state\n1;2023-01-01T10:00:00Z;1000;USD;done\n"


def test_read_csv_transactions() -> None:
    with patch("builtins.open", mock_open(read_data=CSV_CONTENT)):
        transactions = read_csv_transactions("fake_path.csv")

    assert len(transactions) == 1
    assert transactions[0]["id"] == "1"
    assert transactions[0]["amount"] == 1000
    assert transactions[0]["currency_name"] == "USD"
    assert transactions[0]["state"] == "done"
    assert isinstance(transactions[0]["date"], datetime)


def test_read_xlsx_transactions() -> None:
    mock_sheet = MagicMock()
    mock_sheet.__getitem__.return_value = [MagicMock(value="id"), MagicMock(value="date"), MagicMock(value="amount")]

    mock_sheet.iter_rows.return_value = [("1", "2023-01-01T10:00:00Z", 1000), (None, None, None)]  # Пропускается

    mock_workbook = MagicMock()
    mock_workbook.__getitem__.return_value = mock_sheet
    mock_workbook.active = mock_sheet

    with patch("openpyxl.load_workbook", return_value=mock_workbook):
        transactions = read_xlsx_transactions("fake.xlsx")

    assert len(transactions) == 1
    assert transactions[0]["id"] == "1"
    assert transactions[0]["amount"] == 1000
    assert isinstance(transactions[0]["date"], datetime)


def test_process_transactions_prints_correctly() -> None:
    sample_transactions = [
        {"id": "1", "amount": 100, "state": "done", "currency_name": "USD", "date": datetime.now()},
        {"id": "2", "amount": 200, "state": "pending", "currency_name": "USD", "date": datetime.now()},
        {"id": "3", "amount": 200, "state": "done", "currency_name": "EUR", "date": datetime.now()},
    ]

    with patch("builtins.print") as mock_print:
        process_transactions(sample_transactions)

    # Проверяем, что вызвался print с правильными строками
    calls = [call.args[0] for call in mock_print.call_args_list]
    assert "Всего транзакций: 3" in calls
    assert any("done: 2" in c for c in calls)
    assert any("USD: 2" in c for c in calls)
    assert any("EUR: 1" in c for c in calls)
    assert any("Самые крупные транзакции" in c for c in calls)


def test_filter_by_status(sample_transactions=None):
    result = filter_transactions_by_status(sample_transactions, "EXECUTED")
    assert len(result) == 2
    assert all(t["state"] == "EXECUTED" for t in result)


def test_sort_transactions(sample_transactions=None):
    tx = sample_transactions.copy()
    tx[0]["date"] = None
    tx[1]["date"] = "2023-05-01T10:00:00Z"
    tx[2]["date"] = "2023-01-01T09:00:00Z"
    tx[3]["date"] = "2023-12-01T08:00:00Z"
    from datetime import datetime
    tx[1]["date"] = datetime.strptime(tx[1]["date"], "%Y-%m-%dT%H:%M:%SZ")
    tx[2]["date"] = datetime.strptime(tx[2]["date"], "%Y-%m-%dT%H:%M:%SZ")
    tx[3]["date"] = datetime.strptime(tx[3]["date"], "%Y-%m-%dT%H:%M:%SZ")

    sorted_tx = sort_transactions(tx, ascending=True)
    assert sorted_tx[0]["date"].year == 2023
    assert sorted_tx[-1]["date"].year == 2023


def test_filter_rub(sample_transactions=None):
    rub_tx = filter_rub(sample_transactions)
    assert len(rub_tx) == 3
    assert all(t["currency_name"].lower() == "руб." for t in rub_tx)


# Примерные транзакции
transactions_test = [
    {"description": "Открытие вклада", "state": "EXECUTED", "currency_name": "руб.", "date": None, "amount": 5000},
    {"description": "Перевод", "state": "CANCELED", "currency_name": "usd", "date": None, "amount": 1000},
    {"description": "Оплата телефона", "state": "EXECUTED", "currency_name": "руб.", "date": None, "amount": 300},
]


def test_process_transactions_executed_rub_filter_and_search():
    user_inputs = [
        "EXECUTED",     # фильтр по статусу
        "нет",          # сортировка по дате
        "да",           # только рублевые
        "да",           # фильтр по описанию
        "вклад",        # ключевое слово
        "нет"           # подсчет категорий
    ]

    with patch("builtins.input", side_effect=user_inputs):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            process_transactions(transactions_test)

            output = mock_stdout.getvalue()

            # Проверки:
            assert "Операции отфильтрованы по статусу: EXECUTED" in output
            assert "Всего банковских операций в выборке: 1" in output
            assert "Открытие вклада" in output

def test_process_transactions_nothing_found():
        user_inputs = [
            "EXECUTED",  # статус
            "нет",  # сортировка
            "да",  # только рублевые
            "да",  # поиск
            "неизвестное",  # ключ
            "нет"  # категории
        ]

        with patch("builtins.input", side_effect=user_inputs):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                process_transactions(transactions_test)
                output = mock_stdout.getvalue()
                assert "Не найдено ни одной транзакции" in output
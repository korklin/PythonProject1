import pytest
from unittest.mock import mock_open, patch, MagicMock
from datetime import datetime
from src.transaction_processor import read_csv_transactions, read_xlsx_transactions, process_transactions


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

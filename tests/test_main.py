import csv
import json
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Any

import openpyxl
import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from _pytest.tmpdir import tmp_path

from src.main import (filter_rub, filter_transactions_by_status, print_transaction, process_transactions,
                      read_csv_transactions, read_json_transactions, read_xlsx_transactions, sort_transactions)


# Фикстуры для тестовых данных
@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {"id": 1, "date": datetime(2023, 1, 1), "amount": 100, "currency_name": "руб.", "state": "EXECUTED"},
        {"id": 2, "date": datetime(2023, 1, 2), "amount": 200, "currency_name": "USD", "state": "CANCELED"},
        {"id": 3, "date": datetime(2023, 1, 3), "amount": 300, "currency_name": "руб.", "state": "PENDING"},
    ]


@pytest.fixture
def sample_csv_file(sample_transactions: list[dict]) -> str:
    with NamedTemporaryFile(mode="w+", suffix=".csv", delete=False, encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "amount", "currency_name", "state"], delimiter=";")
        writer.writeheader()
        for t in sample_transactions:
            row = t.copy()
            row["date"] = row["date"].strftime("%Y-%m-%dT%H:%M:%SZ")
            writer.writerow(row)
        return f.name


@pytest.fixture
def sample_json_file(sample_transactions: list[dict]) -> str:
    with NamedTemporaryFile(mode="w+", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(sample_transactions, f, default=str)
        return f.name


@pytest.fixture
def sample_xlsx_file(sample_transactions: list[dict]) -> str:
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = "Transactions"
    ws.append(["id", "date", "amount", "currency_name", "state"])
    for t in sample_transactions:
        ws.append([t["id"], t["date"].strftime("%Y-%m-%dT%H:%M:%SZ"), t["amount"], t["currency_name"], t["state"]])

    with NamedTemporaryFile(mode="wb+", suffix=".xlsx", delete=False) as f:
        wb.save(f.name)
        return f.name


# Тесты функций чтения файлов
def test_read_csv_transactions(sample_csv_file: str, sample_transactions: list[dict]) -> None:
    transactions = read_csv_transactions(sample_csv_file)
    assert len(transactions) == 3
    assert transactions[0]["id"] == "1"
    assert transactions[0]["amount"] == 100
    assert transactions[0]["currency_name"] == "руб."


def test_read_json_transactions(sample_json_file: str, sample_transactions: list[dict], transactions: list) -> None:
    transactions = read_json_transactions(sample_json_file)
    assert len(transactions) == 3
    assert transactions[0]["id"] == 1
    assert transactions[0]["amount"] == 100


def test_read_xlsx_transactions(sample_xlsx_file: str, sample_transactions: list[dict]) -> None:
    transactions = read_xlsx_transactions(sample_xlsx_file)
    assert len(transactions) == 3
    assert transactions[0]["id"] == 1
    assert transactions[0]["amount"] == 100


# Тесты функций обработки транзакций
def test_filter_transactions_by_status(sample_transactions: list[dict]) -> None:
    executed = filter_transactions_by_status(sample_transactions, "EXECUTED")
    assert len(executed) == 1
    assert executed[0]["state"] == "EXECUTED"


def test_sort_transactions(sample_transactions: list[dict]) -> None:
    sorted_asc = sort_transactions(sample_transactions, ascending=True)
    assert sorted_asc[0]["id"] == 1
    assert sorted_asc[-1]["id"] == 3

    sorted_desc = sort_transactions(sample_transactions, ascending=False)
    assert sorted_desc[0]["id"] == 3
    assert sorted_desc[-1]["id"] == 1


def test_filter_rub(sample_transactions: list[dict]) -> None:
    rub_transactions = filter_rub(sample_transactions)
    assert len(rub_transactions) == 2
    assert all(t["currency_name"] == "руб." for t in rub_transactions)


def test_print_transaction(capsys: pytest.CaptureFixture[str], sample_transactions: list[dict]) -> None:
    print_transaction(sample_transactions[0])
    captured = capsys.readouterr()
    assert "01.01.2023" in captured.out
    assert "100 руб." in captured.out


# Интеграционный тест
def test_process_transactions(
    capsys: pytest.CaptureFixture[str], sample_transactions: list[dict], monkeypatch: pytest.MonkeyPatch
) -> None:
    # Мокаем ввод пользователя
    inputs = iter(
        [
            "EXECUTED",  # статус
            "да",  # сортировать?
            "возрастанию",  # направление
            "нет",  # только рубли?
            "нет",  # фильтр по описанию?
            "нет",  # подсчет категорий?
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    process_transactions(sample_transactions)
    captured = capsys.readouterr()
    assert "Распечатываю итоговый список транзакций" in captured.out
    assert "Всего банковских операций в выборке: 1" in captured.out


# Тест на пустые данные
def test_empty_transactions(capsys: pytest.CaptureFixture[str]) -> None:
    process_transactions([])
    captured = capsys.readouterr()
    assert "Список транзакций пуст." in captured.out


# Пропущенные значения в amount или date
def test_read_csv_missing_fields(tmp_path: Any) -> None:
    csv_path = tmp_path / "missing.csv"
    csv_path.write_text("id;date;amount;currency_name;state\n1;;not_a_number;руб.;EXECUTED", encoding="utf-8")

    transactions: List[Dict[str, Any]] = read_csv_transactions(str(csv_path))
    assert transactions[0]["amount"] == 0
    assert transactions[0]["date"] is None


# Фильтрация по статусу с пробелами и регистром
def test_filter_transactions_case_insensitive(sample_transactions: List[Dict[str, Any]]) -> None:
    result = filter_transactions_by_status(sample_transactions, " EXECUTED ")
    assert len(result) == 1


# Ошибка при чтении JSON
def test_read_json_invalid(tmp_path: Any) -> None:
    bad_path = tmp_path / "bad.json"
    bad_path.write_text("{ invalid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        read_json_transactions(str(bad_path))

# C разными вариантами написания
def test_filter_rub_variants() -> None:
    txs = [{"currency_name": " РУБ. "}, {"currency_name": "usd"}, {"currency_name": "Руб."}]
    filtered = filter_rub(txs)
    assert len(filtered) == 2


# Нет совпадений после фильтрации
def test_process_transactions_no_match(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str], sample_transactions: List[Dict[str, Any]]) -> None:
    inputs = iter([
        "EXECUTED",
        "нет",  # сортировка
        "да",   # фильтр по валюте
        "да",   # фильтр по описанию
        "несуществующее_слово",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    process_transactions(sample_transactions)
    out = capsys.readouterr().out
    assert "Не найдено ни одной транзакции" in out

# Транзакции без даты
def test_sort_transactions_with_missing_date(sample_transactions: List[Dict[str, Any]]) -> None:
    sample_transactions[0]["date"] = None
    sorted_tx = sort_transactions(sample_transactions)
    assert sorted_tx[0]["date"] is None  # должна идти первой


# Параметризованный тест для filter_transactions_by_status
@pytest.mark.parametrize(
    "status_input, expected_ids",
    [
        ("EXECUTED", [1]),
        ("executed", [1]),
        ("  executed  ", [1]),
        ("CANCELED", [2]),
        ("pending", [3]),
        ("PENDING ", [3]),
        ("nonexistent", []),
        ("", []),
        ("   ", []),
    ]
)
def test_filter_transactions_by_status_parametrized(
    sample_transactions: List[Dict[str, Any]],
    status_input: str,
    expected_ids: List[int]
) -> None:
    result = filter_transactions_by_status(sample_transactions, status_input)
    result_ids = [t["id"] for t in result]
    assert result_ids == expected_ids


# Параметризованный тест для sort_transactions
@pytest.fixture
def unsorted_transactions() -> List[Dict[str, Any]]:
    return [
        {"id": 3, "date": datetime(2023, 1, 3)},
        {"id": 1, "date": datetime(2023, 1, 1)},
        {"id": 2, "date": datetime(2023, 1, 2)},
    ]

@pytest.mark.parametrize(
    "ascending, expected_order",
    [
        (True, [1, 2, 3]),
        (False, [3, 2, 1]),
    ]
)
def test_sort_transactions_parametrized(
    unsorted_transactions: List[Dict[str, Any]],
    ascending: bool,
    expected_order: List[int]
) -> None:
    sorted_tx = sort_transactions(unsorted_transactions, ascending=ascending)
    result_ids = [t["id"] for t in sorted_tx]
    assert result_ids == expected_order


# Параметризованный тест для filter_rub
@pytest.mark.parametrize(
    "transactions, expected_ids",
    [
        (
            [
                {"id": 1, "currency_name": "руб."},
                {"id": 2, "currency_name": "usd"},
                {"id": 3, "currency_name": "РУБ."},
                {"id": 4, "currency_name": "  руб.  "},
            ],
            [1, 3, 4]
        ),
        (
            [
                {"id": 5, "currency_name": "euro"},
                {"id": 6, "currency_name": "rub"},  # нет точки
            ],
            []
        )
    ]
)
def test_filter_rub_parametrized(transactions: List[Dict[str, Any]], expected_ids: List[int]) -> None:
    result = filter_rub(transactions)
    result_ids = [t["id"] for t in result]
    assert result_ids == expected_ids

# Некорректный путь к файлу
def test_read_json_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        read_json_transactions("nonexistent_file.json")


# Тест на ввод некорректного статуса в process_transactions
def test_process_transactions_invalid_status(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str], sample_transactions: List[Dict[str, Any]]) -> None:
    inputs = iter([
        "WRONG",  # неверный статус
        "CANCELED",  # корректный
        "нет", "нет", "нет", "нет"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    process_transactions(sample_transactions)
    out = capsys.readouterr().out
    assert "Статус 'WRONG' недопустим" in out
    assert "Операции отфильтрованы по статусу: CANCELED" in out


def test_read_xlsx_invalid_date_handling(tmp_path: Path) -> None:
    path = tmp_path / "bad_date.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = "Sheet1"
    ws.append(["id", "date", "amount", "currency_name", "state"])
    ws.append([1, "invalid_date", "100", "руб.", "EXECUTED"])
    wb.save(path)

    result = read_xlsx_transactions(str(path))
    assert result[0]["date"] is None


def test_process_transactions_with_categories(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str], sample_transactions: List[Dict[str, Any]]) -> None:
    inputs = iter([
        "EXECUTED",
        "нет", "нет", "нет",  # сортировка, рубли, описание
        "да",
        "вклад, перевод"
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    process_transactions(sample_transactions)
    out = capsys.readouterr().out
    assert "Операции по категориям" in out

def test_read_csv_extra_columns(tmp_path: Path) -> None:
    path = tmp_path / "extra.csv"
    path.write_text(
        "state;id;amount;currency_name;date;extra\n"
        "EXECUTED;1;100;руб.;2023-01-01T00:00:00Z;ignored",
        encoding="utf-8"
    )
    transactions = read_csv_transactions(str(path))
    assert transactions[0]["id"] == "1"
    assert transactions[0]["amount"] == 100
    assert "extra" in transactions[0]

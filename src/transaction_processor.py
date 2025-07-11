import csv
import openpyxl
from datetime import datetime
from typing import List, Dict, Union


def read_csv_transactions(file_path: str) -> List[Dict[str, Union[str, int, datetime]]]:
    """
    Чтение транзакций из CSV файла
    """
    transactions = []

    with open(file_path, mode='r', encoding='utf-8') as file:
        # Определяем разделитель как точку с запятой
        reader = csv.DictReader(file, delimiter=';')

        for row in reader:
            # Преобразуем строку даты в объект datetime
            try:
                row['date'] = datetime.strptime(row['date'], '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                row['date'] = None

            # Преобразуем amount в число
            try:
                row['amount'] = int(row['amount'])
            except (ValueError, KeyError):
                row['amount'] = 0

            transactions.append(row)

    return transactions


def read_xlsx_transactions(file_path: str, sheet_name: str = None) -> List[Dict[str, Union[str, int, datetime]]]:
    """
    Чтение транзакций из XLSX файла
    """
    transactions = []

    # Загружаем книгу Excel
    workbook = openpyxl.load_workbook(file_path)

    # Выбираем лист (если не указан, берем первый)
    sheet = workbook[sheet_name] if sheet_name else workbook.active

    # Получаем заголовки из первой строки
    headers = [cell.value for cell in sheet[1]]

    # Обрабатываем строки, начиная со второй
    for row in sheet.iter_rows(min_row=2, values_only=True):
        transaction = dict(zip(headers, row))

        # Пропускаем пустые строки
        if not transaction.get('id'):
            continue

        # Преобразуем дату
        if isinstance(transaction['date'], str):
            try:
                transaction['date'] = datetime.strptime(transaction['date'], '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                transaction['date'] = None
        elif isinstance(transaction['date'], datetime):
            pass  # Уже в правильном формате
        else:
            transaction['date'] = None

        # Преобразуем amount в число
        try:
            transaction['amount'] = int(transaction['amount'])
        except (ValueError, TypeError):
            transaction['amount'] = 0

        transactions.append(transaction)

    return transactions


def process_transactions(transactions: List[Dict]) -> None:
    """
    Обработка и вывод информации о транзакциях
    """
    print(f"Всего транзакций: {len(transactions)}")

    if not transactions:
        return

    # Статистика по статусам
    status_counts = {}
    for t in transactions:
        status = t.get('state', 'UNKNOWN')
        status_counts[status] = status_counts.get(status, 0) + 1

    print("\nСтатистика по статусам:")
    for status, count in status_counts.items():
        print(f"{status}: {count}")

    # Топ-5 валют по количеству транзакций
    currency_counts = {}
    for t in transactions:
        currency = t.get('currency_name', 'UNKNOWN')
        currency_counts[currency] = currency_counts.get(currency, 0) + 1

    top_currencies = sorted(currency_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nТоп-5 валют по количеству транзакций:")
    for currency, count in top_currencies:
        print(f"{currency}: {count}")

    # Самая крупная транзакция
    max_amount = max(t['amount'] for t in transactions if 'amount' in t)
    largest_transactions = [t for t in transactions if t.get('amount') == max_amount]

    print("\nСамые крупные транзакции (сумма: {max_amount}):")
    for t in largest_transactions:
        print(f"ID: {t['id']}, Дата: {t['date']}, Валюта: {t['currency_name']}")


def main():
    # Обработка CSV файла
    print("Обработка CSV файла...")
    csv_transactions = read_csv_transactions('transactions.csv')
    process_transactions(csv_transactions)

    # Обработка XLSX файла
    print("\nОбработка XLSX файла...")
    xlsx_transactions = read_xlsx_transactions('transactions_excel.xlsx', 'Лист 1')
    process_transactions(xlsx_transactions)


if __name__ == "__main__":
    main()
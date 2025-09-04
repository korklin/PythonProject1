def filter_by_state(data_base: list, state: str = "EXECUTED") -> list:
    """
    Принимает список словарей и опционально значение для ключа state
    и возвращает новый список словарей, содержащий только те словари, у которых ключ
    state соответствует указанному значению.
    """
    new_data_base = []
    # Запускаем цикл для проверки статуса ключа state
    for data in data_base:
        if data.get("state") == state:
            new_data_base.append(data)
        else:
            continue
        if len(new_data_base) < 1:
            print('Операции с таким статусом не найдено')
        else:
            pass
    return new_data_base


def sort_by_date(data_base: list, sort_by: bool = True) -> list:
    """
    Принимает список словарей и необязательный параметр, задающий порядок сортировки
    (по умолчанию — убывание). Функция должна возвращать новый список, отсортированный
    по дате (date).
    """
    sorted_date = []
    try:
        for data in data_base:
            sorted_date = sorted(data_base, key=lambda data: data["date"], reverse=sort_by)
        return sorted_date
    except (ValueError, KeyError) as e:
        raise ValueError(f'Некорректный формат даты:{e}')

from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(payment: str) -> str:
    """
    Маскирует номер карты, оставляя первые 6 и последние 4 цифры,
    либо номер счета, оставляя последние 4 цифры
    """
    # Находим индекс первой цифры
    first_digit_pos = next((i for i, c in enumerate(payment) if c.isdigit()), None)

    # Разделяем строку с сохранением регистров
    payment_type = payment[:first_digit_pos].strip()
    payment_number = ''.join(filter(str.isdigit, payment[first_digit_pos:]))
    if 'счет' in payment_type.lower():
        if len(payment_number) < 20:
            raise ValueError('Номер счета слишком короткий')
        masked = get_mask_account(payment_number)
        return f'{payment_type.capitalize()} {masked}'
    else:
        if len(payment_number) != 16:
            raise ValueError('Номер карты должен содержать 16 цифр')
        masked = get_mask_card_number(payment_number)

    return f'{payment_type} {masked}'


def get_date(date_str: str) -> str:
    '''Функция принимает на вход строку с датой в формате
       "2024-03-11T02:26:18.671407" и возвращает строку с датой в формате
       "ДД.ММ.ГГГГ"
    '''

    if not date_str:
        raise ValueError('Пустая строка')
    if 'T' not in date_str or date_str.index('T') != 10:
        raise ValueError('Некорректный формат')
    # Разделяем дату и время по символу 'T'
    date_part = date_str.split('T')[0]
    # Проверяем, что дата состоит из трёх частей, разделённых "-"
    if date_part.count('-') != 2:
        raise ValueError('Некорректный разделитель. Используйте "-"')

    try:
        year, month, day = date_part.split('-')
        # Проверяем, что год, месяц и день состоят из цифр
        if not (year.isdigit() and month.isdigit() and day.isdigit()):
            raise ValueError('Год, месяц и день должны быть числами')
        return f'{day}.{month}.{year}'
    except ValueError as e:
        raise ValueError(f'Ошибка обработки даты: {e}')


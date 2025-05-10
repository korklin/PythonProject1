from masks import get_mask_account, get_mask_card_number


def mask_account_card(payment: str) -> str:
    """
    Маскирует номер карты, оставляя первые 6 и последние 4 цифры,
    либо номер счета, оставляя последние 4 цифры
    """
    # Находим индекс первой цифры
    first_digit_pos = next((i for i, c in enumerate(payment) if c.isdigit()), None)

    # Разделяем строку с сохранением регистров
    payment_type = payment[:first_digit_pos].strip()
    payment_number = "".join(filter(str.isdigit, payment[first_digit_pos:]))
    if "Счет" in payment:
        if len(payment_number) < 20:
            raise ValueError("Номер счета слишком короткий")
        masked = get_mask_account(payment_number)
        return f"{payment_type.capitalize()} {masked}"
    else:
        if len(payment_number) != 16:
            raise ValueError("Номер карты должен содержать 16 цифр")
        masked = get_mask_card_number(payment_number)

    return f"{payment_type} {masked}"


def get_date(date_str: str) -> str:
    '''Функция принимает на вход строку с датой в формате
       "2024-03-11T02:26:18.671407" и возвращает строку с датой в формате
       "ДД.ММ.ГГГГ"
    '''
    # Разделяем дату и время по символу 'T'
    date_part = date_str.split("T")[0]
    year, month, day = date_part.split("-")
    return f"{day}.{month}.{year}"


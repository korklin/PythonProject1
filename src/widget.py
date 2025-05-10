def mask_account_card(payment_type: str, payment_number: str) -> str:
    '''
    Маскирует номер карты, оставляя первые 6 и последние 4 цифры,
    либо номер счета, оставляя последние 4 цифры
    '''

    cleaned_number = ''.join(filter(str.isdigit, payment_number))
    if data_type == 'Счет':
        if len(cleaned_number) < 20:
            raise ValueError ('Номер счета слишком короткий')
        masked = get_mask_account(cleaned_number)
    else:
        if len(cleaned_number) != 16:
            raise ValueError ('Номер карты должен содержать 16 цифр')
        masked = get_mask_card_number(cleaned_number)

    return f'{payment_type.capitalize()} {masked}'


def get_date (date_str: str) -> str:
    # Разделяем дату и время по символу 'T'
    date_part = date_str.split('T')[0]
    year, month, day = date_part.split('-')
    return f'{day}.{month}.{year}'
def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер карты, оставляя первые 6 и последние 4 цифры.
    """
    # Удаляем все нецифровые символы (если есть)
    cleaned_number = "".join(filter(str.isdigit, card_number))

    # Проверяем, что номер карты валидный
    if len(cleaned_number) != 16:
        raise ValueError("Номер карты должен содержать 16 цифр")

    # Разбиваем на части и маскируем
    part1 = cleaned_number[:4]
    part2 = cleaned_number[4:6]
    part3 = "****"
    part4 = cleaned_number[-4:]

    # Собираем результат
    masked_number = f"{part1} {part2}** {part3} {part4}"
    return masked_number


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер счёта, оставляя только последние 4 цифры.
    """
    # Удаляем все нецифровые символы (если есть)
    cleaned_number = "".join(filter(str.isdigit, account_number))

    # Проверяем, что номер счёта валидный (минимум 4 цифры)
    if len(cleaned_number) < 4:
        raise ValueError("Номер счёта должен содержать минимум 4 цифры")

    # Получаем последние 4 цифры
    last_four = cleaned_number[-4:]

    # Формируем маскированный номер
    masked_account = f"**{last_four}"
    return masked_account

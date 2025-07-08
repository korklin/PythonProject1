import logging
from datetime import datetime
from pathlib import Path


# Настройка логирования
def setup_logging() -> None:
    """Настройка конфигурации логирования"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)  # Создаем папку logs, если её нет

    log_file = logs_dir / f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w"),  # 'w' для перезаписи при каждом запуске
            logging.StreamHandler(),
        ],
    )


setup_logging()
logger = logging.getLogger(__name__)


def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер карты, оставляя первые 6 и последние 4 цифры.
    Логирует ошибки валидации.
    """
    # Удаляем все нецифровые символы (если есть)
    try:
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
        logger.error(f"Успешная маскировка карты: {masked_number}")
        return masked_number
    except ValueError as e:
        logger.error(f"Ошибка маскировки карты: {e}")
        raise


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер счёта, оставляя только последние 4 цифры.
    Логирует ошибки валидации
    """
    try:
        if account_number is None:
            raise ValueError("Номер счета не может быть None")
        # Удаляем все нецифровые символы (если есть)
        cleaned_number = "".join(filter(str.isdigit, account_number))

        # Проверяем, что номер счёта валидный (минимум 20 цифр)
        if len(cleaned_number) < 20:
            raise ValueError("Номер счёта должен содержать минимум 20 цифр")

        # Получаем последние 4 цифры
        last_four = cleaned_number[-4:]

        # Формируем маскированный номер
        masked_account = f"**{last_four}"
        logger.info(f": {masked_account}")
        return masked_account
    except ValueError as e:
        logger.error(f": {e}")
        raise

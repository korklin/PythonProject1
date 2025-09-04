import os
from functools import wraps
from typing import Any, Callable, Optional, TextIO, TypeVar, cast

from _pytest.capture import CaptureFixture

from src.decorators import log


# Основные функции с типизацией
@log(filename="test_log.txt")
def successful_func(a: int, b: int) -> int:
    """Складывает два числа."""
    return a + b


@log()
def failing_func(a: float, b: float) -> float:
    """Делит a на b."""
    return a / b


# Тесты с типизацией
def test_log_to_file_success() -> None:
    """Проверяем запись успешного выполнения в файл."""
    if os.path.exists("test_log.txt"):
        os.remove("test_log.txt")

    successful_func(2, 3)

    with open("test_log.txt", "r") as file:
        logs: str = file.read()

    assert "successful_func started" in logs
    assert "successful_func ok" in logs


def test_log_to_file_error() -> None:
    """Проверяем запись ошибки в файл."""
    log_file: str = "test_log.txt"
    if os.path.exists(log_file):
        os.remove(log_file)

    @log(filename=log_file)
    def divide(a: float, b: float) -> float:
        return a / b

    try:
        divide(10.0, 0.0)
    except ZeroDivisionError:
        pass

    with open(log_file, "r") as file:
        logs: str = file.read()

    assert "divide started" in logs
    assert "divide error: ZeroDivisionError" in logs
    assert "Inputs: (10.0, 0.0), {}" in logs


def test_log_to_console_success(capsys: CaptureFixture[str]) -> None:
    """Проверяем вывод успешного выполнения в консоль."""

    @log()
    def add(a: int, b: int) -> int:
        return a + b

    add(5, 7)
    captured = capsys.readouterr()
    output: str = captured.out

    assert "add started" in output
    assert "add ok" in output


def test_log_to_console_error(capsys: CaptureFixture[str]) -> None:
    """Проверяем вывод ошибки в консоль."""

    @log()
    def div(a: float, b: float) -> float:
        return a / b

    try:
        div(1.0, 0.0)
    except ZeroDivisionError:
        pass

    captured = capsys.readouterr()
    output: str = captured.out

    assert "div started" in output
    assert "div error: ZeroDivisionError" in output
    assert "Inputs: (1.0, 0.0), {}" in output

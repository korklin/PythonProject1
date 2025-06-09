import datetime
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

T = TypeVar("T")  # Обобщенный тип для возвращаемого значения


def log(filename: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Декоратор для логирования выполнения функций."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            start_message = f"{current_time} - {func.__name__} started\n"

            if filename:
                with open(filename, "a") as file:
                    file.write(start_message)
            else:
                print(start_message, end="")

            try:
                result = func(*args, **kwargs)
                end_message = f"{current_time} - {func.__name__} ok\n"

                if filename:
                    with open(filename, "a") as file:
                        file.write(end_message)
                else:
                    print(end_message, end="")

                return result

            except Exception as e:
                error_message = (
                    f"{current_time} - {func.__name__} error: {type(e).__name__}. " f"Inputs: {args}, {kwargs}\n"
                )

                if filename:
                    with open(filename, "a") as file:
                        file.write(error_message)
                else:
                    print(error_message, end="")
                raise

        return cast(Callable[..., T], wrapper)

    return decorator

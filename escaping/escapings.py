from abc import ABC, abstractmethod
import re

from constants import (
    EMAIL_REGULAR_FOR_VALIDATION,
    PHONE_REGULAR_FOR_VALIDATION,
    SKYPE_REGULAR_FOR_VALIDATION,
    SKYPE_REGULAR,
)


class Escaping(ABC):
    """Абсткатный класс экранирования.

    Attributes:
        regular_for_validation (str): регулярное выражение для валидации.
    """

    regular_for_validation: str

    def __init__(self, escape_symbol: str) -> None:
        """Инициализация объекта.

        Args:
            escape_symbol (str): символ экранирования.
        """
        self.escape_symbol = escape_symbol

    def _validate_data(self, data: str) -> None:
        """Валидирует данные.

        Args:
            data (str): данные для валидации.
        """
        if not isinstance(data, str):
            raise ValueError("Данные должны быть строкой.")
        pattern = re.compile(self.regular_for_validation)
        if not pattern.match(data):
            raise ValueError("Данные не соответсвуют регулярному выражению.")

    @abstractmethod
    def _escaping_data(self, data: str) -> str:
        """Экранирует данные.

        Args:
            data (str): данные для экранирования.
        Returns:
            str: экранированные данные.
        """

    def get_escaping_data(self, data: str) -> str:
        """Возвращает экранированные данные.

        Args:
            data (str): данные для экранирования.
        Returns:
            str: экранированные данные.
        """
        self._validate_data(data)
        return self._escaping_data(data)


class EmailEscaping(Escaping):
    """Класс экранирования email.

    Attributes:
        regular_for_validation (str): регулярное выражение для валидации.
    """

    regular_for_validation = EMAIL_REGULAR_FOR_VALIDATION

    def _escaping_data(self, data: str) -> str:
        name, domen = data.split("@")
        name = re.sub(r".", self.escape_symbol, name)
        return f"{name}@{domen}"


class PhoneEscaping(Escaping):
    """Класс экранирования phone.

    Attributes:
        regular_for_validation (str): регулярное выражение для валидации.
    """

    regular_for_validation = PHONE_REGULAR_FOR_VALIDATION

    def __init__(self, escape_symbol: str, count_escape: int = 3) -> None:
        """Инициализация объекта.

        Args:
            escape_symbol (str): символ экранирования.
            count_escape (int, optional):
                количество символов экранирования. По дефолту 3.
        """
        super().__init__(escape_symbol)
        self.count_escape = count_escape

    def _escaping_data(self, data: str) -> str:
        data = re.sub(r"\s+", " ", data)
        return re.sub(
            r"\d",
            self.escape_symbol,
            data[::-1],
            self.count_escape,
        )[::-1]


class SkypeEscaping(Escaping):
    """Класс экранирования skype.

    Attributes:
        regular_for_validation (str): регулярное выражение для валидации.
    """

    regular_for_validation = SKYPE_REGULAR_FOR_VALIDATION

    def _escaping_data(self, data: str) -> str:
        return re.sub(SKYPE_REGULAR, f"skype:{self.escape_symbol*3}", data, 1)

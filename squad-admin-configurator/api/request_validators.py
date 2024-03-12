import hmac
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from dateutil.parser import isoparse as datetime_isoparse
from django.conf import settings
from rest_framework.request import Request
from rest_framework.validators import ValidationError

if TYPE_CHECKING:
    from .models import ReceivedWebhook

BM_MAX_DEVIATION = timedelta(seconds=settings.HMAC_VALIDATION["BATTLEMETRICS"]["MAX_DEVIATION_OF_TIMESTAMP_IN_SEC"])


class NotValidatedError(Exception):
    pass


class BaseRequestHMACValidator(ABC):
    """
    Абстрактный класс валидатора HMAC в запросе
    """

    def __init__(self, request: Request, webhook_object: "ReceivedWebhook") -> None:
        self.request: Request = request
        self.webhook_object: "ReceivedWebhook" = webhook_object

        # True if is_valid() has been called
        self._validate: bool = False
        self._error: Exception = None

    @property
    def errors(self) -> Exception:
        """Возвращает ошибку, которая была получена при валидации

        Raises:
            NotValidatedError: Если is_valid() не был вызван для этого объекта

        Returns:
            Exception: Ошибка возникшая в процессе валидации
        """
        if self._validate:
            return self._error

        raise NotValidatedError("Before receiving errors, you need to call the is_valid() method")

    def is_valid(self, raise_validation_error=True) -> bool:
        """Проверяет валиден ли запрос по отношению к вебхуку

        Args:
            raise_exception (bool, optional): Пробрасывать ли ValidationError в
            вызывающий код. Defaults to True.

        Raises:
            error: ValidationError который был получен при валидации

        Returns:
            bool: валиден ли запрос
        """

        try:
            self.validate_hmac()
            return True
        except ValidationError as error:
            self._error = error
            if raise_validation_error:
                raise error
            return False
        finally:
            self._validate = True

    @abstractmethod
    def validate_hmac(self) -> None:
        """Получает сигнатуры из заголовка запроса, генерирует сигнатуру из
        данных

        Raises:
            ValidationError: В любой непонятной ситуации
        """
        raise NotImplementedError("validate_hmac is not implemented")

    @abstractmethod
    def get_signature_from_request(self) -> str:
        """Получает сигнатуру по регулярке из заголовка полученного запроса

        Raises:
            ValidationError: Если сигнатуру получить не удалось
        Returns:
            str: Сигнатура
        """
        raise NotImplementedError("get_signature_from_request is not implemented")

    @abstractmethod
    def generate_signature_from_request(self) -> str:
        """Генерирует сигнатуру через hmac.digest из данных самого запроса

        Raises:
            ValidationError: Если по каким то причинам генерация сигнатуры
                             невозможна
        Returns:
            str: Сигнатура
        """
        raise NotImplementedError("generate_signature_from_request is not implemented")

    def compare_signature(self, sign_1, sign_2) -> bool:
        """Сравнивает две сигнатура через функцию с постоянным временем

        Args:
            sign_1 (str): Сигнатура 1
            sign_2 (str): Сигнатура 2

        Returns:
            bool: True если сигнатуры одинаковые, False если разные
        """
        return hmac.compare_digest(sign_1, sign_2)


class DefaultRequestHMACValidator(BaseRequestHMACValidator):
    """
    Стандартный валидатор HMAC, получает сигнатуру из заголовка по регулярке
    без какой либо логики, во время локальный генерации из hmac из данных
    запроса - просто передаёт request.data в hmac.digest, тоже без особой
    логики
    """

    def validate_hmac(self) -> None:
        if not self.webhook_object.hmac_is_active:
            return

        if self.webhook_object.hmac_header not in self.request.headers:
            raise ValidationError("HMAC header not found")

        signature_from_request: str = self.get_signature_from_request()

        if signature_from_request is None:
            raise ValidationError("HMAC signature in header not found")

        generated_signature: str = self.generate_signature_from_request()

        if not self.compare_signature(signature_from_request, generated_signature):
            raise ValidationError("Request body, signature or secret key is corrupted, hmac does not match")

    def get_signature_from_request(self) -> str | None:
        header = self.request.headers[self.webhook_object.hmac_header]

        match_header: re.Match | None = re.search(
            self.webhook_object.hmac_header_regex,
            header,
            re.A,
        )
        return match_header.group(0) if match_header else None

    def generate_signature_from_request(self) -> str:
        return hmac.digest(
            self.webhook_object.hmac_secret_key.encode(),
            self.request.body,
            self.webhook_object.hmac_hash_type,
        ).hex()


class BattlemetricsRequestHMACValidator(DefaultRequestHMACValidator):
    """Валидатор запроса по hmac для запросов от Battlemetrics или реализующих
    его логику сервисов

    Разница в том, что Battlemetrics передаёт в заголовке сигнатуры еще
    и timestamp в iso формате, данный валидатор ищет эту дату, парсит и
    сравнивает текущее время с временем timestamp (с учетом возможного
    отклонения его от текущего времени в одну и в другую сторону)

    Сигнатура из request.data формируется из данных в формате
    {timestamp}.{request.data}
    """

    def generate_signature_from_request(self) -> str:
        now: datetime = datetime.now(timezone.utc)
        header = self.request.headers[self.webhook_object.hmac_header]

        timestamp_match = re.search(r"(?<=t=)[\w\-:.+]+(?=,|\Z)", header, flags=re.A)

        if timestamp_match is None:
            raise ValidationError("Timestamp in HMAC header not found")

        timestamp_text = timestamp_match.group(0)

        try:
            timestamp = datetime_isoparse(timestamp_text)
        except ValueError:
            raise ValidationError("Timestamp in HMAC header have not valid format, required iso format")

        if timestamp.tzinfo is None:
            raise ValidationError("Timestamp in HMAC header must have a timezone")

        if not (now - BM_MAX_DEVIATION < timestamp < now + BM_MAX_DEVIATION):
            raise ValidationError("Timestamp is very old or very far in the future")

        return hmac.digest(
            self.webhook_object.hmac_secret_key.encode(),
            f"{timestamp_text}.".encode() + self.request.body,
            self.webhook_object.hmac_hash_type,
        ).hex()

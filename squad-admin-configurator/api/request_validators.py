import hmac
import re
from datetime import datetime, timedelta, timezone

from api.models import ReceivedWebhook
from dateutil.parser import isoparse
from django.conf import settings
from rest_framework.validators import ValidationError

BM_MAX_DEVIATION = settings.HMAC_VALIDATION["BATTLEMETRICS"][
    "MAX_DEVIATION_OF_TIMESTAMP_IN_SEC"
]


def get_signature_from_header(header, pattern):
    """Извлечение сигнатуры из заголовка"""
    match_header = re.search(pattern, header, re.A)
    return match_header.group(0) if match_header else None


def generate_signature_from_request(request, webhook_object):
    """
    Генерация сигнатуры из реквеста, секретного ключа и типа хеша,
    для некоторых сервисов алгоритмы генерации HMAC слегка отличаются
    """
    if webhook_object.request_sender == ReceivedWebhook.BATTLEMETRICS:
        now = datetime.now(timezone.utc)
        deviation_timed = timedelta(seconds=BM_MAX_DEVIATION)
        header = request.headers[webhook_object.hmac_header]

        timestamp_match = re.search(
            r"(?<=t=)[\w\-:.+]+(?=,|\Z)", header, flags=re.A
        )
        if timestamp_match is None:
            raise ValidationError("Timestamp in HMAC header not found")

        timestamp_text = timestamp_match.group(0)

        try:
            timestamp = isoparse(timestamp_text)
        except ValueError:
            raise ValidationError(
                "Timestamp in HMAC header have not valid format"
            )

        if not (now - deviation_timed < timestamp < now + deviation_timed):
            raise ValidationError(
                "Timestamp is very old or very far in the future"
            )

        return hmac.digest(
            webhook_object.hmac_secret_key.encode(),
            f"{timestamp_text}.".encode() + request.body,
            webhook_object.hmac_hash_type,
        ).hex()

    return hmac.digest(
        webhook_object.hmac_secret_key.encode(),
        request.body,
        webhook_object.hmac_hash_type,
    ).hex()


def validate_hmac_in_request(request, webhook_object):
    """
    Полный пайплайн генерации и валидации HMAC с выбросом наружу
    ValidationError при ошибках валидации
    """

    if not webhook_object.hmac_is_active:
        return

    if webhook_object.hmac_header not in request.headers:
        raise ValidationError("HMAC header not found")

    header = request.headers[webhook_object.hmac_header]

    request_hmac_signature = get_signature_from_header(
        header, webhook_object.hmac_header_regex
    )

    if request_hmac_signature is None:
        raise ValidationError("HMAC signature in header not found")

    generated_hmac_signature = generate_signature_from_request(
        request, webhook_object
    )

    if not hmac.compare_digest(
        generated_hmac_signature, request_hmac_signature
    ):
        raise ValidationError(
            "Request body, signature or secret key is corrupted, "
            "hmac does not match"
        )

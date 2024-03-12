import logging
from collections.abc import Sequence

from discord_webhook import DiscordWebhook
from requests.exceptions import Timeout


def send_messages_to_discord(
    webhook_uri: str,
    username: str,
    messages: list[str] | str = None,
) -> None:
    if isinstance(messages, str):
        messages: list[str] = [messages]
    elif not isinstance(messages, Sequence):
        raise ValueError("message must be a sequence")

    discord_webhook = DiscordWebhook(
        url=webhook_uri,
        username=username,
        rate_limit_retry=True,
    )

    for text in messages:
        discord_webhook.content = text
        last_error: None | Exception = None
        for _ in range(3):
            try:
                discord_webhook.execute()
                last_error = None
            except Timeout as e:
                logging.warning(f'Timeout when send message "{text}" to discord')
                last_error = e
            except ConnectionError as e:
                logging.warning(f'Connection error when send message "{text}" to discord')
                last_error = e
            break

        if last_error is not None:
            logging.error("Ошибка при отправке сообщения в дискорд", exc_info=last_error)

from datetime import datetime
from hashlib import algorithms_available as hashlib_algorithms
from ipware import get_client_ip

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from server_admins.models import Role, Server

from .validators import regex_validator, url_postfix_validator


class WebhookLog(models.Model):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'

    LOG_LEVELS = [
        (INFO, 'Информация'),
        (WARNING, 'Предупреждение'),
        (ERROR, 'Ошибка')
    ]

    message = models.TextField('Лог сообщений')
    request_info = models.TextField(
        'Сведения о запросе', blank=True
    )
    webhook_info = models.TextField('Сведения о вебхуке')
    level = models.CharField(
        'Уровень логирования',
        max_length=10,
        choices=LOG_LEVELS
    )

    creation_date = models.DateTimeField(
        'Дата создания сообщения',
        auto_now_add=True
    )

    content_type = models.ForeignKey(
        ContentType,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Модель вебхука'
    )
    object_id = models.PositiveIntegerField('ID вебхука')
    content_object = GenericForeignKey()

    def __str__(self):
        return self.message[:50]

    class Meta:
        verbose_name = 'Лог вебхука'
        verbose_name_plural = '1. Логи вебхуков'
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        ordering = ('-creation_date', )


class ReceivedWebhook(models.Model):
    HMAC_HASHES = hashlib_algorithms
    HMAC_HASHES_CHOICES = sorted(list(zip(HMAC_HASHES, HMAC_HASHES)))

    BATTLEMETRICS = 'battlemetrics'
    REQUEST_SENDERS = [
        (BATTLEMETRICS, 'Battlemetrics.com')
    ]

    description = models.CharField('Описание', max_length=300)
    is_active = models.BooleanField('Активирован')

    url = models.CharField(
        'URL постфикс пути',
        max_length=100,
        unique=True,
        validators=(url_postfix_validator, )
    )

    creation_date = models.DateTimeField(
        'Дата добавления вебхука',
        auto_now_add=True
    )

    hmac_is_active = models.BooleanField(
        'Активирована ли проверка HMAC подписи',
        default=False,
        help_text=('Механизм проверки целостности информации, позволяющий '
                   'гарантировать то, что передаваемые данные не были '
                   'изменены посторонними лицами. Должен поддерживаться '
                   'тем, кто будет вызывать вебхук')
    )

    hmac_hash_type = models.CharField(
        'Тип хеша в HMAC',
        choices=HMAC_HASHES_CHOICES,
        max_length=64,
        blank=True,
        help_text=('Обычно предоставляется тем, кто будет вызывать вебхук, '
                   'например sha256 для Battlemetrics')
    )

    hmac_secret_key = models.CharField(
        'Секретный ключ HMAC',
        max_length=1024,
        blank=True,
        help_text='Обычно предоставляется тем, кто будет вызывать вебхук'
    )

    hmac_header = models.CharField(
        'Название заголовка который содержит HMAC сигнатуру',
        max_length=64,
        blank=True,
        help_text='Например X-SIGNATURE для Battlemetrics'
    )

    hmac_header_regex = models.CharField(
        'Регулярное выражение для получения HMAC сигнатуры из заголовка',
        max_length=256,
        blank=True,
        validators=(regex_validator, ),
        help_text=('Например .* если весь заголовок - сигнатура, '
                   r'или (?<=s=)\w+(?=,|\Z) для Battlemetrics')
    )

    request_sender = models.CharField(
        'Сервис отправляющий запрос',
        max_length=128,
        blank=True,
        choices=REQUEST_SENDERS,
        help_text=('Активирует специфичные для каждого сервиса алгоритмы '
                   'проверки HMAC у запроса')
    )

    def __str__(self):
        return self.description

    class Meta:
        abstract = True

    def clean(self):
        if self.hmac_is_active:
            checked_fields = {'hmac_hash_type': self.hmac_hash_type,
                              'hmac_secret_key': self.hmac_secret_key,
                              'hmac_header': self.hmac_header,
                              'hmac_header_regex': self.hmac_header_regex}

            errors = {}
            for name, field in checked_fields.items():
                if field == '':
                    errors[name] = ('Обязательное поле при активированной '
                                    'проверки HMAC')

            raise ValidationError(errors)

        return super().clean()

    def get_webhook_info(self):
        """
        Возвращает строковое представление полей, используется при
        логировании

        Список полей специфичных для каждой модели вебхука - получается из
        поля LOGGED_FIELDS
        """
        list_fields = [
            'id', 'description', 'url', 'creation_date',
            'hmac_is_active', 'hmac_hash_type', 'hmac_header',
            'request_sender'
        ]

        try:
            list_fields.extend(self.__getattribute__('LOGGED_FIELDS'))
        except AttributeError:
            pass

        return_info = []
        for field_name in list_fields:
            verbose_name = (
                self._meta.get_field(field_name).verbose_name
            )

            field = self.__getattribute__(field_name)
            if isinstance(field, datetime):
                field = field.isoformat()
            elif field.__class__.__name__ == 'ManyRelatedManager':
                field = ', '.join([str(m2m_model)
                                  for m2m_model in field.all()])

            return_info.append(
                f'{verbose_name}: {field}'
            )

        return '\n'.join(return_info)

    def write_log(self, message, log_level, request=None):

        request_info = ''
        if request is not None:
            ip, _ = get_client_ip(request)
            request_info = (f'IP: {ip}\n'
                            f'User-agent: {request.headers.get("user-agent")}')

        WebhookLog.objects.create(
            message=message,
            level=log_level,
            content_object=self,
            webhook_info=self.get_webhook_info(),
            request_info=request_info
        )


class ServerUrl(models.Model):
    """
    Модель предназначена для хранения url и управления доступностью
    получения конфигурации админов игрового сервера через API
    """
    server = models.OneToOneField(
        Server,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='Сервер',
        related_name='server_url'
    )
    is_active = models.BooleanField('Активирована ли раздача файла')
    url = models.CharField('URL постфикс пути', max_length=100, unique=True,
                           validators=(url_postfix_validator, ))

    def __str__(self):
        return self.server.title

    class Meta:
        verbose_name = 'Доступ к конфигурации игрового сервера'
        verbose_name_plural = '2. Доступ к конфигурации игрового сервера'


class RoleWebhook(ReceivedWebhook):
    """
    Модель вебхуков на добавления ролей на серверах
    """
    LOGGED_FIELDS = ['servers', 'roles', 'unit_of_duration',
                     'allow_custom_duration_until_end', 'duration_until_end',
                     'active_and_increase_common_date_of_end']

    # Хранимое в базе имя единицы измерения - фактически название параметра
    # для timedelta, например:
    # timedelta(hours=5)
    #           ^^^^^
    HOUR = 'hours'
    DAY = 'days'
    WEEK = 'weeks'

    UNITS_OF_DURATION = [
        (HOUR, 'Час'),
        (DAY, 'День'),
        (WEEK, 'Неделя')
    ]

    servers = models.ManyToManyField(
        Server,
        verbose_name='Сервера на которых будут выданы роли'
    )

    roles = models.ManyToManyField(
        Role,
        verbose_name='Роли которые будут выданы на серверах'
    )

    unit_of_duration = models.CharField(
        'Единица измерения продолжительности',
        max_length=10,
        choices=UNITS_OF_DURATION,
        help_text='Единица измерения времени, на которое будет выдана роль'
    )

    allow_custom_duration_until_end = models.BooleanField(
        'Разрешено ли в запросе устанавливать продолжительность полномочий',
        default=False,
        help_text=('Если активно - в запросе можно передать число, время на '
                   'которое будет выдана роль')
    )

    duration_until_end = models.IntegerField(
        'Стандартно выдаваемая продолжительность полномочий',
    )

    active_and_increase_common_date_of_end = models.BooleanField(
        'Активировать пользователя и увеличивать общее время '
        'до окончания полномочий',
        default=True,
        help_text=('Если время до общего окончания полномочий меньше времени '
                   'чем выдаёт вебхук - общее время будет установлено на '
                   'время выданное вебхуком. Также активирует пользователя '
                   'если он был деактивирован. Если данный флаг выключен, '
                   'а у пользователя истекло время - '
                   'выдача вебхуком ролей фактически не будет срабатывать')
    )

    class Meta:
        verbose_name = 'Вебхук на добавление роли'
        verbose_name_plural = '3. Вебхуки на добавление ролей'

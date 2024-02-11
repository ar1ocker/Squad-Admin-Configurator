import argparse
import re

from django.core.management.base import BaseCommand, CommandParser
from django.db.transaction import atomic
from server_admins.models import (
    Permission,
    Privileged,
    Role,
    Server,
    ServerPrivileged,
)


def yes_or_no(text) -> bool:
    while True:
        answer: str = input(text + " (y/n): ").strip()
        if answer in ["y", "n"]:
            return True if answer == "y" else False


def question_with_confirmation(text) -> str:
    while True:
        answer: str = input(text + ": ").strip()

        if answer == "":
            continue

        if answer and yes_or_no(f'"{answer}", всё верно?'):
            return answer


class Command(BaseCommand):
    help = "Добавление админов, разрешений и ролей из конфига администраторов"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "file", type=argparse.FileType("r", encoding="utf-8")
        )

    def handle(self, *args, **options):
        processing_comment = question_with_confirmation(
            "Введите комментарий к обработке этого файла"
        )
        with atomic():
            server_id = self.choose_server()

            if server_id is None:
                server_id = self.create_server()

            file_text = options["file"].read()

            roles_list = self.find_roles(file_text)

            if roles_list is None:
                return

            roles_by_names = self.get_db_roles(roles_list)

            privileges = self.find_privileges(file_text)

            for config_priv in privileges:
                role = roles_by_names.get(config_priv["role"])
                if role is None:
                    self.stdout.write(
                        f'Роль {config_priv["role"]} не найдена, '
                        f'{config_priv["steam_id"]} пропущен'
                    )
                    continue

                priv, _ = Privileged.objects.get_or_create(
                    steam_id=config_priv["steam_id"],
                    defaults={
                        "name": (
                            config_priv["comment"] or config_priv["steam_id"]
                        ),
                        "description": processing_comment,
                    },
                )

                server_priv, _ = ServerPrivileged.objects.get_or_create(
                    server_id=server_id,
                    privileged=priv,
                    comment=processing_comment,
                )

                server_priv.roles.add(role)

    def find_privileges(self, file_text):
        """
        Поиск привилегированных пользователей
        """
        admin_regex = (
            r"(?m)^ *Admin=(?P<steam_id>\d+):"
            r"(?P<role>[\w]+) *(?://)* *(?P<comment>.*)$"
        )
        priv = [
            _match.groupdict()
            for _match in re.finditer(admin_regex, file_text)
        ]

        if len(priv) == 0:
            self.stdout.write("Привилегированные пользователи не найдены")
            return None

        self.stdout.write(
            "Найдены привилегированные пользователи:\n\t"
            + "\n\t".join([
                f'{admin["role"]}: {admin["steam_id"]}, {admin["comment"]}'
                for admin in priv
            ])
        )

        return priv

    def get_db_roles(self, roles) -> dict:
        """
        Возвращает связь названия ролей и фактических записей в БД
        """
        return_roles: dict[str, Role] = {}
        for config_role in roles:
            role: Role = self.create_new_role_or_get_old(
                config_role["title"],
                [
                    perm.strip()
                    for perm in config_role["permissions"].split(",")
                ],
            )

            return_roles[config_role["title"]] = role

        return return_roles

    def create_new_role_or_get_old(self, role_name, permissions_names) -> Role:
        """
        Создание новой роли или получении уже существующей
        """
        old_role = None
        try:
            old_role = Role.objects.prefetch_related("permissions").get(
                title=role_name
            )
        except Role.DoesNotExist:
            pass

        if old_role is None:
            return self.create_role(permissions_names, role_name)

        old_role_permissions = ", ".join(
            [str(perm) for perm in old_role.permissions.all()]
        )
        self.stdout.write(
            f"Роль {role_name} уже существует, создаем новую "
            "или используем существующую без изменения разрешений?\n"
            f"Разрешения на существующей роли: {old_role_permissions}\n"
            f"Разрешения на новой роли: {', '.join(permissions_names)}"
        )

        if yes_or_no("Используем существующую роль?"):
            return old_role
        else:
            return self.create_role(permissions_names)

    def create_role(self, permissions_names, role_name=None) -> Role:
        """
        Создание новой роли
        """
        while True:
            new_role_name = role_name or question_with_confirmation(
                "Введите название новой роли"
            )

            new_role, created = Role.objects.get_or_create(title=new_role_name)
            if created:
                self.stdout.write(f"Роль {new_role_name} создана")
                break

            self.stdout.write(f"Роль {new_role_name} уже существует")
            role_name = None

        perm_objects = []
        for perm in permissions_names:
            perm_objects.append(
                Permission.objects.get_or_create(title=perm)[0]
            )

        new_role.permissions.set(perm_objects)
        return new_role

    def find_roles(self, file_text):
        """
        Поиск ролей в файле
        """
        roles_regex = (
            r"(?m)^ *Group=(?P<title>\w+):"
            r"(?P<permissions>[\w, ]+)(?: *(?://)*.*$)"
        )
        roles = [
            _match.groupdict()
            for _match in re.finditer(roles_regex, file_text)
        ]

        if len(roles) == 0:
            self.stdout.write("Роли не найдены")
            return None

        self.stdout.write(
            "Найдены роли:\n\t"
            + "\n\t".join(
                [f'{role["title"]}: {role["permissions"]}' for role in roles]
            )
        )

        return roles

    def choose_server(self) -> int | None:
        """
        Выбор сервера или создание нового
        """
        servers = {
            serv[0]: f"{serv[0]}) {serv[1]} - {serv[2]}"
            for serv in Server.objects.order_by("id").values_list(
                "id", "title", "description"
            )
        }

        if len(servers) == 0:
            return None

        self.stdout.write("\n".join(servers.values()))

        while True:
            self.stdout.write(
                "Выберите сервер в который будут добавлены пользователи "
                "из файла конфигурации"
            )

            server_id = question_with_confirmation(
                'Номер сервера или "-" если хотите создать новый сервер'
            )

            if server_id == "-":
                return None

            if not server_id.isdigit():
                continue

            server_id = int(server_id)

            if server_id not in servers:
                continue

            self.stdout.write(f"Выбран сервер - {servers[server_id]}")

            return server_id

    def create_server(self) -> int:
        """
        Создание сервера с указанным именем
        """
        title: str = question_with_confirmation("Введите имя нового сервера")
        server: Server = Server.objects.create(title=title)

        self.stdout.write(
            f"Создан новый сервер - {server.id} - {server.title}"
        )

        return server.id

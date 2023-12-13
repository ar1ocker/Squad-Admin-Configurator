import argparse

from django.core.management.base import BaseCommand, CommandParser
from django.db import IntegrityError, transaction
from server_rotations.layers_parser import LayerSpec
from server_rotations.models import Layer, LayerPackLayer, LayersPack


class Command(BaseCommand):
    help = "Добавление паков карт из файлов"

    def yes_or_no(self, text, style=None):
        if not style:
            style = self.style.SUCCESS

        while True:
            self.stdout.write(text + " (y/n):", style)
            answer = input().strip()
            if answer in ["y", "n"]:
                return True if answer == "y" else False

    def question_with_confirmation(self, text, style=None):
        if not style:
            style = self.style.SUCCESS

        while True:
            self.stdout.write(text + " (y/n):", style)
            answer = input().strip()
            if answer and self.yes_or_no(f'"{answer}", всё верно?', style):
                return answer

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("file", type=argparse.FileType("r"))
        parser.add_argument("--ignore_errors", action="store_true")

    def handle(self, *args, **options):
        file_text = options["file"].read()
        nodes = LayerSpec.parse(file_text)
        errors = LayerSpec.check_errors(nodes)

        if errors and not options["ignore_errors"]:
            self.stdout.write("\n".join(errors))
            if not self.yes_or_no("Игнорируем ошибки?"):
                exit()

        layers_nodes = filter(lambda n: n.kind == LayerSpec.LAYER.name, nodes)
        layers = [layer_node.value for layer_node in layers_nodes]

        if layers:
            self.stdout.write(
                f"Найдены карты ({len(layers)}):", self.style.SUCCESS
            )
            self.stdout.write("\n".join(layers))
        else:
            self.stdout.write("Карт не найдено", self.style.ERROR)
            exit(1)

        with transaction.atomic():
            pack = self.create_pack()
            layers_objs = self.create_layers(layers)

            layer_pack_layers = [
                LayerPackLayer(pack=pack, layer=layer, queue_number=key)
                for key, layer in enumerate(layers_objs)
            ]

            LayerPackLayer.objects.bulk_create(layer_pack_layers)

        self.stdout.write("Карты добавлены", self.style.SUCCESS)

    def create_pack(self):
        while True:
            pack_name = self.question_with_confirmation(
                "Введите имя нового пака с картами"
            )

            try:
                return LayersPack.objects.create(title=pack_name)
            except IntegrityError:
                self.stdout.write("Пак с таким именем уже существует")

    def create_layers(self, layers):
        ret_objs = []
        for layer_name in layers:
            layer, _ = Layer.objects.get_or_create(name=layer_name)
            ret_objs.append(layer)

        return ret_objs

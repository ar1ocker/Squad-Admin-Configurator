import copy

from rest_framework.permissions import DjangoModelPermissions


class AdvancedDjangoModelPermissions(DjangoModelPermissions):
    # TODO: Удалить когда примут новую версию с этим коммитом
    # https://github.com/encode/django-rest-framework/commit/0618fa88e1a8c2cf8a2aab29ef6de66b49e5f7ed
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]

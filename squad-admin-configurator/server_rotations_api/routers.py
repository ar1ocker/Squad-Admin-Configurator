from rest_framework.routers import SimpleRouter

from .views import RotationDistributionViewSet

router = SimpleRouter(use_regex_path=False)

router.register("", RotationDistributionViewSet, basename="rotation_distribution")

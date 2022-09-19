from rest_framework import routers
from .auth import Role_viewset, Userprofile_viewset

router = routers.DefaultRouter()
router.register('role', Role_viewset)
router.register('user', Userprofile_viewset)

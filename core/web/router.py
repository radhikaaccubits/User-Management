from rest_framework import routers
from .views import role_viewset,userprofile_viewset

router=routers.DefaultRouter()
router.register('role',role_viewset)
router.register('user',userprofile_viewset)
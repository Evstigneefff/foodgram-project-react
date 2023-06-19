from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers

from users.views import CustomUserViewSet

app_name = 'users'

router = routers.DefaultRouter()
router.register(r'api/users', CustomUserViewSet, basename='users')

auth_urls = [
    path(r'api/auth/token/login/', TokenCreateView.as_view()),
    path(r'api/auth/token/logout/', TokenDestroyView.as_view()),
    path(r'api/auth/', include('djoser.urls'))
]

urlpatterns = router.urls
urlpatterns += auth_urls

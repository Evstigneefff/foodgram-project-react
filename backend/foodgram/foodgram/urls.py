from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('api/recipes/', include('api.urls')),
    path('api/', include('rest_framework.urls', namespace='rest_framework')),
]

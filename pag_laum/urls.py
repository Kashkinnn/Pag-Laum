from django.contrib import admin
from django.urls import include, path

from apps.login.views import logout_session_view

urlpatterns = [
    path('admin/', admin.site.urls),

    
    path('', include('apps.login.urls')),
    path('register/', include('apps.register.urls')),
    path('home/', include('apps.home.urls')),
    path('logout/', logout_session_view, name='logout'),
]

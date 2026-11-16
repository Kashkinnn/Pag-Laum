from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    
    path('', include('apps.login.urls')),
    path('register/', include('apps.register.urls')),
    path('home/', include('apps.home.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
]

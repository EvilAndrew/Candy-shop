from django.contrib import admin
from django.urls import path, include
from candy_shop import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('candy_shop.urls', namespace='candy_shop'))
]

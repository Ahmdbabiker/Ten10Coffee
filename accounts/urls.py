from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('signin/' , signin , name="signin"),
    path('signup/' , signup , name="signup"),
    path('signout/' , signout , name="signout"),
    path('add_address/' , add_address , name="add_address")
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from core.views import ProfileUpdateView

urlpatterns = [
    path('signin/' , signin , name="signin"),
    path('signup/' , signup , name="signup"),
    path('signout/' , signout , name="signout"),
    path('add_address/' , ProfileUpdateView.as_view() , name="add_address")
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

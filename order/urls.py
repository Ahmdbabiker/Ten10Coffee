from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('process_order/', process_order, name="process_order"),
    path('apply-coupon/', apply_coupon, name='apply_coupon'),
    path('apply-stamp/', apply_stamp, name='apply_stamp'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

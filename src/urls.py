from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from core.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('' , home , name='home'),
    path('meal_detials/<slug:slug_name>/' ,meal_details , name="meal_detail"),
    path('accounts/' , include('accounts.urls')),
    path('cart/' , include('cart.urls')),
    path('order/' , include('order.urls')),
    path('admin_dashboard/' , admindash , name="admindash"),
    path('admin_dashboard/admin_orders/<int:order_type>/' , admin_orders , name="admin_orders"),
    path('admin_dashboard/get-new-orders/', get_new_orders, name='get_new_orders'),
    path('admin_dashboard/order_detail/<int:order_id>/' , order_detail , name="order_detail"),
    path('admin_dashboard/general_rate/<int:rate_int>/' , general_rating , name="general_rating"),
    path('admin_dashboard/manage_products/' , product_admin , name="product_admin"),
    path('admin_dashboard/manage_products/edit/<int:pk>/' , ProductUpdateView.as_view() , name="edit_product"),
    path('admin_dashboard/manage_products/add_product/' , ProductAdd.as_view() , name="add_product"),
    path('myorders/<int:user_id>' , user_orders , name="myorders"),
    path('orderDone' , order_done , name="order_done"),
    path('edit_shipping_phone_number/' , ProfileUpdateView.as_view() , name="edit_shiping_phone"),
    path('dicount/not_found/' , dicounts , name="discount"),
    path('contact/' , contact , name="contact" ),
    path('admin_dashboard/add_coupon/' , add_coupon , name="add_coupon"),
    path('admin_dashboard/all_users/' , all_users , name="all_users"),
    #path('admin_dashboard/general_rate/<int:rate_int>/<int:product_id>/', general_rating, name="general_rating_with_product"),

#AhmdBabikerMahi

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


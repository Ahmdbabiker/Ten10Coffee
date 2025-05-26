from django.db import models
from django.contrib.auth.models import User
from core.models import *
from django.utils.timezone import now

# Create your models here.


# Create Order Model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_address = models.TextField(max_length=15000)
    shipping_city = models.CharField(max_length=255, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    shipping_amount = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    phone_number = models.IntegerField(null=True , blank=True)
    unknown_user = models.CharField(null=True , max_length=50 , blank=True)
    pickup = models.BooleanField(default=False , null=True)
    is_new = models.BooleanField(default=True , null=True)  
    notes = models.TextField(null=True , blank=True)
    extra_data = models.JSONField(blank=True, null=True)
	
    def __str__(self):
        return f'Order - {str(self.id)}'       
    def order_items(self):
    	return  OrderItem.objects.filter(order__id = self.id)


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage or fixed discount
    active = models.BooleanField(default=True)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        return self.active and (not self.expiration_date or self.expiration_date > now())




# Create Order Items Model
class OrderItem(models.Model):
    # Foreign Keys
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    extras = models.ManyToManyField(Extra, blank=True, related_name='order_items')

 
   
    def __str__(self):
        return f'Order Item - {str(self.id)}'



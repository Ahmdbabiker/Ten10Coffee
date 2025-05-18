from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models import Avg

class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone_number = models.IntegerField(null=True)
    home_location = models.URLField(null=True , blank=True)

@receiver(post_save , sender = User)
def create_profile(sender , instance , created , **kwargs):
    if created : 
        save_profile = Profile(user = instance)
        save_profile.save()

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Extra(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
    
    def extras(self):
        return Product.objects.filter(extras__id = self.id)


class Product(models.Model):
    name = models.CharField(max_length=52)
    slug = models.SlugField()
    desc = models.CharField(max_length=255 , null=True , blank=True)
    price = models.DecimalField(max_digits=7 , decimal_places=2)
    no_of_buying = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images' , null=True ,blank=True, default='static/images/ten.png')
    tag = models.ForeignKey(Tag , on_delete=models.CASCADE)
    extras = models.ManyToManyField(Extra, blank=True, related_name='products')

    def save(self, *args, **kwargs):
        if not self.slug:  # Only set slug if it's empty
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def product_rate(self):
        return Rating.objects.filter(product__id = self.id)

    def average_rating(self):
        return self.rating_set.aggregate(Avg('rate'))['rate__avg'] or 0
class Rating(models.Model):
    CHOISES = (
        (1,'سيء جداً'),
        (2,'سيء'),
        (3,'جيد'),
        (4,'جيد جداً'),
        (5,'ممتاز'),
    )
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    user_rated = models.ForeignKey(User , on_delete=models.CASCADE)
    date_rated = models.DateField(auto_now_add=True)
    comment = models.CharField(max_length=255 , null=True)
    rate =  models.PositiveSmallIntegerField(choices=CHOISES)

    def __str__(self):
        return f"{self.user_rated.username} Rated {self.product}"


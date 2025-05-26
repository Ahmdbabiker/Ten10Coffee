from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

CITY_CHOICES = [
    ('her', 'الهير (التوصيل مجاناً)'),
    ('aen', 'العين (100 د.إ رسوم التوصيل)'),
    ('sh', 'الشويب (30 د.إ رسوم التوصيل)'),
    ('fq', 'الفقع (30 د.إ رسوم التوصيل )'),
    ('nah', 'ناهل (40 د.إ رسوم التوصيل )'),
    ('sw', 'سويحان (50 د.إ رسوم التوصيل)'),
    ('other', 'اخرى (تحدد من قبل المحل)'),
]

class City(models.Model):
    name = models.CharField('اسم المدينة',max_length=255, blank=True, null=True)
    shipping_price = models.DecimalField('رسوم التوصيل',max_digits=7, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10, blank=True, null=True,
                                    validators=[RegexValidator(r'^\d{1,10}$'),
                                                MinLengthValidator(10)])
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


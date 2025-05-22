from django.shortcuts import render , redirect ,  get_object_or_404
from .models import *
from django.contrib import messages
from django.db.models import Avg
from order.models import *
from django.db.models import Sum
from django.utils import timezone
import time
from datetime import timedelta
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.http import StreamingHttpResponse
import json
from urllib.parse import urlencode
from order.models import *



# Create your views here.

def home(request):
    all_products = Product.objects.all()
    best_seller = Product.objects.order_by('-no_of_buying')[:3]
    data = {"all_products":all_products ,
    "best":best_seller}
    return render(request , "index.html" , data)

def contact(request):
    pass
    return render(request , "contact.html")


def meal_details(request , slug_name):
    get_meal = Product.objects.get(slug = slug_name)
    similar = Product.objects.filter(tag = get_meal.tag ).exclude(slug = slug_name)
    all_products = Product.objects.all()
    for product in all_products:
        ratings = product.product_rate()
        rates = [rating.rate for rating in ratings]

    if request.POST:
        rate = request.POST.get("rate")
        comment = request.POST.get("comment")
        user = request.user
        if user.is_authenticated:
            if Rating.objects.filter(user_rated = user , product__slug = slug_name).exists():
                messages.error(request , "لقد قمت بالتعليق بالفعل على هذا العنصر")
                return redirect("meal_detail" , slug_name)
            else:
                Rating.objects.create(
                    product = get_meal , user_rated = user ,
                    comment = comment , rate = rate)
                messages.success(request , "شكراً لك على تقييمك ")
        else:
            messages.error(request , "قم بإنشاء حساب لترك تقييم ")
    meal_Rate = Rating.objects.filter(product__slug = get_meal.slug)
    meal_avg = meal_Rate.aggregate(Avg('rate'))
    avg_extracted = meal_avg['rate__avg']
    count_rating = meal_Rate.count()


    data = {"meal_details":get_meal ,
    "similar":similar , "rate":meal_Rate ,
    "avg_rate" : avg_extracted ,"rates":rates, "count_rating":count_rating}
    return render(request , "meal_details.html" , data)

def admindash(request):
    if request.user.is_superuser or request.user.is_staff:
        products = Product.objects.all().count()
        rate = Rating.objects.all()
        rate_Avg = rate.aggregate(Avg('rate'))
        rate_extrcated = rate_Avg['rate__avg']
        orders = Order.objects.all().count()
        users = User.objects.all().exclude(is_superuser = True).count()
        best_seller = Product.objects.order_by("-no_of_buying").first()
        total = Order.objects.aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0
        total_formatted = f"{total:.2f}"
        data = {"products":products , "rate":rate_extrcated ,
        "orders":orders , "users":users , "best_seller":best_seller ,
        "total":total_formatted}

    else:
        messages.error(request, "دخول خاطئ")
        return redirect("home")
    return render(request , "admin_page.html" , data)


def admin_orders(request , order_type):
    if request.user.is_superuser or request.user.is_staff :
        today = timezone.now().date()
        order_no = order_type
        orders = None
        order_items = None
        unregistered_user = request.session.get("unknown_user")
        if order_type == 1:
            orders = Order.objects.all()
            paginator = Paginator(orders , 10)
            page_number = request.GET.get('page')
            orders = paginator.get_page(page_number)

            for order in orders :
                order_items = order.orderitem_set.all()

        elif order_type == 2 :
           print("live orders")
        elif order_type ==3 :
            orders = Order.objects.filter(date_ordered__date = today)
            paginator = Paginator(orders , 10)
            page_number = request.GET.get('page')
            orders = paginator.get_page(page_number)
            print(orders)
        elif order_type == 4 :
            orders = Order.objects.filter(user__is_superuser = True)
        elif order_type == 5 :
            orders = Order.objects.filter(user__is_superuser = False)
        elif order_type == 6 :
            last_7 = today - timedelta(days=7)
            orders = Order.objects.filter(date_ordered__date__gte = last_7)
            paginator = Paginator(orders , 10)
            page_number = request.GET.get('page')
            orders = paginator.get_page(page_number)
            print(orders)
        elif  order_type == 7 :
            last_30 = today - timedelta(days=30)
            orders = Order.objects.filter(date_ordered__date__gte = last_30)
            paginator = Paginator(orders , 10)
            page_number = request.GET.get('page')
            orders = paginator.get_page(page_number)
            print(orders)
        data = {"orders":orders ,
        "order_no":order_no , "order_items":order_items , "unregistered_user":unregistered_user}
        return render(request , "admin_orders.html" , data )
    else:
        messages.success(request , "دخول خاطىء")
        return redirect("home")


def general_rating(request, rate_int):
    rate = Rating.objects.all()
    rate_avg = rate.aggregate(Avg('rate'))['rate__avg']  # Overall average rating
    rate_score = None
    products = Product.objects.all()

    # Filter ratings based on the selected rating value (rate_int)
    if rate_int == 0:
        rate_score = rate
    elif 1 <= rate_int <= 5:
        rate_score = rate.filter(rate=rate_int)

    selected_product = None
    product_ratings = rate_score  # Default to filtered ratings by rate_int

    if request.method == "POST":
        productts = request.POST.get("productts")  # Get selected product ID
        if productts:
            selected_product = get_object_or_404(Product, id=productts)
            product_ratings = rate_score.filter(product=selected_product)  # Filter ratings for the selected product
            rate_avg = product_ratings.aggregate(Avg('rate'))['rate__avg']  # Average rating for the selected product

    data = {
        "rate_extrcated": rate_avg,
        "rate_score": product_ratings,
        "products": products,
        "selected_product": selected_product,
    }
    return render(request, "gen_rate.html", data)


def get_new_orders(request):
    if request.method == "GET":
        new_orders = Order.objects.filter(is_new=True)
        orders_data = [{'id': order.id} for order in new_orders]
        return JsonResponse({'orders': orders_data})




def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order).prefetch_related('extras')

    total_amount = 0  # Initialize total_amount

    enriched_order_items = []
    for item in order_items:
        item_total = item.price * item.quantity  # Base price for the item
        item_data = {
            "product": item.product,
            "quantity": item.quantity,
            "price": item.price,
            "extras": []
        }
        product_extras = order.extra_data.get(str(item.product.id), []) if order.extra_data else []
        for extra in item.extras.all():
            apply_to = None
            specific_quantity = None

            for json_extra in product_extras:
                if json_extra['extra_id'] == str(extra.id):  # Match on extra_id
                    apply_to = json_extra['apply_to']
                    specific_quantity = json_extra.get('specific_quantity')
                    break

            # Calculate the extra amount based on whether it's applied to all or specific quantities
            if apply_to == "all":
                extra_total = extra.price * item.quantity
            elif apply_to == "specific" and specific_quantity is not None:
                extra_total = extra.price * specific_quantity
            else:
                extra_total = extra.price

            item_total += extra_total  # Add the extra amount to the item total

            item_data["extras"].append({
                "name": extra.name,
                "price": extra.price,
                "apply_to": apply_to,
                "specific_quantity": specific_quantity
            })

        total_amount += item_total  # Add the item total to the overall total

        enriched_order_items.append(item_data)

    return render(request, "order_detail.html", {
        "order_item": enriched_order_items,
        "order": order,
        "total_amount": total_amount
    })











def product_admin(request):
    all_products = Product.objects.all()
    if request.method == 'POST':
        product_id = request.POST.get("product")
        get_product = Product.objects.get(id = product_id)
        get_product.delete()
        return redirect("product_admin")
    data = {"all_products":all_products}
    return render(request , "manage_product.html" ,data)

def edit_product(request , product_id):
    get_product = Product.objects.get(id = product_id)
    if request.method == "POST":
        name = request.POST.get("name")
        desc = request.POST.get("desc")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        get_product.name = name
        get_product.desc = desc
        get_product.price = price

        if image:
            get_product.image = image

        get_product.save()

        messages.success(request , "تم التعديل")
        return redirect("product_admin")


    data = {"get_product":get_product}
    return render(request , "edit_product.html" , data)

def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        desc = request.POST.get("desc")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        tag = request.POST.get("tag")
        slug = slugify(name)

        tag_selected = None

        if tag == '1' :
            tag_selected = Tag.objects.get(id = 1 )
        elif tag == '2' :
            tag_selected = Tag.objects.get(id = 2 )
        elif tag == '3' :
            tag_selected = Tag.objects.get(id = 3 )


        add_new_product = Product.objects.create(name = name , slug =slug, desc = desc ,
        price = price , image = image ,tag = tag_selected)
        add_new_product.save()
        messages.success(request , "تمت الإضافة")
        return redirect("product_admin")

    return render(request , "add_product.html" )

def user_orders(request , user_id):
    current_user = request.user.id
    get_user = OrderItem.objects.filter(user__id = current_user)
    data  = {"user_orders":get_user}
    return render(request, "my_orders.html" , data)

def order_done(request):
    get_session = request.session.get("order_no")
    if request.user.is_authenticated:
        current_user = request.user.id
        profile = Profile.objects.get(user__id = current_user)
        base_url = "https://wa.me/971504779748"
        message = f"Order ID: {get_session}\nLocation: {profile.home_location}"
        query_params = urlencode({'text': message})
        whatsapp_link = f"{base_url}?{query_params}"
    else:
        base_url = "https://wa.me/971563179971"
        message = f"Order ID: {get_session}"
        query_params = urlencode({'text': message})
        whatsapp_link = f"{base_url}?{query_params}"

    data = {"order_id":get_session ,"whatsapp_link":whatsapp_link }
    return render(request , "order_done.html" , data)

def edit_shiping_phone(request , user_id):
    current_user = request.user.id
    grap_user = Profile.objects.get(user__id = current_user)
    if request.method == "POST":
        phoneno = request.POST.get("phoneno")
        address = request.POST.get("address")
        address_url = request.POST.get("address_url")

        grap_user.phone_number = phoneno
        grap_user.address = address
        grap_user.home_location = address_url

        grap_user.save()
        messages.success(request , "تم تعديل البيانات")
        return redirect("home")
    data = {"grap_user":grap_user}
    return render(request , 'edit_ship_details.html' , data)

def dicounts(request):
    pass
    return render(request , "discounts.html")


def add_coupon(request):
    if request.method == "POST":
       coupon_code = request.POST.get("coupon_code")
       discount = request.POST.get("coupon_discount")
       date_end= request.POST.get("date_end")
       active = request.POST.get("acti")
       if active == '1':
           active = True
       elif active == '2':
           active = False
       add_coupon = Coupon.objects.create(code=coupon_code , discount = discount , active=active , expiration_date = date_end)

       messages.success(request ,"تم إضافة الكوبون")
       return redirect("admindash")
    all_coupons = Coupon.objects.all()
    data = {"coupons":all_coupons}

    return render(request , 'coupons.html' , data)



def all_users(request):
    if request.user.is_superuser:
        users = Profile.objects.all()
        us = User.objects.all()
        user_order_counts = {}  # Create a dictionary to store order counts

        for user in us:
            user_order_counts[user.username] = Order.objects.filter(user=user).count()
        data = {'user_order_counts': user_order_counts , 'users':users}
    else:
        return redirect("home")
    return render(request , 'users.html' , data)



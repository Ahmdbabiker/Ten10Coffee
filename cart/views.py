from django.shortcuts import render , redirect , get_object_or_404
from .cart import Cart
from core.models import Product , Profile
from django.http import JsonResponse
from datetime import datetime
from decimal import Decimal
from django.contrib import messages
# Create your views here.



def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    total = cart.total()
    data = {"cart_products":cart_products , "quantities":quantities , "total":total}

    return render(request , 'cart_item.html' , data)



def cart_add(request):
    cart = Cart(request)
    #test for post
    if request.POST.get('action') == 'post':

        #get stuff
        product_id = int (request.POST.get('product_id'))
        product_qty = int (request.POST.get('product_qty'))
        #lookup product in DB
        product = get_object_or_404(Product , id=product_id)
        #save to session
        cart.add(product=product , quantity =product_qty )

        #get cart  quantity
        cart_quantity = cart.__len__()


        response = JsonResponse({'quantity ' : cart_quantity})
        return response


        #return response

        #response = JsonResponse({'product name ' : product.name})




def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':

        #get stuff
        product_id = int (request.POST.get('product_id'))

        cart.delete(product = product_id )

        response = JsonResponse({'product':product_id})
        return response

def cart_update(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        # Get product ID and new quantity
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # Update cart with new quantity
        cart.update(product=product_id, quantity=product_qty)

        return JsonResponse({
            'success': True,
            'qty': product_qty,
            'product_id': product_id,
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def customer_data(request):

    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    cart_len = len(cart)

    if cart_len > 0 :

        if request.user.is_superuser :
            total = cart.total()
        else:
            total = cart.total()

        today = datetime.today().date()

        if request.user.is_authenticated:
            user_data = Profile.objects.get(user__id = request.user.id)
            form_data = {
                'phoneno' : user_data.phone_number,
                'address' : user_data.address
            }
            request.session['user_data'] = form_data
            data = {"user_data":user_data ,"cart_products":cart_products,
            "quantities":quantities , "total":total , "today":today }
            return render(request , "customer_details.html" , data)

        if request.method == "POST":
            pickup = request.POST.get("pickup")
            if pickup:
                print("i got the pickup")
            else:
                print("sorry ")

            return redirect("billing")

        data = {"cart_products":cart_products,
        "quantities":quantities , "total":total , "today":today }
        return render(request , "customer_details.html" , data )
    else:
        messages.error(request , "قم بإضافة المنتجات إلى السلة ")
        return redirect("home")


def billing_details(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        if request.user.is_superuser :
            total = cart.total()
        else:
            total = cart.total()

        today = datetime.today().date()

        if request.user.is_authenticated:
            if request.method == "POST":
                pickup = request.POST.get("pickup")
                if pickup:
                    total = cart.total()

            get_session_data = request.session.get("user_data")
            get_session_data['pickup'] = pickup
            request.session['user_data'] = get_session_data
            request.session.modified = True
            print(get_session_data)

            data = {"session_data":get_session_data,"cart_products":cart_products , "quantities":quantities ,
            "total":total , "today":today , "pickup":pickup}
            return render(request , "billing.html" , data )
        else:
            if request.method == "POST":
                pickup = request.POST.get("pickup")
                if pickup:
                    total = cart.total()
            get_session_data = request.POST
            request.session["unknown_user"] = {
                'name': request.POST.get("name"),
                'phone_no':request.POST.get("phoneno"),
                'address':request.POST.get("address"),
            }
            unknown_session = request.session.get("unknown_user")
            unknown_session['pickup'] = pickup
            request.session['unknown_user'] = unknown_session
            request.session.modified = True

            data = {"session_data":unknown_session,"cart_products":cart_products , "quantities":quantities ,
            "total":total , "today":today , "pickup":pickup}
            return render(request , "billing.html" , data )
    else:
        return redirect("home")

    data = {
    "cart_products":cart_products , "quantities":quantities ,
    "total":total , "today":today}
    return render(request , "billing.html" ,data)



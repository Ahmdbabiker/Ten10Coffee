from django.shortcuts import render , redirect , get_object_or_404
from .cart import Cart
from core.models import Product , Profile
from django.http import JsonResponse
from datetime import datetime
from decimal import Decimal
from django.contrib import messages
from core.models import Extra
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
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    cart_len = len(cart)

    if cart_len > 0:
        total = cart.total()
        today = datetime.today().date()

        # Prepare products with extras and quantity ranges
        products_with_extras = []
        for product in cart_products:
            extras = product.extras.all()
            quantity = quantities.get(str(product.id), {}).get('quantity', 1)
            products_with_extras.append({
                'product': product,
                'extras': extras,
                'quantity': quantity,
                'quantity_range': range(1, quantity + 1)  # Range for selecting specific quantity
            })

        # For authenticated users, retrieve and pass user data
        if request.user.is_authenticated:
            user_data = Profile.objects.get(user__id=request.user.id)
            form_data = {
                'phoneno': user_data.phone_number,
                'address': user_data.address
            }
            request.session['user_data'] = form_data

            data = {
                "user_data": user_data,
                "cart_products": cart_products,
                "quantities": quantities,
                "total": total,
                "today": today,
                "products_with_extras": products_with_extras,
                "apply_extra_options": ["one", "all", "specific"],  # Added "specific" option
            }
            return render(request, "customer_details.html", data)

        # For non-authenticated users
        data = {
            "cart_products": cart_products,
            "quantities": quantities,
            "total": total,
            "today": today,
            "products_with_extras": products_with_extras,
            "apply_extra_options": ["one", "all", "specific"],  # Added "specific" option
        }
        return render(request, "customer_details.html", data)

    else:
        messages.error(request, "قم بإضافة المنتجات إلى السلة ")
        return redirect("home")








def billing_details(request):
    if request.method == "POST":
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        total = cart.total()

        selected_extras = {}

        # Collect selected extras with application scope
        for key, value in request.POST.items():
            if key.startswith('extra__'):
                _, product_id, extra_id = key.split('__')
                apply_to_key = f"apply_to__{product_id}__{extra_id}"
                apply_to = request.POST.get(apply_to_key, "all")

                if product_id not in selected_extras:
                    selected_extras[product_id] = []

                extra_data = {
                    "extra_id": extra_id,
                    "extra_name": value,
                    "apply_to": apply_to,
                }

                # Handle specific quantity (for apply_to "specific")
                if apply_to == "specific":
                    quantity_key = f"quantity__{product_id}__{extra_id}"
                    specific_quantity = request.POST.get(quantity_key)

                    if specific_quantity:
                        try:
                            specific_quantity = int(specific_quantity)  # Convert to int
                        except ValueError:
                            specific_quantity = 0  # Default to 0 if invalid
                    else:
                        specific_quantity = 0  # Default to 0 if not provided

                    extra_data["specific_quantity"] = specific_quantity

                selected_extras[product_id].append(extra_data)

        # Save selected extras to session
        request.session['user_extras'] = selected_extras

        # Calculate the total based on selected extras
        for product_id, extras in selected_extras.items():
            product_quantity = quantities.get(str(product_id), {}).get('quantity', 1)
            for extra in extras:
                extra_obj = Extra.objects.filter(id=extra['extra_id']).first()
                if extra_obj:
                    if extra['apply_to'] == "all":
                        total += extra_obj.price * product_quantity
                    elif extra['apply_to'] == "one":
                        total += extra_obj.price
                    elif extra['apply_to'] == "specific":
                        specific_quantity = extra.get("specific_quantity", 0)
                        total += extra_obj.price * specific_quantity

        # Process data for rendering
        if request.user.is_authenticated:
            user_data = request.session.get("user_data", {})
            data = {
                "session_data": user_data,
                "cart_products": cart_products,
                "quantities": quantities,
                "total": total,
            }
            return render(request, "billing.html", data)
        else:
            request.session["unknown_user"] = {
                "name": request.POST.get("name"),
                "phone_no": request.POST.get("phoneno"),
                "address": request.POST.get("address"),
            }
            data = {
                "cart_products": cart_products,
                "quantities": quantities,
                "total": total,
            }
            return render(request, "billing.html", data)

    return redirect("home")




















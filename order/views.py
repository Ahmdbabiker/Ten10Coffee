from django.shortcuts import render , redirect
from .models import *
from core.models import *
from cart.cart import Cart
from django.contrib import messages
from decimal import Decimal
from decimal import Decimal
from django.shortcuts import redirect
from django.contrib import messages




def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.total()

        # Log the initial totals for debugging
        print(f" (المبلغ قبل الخصم): {totals}")

        if len(cart) == 0:
            return redirect("home")

        dis = request.session.get('discount', 0)  # Default to 0 if no discount

        # If there is a discount, apply it to the totals
        if dis > 0:
            print(f"Applying discount: {dis}")
            totals -= Decimal(dis)
            totals = max(totals, 0)  # Ensure total is non-negative

        print(f" (المبلغ بعد الخصم): {totals}")

        amount_paid = totals

        # Clear the discount session value after using it
        request.session.pop('discount', None)

        if request.user.is_authenticated:
            user = request.user
            user_data = request.session.get("user_data")

            shipping_address = f"{user_data['address']} \n"
            phone = user_data.get('phoneno')
            pickk = user_data.get('pickup')
            picked = pickk == "yes"  # Boolean assignment directly

            # Create the order for authenticated user
            create_order = Order.objects.create(
                user=user,
                shipping_address=shipping_address,
                amount_paid=amount_paid,
                phone_number=phone,
                pickup=picked
            )

            order_id = create_order.id
            order_id_session = request.session["order_no"] = order_id

            # Add order items
            for product in cart_products():
                product_id = product.id
                price = product.price

                for key, value in quantities().items():
                    if int(key) == product.id:
                        quantity = value['quantity'] if isinstance(value, dict) else value
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=quantity, price=price)
                        create_order_item.save()

                        # Update product stock
                        product = Product.objects.get(id=product_id)
                        product.no_of_buying += quantity
                        product.save()

            # Clear the cart after the order is placed
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            # Success message and redirect
            messages.success(request, "تم تأكيد الطلب")
            return redirect('order_done')

        else:
            # Handle order for unknown user
            user_data = request.session.get("unknown_user")

            dict_user_data = user_data.get("address")
            phone = user_data.get("phone_no")
            unknown_user_name = user_data.get("name")
            pickk = user_data.get('pickup')
            picked = pickk == "yes"

            create_order = Order.objects.create(
                shipping_address=dict_user_data,
                amount_paid=amount_paid,
                phone_number=phone,
                unknown_user=unknown_user_name,
                pickup=picked
            )

            order_id = create_order.pk
            order_id_session = request.session["order_no"] = order_id

            # Add order items for unknown user
            for product in cart_products():
                product_id = product.id
                price = product.price

                for key, value in quantities().items():
                    if int(key) == product.id:
                        quantity = value['quantity'] if isinstance(value, dict) else value
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
                        create_order_item.save()

            # Clear the cart for unknown user
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            messages.success(request, "تم الطلب")
            return redirect('order_done')

    else:
        messages.success(request, "تم رفض الطلب")
        return redirect('home')






def apply_coupon(request):
    if request.method == 'POST':
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.total()

        coupon_code = request.POST.get('coupon_code', '').strip()  # Strip to remove extra spaces

        dic = None
        if not coupon_code:
            message = "يرجى إدخال رمز الخصم"
            return render(request, 'billing.html', {'message': message, 'total': totals})

        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            message = "رمز خصم غير صحيح"
            return render(request, 'billing.html', {'message': message, 'total': totals})

        if not coupon.is_valid():
            message = "رمز الخصم المدخل منتهي الصلاحية"
        else:
            discount = coupon.discount
            totals -= discount  # Apply discount
            totals = max(totals, 0)  # Ensure total does not go below zero

            # Store coupon details in session for later use (e.g., in checkout)
            request.session['discount'] = float(discount)
            request.session['coupon_code'] = coupon_code

            dic = request.session['discount'] = float(discount)

            message = "مبروك!تم الحصول على الخصم"

        return render(request, 'billing.html', {
            'message': message,
            'total': totals,
            'cart_products': cart_products,
            'quantities': quantities,
            'dic':dic,
        })
    else:
        return redirect("home")

    return redirect('billing')





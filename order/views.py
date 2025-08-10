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
    if request.method == "POST":
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.total()

        if len(cart) == 0:
            return redirect("home")

        # Handle any discounts if applicable
        discount = request.session.get('discount', 0)
        stamp_discount = request.session.get('stamp_discount', 0)
        if discount > 0:
            totals -= Decimal(discount)
            totals = max(totals, 0)
        if stamp_discount > 0:
            totals -= Decimal(stamp_discount)
            totals = max(totals, 0)
        # Get the extras data from the session
        get_extras = request.session.get("user_extras", {})

        # Apply extras based on user selection
        for product_id, extras in get_extras.items():
            quantity = quantities.get(str(product_id), {}).get('quantity', 1)

            # Iterate through the selected extras
            for extra in extras:
                extra_obj = Extra.objects.filter(id=extra["extra_id"]).first()
                if extra_obj:
                    # Apply the extra based on the user's choice
                    if extra["apply_to"] == "all":
                        totals += extra_obj.price * quantity  # Apply to all items in the quantity
                    elif extra["apply_to"] == "one":
                        totals += extra_obj.price  # Apply to one item only
                    elif extra["apply_to"] == "specific":
                        specific_quantity = extra.get("specific_quantity", 0)
                        totals += extra_obj.price * specific_quantity  # Apply to a specific number of items

        # Final total to be paid
        amount_paid = totals
        request.session.pop('discount', None)

        if request.user.is_authenticated:
            # Handle authenticated user order
            user = request.user
            user_data = request.session.get("user_data")
            shipping_address = f"{user_data['address']} \n"
            phone = user_data.get('phoneno')
            pickup = user_data.get('pickup') == "yes"
            notes = user_data.get('notes')
            shipping_city = user_data.get('city')
            shipping_price = Decimal(user_data.get('shipping_price'))
            if pickup:
                shipping_price = Decimal(0.00)
            amount_paid += shipping_price
            # Create the order
            create_order = Order.objects.create(
                user=user,
                shipping_address=shipping_address,
                amount_paid=amount_paid,
                shipping_amount=shipping_price,
                shipping_city=shipping_city,
                phone_number=phone,
                pickup=pickup,
                notes=notes,
                extra_data=get_extras
            )

            order_id = create_order.id
            request.session["order_no"] = order_id

            # Create order items
            for product in cart_products:
                product_id = product.id
                price = product.price
                quantity = quantities.get(str(product_id), {}).get('quantity', 1)

                create_order_item = OrderItem.objects.create(
                    order=create_order,
                    product_id=product_id,
                    user=user,
                    quantity=quantity,
                    price=price
                )

                # Add extras to the order item
                product_extras = get_extras.get(str(product_id), [])
                for extra in product_extras:
                    extra_obj = Extra.objects.filter(id=extra["extra_id"]).first()
                    if extra_obj:
                        if extra["apply_to"] == "specific":
                            specific_quantity = extra.get("specific_quantity", 0)
                            for _ in range(specific_quantity):
                                create_order_item.extras.add(extra_obj)
                        else:
                            create_order_item.extras.add(extra_obj)

                # Update product purchase count
                product.no_of_buying += quantity
                product.save()
            # Create Stamp every 10th order
            user_orders = user.order_set.count()
            expected_stamp_count = user_orders // 10
            current_stamp_count = user.stamp_set.count()
            if expected_stamp_count > current_stamp_count:
                Stamp.objects.create(user=user, order_count_at_creation=user_orders)

            # Clear session data
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            stamp_id = int(request.session.get('stamp_id'))
            try:
                stamp = Stamp.objects.get(id=stamp_id, user=user)
                stamp.used = True
                stamp.save()
            except Stamp.DoesNotExist:
                pass

            messages.success(request, "تم تأكيد الطلب")
            return redirect('order_done')

        else:
            # Handle guest user order
            user_data = request.session.get("unknown_user")
            shipping_address = user_data.get("address")
            phone = user_data.get("phone_no")
            unknown_user_name = user_data.get("name")
            notes = user_data.get("notes")
            pickup = user_data.get('pickup') == "yes"
            shipping_city = user_data.get('city')
            shipping_price = Decimal(user_data.get('shipping_price'))
            if pickup:
                shipping_price = Decimal(0.00)
            amount_paid += shipping_price
            # Create the order for the guest user
            create_order = Order.objects.create(
                shipping_address=shipping_address,
                amount_paid=amount_paid,
                shipping_amount=shipping_price,
                shipping_city=shipping_city,
                phone_number=phone,
                unknown_user=unknown_user_name,
                pickup=pickup,
                notes=notes,
                extra_data=get_extras
            )

            order_id = create_order.pk
            request.session["order_no"] = order_id

            # Create order items for guest user
            for product in cart_products:
                product_id = product.id
                price = product.price
                quantity = quantities.get(str(product_id), {}).get('quantity', 1)

                create_order_item = OrderItem.objects.create(
                    order=create_order,
                    product_id=product_id,
                    quantity=quantity,
                    price=price
                )

                # Add extras to the order item
                product_extras = get_extras.get(str(product_id), [])
                for extra in product_extras:
                    extra_obj = Extra.objects.filter(id=extra["extra_id"]).first()
                    if extra_obj:
                        if extra["apply_to"] == "specific":
                            specific_quantity = extra.get("specific_quantity", 0)
                            for _ in range(specific_quantity):
                                create_order_item.extras.add(extra_obj)
                        else:
                            create_order_item.extras.add(extra_obj)

            # Clear session data
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            messages.success(request, "تم الطلب")
            return redirect('order_done')

    messages.error(request, "تم رفض الطلب")
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


def apply_stamp(request):
    if request.method == 'POST':
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.total()
        user = request.user
        user_stamps = user.stamp_set.filter(used=False).order_by("-created_at")
        stamp = user_stamps.first()
        if stamp:
            product_prices = [product.price for product in cart_products]
            if product_prices:
                sorted_prices = sorted(product_prices, reverse=True)
                discount = next((p for p in sorted_prices if p <= 50), 0)
                totals -= discount  # Apply discount
                totals = max(totals, 0)  # Ensure total does not go below zero
                request.session["stamp_id"] = stamp.id
                request.session["stamp_discount"] = float(discount)
                message = f"مبروك! تم الحصول على خصم بقيمة {discount} درهما"
            else:
                message = "لا توجد منتجات في السلة لتطبيق الطابع."
        else:
            message = "لا يوجد لديك طوابع متاحة."

        return render(request, 'billing.html', {
            'message': message,
            'total': totals,
            'cart_products': cart_products,
            'quantities': quantities,
        })
    else:
        return redirect("home")

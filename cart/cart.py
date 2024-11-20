from core.models import Product
from decimal import Decimal

class Cart():
    def __init__(self,request):
        self.session = request.session


        #Get the current session key if its exists
        cart = self.session.get('session_key')


        #if the user is new ? create one
        if 'session_key' not in self.session:
            cart = self.session['session_key'] = {}


        #make sure cart is available on all pages of site
        self.cart = cart



    def add(self , product , quantity ):
        product_id = str(product.id)
        product_qty = str(quantity)

        if product_id in self.cart:
            pass
        else:
            #self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = {'quantity': int(product_qty)}


        self.session.modified = True



    def __len__(self):
        return len(self.cart)
    product= 0



    def get_prods(self):
        #get ids from the cart
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        return products



    def get_quants(self):
        quantities = self.cart
        return quantities



    def update(self, product, quantity):
        product_id = str(product)
        self.cart[product_id] = {'quantity': quantity}

        # Mark the session as modified to save changes
        self.session['cart'] = self.cart
        self.session.modified = True

        return self.cart


    def delete(self , product):
        product_id = str(product)

        #delete from dictionay/cart

        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True



    def total(self):
        #get product keys
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        quantities = self.cart

        total = 0

        for key, value in quantities.items():
            try:
                product = Product.objects.get(id=int(key))
                total = total + (product.price * value['quantity'])
            except :
                total = total + (product.price * value )


        return total

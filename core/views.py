from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from .models import Category,BlogPost,Product,Wishlist
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from .models import *
from .models import Product, Category
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import  login
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required

from .models import MyCart, Address
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .forms import CategoryForm, SignupForm
from django.shortcuts import render
from .models import Order
from decimal import Decimal
import razorpay
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json
from django.core.paginator import Paginator
import re
import uuid
from django.core.exceptions import PermissionDenied
from .models import Order

from django.views.decorators.csrf import csrf_protect

@login_required
def logout(request):
    auth_logout(request)
    return  redirect('loginaccount')


@login_required(login_url='loginaccount')  # update this to match your login URL name
def wishlistproduct(request):
    categories = Category.objects.all()
    wishlist_items = Wishlist.objects.filter(user=request.user)
    cart_items = MyCart.objects.filter(user=request.user)
    products = Product.objects.all()

    message = "Your wishlist is empty." if not wishlist_items else ""

    return render(request, 'wishlist-product.html', {
        'wishlist_items': wishlist_items,
        'message': message,
        'cart_items': cart_items,
        'products': products,
        'categories': categories,
    })
from django.http import JsonResponse
from datetime import datetime, timedelta


def check_delivery(request):

    pincode = request.GET.get('pincode')

    # FAST DELIVERY PINCODES
    fast_delivery = [
        "560001",
        "560037",
        "560066",
        "560100",
        "560102",
    ]

    # RURAL DELIVERY PINCODES
    rural_delivery = [
        "563130",
        "562125",
        "561203",
        "563101",
    ]

    # NO DELIVERY
    no_delivery = [
        "999999",
        "888888",
    ]

    today = datetime.today()

    # Fast delivery = 2 days
    if pincode in fast_delivery:

        delivery_date = today + timedelta(days=2)

        return JsonResponse({
            "status": "fast",
            "delivery_date": delivery_date.strftime("%A, %d %B")
        })

    # Rural delivery = 5 days
    elif pincode in rural_delivery:

        delivery_date = today + timedelta(days=5)

        return JsonResponse({
            "status": "rural",
            "delivery_date": delivery_date.strftime("%A, %d %B")
        })

    # No delivery
    elif pincode in no_delivery:

        return JsonResponse({
            "status": "unavailable"
        })

    else:

        return JsonResponse({
            "status": "unavailable"
        })


@login_required(login_url='loginaccount')
@require_POST
def clear_cart(request):
    MyCart.objects.filter(user=request.user).delete()
    return JsonResponse({"status": "success"})
    
@login_required(login_url='loginaccount')
def add_to_wishlist(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        return JsonResponse({"status": "added"})
    else:
        return JsonResponse({"status": "exists"})

@login_required(login_url='loginaccount')
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.GET.get('quantity', 1))

    # Add product to cart
    cart_item, created = MyCart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    # 🔥 Redirect directly to checkout page
    return redirect('checklist')     
@login_required
def clear_wishlist(request):
    Wishlist.objects.filter(user=request.user).delete()
    return redirect('wishlistproduct')


def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlistproduct')


def home(request):

    category_id = request.GET.get('category_id')
    selected_categories = request.GET.getlist('category')

    if category_id:
        products = Product.objects.filter(
            category_id=category_id,
            availability=True,
            product_type='bonsai'
        )
        selected_categories = [category_id]

    elif selected_categories:
        products = Product.objects.filter(
            category__id__in=selected_categories,
            availability=True,
            product_type='bonsai'
        )
    else:
        products = Product.objects.filter(
            availability=True,
            product_type='bonsai'
        )

    terrarium_products = Product.objects.filter(
        product_type='terrarium',
        availability=True
    )

    categories = Category.objects.all()

    cart_items = (
        MyCart.objects.filter(user=request.user)
        if request.user.is_authenticated else []
    )
    posts = BlogPost.objects.all().order_by('-date')


    return render(request, 'home.html', {
        'categories': categories,
        'products': products,
        'terrarium_products': terrarium_products,
        'cart_items': cart_items,
        'posts': posts,  # Correct variable name
        'page_title': 'Our Blog',  # Optional metadata
        'selected_categories': list(map(int, selected_categories)) if selected_categories else [],
        'show_login_alert': not request.user.is_authenticated,
    })
    
@login_required(login_url='loginaccount')
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Quantity default = 1
    qty = request.POST.get("quantity") or 1
    try:
        quantity = int(qty)
        if quantity < 1:
            quantity = 1
    except:
        quantity = 1

    # Add / update cart
    cart_item, created = MyCart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity = quantity
        cart_item.save()

    # Remove from wishlist
    Wishlist.objects.filter(user=request.user, product=product).delete()

    messages.success(request, "Item moved to cart successfully!")
    return redirect("cart")



def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(MyCart, product__id=product_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()
        return redirect('cart')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_images = ProductImage.objects.filter(product=product)
    categories = Category.objects.all()
    
    # Get related products (4 products from the same category, excluding current product)
    print(product.product_type)
    related_products = Product.objects.filter(
        product_type=product.product_type
    ).exclude(id=product.id)[:4]  # Random order for variety

    context = {
        'product': product,
        'product_images': product_images,
        'categories': categories,
        'related_products': related_products,
    }

    return render(request, 'product-template.html', context)

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart

    return redirect('cart')

def about(request):
    categories = Category.objects.all()
    if request.user.is_authenticated:
        cart_items = MyCart.objects.filter(user=request.user)
    else:
        cart_items = []  

    
    return render(request, 'about-us.html', {
        'cart_items': cart_items,
        'categories': categories
    })


@login_required
def orderhistory(request):
    categories = Category.objects.all()

    # Get orders for logged-in user
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    orders_with_items = []

    for order in user_orders:
        order_items_list = OrderItem.objects.filter(order=order)

        order_total = sum(item.quantity * item.price for item in order_items_list)

        orders_with_items.append({
            'order': order,
            'order_items': order_items_list,
            'total_amount': order_total
        })

    # Cart items
    cart_items = MyCart.objects.filter(user=request.user)

    context = {
        'orders_with_items': orders_with_items,
        'cart_items': cart_items,
        'categories': categories
    }

    return render(request, 'order-history.html', context)


def order_history_detail(request, order_id):
    # Fetch the specific order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    # Calculate the total for the order
    total_amount = sum(item.quantity * item.price for item in order_items)

    # ✅ Cart count logic
    session_cart = request.session.get('cart', {})
    cart_count = sum(session_cart.values())

    # ✅ Fetch current cart items of user
    cart_items = MyCart.objects.filter(user=request.user)

    # Add to context
    context = {
        'order': order,
        'order_items': order_items,
        'total_amount': total_amount,
        'cart_count': cart_count,
        'cart_items': cart_items  # ✅ Now available in order-history.html
    }

    return render(request, 'order-history.html', context)



def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    total_amount = 0
    order = Order.objects.create(user=request.user, total_amount=total_amount, status='Pending')
    print(f"Order created: {order.id}")  # Debugging line to confirm order creation

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue  # Skip if the product doesn't exist

        price = product.discounted_price if product.discounted_price else product.price
        order_item = OrderItem.objects.create(
            order=order, 
            product=product, 
            quantity=quantity, 
            price=price
        )
        print(f"Order item created: {order_item.id} for product {product.name}")  # Debug line
        total_amount += price * quantity
        product.stock_quantity -= quantity
        product.save()

    order.total_amount = total_amount
    order.save()

    print(f"Final order total amount: {order.total_amount}")  # Debug line
    
    return redirect(f'/orderhistory/{order.id}/')




def update_cart(request, product_id):
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = MyCart.objects.get_or_create(user=request.user, product=product)
        cart_item.quantity = quantity
        cart_item.save()

        # Return the updated total price as JSON
        return JsonResponse({
            'total_price': str(cart_item.total_price),
            'quantity': cart_item.quantity
        })
    return redirect('cart')




def remove_from_cart(request, pk):
    cart = MyCart.objects.get(id=pk)
    cart.delete()

    return redirect('cart')




@csrf_exempt
def payment_verify(request):
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Handle both GET (from handler redirect) and POST (from callback_url)
    if request.method in ['POST', 'GET']:
        params = request.POST if request.method == 'POST' else request.GET
        try:
            params_dict = {
                'razorpay_order_id': params.get('razorpay_order_id'),
                'razorpay_payment_id': params.get('razorpay_payment_id'),
                'razorpay_signature': params.get('razorpay_signature')
            }
            razorpay_client.utility.verify_payment_signature(params_dict)
            order = Order.objects.filter(payment_id=params_dict['razorpay_order_id']).first()
            order.payment_id = params_dict['razorpay_payment_id']
            order.payment_status = 'Paid'
            order.save()
            return redirect('order_complete')
        except:
            return redirect('order_failure')

@login_required
def order_complete(request):
    # You can fetch the latest order for the user or pass data from payment_verify
    MyCart.objects.filter(user=request.user).delete()
    categories = Category.objects.all()

    latest_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    if latest_order:
        context = {
            'address': latest_order.address,
            'total': latest_order.total_amount,
            'categories': categories,
        }
        return render(request, 'order-complete.html', context)
    return redirect('home')


@login_required
def order_failure(request):
    return render(request, 'order-failure.html')


@login_required
def checklist(request):
    # Initialize Razorpay client
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    categories = Category.objects.all()
    

    # Fetch cart items for the logged-in user
    cart_items = MyCart.objects.filter(user=request.user)

    # Calculate the subtotal for the cart items
    subtotal = 0
    for item in cart_items:
        subtotal += item.quantity * (item.product.discounted_price if item.product.discounted_price else item.product.price)

    # Set shipping charge (could be dynamic if needed)
    shipping_charge = 0
    total = subtotal + shipping_charge  # Total amount including shipping

    # Fetch existing address
    user_address = Address.objects.filter(user=request.user).first()

    # Fetch all user addresses
    user_addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        # Check if address and payment method are provided
        if 'address' in request.POST and 'payment_method' in request.POST:
            selected_address_id = request.POST.get('address')
            payment_method = request.POST.get('payment_method')
            
            try:
                # Fetch the selected address
                selected_address = Address.objects.get(id=selected_address_id)

                # Create an order
                order = Order.objects.create(
                    user=request.user,
                    address=selected_address,
                    total_amount=Decimal(total),
                    payment_method=payment_method,
                    status='Pending' if payment_method == 'online' else 'Placed'
                )

                # Add cart items to the order as OrderItem instances
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=Decimal(item.product.discounted_price or item.product.price)
                    )

                # Handle payment method logic
                if payment_method == 'online':


                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

                    # Create Razorpay order
                    razorpay_order = client.order.create({
                        'amount': int(total * 100),  # Amount in paise
                        'currency': 'INR',
                        'payment_capture': '1'
                    })


                    # Update order with Razorpay order ID
                    order.payment_id = razorpay_order['id']
                    order.save()

                    # Return JSON response for AJAX
                    return JsonResponse({
                        'razorpay_order_id': razorpay_order['id'],
                        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                        'razorpay_amount': int(total * 100),
                        'razorpay_currency': 'INR',
                        'order_id': order.id,
                        'callback_url': request.build_absolute_uri('/payment/verify/'),
                    })

                elif payment_method == 'cod':
                    # Order is already marked as 'Placed' for COD
                    messages.success(request, "Order placed successfully with Cash on Delivery.")
                    cart_items.delete()

                    context = {
                        'address': selected_address,
                        'cart_items': cart_items,
                        'total': total
                    }
                    return render(request, 'order-complete.html', context)

            except Address.DoesNotExist:
                return JsonResponse({'error': 'Selected address does not exist.'}, status=400)
            except Exception as e:
                return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
        else:
            return JsonResponse({'error': 'Please select an address and payment method.'}, status=400)

    return render(request, 'checkout-style1.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_charge': shipping_charge,
        'total': total,
        'user_address': user_address,  # Pass existing address to template
        'user_addresses': user_addresses,
        'categories': categories, # Pass all user addresses to template
    })

@login_required
def proaddress(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        postcode = request.POST.get('postcode')
        email = request.POST.get('email')

        import re

        if not first_name.isalpha():
            messages.error(request, "First name should contain only letters.")
            return redirect(request.POST.get('next'))

        if not re.match(r'^[0-9]{10}$', phone):
            messages.error(request, "Enter a valid 10 digit phone number.")
            return redirect(request.POST.get('next'))

        if not re.match(r'^[0-9]{6}$', postcode):
            messages.error(request, "Enter a valid 6 digit postcode.")
            return redirect(request.POST.get('next'))

        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            messages.error(request, "Enter a valid email address.")
            return redirect(request.POST.get('next'))

        Address.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            company_name=request.POST.get('company_name'),
            country=request.POST.get('country'),
            street_address=request.POST.get('street_address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            postcode=postcode,
            email=email,
            phone=phone,
        )

        messages.success(request, "Address added successfully 🌿")

        return redirect(request.POST.get('next'))

    # ✅ GET request
    addresses = Address.objects.filter(user=request.user)
    cart_items = MyCart.objects.filter(user=request.user)
    categories = Category.objects.all()

    return render(request, "pro-address.html", {
        "addresses": addresses,
        "cart_items": cart_items,
        "categories": categories,
    })

def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.company_name = request.POST.get('company_name')
        address.country = request.POST.get('country')
        address.street_address = request.POST.get('street_address')
        address.apartment_suite_unit = request.POST.get('apartment_suite_unit')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.postcode = request.POST.get('postcode')
        address.email = request.POST.get('email')
        address.phone = request.POST.get('phone')
        address.save()
        return redirect('proaddress')  # Change as needed

    return render(request, 'edit_address.html', {'address': address})


@login_required
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()

    messages.success(request, "Address deleted successfully 🌿")

    return redirect('proaddress')



def changepassword(request):
    categories = Category.objects.all()
    
    if request.user.is_authenticated:
        cart_items = MyCart.objects.filter(user=request.user)
    else:
        cart_items = [] 

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        
        if not request.user.check_password(old_password):
           
            form_error = "Old password is incorrect."
            return render(request, 'change-password.html', {
                'cart_items': cart_items,
                'form_error': form_error,
            })

        
        if new_password1 != new_password2:
            form_error = "New passwords do not match."
            return render(request, 'change-password.html', {
                'cart_items': cart_items,
                'form_error': form_error,
            })

       
        request.user.set_password(new_password1)
        request.user.save()

        update_session_auth_hash(request, request.user)

        messages.success(request, "Your password has been successfully updated!")

        return render(request, 'change-password.html', {
            'cart_items': cart_items,
            
        })

    return render(request, 'change-password.html', {
        'cart_items': cart_items,
        'categories': categories,
    })

def cartempty(request):
    categories = Category.objects.all()
    MyCart.objects.filter(user=request.user).delete()
    messages.success(request, "Your cart has been emptied successfully.")
    return render(request, 'cart-empty.html', {'categories': categories})

def ordercompleted(request):
    # Get all products
    products = Product.objects.all()

    # Calculate cart total
    cart_items = MyCart.objects.filter(user=request.user)

    subtotal = sum(
        item.quantity * (item.product.discounted_price or item.product.price)
        for item in cart_items
    )

    shipping_charge = 0
    total = subtotal + shipping_charge

    return render(request, 'order-complete.html', {
        'total': total,
        'products': products  
    })





def create_order(request):
    if request.method == "POST":
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

        amount = 50000  
        currency = 'INR'

        # Create the Razorpay order
        order = client.order.create({
            'amount': amount,
            'currency': currency,
            'payment_capture': 1
        })

        order_id = order['id']
        return JsonResponse({'order_id': order_id, 'amount': amount})

    return JsonResponse({'status': 'invalid request'}, status=400)


def blog(request):
    categories = Category.objects.all()
      
    cart_items = MyCart.objects.filter(user=request.user) if request.user.is_authenticated else []

    # Fetch all blog posts ordered by most recent date
    posts = BlogPost.objects.all().order_by('-date')

    # Additional context you might want to pass later (example: tags, categories, user name)
    context = {
        'cart_items': cart_items,
        'posts': posts,  # Correct variable name
        'page_title': 'Our Blog',  # Optional metadata
        'user_name': request.user.username if request.user.is_authenticated else 'Guest',
        'categories': categories
        
    }

    return render(request, 'blog-grid.html', context)

# FRONTEND PAGE for terrariums.
def terrarium_page(request, category_id=None):

    # Cart items for logged in user
    if request.user.is_authenticated:
        cart_items = MyCart.objects.filter(user=request.user)
    else:
        cart_items = []

    categories = Category.objects.all()

    # Category filter
    if category_id:
        products = Product.objects.filter(
            category_id=category_id,
            availability=True,
            product_type='terrarium'
        )

        selected_categories = [category_id]

    else:
        selected_categories = request.GET.getlist('category')

        if selected_categories:
            products = Product.objects.filter(
                category__id__in=selected_categories,
                availability=True,
                product_type='terrarium'
            )

        else:
            products = Product.objects.filter(
                availability=True,
                product_type='terrarium'
            )

    # Session cart
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    context = {
        'products': products,
        'categories': categories,
        'selected_categories': list(map(int, selected_categories)) if selected_categories else [],
        'product_count': products.count(),

        'total_count': Product.objects.filter(
            availability=True,
            product_type='terrarium'
        ).count(),

        'cart_count': cart_count,
        'cart_items': cart_items,
    }

    return render(request, 'terrarium.html', context)


def contact(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    cart_items = MyCart.objects.filter(user=request.user) if request.user.is_authenticated else []

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Save to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        messages.success(request, ' Thank you! Your message has been sent.')

    return render(request, 'contact-us.html', {
        'categories': categories,
        'products': products,
        'cart_items': cart_items,
    })

def base(request):
    return render(request, 'base.html')




def loginaccount(request):
    categories = Category.objects.all()

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)

            if user.check_password(password):
                login(request, user)

                # SweetAlert success message
                messages.success(request, "Login successful 🎉")

                return redirect("/")  # redirect to home page

            else:
                messages.error(request, "Invalid email or password.")

        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")

    return render(request, "login-account.html", {
        "categories": categories
    })


def shop_page(request):
    categories = Product.objects.values_list('category', flat=True).distinct()
    related_products_by_category = {}

    for category in categories:
        related_products_by_category[category] = Product.objects.filter(category=category)[:4]  # Limit to 4 per category

    return render(request, 'product-template.html', {
        'related_products_by_category': related_products_by_category
    })


@login_required(login_url='loginaccount')
def cart(request):
    categories = Category.objects.all()
    cart_items = MyCart.objects.filter(user=request.user).select_related('product')

    original_total = 0
    total_discount = 0
    final_total = 0

    for item in cart_items:
        price = item.product.price or 0
        discounted_price = item.product.discounted_price or price

        original_total += price * item.quantity
        total_discount += (price - discounted_price) * item.quantity
        final_total += discounted_price * item.quantity

    return render(request, 'cart-page.html', {
        'cart_items': cart_items,
        'original_total': original_total,
        'total_discount': total_discount,
        'final_total': final_total,
        'categories': categories,
    })

def increase_quantity(request, pk):
    cart = MyCart.objects.get(id=pk)
    cart.quantity += 1
    cart.save()
    return redirect('cart')

def decrease_quantity(request, pk):
    cart = MyCart.objects.get(id=pk)
    cart_quantity = cart.quantity
    if cart_quantity == 1:
        cart.delete()
        return redirect('cart')
    else:
        cart.quantity -= 1
        cart.save()
        return redirect('cart')


@login_required(login_url='loginaccount')
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = MyCart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        cart_item.quantity = 1
        cart_item.save()
        return JsonResponse({"status": "added"})
    else:
        return JsonResponse({"status": "exists"})


def Faq(request):
    categories = Category.objects.all()
    cart_items = MyCart.objects.filter(user=request.user)

    return render(request, 'faq.html', {
        'cart_items': cart_items,
        'categories': categories,
    })

@login_required
def privacypolicy(request):
    categories = Category.objects.all()
    
    cart_items = MyCart.objects.filter(user=request.user)
    return render(request, 'privacy-policy.html', {
        'cart_items': cart_items,
        'categories': categories,
    })



def paymentpolicy(request):
        return render(request, 'payment-policy.html')

def profile(request):    
    # Fetch all categories and products for the profile page
    categories = Category.objects.all()
    products = Product.objects.all()

    # Check if the user is logged in
    if request.user.is_authenticated:
        cart_items = MyCart.objects.filter(user=request.user)
    else:
        cart_items = []  # If the user is not logged in, no cart items

    # Render the profile page with all necessary data
    return render(request, 'profile.html', {
        'categories': categories,
        'products': products,
        'cart_items': cart_items,
    })

def blog_detail(request, slug):  # ✅ add slug parameter
    categories = Category.objects.all()
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'article-post.html', {'post': post, 'categories': categories})


@login_required
def termscondition(request):
    categories = Category.objects.all()

    cart_items = MyCart.objects.filter(user=request.user)

    
    return render(request, 'terms-condition.html', {
        'cart_items': cart_items,
         'categories': categories
    })

def returnpolicy(request):
    categories = Category.objects.all()
    cart_items = MyCart.objects.filter(user=request.user)

    return render(request, 'return-policy.html', {
        'cart_items': cart_items,
         'categories': categories
    })


def comingsoon(request):
    return render (request, 'coming-soon.html')

@csrf_protect
def createaccount(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            # All good — create user
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                )

                Profile.objects.create(
                    user=user,
                    phone=form.cleaned_data['phone']
                )

                login(request, user)  # auto-login after signup (optional but nice)
                messages.success(request, "Account created successfully! 🎉")
                return redirect('home')  # or 'dashboard' or wherever

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            # Form invalid — show errors (fields stay filled!)
            for field_name, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field_name}: {error}")

    else:
        # GET request — empty form
        form = SignupForm()

    return render(request, "create-account.html", {'form': form})

from django.shortcuts import render
from .models import Product, Category, MyCart

def collection(request, category_id=None):

    # Cart items for logged in user
    if request.user.is_authenticated:
        cart_items = MyCart.objects.filter(user=request.user)
    else:
        cart_items = []

    categories = Category.objects.all()

    # Category from URL
    if category_id:
        products = Product.objects.filter(
            category_id=category_id,
            availability=True,
            product_type='bonsai'
        )

        selected_categories = [category_id]

    else:
        selected_categories = request.GET.getlist('category')

        if selected_categories:
            products = Product.objects.filter(
                category__id__in=selected_categories,
                availability=True,
                product_type='bonsai'
            )

        else:
            products = Product.objects.filter(
                availability=True,
                product_type='bonsai'
            )

    # Session cart
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    context = {
        'products': products,
        'categories': categories,
        'selected_categories': list(map(int, selected_categories)) if selected_categories else [],
        'product_count': products.count(),

        'total_count': Product.objects.filter(
            availability=True,
            product_type='bonsai'
        ).count(),

        'cart_count': cart_count,
        'cart_items': cart_items,
    }

    return render(request, 'collection.html', context)



def categories(request, pk):
    category = get_object_or_404(Category, id=pk)
    
    # Only active products in this category
    products = Product.objects.filter(category=category, availability=True)
    
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'collection.html', context)










from .models import (
    Order, Product, MyCart,
    ContactMessage, Wishlist
)
from django.contrib.auth.models import User


from .models import (
    Product, BlogPost, Category, Order,
    MyCart, ContactMessage
)
from .forms import ProductForm, BlogForm, CategoryForm

def founder_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You are not allowed to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper




@staff_member_required(login_url='login')
def dashboard(request):

    # ========================
    # ORDER STATS
    # ========================

    total_orders = Order.objects.count()

    total_revenue = (
        Order.objects
        .filter(status="Completed")
        .aggregate(total=Sum("total_amount"))["total"] or 0
    )

    pending_orders = Order.objects.filter(status="Pending").count()
    completed_orders = Order.objects.filter(status="Completed").count()
    cancelled_orders = Order.objects.filter(status="Canceled").count()

    recent_orders = (
        Order.objects
        .select_related("user")
        .order_by("-created_at")[:5]
    )

    # ========================
    # PRODUCT STATS
    # ========================

    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock_quantity__lte=5).count()
    out_of_stock = Product.objects.filter(stock_quantity=0).count()

    # ========================
    # CUSTOMER STATS
    # ========================

    total_customers = User.objects.count()

    first_day_of_month = timezone.now().replace(day=1)
    new_customers_this_month = User.objects.filter(
        date_joined__gte=first_day_of_month
    ).count()

    # ========================
    # CART STATS
    # ========================

    active_carts = MyCart.objects.values("user").distinct().count()
    total_cart_items = MyCart.objects.count()

    # ========================
    # CONTACT STATS
    # ========================

    total_messages = ContactMessage.objects.count()

    today = timezone.now().date()
    messages_today = ContactMessage.objects.filter(
        submitted_at__date=today
    ).count()

    # ========================
    # MONTHLY REVENUE CHART
    # ========================

    monthly_sales = (
        Order.objects
        .filter(status="Completed")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )

    months = []
    sales = []

    for entry in monthly_sales:
        months.append(entry["month"].strftime("%b"))
        sales.append(float(entry["total"] or 0))

    context = {
        # Orders
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "recent_orders": recent_orders,

        # Products
        "total_products": total_products,
        "low_stock_products": low_stock_products,
        "out_of_stock": out_of_stock,

        # Customers
        "total_customers": total_customers,
        "new_customers_this_month": new_customers_this_month,

        # Cart
        "active_carts": active_carts,
        "total_cart_items": total_cart_items,

        # Contact
        "total_messages": total_messages,
        "messages_today": messages_today,

        # Chart
        "months": json.dumps(months),
        "sales": json.dumps(sales),
    }

    return render(request, "dashboard/index.html", context)

@login_required(login_url='login')
@founder_required

def product_list(request):

    search = request.GET.get('search', '')

    products = Product.objects.select_related('category').all().order_by('-id')

    # Search filter
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(category__name__icontains=search) |
            Q(price__icontains=search) |
            Q(stock_quantity__icontains=search)
        )

    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')

    products = paginator.get_page(page_number)

    context = {
        'products': products,
        'search': search,
    }

    return render(request, 'dashboard/products/list.html', context)

@login_required(login_url='login')
@founder_required
def product_create(request):

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('product_list')
        else:
            print(form.errors)  # DEBUG
    else:
        form = ProductForm()

    return render(request, 'dashboard/products/form.html', {
        'form': form
    })

@founder_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "dashboard/products/form.html", {
        "form": form,
        "title": "Edit Product"
    })


@founder_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(request, "dashboard/products/delete.html", {
        "product": product
    })


@founder_required
def blog_list(request):
    blogs = BlogPost.objects.all().order_by('-id')

    return render(request, "dashboard/blogs/list.html", {
        "blogs": blogs
    })

@founder_required
def blog_create(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("blog_list")
    else:
        form = BlogForm()

    return render(request, "dashboard/blogs/form.html", {
        "form": form,
        "title": "Add Blog"
    })

@founder_required
def blog_update(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect("blog_list")
    else:
        form = BlogForm(instance=blog)

    return render(request, "dashboard/blogs/form.html", {
        "form": form,
        "title": "Edit Blog"
    })

@founder_required
def blog_delete(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)

    if request.method == "POST":
        blog.delete()
        return redirect("blog_list")

    return render(request, "dashboard/blogs/delete.html", {
        "blog": blog
    })

@login_required(login_url='login')
@founder_required
def blog_list(request):
    blogs = BlogPost.objects.all().order_by('-date')
    return render(request, 'dashboard/blogs/list.html', {'blogs': blogs})


@login_required(login_url='login')
@founder_required
def blog_create(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogForm()

    return render(request, 'dashboard/blogs/form.html', {'form': form})


@login_required(login_url='login')
@founder_required
def blog_update(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogForm(instance=blog)

    return render(request, 'dashboard/blogs/form.html', {'form': form})


@login_required(login_url='login')
@founder_required
def blog_delete(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)

    if request.method == "POST":
        blog.delete()
        return redirect('blog_list')

    return render(request, 'dashboard/blogs/delete.html', {'blog': blog})



# ================= CATEGORY LIST =================
@founder_required
def category_list(request):
    categories = Category.objects.all().order_by('-id')

    return render(request, "dashboard/categories/list.html", {
        "categories": categories
    })

# ================= CATEGORY CREATE =================
@founder_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("category_list")
    else:
        form = CategoryForm()

    return render(request, "dashboard/categories/form.html", {
        "form": form,
        "title": "Add Category"
    })


# ================= CATEGORY UPDATE =================
@founder_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "dashboard/categories/form.html", {
        "form": form,
        "title": "Edit Category"
    })
# ================= CATEGORY DELETE =================
@founder_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        category.delete()
        return redirect("category_list")

    return render(request, "dashboard/categories/delete.html", {
        "category": category
    })


@founder_required
def order_list(request):
    """
    List all orders - only visible to founders/admins
    """
    orders = (
        Order.objects
        .select_related("user", "address")           # 1 query for user + address
        .prefetch_related("order_items__product")    # 1 query for all items + products
        .order_by("-created_at")                     # newest first
    )

    context = {
        "orders": orders,
        "page_title": "All Orders",
    }

    return render(request, "dashboard/orders/list.html", context)


@login_required
def order_detail(request, order_id):
    """
    View single order detail - founder sees all, regular user only their own
    """
    order = get_object_or_404(Order, id=order_id)

    # Security: regular logged-in users can only see THEIR own orders
    if not request.user.is_superuser and order.user != request.user:
        raise PermissionDenied("You do not have permission to view this order.")

    # Pre-calculate subtotal for each item (avoids doing math in template)
    for item in order.order_items.select_related("product"):
        item.subtotal = item.quantity * item.price  # float/decimal is fine

    context = {
        'order': order,
        'order_items': order.order_items.all(),  # already annotated with subtotalz
        'page_title': f"Order #{order.id}",
    }

    return render(request, 'dashboard/orders/order-detail.html', context)


@staff_member_required  # Only staff/founder can access
def customer_list(request):
    customers = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/customers/list.html', {
        'customers': customers,
    })
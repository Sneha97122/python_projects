from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from myapp.models import *
import os
from django.contrib.auth.decorators import *
from django.conf import settings
import razorpay

# Create your views here.


def index(request):
    category=Category.objects.all()
    product=Product.objects.all()
    feature_product=Product.objects.filter(is_featured=True)
    deal_product=Product.objects.filter(is_deal=True).first()
    return render(request,"index.html",{"category":category,"product":product,"feature_product":feature_product,"deal_product":deal_product})


def about(request):
    return render(request,"about.html")


def blog_single(request):
    return render(request,"blog_single.html")


def blog(request):
    return render(request,"blog.html")

@login_required(login_url='login')
def cart(request):
    if User is None:
        return redirect("login")
    else:
        carts = Cart.objects.filter(user=request.user)

        sum = 0
        for c in carts:
            sum += c.total_price()

        addresses = Address.objects.filter(user=request.user)  

    return render(request, "cart.html", {
        "carts": carts,
        "total": int(sum),
        "addresses": addresses,   
    })




def contact(request):
    return render(request,"contact.html")


def product_single(request):
    pid=request.GET.get('pid')
    product_detail=Product.objects.get(pk=pid)
    
    return render(request,"product_single.html",{"product_detail":product_detail})


def shop(request):
    productes=Product.objects.all()
    category=Category.objects.all()
    return render(request,"shop.html",{"productes":productes,"category":category})





def register_page(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = username,
            password = password,
        )
        return redirect("login")
    
    return render(request,"register_page.html")



def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            request.session['user_id'] = user.id
            request.session['user_name'] = user.username

            return redirect("index")

        else:
            return render(request, "login_page.html", {
                "error": "Invalid Username or Password"
            })

    return render(request, "login_page.html")


def logout(request):
    request.session.flush()
    return redirect('index')



def add_to_cart(request):
    pid=request.GET.get('pid')

    cart_item=Cart.objects.filter(
        user=request.user,
        product_id=pid
    ).first()

    if cart_item:
        cart_item.qty += 1
        cart_item.save()
    else:
        Cart.objects.create(
            user=request.user,
            product_id=pid,
            qty=1
        )
    
    return redirect('shop')


def increment(request):
    cid=request.GET.get('cid')
    cart=Cart.objects.get(pk=cid)

    cart.qty +=1
    cart.save()

    return redirect('cart')


def decrement(request):
    cid=request.GET.get('cid')
    cart=Cart.objects.get(pk=cid)

    if cart.qty > 1:
        cart.qty -= 1
        cart.save()
    else:
        cart.delete()
    return redirect('cart')


def remove_cart(request):
    cid=request.GET.get('cid')
    cart=Cart.objects.get(pk=cid)

    cart.delete()

    return redirect('cart')


def add_to_wishlist(request):
    pid=request.GET.get('pid')
    wishlist=Wishlist.objects.get_or_create(
        user=request.user,
        product_id=pid
    )
    return redirect('shop')

def wishlist(request):
    items=Wishlist.objects.filter(user=request.user)

    return render(request,"wishlist.html",{"items":items})



def add_address(request):
    if request.method =='POST':
        address=request.POST.get('address')
        city=request.POST.get('city')
        pincode=request.POST.get('pincode')

        Address.objects.create(
            user=request.user,address=address,city=city,pincode=pincode
        )
        return redirect('checkout')

    return render(request,"add_address.html")
    


# checkout functionality
def checkout(request):
    cart=Cart.objects.filter(user=request.user)
    address=Address.objects.filter(user=request.user)
    total=0
    for c in cart:
        total += c.total_price()

    return render(request,"checkout.html",{"cart":cart,"address":address,"total":total})

    

# def place_order(request):

#     if request.method == "POST":
#         address_id = request.POST.get("address_id")
#         payment_method = request.POST.get("payment_method")
#         coupon_code = request.POST.get("code")

#         cart = Cart.objects.filter(user=request.user)

#         # Calculate Cart Total
#         total = 0

#         for c in cart:
#             total += c.total_price()

#         # Apply Coupon
#         discount_amount=0
#         if coupon_code:
#             try:
#                 coupon = Coupon.objects.get(
#                     code=coupon_code.upper()
#                 )

#                 discount_amount = (
#                     total * coupon.discount
#                 ) / 100

#                 total = total - discount_amount

#             except Coupon.DoesNotExist:

#                 address = Address.objects.filter(
#                     user=request.user
#                 )

#                 return render(
#                     request,
#                     "checkout.html",
#                     {
#                         "cart": cart,
#                         "address": address,
#                         "total": total,
#                         "error": "Invalid Coupon Code",
#                         "discount ":discount_amount
#                     }
#                 )

#         # Selected Address
#         address = Address.objects.get(
#             id=address_id,
#             user=request.user
#         )

#         # Create Order
#         order = Order.objects.create(
#             user=request.user,
#             address=address,
#             total_amount=total,
#             payment_method=payment_method
#         )

#         # Create Order Items
#         for c in cart:

#             OrderItem.objects.create(
#                 order=order,
#                 product=c.product,
#                 qty=c.qty,
#                 price=c.product.price
#             )

#         # COD
#         if payment_method == "COD":

#             cart.delete()

#             return redirect("index")

#         # ONLINE PAYMENT
#         elif payment_method in [
#             "ONLINE",
#             "BANK",
#             "PAYPAL",
#             "RAZORPAY"
#         ]:

#             client = razorpay.Client(
#                 auth=(
#                     settings.RAZORPAY_KEY_ID,
#                     settings.RAZORPAY_KEY_SECRET
#                 )
#             )

#             razorpay_order = client.order.create({
#                 "amount": int(total * 100),
#                 "currency": "INR"
#             })

#             order.razorpay_order_id = razorpay_order["id"]
#             order.save()

#             address = Address.objects.filter(
#                 user=request.user
#             )

#             return render(
#                 request,
#                 "checkout.html",
#                 {
#                     "cart": cart,
#                     "address": address,
#                     "total": total,
#                     "order": order,
#                     "razorpay_order": razorpay_order,
#                     "razorpay_key": settings.RAZORPAY_KEY_ID
#                 }
#             )

#     return redirect("checkout")


from django.shortcuts import render, redirect
from django.conf import settings
from .models import Cart, Address, Order, OrderItem, Coupon
import razorpay

def place_order(request):
    if request.method == "POST":
        address_id = request.POST.get("address_id")
        payment_method = request.POST.get("payment_method")
        coupon_code = request.POST.get("code")  

        cart = Cart.objects.filter(user=request.user)
        addresses = Address.objects.filter(user=request.user)

        subtotal = sum(c.total_price() for c in cart)
        total = subtotal

        discount_amount = 0
        applied_coupon = None
        
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code.upper(), active=True)
                discount_amount = (subtotal * coupon.discount) / 100
                total = subtotal - discount_amount
                applied_coupon = coupon.code
            except Coupon.DoesNotExist:
                return render(request, "checkout.html", {
                    "cart": cart,
                    "address": addresses,
                    "total": subtotal,
                    "error": "Invalid or Expired Coupon Code",
                    "discount_amount": 0
                })

        try:
            selected_address = Address.objects.get(id=address_id, user=request.user)
        except (Address.DoesNotExist, ValueError):
            return render(request, "checkout.html", {
                "cart": cart,
                "address": addresses,
                "total": total,
                "error": "Please select a valid delivery address.",
                "discount_amount": discount_amount
            })

        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            total_amount=total,
            payment_method=payment_method,
            coupon_code=applied_coupon,
            payment_status="Pending",
            status="Pending"
        )

        for c in cart:
            OrderItem.objects.create(
                order=order,
                product=c.product,
                qty=c.qty,
                price=c.product.price  
            )

        if payment_method == "COD":
            cart.delete()  
            return redirect("index")

        elif payment_method in ["ONLINE", "BANK", "PAYPAL", "RAZORPAY"]:
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            razorpay_order = client.order.create({
                "amount": int(total * 100),  
                "currency": "INR"
            })

            order.razorpay_order_id = razorpay_order["id"]
            order.save()

            return render(request, "checkout.html", {
                "cart": cart,
                "address": addresses,
                "subtotal": subtotal,  
                "total": total,        
                "order": order,
                "razorpay_order": razorpay_order,
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "discount_amount": discount_amount
            })

    return redirect("checkout")



def payment_success(request):
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.payment_status = "Paid"
            order.status = "Accepted"
            order.save()
        except Order.DoesNotExist:
            pass
            
   
    Cart.objects.filter(user=request.user).delete()
    
    return redirect("index")



# filter the product by category

def filter_product(request):
    cid=request.GET.get('cid')
    
    if cid:
        productes=Product.objects.filter(category_id=cid)

    else:
        productes=Product.objects.all()
    category=Category.objects.all()

    return render(request,"shop.html",{"productes":productes,"category":category})

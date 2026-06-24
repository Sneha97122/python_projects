from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from myapp.models import *
import os
from django.contrib.auth.decorators import *
from django.conf import settings
import razorpay
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.


def index(request):
    category=Category.objects.all()
    product=Product.objects.all()
    feature_product=Product.objects.filter(is_featured=True)
    deal_product=Product.objects.filter(is_deal=True).first()
    return render(request,"index.html",{"category":category,"product":product,"feature_product":feature_product,"deal_product":deal_product})


def about(request):
    return render(request,"about.html",{"login":True})




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


def product_single(request):
    pid=request.GET.get('pid')
    product_detail=Product.objects.get(pk=pid)
    
    return render(request,"product_single.html",{"product_detail":product_detail})

@login_required(login_url='login')
def shop(request):
    search=request.GET.get('search')
    productes=Product.objects.all()
    category=Category.objects.all()

    if search:
        productes=Product.objects.filter(name__icontains=search)

    # add pagination functionality

    paginator=Paginator(productes,8)
    page_number=request.GET.get('page')
    productes=paginator.get_page(page_number)

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

@login_required(login_url='login')
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


def blog(request):
    search=request.GET.get('search')
    blogs=Blog.objects.all().order_by('created_at')

    if search:
        blogs=blogs.filter(title__icontains=search)

    category=Category.objects.all()

    paginator=Paginator(blogs,3)
    page_number=request.GET.get('page')
    blogs=paginator.get_page(page_number)
    
    recent_blog=Blog.objects.all().order_by('created_at')[:3]

    return render(request,"blog.html",{"category":category,"blogs":blogs,"recent_blog":recent_blog})



def blog_single(request):
    bid=request.GET.get('bid')
    blog=Blog.objects.get(id=bid)

    search=request.GET.get('search')

    if search:
        blog=Blog.objects.filter(Q(title__icontains=search)|
                          Q(description__icontaints=search))
        
    if request.method == 'POST':
        name=request.POST.get("name")
        email=request.POST.get("email")
        message=request.POST.get("message")

        Comment.objects.create(blog=blog,name=name,email=email,message=message)
        return redirect(f'/blog_single/id?bid={bid}')
    comments=Comment.objects.filter(blog=blog).order_by('id')[:3]
    category=Category.objects.all()
    recent_blog=Blog.objects.all().order_by('created_at')[:3]

    return render(request,"blog_single.html",{"blog":blog,"comments":comments,"category":category,"recent_blog":recent_blog})



def contact(request):
    if request.method == "POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        subject=request.POST.get("subject")
        message=request.POST.get("message")

        Contect_us.objects.create(name=name,email=email,subject=subject,message=message)
    return render(request,"contact.html",{"success":True})


def chatbot(request):
    message=request.GET.get('message','').lower()

    if "hello" in message:
        return JsonResponse({
        "answer":"Hello 👋 How can I help you?"
    })

    if "hi" in message:
        return JsonResponse({
        "answer":"Hi 😊 Welcome to FreshMart"
    })

    if "thank" in message:
        return JsonResponse({
        "answer":"You're welcome ❤️"
    })

    if "about" in message or "website" in message:
        return  JsonResponse({
            "answer":
            """
            welcome to vegfood

            we provide:
            🍎 Fruits
            🥦 Vegetables
            🧃 Juices
            🌴 Dates
            🍰 Desserts

            Fast Delivery Available.
            """
        })
    
    if "deal" in message:

        deals = Product.objects.filter(
        is_deal=True
    )

    text = "🔥 Today's Deals\n\n"

    for d in deals:
        text += f"{d.name} ₹{d.deal_price}\n"

        return JsonResponse({
        "answer": text
    })

    # product search
    product=Product.objects.filter(
        name__icontains=message
    ).first()

    if product:
        answer=f"""
        {product.name}
        price:{product.price}
        stock:{product.quntity}
        Category:{product.category.name}
        """
        return JsonResponse({"answer":answer})

    return JsonResponse({
        "answer":"Sorry, I could not find that product"
    })


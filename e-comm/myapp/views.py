from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from myapp.models import *
import os
from django.contrib.auth.decorators import *
# Create your views here.


def index(request):
    category=Category.objects.all()
    return render(request,"index.html",{"category":category})


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
    return render(request,"shop.html",{"productes":productes})





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



# checkout functionality
def checkout(request):
    return render(request,"checkout.html")




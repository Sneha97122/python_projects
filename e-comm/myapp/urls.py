from django.urls import *
from myapp.views import *

urlpatterns=[
    path('',index,name="index"),
    path('about',about,name="about"),
    path('product-single',product_single,name="product_single"),
    path('shop',shop,name="shop"),
    


    # login,register,logout functionality
    path('login',login_page,name="login"),
    path('register',register_page,name="register"),
    path("logout",logout,name="logout"),


    # cart functionality
    path('cart',cart,name="cart"),
    path('add_to_cart/',add_to_cart,name="add_to_cart"),
    path('increment/id',increment,name="increment"),
    path('decrement/id',decrement,name="decrement"),
    path('remove_cart/id',remove_cart,name="remove_cart"),

    # wishlist functionality
    path('wishlist/id',wishlist,name="wishlist"),
    path('add_to_wishlist/id',add_to_wishlist,name="add_to_wishlist"),

    # checkout and order functionality
    path('chekout',checkout,name="checkout"),
    path('add_address',add_address,name="add_address"),
    path('place_order',place_order,name="place_order"),
    path('payment_success',payment_success,name="payment_success"),
    

    # filter by category
    path('filter_product/id',filter_product,name="filter_product"),


    # add blog section
    path('blog_single/id',blog_single,name="blog_single"),
    path('blog',blog,name="blog"),

    # add contect us
    path('contact',contact,name="contact"),

    # add cheatbox 
    path('chatbot/',chatbot,name="chatbot")

]
from django.contrib import admin
from myapp.models import *

# Register your models here.


admin.site.register(Category)

admin.site.register(Product)

admin.site.register(Cart)

admin.site.register(Wishlist)

admin.site.register(Address)



class orderadmin(admin.ModelAdmin):
    list_display=["user","address","total_amount","payment_method","payment_status","status","created_at","razorpay_order_id"]

admin.site.register(Order,orderadmin)


class orderitemadmin(admin.ModelAdmin):
    list_display=["order","product","qty","price"]

admin.site.register(OrderItem,orderitemadmin)


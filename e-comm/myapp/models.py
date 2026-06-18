from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=20)
    image=models.ImageField(upload_to='cat_image/',null=True,blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.CharField(max_length=20)
    price=models.FloatField()
    quntity=models.IntegerField()
    description=models.TextField()
    image=models.ImageField(upload_to='pro_image/',null=True,blank=True)

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    qty=models.IntegerField()

    def total_price(self):
        return self.qty*self.product.price
    
class Address(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    address=models.TextField()
    city=models.CharField(max_length=20,null=True)
    pincode=models.PositiveIntegerField(null=True)


class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        default="Cash On Delivery"
    )

    payment_status = models.CharField(
        max_length=20,
        default="Pending"
    )

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    razorpay_order_id = models.CharField(
    max_length=200,
    null=True,
    blank=True
    )

    razorpay_payment_id = models.CharField(
    max_length=200,
    null=True,
    blank=True
    )


class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    qty=models.IntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)

    def subtotal(self):
        return self.qty*self.price
    
    

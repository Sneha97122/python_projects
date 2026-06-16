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


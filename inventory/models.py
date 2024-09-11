from django.db import models
from django.utils import timezone
import pytz

class Product(models.Model):
    productName = models.CharField(max_length=255, null=False, blank=False)
    productPrice = models.FloatField(default=0)
    quantityInStock = models.IntegerField(default=0)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    productImage = models.ImageField(default='defaultProduct.jpg', upload_to='products/')
    quantityBuyPerItem = models.IntegerField(default=0)
    quantity = models.IntegerField(default=1)

    
    class Meta():
        verbose_name_plural = 'Product'

    def __str__(self):
       return self.productName
    
    @property
    def imageURL(self):
        try:
            url = self.productImage.url
        except:
            url = ''
        return url
    

class TotalSales(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    sales_per_item = models.FloatField(default=0, null=False, blank=False)
    total_sales = models.FloatField(default=0, null=False, blank=False)

    def __str__(self):
        return f"Total Sales: {self.total_sales}"

class DailySales(models.Model):
    date = models.DateField(default=timezone.now)
    sales_amount = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if not self.date:
            utc_now = timezone.now()
            desired_timezone = pytz.timezone('Asia/Manila') 
            local_time = utc_now.astimezone(desired_timezone)
            self.date = local_time.replace(hour=0, minute=0, second=0, microsecond=0).date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Daily Sales on {self.date}: {self.sales_amount}"
    


class Category(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=255, null=False, blank=False)

    class Meta():
         verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
#===================================================================================


class Supplier(models.Model):
    supplierName = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=11, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    country = models.CharField(max_length=255, null=False, blank=False)
    profile = models.ImageField(upload_to='customer_profiles/', default='default.png', blank=True, null=True)
    background_profile = models.ImageField(upload_to='customer_profiles/', default='default.png', blank=True, null=True)

    class Meta():
         verbose_name_plural = 'Product Suppliers'

    def __str__(self):
            return self.supplierName
    
    @property
    def profile_imageURL(self):
        try:
            url = self.profile.url
        except:
            url = ''
        return url
    
    @property
    def background_imageURL(self):
        try:
            url = self.background_profile.url
        except:
            url = ''
        return url
#===================================================================================


class Transaction(models.Model):
    transactions = (
        ('Decrease stock', 'Decrease stock'),
        ('Add Product', 'Add Product'),
    )
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    transactionType = models.CharField(max_length=45, null=False, blank=False, choices=transactions)
    transactionDate = models.DateTimeField(auto_now_add=True)

    class Meta():
         verbose_name_plural = 'Transaction'

    def __str__(self):
         return self.productId + " : " + self.transactionType
#===================================================================================



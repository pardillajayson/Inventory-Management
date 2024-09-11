from django.contrib import admin
from . models import *


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Transaction)
admin.site.register(TotalSales)
admin.site.register(DailySales)

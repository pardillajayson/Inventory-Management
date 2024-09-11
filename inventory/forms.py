from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput
from .models import Product


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['productName','productPrice','quantityInStock', 'supplier', 'category', 'productImage']


class AddQuantityForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['quantity']

class PurchaseForm(forms.Form):
    product_name = forms.CharField(max_length=255, label='Product')
    quantity = forms.FloatField(min_value=1, label='Quantity')

#create user
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

#Login form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())


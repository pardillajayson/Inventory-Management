from django.urls import path
from . import views


urlpatterns = [
    path('', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('user-settings/', views.user_settings, name='user_settings'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('purchase/', views.purchase_product, name='purchase_product'),
    path('settings/', views.settings, name='settings'),
    path('result/', views.result, name='result'),
    path('supplier/', views.supplier, name='suppliers'),
    path('list-of-all-products/', views.listOfAllProducts, name='list_of_all_products'),
    path('supplier/<str:pk>/', views.singleSupplier, name='single_supplier'),
    path('add_quantity/<int:pk>/', views.add_quantity, name='add_quantity'),
    path('add-new-product/', views.addNewProducts, name='add_new_products'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('delete_product/<str:pk>/', views.delete_product, name='delete_product'),

    path('supplier/<str:pk>/supplier-background-profiles/', views.supplier_background_profile, name='single_supplier_background_profile'),
    path('supplier/<str:pk>/supplier-profile-pictures/', views.supplier_profile_picture, name='single_supplier_profile_pictures'),
]
















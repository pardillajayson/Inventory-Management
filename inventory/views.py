from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import *
from django.forms import formset_factory
from .forms import *
from django.contrib import messages
import logging
from django.utils import timezone
import os   
from datetime import datetime
import plotly.graph_objs as go
from plotly.offline import plot
from django.shortcuts import render, get_object_or_404, redirect
import pytz

logger = logging.getLogger(__name__)

#=====================================================================================
# start authentication

def logoutPage(request):
    auth.logout(request)
    return redirect('login')

def registerPage(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('login')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CreateUserForm()
    return render(request, 'inventory/register.html', {'form': form})

def loginPage(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                messages.info(request, f'Welcome to the inventory management system {user}')
                return redirect('dashboard')
        messages.warning(request, 'Invalid username or password.')

    context = {'form': form}
    return render(request, 'inventory/login.html', context=context)

# end authentication
#=====================================================================================

def dashboard(request):
    # Count products and suppliers
    all_products = Product.objects.all().count()
    all_supplier = Supplier.objects.all().count()

    # Fetch sales, products, and suppliers
    sales = TotalSales.objects.all()
    products = Product.objects.all()
    suppliers = Supplier.objects.all()
    daily_sales_data = DailySales.objects.all().order_by('-date')

    # Quantity sold per product
    total_quantity_sold_per_product = {}
    for product in products:
        total_quantity_sold_per_product[product.productName] = product.quantityBuyPerItem

    # Stock per product
    total_stock_per_product = {}
    for product in products:
        total_stock_per_product[product.productName] = product.quantityInStock

    # Total sales
    total_sale = sum(sale.sales_per_item for sale in sales)
    formatted_total_sale = "{:,}".format(total_sale)

    # Transactions
    log_file_path = 'C:/Users/shiella/OneDrive/Desktop/logging/logfile'
    transactions = []
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            for line in file:
                try:
                    parts = line.strip().split(', ')
                    time_str = parts[0].split(': ', 1)[1]
                    parsed_time = datetime.fromisoformat(time_str)
                    formatted_time = parsed_time.strftime('%Y-%m-%d %I:%M:%S %p')
                    transaction = {
                        'time': formatted_time,
                        'product': parts[1].split(': ', 1)[1],
                        'quantity': parts[2].split(': ', 1)[1],
                        'amount': parts[3].split(': ', 1)[1]
                    }
                    transactions.append(transaction)
                except (IndexError, ValueError) as e:
                    continue

        transactions.sort(key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %I:%M:%S %p'), reverse=True)
        latest_transactions = transactions[:5]

    # Prepare data for the bar chart
    product_names = list(total_quantity_sold_per_product.keys())
    quantities = list(total_quantity_sold_per_product.values())

    # Prepare data for the pie chart
    stock_product_names = list(total_stock_per_product.keys())
    stock_quantities = list(total_stock_per_product.values())

    # Prepare data for the line chart
    dates = [data.date for data in daily_sales_data]
    sales_amounts = [data.sales_amount for data in daily_sales_data]

    # Create a Plotly bar chart
    bar_chart = go.Bar(
        x=product_names,
        y=quantities,
        marker=dict(color='rgb(54, 52, 72)', line=dict(color='blue', width=1)),
    )

    # Create a Plotly pie chart
    pie_chart = go.Pie(
        labels=stock_product_names,
        values=stock_quantities,
        hoverinfo='label',
        textinfo='label+value',)

    # Create a Plotly line chart
    line_chart = go.Scatter(
        x=dates,
        y=sales_amounts,
        mode='lines+markers',
        line=dict(color='blue', width=1), 
        marker=dict(size=6),
        fill='tozeroy',  
        fillcolor='rgb(54, 52, 72)',
    )

    # Layout for the bar chart
    bar_layout = go.Layout(
        title='Best Sellers',
        title_font=dict(color='rgb(235, 228, 228)', size=20),
        title_x=0.5, 
        xaxis=dict(title='Product',
                   titlefont=dict(color='rgb(235, 228, 228)'),
                   tickfont=dict(color='rgb(235, 228, 228)')),
        yaxis=dict(title='Quantity',
                   gridcolor='rgba(255, 255, 255, 0.2)', 
                   gridwidth=1, 
                   titlefont=dict(color='rgb(235, 228, 228)'),
                   tickfont=dict(color='rgb(235, 228, 228)')),
        plot_bgcolor='rgb(36,35,35)',
        paper_bgcolor='rgb(36,35,35)',
        height=240,
    )

    # Layout for the pie chart
    pie_layout = go.Layout(
        title='Inventory Stock',
        title_font=dict(color='white', size=20),
        title_x=0.5,
        plot_bgcolor='rgb(36,35,35)',
        paper_bgcolor='rgb(36,35,35)',
        height=242,
    )

    # Layout for the line chart
    line_layout = go.Layout(
        title='Track Sales per Day',
        title_font=dict(color='rgb(235, 228, 228)', size=20),
        title_x=0.5,
        xaxis=dict(
            title='Date',
            titlefont=dict(color='rgb(235, 228, 228)'), 
            tickfont=dict(color='rgb(235, 228, 228)'), 
            gridcolor='rgba(255, 255, 255, 0.2)', 
            gridwidth=0.5,     
        ),
        yaxis=dict(
            title='Sales Amount',
            titlefont=dict(color='rgb(235, 228, 228)'), 
            tickfont=dict(color='lightgrey'), 
            gridcolor='rgba(255, 255, 255, 0.2)', 
            gridwidth=1,                       
        ),
        plot_bgcolor='rgb(36,35,35)',
        paper_bgcolor='rgb(36,35,35)',
        height=450, 
    )



    # Create figures for Plotly graphs
    bar_fig = go.Figure(data=[bar_chart], layout=bar_layout)
    pie_fig = go.Figure(data=[pie_chart], layout=pie_layout)
    line_fig = go.Figure(data=[line_chart], layout=line_layout)

    # Convert figures to JSON strings
    graph_json = plot(bar_fig, output_type='div', include_plotlyjs=False)
    pie_graph_json = plot(pie_fig, output_type='div', include_plotlyjs=False)
    line_graph_json = plot(line_fig, output_type='div', include_plotlyjs=False)

    context = {
        'daily_sales': daily_sales_data,
        'transactions': latest_transactions,
        'total_item': all_products,
        'total_supplier': all_supplier,
        'total_sale': formatted_total_sale,
        'products': products,
        'total_stock_per_product': total_stock_per_product,
        'total_quantity_sold_per_product': total_quantity_sold_per_product,
        'suppliers': suppliers,
        'graph': graph_json,
        'pie_graph': pie_graph_json,
        'line_graph': line_graph_json,
    }
    return render(request, 'inventory/dashboard.html', context)


def purchase_product(request):
    PurchaseFormSet = formset_factory(PurchaseForm, extra=1)
    if request.method == 'POST':
        formset = PurchaseFormSet(request.POST)
        if formset.is_valid():
            purchases = []
            total_cost = 0
            for form in formset:
                product_name = form.cleaned_data.get('product_name')
                quantity = form.cleaned_data.get('quantity')
                if product_name and quantity:
                    product = Product.objects.get(productName=product_name)
                    if product.quantityInStock >= quantity:
                        try:
                            product = Product.objects.get(productName=product_name)
                            cost = quantity * product.productPrice
                            total_cost += cost
                            purchases.append({
                                'product_name': product_name,
                                'quantity': quantity,
                                'price': product.productPrice,
                                'cost': cost
                            })

                            # Update product stock
                            product.quantityInStock -= quantity
                            if product.quantityInStock <= 10:
                                messages.warning(request, 'Inventory stock is too low, check the inventory now!')
                                
                            product.quantityBuyPerItem += quantity
                            product.save()

                            # Log the transaction
                            logger.info(f"Time: {timezone.now()}, Product: {product.productName}, Quantity Sold: {quantity}, Amount of the Bill: {cost}")

                            # Update or create TotalSales record for the specific product
                            total_sales_item, created = TotalSales.objects.get_or_create(product=product)
                            total_sales_item.sales_per_item += cost
                            total_sales_item.save()

                            # Update or create TotalSales record for overall total sales
                            total_sales_overall, created = TotalSales.objects.get_or_create(product=None)
                            total_sales_overall.total_sales += cost
                            total_sales_overall.save()

                            # Update or create DailySales record for the current date
                            today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                            daily_sales, created = DailySales.objects.get_or_create(date=today)
                            daily_sales.sales_amount += cost
                            daily_sales.save()


                        except Product.DoesNotExist:
                            form.add_error('product_name', 'This product does not exist.')
                            return render(request, 'inventory/purchase.html', {'formset': formset})
                    else:
                        messages.warning(request, f'Available stock for {product.productName}'+' is low!! please check the inventory now.')
                        return redirect('purchase_product')
                    
            # Debugging output
            logger.info(f"Total Cost: {total_cost}, Purchases: {purchases}")

            request.session['purchases'] = purchases
            request.session['total_cost'] = total_cost
            return redirect('result')
    else:
        formset = PurchaseFormSet()

    context = {
        'formset': formset,
    }
    return render(request, 'inventory/purchase.html', context)


def result(request):
    purchases = request.session.get('purchases', [])
    total_cost = request.session.get('total_cost', 0)
    return render(request, 'inventory/purchase_result.html', {'purchases': purchases, 'total_cost': total_cost})

def singleSupplier(request, pk):
    single_supplier = Supplier.objects.get(id=pk)
    items = single_supplier.product_set.all()   
    context = {
        'suppliers':single_supplier,
        'item':items
    }
    return render(request, 'inventory/single_supplier.html', context)

def supplier(request):
    suppliers = Supplier.objects.all()
    context = {
        'suppliers':suppliers
    }
    return render(request, 'inventory/suppliers.html', context)

def supplier_background_profile(request,pk):
    single_supplier = Supplier.objects.get(id=pk)

    context = {
        'suppliers':single_supplier,
    }
    return render(request, 'inventory/user_backgroundprofile.html', context)

def supplier_profile_picture(request,pk):
    single_supplier = Supplier.objects.get(id=pk)

    context = {
        'suppliers':single_supplier,
    }
    return render(request, 'inventory/user_profile_pictures.html', context)

def user_settings(request):
    return render(request, 'inventory/user_settings.html')

def listOfAllProducts(request):
    search_query = request.GET.get('search')
    products = Product.objects.all()

    if search_query:
        products = products.filter(productName__icontains=search_query)
        
    context = {
        'products':products
    }
    return render(request, 'inventory/list_of_products.html', context)

def settings(request):
    return render(request, 'inventory/settings.html')

def add_quantity(request, pk):
    product = get_object_or_404(Product,id=pk)

    if request.method == 'POST':
        form = AddQuantityForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            product.quantityInStock += quantity
            product.save()
            messages.success(request, f'{quantity} stock successfully added for {product.productName}.')
            return redirect('list_of_all_products')
    else:
        form = AddQuantityForm()

    context = {
        'form': form,
        'product': product
    }
    return render(request, 'inventory/add_quantity.html', context)


def addNewProducts(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            return redirect('list_of_all_products')
    else:
        form = AddProductForm()
    context = {
        'form': form
    }
    return render(request, 'inventory/add_product.html', context)


def get_transactions(log_file_path):
    transactions = []
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            for line in file:
                try:
                    parts = line.strip().split(', ')
                    time_str = parts[0].split(': ', 1)[1]

                    # Assume the time in the log file is in UTC
                    parsed_time = datetime.fromisoformat(time_str)
                    if parsed_time.tzinfo is None:
                        # If the datetime is naive, set it to UTC
                        parsed_time = pytz.utc.localize(parsed_time)

                    # Convert the UTC time to Philippine Time
                    philippine_time = parsed_time.astimezone(pytz.timezone('Asia/Manila'))
                    formatted_time = philippine_time.strftime('%Y-%m-%d %I:%M:%S %p')

                    transaction = {
                        'time': formatted_time,
                        'product': parts[1].split(': ', 1)[1],
                        'quantity': parts[2].split(': ', 1)[1],
                        'amount': parts[3].split(': ', 1)[1]}
                    transactions.append(transaction)

                except (IndexError, ValueError) as e:
                    print(f"Error parsing line: {line}. Error: {e}")
                    continue
        transactions.sort(key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %I:%M:%S %p'), reverse=True)
    return transactions

def transactions_view(request):
    log_file_path = 'C:/Users/shiella/OneDrive/Desktop/logging/logfile'
    transactions = get_transactions(log_file_path)

    context = {
        'transactions': transactions,
    }
    return render(request, 'inventory/transactions.html', context)

def delete_product(request, pk):
    single_product = Product.objects.get(id = pk)
    single_product.delete()
    messages.success(request, 'successfully deleted')
    return redirect('list_of_all_products')


    




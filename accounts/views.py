from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import *
from .form import OrderForm, CreateUserForm
from .filters import OrderFilter
from .my_middleware import simple_middleware
from .decorators import unauthenticated_user, allowed_users, admin_only

# Create your views here.

# REGISTER


@unauthenticated_user
def registerPage(request):
    # check đã login chưa
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Xử lý group
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            
            username = form.cleaned_data.get('username')
            
            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)

# LOGIN


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)

# LOGOUT


def logoutUser(request):
    logout(request)
    return redirect('login')

# USER PAGE


@login_required(login_url='login')
def userPage(request):
    context = {}
    return render(request, 'accounts/user.html', context)


# HOME PAGE
# Bắt buộc login mới vào
@login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
@admin_only
def home(request):
    orders = Order.objects.order_by('date_created').all()
    customers = Customer.objects.all()

    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    orders = orders[0:5]
    context = {'orders': orders, 'customers': customers, 'total_customers': total_customers,
               'total_orders': total_orders, 'delivered': delivered, 'pending': pending}
    return render(request, 'accounts/dashboard.html', context)

# PRODUCTS PAGE


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()

    return render(request, 'accounts/products.html', {'products': products})

# CUSTOMER PAGE


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)

    orders = customer.order_set.all()
    total_orders = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer': customer, 'orders': orders,
               'total_orders': total_orders, 'myFilter': myFilter}

    return render(request, 'accounts/customer.html', context)

# ORDER PAGE


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(
        Customer, Order, fields=('product', 'status'), extra=10)
    customer = Customer.objects.get(id=pk)
    formSet = OrderFormSet(queryset=Order.objects.none(), instance=customer)

    if request.method == 'POST':
        formSet = OrderFormSet(request.POST, instance=customer)
        if formSet.is_valid():
            formSet.save()
            return redirect('/customer/'+str(pk))
    context = {'formSet': formSet}
    return render(request, 'accounts/order_form.html', context)

# UPDATE ORDER


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/order_form.html', context)

# DELETE ORDER


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {'item': order}
    return render(request, 'accounts/delete.html', context)

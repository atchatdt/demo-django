from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

from .models import *
from .form import OrderForm, CreateUserForm
from .filters import OrderFilter

# Create your views here.


def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()


    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def loginPage(request):
    context = {}
    return render(request, 'accounts/login.html')


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


def products(request):
    products = Product.objects.all()

    return render(request, 'accounts/products.html', {'products': products})


def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)

    orders = customer.order_set.all()
    total_orders = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer': customer, 'orders': orders,
               'total_orders': total_orders, 'myFilter': myFilter}

    return render(request, 'accounts/customer.html', context)


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


def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {'item': order}
    return render(request, 'accounts/delete.html', context)

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,Sale,Customer,Setting
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import csv
from reportlab.pdfgen import canvas
from django.db.models import Sum
from django.utils.timezone import localtime
from collections import defaultdict
import datetime
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.utils.timezone import now, timedelta
from .models import Product, Sale,Supplier

def dashboard(request):
    # Main dashboard metrics
    product_count = Product.objects.count()
    total_stock = sum(p.quantity for p in Product.objects.all())
    total_sales = sum(sale.total_price() for sale in Sale.objects.all())
    low_stock_count = Product.objects.filter(quantity__lt=100).count()

    # Date calculations
    today = now().date()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    # Recent activity
    recent_products = Product.objects.order_by('-id')[:5]  # Recently added
    recent_sales = Sale.objects.filter(date__gte=two_days_ago).order_by('-date')[:5]
    low_stock_products = Product.objects.filter(quantity__lt=10)
    reordered = Product.objects.filter(quantity__gt=100).order_by('-id')[:3]  # Assumed reordered

    # Restock suggestions
    restock_suggestions = Product.objects.filter(quantity__lt=5)

    context = {
        'product_count': product_count,
        'total_stock': total_stock,
        'total_sales': total_sales,
        'low_stock_count': low_stock_count,
        'recent_products': recent_products,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
        'reordered': reordered,
        'restock_suggestions': restock_suggestions,
    }
    return render(request, 'index.html', context)



def products(request):
    if request.method == "POST":
        name = request.POST.get('name')
        category = request.POST.get('category')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        Product.objects.create(name=name, category=category, quantity=quantity, price=price)
        return redirect('products')

    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('products')


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.category = request.POST.get('category')
        product.quantity = request.POST.get('quantity')
        product.price = request.POST.get('price')
        product.save()
        return redirect('products')

    return render(request, 'edit_product.html', {'product': product})


def sales(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))
        product = Product.objects.get(id=product_id)
        if product.quantity >= quantity:
            product.quantity -= quantity
            product.save()
            Sale.objects.create(product=product, quantity=quantity)

        return redirect('sales')

    all_sales = Sale.objects.all()
    products = Product.objects.all()
    return render(request, 'sales.html', {'sales': all_sales, 'products': products})

# views.py
def reports(request):
    sales = Sale.objects.select_related('product')
    sales_data = {}
    revenue_data = {}

    for sale in sales:
        name = sale.product.name
        sales_data[name] = sales_data.get(name, 0) + sale.quantity
        revenue_data[name] = revenue_data.get(name, 0) + (sale.quantity * sale.product.price)

    context = {
        'sales_data': json.dumps(sales_data, cls=DjangoJSONEncoder),
        'revenue_data': json.dumps(revenue_data, cls=DjangoJSONEncoder),
    }

    return render(request, 'reports.html', context)


def suppliers_view(request):
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers.html', {'suppliers': suppliers})

def add_supplier(request):
    if request.method == 'POST':
        Supplier.objects.create(
            name=request.POST['name'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            address=request.POST['address']
        )
    return redirect('suppliers')

def delete_supplier(request, supplier_id):
    if request.method == 'POST':
        supplier = get_object_or_404(Supplier, id=supplier_id)
        supplier.delete()
    return redirect('suppliers')

def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        supplier.name = request.POST['name']
        supplier.phone = request.POST['phone']
        supplier.email = request.POST['email']
        supplier.address = request.POST['address']
        supplier.save()
    return redirect('suppliers')


def customers(request):
    all_customers = Customer.objects.all()
    return render(request, 'customers.html', {'customers': all_customers})

def add_customer(request):
    if request.method == 'POST':
        Customer.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            address=request.POST['address']
        )
        return redirect('customers')
    return render(request, 'add_customer.html')

def edit_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        customer.name = request.POST['name']
        customer.email = request.POST['email']
        customer.phone = request.POST['phone']
        customer.address = request.POST['address']
        customer.save()
        return redirect('customers')
    return render(request, 'edit_customer.html', {'customer': customer})

def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    return redirect('customers')

def customer_sales(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    sales = Sale.objects.filter(customer=customer)
    return render(request, 'customer_sales.html', {'customer': customer, 'sales': sales})
def settings_view(request):
    setting = Setting.objects.first()
    if not setting:
        setting = Setting.objects.create(tax_rate=0)

    if request.method == 'POST':
        tax = float(request.POST.get('taxRate', 0))
        setting.tax_rate = tax
        setting.save()
        return redirect('settings')

    return render(request, 'settings.html', {'setting': setting})
def export_sales_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product', 'quantity', 'Date', 'total_price'])
    for sale in Sale.objects.all():
        writer.writerow([sale.product.name, sale.quantity, sale.total_price, sale.date])

    return response

def export_sales_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, "Sales Report")

    y = 770
    for sale in Sale.objects.all():
        line = f"{sale.product.name}, Qty: {sale.product.quantity}, Total: {sale.total_price}, Date: {sale.date}"
        p.drawString(80, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response



# Create your views here.

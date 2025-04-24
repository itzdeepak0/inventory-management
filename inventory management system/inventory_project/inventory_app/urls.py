from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.products, name='products'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('sales/', views.sales, name='sales'),
    path('reports/', views.reports, name='reports'),
    path('suppliers/', views.suppliers_view, name='suppliers'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/delete/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),

    path('customers/', views.customers, name='customers'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/edit/<int:id>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:id>/', views.delete_customer, name='delete_customer'),
    path('customers/<int:customer_id>/sales/', views.customer_sales, name='customer_sales'),

    path('settings/', views.settings_view, name='settings'),

    path('export/csv/', views.export_sales_csv, name='export_sales_csv'),
    path('export/pdf/', views.export_sales_pdf, name='export_sales_pdf'),

]

"""Reimbursement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import view

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('signup/', view.signup),
    path('signin/', view.signin),
    path('verify/', view.verify),
    path('new_invoice/', view.new_invoice),
    path('look_invoice/', view.look_invoice),
    path('new_rei_basket/', view.new_rei_basket),
    path('put_invoice_tobasket/', view.put_invoice_tobasket),
    path('modify_invoice/', view.modify_invoice),
    path('re_apply_invoicet/', view.re_apply_invoicet),    
    path('refuse_invoicet/', view.refuse_invoicet),
    path('get_his_morder/', view.get_his_morder), 
    path('get_all_category/', view.get_all_category),  
]

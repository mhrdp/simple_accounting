from django import db
from django.core.checks.messages import DEBUG, Debug
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.views.generic import View

from django.core.paginator import (
    Paginator, EmptyPage, PageNotAnInteger
)

from .forms import ProductForm, IncomeForm, ExpenseForm
from .models import Product, ExpenseCategory, SubCategory, Journal
from .utils import render_to_pdf

from user.models import CompanyDetail

from decimal import Decimal

import json
import csv

# Create your views here.
@login_required
def expense_filter_by_date(request):
    expense_paginate = None
    page_range = None
    sum_of_filtered_expense = None

    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    if date_start and date_end:
        filtered_expense = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            date_added__range=(date_start, date_end)
        ).order_by('date_added')
        sum_of_filtered_expense = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            date_added__range=(date_start, date_end)
        ).aggregate(
            sum=Sum('total')
        )

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(filtered_expense, 10)

        try:
            expense_paginate = paginator.page(page)
        except PageNotAnInteger:
            expense_paginate = paginator.page(1)
        except EmptyPage:
            expense_paginate = paginator.page(paginator.num_pages)

        index = expense_paginate.number-1
        max_index = len(paginator.page_range)
        start_index = index-3 if index>=3 else 0
        end_index = index+3 if index<=max_index-3 else max_index

        page_range = list(paginator.page_range)[start_index:end_index]
    else:
        pass

    content = {
        'paginate': expense_paginate,
        'page_range': page_range,
        'sum_of_filtered_expense': sum_of_filtered_expense,
    }
    return render(request, 'books/filtered_expense.html', content)

# Ajax for categories and sub categories dependent dropdown
def expense_dropdown_ajax(request):
    categories = request.GET.get('category')
    sub_categories = SubCategory.objects.filter(
        category=categories
    ).order_by('-sub_category')

    content = {
        'sub_categories': sub_categories,
    }
    return render(request, 'books/category_ajax.html', content)
# End of ajax categories and sub categories

# Ajax for autofill income form
def income_form_autofill_ajax(request):
    product_name = request.GET.get('product_name')
    price = Product.objects.filter(
        id=product_name
    )

    content = {
        'product_price': price,
    }
    return render(request, 'books/income_form_autofill.html', content)
# end of ajax autofill income form
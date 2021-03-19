from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.paginator import (
    Paginator, EmptyPage, PageNotAnInteger
)

from .forms import ProductForm, IncomeForm, ExpenseForm
from .models import Product, ExpenseCategory, SubCategory, Journal

import json

# Create your views here.

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

@login_required
def register_product(request):
    product_form_notification = ''
    if request.method == 'POST':
        product_form = ProductForm(request.POST or None)
        if product_form.is_valid():
            product_form_save = product_form.save(commit=False)
            product_form_save.username = request.user

            product_form_save.save()
            product_form_notification = 'Your product has been inputted!'

            return redirect('register_product')
        else:
            product_form_notification = 'Your data is not valid!'
    else:
        product_form = ProductForm()
    content = {
        'product_form': product_form,
        'product_form_notification': product_form_notification
    }
    return render(request, 'books/register_product.html', content)

@login_required
def register_income(request):
    empty_notification = ''
    if request.method == 'POST':
        income_form = IncomeForm(request.user, request.POST or None)

        # Validation for product_name field
        if Product.product_name != None:
            # income_form.fields['product_name'].queryset = Product.objects.filter(username=request.user.pk)
            if income_form.is_valid():
                income_form_save = income_form.save(commit=False)
                income_form_save.username = request.user
                income_form_save.industry = request.user.companydetail.industry
                income_form_save.book_category = "Debit"

                income_form_save.total = (income_form_save.price*income_form_save.quantity)+income_form_save.additional_price

                income_form_save.save()
                messages.success(request, 'Your data has been inputted!')
                return redirect('register_income')
            else:
                messages.error(request, 'There\'s something wrong in your data!')
    else:
        income_form = IncomeForm(request.user)

    content = {
        'income_form': income_form,
        'empty_notification': empty_notification,
    }
    return render(request, 'books/register_income.html', content)

@login_required
def register_expense(request):
    expense_form_notification = ''
    if request.method == 'POST':
        expense_form = ExpenseForm(request.POST or None)
        if expense_form.is_valid():
            expense_form_save = expense_form.save(commit=False)
            expense_form_save.username = request.user
            expense_form_save.industry = request.user.companydetail.industry
            expense_form_save.book_category = 'Kredit'

            expense_form_save.total = expense_form_save.price*expense_form_save.quantity

            expense_form_save.save()
            return redirect('register_expense')
        else:
            expense_form_notification = 'There\'s something wrong in your input!'
    else:
        expense_form = ExpenseForm()
    
    content = {
        'expense_form': expense_form,
        'expense_form_notification': expense_form_notification,
    }
    return render(request, 'books/register_expense.html', content)

@login_required
def list_of_expense(request):
    # List of all the expenses
    list_of_expense = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit'
    ).order_by('date_added')

    #Paginator, to split page into several pages
    page = request.GET.get('page', 1)
    paginator = Paginator(list_of_expense, 20) # split page per 20 items
    try:
        expense_page = paginator.page(page)
    except PageNotAnInteger:
        expense_page = paginator.page(1)
    except EmptyPage:
        expense_page = paginator.page(paginator.num_pages)

    # Data for chart for the last 30 days
    expense_chart_last_30_days = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit',
    ).values(
        'date_added'
    ).order_by(
        'date_added'
    )[:30].annotate(
        sum=Sum('total')
    )

    content = {
        'list_of_expense': list_of_expense,
        'expense_page': expense_page,
        'expense_chart_last_30_days': expense_chart_last_30_days,
    }
    return render(request, 'books/list_of_expense.html', content)

@login_required
def edit_expense(request, pk):
    # Call ajax for dependent dropdown
    categories = request.GET.get('category')
    sub_categories = SubCategory.objects.filter(
        category=categories
    ).order_by('-sub_category')

    # Views for edit
    user_obj = get_object_or_404(Journal, pk=pk)
    if not request.user == user_obj.username:
        return redirect('list_of_expense')
    else:
        obj = get_object_or_404(Journal, pk=pk)
        expense_form = ExpenseForm(request.POST or None, instance=obj)
        if expense_form.is_valid():
            save_expense_form = expense_form.save(commit=False)

            save_expense_form.total = save_expense_form.quantity * save_expense_form.price
            save_expense_form.save()

            messages.success(request, 'Updated!')
            return redirect('list_of_expense')

    content = {
        'sub_categories': sub_categories,
        'expense_form': expense_form,
    }
    return render(request, 'books/edit_expense.html', content)
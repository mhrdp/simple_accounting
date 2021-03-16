from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .forms import ProductForm, IncomeForm, ExpenseForm
from .models import Product, ExpenseCategory, SubCategory

# Create your views here.

# Ajax for categories and sub categories
def expense_dropdown_ajax(request):
    categories = request.GET.get('category')
    sub_categories = SubCategory.objects.filter(
        categories=categories
    ).order_by('-sub_category')

    content = {
        'sub_categories': sub_categories,
    }
    return render(request, 'books/ajax.html', content)
# End of ajax

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
    income_form_notification = ''
    if request.method == 'POST':
        income_form = IncomeForm(request.POST or None)

        income_form.fields['product_name'].queryset = Product.objects.filter(username=request.user.pk)

        if income_form.is_valid():
            income_form_save = income_form.save(commit=False)
            income_form_save.username = request.user
            income_form_save.industry = request.user.companydetail.industry
            income_form_save.book_category = "Debit"

            income_form_save.total = (income_form_save.price*income_form_save.quantity)+income_form_save.additional_price

            income_form_save.save()
            return redirect('register_income')
        else:
            income_form_notification = 'There\'s some error in your input!'
    else:
        income_form = IncomeForm()

    content = {
        'income_form': income_form,
        'income_form_notification': income_form_notification,
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
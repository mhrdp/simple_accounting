from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from django.http.response import HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from .forms import ProductForm, IncomeForm, ExpenseForm
from .models import Product, Journal, ExpenseCategory, SubCategory

@login_required
def edit_product(request, pk):
    user_obj = get_object_or_404(Product, pk=pk)
    if not request.user == user_obj.username:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('list_of_product')
    else:
        product_obj = get_object_or_404(Product, pk=pk)
        product_form = ProductForm(request.POST or None, instance=product_obj)
        if product_form.is_valid():
            form_save = product_form.save(commit=False)
            form_save.save()

            messages.success(request, 'Data berhasil diperbaharui!')
            if not request.session['previous_page']:
                return redirect('list_of_product')
            else:
                return HttpResponseRedirect(request.session['previous_page'])
    content = {
        'product_form': product_form,
        'product_obj': product_obj,
    }
    return render(request, 'books/edit/edit_product.html', content)

@login_required
def delete_product(request, pk):
    user_obj = get_object_or_404(Product, pk=pk)
    if not request.user == user_obj.username:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini')
        return redirect('list_of_product')
    else:
        product_obj = Product.objects.get(pk=pk)
        if product_obj:
            product_obj.delete()
            messages.success(request, 'Anda berhasil menghapus data ini')
            if not request.session['previous_page']:
                return redirect('list_of_product')
            else:              
                return HttpResponseRedirect(request.session['previous_page'])

    content = {
        'del_product': product_obj,
    }

    return render(request, 'books/edit/delete_product.html', content)

@login_required
def edit_income(request, pk):
    # Call ajax for autofill price field
    product_name = request.GET.get('product_name')
    price = Product.objects.filter(
        id=product_name
    )

    # Views for edit
    user_obj = get_object_or_404(Journal, pk=pk)
    if not request.user == user_obj.username:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('list_of_income')
    else:
        obj = get_object_or_404(Journal, pk=pk)

        # request.user is needed here to filter products' list based on username, see IncomeForm in forms.py for detail
        income_form = IncomeForm(request.user, request.POST or None, instance=obj)
        if income_form.is_valid():
            income_form_save = income_form.save(commit=False)

            if income_form_save.additional_price is None:
                income_form_save.additional_price = 0

            income_form_save.total = (income_form_save.price*income_form_save.quantity)+income_form_save.additional_price

            income_form_save.save()
            messages.success(request, 'Data berhasil diperbaharui')
            if not request.session['previous_page']:
                return redirect('list_of_income')
            else:
                return HttpResponseRedirect(request.session['previous_page'])

    content = {
        'income_form': income_form,
        'product_name': obj.product_name,
        'product_price': price,
    }
    return render(request, 'books/edit/edit_income.html', content)

@login_required
def delete_income(request, pk):
    user_obj = get_object_or_404(Journal, pk=pk)
    if not request.user == user_obj.username:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini')
        return redirect('list_of_income')
    else:
        income_obj = Journal.objects.get(pk=pk)
        if income_obj:
            income_obj.delete()
            messages.success(request, 'Anda berhasil menghapus data ini')
            if not request.session['previous_page']:
                return redirect('list_of_income')
            else:
                return HttpResponseRedirect(request.session['previous_page'])

    content = {
        'del_income': income_obj,
    }
    return render(request, 'books/edit/delete_income.html', content)

@login_required
def delete_expense(request, pk):
    user_obj = get_object_or_404(Journal, pk=pk)
    if not request.user == user_obj.username:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini')
        return redirect('list_of_expense')
    else:
        expense_obj = Journal.objects.get(pk=pk)
        if expense_obj:
            expense_obj.delete()
            if not request.session['previous_page']:
                return redirect('list_of_expense')
            else:
                return HttpResponseRedirect(request.session['previous_page'])

    content = {
        'del_expense': expense_obj,
    }
    return render(request, 'books/edit/delete_expense.html', content)

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
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini')
        return redirect('list_of_expense')
    else:
        obj = get_object_or_404(Journal, pk=pk)
        expense_form = ExpenseForm(request.POST or None, instance=obj)
        if expense_form.is_valid():
            save_expense_form = expense_form.save(commit=False)

            save_expense_form.total = save_expense_form.quantity * save_expense_form.price
            save_expense_form.save()

            messages.success(request, 'Data berhasil di perbaharui')
            if not request.session['previous_page']:
                return redirect('list_of_expense')
            else:
                return HttpResponseRedirect(request.session['previous_page'])

    content = {
        'sub_categories': sub_categories,
        'expense_form': expense_form,
        'item_name': obj.item_name,
    }
    return render(request, 'books/edit/edit_expense.html', content)
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, StreamingHttpResponse

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
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

@login_required
def income_filter_by_date(request):
    income_paginate = None
    page_range = None
    sum_of_filtered_income = None

    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    if date_start and date_end:
        filtered_income = Journal.objects.filter(
            username=request.user.pk,
            book_category='Debit',
            date_added__range=(date_start, date_end)
        ).order_by('date_added')
        sum_of_filtered_income = Journal.objects.filter(
            username=request.user.pk,
            book_category='Debit',
            date_added__range=(date_start, date_end)
        ).aggregate(
            sum=Sum('total')
        )

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(filtered_income, 10)

        try:
            income_paginate = paginator.page(page)
        except PageNotAnInteger:
            income_paginate = paginator.page(1)
        except EmptyPage:
            income_paginate = paginator.page(paginator.num_pages)
        
        # Display only the six pages maximum from the current total pages of pagination
        index = income_paginate.number-1 # -1 because index start from 0
        max_index = len(paginator.page_range)
        start_index = index-3 if index>=3 else 0
        end_index = index+3 if index<=max_index-3 else max_index

        # Make a list to be looped with for loop
        page_range = list(paginator.page_range)[start_index:end_index]
    else:
        pass
        
    content = {
        'paginate': income_paginate,
        'page_range': page_range,
        'sum_of_filtered_income': sum_of_filtered_income,

        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'books/filtered_income.html', content)

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

# Export table to CSV / Excel / PDF
def export_journal_to_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="journal.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date Added', 'Expense', 'Income', 'Book Category', 'Category', 'Sub Category', 'Price', 'Quantity', 'Total', 'Notes'])

    if start_date != None and start_date != '' and end_date != None and end_date != '':
        journal = Journal.objects.filter(
            username=request.user.pk,
            date_added__range=(start_date, end_date),
        ).values_list(
            'date_added', 'item_name', 'product_name__product_name', 'book_category', 'category__category', 'sub_category__sub_category', 'price', 'quantity', 'total', 'notes'
        )
    else:
        journal = Journal.objects.filter(
            username=request.user.pk,
        ).values_list(
            'date_added', 'item_name', 'product_name__product_name', 'book_category', 'category__category', 'sub_category__sub_category', 'price', 'quantity', 'total', 'notes'
        )
    for expense in journal:
        writer.writerow(expense)
    return response

@login_required
def export_profit_loss_to_pdf(request):
    company_name = get_object_or_404(CompanyDetail, username=request.user.pk)

    get_current_month = timezone.now().month
    
    # Convert month's number to the name of the month
    # timezone.now() by default return number
    months = {}
    list_of_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    for i, j in zip(range(1, 13), list_of_months):
        months[i] = j
    # End

    get_previous_month = months[get_current_month-1]

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date != None and end_date != None and start_date != '' and end_date != '':
        # Income in running month
        monthly_income = Journal.objects.filter(
            username=request.user.pk,
            book_category='Debit',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )

        # Inventory Value in running month
        monthly_raw_material = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Bahan Mentah',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )
        monthly_wip = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Barang Setengah Jadi',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )
        monthly_finished_goods = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Barang Jadi',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )
        monthly_production_misc = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Biaya Produksi Lainnya',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )

        # Operating Cost
        monthly_marketing = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Operasional',
            sub_category__sub_category='Biaya Pemasaran',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )
        monthly_logistic = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Operasional',
            sub_category__sub_category='Transportasi / Logistik',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )
        monthly_operation_misc = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Operasional',
            sub_category__sub_category='Biaya Operasional Lainnya',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )

        # Administration Cost
        monthly_office_needs = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Kebutuhan Kantor',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )
        monthly_salary = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Gaji Karyawan',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )
        monthly_rent = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Biaya Sewa',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )
        monthly_administration_misc = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Biaya Administrasi Lainnya',
            date_added__range=(start_date, end_date),
        ).aggregate(
            sum=Sum('total')
        )
    else:
        # Income in running month
        monthly_income = Journal.objects.filter(
            username=request.user.pk,
            book_category='Debit',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )

        # Inventory Value in running month
        monthly_raw_material = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Bahan Mentah',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_wip = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Barang Setengah Jadi',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_finished_goods = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Barang Jadi',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_production_misc = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Biaya Produksi Lainnya',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )

        # Operating Cost
        monthly_marketing = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Operasional',
            sub_category__sub_category='Biaya Pemasaran',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_logistic = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Operasional',
            sub_category__sub_category='Transportasi / Logistik',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_operation_misc = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Operasional',
            sub_category__sub_category='Biaya Operasional Lainnya',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )

        # Administration Cost
        monthly_office_needs = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Kebutuhan Kantor',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_salary = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Gaji Karyawan',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_rent = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Biaya Sewa',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_administration_misc = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Biaya Administrasi Lainnya',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )

    # This to replace None type in dict into zero (0)
    def dict_clean(items):
        result = {}
        for key, value in items:
            if value == None:
                value = 0
            result[key] = value
        return result
    
    # To make sure object type Decimal serializable by JSON by changing it to float and format it to reselble Decimal
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                float_obj = float(obj)
                return float_obj
            return json.JSONEncoder.default(self, float_obj)

    # Re-format income
    income_dict = json.dumps(monthly_income, cls=DecimalEncoder)
    monthly_income_0 = json.loads(income_dict, object_pairs_hook=dict_clean)

    # Re-format production cost
    raw_material_dict = json.dumps(monthly_raw_material, cls=DecimalEncoder)
    monthly_raw_material_0 = json.loads(raw_material_dict, object_pairs_hook=dict_clean)

    wip_dict = json.dumps(monthly_wip, cls=DecimalEncoder)
    monthly_wip_0 = json.loads(wip_dict, object_pairs_hook=dict_clean)

    finished_goods_dict = json.dumps(monthly_finished_goods, cls=DecimalEncoder)
    monthly_finished_goods_0 = json.loads(finished_goods_dict, object_pairs_hook=dict_clean)

    misc_production_dict = json.dumps(monthly_production_misc, cls=DecimalEncoder)
    monthly_production_misc_0 = json.loads(misc_production_dict, object_pairs_hook=dict_clean)

    # Re-format operational cost
    marketing_dict = json.dumps(monthly_marketing, cls=DecimalEncoder)
    monthly_marketing_0 = json.loads(marketing_dict, object_pairs_hook=dict_clean)

    logistic_dict = json.dumps(monthly_logistic, cls=DecimalEncoder)
    monthly_logistic_0 = json.loads(logistic_dict, object_pairs_hook=dict_clean)

    misc_operational_dict = json.dumps(monthly_operation_misc, cls=DecimalEncoder)
    monthly_operation_misc_0 = json.loads(misc_operational_dict, object_pairs_hook=dict_clean)

    # Re-format administration cost
    office_needs_dict = json.dumps(monthly_office_needs, cls=DecimalEncoder)
    monthly_office_needs_0 = json.loads(office_needs_dict, object_pairs_hook=dict_clean)

    salary_dict = json.dumps(monthly_salary, cls=DecimalEncoder)
    monthly_salary_0 = json.loads(salary_dict, object_pairs_hook=dict_clean)

    rent_dict = json.dumps(monthly_rent, cls=DecimalEncoder)
    monthly_rent_0 = json.loads(rent_dict, object_pairs_hook=dict_clean)

    misc_administration_dict = json.dumps(monthly_administration_misc, cls=DecimalEncoder)
    monthly_administration_misc_0 = json.loads(misc_administration_dict, object_pairs_hook=dict_clean)

    # To sum it you need to convert it to float first so you can do mathematical operations with the result
    # The end result of formatting the float was a string, so don't use formatted result if you want to do mathematical operations
    monthly_production_sum = monthly_raw_material_0['sum'] + monthly_wip_0['sum'] + monthly_finished_goods_0['sum'] + monthly_production_misc_0['sum'] # a float
    format_float_production_sum = '{:.2f}'.format(monthly_production_sum) # a string

    # Format monthly_income data type to float
    monthly_income_sum = float(monthly_income_0['sum']) # a float

    # Gross Profit = monthly_income - monthly_production_sum
    # type float
    monthly_gross_profit = monthly_income_sum - monthly_production_sum

    # Total of operational cost
    monthly_operational_sum = monthly_marketing_0['sum'] + monthly_logistic_0['sum'] + monthly_operation_misc_0['sum']

    # Total Administrative cost
    monthly_administration_sum = monthly_office_needs_0['sum'] + monthly_salary_0['sum'] + monthly_rent_0['sum'] + monthly_administration_misc_0['sum']

    # Operational cost + administrative cost
    monthly_business_load_sum = monthly_operational_sum + monthly_administration_sum

    # NETT profit
    monthly_nett_profit = monthly_gross_profit - monthly_business_load_sum

    data = {
        'start_date': start_date,
        'end_date': end_date,
        'company_name': company_name,
        'get_previous_month': get_previous_month,
        'current_month': months[get_current_month],

        'monthly_income': monthly_income,

        'monthly_raw_material': monthly_raw_material,
        'monthly_wip': monthly_wip,
        'monthly_finished_goods': monthly_finished_goods,
        'monthly_production_misc': monthly_production_misc,
        'monthly_production_sum': format_float_production_sum,

        'monthly_gross_profit': monthly_gross_profit,

        'monthly_marketing': monthly_marketing,
        'monthly_logistic': monthly_logistic,
        'monthly_operation_misc': monthly_operation_misc,
        'monthly_operational_sum': monthly_operational_sum,

        'monthly_office_needs': monthly_office_needs,
        'monthly_salary': monthly_salary,
        'monthly_rent': monthly_rent,
        'monthly_administration_misc': monthly_administration_misc,
        'monthly_administration_sum': monthly_administration_sum,

        'monthly_business_load_sum': monthly_business_load_sum,

        'monthly_nett_profit': monthly_nett_profit,
    }
    pdf = render_to_pdf('pdf/profit_loss_pdf.html', data)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')

        if start_date != None and end_date != None:
            filename = f'profit_loss-{start_date}-{end_date}.pdf'
        else:
            filename = f'profit_loss-{months[get_current_month-1]}.pdf'
        
        content = 'inline; filename="%s"' %(filename)
        download = request.GET.get('download')

        if download:
            content = 'attachment; filename="%s"' %(filename)
        response['Content-Disposition'] = content

        return response
    return HttpResponse('Not Found')
# End of export

@login_required
def register_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST or None)
        if product_form.is_valid():
            product_form_save = product_form.save(commit=False)
            product_form_save.username = request.user

            product_form_save.save()
            
            messages.success(request, 'Your product has been registered!')
            return redirect('register_product')
        else:
            messages.error(request, 'There\'s something wrong! Please try again.')
    else:
        product_form = ProductForm()
    content = {
        'product_form': product_form,
    }
    return render(request, 'books/register_product.html', content)

@login_required
def register_income(request):
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

                if income_form_save.additional_price is None:
                    income_form_save.additional_price = 0

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
            messages.success(request, 'Your data has been inputted!')
            return redirect('register_expense')
        else:
            messages.error(request, 'There\'s something wrong in your data!')
    else:
        expense_form = ExpenseForm()
    
    content = {
        'expense_form': expense_form,
        'expense_form_notification': expense_form_notification,
    }
    return render(request, 'books/register_expense.html', content)

@login_required
def list_of_income(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date != None and end_date != None and start_date != '' and end_date != '':
        if end_date < start_date:
            messages.error(request, 'Hey, you can\'t have end date bigger than start_date!')
        else:
            list_of_income = Journal.objects.filter(
                username=request.user.pk,
                book_category='Debit',
                date_added__range=(start_date, end_date)
            ).order_by(
                '-date_added'
            )

            # Data for chart
            income_data_last_30_days = Journal.objects.filter(
                username=request.user.pk,
                book_category='Debit',
                date_added__range=(start_date, end_date),
            ).values(
                'date_added'
            ).order_by(
                'date_added'
            ).annotate(
                sum=Sum('total')
            )
    else:
        # List all of the income
        list_of_income = Journal.objects.filter(
            username=request.user.pk,
            book_category='Debit'
        ).order_by(
            '-date_added'
        )

        # Data for chart
        income_data_last_30_days = Journal.objects.filter(
            username=request.user.pk,
            book_category='Debit'
        ).values(
            'date_added'
        ).order_by(
            'date_added'
        )[:30].annotate(
            sum=Sum('total')
        )
    
    # Paginator, to split page into several pages
    page = request.GET.get('page', 1)
    paginator = Paginator(list_of_income, 10) # split page per 10 items
    try:
        income_page = paginator.page(page)
    except PageNotAnInteger:
        income_page = paginator.page(1)
    except EmptyPage:
        income_page = paginator.page(paginator.num_pages)
    
    # Display only the six pages maximum from the current total pages of pagination
    index = income_page.number-1 # -1 because index start from 0
    max_index = len(paginator.page_range)
    start_index = index-3 if index>=3 else 0
    end_index = index+3 if index<=max_index-3 else max_index

    # Make a list to be looped with for loop
    page_range = list(paginator.page_range)[start_index:end_index]

    # Get month
    get_current_month = timezone.now().month
    
    # Convert month's number to the name of the month
    # timezone.now() by default return number
    months = {}
    list_of_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    for i, j in zip(range(1, 13), list_of_months):
        months[i] = j

    content = {
        'paginate': income_page,
        'page_range': page_range,
        'income_chart_last_30_days': income_data_last_30_days,

        'start_date': start_date,
        'end_date': end_date,
        'month': months[get_current_month],
    }
    return render(request, 'books/list_of_income.html', content)

@login_required
def list_of_expense(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date != None and start_date != '' and end_date != None and end_date != '':
        if end_date < start_date:
            messages.error(request, 'Hey! You can\'t have start date bigger than end date!')
        else:
            list_of_expense = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                date_added__range=(start_date, end_date),
            ).order_by(
                '-date_added'
            )

            # Data for chart for the last 30 days
            expense_chart = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                date_added__range=(start_date, end_date),
            ).values(
                'date_added'
            ).order_by(
                'date_added'
            ).annotate(
                sum=Sum('total')
            )
    else:
        # List all of the expenses
        list_of_expense = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit'
        ).order_by('-date_added')

        # Data for chart for the last 30 days
        expense_chart = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
        ).values(
            'date_added'
        ).order_by(
            'date_added'
        )[:30].annotate(
            sum=Sum('total')
        )

    #Paginator, to split page into several pages
    page = request.GET.get('page', 1)
    paginator = Paginator(list_of_expense, 10) # split page per 10 items
    try:
        expense_page = paginator.page(page)
    except PageNotAnInteger:
        expense_page = paginator.page(1)
    except EmptyPage:
        expense_page = paginator.page(paginator.num_pages)

    # Display only the six pages maximum from the current total pages of pagination
    index = expense_page.number-1 # -1 because index start from 0
    max_index = len(paginator.page_range)
    start_index = index-3 if index>=3 else 0
    end_index = index+3 if index<=max_index-3 else max_index

    # Make a list to be looped with for loop
    page_range = list(paginator.page_range)[start_index:end_index]

    # Get month
    get_current_month = timezone.now().month
    
    # Convert month's number to the name of the month
    # timezone.now() by default return number
    months = {}
    list_of_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    for i, j in zip(range(1, 13), list_of_months):
        months[i] = j

    content = {
        'page_range': page_range,
        'paginate': expense_page,
        'expense_chart_last_30_days': expense_chart,

        'month': months[get_current_month],
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'books/list_of_expense.html', content)

@login_required
def list_of_product(request):
    keyword_search = request.GET.get('product_search')
    if keyword_search != None and keyword_search != '':
        product_obj = Product.objects.filter(
            username=request.user.pk,
            product_name__contain=keyword_search,
        ).order_by{
            '-product_name'
        }
    else:
        product_obj = Product.objects.filter(
            username=request.user.pk,
        ).order_by(
            '-product_name'
        )
    
    # Pagination, to split the page
    page = request.GET.get('page', 1)
    paginator = Paginator(product_obj, 10)
    try:
        product = paginator.page(page)
    except:
        product = paginator.page(1)
    except:
        product = paginator.page(paginator.num_pages)
    
    # Make the paginator only show three pages before and after current page
    index = product.number-1 # -1 because index start from 0
    max_index = len(paginator.page_range)
    start_index = index-3 if index>=3 else 0
    end_index = index+3 if index<=max_index-3 else max_index

    # Make a list to be looped with for loop
    page_range = list(paginator.page_range)[start_index:end_index]
    content = {
        'paginate': product,
        'page_range': page_range,

        'keyword_search': keyword_search,
    }
    return render(request, 'books/list_of_product.html', content)

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
        messages.error(request, 'You\'re not authorized to see this page')
        return redirect('list_of_income')
    else:
        obj = get_object_or_404(Journal, pk=pk)
        income_form = IncomeForm(request.user, request.POST or None, instance=obj)
        if income_form.is_valid():
            income_form_save = income_form.save(commit=False)

            if income_form_save.additional_price is None:
                income_form_save.additional_price = 0

            income_form_save.total = (income_form_save.price*income_form_save.quantity)+income_form_save.additional_price

            income_form_save.save()
            messages.success(request, 'Your data has been updated!')
            return redirect('list_of_income')

    content = {
        'income_form': income_form,
        'product_name': obj.product_name,
        'product_price': price,
    }
    return render(request, 'books/edit_income.html', content)

@login_required
def delete_income(request, pk):
    user_obj = get_object_or_404(Journal, pk=pk)
    if not request.user == user_obj.username:
        messages.error(request, 'You\'re not authorized to use this page')
        return redirect('list_of_income')
    else:
        income_obj = Journal.objects.get(pk=pk)
        if income_obj:
            income_obj.delete()
            return redirect('list_of_income')

    content = {
        'del_income': income_obj,
    }
    return render(request, 'books/delete_income.html', content)

@login_required
def delete_expense(request, pk):
    user_obj = get_object_or_404(Journal, pk=pk)
    if not request.user == user_obj.username:
        messages.error(request, 'You\'re not authorized to use this page')
        return redirect('list_of_expense')
    else:
        expense_obj = Journal.objects.get(pk=pk)
        if expense_obj:
            expense_obj.delete()
            return redirect('list_of_expense')

    content = {
        'del_expense': expense_obj,
    }
    return render(request, 'books/delete_expense.html', content)

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
        messages.error(request, 'You\'re not authorized to see this page')
        return redirect('list_of_expense')
    else:
        obj = get_object_or_404(Journal, pk=pk)
        expense_form = ExpenseForm(request.POST or None, instance=obj)
        if expense_form.is_valid():
            save_expense_form = expense_form.save(commit=False)

            save_expense_form.total = save_expense_form.quantity * save_expense_form.price
            save_expense_form.save()

            messages.success(request, 'Your data has been updated!')
            return redirect('list_of_expense')

    content = {
        'sub_categories': sub_categories,
        'expense_form': expense_form,
        'item_name': obj.item_name,
    }
    return render(request, 'books/edit_expense.html', content)

@login_required
def user_dashboard(request):
    # List of income and expense, latest 5 items
    expense_list_trim = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit'
    ).order_by('-date_added')[:5]

    income_list_trim = Journal.objects.filter(
        username=request.user.pk,
        book_category='Debit'
    ).order_by('-date_added')[:5]

    # Aggregate expense and income by latest 12 month
    expense_by_month = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit'
    ).annotate(
        month=TruncMonth('date_added')
    ).values(
        'month'
    ).order_by(
        'month'
    )[:12].annotate(
        sum=Sum('total')
    )

    income_by_month = Journal.objects.filter(
        username=request.user.pk,
        book_category='Debit',
    ).annotate(
        month=TruncMonth('date_added')
    ).values(
        'month'
    ).order_by(
        'month'
    )[:12].annotate(
        sum=Sum('total')
    )

    # Income and Expense for running month
    get_current_month = timezone.now().month

    # Convert month's number to the name of the month
    # timezone.now() by default return number
    months = {}
    list_of_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    for i, j in zip(range(1, 13), list_of_months):
        months[i] = j
    # End

    expense_in_running_month = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit',
        date_added__month=get_current_month
    ).aggregate(
        sum=Sum('total')
    )
    expense_in_running_month_per_day = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit',
        date_added__month=get_current_month,
    ).values(
        'date_added'
    ).order_by(
        'date_added'
    ).annotate(
        sum=Sum('total')
    )

    income_in_running_month = Journal.objects.filter(
        username=request.user.pk,
        book_category='Debit',
        date_added__month=get_current_month,
    ).aggregate(
        sum=Sum('total')
    )
    income_in_running_month_per_day = Journal.objects.filter(
        username=request.user.pk,
        book_category='Debit',
        date_added__month=get_current_month,
    ).values(
        'date_added'
    ).order_by(
        'date_added'
    ).annotate(
        sum=Sum('total')
    )

    # This to replace None type in dict into zero (0)
    def dict_clean(items):
        result = {}
        for key, value in items:
            if value == None:
                value = 0
            result[key] = value
        return result
    
    # To make sure object type Decimal serializable by JSON by changing it to float and format it to reselble Decimal
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                float_obj = float(obj)
                return float_obj
            return json.JSONEncoder.default(self, float_obj)
    
    # Re-format expense_in_running_month dict to JSON
    expense_dict = json.dumps(expense_in_running_month, cls=DecimalEncoder)
    expense_0 = json.loads(expense_dict, object_pairs_hook=dict_clean)

    # Re-format income_in_running_month dict to JSON
    income_dict = json.dumps(income_in_running_month, cls=DecimalEncoder)
    income_0 = json.loads(income_dict, object_pairs_hook=dict_clean)

    nett_profit = float(income_0['sum']) - float(expense_0['sum'])

    # You can achieve same result with this way below, but will stick with above ways as it already proofable by me  in any sort of situations
    # nett_profit_2 = float(income_by_month[0]['sum']) - float(expense_by_month[0]['sum'])
    # {:.2f}.format(...) mean to format the float-type object to show 2 decimals instead of one, but it became string as a result because it was a string formatting.
    profit_percentage = None
    if float(income_0['sum']) > 0:
        profit_percentage = (nett_profit / float(income_0['sum'])) * 100
        format_profit_percentage = '{:.2f}'.format(profit_percentage)
    else:
        profit_percentage = 0
        format_profit_percentage = '{:.2f}'.format(profit_percentage)

    content = {
        'month': months[get_current_month],

        'expense_list_trim': expense_list_trim,
        'income_list_trim': income_list_trim,

        'expense_by_month': expense_by_month,
        'income_by_month': income_by_month,

        'expense_in_running_month': expense_in_running_month,
        'expense_in_running_month_per_day': expense_in_running_month_per_day,

        'income_in_running_month': income_in_running_month,
        'income_in_running_month_per_day': income_in_running_month_per_day,

        
        # 'nett_profit_2': nett_profit_2,
        'nett_profit': nett_profit,
        'profit_percentage': format_profit_percentage,
    }
    return render(request, 'books/user_dashboard.html', content)

@login_required
def journal(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date != None and end_date != None and start_date != '' and end_date != '':
        if end_date < start_date:
            messages.error(request, 'You can\'t have end date bigger than start date')
        else:
            
            journal_all = Journal.objects.filter(
                username=request.user.pk,
                date_added__range=(start_date, end_date),
            ).order_by(
                'date_added',
            )
            
            expense_total = Journal.objects.filter(
                username=request.user.pk,
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )

            income_total = Journal.objects.filter(
                username=request.user.pk,
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )

            kredit_chart = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                date_added__range=(start_date, end_date),
            ).values(
                'date_added'
            ).order_by(
                'date_added'
            ).annotate(
                sum=Sum('total')
            )
            debit_chart = Journal.objects.filter(
                username=request.user.pk,
                book_category='Debit',
                date_added__range=(start_date, end_date),
            ).values(
                'date_added'
            ).order_by(
                'date_added'
            ).annotate(
                sum=Sum('total')
            )

            # In case one of income or expense not present in some dates, you might need to do this so it won't return NULL inside the charts
            journal_date_for_chart = Journal.objects.filter(
                username=request.user.pk,
                date_added__range=(start_date, end_date)
            ).values(
                'date_added'
            ).order_by(
                'date_added'
            ).annotate(
                sum=Sum('total')
            )
    else:
        journal_all = Journal.objects.filter(
            username=request.user.pk
        ).order_by('date_added')

        expense_total = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit'
        ).aggregate(
            sum=Sum('total')
        )

        income_total = Journal.objects.filter(
            username=request.user.pk,
            book_category='Debit',
        ).aggregate(
            sum=Sum('total')
        )

        kredit_chart = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit'
        ).values(
            'date_added'
        ).order_by(
            'date_added'
        )[:30].annotate(
            sum=Sum('total')
        )
        debit_chart = Journal.objects.filter(
            username=request.user.pk,
            book_category='Debit'
        ).values(
            'date_added'
        ).order_by(
            'date_added'
        )[:30].annotate(
            sum=Sum('total')
        )

        # In case one of income or expense not present in some dates, you might need to do this so it won't return NULL inside the charts
        journal_date_for_chart = Journal.objects.filter(
            username=request.user.pk,
        ).values(
            'date_added'
        ).order_by(
            'date_added'
        )[:30].annotate(
            sum=Sum('total')
        )

    # Pagination, to split the page
    page = request.GET.get('page', 1)
    paginator = Paginator(journal_all, 10)
    try:
        journal = paginator.page(page)
    except PageNotAnInteger:
        journal = paginator.page(1)
    except EmptyPage:
        journal = paginator.page(paginator.num_pages)
    
    # Make the paginator only show three pages before and after current page
    index = journal.number-1 # -1 because index start from 0
    max_index = len(paginator.page_range)
    start_index = index-3 if index>=3 else 0
    end_index = index+3 if index<=max_index-3 else max_index

    # Make a list to be looped with for loop
    page_range = list(paginator.page_range)[start_index:end_index]
    

    content = {
        'paginate': journal,
        'page_range': page_range,

        'start_date': start_date,
        'end_date': end_date,

        'expense_total': expense_total,
        'income_total': income_total,

        'kredit_chart': kredit_chart,
        'debit_chart': debit_chart,
        'journal_date_for_chart': journal_date_for_chart,
    }
    return render(request, 'books/journal.html', content)

@login_required
def profit_loss(request):
    company_name = get_object_or_404(CompanyDetail, username=request.user.pk)

    get_current_month = timezone.now().month

    # Convert month's number to the name of the month
    # timezone.now() by default return number
    months = {}
    list_of_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    for i, j in zip(range(1, 13), list_of_months):
        months[i] = j
    # End

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date != None and end_date != None and start_date != '' and start_date != '':
        if end_date < start_date:
            messages.error(request, 'End date can\'t be lower than start date')
        else:
            # Income in running month
            monthly_income = Journal.objects.filter(
                username=request.user.pk,
                book_category='Debit',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )

            # Inventory Value in running month
            monthly_raw_material = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Produksi',
                sub_category__sub_category='Bahan Mentah',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )
            monthly_wip = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Produksi',
                sub_category__sub_category='Barang Setengah Jadi',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )
            monthly_finished_goods = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Produksi',
                sub_category__sub_category='Barang Jadi',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )
            monthly_production_misc = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Produksi',
                sub_category__sub_category='Biaya Produksi Lainnya',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )

            # Operating Cost
            monthly_marketing = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Operasional',
                sub_category__sub_category='Biaya Pemasaran',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )
            monthly_logistic = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Operasional',
                sub_category__sub_category='Transportasi / Logistik',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )
            monthly_operation_misc = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Operasional',
                sub_category__sub_category='Biaya Operasional Lainnya',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )

            # Administration Cost
            monthly_office_needs = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Administrasi',
                sub_category__sub_category='Kebutuhan Kantor',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )
            monthly_salary = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Administrasi',
                sub_category__sub_category='Gaji Karyawan',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )
            monthly_rent = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Administrasi',
                sub_category__sub_category='Biaya Sewa',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )
            monthly_administration_misc = Journal.objects.filter(
                username=request.user.pk,
                book_category='Kredit',
                category__category='Biaya Administrasi',
                sub_category__sub_category='Biaya Administrasi Lainnya',
                date_added__range=(start_date, end_date),
            ).aggregate(
                sum=Sum('total')
            )
    else:
        # Income in running month
        monthly_income = Journal.objects.filter(
            username=request.user.pk,
            book_category='Debit',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )

        # Inventory Value in running month
        monthly_raw_material = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Bahan Mentah',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_wip = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Barang Setengah Jadi',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_finished_goods = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Barang Jadi',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_production_misc = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Produksi',
            sub_category__sub_category='Biaya Produksi Lainnya',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )

        # Operating Cost
        monthly_marketing = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Operasional',
            sub_category__sub_category='Biaya Pemasaran',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_logistic = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Operasional',
            sub_category__sub_category='Transportasi / Logistik',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_operation_misc = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Operasional',
            sub_category__sub_category='Biaya Operasional Lainnya',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )

        # Administration Cost
        monthly_office_needs = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Kebutuhan Kantor',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_salary = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Gaji Karyawan',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_rent = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Biaya Sewa',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )
        monthly_administration_misc = Journal.objects.filter(
            username=request.user.pk,
            book_category='Kredit',
            category__category='Biaya Administrasi',
            sub_category__sub_category='Biaya Administrasi Lainnya',
            date_added__month=get_current_month-1,
        ).aggregate(
            sum=Sum('total')
        )

    # This to replace None type in dict into zero (0)
    def dict_clean(items):
        result = {}
        for key, value in items:
            if value == None:
                value = 0
            result[key] = value
        return result
    
    # To make sure object type Decimal serializable by JSON by changing it to float and format it to reselble Decimal
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                float_obj = float(obj)
                return float_obj
            return json.JSONEncoder.default(self, float_obj)

    # Re-format income
    income_dict = json.dumps(monthly_income, cls=DecimalEncoder)
    monthly_income_0 = json.loads(income_dict, object_pairs_hook=dict_clean)

    # Re-format production cost
    raw_material_dict = json.dumps(monthly_raw_material, cls=DecimalEncoder)
    monthly_raw_material_0 = json.loads(raw_material_dict, object_pairs_hook=dict_clean)

    wip_dict = json.dumps(monthly_wip, cls=DecimalEncoder)
    monthly_wip_0 = json.loads(wip_dict, object_pairs_hook=dict_clean)

    finished_goods_dict = json.dumps(monthly_finished_goods, cls=DecimalEncoder)
    monthly_finished_goods_0 = json.loads(finished_goods_dict, object_pairs_hook=dict_clean)

    misc_production_dict = json.dumps(monthly_production_misc, cls=DecimalEncoder)
    monthly_production_misc_0 = json.loads(misc_production_dict, object_pairs_hook=dict_clean)

    # Re-format operational cost
    marketing_dict = json.dumps(monthly_marketing, cls=DecimalEncoder)
    monthly_marketing_0 = json.loads(marketing_dict, object_pairs_hook=dict_clean)

    logistic_dict = json.dumps(monthly_logistic, cls=DecimalEncoder)
    monthly_logistic_0 = json.loads(logistic_dict, object_pairs_hook=dict_clean)

    misc_operational_dict = json.dumps(monthly_operation_misc, cls=DecimalEncoder)
    monthly_operation_misc_0 = json.loads(misc_operational_dict, object_pairs_hook=dict_clean)

    # Re-format administration cost
    office_needs_dict = json.dumps(monthly_office_needs, cls=DecimalEncoder)
    monthly_office_needs_0 = json.loads(office_needs_dict, object_pairs_hook=dict_clean)

    salary_dict = json.dumps(monthly_salary, cls=DecimalEncoder)
    monthly_salary_0 = json.loads(salary_dict, object_pairs_hook=dict_clean)

    rent_dict = json.dumps(monthly_rent, cls=DecimalEncoder)
    monthly_rent_0 = json.loads(rent_dict, object_pairs_hook=dict_clean)

    misc_administration_dict = json.dumps(monthly_administration_misc, cls=DecimalEncoder)
    monthly_administration_misc_0 = json.loads(misc_administration_dict, object_pairs_hook=dict_clean)

    # To sum it you need to convert it to float first so you can do mathematical operations with the result
    # The end result of formatting the float was a string, so don't use formatted result if you want to do mathematical operations
    monthly_production_sum = monthly_raw_material_0['sum'] + monthly_wip_0['sum'] + monthly_finished_goods_0['sum'] + monthly_production_misc_0['sum'] # a float
    format_float_production_sum = '{:.2f}'.format(monthly_production_sum) # a string

    # Format monthly_income data type to float
    monthly_income_sum = float(monthly_income_0['sum']) # a float

    # Gross Profit = monthly_income - monthly_production_sum
    # type float
    monthly_gross_profit = monthly_income_sum - monthly_production_sum

    # Total of operational cost
    monthly_operational_sum = monthly_marketing_0['sum'] + monthly_logistic_0['sum'] + monthly_operation_misc_0['sum']

    # Total Administrative cost
    monthly_administration_sum = monthly_office_needs_0['sum'] + monthly_salary_0['sum'] + monthly_rent_0['sum'] + monthly_administration_misc_0['sum']

    # Operational cost + administrative cost
    monthly_business_load_sum = monthly_operational_sum + monthly_administration_sum

    # NETT profit
    monthly_nett_profit = monthly_gross_profit - monthly_business_load_sum

    content = {
        'current_month': months[get_current_month],
        'previous_month': months[get_current_month-1],
        'company_name': company_name,
        'start_date': start_date,
        'end_date': end_date,

        'monthly_income': monthly_income,

        'monthly_raw_material': monthly_raw_material,
        'monthly_wip': monthly_wip,
        'monthly_finished_goods': monthly_finished_goods,
        'monthly_production_misc': monthly_production_misc,
        'monthly_production_sum': format_float_production_sum,

        'monthly_gross_profit': monthly_gross_profit,

        'monthly_marketing': monthly_marketing,
        'monthly_logistic': monthly_logistic,
        'monthly_operation_misc': monthly_operation_misc,
        'monthly_operational_sum': monthly_operational_sum,

        'monthly_office_needs': monthly_office_needs,
        'monthly_salary': monthly_salary,
        'monthly_rent': monthly_rent,
        'monthly_administration_misc': monthly_administration_misc,
        'monthly_administration_sum': monthly_administration_sum,

        'monthly_business_load_sum': monthly_business_load_sum,

        'monthly_nett_profit': monthly_nett_profit,
    }
    return render(request, 'books/profit_loss.html', content)
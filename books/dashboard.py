from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Count
from django.utils import timezone

from django.core.exceptions import PermissionDenied

from decimal import Decimal

from .models import Journal, Product

import json

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

        'nett_profit': nett_profit,
        'profit_percentage': format_profit_percentage,
    }
    return render(request, 'books/user_dashboard.html', content)

# Function to limit page to superuser only from backend
def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner

@login_required
@superuser_only
def admin_dashboard(request):
    # All dates for journal for chart
    journal_date = Journal.objects.all().annotate(
        month=TruncMonth('date_added')
    ).values(
        'month'
    ).order_by(
        'month'
    )[:12].annotate(
        sum=Count('month')
    )

    # Aggregate the expenses for the last 12 months
    expense_by_month = Journal.objects.filter(
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

    # Aggregate the incomes for the last 12 months
    income_by_month = Journal.objects.filter(
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

    # Aggregate total number of products and user group by product's type
    goods_business_count = Product.objects.filter(
        # You need to use the value of the variable inside models when you filter the ModelChoice
        types='Barang'
    ).values(
        'username__username',
    ).annotate(
        products=Count('username'),
    ).order_by()[:21]

    user_selling_goods = Product.objects.filter(
        types='Barang',
    ).values(
        'username',
    ).distinct().count()

    number_of_goods_listed = Product.objects.filter(
        types='Barang',
    ).values(
        'username',
    ).count()

    services_business_count = Product.objects.filter(
        # You need to use the value of the variable inside models when you filter the ModelChoice
        types='Jasa'
    ).values(
        'username__username',
    ).annotate(
        products=Count('username'),
    ).order_by()[:21]

    user_selling_services = Product.objects.filter(
        types='Jasa',
    ).values(
        'username'
    ).distinct().count()

    number_of_services_listed = Product.objects.filter(
        types='Jasa',
    ).values(
        'username'
    ).count()

    # Sum all of the transactions
    global_transactions = Journal.objects.all().values(
        'total'
    ).aggregate(
        sum=Sum('total')
    )

    # Sum all of the expenses
    global_expenses = Journal.objects.filter(
        book_category='Kredit',
    ).values(
        'total'
    ).aggregate(
        sum=Sum('total')
    )

    # Sum all of the income
    global_incomes = Journal.objects.filter(
        book_category='Debit',
    ).values(
        'total'
    ).aggregate(
        sum=Sum('total')
    )
    
    content = {
        'goods_business_count': goods_business_count,
        'user_selling_goods': user_selling_goods,
        'number_of_goods_listed': number_of_goods_listed,

        'services_business_count': services_business_count,
        'user_selling_services': user_selling_services,
        'number_of_services_listed': number_of_services_listed,

        'income_by_month': income_by_month,
        'expense_by_month': expense_by_month,
        'journal_date': journal_date,

        'global_transactions': global_transactions,
        'global_expenses': global_expenses,
        'global_incomes': global_incomes,
    }
    return render(request, 'books/admin_dashboard.html', content)
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.core.paginator import (
    Paginator, EmptyPage, PageNotAnInteger
)

from .models import Journal, Product

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

    # Catch the latest paginated page the user visit before editing the data, and store it to the session
    # The number of page inside request.GET.get() must be converted into string so it can be concatinated
    request.session['previous_page'] = request.path_info + '?page=' + request.GET.get('page', '1')

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
    
    expense_in_running_month = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit',
        date_added__month=get_current_month,
    ).aggregate(
        sum=Sum('total')
    )

    num_of_items_bought_in_running_month = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit',
        date_added__month=get_current_month,
    ).aggregate(
        sum=Sum('quantity')
    )

    total_expense_filtered = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit',
        date_added__range=(start_date, end_date),
    ).aggregate(
        sum=Sum('total')
    )

    total_num_items_bought_filtered = Journal.objects.filter(
        username=request.user.pk,
        book_category='Kredit',
        date_added__range=(start_date, end_date),
    ).aggregate(
        sum=Sum('quantity')
    )

    # Catch the latest paginated page the user visit before editing the data, and store it to the session
    # The number of page inside request.GET.get() must be converted into string so it can be concatinated
    request.session['previous_page'] = request.path_info + '?page=' + request.GET.get('page', '1')

    content = {
        'page_range': page_range,
        'paginate': expense_page,
        'expense_chart_last_30_days': expense_chart,

        'month': months[get_current_month],
        'start_date': start_date,
        'end_date': end_date,

        'expense_in_running_month': expense_in_running_month,
        'num_of_item_bought_in_running)month': num_of_items_bought_in_running_month,
        'total_expense_filtered': total_expense_filtered,
        'total_num_items_filtered': total_num_items_bought_filtered,
    }
    return render(request, 'books/list_of_expense.html', content)

@login_required
def list_of_product(request):
    keyword_search = request.GET.get('product_search')
    if keyword_search != None and keyword_search != '':
        product_obj = Product.objects.filter(
            username=request.user.pk,
            product_name__icontains=keyword_search,
        ).order_by(
            'product_name'
        )
    else:
        product_obj = Product.objects.filter(
            username=request.user.pk,
        ).order_by(
            'product_name'
        )
    
    # Pagination, to split the page
    page = request.GET.get('page', 1)
    paginator = Paginator(product_obj, 10)
    try:
        product = paginator.page(page)
    except PageNotAnInteger:
        product = paginator.page(1)
    except EmptyPage:
        product = paginator.page(paginator.num_pages)
    
    # Make the paginator only show three pages before and after current page
    index = product.number-1 # -1 because index start from 0
    max_index = len(paginator.page_range)
    start_index = index-3 if index>=3 else 0
    end_index = index+3 if index<=max_index-3 else max_index

    # Make a list to be looped with for loop
    page_range = list(paginator.page_range)[start_index:end_index]

    # Catch the latest paginated page the user visit before editing the data, and store it to the session
    # The number of page inside request.GET.get() must be converted into string so it can be concatinated
    request.session['previous_page'] = request.path_info + '?page=' + request.GET.get('page', '1')

    content = {
        'paginate': product,
        'page_range': page_range,

        'keyword_search': keyword_search,
    }
    return render(request, 'books/list_of_product.html', content)
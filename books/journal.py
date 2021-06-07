from django.shortcuts import render

from django.db.models import Sum, Count
from django.core.paginator import (
    Paginator, EmptyPage, PageNotAnInteger
)

from django.contrib.auth.decorators import login_required

from .models import Journal

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
                '-date_added',
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
        ).order_by('-date_added')

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
from django.utils import timezone
from django.shortcuts import render, get_object_or_404

from django.db.models import Sum, Count

from django.contrib.auth.decorators import login_required

from decimal import Decimal

from .models import Journal
from user.models import CompanyDetail

import json


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
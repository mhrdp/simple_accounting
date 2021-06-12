from django.shortcuts import render

from .models import Product, SubCategory

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
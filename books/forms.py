from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField

from datetime import date
from .models import Journal, ExpenseCategory, SubCategory, Product

class IncomeForm(forms.ModelForm):
    date_added = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class':'form-control form-control-sm',
                'type':'date'
                }
        ),
        initial = date.today,
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class':'form-control form-control-sm',}
        ),
        initial = 0,
    )

    price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-control form-control-sm',
                'placeholder': 'Harga...',
                }
        )
    )
    additional_price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-control form-control-sm',
                'placeholder': 'Harga Tambahan...',
                }
        ),
        required=False,
        initial=0
    )
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class':'form-control form-control-sm',
                'placeholder': 'Notes...',
                }
        ),
        required=False,
    )
    class Meta:
        model = Journal
        fields = [
            'date_added', 'product_name', 'quantity', 'price', 
            'additional_price', 'notes'
        ]
    
    # This to filter the product name based on user
    # You need to rewrite a function inside ModelForm to be able to fetch requested user in the ModelForm, couse apparently you can't do it normally like in views.py
    # The requirement for this was to call request.user when calling the form in views.py, in this case IncomeForm(request.user, ...)
    def __init__(self, user, *args, **kwargs):
        super(IncomeForm, self).__init__(*args, **kwargs)
        self.fields['product_name'] = forms.ModelChoiceField(
            queryset=Product.objects.filter(username=user).order_by('product_name'),
            widget=forms.Select(
                attrs={
                    'class':'form-control form-control-sm',
                    'placeholder': 'Nama Produk...',
                    }
            ),
            required=True,
        )

class ExpenseForm(forms.ModelForm):
    date_added = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class':'form-control form-control-sm',
                'type':'date',
                }
        ),
        initial=date.today
    )
    
    item_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control form-control-sm',
                'placeholder': 'Nama Barang...',
                }
        )
    )
    category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all().order_by('category'),
        widget=forms.Select(
            attrs={
                'class':'form-control form-control-sm',
                'placeholder': 'Kategori...',
                }
        )
    )
    sub_category = forms.ModelChoiceField(
        queryset=SubCategory.objects.none(),
        widget=forms.Select(
            attrs={
                'class':'form-control form-control-sm',
                'placeholder': 'Kategori Tambahan...',
                }
        )
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class':'form-control form-control-sm',}
        ),
        initial = 0,
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-control form-control-sm',
                'placeholder': 'Harga...',
                }
        )
    )
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class':'form-control form-control-sm',
                'placeholder': 'Catatan Tambahan...'
                }
        ),
        required=False,
    )
    class Meta:
        model = Journal
        fields = [
            'date_added', 'item_name', 'category', 'sub_category', 
            'quantity', 'price', 'notes'
        ]

    # This is to get sub_category data based on its foreign key
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_category'].queryset = SubCategory.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(
                    category_id=category_id
                ).order_by('-sub_category')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['sub_category'].queryset = SubCategory.objects.filter(
                category_id=self.instance.category_id
            )

class ProductForm(forms.ModelForm):
    goods = 'Barang'
    services = 'Jasa'
    PRODUCT_TYPES = [
        (goods, 'Barang'),
        (services, 'Jasa'),
    ]

    product_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder': 'Nama Produk...',
                }
        )
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-control',
                'placeholder': 'Harga...',
                }
        )
    )

    types = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class':'form-control'}
        ),
        choices=PRODUCT_TYPES,
    )

    class Meta:
        model = Product
        fields = {
            'product_name', 'price', 'types'
        }
from django import forms
from django.conf import settings

from datetime import date
from .models import Journal, ExpenseCategory, SubCategory, Product

class IncomeForm(forms.ModelForm):
    date_added = forms.DateField(
        widget=forms.SelectDateWidget(
            attrs={'class':'form-control'}
        ),
        initial=date.today,
    )
    product_name = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={'class':'form-control'}
        )
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class':'form-control'}
        )
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={'class':'form-control'}
        )
    )
    additional_price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={'class':'form-control'}
        )
    )
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={'class':'form-control'}
        )
    )
    class Meta:
        model = Journal
        fields = [
            'date_added', 'product_name', 'quantity', 'price', 
            'additional_price', 'notes'
        ]

class ExpenseForm(forms.ModelForm):
    date_added = forms.DateField(
        widget=forms.SelectDateWidget(
            attrs={'class':'form-control'}
        ),
        initial=date.today
    )
    item_name = forms.CharFIeld(
        widget=forms.TextInput(
            attrs={'class':'form-control'}
        )
    )
    category = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={'class':'form-control'}
        )
    )
    sub_category = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={'class':'form-control'}
        )
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class':'form-control'}
        )
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={'class':'form-control'}
        )
    )
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={'class':'form-control'}
        )
    )
    class Meta:
        model = Journal
        fields = [
            'date_added', 'item_name', 'category', 'sub_category', 
            'quantity', 'price', 'notes'
        ]

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
    product_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class':'form-control'}
        )
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={'class':'form-control'}
        )
    )
    class Meta:
        model = Product
        fields = {
            'product_name', 'price'
        }
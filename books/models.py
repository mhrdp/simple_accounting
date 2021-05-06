from django.db import models
from django.conf import settings

from user.models import Industry

from datetime import date

# Create your models here.

# Dependent dropdown model
class ExpenseCategory(models.Model):
    category = models.CharField(max_length=55)

    def __str__(self):
        return self.category

class SubCategory(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    sub_category = models.CharField(max_length=55)

    def __str__(self):
        return self.sub_category
# End of dependent dropdown model

class Product(models.Model):
    username = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, null=True
    )

    product_name = models.CharField(max_length=155, null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product_name
    
class Journal(models.Model):
    # REMINDER !!!
    # This models kind of unsecure because it allows user to pass a NULL values for some fields if they rewrote the front-end code from developer console, because some of the authentication system only limited to the front-end side.
    # Possibly need a better solution for the future to merge two models into one table inside the template (not at the DB side of thing), instead of combining all of it into one models like this
    # Or maybe use additional validation in views.py to make sure the required submitted fields does not empty

    DB = 'Debit'
    CR = 'Kredit'
    BOOK_TYPE = [
        (DB, 'Debit'),
        (CR, 'Kredit'),
    ]

    date_added = models.DateField(
        default=date.today
    )
    username = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT)

    # Income Specific
    product_name = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=False)
    additional_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0)

    # Expense Specific
    item_name = models.CharField(max_length=155, blank=False)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.PROTECT,
        blank=False, null=True
        )
    sub_category = models.ForeignKey(
        SubCategory, on_delete=models.PROTECT,
        blank=False, null=True
        )

    # General
    quantity = models.IntegerField(null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    book_category = models.CharField(
        max_length=25,
        choices=BOOK_TYPE,
        )
    notes = models.TextField(max_length=255, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.book_category
    
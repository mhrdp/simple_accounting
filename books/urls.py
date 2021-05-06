from django.urls import path
from django.conf.urls import url

from . import views as books_views

urlpatterns = [
    path('input/product/new/', books_views.register_product, name='register_product'),
    path('input/income/new/', books_views.register_income, name='register_income'),
    path('input/expense/new/', books_views.register_expense, name='register_expense'),

    path('books/product/list/', books_views.list_of_product, name='list_of_product'),
    
    path('books/expense/list/', books_views.list_of_expense, name='list_of_expense'),
    path(r'books/expense/edit/<int:pk>/', books_views.edit_expense, name='edit_expense'),
    path(r'books/expense/delete/<int:pk>/', books_views.delete_expense, name='delete_expense'),

    path('books/income/list/', books_views.list_of_income, name='list_of_income'),
    path(r'books/income/edit/<int:pk>/', books_views.edit_income, name='edit_income'),
    path(r'books/income/delete/<int:pk>/', books_views.delete_income, name='delete_income'),

    path('books/journal/', books_views.journal, name='journal'),
    path('books/profit-loss/', books_views.profit_loss, name='profit_loss'),

    path('ajax/expense-dropdown/', books_views.expense_dropdown_ajax, name='dropdown_ajax'),
    path('ajax/income-autofill/', books_views.income_form_autofill_ajax, name='income_form_autofill'),

    path('books/income/list/filter', books_views.income_filter_by_date, name='income_filter_by_date'),
    path('books/expense/list/filter/', books_views.expense_filter_by_date, name='expense_filter_by_date'),

    path('dashboard/', books_views.user_dashboard, name='user_dashboard'),

    url('books/journal/export/csv/', books_views.export_journal_to_csv, name='journal_to_csv'),
    url('books/ledger/pdf/', books_views.export_profit_loss_to_pdf, name='profit_loss_to_pdf'),
]

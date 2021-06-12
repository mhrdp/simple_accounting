from django.urls import path
from django.conf.urls import url

from . import views as books_views
from . import dashboard
from . import journal
from . import income_statement
from . import input
from . import books_list
from . import books_edit
from . import export

urlpatterns = [
    # input
    path('input/product/new/', input.register_product, name='register_product'),
    path('input/income/new/', input.register_income, name='register_income'),
    path('input/expense/new/', input.register_expense, name='register_expense'),

    # books list
    path('books/product/list/', books_list.list_of_product, name='list_of_product'),
    path('books/expense/list/', books_list.list_of_expense, name='list_of_expense'),
    path('books/income/list/', books_list.list_of_income, name='list_of_income'),

    # books edit
    path(r'books/product/edit/<int:pk>/', books_edit.edit_product, name='edit_product'),
    path(r'books/product/delete/<int:pk>/', books_edit.delete_product, name='delete_product'),

    path(r'books/expense/edit/<int:pk>/', books_edit.edit_expense, name='edit_expense'),
    path(r'books/expense/delete/<int:pk>/', books_edit.delete_expense, name='delete_expense'),

    path(r'books/income/edit/<int:pk>/', books_edit.edit_income, name='edit_income'),
    path(r'books/income/delete/<int:pk>/', books_edit.delete_income, name='delete_income'),

    # journal and profit loss
    path('books/journal/', journal.journal, name='journal'),
    path('books/profit-loss/', income_statement.profit_loss, name='profit_loss'),

    # dashboards
    path('dashboard/', dashboard.user_dashboard, name='user_dashboard'),
    path('admin/dashboard/', dashboard.admin_dashboard, name='admin_dashboard'),

    # export
    url('books/journal/export/csv/', export.export_journal_to_csv, name='journal_to_csv'),
    url('books/ledger/pdf/', export.export_profit_loss_to_pdf, name='profit_loss_to_pdf'),

    # misc
    path('ajax/expense-dropdown/', books_views.expense_dropdown_ajax, name='dropdown_ajax'),
    path('ajax/income-autofill/', books_views.income_form_autofill_ajax, name='income_form_autofill'),
]

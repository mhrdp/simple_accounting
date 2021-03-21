from django.urls import path

from . import views as books_views

urlpatterns = [
    path('input/product/new/', books_views.register_product, name='register_product'),
    path('input/income/new/', books_views.register_income, name='register_income'),
    path('input/expense/new/', books_views.register_expense, name='register_expense'),

    path('books/expense/list/', books_views.list_of_expense, name='list_of_expense'),
    path(r'books/expense/edit/<int:pk>/', books_views.edit_expense, name='edit_expense'),

    path('books/income/list/', books_views.list_of_income, name='list_of_income'),
    path(r'books/income/edit/<int:pk>/', books_views.edit_income, name='edit_income'),

    path('books/dropdown-ajax/', books_views.expense_dropdown_ajax, name='dropdown_ajax'),
    path('books/income-autofill-ajax/', books_views.income_form_autofill_ajax, name='income_form_autofill'),

    path('books/', books_views.books_options, name='books_options'),
    path('input/', books_views.input_options, name='input_options'),

    path('dashboard/', books_views.user_dashboard, name="user_dashboard"),
]

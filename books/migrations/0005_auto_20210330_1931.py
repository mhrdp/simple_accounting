# Generated by Django 3.1.7 on 2021-03-30 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_auto_20210330_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='product_name',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='books.product'),
        ),
    ]

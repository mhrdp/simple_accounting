# Generated by Django 3.1.7 on 2021-05-06 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_auto_20210506_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='product_name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='books.product'),
        ),
    ]
# Generated by Django 3.1.7 on 2021-05-17 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0013_auto_20210517_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='types',
            field=models.CharField(choices=[('Goods', 'Barang'), ('Services', 'Jasa')], default='Goods', max_length=50),
        ),
    ]

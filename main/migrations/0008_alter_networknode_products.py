# Generated by Django 4.2 on 2025-04-11 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_networknode_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='networknode',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='network_nodes', to='main.product', verbose_name='Продукты'),
        ),
    ]

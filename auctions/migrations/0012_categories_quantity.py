# Generated by Django 4.0.6 on 2022-08-16 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_listing_active_alter_listing_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='categories',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]

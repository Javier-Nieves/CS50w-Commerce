# Generated by Django 4.0.6 on 2022-08-12 14:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_remove_listing_watchlist_listing_watch'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='watch',
        ),
        migrations.AddField(
            model_name='listing',
            name='watching',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='listing',
            name='seller',
            field=models.ForeignKey(max_length=64, on_delete=django.db.models.deletion.CASCADE, related_name='MyListings', to=settings.AUTH_USER_MODEL),
        ),
    ]

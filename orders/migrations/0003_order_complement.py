# Generated by Django 3.1 on 2021-07-11 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20210711_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='complement',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]

# Generated by Django 2.2.12 on 2020-06-18 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledgerdata',
            name='bill_ammount',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ledgerdata',
            name='frieght',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ledgerdata',
            name='pcs_mtr',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

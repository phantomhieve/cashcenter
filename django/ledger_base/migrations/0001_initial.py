# Generated by Django 3.0.5 on 2020-08-11 16:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LedgerDataBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('l_r_no', models.CharField(max_length=255)),
                ('l_r_date', models.DateField(blank=True, null=True)),
                ('bale_no', models.CharField(blank=True, max_length=255, null=True)),
                ('supplier', models.CharField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('item', models.CharField(blank=True, max_length=255, null=True)),
                ('pcs_mtr', models.FloatField(blank=True, null=True)),
                ('price', models.FloatField(blank=True, default=0)),
                ('weight', models.CharField(blank=True, max_length=255, null=True)),
                ('frieght', models.FloatField(blank=True, null=True)),
                ('transport', models.CharField(blank=True, max_length=255, null=True)),
                ('delivery', models.DateField(blank=True, null=True)),
                ('reciept', models.CharField(blank=True, max_length=255, null=True)),
                ('remark', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.BooleanField(default=False)),
                ('hsn_code', models.CharField(blank=True, max_length=255, null=True)),
                ('bill_ammount', models.FloatField(blank=True, null=True)),
                ('no_of_bale', models.IntegerField(blank=True, default=1)),
                ('approved', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['l_r_date', 'id'],
                'unique_together': {('user', 'l_r_no')},
            },
        ),
    ]
# Generated by Django 2.2.12 on 2020-05-26 21:41

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
            name='UserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop', models.CharField(max_length=50)),
                ('main_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='main_user', to=settings.AUTH_USER_MODEL)),
                ('primary_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='primary_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

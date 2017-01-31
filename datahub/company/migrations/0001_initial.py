# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-17 07:51
from __future__ import unicode_literals

import datahub.core.mixins
import datahub.core.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Advisor',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=255, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            bases=(models.Model, ),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BusinessType',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='CompaniesHouseCompany',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('registered_address_1', models.CharField(max_length=255)),
                ('registered_address_2', models.CharField(blank=True, max_length=255, null=True)),
                ('registered_address_3', models.CharField(blank=True, max_length=255, null=True)),
                ('registered_address_4', models.CharField(blank=True, max_length=255, null=True)),
                ('registered_address_town', models.CharField(max_length=255)),
                ('registered_address_county', models.CharField(blank=True, max_length=255, null=True)),
                ('registered_address_postcode', models.CharField(blank=True, max_length=255, null=True)),
                ('company_number', models.CharField(db_index=True, max_length=255, null=True, unique=True)),
                ('company_category', models.CharField(blank=True, max_length=255)),
                ('company_status', models.CharField(blank=True, max_length=255)),
                ('sic_code_1', models.CharField(blank=True, max_length=255)),
                ('sic_code_2', models.CharField(blank=True, max_length=255)),
                ('sic_code_3', models.CharField(blank=True, max_length=255)),
                ('sic_code_4', models.CharField(blank=True, max_length=255)),
                ('uri', models.CharField(blank=True, max_length=255)),
                ('incorporation_date', models.DateField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('archived', models.BooleanField(default=False)),
                ('archived_on', models.DateTimeField(null=True)),
                ('archived_reason', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=255)),
                ('registered_address_1', models.CharField(max_length=255)),
                ('registered_address_2', models.CharField(blank=True, max_length=255, null=True)),
                ('registered_address_3', models.CharField(blank=True, max_length=255, null=True)),
                ('registered_address_4', models.CharField(blank=True, max_length=255, null=True)),
                ('registered_address_town', models.CharField(max_length=255)),
                ('registered_address_county', models.CharField(blank=True, max_length=255, null=True)),
                ('registered_address_postcode', models.CharField(blank=True, max_length=255, null=True)),
                ('company_number', models.CharField(blank=True, max_length=255, null=True)),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('alias', models.CharField(blank=True, help_text='Trading name', max_length=255, null=True)),
                ('lead', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('trading_address_1', models.CharField(blank=True, max_length=255, null=True)),
                ('trading_address_2', models.CharField(blank=True, max_length=255, null=True)),
                ('trading_address_3', models.CharField(blank=True, max_length=255, null=True)),
                ('trading_address_4', models.CharField(blank=True, max_length=255, null=True)),
                ('trading_address_town', models.CharField(blank=True, max_length=255, null=True)),
                ('trading_address_county', models.CharField(blank=True, max_length=255, null=True)),
                ('trading_address_postcode', models.CharField(blank=True, max_length=255, null=True)),
                ('account_manager', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='companies', to=settings.AUTH_USER_MODEL)),
                ('archived_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('business_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.BusinessType')),
            ],
            options={
                'verbose_name_plural': 'companies',
            },
            bases=(datahub.core.mixins.KorbenSaveModelMixin, datahub.core.models.ArchivableModel),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('archived', models.BooleanField(default=False)),
                ('archived_on', models.DateTimeField(null=True)),
                ('archived_reason', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('primary', models.BooleanField()),
                ('telephone_countrycode', models.CharField(max_length=255)),
                ('telephone_number', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('address_same_as_company', models.BooleanField(default=False)),
                ('address_1', models.CharField(blank=True, max_length=255, null=True)),
                ('address_2', models.CharField(blank=True, max_length=255, null=True)),
                ('address_3', models.CharField(blank=True, max_length=255, null=True)),
                ('address_4', models.CharField(blank=True, max_length=255, null=True)),
                ('address_town', models.CharField(blank=True, max_length=255, null=True)),
                ('address_county', models.CharField(blank=True, max_length=255, null=True)),
                ('address_postcode', models.CharField(blank=True, max_length=255, null=True)),
                ('telephone_alternative', models.CharField(blank=True, max_length=255, null=True)),
                ('email_alternative', models.EmailField(blank=True, max_length=254, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(datahub.core.mixins.KorbenSaveModelMixin, datahub.core.models.ArchivableModel),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='EmployeeRange',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('archived', models.BooleanField(default=False)),
                ('archived_on', models.DateTimeField(null=True)),
                ('archived_reason', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('subject', models.TextField()),
                ('date_of_interaction', models.DateTimeField()),
                ('notes', models.TextField()),
                ('archived_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='company.Company')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='company.Contact')),
                ('dit_advisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(datahub.core.mixins.KorbenSaveModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='InteractionType',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='TurnoverRange',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='UKRegion',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='interaction',
            name='dit_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Team'),
        ),
        migrations.AddField(
            model_name='interaction',
            name='interaction_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.InteractionType'),
        ),
        migrations.AddField(
            model_name='interaction',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Service'),
        ),
        migrations.AddField(
            model_name='contact',
            name='address_country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.Country'),
        ),
        migrations.AddField(
            model_name='contact',
            name='advisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contact',
            name='archived_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contact',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='company.Company'),
        ),
        migrations.AddField(
            model_name='contact',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Role'),
        ),
        migrations.AddField(
            model_name='contact',
            name='teams',
            field=models.ManyToManyField(blank=True, to='company.Team'),
        ),
        migrations.AddField(
            model_name='contact',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Title'),
        ),
        migrations.AddField(
            model_name='company',
            name='employee_range',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.EmployeeRange'),
        ),
        migrations.AddField(
            model_name='company',
            name='export_to_countries',
            field=models.ManyToManyField(blank=True, null=True, related_name='company_export_to_countries', to='company.Country'),
        ),
        migrations.AddField(
            model_name='company',
            name='future_interest_countries',
            field=models.ManyToManyField(blank=True, null=True, related_name='company_future_interest_countries', to='company.Country'),
        ),
        migrations.AddField(
            model_name='company',
            name='registered_address_country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_company_related', related_query_name='(app_label)s_companys', to='company.Country'),
        ),
        migrations.AddField(
            model_name='company',
            name='sector',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Sector'),
        ),
        migrations.AddField(
            model_name='company',
            name='trading_address_country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_trading_address_country', to='company.Country'),
        ),
        migrations.AddField(
            model_name='company',
            name='turnover_range',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.TurnoverRange'),
        ),
        migrations.AddField(
            model_name='company',
            name='uk_region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.UKRegion'),
        ),
        migrations.AddField(
            model_name='companieshousecompany',
            name='registered_address_country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_companieshousecompany_related', related_query_name='(app_label)s_companieshousecompanys', to='company.Country'),
        ),
        migrations.AddField(
            model_name='advisor',
            name='dit_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Team'),
        ),
        migrations.AddField(
            model_name='advisor',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='advisor',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]

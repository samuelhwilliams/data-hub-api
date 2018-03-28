# Generated by Django 2.0.3 on 2018-03-27 09:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('metadata', '0002_add_sector_hierarchy'),
        ('investment', '0042_correct_spi_stage_log_created_on_and_ordering'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestmentProjectSPIReportConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('after_care_offered', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='metadata.Service')),
                ('client_proposal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='metadata.Service')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('project_manager_assigned', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='metadata.Service')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
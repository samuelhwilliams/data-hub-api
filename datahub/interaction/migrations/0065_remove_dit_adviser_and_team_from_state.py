# Generated by Django 2.2.3 on 2019-07-31 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0064_update_service_foreign_key'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='interaction',
                    name='dit_adviser',
                ),
                migrations.RemoveField(
                    model_name='interaction',
                    name='dit_team',
                ),
            ],
        ),
    ]

# Generated by Django 5.0.3 on 2024-04-10 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pdf_Extracter_app', '0002_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='PathInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icm', models.CharField(blank=True, max_length=50, null=True)),
                ('icm1', models.CharField(blank=True, max_length=50, null=True)),
                ('excel_download', models.CharField(blank=True, max_length=100, null=True)),
                ('file', models.CharField(blank=True, max_length=100000, null=True)),
                ('df1_json', models.CharField(blank=True, max_length=100000, null=True)),
                ('excel_path', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
    ]

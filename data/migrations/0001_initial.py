# Generated by Django 3.0 on 2020-09-09 14:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('cid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 're_category',
            },
        ),
        migrations.CreateModel(
            name='Morder',
            fields=[
                ('mid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('start_datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='建立时间')),
                ('re_datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='报销时间')),
            ],
            options={
                'db_table': 're_morder',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('sid', models.AutoField(primary_key=True, serialize=False)),
                ('ssid', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=20)),
                ('email', models.CharField(max_length=30)),
                ('passward', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 're_student',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('iid', models.AutoField(primary_key=True, serialize=False)),
                ('inum', models.IntegerField()),
                ('money', models.DecimalField(decimal_places=2, max_digits=6)),
                ('description', models.CharField(max_length=100)),
                ('status', models.IntegerField()),
                ('application_datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='申请时间')),
                ('re_datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='报销时间')),
                ('categoryid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Category')),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Student')),
            ],
            options={
                'db_table': 're_invoice',
            },
        ),
        migrations.CreateModel(
            name='Binding',
            fields=[
                ('bid', models.AutoField(primary_key=True, serialize=False)),
                ('add_datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='添加时间')),
                ('invoiceid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Invoice')),
                ('morderid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Morder')),
            ],
            options={
                'db_table': 're_binding',
            },
        ),
    ]

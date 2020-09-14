from django.db import models
import django.utils.timezone as timezone
# Create your models here.

class Category(models.Model):
    cid = models.AutoField(primary_key = True)
    name = models.CharField(max_length=10)

    class Meta:
        db_table = 're_category'

class Student(models.Model):
    sid = models.AutoField(primary_key = True)
    ssid = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    passward = models.CharField(max_length=32)

    class Meta:
        db_table = 're_student'

class Morder(models.Model):
    mid = models.AutoField(primary_key = True)
    name = models.CharField(max_length=20)
    start_datetime = models.DateTimeField('建立时间', default = timezone.now)
    re_datetime = models.DateTimeField('报销时间', default = timezone.now)

    class Meta:
        db_table = 're_morder'

class Invoice(models.Model):
    iid = models.AutoField(primary_key = True)
    inum = models.IntegerField()
    categoryid = models.ForeignKey(Category, on_delete=models.CASCADE)
    userid = models.ForeignKey(Student, on_delete=models.CASCADE)
    money = models.DecimalField(max_digits= 6, decimal_places=2)
    description = models.CharField(max_length=100)
    # 0 提交 1 已报销 2 被撤回
    status = models.IntegerField()
    application_datetime = models.DateTimeField('申请时间', default = timezone.now)
    re_datetime = models.DateTimeField('报销时间', default = timezone.now)

    class Meta:
        db_table = 're_invoice'

class Binding(models.Model):
    bid = models.AutoField(primary_key = True)
    invoiceid = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    morderid = models.ForeignKey(Morder, on_delete=models.CASCADE)
    add_datetime = models.DateTimeField('添加时间', default = timezone.now)

    class Meta:
        db_table = 're_binding'

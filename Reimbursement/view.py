from django.http import HttpResponse
from django.shortcuts import render
from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
import django.utils.timezone as timezone
import copy
import time
import random
from django.db.models import Sum , Count# 引入

from data.models import Category, Student, Morder, Invoice, Binding
from Reimbursement.defaul_info import verify_student, DEFAULT_ADMINSTRATOR, DEFAULT_SIGNUP_EMAIL_URL
from Reimbursement.toolkit import password_hash, validate_password
from Reimbursement.mredis import *
from Reimbursement.wangyi_email import Email163

@csrf_exempt
def signup(request):
    rs = {'code': 100, 'msg':''}
    if request.method == "POST":
        ssid = request.POST['ssid']
        name = request.POST['name']
        email = request.POST['email']
        passward = request.POST['passward']
        code, msg = verify_student(ssid, name)
        print(ssid, email, name, passward)
        if code == 0:
            if len(Student.objects.filter(ssid=ssid)) > 0:
                rs =  {'code' : 104, 'msg' : 'The user is already registered'}
            else:
                # 计算并保存password的hash值
                passward = password_hash(passward)
                add_student_info(ssid, name, email, passward)
                # 发送邮件
                email163 = Email163.instance()
                email163.sendEmail(email, DEFAULT_SIGNUP_EMAIL_URL + ssid)
                rs =  {'code' : 100, 'msg' : 'The verification email has been sent to the target mailbox'}
        else:
            rs = {'code' : code, 'msg' : msg}
    else:
        rs = {'code': 109, 'msg': 'Not accept get request'}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def signin(request):
    rs = {'code': 100, 'msg':'', 'level' : 0, 'token': ''}
    if request.method == "POST":
        ssid = request.POST['ssid']
        passward = request.POST['passward']
        # 查询密码是否正确，并返回用户角色
        rs = get_student_info(ssid)
        if len(rs) == 0:
            rs = {'code' : 101, 'msg' : 'No information for this student number', 'level' : 0, 'token': ''}
        else:
            # 判断密码是否正确
            if validate_password(passward, rs[2]):
                rs = {'code' : 100, 'msg' : 'login successful', 'level' : 0, 'token': get_token(ssid)}
                if ssid in DEFAULT_ADMINSTRATOR:
                    rs['level'] = 1
            else:
                rs = {'code' : 102, 'msg' : 'wrong password', 'level' : 0, 'token': ''}
    else:
        rs = {'code': 109, 'msg': 'Not accept get request', 'level' : 0, 'token': ''}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def verify(request):
    '''
        www.oscar-lab.cn:8000/verify/?ssid=21917053
    '''
    rs = {'code' : 100, 'msg' : ''}
    if request.method == 'GET':
        ssid = request.GET['ssid']
        rs = get_student_info(ssid)
        if len(rs) == 0:
            rs = {'code' : 101, 'msg' : 'No information for this student number'}
        else:
            # 验证成功, 将数据持久化到数据库中
            name, email, passward = rs
            student = Student(ssid=ssid, name=name, email=email, passward=passward)
            student.save()
            rs = {'code' : 100, 'msg' : 'registration success'}
    else:
        rs = {'code': 109, 'msg': 'Not accept post request'}
    print(rs)
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    # 重定向到登录页面
    return response

@csrf_exempt
def new_invoice(request):
    rs = {'code' : 100, 'msg' : '','invoice_num':0}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        categoryid = int(request.POST['categoryid'])
        money = round(float(request.POST['money']), 2)
        token = request.POST['token']
        description = request.POST['description']
        if verify_token(ssid, token):
            invoice_num = get_invoice_num()
            invoice = Invoice(categoryid=Category.objects.get(cid = categoryid),
                                userid=Student.objects.get(ssid = ssid),
                                inum=invoice_num, money=money,
                                description=description,status=0)
            invoice.save()
            rs = {'code' : 100, 'msg' : 'Added successfully', 'invoice_num':invoice_num}
        else:
            rs = {'code' : 101, 'msg' : 'Incorrect token, access denied', 'invoice_num':0}
    else:
        rs = {'code' : 109, 'msg' : 'Not accept get request', 'invoice_num':0}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def look_invoice(request):
    rs = {'code' : 100, 'msg' : '','datas':[]}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        look_type = int(request.POST['looktype'])
        passed = request.POST['passed']
        token = request.POST['token']
        if verify_token(ssid, token):
            if passed is True:
                morder_id = int(request.POST['mid'])
            else:
                morder_id = get_basket_num()
            infos = []
            if look_type == 0:
                # 查询我的所有, 按发票号排序
                infos = Invoice.objects.filter(userid = Student.objects.get(ssid=ssid)).order_by('status', 'inum')
            elif look_type == 1:
                # 查询我的发票, 按发票种类排序
                infos = Invoice.objects.filter(status=0).order_by('userid', 'categoryid')
            elif look_type == 2:
                # 查询我已报销的发票, 按发票号排序
                infos = Invoice.objects.filter(userid = Student.objects.get(ssid=ssid)).filter(status=3).order_by('status', 'inum')
            elif look_type == 3:
                # 查询我已报销的发票, 按发票种类排序
                infos = Invoice.objects.filter(userid = Student.objects.get(ssid=ssid)).filter(status=3).order_by('status', 'categoryid')
            elif look_type == 4:
                # 查询所有未报销的发票
                infos = Invoice.objects.filter(userid = Student.objects.get(ssid=ssid)).filter(status=0).order_by('inum')
            elif look_type == 5 and morder_id != 0:
                # 查询一次报销表单里的所有发票，按发票号排序
                temp = Binding.objects.filter(morderid = Morder.objects.get(mid=morder_id)).values('invoiceid')
                invoice_nums = []
                for t in temp:
                    invoice_nums.append(t['invoiceid'])
                infos = Invoice.objects.filter(iid__in=invoice_nums).order_by('inum')
            elif look_type == 6 and morder_id != 0:
                # 查询一次报销表单里的所有发票，按种类排序
                temp = Binding.objects.filter(morderid = Morder.objects.get(mid=morder_id)).values('invoiceid')
                invoice_nums = []
                for t in temp:
                    invoice_nums.append(t['invoiceid'])
                infos = Invoice.objects.filter(iid__in=invoice_nums).order_by('categoryid')
            elif look_type == 7 and morder_id != 0:
                # 查询一次报销表单里的所有发票，按人名计算和
                temp = Binding.objects.filter(morderid = Morder.objects.get(mid=morder_id)).values('invoiceid')
                invoice_nums = []
                for t in temp:
                    invoice_nums.append(t['invoiceid'])
                infos = Invoice.objects.filter(iid__in=invoice_nums).values('userid_name').annotate(dcount=Count("inum"), totmoney=Sum("money"))
                #infos = Binding.objects.filter(morderid = Morder.objects.get(mid=morder_id)).invoiceid_set.all().values('userid').annotate(dcount=Count("inum"), totmoney=Sum("money"))
            elif look_type == 8 and morder_id != 0:
                # 查询一次报销表单里的所有发票，按种类计算和
                temp = Binding.objects.filter(morderid = Morder.objects.get(mid=morder_id)).values('invoiceid')
                invoice_nums = []
                for t in temp:
                    invoice_nums.append(t['invoiceid'])
                infos = Invoice.objects.filter(iid__in=invoice_nums).values('categoryid').annotate(dcount=Count("inum"), totmoney=Sum("money"))
                # infos = Binding.objects.filter(morderid = Morder.objects.get(mid=morder_id)).invoiceid_set.all().values('categoryid').annotate(dcount=Count("inum"), totmoney=Sum("money"))
            else:
                pass
            data = []
            if look_type == 7:
                for info in infos:
                    record = {
                        'username' : Student.objects.get(sid=info['userid']).name,
                        'dcount' : info['dcount'],
                        'sum' : round(float(info['totmoney']), 2)
                    }
                    data.append(record)
            elif look_type == 8:
                for info in infos:
                    record = {
                        'category' : Category.objects.get(cid=info['categoryid']).name,
                        'dcount' : info['dcount'],
                        'sum' : round(float(info['totmoney']), 2)
                    }
                    data.append(record)
            else:
                for info in infos:
                    record = {
                        'inum' : info.inum,
                        'name' : info.userid.name,
                        'category' : info.categoryid.name,
                        'money' : round(float(info.money), 2),
                        'description' : info.description,
                        'status' : info.status,
                        'application_datetime' : info.application_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        're_datetime' : info.re_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    data.append(record)
            rs = {'code' : 100, 'msg' : 'search successful','datas':data}
        else:
            rs = {'code' : 101, 'msg' : 'Incorrect token, access denied','datas':[]}
    else:
        rs = {'code' : 109, 'msg' : 'Not accept get request','datas':[]}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def new_rei_basket(request):
    rs = {}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        name = request.POST['name']
        if verify_token(ssid, token):
            if can_new_basket():
                morder = Morder(name=name)
                morder.save()
                record_basket_num(morder.mid)
                rs = {'code': 100, 'msg':'Created successfully'}
            else:
                rs = {'code': 102, 'msg':'There is already a reimbursement list'}
        else:
            rs = {'code': 101, 'msg':'Incorrect token, access denied'}
    else:
        rs = {'code' : 109, 'msg' : 'Not accept get request'}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def put_invoice_tobasket(request):
    rs = {}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        inum = request.POST['inum']
        if verify_token(ssid, token):
            morder_id = get_basket_num()
            if morder_id != 0:
                Invoice.objects.filter(inum=inum).update(status=2)
                binding = Binding(invoiceid=Invoice.objects.get(inum=inum),
                                    morderid=Morder.objects.get(mid=morder_id))
                binding.save()
                rs = {'code':100, 'msg':'Successfully added'}
            else:
                rs = {'code':103, 'msg':'There are currently no reimbursement items'}
        else:
            rs = {'code':101, 'msg':'Incorrect token, access denied'}
    else:
        rs =  {'code' : 109, 'msg' : 'Not accept get request'}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def modify_invoice(request):
    rs = {'code' : 100, 'msg' : '','datas':[]}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        inum = request.POST['inum']
        categoryid = int(request.POST['categoryid'])
        money = round(float(request.POST['money']), 2)
        description = request.POST['description']
        if verify_token(ssid, token):
            invoice = Invoice.objects.get(inum=inum)
            invoice.categoryid = Category.objects.get(cid=categoryid)
            invoice.money = money
            invoice.description = description
            invoice.save()
            rs = {'code':100, 'msg':'Successfully modify'}
        else:
            rs = {'code':101, 'msg':'Incorrect token, access denied'}
    else:
        rs =  {'code' : 109, 'msg' : 'Not accept get request'}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def re_apply_invoicet(request):
    rs = {}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        inum = request.POST['inum']
        if verify_token(ssid, token):
            morder_id = get_basket_num()
            if morder_id != 0:
                Invoice.objects.filter(inum=inum).update(status=0)
                rs = {'code':100, 'msg':'Successfully added'}
            else:
                rs = {'code':103, 'msg':'There are currently no reimbursement items'}
        else:
            rs = {'code':101, 'msg':'Incorrect token, access denied'}
    else:
        rs =  {'code' : 109, 'msg' : 'Not accept get request'}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def refuse_invoicet(request):
    rs = {}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        inum = request.POST['inum']
        if verify_token(ssid, token):
            morder_id = get_basket_num()
            if morder_id != 0:
                Invoice.objects.filter(inum=inum).update(status=2)
                rs = {'code':100, 'msg':'Successfully refuse'}
            else:
                rs = {'code':103, 'msg':'There are currently no reimbursement items'}
        else:
            rs = {'code':101, 'msg':'Incorrect token, access denied'}
    else:
        rs =  {'code' : 109, 'msg' : 'Not accept get request'}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def get_his_morder(request):
    rs = {}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        if verify_token(ssid, token):
            infos = Morder.objects.all().order_by('start_datetime')
            datas = []
            for info in infos:
                datas.append({
                    'mid': info.mid,
                    'name': info.name,
                    'start_datetime': info.start_datetime,
                    're_datetime': info.re_datetime,
                })
            rs = {'code':100, 'msg':'search successful', 'datas':datas}
        else:
            rs = {'code':101, 'msg':'Incorrect token, access denied', 'datas':[]}
    else:
        rs =  {'code' : 109, 'msg' : 'Not accept get request', 'datas':[]}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response


@csrf_exempt
def get_all_category(request):
    rs = {}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        if verify_token(ssid, token):
            infos = Category.objects.all()
            datas = []
            for info in infos:
                datas.append({
                    'cid': info.cid,
                    'name': info.name,
                })
            rs = {'code':100, 'msg':'search successful', 'datas':datas}
        else:
            rs = {'code':101, 'msg':'Incorrect token, access denied', 'datas':[]}
    else:
        rs =  {'code' : 109, 'msg' : 'Not accept get request', 'datas':[]}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def over_basket(request):
    rs = {}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        if verify_token(ssid, token):
            morder_id = get_basket_num()
            if morder_id != 0:
                dtime = timezone.now
                Morder.objects.filter(mid=morder_id).update(re_datetime=dtime)
                temp = Binding.objects.filter(morderid = Morder.objects.get(mid=morder_id)).values('invoiceid')
                invoice_nums = []
                for t in temp:
                    invoice_nums.append(t['invoiceid'])
                Invoice.objects.filter(iid__in=invoice_nums).update(status=3)
                Invoice.objects.filter(iid__in=invoice_nums).update(re_datetime=dtime)
                rs = {'code':100, 'msg':'Successfully'}
            else:
                rs = {'code':103, 'msg':'There are currently no reimbursement items'}
        else:
            rs = {'code':101, 'msg':'Incorrect token, access denied', 'datas':[]}
    else:
        rs =  {'code' : 109, 'msg' : 'Not accept get request', 'datas':[]}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def get_invoicet_info(request):
    rs = {}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        inum = request.POST['inum']
        if verify_token(ssid, token):
            info = Invoice.objects.filter(inum=inum)[0]
            record = {
                'inum' : info.inum,
                'name' : info.userid.name,
                'category' : info.categoryid.name,
                'money' : round(float(info.money), 2),
                'description' : info.description,
                'status' : info.status,
                'application_datetime' : info.application_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                're_datetime' : info.re_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            }
            rs = {'code':100, 'msg': 'Successfully', 'datas' : record}
        else:
            rs = {'code':101, 'msg':'Incorrect token, access denied', 'datas' : {}}
    else:
        rs =  {'code' : 109, 'msg' : 'Not accept get request', 'datas' : {}}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response

@csrf_exempt
def del_invoicet(request):
    rs = {}
    if request.method == 'POST':
        ssid = request.POST['ssid']
        token = request.POST['token']
        inum = request.POST['inum']
        if verify_token(ssid, token):
            info = Invoice.objects.filter(inum=inum).delete()
            rs = {'code':100, 'msg': 'Successfully'}
        else:
            rs = {'code':101, 'msg':'Incorrect token, access denied'}
    else:
        rs =  {'code' : 109, 'msg' : 'Not accept get request'}
    response = HttpResponse(json.dumps(rs))
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Allow-Methods"] = "GET,POST"
    response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
    return response
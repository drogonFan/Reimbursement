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

from data.models import Category, Student, Morder, Invoice, Binding
from Reimbursement.defaul_info import verify_student, DEFAULT_ADMINSTRATOR, DEFAULT_SIGNUP_EMAIL_URL
from Reimbursement.toolkit import password_hash, validate_password
from Reimbursement.mredis import add_student_info, get_student_info
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
        if code == 0:
            if len(Student.objects.filter(ssid=ssid)) > 0:
                rs =  {'code' : 104, 'msg' : 'The user is already registered'}
            else:
                # 计算并保存password的hash值
                passward = password_hash(passward)
                add_student_info(ssid, name, email, passward)
                # 发送邮件
                email163 = Email163.instance()
                email163.new_thread_sendemail(email, DEFAULT_SIGNUP_EMAIL_URL + ssid)
                rs =  {'code' : 100, 'msg' : 'The verification email has been sent to the target mailbox'}
        else:
            rs = {'code' : code, 'msg' : msg}
    else: 
        rs = {'code': 109, 'msg': 'Not accept get request'}
    return HttpResponse(json.dumps(rs))

@csrf_exempt
def signin(request):
    rs = {'code': 100, 'msg':'', 'level' : 0}
    if request.method == "POST":
        ssid = request.POST['ssid']
        passward = request.POST['passward']
        # 查询密码是否正确，并返回用户角色
        rs = get_student_info(ssid)
        if len(rs) == 0:
            rs = {'code' : 101, 'msg' : 'No information for this student number', 'level' : 0}
        else:
            # 判断密码是否正确
            if validate_password(passward, rs[2]):
                rs = {'code' : 100, 'msg' : 'login successful', 'level' : 0}
                if ssid in DEFAULT_ADMINSTRATOR:
                    rs['level'] = 1
            else:
                rs = {'code' : 102, 'msg' : 'wrong password', 'level' : 0}        
    else: 
        rs = {'code': 109, 'msg': 'Not accept get request', 'level' : 0}
    return HttpResponse(json.dumps(rs))

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
    return HttpResponse(json.dumps(rs))
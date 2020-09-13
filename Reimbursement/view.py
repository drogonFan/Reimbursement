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
from Reimbursement.defaul_info import verify_student

@csrf_exempt
def signup(request):
    rs = {'code': 100, 'msg':''}
    if request.method == "POST":
        ssid = request.POST['ssid']
        name = request.POST['name']
        email = request.POST['email']
        passward = request.POST['email']
        # 验证是否本实验室成员（日后可以改为发邮件验证）
        code, msg = verify_student(ssid, name)
        if code == 0:
            # 保存对象
            student = Student(ssid=ssid, name=name, email=email, passward=passward)
            student.save()
        else:
            rs = {'code' : code, 'msg' : msg}
    else: 
        rs = {'code': 109, 'msg': 'Not accept get request'}
    return HttpResponse(json.dumps(rs))

@csrf_exempt
def signin(request):
    rs = {'code': 100, 'msg':''}
    if request.method == "POST":
        ssid = request.POST['ssid']
        name = request.POST['name']
        email = request.POST['email']
        passward = request.POST['email']
        # 验证是否本实验室成员（日后可以改为发邮件验证）
        code, msg = verify_student(ssid, name)
        if code == 0:
            # 保存对象
            student = Student(ssid=ssid, name=name, email=email, passward=passward)
            student.save()
        else:
            rs = {'code' : code, 'msg' : msg}
    else: 
        rs = {'code': 109, 'msg': 'Not accept get request'}
    return HttpResponse(json.dumps(rs))
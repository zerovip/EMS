import json
import time
import pymysql
from urllib.parse import unquote

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Max

from .models import User, Usergroup, Device
from .forms import UserForm, UsergroupForm, DeviceForm, SelfForm
from .data_db import Data_db
from .controller import control

control_password = 'lizihe970106'

#######################################################################################################################################
#预处理或功能集成部分
#######################################################################################################################################
#登陆后的权限列表
def ls_perm(username):
    user=User.objects.get(username=username)
    list_p = {
            'username':username,
            'charge':user.charge,
            'tem':user.tem,
            'hum':user.hum,
            'pm25':user.pm25,
            'pm10':user.pm10,
            'device':user.device,
            'master':user.master,
            'device_p':Device.objects.all(),
            }
    if user.master == 'S':
        all_m_s = Usergroup.objects.all()
        mas_ls = {}
        for it_m_s in all_m_s:
            per_ls = {}
            for person in User.objects.filter(group=it_m_s):
                per_ls['{0}'.format(person.id)] = person.username
            mas_ls['{0}'.format(it_m_s.groupname)] = (
                    it_m_s.id,
                    per_ls,
                    )
        list_p['master_s'] = mas_ls
    elif user.master == 'G':
        group = user.group
        list_p['group_id'] = group.id
        list_p['group_n'] = group.groupname
        list_p['group_m'] = User.objects.filter(group=group)
    return list_p

#处理cookies部分
class Session:
    def __init__(self, request):
        self.request = request
        self.username = request.session.get('username')
        self.password = request.session.get('password')
    def del_session(self):
        del self.request.session['username']
        del self.request.session['password']
        return self.request

#检查登陆状态装饰器，未登录者只有最基本的查看实时数据的权限
def login_check(func):
    def wrapper(request, id=0):
        status = 0
        tip = ''
        logged = {'device_p':Device.objects.all()}
        def resp(request, status, tip, logged):
            return render(request, 'emsys/index.html', {
                'tip':tip,
                'status':status,
                'logged':logged,
                })
        s = Session(request)
#        username = request.session.get('username')
#        password = request.session.get('password')
        if s.username != None:
            try:
                user = User.objects.get(username=s.username)
                if user.password != s.password:
                    request = s.del_session()
#                    del request.session['username']
#                    del request.session['password']
                    tip = '密码已被更改，请重新登录。'
                    return resp(request, status, tip, logged)
                else:
                    midf=func(request, id)
                    return midf
            except User.DoesNotExist:
                request = s.del_session()
                tip = '可能用户名发生变更，请重新登录。'
                return resp(request, status, tip, logged)
        else:
            return resp(request, status, tip, logged)
    return wrapper

#用户编辑权限检查装饰器，装饰器按照由下到上的顺序装饰
def user_perm(func):
    def wrapper(request, id=0):
        name = Session(request).username
        master = User.objects.get(username=name).master
        if master == 'N':
            return redirect('/emsys/')
        elif master == 'G':
            if int(id) == 0:
                return redirect('/emsys/')
            else:
                if User.objects.get(username=name).group == User.objects.get(id=int(id)).group:
                    midf = func(request, id)
                    return midf
                else:
                    return redirect('/emsys/')
        elif master == 'S':
            midf = func(request, id)
            return midf
    return wrapper

#用户组编辑权限装饰器
def usp_perm(func):
    def wrapper(request, id=0):
        name = Session(request).username
        master = User.objects.get(username=name).master
        if master != 'S':
            return redirect('/emsys')
        else:
            midf = func(request, id)
            return midf
    return wrapper

#设备编辑权限装饰器
def dev_perm(func):
    def wrapper(request, id=0):
        name = Session(request).username
        device = User.objects.get(username=name).device
        if device != True:
            return redirect('/emsys')
        else:
            midf = func(request, id)
            return midf
    return wrapper

#数据查看权限装饰器
#已废弃，在数据页用模板进行

#######################################################################################################################################
#页面功能部分
#######################################################################################################################################
#登陆
def login(request):
    logged = {'device_p':Device.objects.all()}
    tip = ''
    status = 0
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username != '':
            if password != '':
                try:
                    user = User.objects.get(username=username)
                    if user.password != password:
                        tip = '密码错误。'
                    else:
                        request.session['username'] = username
                        request.session['password'] = password
                        logged = ls_perm(username)
                        status = 1
                        return redirect('index')
                except User.DoesNotExist:
                    tip = '该用户名未注册。'
            else:
                tip = '请输入密码。'
        else:
            tip = '请输入用户名。'
    else:
        return redirect('/emsys/')
    return render(request, 'emsys/index.html',{
        'tip':tip,
        'status':status,
        'logged':logged,
        })

#登出
def logout(request):
    s = Session(request)
    if s.username != None:
        s.del_session()
    return redirect('/emsys/')

#首页
@login_check
def index(request, id):
    username = request.session.get('username')
    return render(request, 'emsys/index.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        })

#添加设备页
@dev_perm
@login_check
def dev_add(request, id):
    username = request.session.get('username')
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            mid = Device.objects.aggregate(Max('id'))['id__max']
            control('ADDANID{0}'.format(mid), control_password)
            return redirect('/emsys/')
    else:
        form = DeviceForm()
    return render(request, 'emsys/add.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        'object':'设备',
        'form':form,
        })

#编辑设备页
@dev_perm
@login_check
def dev_edit(request, id):
    username = request.session.get('username')
    data = Device.objects.get(id=int(id))
    if request.method == 'POST':
        form = DeviceForm(request.POST, initial=data.__dict__, instance=data)
        if form.is_valid():
            if form.has_changed():
                form.save()
            return redirect('/emsys/')
    else:
        form = DeviceForm(instance=data)
    return render(request, 'emsys/edit.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        'object':'设备',
        'form':form,
        'id':id,
        'part':'dev',
        })

#删除设备页
@dev_perm
@login_check
def dev_del(request, id):
    username = request.session.get('username')
    data = Device.objects.get(id=int(id))
    data.delete()
    return render(request, 'emsys/tip.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        })

#管理设备页
@dev_perm
@login_check
def dev_control(request, id):
    username = request.session.get('username')
    return render(request, 'emsys/dev_control.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        })

#单片机控制器启动
def data_control(request, action):
    dev_id = str(request.POST.get('id'))
    if action == 'on':
        request = 'START'
    elif action =='off':
        request = 'STOP'
    data_re = control(request+dev_id, control_password)
    return HttpResponse(json.dumps(data_re))

#添加用户组页
@usp_perm
@login_check
def usgp_add(request, id):
    username = request.session.get('username')
    if request.method == 'POST':
        form = UsergroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/emsys/')
    else:
        form = UsergroupForm()
    return render(request, 'emsys/add.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        'object':'用户组',
        'form':form,
        })

#编辑用户组页
@usp_perm
@login_check
def usgp_edit(request, id):
    username = request.session.get('username')
    data = Usergroup.objects.get(id=int(id))
    if request.method == 'POST':
        form = UsergroupForm(request.POST, initial=data.__dict__, instance=data)
        if form.is_valid():
            if form.has_changed():
                form.save()
            return redirect('/emsys/')
    else:
        form = UsergroupForm(instance=data)
    return render(request, 'emsys/edit.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        'object':'用户组',
        'form':form,
        'id':id,
        'part':'usergroup',
        'total':Usergroup.objects.get(id=int(id)).num
        })

#删除用户组页
@usp_perm
@login_check
def usgp_del(request, id):
    username = request.session.get('username')
    data = Usergroup.objects.get(id=int(id))
    data.delete()
    return render(request, 'emsys/tip.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        })

#添加用户页
@user_perm
@login_check
def user_add(request, id):
    username = request.session.get('username')
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            belong=form.cleaned_data['group']
            belong.num += 1
            belong.save()
            return redirect('/emsys/')
    else:
        belong = Usergroup.objects.get(id=id)
        form = UserForm(initial={
            'group':belong,
            'charge':belong.charge.all(),
            'tem':belong.tem,
            'hum':belong.hum,
            'pm25':belong.pm25,
            'pm10':belong.pm10,
            'device':belong.device,
            })
    return render(request, 'emsys/add.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        'object':'用户',
        'form':form,
        })

#编辑用户页
#这里加判断，如果id等于自己，redirect到self
@user_perm
@login_check
def user_edit(request, id):
    username = request.session.get('username')
    if User.objects.get(username=username).id == int(id):
        return redirect('/emsys/user/self/')
    else:
        data = User.objects.get(id=int(id))
        if request.method == 'POST':
            form = UserForm(request.POST, initial=data.__dict__, instance=data)
            if form.is_valid():
                if form.has_changed():
                    form.save()
                return redirect('/emsys/')
        else:
            form = UserForm(instance=data)
    return render(request, 'emsys/edit.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        'object':'用户',
        'form':form,
        'id':id,
        'part':'user',
        })

#编辑个人信息页
@login_check
def self(request, id):
    username = request.session.get('username')
    data = User.objects.get(username=username)
    if request.method == 'POST':
        form = SelfForm(request.POST, initial=data.__dict__, instance=data)
        if form.is_valid():
            if form.has_changed():
                form.save()
            return redirect('/emsys/')
    else:
        form = SelfForm(instance=data)
    return render(request, 'emsys/self.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        'form':form,
        })

#删除用户页
@user_perm
@login_check
def user_del(request, id):
    username = request.session.get('username')
    data = User.objects.get(id=int(id))
    data.delete()
    return render(request, 'emsys/tip.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        })

#数据查询页
@login_check
def data_history(request, id):
    if id:
        id = unquote(id).replace('-', '')
    username = request.session.get('username')
    db = pymysql.connect(
            host = "localhost",
            user = "root",
            password = "lizihe970106",
            db = "emsys",
            charset = "utf8",
            cursorclass = pymysql.cursors.DictCursor,
            )
    cursor = db.cursor()
    sql = "SELECT time, tem, hum, pm25, pm10 FROM {0}".format(id)
    try:
        cursor.execute(sql)
        data_get = cursor.fetchall()
    except pymysql.err.ProgrammingError:
        data_get = [{'time':'请查询。'},]
# need(str) 需要的数据 示例：'1_地点一_20161010'
    return render(request, 'emsys/data_history.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        'data':data_get,
        })

#警报设置页
@login_check
def data_warning(request, id):
    username = request.session.get('username')
    if request.method == 'POST':
        need = ['tem_x', 'tem_n', 'tem_e', 'hum_x', 'hum_n', 'hum_e', 'pm25_x', 'pm25_n', 'pm25_e', 'pm10_x', 'pm10_n', 'pm10_e']
        save = {}
        for i in need:
            exec("{0} = request.POST.get('{0}')".format(i,))
            exec("save['{0}'] = ".format(i) + i)
        the_range = request.POST.get('range')
        if the_range == 'server':
            file_save = open("./emsys/mail.zero", "w+")
            file_save.write(json.dumps(save))
            file_save.close()
            mssg = '修改成功。'
        else:
            if float(save['tem_n']) < 0:
                tem_n_m = float(save['tem_n']) + 100
            else:
                tem_n_m = float(save['tem_n'])
            if float(save['tem_x']) < 0:
                tem_x_m = float(save['tem_x']) + 100
            else:
                tem_x_m = float(save['tem_x'])
            the_dev_id = str(the_range).zfill(2)
            tem_n_ = str(int(tem_n_m*100)).zfill(4)
            hum_n_ = str(int(float(save['hum_n'])*100)).zfill(4)
            pm25_n_ = str(int(save['pm25_n'])).zfill(4)
            pm10_n_ = str(int(save['pm10_n'])).zfill(4)
            tem_x_ = str(int(tem_x_m*100)).zfill(4)
            hum_x_ = str(int(float(save['hum_x'])*100)).zfill(4)
            pm25_x_ = str(int(save['pm25_x'])).zfill(4)
            pm10_x_ = str(int(save['pm10_x'])).zfill(4)
            try_con = the_dev_id + 'WARH' + tem_n_ + \
                    hum_n_ + pm25_n_ + pm10_n_ + tem_x_ + hum_x_ + pm25_x_ + pm10_x_
            mssg_ = control(try_con, control_password)
            mssg = '蜂鸣器设置结果：'+str(mssg_)
    else:
        mssg = '请编辑。'
    file_save = open("./emsys/mail.zero", "r")
    file_data = json.load(file_save)
    file_save.close()
    return render(request, 'emsys/data_warning.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username),
        'mssg':mssg,
        'file_data':file_data,
        })

#ajax通讯部分
def ajax(request):
    start = unquote(str(request.GET.get('start')).replace('-', ''))[:14]
    end = unquote(str(request.GET.get('end')).replace('-', ''))[:14]
    choose = request.POST.get('choose')
    all_dev = Device.objects.all()
    if choose == None:
        choose = []
        for dev in all_dev:
            choose.append('{0}0'.format(dev.id))
            choose.append('{0}1'.format(dev.id))
            choose.append('{0}2'.format(dev.id))
            choose.append('{0}3'.format(dev.id))
    if start == 'None':
        end = time.strftime('%Y%m%d %H:%M', time.localtime())
        end_ = time.mktime(time.strptime(end, '%Y%m%d %H:%M'))
        start_ = time.localtime(end_-1800)
        start = time.strftime('%Y%m%d %H:%M', start_)
        return_data = Data_db().read_out(choose, start)
        return_data['start'] = time.strftime('%Y-%m-%d %H:%M', start_)
        return_data['end'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(end_))
        return_data['msg'] = 'ok'
        return_data['wait'] = 40
        return_data['step'] = '1m'
    else:
        start_ = time.mktime(time.strptime(start, '%Y%m%d %H:%M'))
        if start_ >= time.time():
            return_data = {'msg':'early', 'wait':40}
        else:
            if end == 'None':
                m = Data_db()
                return_data = m.read_out(choose, start)
                the_num = len(return_data[choose[0]])
                start_ = time.mktime(time.strptime(start,"%Y%m%d %H:%M"))
                start_l = time.localtime(start_)
                start_r = time.strftime('%Y-%m-%d %H:%M', start_l)
                end_l = time.localtime(start_ + (the_num-1)*60)
                end_r = time.strftime('%Y-%m-%d %H:%M', end_l)
            else:
                m = Data_db()
                return_data = m.read_out(choose, start, end)
                start_r = unquote(str(request.GET.get('start')))[:14]
                end_r = unquote(str(request.POST.get('end')))[:14]
            return_data['start'] = start_r
            return_data['end'] = end_r
            return_data['msg'] = 'ok'
            return_data['step'] = '1m'
    return HttpResponse(json.dumps(return_data))

#向外API接口
def api(request):
    pass

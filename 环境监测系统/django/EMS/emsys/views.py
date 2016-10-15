import socket

from django.shortcuts import render, redirect

from .models import User, Usergroup, Device
from .forms import UserForm, UsergroupForm, DeviceForm, SelfForm

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
            print('not valid')
            print(form)
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
            return redirect('/emsys/')
    else:
        form = UserForm()
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

#数据查询页
@login_check
def data_history(request, id):
    username = request.session.get('username')
    return render(request, 'emsys/data_history.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username)
        })

#警报设置页
@login_check
def data_warning(request, id):
    username = request.session.get('username')
    return render(request, 'emsys/data_warning.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username)
        })

#向外API接口
def api(request):
    pass


#######################################################################################################################################
#做TCP服务器接收数据部分
#这一部分其实不应该写到views里而是应该另写到一个文件里
#######################################################################################################################################
'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #遵守IPv4与TCP协议
s.bind(('0.0.0.0', 1025))    #前面绑定服务器上一个网卡的IP地址，0.0.0.0表示绑定到所有网络地址
s.listen(5)    #监听端口，指定等待连接的最大数量
#这一部分以后再用Device那个表的数据量重写一下，加上判断等
while True:
    # 接受一个新连接:
    sock, addr = s.accept()
    # 创建新线程来处理TCP连接:
    t = threading.Thread(target=tcplink, args=(sock, addr))
    t.start()

def tcplink(sock, addr):
    sock.send('Welcome!')
    while True:
        data = sock.recv(1024)
        time.sleep(1)
#接下来解析data之后存进去就行了
        if data == 'exit' or not data:
            break
        sock.send('Hello, %s!' % data)
    sock.close()
    print ('Connection from %s:%s closed.' % addr)
'''

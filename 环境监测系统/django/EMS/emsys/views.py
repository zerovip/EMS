import socket

from django.shortcuts import render, redirect

from .models import User, Usergroup, Device

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
            }
#    if device
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
    def wrapper(request):
        status = 0
        tip = ''
        logged = ''
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
                    midf=func(request)
                    return midf
            except User.DoesNotExist:
                request = s.del_session()
                tip = '可能用户名发生变更，请重新登录。'
                return resp(request, status, tip, logged)
        else:
            return resp(request, status, tip, logged)
    return wrapper

#######################################################################################################################################
#页面功能部分
#######################################################################################################################################
#登陆
def login(request):
    logged = ''
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
    return HttpResponseRedirect('/emsys/')

#首页
@login_check
def index(request):
    username = request.session.get('username')
    return render(request, 'emsys/index.html', {
        'tip':'',
        'status':1,
        'logged':ls_perm(username)
        })


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

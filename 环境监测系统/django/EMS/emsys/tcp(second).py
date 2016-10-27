import time
import socket
import threading

from data_db import Data_db
from .email_SMTP import send_mail

#######################################################################################################################################
#TCP服务器部分重写，用了多线程。
#######################################################################################################################################
HOST = ''
PORT = 7790
BUFSIZ = 1024
ADDR = (HOST, PORT)
password = 'lizihe970106'

# 接收单片机客户端数据并反馈的函数（替代之前的 SocketServer 部分）
def handle_data(sock, dev_id):
    while True:
        try:
            data = sock.recv(BUFSIZ)
        except ConnectionResetError:
            # 客户端因为故障等被强迫下线
            del linking_dev[dev_id]
            break
        if time.strftime('%H:%M', time.localtime()) == '00:02':
            d = Data_db()
            ret_code = data_save(d, data)
            print(ret_code)
            sock.send(ret_code.encode())

# 接收控制器客户端得指令
def handle_cont(sock):
    while True:
        try:
            data = sock.recv(BUFSIZ)
        except ConnectionResetError:
            del linking_dev['control']
            break
        if data.decode()[:7] == 'ADDANID':
            prepare.append(int(data.decode()[7:]))
            sock.send('成功'.encode)
        elif data.decode()[:4] == 'STOP':
            id = int(data.decode()[4:])
            linking_dev[id].send('\r\nstop\r\n'.encode())
            sock.send('成功'.encode)
        elif data.decode()[:5] == 'START':
            id = int(data.decode()[5:])
            linking_dev[id].send('\r\nstat\r\n'.encode())
            sock.send('成功'.encode)
        elif data.decode() == 'exit':
            sock.send('退出'.encode)
            sock.close()
            break

tcpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServerSocket.bind(ADDR)
tcpServerSocket.listen(5)

linking_dev = {}
prepare = []

'''服务器端主体部分：
    单片机在第一次连接后会确认身份，在此过程中出现问题会关闭连接，以免堵塞其他首次请求。
        单片机可以根据返回的错误信息适当调整后再次请求连接，
        身份确认通过后，服务器会发ok回去，此时才会单开一个线程供单片机使用。
        在此线程中，服务器接收请求并作出回应。
    控制器是用来控制单片机的客户端类型，首次连接时需确认身份。
        身份确认格式为：‘con’+密码，格式正确且密码正确才会单开一个线程给控制器，
        控制器可以接收到 '允许控制' 作为信号。
        密码错误则直接关闭连接并在命令行内打印提醒注意。

        可以操作的控制有：
        指令：'ADDANID'+一设备ID 在设备添加完成后调用
            要求添加设备时先在网页上添加设备，
            然后新加的设备迅速连接服务器并发 DEVMYNUM 方可配对成功
        指令：'STOP'+一设备ID
        指令：'START'+一设备ID

        再有控制单片机的需求直接重写 handle_cont 函数即可。
'''
while True:
    print('--------等待连接--------')
    tcpCliSocket, addr = tcpServerSocket.accept()
    print('--------与{0}建立了连接--------'.format(addr))
    try:
        check_data = tcpCliSocket.recv(BUFSIZ)
    except ConnectionResetError:
        print('--------该连接被迫下线--------')
    # 这条信息为区分单片机客户端与控制器客户端所用
    if (check_data[0] == 10) & (check_data[1] == 13) & (data[-2] == 13)& (data[-1] == 10):
        if len(check_data) == 12:
            ask_data = (check_data[2:10]).decode()
            if ask_data == 'DEVMYNUM':
                # 新设备
                if len(prepare) != 0:
                    the_id = prepare[0]
                    if the_id in linking_dev:
                        # 应该不会出现。出现说明 prepare 列表出现了错误
                        print('出现了问题，请检查 prepare 不应该有已经分配出去的ID')
                    linking_dev[the_id] = tcpCliSocket
                    del prepare[0]
                    tcpCliSocket.send('ok{0}'.format(the_id).encode())
                    data_rev = threading.Thread(target=handle_data, args=(tcpCliSocket, the_id))
                    data_rev.start()
                else:
                    # 先去添加设备页添加设备再操作
                    tcpCliSocket.send('err1'.encode())
                    tcpCliSocket.close()
            elif ask_data[0:6] == 'DEVNUM':
                # 原有设备
                the_dev_id = int(ask_data[6:8])
                if the_dev_id in linking_dev:
                    # 之前得连接没有正确关闭
                    print('之前得连接没有正确关闭，之前的端口是：')
                    print(linking_dev[the_dev_id].getpeername())
                    linking_dev[the_dev_id].close()
                linking_dev[the_dev_id] = tcpCliSocket
                tcpCliSocket.send('ok{0}'.format(the_dev_id).encode())
                data_rev = threading.Thread(target=handle_data, args=(tcpCliSocket, the_dev_id))
                data_rev.start()
            else:
                # 数据格式不正确
                tcpCliSocket.send('err2'.encode())
                tcpCliSocket.close()
        else:
            # 数据长度有误
            tcpCliSocket.send('err3'.encode())
            tcpCliSocket.close()
    else:
        # 有可能是控制器客户端
        if check_data[:3] == 'con':
            # 就是控制器客户端
            if check_data[3:] == password:
                # 密码正确，允许控制
                if 'control' in linking_dev:
                    linking_dev['control'].close()
                    del linking_dev['control']
                tcpCliSocket.send('允许控制'.encode())
                linking_dev['control'] = tcpCliSocket
                con_thread = threading.Thread(target=handle_cont, args=(tcpCliSocket,))
                con_thread.start()
            else:
                # 密码错误
                print('--------有控制器试图连接，因密码错误被拒绝。请关注。--------')
                print('--------地址与端口是：{0}--------'.format(tcpCliSocket.getpeername()))
                tcpCliSocket.close()
        else:
            # 是单片机客户端，且数据开头和结尾不符规定
            tcpCliSocket.send('err4'.encode())
            tcpCliSocket.close()

tcpServerSocket.close()

#######################################################################################################################################
#下位机数据含义解析模块，根据通讯规则制定
#######################################################################################################################################
#数据写入
def data_write(d, dev_id, date_n_time, data_list):
    for index, data in enumerate(data_list):
        time_flo = time.mktime(time.strptime(date_n_time, '%Y-%m-%d %H:%M'))+60*index
        time_rec = time.strftime('%Y%m%d %H:%M', time.localtime(time_flo))
        tem_ori = 10*(data[0]//16)+(data[0]%16)+0.1*(data[1]//16)+0.01*(data[1]%16)
        if tem_ori > 80:
            tem = tem_ori-100
        else:
            tem = tem_ori
        hum = 10*(data[2]//16)+(data[2]%16)+0.1*(data[3]//16)+0.01*(data[3]%16)
        pm25 = 1000*(data[4]//16)+100*(data[4]%16)+10*(data[5]//16)+(data[5]%16)
        pm10 = 1000*(data[6]//16)+100*(data[6]%16)+10*(data[7]//16)+(data[7]%16)
        print(time_rec)
        print(dev_id)
        print(tem,hum,pm25,pm10)
        file_save = open("./emsys/mail.zero", "r")
        file_data = json.load(file_save)
        file_save.close()
        for i in ['tem', 'hum', 'pm25', 'pm10']:
            if (exec(i) > file_data[i+'_x']) or (exec(i) < file_data[i+'_n'):
                p_l = []
                p_l.append(file_data[i+'_e'])
                send_mail(p_l, '环境监测系统警报提醒', i+'超标，请您查看。——邮件为自动发送，请勿回复。')
        try:
            d.write_in(
                    [time_rec, str(dev_id)],
                    [str(tem), str(hum), str(pm25), str(pm10)],
                    )
        except:
            # 调用 Data_db 写入接口出现问题
            return 'write error'
        else:
            # 成功
            return 'okwrite SUC'

#数据接收保存
def data_save(d, data):
    total = len(data)
    print(("total length is %d") %(total))
    #判断起始位和结束位
    if(total==1):
        return 'E0'
    elif (data[0] == 13) & (data[1] == 10) & (data[-2] == 13) & (data[-1] == 10):
        dev_id = (data[2]//16)*10+(data[2]%16)
        date_n_time = '{0}{1}{2}{3}-{4}{5}-{6}{7} {8}{9}:{10}{11}'.format(
                    data[3]//16,
                    data[3]%16,
                    data[4]//16,
                    data[4]%16,
                    data[5]//16,
                    data[5]%16,
                    data[6]//16,
                    data[6]%16,
                    data[7]//16,
                    data[7]%16,
                    data[8]//16,
                    data[8]%16,
                    )
        #如果只有一个数据(data[3]高八位和低八位表示数据)
        if total == 20:
            data_to_save = [data[10:18],]
        elif (total-12)%8 == 0:
            if (total-12)/8 == 10*(data[9]//16)+(data[9]%16):
                data_to_save = []
                for i in range((total-12)/8):
                    data_to_save.append(data[8*i+10:8*i+18])
            else:
                # 显示的应该包含的数据数与实际接收到的数据数不符
                return 'F2'
        else:
            # 接收到的数据量既不是一个数据也不是多个数据
            return 'F1'
        print(dev_id)
        print(date_n_time)
        print(data_to_save)
        m = data_write(d, dev_id, date_n_time, data_to_save)
        return m
    #下位机特殊请求
    elif(data[0] == 10)&(data[1] == 13) & (data[-2] == 13)& (data[-1] == 10):
        print(data[2],data[3],total)
        #请求时间
        if(data[2] == 87) & (data[3] == 84) & (total==6):
            time_str = time.strftime("%Y%m%d%H%M%S",time.localtime())
            return '\r\nWT' + time_str + '\r\n'
        else:
            return 'F3'
    else:
        # 不是以回车换行开头结尾，为干扰数据，直接丢弃。
        return 'F0'

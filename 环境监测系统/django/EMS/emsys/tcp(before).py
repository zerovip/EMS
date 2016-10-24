import time
from socketserver import TCPServer, StreamRequestHandler, ForkingMixIn

from data_db import Data_db

#######################################################################################################################################
#下位机数据含义解析模块，根据通讯规则制定
#######################################################################################################################################
#数据写入
def data_write(d, dev_id, date_n_time, data_list):
    for index, data in enumerate(data_list):
        time_flo = time.mktime(time.strptime(date_n_time, '%Y-%m-%d %H:%M'))+60*index
        time_rec = time.strftime('%Y-%m-%d %H:%M', time.localtime(time_flo))
        tem_ori = 10*(data[0]//16)+(data[0]%16)+0.1*(data[1]//16)+0.01*(data[1]%16)
        if tem_ori > 80:
            tem = tem_ori-100
        else:
            tem = tem_ori
        hum = 10*(data[2]//16)+(data[2]%16)+0.1*(data[3]//16)+0.01*(data[3]%16)
        pm25 = 1000*(data[4]//16)+100*(data[4]%16)+10*(data[5]//16)+(data[5]%16)
        pm10 = 1000*(data[6]//16)+100*(data[6]%16)+10*(data[7]//16)+(data[7]%16)
        try:
            d.write_in(
                    [time_rec, dev_id],
                    [tem, hum, pm25, pm10],
                    )
        except:
            # 调用 Data_db 写入接口出现问题
            return 4
        else:
            # 成功
            return 0

#数据接收保存
def data_save(d, data):
    total = len(data_save)
    if (data[0] == 13) & (data[1] == 10) & (data[-2] == 13) & (data[-1] == 10):
        dev_id = (data[2]//16)*10+(data[2]%16)
        date_n_time = '{0}[1][2][3]-{4}{5}-{6}{7} {8}{9}:{10}{11}'.format(
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
        if total == 19:
            data_to_save = [data[9:17],]
        elif (total-12)%8 == 0:
            if (total-12)/8 == 10*(data[9]//16)+(data[9]%16):
                data_to_save = []
                for i in range((total-12)/8):
                    data_to_save.append(data[8*i+10:8*i+18])
            else:
                # 显示的应该包含的数据数与实际接收到的数据数不符
                return 2
        else:
            # 接收到的数据量既不是一个数据也不是多个数据
            return 3
        m = data_write(d, dev_id, date_n_time, data_to_save)
        return m
    else:
        # 不是以回车换行开头结尾，为干扰数据，直接丢弃。
        return 1

#######################################################################################################################################
#TCP服务器部分，直接调用Data_db的写入接口
#使用分叉处理多个客户端同时连接
#######################################################################################################################################
class Server(ForkingMixIn, TCPServer):
    pass

class Handler(StreamRequestHandler):
    def handle(self):
        addr = self.request.getpeername()
        print('Got connected with ', addr)
        d = Data_db()
        while True:
            self.data = self.request.recv(1024)
            if time.strftime('%H:%M', time.localtime()) == '00:02':
                d = Data_db()
            ret_code = data_save(d, self.data)
            self.request.sendall(ret_code.encode())
server = Server(('',1234), Handler)
server.serve_forever()

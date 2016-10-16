from socketserver import TCPServer, StreamRequestHandler, ForkingMixIn

from .data_db import Data_db

#######################################################################################################################################
#下位机数据含义解析模块，根据通讯规则制定
#######################################################################################################################################
def data_save(data):
    total = len(data_save)
    if total == 19:
        if (data[0] == 13) & (data[1] == 10) & (data[17] == 13) & (data[18] == 10):
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
            tem_ori = 10*(data[9]//16)+(data[9]%16)+0.1*(data[10]//16)+0.01*(data[10]%16)
            if tem_ori > 80:
                tem = tem_ori-100
            else:
                tem = tem_ori
            hum = 10*(data[11]//16)+(data[11]%16)+0.1*(data[12]//16)+0.01*(data[12]%16)
            pm25 = 1000*(data[13]//16)+100*(data[13]%16)+10*(data[14]//16)+(data[14]%16)
            pm10 = 1000*(data[15]//16)+100*(data[15]%16)+10*(data[16]//16)+(data[16]%16)
            Data_db().write_in(
                    [date_n_time, dev_id],
                    [tem, hum, pm25, pm10],
                    )
            return 0
        else:
            return 1
    else:




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
        while True:
            self.data = self.request.recv(1024)
            data_save(self.data)
            print(self.data)
	    self.request.sendall('getit'.encode())

server = Server(('',1234), Handler)
server.serve_forever()



msg = [
        '2016-10-10 00:00',
        1,
        ]
data = [
        20,
        20,
        1000,
        600,
        ]

d1 = Data_db()
d2 = Data_db()

d1.write_in(msg, data)
d2.write_in(msg, data)

#这里要做一个指针

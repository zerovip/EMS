import json
import time
import MySQLdb

#数据库部分要更改
db = MySQLdb.connect("localhost", "root", "lizihe970106", "ems_data", charset='utf8')
cursor = db.cursor()
sql = "SELECT id, name FROM emsys_device"
cursor.execute(sql)
results = cursor.fetchall()
db.close
all_device={}
for i in results:
    all_device[i[0]] = i[1]

#应该是只向外提供 write_in 和 read_out 接口，其余自己实现。
#有可能initial也要提供出来，这个地方没有想好是只实例化一个对象出来用initial，还是再实例化一个对象出来好
#前者可能更便捷？但后者在处理两天相交时应该更有效一些，交接完成后销毁另一个。
#暂时使用第二种方法吧，更保险一些。做一个二向循环的指针，来决定调用哪一个对象
#上两行存疑。。用类变量的话可能可以直接来。待做实验验证销毁部分。
class Data_db:
    '''定义我自己的数据库，提供接口。数据的存储分为内存和外存两部分组成。内存部分使用mmap实现多进程内存共享。
        内存存储四十分钟数据，每四十分钟（确切地说是每四十条数据）清空重置一次；每十分钟（每十条数据）写入一次；
        请求数据时优先使用内存，内存没有需要的数据时，使用外存。

        内存格式为：
        temp = {
            '1_地点一_2016-10-10':{
                '00:00':[tem, hum, pm25, pm10],
                '00:01':[],
                },
            '2_地点二_2016-10-10':{
                '00:00':[],
                },
            }

        外存在 data_db 文件夹下，存储方式为：
        temp 的键为文件名（.zero）
        对应的值作为字符串存入

        接口统一说明：

        存数据：
            write_in(msg, data):
            msg是一个列表[time, dev]，time格式为"2016-10-10 00:00", dev是一个数字。
            data是一个列表[tem, hum, pm25, pm10]

        读取数据：
            read_out(choose, start, end):
            choose是一个列表，格式示例：['00','01','11']。前一位代表设备id，后一位代表项目（0-温度，1-湿度，2-PM2.5，3-PM10）
            start 和 end 分别是起止时间，格式为"2016-10-10 00:00"，end可以为空，代表到当前时间。
            返回值是一个字典，键为choose中的每一项，值为一个列表。格式示例如下：
            {
                '00':[10,20,30,40,],
                '01':[10,20,30,40,],
                '11':[10,20,30,40,],
                }
        '''
    temp = {}

    def __init__(self):
        self.initial()

    def initial(self):
        '初始化一个内存列表。'
        # 重置内存与新建文件，建议每天23:59以后使用一次；新加设备时也可调用
        # 先把内存写入
        for i in Data_db.temp:
            self.update_data(i, Data_db.temp[i])
        # 再重置内存
        Data_db.temp = {}
        for device in all_device:
            Data_db.temp['{0}_{1}_{2}'.format(device, all_device[device], time.strftime("%Y-%m-%d", time.localtime()))] = {}

    def write_in(self, msg, data):
        '写入模块，msg是一个列表[time, dev]，time格式为"2016-10-10 00:00", dev是一个数字。data是一个列表[tem, hum, pm25, pm10]。'
        # 获取数据
        time = msg[0]
        dev_id = msg[1]
        dev_name = all_device[dev_id]
        data = data
        # 写入内存
        try:
            Data_db.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])][time[11:]] = data
        except KeyError:
            # 这里只是暂时初始化，应对特殊情况，最好还是调用self.initial()
            # 因为initial是当前系统时间，存储的时候用的时间是发过来的。所以这两句主要可以应对两天交界处的情况。
            Data_db.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])] = {}
            Data_db.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])][time[11:]] = data
        # 写入外存与清空内存
        d_num = len(Data_db.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])])
        if ( d_num==10 or d_num==20 or d_num==30 or d_num==40 ):
            key_name = '{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])
            all_data = Data_db.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])]
            self.update_data(key_name, all_data)
        if d_num == 40:
            Data_db.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])] = {}

    def update_data(self, key_name, data):
        '将内存更新至外存。'
        try:
            e_file = open("./data_db/{0}.zero".format(key_name), "r+")
        except FileNotFoundError:
            new = open("./data_db/{0}.zero".format(key_name), "w")
            new.close()
            e_file = open("./data_db/{0}.zero".format(key_name), "r+")
        finally:
            e_data = json.load(e_file)
            e_data.update(data)
            e_file.write(json.dumps(e_data))
            e_file.close()

    def read_out(self, choose, start, end=time.strftime("%Y-%m-%d %H:%M", time.localtime())):
        '''优先在内存里找，找不到再去找外存。
            根据豆豆给我的前端数据请求格式写成。
            start 和 end 分别是起止时间，choose是一个列表，格式如下：
            ['00','01','11']前一位代表设备id，后一位代表项目（0-温度，1-湿度，2-PM2.5，3-PM10）
            返回值是一个字典，键为choose中的每一项，值为一个列表
            {
                '00':[10,20,30,40,],
                '01':[10,20,30,40,],
                '11':[10,20,30,40,],
                }

            ！！注意！！
            历史查询处需要大段时间数据的请直接调用IO接口读取外存！
            请不要用for循环调取本接口获取大段时间数据！
        '''
        start_ = time.mktime(time.strptime(start,'%Y-%m-%d %H:%M'))
        end_ = time.mktime(time.strptime(end,'%Y-%m-%d %H:%M'))
        a = []
        while start_ != end_+60:
            x = time.localtime(start_)
            a.append(time.strftime('%Y-%m-%d %H:%M', x))
            start_ += 60
        rt_data = {}
        for item in choose:
            rt_data[item] = []
            for time_it in a:
                date = time_it[:10]
                time = time_it[11:]
                try:
                    rt_data[item].append(Data_da.temp['{0}_{1}_{2}'.format(item[0], all_device[item[0]], date)][time][int(item[1])])
                except:
                    try:
                        read_f = open("./data_db/{0}_{1}_{2}.zero".format(item[0], all_device[item[0]], date), "r")
                        read_d = json.load(read_f)
                        rt_data[item].append(read_d[time][int(item[1])])
                    except:
                        rt_data[item].append('null')
        return rt_data

    def __del__(self):
        '销毁一个对象。在两天相交处调用。'
        for i in Data_db.temp:
            self.update_data(i, Data_db.temp[i])

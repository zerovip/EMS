import json
import time
import pymysql

# 请先根据数据库配置更改此处并预先建立名称为 "emsys" 数据库。
host = "localhost"
user = "root"
password = "lizihe970106"

#定义自己的数据库
class Data_db:
    '''每天实例化一次，添加设备后实例化一次。使用实例化后的对象实现写入与读出数据。
        写入数据方法：
            Data_db.write_in(msg, data)
                msg(list) = [time, dev]
                    time(str) 数据时间 示例：'20161010 00:00'
                    dev(int) 设备id
                data(list) = [tem, hum, pm25, pm10]
            无返回值
        读取数据方法：
            Data_db.read_out(choose, start, end)
                choose(list) = [dev'n'item_1, dev'n'item_2]
                    dev'n'item(str) 设备号与数据项目 示例：'12' 设备1的PM2.5
                        对应关系：0-温度 1-湿度 2-PM2.5 3-PM10
                start(str) 开始时间 示例：'20161010 00:00'
                end(str) 截止时间 示例：'20161010 00:00' 为空则取当前时间为默认值
            return data(dic) 数据字典 键遍历 choose 中每一项，值为相应时间范围内数据 示例：
                {
                    '00':[10.10, 10.20, 10.30, 10.40, 10.50],
                    '23':[1111, 2222, 3333, 'null', 5555],
                    }
    '''

    def __init__(self):
        '初始化时获取所有设备并建表。'
        db = pymysql.connect(
                host = host,
                user = user,
                password = password,
                db = "ems_data",
                charset ='utf8',
                cursorclass = pymysql.cursors.DictCursor,
                )
        cursor = db.cursor()
        sql = "SELECT id, name FROM emsys_device"
        cursor.execute(sql)
        result = cursor.fetchall()
        self.results = {}
        for i in result:
            self.results[i['id']] = i['name']
        db.close()

        db = pymysql.connect(
                host = host,
                user = user,
                password = password,
                db = "emsys",
                charset ='utf8',
                cursorclass = pymysql.cursors.DictCursor,
                )
        cursor = db.cursor()
        today = time.strftime("%Y%m%d", time.localtime())
        for device in self.results:
            sql = """CREATE TABLE {0}_{1}_{2} (
                    time CHAR(6),
                    tem CHAR(6),
                    hum CHAR(6),
                    pm25 CHAR(6),
                    pm10 CHAR(6) )""".format(device, self.results[device], today)
            try:
                cursor.execute(sql)
            except pymysql.err.InternalError:
                pass
        db.close()

    def write_in(self, msg, data):
        '''写入模块。
            msg是一个列表[time, dev]：
                time格式为"20161010 00:00"；
                dev是一个数字。
            data是一个列表[tem, hum, pm25, pm10]。

            ！！注意！！
            如果发过来的时间在数据库中已经存在，则会重复写入该记录。
        '''
        db = pymysql.connect(
                host = host,
                user = user,
                password = password,
                db = "emsys",
                charset ='utf8',
                cursorclass = pymysql.cursors.DictCursor,
                )
        cursor = db.cursor()
        sql = """INSERT INTO {0}_{1}_{2} (
                time, tem, hum, pm25, pm10)
                VALUES ('{3}', '{4}', '{5}', '{6}', '{7}')""".format(
                        msg[1],
                        self.results[int(msg[1])],
                        msg[0][:8],
                        msg[0][9:],
                        data[0],
                        data[1],
                        data[2],
                        data[3],
                        )
        try:
            cursor.execute(sql)
        except pymysql.err.ProgrammingError:
            # 做应急使用，包括但不限于：
                # 两天相交处；
                # 发来的数据是未来日期的。
            # 但不要因此而永远只用一个实例对象，
            # 两天相交处以及添加设备后应重新实例化一个对象出来用。
            create_table = """CREATE TABLE {0}_{1}_{2} (
                    time CHAR(6),
                    tem CHAR(6) NOT NULL,
                    hum CHAR(6) NOT NULL,
                    pm25 CHAR(6) NOT NULL,
                    pm10 CHAR(6) NOT NULL,
                    PRIMARY KEY (time) )""".format(msg[1], self.results[int(msg[1])], msg[0][:8])
            try:
                cursor.execute(create_table)
                cursor.execute(sql)
            except pymysql.err.InternalError:
                pass
            print(sql)
            raise
        db.commit()
        db.close()

    def read_out(self, choose, start,
            end=time.strftime("%Y%m%d %H:%M", time.localtime())):
        '''根据豆豆给我的前端数据请求格式写成。

            start 和 end 分别是起止时间。
            choose是一个列表，格式如下：
                示例：['00','01','11']
                前一位代表设备id，后一位代表项目（0-温度，1-湿度，2-PM2.5，3-PM10）

            返回值是一个字典，键为choose中的每一项，值为一个列表
                {
                    '00':[10,20,30,40,],
                    '01':[10,20,30,40,],
                    '11':[10,20,30,40,],
                    }

            ！！注意！！
            1.如果查询某一设备某一大段时间的所有数据，
                请直接用 pymysql 模块读取数据库，
                该方法为前端做折线图所专用，
                破坏了原本的数据格式，
                除非需要某个项目的数据，
                其他情况不要试图用此方法获取数据；
            2.如果在记录中同一时间数据出现多条，
                默认选取第一条，即最先被记录的数据，
                如需要通过比较删除其他数据，
                可以参考本方法中 SELECT 之后的 len 方法获取。
        '''
        start_ = time.mktime(time.strptime(start,'%Y%m%d %H:%M'))
        end_ = time.mktime(time.strptime(end,'%Y%m%d %H:%M'))
        time_range = []
        while start_ != end_+60:
            x = time.localtime(start_)
            time_range.append(time.strftime('%Y%m%d %H:%M', x))
            start_ += 60

        return_data = {}
        db = pymysql.connect(
                host = host,
                user = user,
                password = password,
                db = "emsys",
                charset ='utf8',
                cursorclass = pymysql.cursors.DictCursor,
                )
        cursor = db.cursor()
        for item in choose:
            item_data = []
            it_id = int(item[0])
            it_need = int(item[1])
            need_dic = {0:'tem', 1:'hum', 2:'pm25', 3:'pm10',}
            for time_it in time_range:
                sql = "SELECT tem, hum, pm25, pm10 FROM {0}_{1}_{2} WHERE time = '{3}'".format(
                        it_id,
                        self.results[it_id],
                        time_it[:8],
                        time_it[9:],
                        )
                try:
                    cursor.execute(sql)
                    data_get = cursor.fetchall()
                    if len(data_get) != 0:
                        item_data.append(data_get[0][need_dic[it_need]])
                    else:
                        item_data.append('null')
                except pymysql.err.ProgrammingError:
                    item_data.append('null')
            return_data[item] = item_data
        db.close()
        return return_data


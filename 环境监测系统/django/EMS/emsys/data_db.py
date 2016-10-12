import json
import time

from .models import Device


class Data_db:
    '''定义我自己的数据库，提供接口。数据的存储分为内存和外存两部分组成。
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
        对应的值作为字符串存入'''

    def initial(self):
        '初始化一个内存列表。'
        # 重置内存与新建文件，建议每天23:59以后使用一次；新加设备时也可调用
        # 先把内存写入
        for i in temp:
            self.update_data(i, temp[i])
        # 再重置内存
        self.temp = {}
        all_device = Device.objects.values()
        for device in all_device:
            self.temp['{0}_{1}_{2}'.format(device.id, device.name, time.strftime("%Y-%m-%d", time.localtime()))] = {}

    def write_in(self, msg, data):
        '写入模块，msg是一个列表[time, dev]，time格式为"2016-10-10 00:00", dev是一个数字。data是一个列表[tem, hum, pm25, pm10]。'
        # 获取数据
        time = msg[0]
        dev_id = msg[1]
        dev_name = Device.objects.get(id=dev_id).name
        data = data

        # 写入内存
        self.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])][time[11:]] = data

        # 写入外存与清空内存
        d_num = len(self.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])])
        if ( d_num==10 or d_num==20 or d_num==30 or d_num==40 ):
            key_name = '{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])
            all_data = self.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])]
            self.update_data(key_name, all_data)
        if d_num == 40:
            self.temp['{0}_{1}_{2}'.format(dev_id, dev_name, time[:10])] = {}

    def update_data(self, key_name, data):
        '将内存更新至外存。'
        e_file = open("./data_db/{0}.zero".format(key_name), "r+")
        e_data = json.load(e_file)
        e_data.update(data)
        e_file.write(json.dumps(e_data))
        e_file.close()

from django.db import models

#设备表
class Device(models.Model):
#    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    discri = models.CharField(max_length=80)
    tem = models.BooleanField(default=True)
    hum = models.BooleanField(default=True)
    pm25 = models.BooleanField(default=True)
    pm10 = models.BooleanField(default=True)
    def __str__(self):
        return self.name

#用户组表
class Usergroup(models.Model):
    groupname = models.CharField(max_length=30, unique=True)
    discri = models.CharField(max_length=80)
    num = models.IntegerField()
    charge = models.ManyToManyField(Device)    #在这个组内新建用户时默认的  管理设备范围
    tem = models.BooleanField(default=True)    #温度数据管理权限
    hum = models.BooleanField(default=True)    #湿度数据管理权限
    pm25 = models.BooleanField(default=True)    #pm2.5数据管理权限
    pm10 = models.BooleanField(default=True)    #pm10数据管理权限
    device = models.BooleanField()    #设备管理权限
    def __str__(self):
        return self.groupname

#用户表
class User(models.Model):
    MASTER_CHOICE = (
        ('N', '无'),
        ('G', '组管理员'),
        ('S', '超级管理员'),
    )
    group = models.ForeignKey(Usergroup)
    username = models.CharField(max_length=30, unique=True)
    realname = models.CharField(max_length=30, null=True)
    password = models.CharField(max_length=50)
    email = models.EmailField()
    charge = models.ManyToManyField(Device)    #该用户的权限
    tem = models.BooleanField(default=True)
    hum = models.BooleanField(default=True)
    pm25 = models.BooleanField(default=True)
    pm10 = models.BooleanField(default=True)
    device = models.BooleanField()
    master = models.CharField(max_length=3, choices=MASTER_CHOICE)
    def __str__(self):
        return self.username

#devices = Device.objects.all()
#如果模型基类的方法不能成功，则用这种方法，把所有的设备数据存在一起，每隔十天导出来一次
#数据组表，每十天进行重写时调用写入
'''
class Dataviews(models.Model):
    device = models.ForeignKey(Device)
    time = models.DateTimeField()
    tem = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    hum = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    pm25 = models.IntegerField(null=True)
    pm10 = models.IntegerField(null=True)
'''
'''
#数据表基类
class Database(models.Model):
    tem = models.FloatField(max_digits=3, decimal_places=1)
    hum = models.FloatField(max_digits=4, decimal_places=2)
    pm25 = models.IntegerField()
    pm10 = models.IntegerField()
    class Meta:
        abstract = True

#数据表调用(根据设备)
for device in devices:
    class Dataviews(Database):
        class Meta(Database.Meta):
            db_table = 'dataviews{0}'.format(device.id)
'''

#如果上述方法不成功，也可以先这样建三个表看看
'''
class Dataviews1(Database):
    pass
class Dataviews2(Database):
    pass
class Dataviews1(Database):
    pass
'''

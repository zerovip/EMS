from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import User, Usergroup, Device

#用户表单，在添加用户、编辑用户页面渲染
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
                'password':forms.TextInput(attrs={
                    'type':'password',
                    }),
                }
        labels = {
                'group':_('所属组'),
                'username':_('用户名'),
                'realname':_('真实姓名'),
                'password':_('密码'),
                'email':_('邮箱'),
                'charge':_('数据管辖范围'),
                'tem':_('温度'),
                'hum':_('湿度'),
                'pm25':_('PM2.5'),
                'pm10':_('PM10'),
                'device':_('设备管理权'),
                'master':_('用户管理权'),
                }
        help_texts = {
                'group':_('方便用户管理，组内的每个人的权限可以不同。'),
                'charge':_('数据管理包括查询历史数据、下载数据。'),
                'device':_('设备管理包括对设备的添加、删除，设备信息的编辑，反向远程控制，与设置报警阈值。'),
                'master':_('超级管理员享有对所有用户的管理权限，组管理员享有对该用户所在组的所有用户的管理权限，其他人只拥有对自己基本信息的修改权限。'),
                }

#编辑自己页的表单，在个人信息编辑页渲染
class SelfForm(ModelForm):
    class Meta:
        model = User
        fields = [
                'username',
                'realname',
                'password',
                'email',
                ]
        widgets = {
                'password':forms.TextInput(attrs={
                    'type':'password',
                    })
                }
        labels = {
                'username':_('用户名'),
                'realname':_('真实姓名'),
                'password':_('密码'),
                'email':_('邮箱'),
                }

#用户组表单，在添加用户组、编辑用户组页面渲染
class UsergroupForm(ModelForm):
    class Meta:
        model = Usergroup
        exclude = ['num']
        labels = {
                'groupname':_('组名'),
                'discri':_('描述'),
                'charge':_('数据管辖范围'),
                'tem':_('温度'),
                'hum':_('湿度'),
                'pm25':_('PM2.5'),
                'pm10':_('PM10'),
                }
        help_texts = {
                'discri':_('可以用来标识该组的职责。'),
                }

#设备表单，在添加设备、编辑设备页面渲染
class DeviceForm(ModelForm):
    class Meta:
        model = Device
        fields = '__all__'
        labels = {
                'name':_('设备名'),
                'discri':_('描述'),
                'tem':_('温度'),
                'hum':_('湿度'),
                'pm25':_('PM2.5'),
                'pm10':_('PM10'),
                }
        help_texts = {
                'discri':_('可以用来标识该设备的其他信息。'),
                }


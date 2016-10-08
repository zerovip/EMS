from django import template

register = template.Library()

def key_myself_1(d, key_name):
    return d[key_name][1]

def key_myself_0(d, key_name):
    return d[key_name][0]

register.filter('key_myself_1', key_myself_1)
register.filter('key_myself_0', key_myself_0)

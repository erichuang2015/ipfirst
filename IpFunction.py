# -*- coding: utf-8 -*-
# IP数据库格式详解 qqzeng-ip.dat
# 编码：UTF8  字节序：Little-Endian
# 返回多个字段信息（如：亚洲|中国|香港|九龙|油尖旺|新世界电讯|810200|Hong Kong|HK|114.17495|22.327115）
# 此脚本为函数定义
import struct, socket, os
import pandas as pd
try:
    import mmap
except ImportError:
    mmap = None

def ip2long(ip):
    _ip = socket.inet_aton(ip)
    return struct.unpack("!L", _ip)[0]
def long2ip(num):
    l = struct.pack("!L", num)
    ip = socket.inet_ntoa(l)
    return ip
def int_to_4byte(st):
    return struct.pack('<L', st)
def int_to_3byte(st):
    return struct.pack('<L', st)[:3]
def int_to_1byte(st):
    return struct.pack('B', st)

# 将ip地址中的0开头的字段的0去掉
def replace_all(s):
    for i in xrange(0, 10):
        s1 = '00' + str(i)
        if s1 in s:
            s2 = s.replace(s1, str(i))
            break
        else:
            s2 = s
    for i in xrange(11,100):
        s5 = '0'+str(i)
        if s5 in s2 :
            s3 = s2.replace(s5,str(i))
            break
        else:
            s3 = s2
    return s3

# 将具有多个isp的运营商的第一个作为运营商
def get_1isp(s):
    isps = s.split('/')
    isp = isps[0]
    return isp

# 将运营商中的网址替换成*
def replace_com(s):
    if '.' in s:
        s1 = '*'
    else:
        s1 = s
    return s1

# 将运营商中的长字节规整到12个字节
def cat_isp(s):
    if len(s)>12:
        s1 = s[:12]
    else:
        s1 = s
    return s1

# 替换地址中的*
def replace_star(s):
    if '|*' in s:
        s1 = s.replace('|*','')
    else:
        s1 = s
    return s1

# 将直辖市转换成单个城市
def bstc(s):
    if '北京' in s:
        s1 = s.replace('北京|北京','北京')
    elif '上海' in s:
        s1 = s.replace('上海|上海','上海')
    elif '重庆' in s:
        s1 = s.replace('重庆|重庆', '重庆')
    elif '天津' in s:
        s1 = s.replace('天津|天津', '天津')
    else:
        s1 = s
    return s1

# 返回地址的长度
def set_loc(s,content):
    kk = content.loc[content['content']==s,'loc'].values
    if len(kk)>0:
        return kk[0]
    else:
        print str(kk)+str(s)

# 获取ip段的前缀
def get_prefix(s):
    ns = s.split('.')
    pre = int(ns[0])
    return pre

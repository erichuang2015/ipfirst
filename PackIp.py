# -*- coding: utf-8 -*-
# IP数据库格式详解 qqzeng-ip.dat
# 编码：UTF8  字节序：Little-Endian
# 返回多个字段信息（如：亚洲|中国|香港|九龙|油尖旺|新世界电讯|810200|Hong Kong|HK|114.17495|22.327115）
import pandas as pd

import IP.IpFunction as f

try:
    import mmap
except ImportError:
    mmap = None

# 打开要压缩的ip库原始文件,绝对地址
ip_origin = pd.read_csv("/home/tandy/17monip/IP/ipbase-isp.dat",sep=' ',names=['start_ip','end_ip','country','province','city','area','isp','timezone','ec','type'])

# 只压缩中国的ip段
ch = ip_origin.loc[ip_origin['country']=='中国']

# 获得ip库原始数据时需要先对数据进行一些处理，比如替换，置NA等等;其实也可以合并后再处理
# 下面给出一些我在处理时的一些方式,在处理过程中可以随时将多余的列及时删除以节省内存

# 首先将运营商长度超过12字节的处理成12字节
# ch['isp'] = [f.get_1isp(x) for x in ch['isp'].values]
ch.loc[:,('isp')] = [f.get_1isp(x) for x in ch['isp'].values]
# ch['isp'] = [f.cat_isp(x) for x in ch['isp'].values]
ch.loc[:,('isp')] = [f.cat_isp(x) for x in ch['isp'].values]
# 处理运营商，非大陆的运营商可能有网站，而我们目前暂不需要
# ch['isp'] = [f.replace_com(x) for x in ch['isp'].values]
ch.loc[:,('isp')] = [f.replace_com(x) for x in ch['isp'].values]
# 正常情况下将IP后面的所有内容返回
# 定制情况可以根据不同的需求返回不同的内容，比如我们目前只需返回城市和运营商
# ch['content'] = ch['province']+'|'+ch['city']+"|"+ch['isp']
ch.loc[:,('content')] = ch['province']+'|'+ch['city']+"|"+ch['isp']
# 将地址中的*去掉以节省点空间，不去掉会很规整
# ch['content'] = [f.replace_star(x) for x in ch['content'].values]
ch.loc[:,('content')] = [f.replace_star(x) for x in ch['content'].values]
# 将ip中的0去掉，便于转换
for x in xrange(0,4):
    # ch['start_ip'] = [f.replace_all(x) for x in ch['start_ip'].values]
    # ch['end_ip'] = [f.replace_all(x) for x in ch['end_ip'].values]
    ch.loc[:, ('start_ip')] = [f.replace_all(x) for x in ch['start_ip'].values]
    ch.loc[:, ('end_ip')] = [f.replace_all(x) for x in ch['end_ip'].values]
# 重置索引,删除多余的列
ch = ch.reset_index()
del ch['index']
del ch['country'],ch['province'],ch['city'],ch['area'],ch['isp'],ch['timezone'],ch['ec'],ch['type']
# 将地址保存起来，作为写成二进制的原始数据
content = pd.DataFrame(ch['content'].unique(),columns=['content'])
# content['lenth'] = [len(x) for x in content['content'].values]
content.loc[:, ('lenth')] = [len(x) for x in content['content'].values]
# 设置地址的流地址
# content['loc'] = 16
content.loc[:, ('loc')] = 16
for i in xrange(1,len(content)):
    content['loc'][i] = content['loc'][i-1]+content['lenth'][i-1]

# 获取前缀
prefix = pd.DataFrame([f.get_prefix(x) for x in ch['start_ip'].values],columns=['prefix'])
prefix = pd.DataFrame(prefix['prefix'].unique(),columns=['prefix'])

prefix['start'] = prefix['end'] = 0
# 获取前缀的索引地址
for i in xrange(0,len(prefix)):
    for j in xrange(0,len(ch)):
        if ch['start_ip'][j].split('.')[0] == str(prefix['prefix'][i]):
            prefix['end'][i] = ch.index[j]

for i in xrange(0,len(prefix)):
    for j in xrange(0,len(ch)):
        if ch['start_ip'][j].split('.')[0] == str(prefix['prefix'][i]):
            prefix['start'][i] = ch.index[j]
            break

prefix['start'][0] = 1

# 设置地址信息的长度和位置
ch['len'] = [len(x) for x in ch['content'].values]
ch['loc'] = [f.set_loc(x,content) for x in ch['content'].values]

# 将ip转换成long
ch['start_ip'] = [f.ip2long(x) for x in ch['start_ip'].values]
ch['end_ip'] = [f.ip2long(x) for x in ch['end_ip'].values]
del ch['content']

# 将压缩的二进制文件写入此文件
myip = open("ip-utf8.dat",'wb')
# 文件头    16字节(4-4-4-4)
# [索引区第一条流位置][索引区最后一条流位置][前缀区第一条的流位置][前缀区最后一条的流位置]
s1 = content['loc'][len(content)-1]+content['lenth'][len(content)-1]
myip.write(f.int_to_4byte(s1))
s2 = len(ch) * 12 + s1
myip.write(f.int_to_4byte(s2 - 12))
myip.write(f.int_to_4byte(s2))
myip.write(f.int_to_4byte(s2 + (len(prefix) - 1) * 9))

# 写入地址数据
# 内容区    长度无限制
# [地区信息][地区信息]……唯一不重复
for x in content['content'].values:
    myip.write(x)

# 建立索引区
# 索引区    12字节(4-4-3-1)
# [起始IP][结束IP][地区流位置][地区流长度]
for y in ch.values:
    myip.write(f.int_to_4byte(y[0]))
    myip.write(f.int_to_4byte(y[1]))
    myip.write(f.int_to_3byte(y[3]))
    myip.write(f.int_to_1byte(y[2]))
# //前缀区   9字节(1-4-4)
# [0-255][索引区start索引位置][索引区end索引位置]
for z in prefix.values:
    myip.write(f.int_to_1byte(z[0]))
    myip.write(f.int_to_4byte(z[1]))
    myip.write(f.int_to_4byte(z[2]))
myip.close()


# coding=utf-8

import threading
import requests
import time
import ConfigParser
from requests.adapters import HTTPAdapter

# 测试上传位置数据
j={'id': '297089', 'imei': '353008061335127', 'isResult': '0', 'latitude': '22.553129', 'longitude': '113.941821',
   'positionType': '0', 'precision': '25.0'}
# 位置上报接口
url='http://.../repeatReportData'


class MultiThreadInterfaceTest():
    def __init__(self,conf_path):
        self.conf=ConfigParser.ConfigParser()
        self.conf.read(conf_path)
        
def testdb():
    headers={"Content-Type": "application/json"}
    re=requests.session ()
    try:
        #发起第一次上报位置
        re.post (url=url, json=j, headers=headers)
    except Exception as e:
        print str (e)
        #睡眠3s
        time.sleep (3)
        re.mount ('http://', HTTPAdapter (max_retries=3))
        try:
            #发起第二次重试上报位置
            re.post (url=url, json=j, headers=headers)
            print 'Thread retry once success:%s' % threading.Thread.name
        except Exception as e:
            try:
                time.sleep (3)
                # 发起第三次重试上报位置
                re.post (url=url, json=j, headers=headers)
                print 'Thread retry twice success:%s' % threading.Thread.name
            except Exception:
                print 'Thread retry twice file:%s' % threading.Thread.name

def test_Muli_by_Tread(threadnum):
    th=threadnum  # 并发线程数
    Threadgroup=[]  # 线程组
    start_time=time.time ()
    for t in range (th):
        thread=threading.Thread (target=testdb)
        Threadgroup.append (thread)
    for t in Threadgroup:
        t.start ()
    for t in Threadgroup:
        t.join ()
    stop_time=time.time ()
    print '总共耗时：%f秒' % (stop_time - start_time)


if __name__ == '__main__':
    threadnum=10000
    test_Muli_by_Tread(threadnum)

from multiprocessing import Process
import multiprocessing
import requests, json, time
from requests.adapters import HTTPAdapter

# j={"baseStation":{"bid":"0","bss":"9","isWifi":"0","mcc":"460","mnc":"1","nid":"0","sid":"0","type":"UNKNOWN"},"id":"297089","imei":"353008061335127","isResult":"0","latitude":"22.553129","longitude":"113.941821","positionType":"0","precision":"25.0"}
j={}
j['id']='297089'
j['imei']='353008061335127'
j['isResult']='0'
j['latitude']='22.553129'
j['longitude']='113.941821'
j['positionType']='0'
j['precision']='25.0'

url='http://..../repeatReportData'


def testdb(a, lock):
    headers={"Content-Type": "application/json"}
    re=requests.session ()
    re.mount ('http://', HTTPAdapter (max_retries=3))
    r=re.post (url=url, json=j, headers=headers)
    with lock:
        if r.status_code != 200:
            a+=1


if __name__ == "__main__":
    process=[]
    num=10000
    lock=multiprocessing.Lock ()
    a=1
    for n in range (num):
        p=Process (target=testdb, args=(a, lock))
        p.start ()
        p.join ()
    print a

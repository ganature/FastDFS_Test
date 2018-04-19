# coding=utf-8
# coding=utf-8
from elasticsearch import Elasticsearch
import requests, sqlite3,time,os
import random,json,logging
import exceptions
class data_source ():
    def __init__(self, database='Log_Data.db', table=None):
        """
        :param database: sqlite3文件
        :param table: 保存日志数据的表名
        """
        if table:
            self.table=table
        else:
            self.table='Log_Data'
        if database:
            self.con = sqlite3.connect ("Log_Data.db")
            self.cur = self.con.cursor ()
        else:
            self.con = sqlite3.connect ("Log_Data.db")
            self.cur = self.con.cursor ()
            self.cur.execute (
                'CREATE TABLE %s(mindex VARCHAR (30),id INT (8),name VARCHAR (30),age INT (8),country VARCHAR (30));' % self.table)
            self.con.commit ()
        self.j = {
            "msgindex": "client1",
            "id": 1,
            "name": "xiao",
            "age": 21,
            "country": "CN"
        }

    def insert_batch_data(self):
        for i in range (73353,100000):
            self.j["id"] = i
            self.j["name"] = random.choice (['xiao', 'Jack', 'Tom', 'Wang'])
            self.j["age"] = random.randint (1, 100)
            self.j["country"] = random.choice (['CN', 'US', 'EU', 'IT'])
            sql = "Insert into Log_Data(mindex,age,name,id,country) VALUES('%s',%d,'%s',%d,'%s')" % (
            self.j['msgindex'], self.j['age'], self.j['name'], self.j['id'], self.j['country'])
            self.cur.execute (sql)
            self.con.commit ()

    def query_all_data(self):
        sql = 'select * from %s' % self.table
        self.cur.execute (sql)
        all_data = self.cur.fetchall ()
        return all_data

    def query_data_count(self):
        sql = 'select count(*) from %s' % self.table
        self.cur.execute (sql)
        all_data = self.cur.fetchall ()
        return all_data[0][0]

    def query_data_by_id(self,id):
        sql='select id from %s where id=%d'%(self.table,id)
        self.cur.execute (sql)
        d=self.cur.fetchall()
        return d


class es_Test ():
    def __init__(self,hosts =None,upload_hosts=None):
        """

        :param hosts: 查询url（elasticsearch）
        :param upload_hosts: 上传url（logstash）
        """
        if hosts is None:
            self.hosts = 'http://192.168.0.20:9200'
        else:
            self.hosts=hosts
        if upload_hosts is None:
            self.upload_hosts = 'http://192.168.0.20:8889'
        else:
            self.upload_hosts =upload_hosts
        self.es = Elasticsearch (self.hosts)
        self.re = requests
        self.log_file='%s_es.log'%(time.strftime ("%Y%m%d", time.localtime ()))
        logging.basicConfig (level=logging.ERROR,
                             format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                             datefmt='%a, %d %b %Y %H:%M:%S',
                             filename=self.log_file,
                             filemode='a')
        self.datebase=data_source()
        self.index='client1-%s'%(time.strftime ("%Y-%m", time.localtime ()))

    def es_search(self, index, body):
        """
        查询日志
        :param index:
        :param body:
        :return:
        """
        try:
            r=self.es.search (index=index, body=body)
            return r
        except Exception as e:
            logging.error(e)

    def es_get(self, index, id):
        return self.es.get (index=index, id=id)

    def es_upload(self, j):
        """
        通过logstash POST请求上传日志
        :param json:
        :return:
        """
        requests.post (url=self.upload_hosts, json=j)

    def batch_es_upload(self):
        """
        批量上传日志
        :return:
        """
        for j in self.datebase.query_all_data ():
            json =["msgindex",
                "id",
                "name",
                "age",
                "country"]
            d=dict(zip(json,j))
            self.es_upload (d)

    def es_delete(self, body=None):
        """
        python的elasticsearch模块删除日志，DELETE请求
        :param index:
        :param body:
        :return:
        """
        if body is None:
            body = {"query": {"match_all": {}}, }
        try:
            e=self.es.delete_by_query (index=self.index, doc_type='doc', body=body)
            logging.info(e)
        except Exception as ee:
            logging.error(ee)

    @staticmethod
    def dict_to_json(dict):
        return json.dumps(dict)

    @staticmethod
    def json_to_dict(j):
        return json.loads(j)

    def query_result_verify(self,re):
        for r in re['hits']['hits']:
            return r['_source']['id']


def test_stable():
    """
    文件上传稳定性测试，连续上传文件
    :return:
    """
    e=es_Test()
    d=data_source()
    t=0
    s=0
    count=d.query_data_count()
    try:
        while True:
            t+=1
            e.batch_es_upload()
            for i in range(count):
                r=e.es_search(index=e.index,body={"query":{"match":{"id":i}}})
                id=e.query_result_verify(r)
                if len(d.query_data_by_id(id))>0:
                    s += 1
                else:
                    logging.info('id:%s未查询到数据'%id)
            with open('es_test.log','a') as es:
                es.write('第%s次上传查询成功'%t)
                es.write('\n')
            #logging.info ('所有上传日志查询成功')
            e.es_delete()
            with open('es_test.log','a') as es:
                es.write ('第%s次上传日志删除成功' % t)
                es.write ('\n')
            #logging.info ('所有上传日志删除成功')
    except Exception as e:
        print e
    finally:
        logging.info('循环次数为：%d;成功查询次数为：%d'%(t,s))
        print '循环次数为：%d;成功查询次数为：%d'%(t,s)

if __name__ == "__main__":
    j={"baseStation":{"bid":"0","bss":"9","isWifi":"0","mcc":"460","mnc":"1","nid":"0","sid":"0","type":"UNKNOWN"},"id":"297089","imei":"353008061335127","isResult":"0","latitude":"22.553129","longitude":"113.941821","positionType":"0","precision":"25.0"}
    url=''
    while True:
        for i in range(1):
            re=requests.post(url=url,json=json.loads(j))
            print re.status_code

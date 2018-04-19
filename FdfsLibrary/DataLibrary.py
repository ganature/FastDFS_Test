#coding=utf-8

import sqlite3
class Data():
    def __init__(self,database='upload_file_reponse.db'):
        """
        连接sqlite3数据库
        :param database: 数据库文件路径  如：upload_file_reponse.db
        """
        self.con=sqlite3.connect(database)
        self.cur=self.con.cursor()

    def init_data(self,table='F_upload_data'):
        sql='Create table %s(Status Varchar(30),StorageIP Varchar(30),' \
            'Remote_file_id Varchar(100),Group_name Varchar(30),Local_file_name Varchar(50),Uploaded_size Varchar(20))'%table
        self.cur.execute (sql)


    def insert_data(self,insert_ret):
        sql='Insert Into F_upload_data (Status,StorageIP,Remote_file_id,Group_name,Local_file_name,Uploaded_size)values(?,?,?,?,?,?)'
        self.cur.execute(sql,insert_ret)
        self.con.commit()

    def select_data(self,select_ret):
        sql='Select * from F_upload_data where Remote_file_id=?'
        self.cur.execute (sql, select_ret)
        return self.cur.fetchall()

    def query_id(self):
        sql='Select Remote_file_id from F_upload_data'
        self.cur.execute (sql)
        return self.cur.fetchall ()

    def select_all_data(self):
        sql='Select * from F_upload_data'
        self.cur.execute(sql)
        data=self.cur.fetchone()
        print type(data)


if __name__=='__main__':
    data_dict={'Status': 'Upload successed.',
               'Storage IP': '120.79.19.89',
               'Remote file_id': 'group1/M00/00/01/rBJvi1oLuruEJjsEAAAAALmk59M0514336',
               'Group name': 'group1',
               'Local file name': 'F:\\UploadTest\\data\\/file_9',
               'Uploaded size': '100.00KB'}
    """d=Data()
    d.conn_sqlite('upload_file_reponse.db')
    #d.init_data()
    print data_dict['Remote file_id']
    print type(data_dict['Remote file_id'])
    #d.insert_data(insert_ret=data_dict.values())
    re=d.select_data(select_ret=data_dict['Remote file_id'])
    print 
    
    
    REPORT_TMPL='aa%(test)s'
    a=REPORT_TMPL % dict(test=''.join(['a','2','c']))
    print a"""
    d=Data()
    d.init_data()
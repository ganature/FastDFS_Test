# coding=utf-8
"""
Author: qiaoxudong
"""
import os, sys, time, logging, json, re
import shutil
import threading
from threading import current_thread
from datetime import datetime
from random import randint
from DataLibrary import Data

try:
    from fdfs_client.client import *
    from fdfs_client.exception import *
except ImportError:
    import_path=os.path.abspath ('../')
    sys.path.append (import_path)
    from fdfs_client.client import *
    from fdfs_client.exceptions import *


class FdfsLibrary:
    ROBOT_LIBRARY_SCOPE='GLOBAL'
    ROBOT_LIBRARY_VERSION='1.0.1'

    def __init__(self):
        """
        FastDFS文件存储服务器稳定性测试
        File storage performance test for FastDFS;
        File Storage Stability Test for FastDFS;
        """
        self.track_IP=None
        self.track_Port='22122'
        self.path_client_conf='client.conf'
        self.data_dir='E:/data'
        logging.basicConfig (level=logging.DEBUG,
                             format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                             datefmt='%a, %d %b %Y %H:%M:%S',
                             filename='file_upload.log',
                             filemode='a')
        self.loctime=time.strftime ("%Y%m%d", time.localtime ())
        self.upload_message=str (self.loctime) +'_message.txt'
        self.upload_result=str (self.loctime) + '_upload_result.json'
        self.client=Fdfs_client (self.path_client_conf)
        self.database=Data ()

    def get_track_info(self, path_client_conf, data_dir):
        """
        :param path_client_conf: 配置文件路径 如：F:\\UploadTest\\client.conf
        :param data_dir: 上传文件路径  如：F:\\UploadTest
        :return:
        """
        self.path_client_conf=path_client_conf
        self.data_dir=data_dir

        logging.info (msg=u'获取client.conf的路径：' + self.path_client_conf)
        logging.info (msg=u'获取上传文件目录：' + self.data_dir)
        return self.path_client_conf

    def get_tracker_server(self):
        """
        获取tracker_IP
        :return:
        """
        fd=Fdfs_ConfigParser ()
        fd.read (self.path_client_conf)
        return fd.get (section='__config__', option='tracker_server')

    def serial_upload_files(self, count):
        '''
        串行上传文件
        :return:
        '''
        result={}
        starttime=time.time ()
        stime=self.time_change (starttime)
        logging.info (msg=u'文件上传开始时间：%s' % stime)
        data_filename=self.data_dir + '/file_'
        s=0
        f=0
        sizes=0
        try:
            for i in range (0, int (count)):
                filename=data_filename + str (i) + '.txt'
                logging.info (msg=u'开始上传文件：%s' % filename)
                ret=self.client.upload_by_filename (filename)
                if ret['Status'] == 'Upload successed.':
                    s+=1
                    logging.info (msg=u'上传成功')
                else:
                    f+=1
                    logging.info (msg=u'上传失败')
                upload_time=time.strftime ("%Y-%m-%d %H:%M:%S", time.localtime ())
                self.save_upload_reponse (upload_time + ':' + str (ret))
                self.database.insert_data (insert_ret=ret.values ())
                sizes+=os.path.getsize (ret['Local file name'])
        except Exception, e:
            print 'error' + str (e)
        endtime=time.time ()
        etime=self.time_change (endtime)
        logging.info (msg=u'上传结束时间：%s' % etime)
        end_time=time.strftime ("%Y-%m-%d %H:%M:%S", time.localtime ())
        content_success=end_time + ': total ' + str (s) + ' Successed'
        content_fail=end_time + ': total ' + str (f) + ' Fail'
        logging.info (msg='Successed:%s' % s)
        logging.info (msg='Fail:%s' % f)
        self.save_upload_reponse (content_success)
        self.save_upload_reponse (content_fail)
        t=endtime - starttime
        logging.info (msg=u'上传文件总共大小为：%f k' % sizes)
        result['starttime']=self.time_change (starttime)
        result['endtime']=endtime
        result['count']=count
        result['success']=s
        result['failure']=f
        result['spend_time']=str (round (float (t), 3)) + 's'
        result['speed']=str (round (float (sizes / t), 2)) + 'kb/s'
        result['sizes']=sizes
        logging.info (msg=u'上传完成')
        return result

    def concurrent_upload_files(self):
        """
        并行上传文件
        :return:
        """
        filename=self.data_dir + '/file_559.txt'
        s=0
        f=0
        result={}

        starttime=time.time ()
        try:
            client=Fdfs_client ('client.conf')
            ret=client.upload_by_filename (filename)
            if (ret['Status'] == 'Upload successed.'):
                s+=1
                logging.info (msg=u'上传成功')
            else:
                f+=1
                logging.info (msg=u'上传失败')
            upload_time=time.strftime ("%Y-%m-%d %H:%M:%S", time.localtime ())
            self.save_upload_reponse (upload_time + ':' + str (ret))
            # self.database.insert_data(ret.values())
        except Exception, e:
            print "error" + str (e)
        endtime=time.time ()
        t=endtime - starttime
        result['spend_time']=str (round (float (t), 3)) + 's'
        result['success']=s
        result['failure']=f
        with open (self.upload_result, 'a') as outfile:
            json.dump (result, outfile, ensure_ascii=False)
            outfile.write ('\n')
        time.sleep (1)

    def deleta_upload_file(self, remote_file_id):
        """
        删除已经上传的文件
        :param remote_file_id:
        :return:
        """
        try:
            logging.info (msg=u'即将删除ID：%s的文件' % remote_file_id)
            re=self.client.delete_file (remote_file_id=remote_file_id)
            if re[0] == 'Delete file successed.':
                logging.info (msg=u'ID为%s已经删除' % remote_file_id)
            return re
        except Exception as e:
            logging.error (msg=e)
        finally:
            pass

    def batch_deleta_upload_file(self):
        """
        批量删除已经上传的文件
        :return:
        """
        file_list = self.get_rID_from_db()
        #file_list=self.analysis_log ()
        for f in file_list:
            self.deleta_upload_file (remote_file_id=str (f))

    def query_upload_file(self, remote_file_id):
        pass

    def batch_create_files(self, count, min_size, max_size):
        """
        批量生成文件
        :param max_size: 生成的最大文件大小，
        :param min_size: 生成的最小文件大小，
        :param data_dir: 生成文件的目标路径
        :param count:   生成文件的个数
        :return:
        """
        if not os.path.exists (self.data_dir):
            logging.info (msg=u'创建文件夹：%s' % self.data_dir)
            os.makedirs (self.data_dir)
        logging.info (msg=u'开始随机生成文件...')
        for x in range (0, count):
            with open ("%sfile_%d.txt" % (self.data_dir, x), 'wb') as fout:
                fout.write (os.urandom (1024 * randint (min_size, max_size)))
        logging.info (msg=u'随机生成文件完毕')

    def batch_delete_files(self, Folderpath):
        """
        删除批量生成的文件
        :param Folderpath:
        :return:
        """
        try:
            shutil.rmtree (Folderpath)
            logging.info ("Folder deleted: %s" % (Folderpath))
        except:
            msg="Failed to delete folder: %s" % (Folderpath)
            logging.error (msg)
            pass

    def get_sizes_files(self):
        """
        统计批量生产文件的总共大小
        :param path: 文件路径
        :return: 返回文件大小：如1000k
        """
        sizes=0
        for d in os.listdir (self.data_dir):
            s=os.path.getsize (os.path.join (self.data_dir, d))
            sizes+=s / 1024
        return sizes

    def save_upload_reponse(self, content):
        """
        保存上传文件返回的响应信息
        :param content: 返回的响应信息
        :return:
        """
        file=self.upload_message
        with open (file, 'a') as f:
            f.write (content)
            f.write ('\n')
            f.close ()

    def analysis_log(self):
        filename=self.upload_message
        id_list=[]
        try:
            with open (filename, 'r') as anal:
                for a in anal.readlines ():
                    l=a.split ()
                    s=l[9].rstrip (',"').lstrip ('\'"')
                    s=s.rstrip ('\'')
                    id_list.append (s)
        except Exception as e:
            logging.error (e)
            print e
        return id_list

    def get_rID_from_db(self):
        """
        从数据库中查询文件remote_file_id
        :return:
        """
        list=self.database.query_id ()
        return list

    def get_arve(self,delay):
        l=[]
        with open (self.upload_result, 'r')as result:
            for r in result.readlines ():
                a=float (str (json.loads (r)['spend_time']).rsplit ('s')[0])
                l.append (a)
        arver_time=float ((sum (l)-delay) / len (l))
        return arver_time

    def time_change(self, t):
        """
        时间格式转换
        :param t:
        :return:
        """
        c=time.localtime (t)
        spend_time=str (c.tm_year) + '/' + str (c.tm_mon) + '/' + str (c.tm_mday) + ' ' + str (
            c.tm_hour) + ':' + str (c.tm_min) + ':' + str (c.tm_sec)
        return spend_time

    def report_html(self, filepath='test.json'):
        report_time=time.strftime ("%Y%m%d", time.localtime ())
        th=u"""<th>测试时间</th><th>上传文件数</th><th>成功</th><th>失败</th><th>平均上传速度上传</th><th>上传耗时</th><th>上传文件总共大小</th>"""
        table=r'''
                
                <div class='jumbotron'>
                <h1>%(h1)s</h1>
                <p>   </p>
                <h2>%(h2)s</h2>
                    <div class='paned-heading'>Result:</div>
                    
                    <table class='table'>
                        <tr >
                            %(th)s
                        </tr>
                        <tr>
                            %(result)s
                        </tr>
                    </table>
                    
                </div>'''
        tr=r'''
                <tr>
                    <td>%(Test_Time)s</td>
                    <td>%(files_count)s</td>
                    <td>%(Success)s</td>
                    <td>%(Fail)s</td>
                    <td>%(speed)s</td>
                    <td>%(cost)s</td>
                    <td>%(sizes)s</td>
                </tr>
        '''
        count=len (open (filepath, 'rU').readlines ())
        trs=[]
        with open (filepath, 'rU') as fp:
            f=fp.readlines ()
        for c in range (0, count - 1):
            res=json.loads (f[c])
            tr_list=tr % dict (
                Test_Time=str (res['starttime']),
                files_count=res['count'],
                Success=str (res['success']),
                Fail=str (res['failure']),
                speed=str (res['speed']),
                cost=str (res['spend_time']),
                sizes=str (res['sizes'])
            )
            trs.append (tr_list)
        css=r"""<link href="bootstrap/dist/css/bootstrap.min.css" rel="stylesheet"><style type="text/css">' 
            body {
                    font-family: Verdana, Helvetica, sans-serif;
                    }
            h1 {
                    font-size: 13pt;
                    font-weight:bold;
                    margin:4pt 0pt 0pt 0pt; 
                    padding:0;
                    } 
            h2 {
                    font-size: 12pt;
                    font-weight:bold;
                    margin:3pt 0pt 0pt 0pt;
                    padding:0;
                    }
            table {
                    margin:1pt 0pt 8pt 40pt;
                    border:0px;width:90%
                    }
            td {
                    border:0px;
                    border-top:1px solid black;
                    font-size: 9pt;
                    }
            tr {
                    vertical-align:top;
                    font-family: Verdana, Helvetica, sans-serif;
                    font-size: 8pt;
                    color:#000000;
                    background-color: #FFFFFF;
                    }
            </style>"""
        body=table % dict (
            h1='FastDFS Upload Test',
            h2='Test Result',
            th=th,
            result=''.join (trs)
        )

        head=r"""
                <!DOCTYPE html>
                <html>
                    <head>
                        <meta content="text/html; charset=UTF-8" http-equiv="content-type">
                        <title>%(title)s</title>
                        %(css)s
                    </head>
                    <body>
                        %(content)s
                    </body>
                </html>
        
        """

        html=str (report_time) + '_report.html'
        cont=head % dict (
            title=u'upload',
            css=css,
            content=body

        )
        with open (html, 'wb') as h:
            h.write (cont.encode ('utf8'))
        return html


def test_threads(ths, delay):
    """
    多线程实现
    :param ths: 线程数
    :param delay: 延迟时间
    :return:
    """
    threads=[]
    for i in range (ths):
        t=threading.Thread (target=c.concurrent_upload_files, args=())
        threads.append (t)
    for i in range (ths):
        threads[i].start ()
        time.sleep (delay)
    for i in range (ths):
        threads[i].join ()


def test_upload_files_by_thraeds():
    """
    多線程並發上传文件
    :return:
    """
    # 线程数
    np=[300,500,750,1000]
    # 延迟启动时间
    delay=[0.05,0.1,0.15,0.2]
    c=FdfsLibrary ()
    for i in range (len (np)):
        for j in range (len (delay)):
            test_threads (ths=np[i], delay=delay[j])
            ar_time=c.get_arve (delay[j])
            s=0
            with open (c.upload_result, 'r')as up:
                for u in up.readlines ():
                    if json.loads (u)['success'] == 1:
                        s+=1
            with open ('test_upload_1212.json', 'a')as u:
                u.write ('Thread number:%s  delay:%s arver_time:%ss  success:%d' % (np[i], delay[j], ar_time, s))
                u.write('\n')
            with open (c.upload_result, 'w+')as j:
                j.truncate ()
            c.batch_deleta_upload_file ()


if __name__ == '__main__':
    c=FdfsLibrary ()
    c.batch_deleta_upload_file()
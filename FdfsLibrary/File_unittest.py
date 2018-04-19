#coding=utf-8
import json,logging,random
import string
import sqlite3
from FdfsLibrary import FdfsLibrary
import multiprocessing
from multiprocessing import Process

class File_Main_Test():
    def __init__(self):
        pass

    def test_upload(self):
        """
        测试文件上传
        :return:
        """
        c = FdfsLibrary ()
        pass
    def test_stability(self):
        """
        长时间上传文件，再删除测试稳定性
        :return:
        """
        c = FdfsLibrary ()
        try:
            while True:
                re = c.serial_upload_files (1000)
                with open ('test_upload_1212.json', 'a') as outfile:
                    json.dump (re, outfile, ensure_ascii=False)
                    outfile.write ('\n')
                c.batch_deleta_upload_file ()
        except Exception as e:
            logging.error (e)

        finally:
            html = c.report_html (filepath='test_upload_1212.json')
            logging.info (msg='The Path Of Report : %s ' % html)
            logging.info (msg='Finish')

if __name__=='__main__':
    c = FdfsLibrary()
    try:
        while True:
            re = c.serial_upload_files(1000)
            with open('test_upload_1212.json', 'a') as outfile:
                json.dump(re, outfile, ensure_ascii=False)
                outfile.write('\n')
            c.batch_deleta_upload_file()
    except Exception as e:
        logging.error(e)

    finally:
        html = c.report_html(filepath='test_upload_1212.json')
        logging.info(msg='The Path Of Report : %s ' % html)
        logging.info(msg='Finish')
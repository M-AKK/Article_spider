# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
#它和open直接打开文件的区别是：可以避免编码方面的一些问题
import codecs
import json
from scrapy.exporters import JsonItemExporter

import MySQLdb
from twisted.enterprise import adbapi
import MySQLdb.cursors

class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item

'''
因为图片通过scrapy自带的pipeline保存到了本地
那么有没有办法让模版中的地址直接和本地的路径做一个绑定
可以通过 继承 ArticlespiderPipeline的方法来实现多态，写自己的方法来重新绑定
'''
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item

'''
这个pipeline可以拦截我们的item
所以在这个可以将数据保存的mysql中
先建立一个保存json 的pipeline，叫做jsonWithEncoding
'''
#python的继承是写在括号里面的
class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    # 要保存json文件，第一步要打开json文件
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding="utf-8")
    # 这个方法是处理item的方法，就是在这里吧数据写入到数据库当中
    def process_item(self,item, spider):
        # 第一步将item准换成字符串
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n" #第二个参数，默认是true，会把unnicode写入到文件中，显示会不正常
        # 第二步，将数据字符串写入到文件当中
        self.file.write(lines)
        return item
    def spider_closed(self, spider):
        self.file.close()

'''
scrapy本身也提供了写入json的一种机制
fieldExport机制可以方便地将json导出成各种类型的文件
'''
class JsonExporterPipeline(object):
    # 调用scrapy提供的jsonexport导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding = "utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

'''自定义pipeline写入数据库'''
class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect(host='127.0.0.1',port=3306,user='root', passwd='6881385mysql', db = 'article_spider', charset="utf8", use_unicode = True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, read_nums)
            VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["read_nums"]))
        self.conn.commit()

'''scrapy提供了连接池，把mysql 插入异步化'''
class MysqlTwistedPipeline(object):
    # 在启动spider 的时候dbpool就传进来了
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        #这个变量名称要和MySQLdb.connections里面的参数名称一样
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DANAME"],
            user = settings["MYSLQ_USER"],
            passwd = settings["MYSLQ_PASSWORD"],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True
        )
        #adbapi将mysql 操作变成异步化
        '''
        可变参数是用在函数的参数传递上的
        单个星号代表这个位置接收任意多个非关键字参数并将其转化成元组
        而双星号代表这个位置接收任意多个关键字参数并将其转化成字典
        '''
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return  cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_inster, item)
        query.addErrback(self.handle_error) # 处理异常

    def handle_error(self, failure ):
        # 处理异步插入的异常
        print(failure)

    def do_inster(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
                    insert into jobbole_article(title, url, create_date, read_nums)
                    VALUES (%s, %s, %s, %s)
                """
        cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["read_nums"]))

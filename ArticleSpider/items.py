# Define here the models for your scraped items
# 网上爬取的数据需要存储成自己定义的结构化数据，通过item来实例化，类似于字典（键值对）但是相比于字典功能更加齐全
# 我们会yield这个类，当scrapy发现这是item实例过的类的时候，它就会将item路由到pipelines当中来，然后再pipelines
# 中集中处理数据的保存、去重等等
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

# 在这里定义一个模版来存储爬取的字段
class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()  #这个是url被转换成压缩格式后的数据
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    read_nums = scrapy.Field()
    content = scrapy.Field()
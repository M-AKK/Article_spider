# Define here the models for your scraped items
# 网上爬取的数据需要存储成自己定义的结构化数据，通过item来实例化，类似于字典（键值对）但是相比于字典功能更加齐全
# 我们会yield这个类，当scrapy发现这是item实例过的类的时候，它就会将item路由到pipelines当中来，然后在pipelines
# 中集中处理数据的保存、去重等等
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
import datetime
from scrapy.loader import ItemLoader
import re


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 自定义itemloader，全部只取第一个值
class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


# 这些是不同的处理数据的规则
def add_jobbole(value):
    return value+"-jobbole"


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date=datetime.datetime.now().date()
    return create_date


def get_nums(value):
    # 可以获取括号里面的数字值
    match_obj = re.match(".*?(\d+).*", value)
    if match_obj:
        nums = int(match_obj.group(1))
    else:
        nums = 0
    return nums


def return_value(value):
    return value


# 在这里定义一个模版来存储爬取的字段
class JobBoleArticleItem(scrapy.Item):
    # 对数据做预处理
    title = scrapy.Field(
        input_processor=MapCompose(add_jobbole)
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
        # 这个只能设置一条output_processor=TakeFirst()#只取第一个
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()  #这个是url被转换成压缩格式后的数据
    front_image_url = scrapy.Field(
        # 有些只有一条，其实没必要用TakeFirst()
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    read_nums = scrapy.Field()
    content = scrapy.Field()
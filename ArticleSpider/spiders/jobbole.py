# -*- coding: utf-8 -*-
# @Time : 2021/1/8 17:25
# @Author : khm
'''
这一个主要讲利用xpath来选择元素

extract()返回的所有数据，存在一个list里。
extract_first()返回的是一个string，是extract()结果中第一个值。
'''
import scrapy
import re
from scrapy.http import Request
from urllib import parse #通过它获取当前域名

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5

import datetime
# 4-16通过Itemloader来生成我们的item
from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']# 含义是过滤爬取的域名，在插件OffsiteMiddleware启用的情况下（默认是启用的），不在此允许范围内的域名就会被过滤，而不会进行爬取
    start_urls = ['http://www.jobbole.com/caijing/']

    def parse(self, response):
        '''
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        '''

        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析，#绑定id
        # post_nodes = response.css("#stock-left-graphic .list-item .content .content-title a::attr(href)").extract()
        # 这个a标签下刚好也有文章详情页的连接
        post_nodes = response.css("#stock-left-graphic .list-item .img a")
        for post_node in post_nodes:
            # 通过上面的节点直接连接下面的图片的，拼接起来
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("") # 详情页url
            # parse.urljoin会自动根据传入的域名获取到主域名
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":image_url}, callback=self.parse_detail, dont_filter=True)

        # 提取下一页并交给scrapy进行下载
        next_urls = response.css("#layui-laypage-1 .a1::attr(href)").extract()[1]
        if next_urls:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    # 提取文章具体字段
    def parse_detail(self, response):
        '''
        # 这里相当于把实例化的item附给这里的一个变量，然后对这个变量进行赋值
        article_item = JobBoleArticleItem()
        # 直接复制xpath的情况
        title = response.xpath("/html/body/div[3]/div[1]/div[3]/div[1]/h1/text()").extract()[0]
        # 利用class来定位
        re2_selector = response.xpath('//div[@class="article-head"]/h1/text()')
        # 获取发表日期,strip是在去掉换行符,可以加.strip().replace(".","").strip()
        create_date = response.xpath('//div[@class="date"]/span/text()').extract()[0].strip()
        read_nums = response.xpath('//div[@class="about-left"]/span[2]/text()').extract()[0]
        regex_str = ".*?(\d+).*"
        match_obj = re.match(regex_str, read_nums)
        if match_obj:
            #print(match_obj.group(1))
            read_nums = int(match_obj.group(1))
        else:
            read_nums = 0

        content = response.xpath('//div[@class="article-main"]').extract()[0]
        front_image_url = response.meta.get("front_image_url", "")

        article_item["url_object_id"] = get_md5(response.url)
        article_item["title"] = title
        article_item["url"] = response.url
        #对日期格式做一个转换
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item["create_date"] = create_date
        #不加[]传进来的就是一个值，只有加上[]才是一个图片地址的数组
        article_item["front_image_url"] = [front_image_url]
        article_item["read_nums"] = read_nums
        article_item["content"] = content
        '''
        # 上面全注释，只用下面几行就够了，改造完成
        front_image_url = response.meta.get("front_image_url", "")
        # 通过itemloader加载item
        item_loader = ArticleItemLoader(item = JobBoleArticleItem(), response = response)
        # 将数据填充进来
        item_loader.add_css("title", ".article-head h1::text")
        #item_loader.add_xpath()
        #有些不是通过选择器，是直接通过response这种形式
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", ".about-left span:nth-child(1)::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("read_nums", '.about-left span:nth-child(2)::text')
        item_loader.add_xpath("content", '//div[@class="article-main"]')

        article_item = item_loader.load_item()

        #通过css选择器提取字段
        '''
        title = response.css(".article-head h1::text").extract()
        create_date = response.css(".about-left span::text").extract()[0]
        #span:nth-child(2)这样来指明是第几个span
        read_nums = response.css('.about-left span:nth-child(2)::text').extract()[0]
        print(read_nums)
        pass
        '''

        yield article_item


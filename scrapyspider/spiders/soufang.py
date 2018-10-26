# -*- coding: utf-8 -*-
"""
需求：抓取房天下网站各个城市的新房和二手房房价信息
思路：
1、先获取所有城市链接
http://www.fang.com/SoufunFamily.htm
2、再获取每个城市新房/二手房链接
上海：http://sh.fang.com/
     http://sh.newhouse.fang.com/house/s/
     http://sh.esf.fang.com/
无锡：http://wuxi.fang.com/
     http://wuxi.newhouse.fang.com/house/s/
     http://wuxi.esf.fang.com/
北京：http://bj.fang.com/
     http://newhouse.fang.com/house/s/
     http://esf.fang.com/

在linux部署工程：
pip freeze > requirements.txt
在virtualenv安装环境：pip install requirements.txt

问题：xpath()获取不到数据,返回的是空[]
原因：Scrapy爬虫看到的页面结构与我们自己在浏览器看到的可能并不一样(比如某个页面元素的id或者class不一样,甚至元素名字也不一样)
解决：使用scrapy shell测试 --> 通过view(response)命令来看看scrapy爬虫所看到的页面具体长啥样(可以在弹出的浏览器中检查元素)
"""

import scrapy
import re
from scrapyspider.items import NewHouseItem, EsfHouseItem
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapyspider.utils.common import get_md5
from scrapyspider.items import MyItemLoader


class scrapyspider(scrapy.Spider):
    # 爬虫名称
    name = 'soufang'
    # 域名范围
    allowed_domains = ['fang.com']
    # 起始页面
    start_urls = ['http://www.fang.com/SoufunFamily.htm']

    # scrapy默认只处理200<=response.status<300的url;现在想统计404页面数量,将404添加到http状态码请求列表
    handle_httpstatus_list = [404]  # 见源码-->scrapy.spidermiddlewares.httperror

    def __init__(self):
        super().__init__()
        self.failed_urls = []

        # 分发器做信号映射：当signals.spider_closed信号发生时调用stats_set_value()函数
        dispatcher.connect(receiver=self.spider_closed, signal=signals.spider_closed)

    # 关闭spider时的逻辑处理
    def spider_closed(self):
        # 给统计数据stats设置key/value
        self.crawler.stats.set_value("failed_urls_detail", ",".join(self.failed_urls))

    # 解析页面
    def parse(self, response):
        if response.status == 404:
            # 将404页面添加到错误url列表
            self.failed_urls.append(response.url)
            # 统计数据stats +1
            self.crawler.stats.inc_value("failed_urls_num")  # failed_urls这一参数会在爬虫结束时的数据统计中出现

        province = None
        # 获取表格所有行
        trs = response.xpath('//div[@class="outCont"]//tr')
        # 遍历所有行
        for tr in trs:
            # 获取省份名称(去空格)
            province_text = re.sub("\s", "", tr.xpath('./td[2]//text()').extract()[0])
            # 判断省份值是否为空字符串：不是""就赋值,是""就不赋值(此时province还是之前的值),如此循环直到有新的值覆盖 -->参考：basic-->类型和变量-->test()
            if province_text:
                province = province_text
            # 海外城市数据不需要
            if province == "其它":
                continue
            # 获取所有城市行
            citys = tr.xpath('./td[3]//a')
            for each in citys:
                # 城市名称
                city = each.xpath('./text()').extract()[0]
                # 该城市链接
                link = each.xpath('./@href').extract()[0]
                pinyin = link.split("//")[1].split(".")[0]
                # 北京比较特殊
                if pinyin == "bj":
                    new_link = "http://newhouse.fang.com/house/s/"
                    esf_link = "http://esf.fang.com/"
                else:
                    # 该城市新房链接
                    new_link = "http://" + pinyin + ".newhouse.fang.com/house/s/"
                    # 该城市二手房链接
                    esf_link = "http://" + pinyin + ".esf.fang.com/"

                # 发送新的请求链接(meta参数用于在不同请求之间传递数据,dict类型)
                yield scrapy.Request(url=new_link, callback=self.parse_new, meta={"info": (province, city)})
                # yield scrapy.Request(url=esf_link, callback=self.parse_esf, meta={"info": (province, city)})
                break
            break

    # 解析新房数据
    def parse_new(self, response):
        item = NewHouseItem()
        # 接收request请求传递过来meta参数信息
        province, city = response.meta.get("info")
        # 获取当前页面小区列表
        communitys = response.xpath('//div[@class="nlc_details"]')
        # 遍历所有小区
        for each in communitys:
            # 小区名字
            community = each.xpath('.//div[@class="nlcd_name"]/a/text()').get().strip()
            # 小区链接
            url = each.xpath('.//div[@class="nlcd_name"]/a/@href').get()
            # 价格
            price_text = "".join(each.xpath('.//div[@class="nhouse_price"]//text()').getall()).split()
            if price_text:
                price = price_text[0]
            else:
                price = "优惠价格"
            # 户型和面积
            rooms_text = "".join("".join(each.xpath('.//div[contains(@class, "house_type")]//text()').getall()).split())
            if "－" in rooms_text:
                rooms, area = rooms_text.split("－")[0], rooms_text.split("－")[1]
            else:
                rooms, area = "", ""
            # 所在区
            district = each.xpath('.//div[@class="address"]//span/text()').get()
            if district:
                district = district.strip()[1:-1]
            # 详细地址
            address = each.xpath('.//div[@class="address"]/a/@title').get()
            # 是否在售
            sale = each.xpath('.//div[contains(@class, "fangyuan")]/span/text()').get()

            item['id'] = get_md5(url)  # 生成随机数id作为主键
            item['province'] = province
            item['city'] = city
            item['community'] = community
            item['url'] = url
            item['price'] = price
            item['rooms'] = rooms
            item['area'] = area
            item['district'] = district
            item['address'] = address
            item['sale'] = sale

            # 通过ItemLoader加载item
            # loader = MyItemLoader(item=NewHouseItem, response=response)
            # loader.add_value('id', get_md5(response.url))
            # loader.add_value('province', province)
            # loader.add_value('city', city)
            # loader.add_xpath('community', './/div[@class="nlcd_name"]/a/text()')
            # loader.add_xpath('url', './/div[@class="nlcd_name"]/a/@href')
            # loader.add_xpath('price', './/div[@class="nhouse_price"]//text()')
            # loader.add_xpath('', '')
            # loader.add_xpath('', '')
            # loader.add_xpath('', '')
            # item = loader.load_item()

            yield item

        # 获取当前页码和尾页页码
        current_page = response.xpath('//div[@class="page"]//a[@class="active"]/text()').get()
        last_page = response.xpath('//div[@class="page"]//a[last()]/text()').get()
        # 判断是否到尾页
        if last_page == "尾页":
            # 获取新页面链接
            if current_page == "1":
                next_page = response.url + "b92"
            else:
                next_page = "/".join(response.url.split("/")[:-2]) + "/" + response.url.split("/")[-2][0:2] + str(int(response.url.split("/")[-2][2:])+1)
            # 继续发送新的请求
            yield scrapy.Request(url=next_page, callback=self.parse_new, meta={"info": (province, city)})

    # 解析二手房首页数据
    def parse_esf(self, response):
        # 创建item对象
        item = EsfHouseItem()
        # 接收request请求传递过来的meta参数信息
        province, city = response.meta.get("info")
        # 获取当前页面房源列表
        houses = response.xpath('//div[@class="houseList"]/dl')
        # 遍历
        for each in houses:
            # 小区名字
            community = each.xpath('.//p[@class="mt10"]/a/span/text()').get()
            # 地址
            address = each.xpath('.//p[@class="mt10"]/span/text()').get()
            # 标题
            title = each.xpath('.//p[@class="title"]/a/text()').get()
            # 几居室
            mt12 = each.xpath('.//p[@class="mt12"]/text()').getall()
            if mt12:
                rooms = "".join(mt12).split()[0]
                # 楼层
                floor = "".join(mt12).split()[1]
                # 朝向
                toward = "".join(mt12).split()[1]
                # 年代
                year = "".join(mt12).split()[1]
            else:
                rooms, floor, toward, year = "", "", "", ""
            # 面积
            area = "-".join(each.xpath('.//div[contains(@class, "area")]/p/text()').getall())
            # 价格
            price = "".join(each.xpath('.//p[@class="mt5 alignR"]/span/text()').getall())
            # 单价
            unit = "/".join(each.xpath('.//p[contains(@class, "danjia")]/text()').getall())

            item['province'] = province
            item['city'] = city
            item['community'] = community
            item['address'] = address
            item['title'] = title
            item['rooms'] = rooms
            item['floor'] = floor
            item['toward'] = toward
            item['year'] = year
            item['area'] = area
            item['price'] = price
            item['unit'] = unit
            yield item

        # 判断是否有下一页
        next_url = response.xpath('//a[@id="PageControl1_hlk_next"]/@href').get()
        # 继续发送新的请求
        if next_url:
            # 这个网站做的很刁钻：二手房首页和其他页的页面展示还不一样,需调用新的函数解析
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_esf_next, meta={"info": (province, city)})

    # 解析二手房非首页数据
    def parse_esf_next(self, response):
        # 创建item对象
        item = EsfHouseItem()
        # 接收request请求传递过来的meta参数信息
        province, city = response.meta.get("info")
        # 获取当前页面房源列表
        houses = response.xpath('//div[contains(@class, "shop_list")]/dl')
        for each in houses:
            # 小区名字
            community = each.xpath('.//p[@class="add_shop"]/a/@title').get()
            # 地址
            address = each.xpath('.//p[@class="add_shop"]/p/span/text()').get()
            # 标题
            title = each.xpath('.//span[@class="tit_shop"]/text()').get()
            # 几居室
            tel_shop = "".join(each.xpath('.//p[@class="tel_shop"]/text()').getall()).split()
            if tel_shop:
                rooms = tel_shop[0]
                # 面积
                area = tel_shop[1]
                # 楼层
                floor = tel_shop[1]
                # 朝向
                toward = tel_shop[1]
                # 年代
                year = tel_shop[1]
            else:
                rooms, area, floor, toward, year = "", "", "", "", ""
            # 价格
            price = each.xpath('.//dd[@class="price_right"]/span[1]/b/text()').get() + each.xpath('.//dd[@class="price_right"]/span[1]/text()').get()
            # 单价
            unit = each.xpath('.//dd[@class="price_right"]/span[2]/text()').get()

            item['province'] = province
            item['city'] = city
            item['community'] = community
            item['address'] = address
            item['title'] = title
            item['rooms'] = rooms
            item['floor'] = floor
            item['toward'] = toward
            item['year'] = year
            item['area'] = area
            item['price'] = price
            item['unit'] = unit
            yield item

        # 判断是否有下一页
        next_url = response.xpath('//div[@class="page_al"]/p[3]/a/@href').get()
        # 继续发送新的请求
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_esf_next, meta={"info": (province, city)})

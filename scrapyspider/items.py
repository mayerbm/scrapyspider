# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
# 导入scrapy加载器
from scrapy.loader import ItemLoader
# 导入scrapy内置处理器
from scrapy.loader.processors import MapCompose, TakeFirst, Join


def func01():
    pass


def func02():
    pass


# 自定义ItemLoader类
class MyItemLoader(ItemLoader):
    # 默认输出值是Identity()返回原值,这里改成输出列表的第一个非空/None值
    default_output_processor = TakeFirst()


class NewHouseItem(scrapy.Item):
    id = scrapy.Field()  # md5加密随机数作为主键
    # 省份
    province = scrapy.Field()
    # 城市
    city = scrapy.Field()
    # 小区名字
    community = scrapy.Field()
    # 价格
    price = scrapy.Field()
    # 几居室
    rooms = scrapy.Field(
        # input_processor=MapCompose(func01),
        # output_processor=MapCompose(func02)
    )
    # 面积
    area = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 行政区域
    district = scrapy.Field()
    # 是否在售
    sale = scrapy.Field()
    # 详情页url
    url = scrapy.Field()


class EsfHouseItem(scrapy.Item):
    province = scrapy.Field()  # 省份
    city = scrapy.Field()  # 城市
    community = scrapy.Field()  # 小区名字
    title = scrapy.Field()  # 标题
    rooms = scrapy.Field()  # 几居室
    floor = scrapy.Field()  # 楼层
    toward = scrapy.Field()  # 朝向
    year = scrapy.Field()  # 年代
    area = scrapy.Field()  # 面积
    address = scrapy.Field()  # 地址
    price = scrapy.Field()  # 总价
    unit = scrapy.Field()  # 单价


class HospitalItem(scrapy.Item):
    # 医院编号
    id = scrapy.Field()
    # 医院名称
    name = scrapy.Field()
    # 医院资质
    aptitude = scrapy.Field()
    # 医院地址
    address = scrapy.Field()
    # 医院擅长项目
    skilled = scrapy.Field()
    # 写入时间
    insert_time = scrapy.Field()


class DoctorItem(scrapy.Item):
    # 医生编号
    id = scrapy.Field()
    # 医生名字
    name = scrapy.Field()
    # 医生所在医院编号
    hospital_id = scrapy.Field()
    # 医生所在医院名称
    hospital_name = scrapy.Field()
    # 医生职称职务
    title = scrapy.Field()
    # 医生擅长项目
    skilled = scrapy.Field()
    # 写入时间
    insert_time = scrapy.Field()


class JianshuspiderItem(scrapy.Item):
    id = scrapy.Field()  # 编号
    title = scrapy.Field()  # 标题
    link = scrapy.Field()  # 链接
    author = scrapy.Field()  # 作者
    pubtime = scrapy.Field()  # 出版时间
    content = scrapy.Field()  # 内容
    readings = scrapy.Field()  # 阅读数
    comments = scrapy.Field()  # 评论数
    subjects = scrapy.Field()  # 专题(该字段需要使用selenium模拟浏览器点击标签)


class SunwzspiderItem(scrapy.Item):
    """
    需求：抓取http://wz.sun0769.com/index.php/question/questionType?type=4网站每个帖子信息
    """

    # 编号
    id = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 链接
    link = scrapy.Field()
    # 状态
    status = scrapy.Field()
    # 网友
    netizen = scrapy.Field()
    # 时间
    time = scrapy.Field()
    # 内容
    content = scrapy.Field()


class TencentspiderItem(scrapy.Item):
    """
    需求：抓取http://hr.tencent.com/position.php?&start=0#a职位数据
    """

    # define the fields for your item here like:

    # 职位名称
    name = scrapy.Field()
    # 详细链接
    detailLink = scrapy.Field()
    # 职位类别
    sort = scrapy.Field()
    # 招聘人数
    num = scrapy.Field()
    # 上班地点
    site = scrapy.Field()
    # 发布时间
    publishTime = scrapy.Field()


class ItacastItem(scrapy.Item):
    # 构建Item模型(类似ORM对象关系映射)：用来定义结构化数据字段，保存爬取到的数据，类似python的dict
    name = scrapy.Field()  # 姓名
    title = scrapy.Field()  # 职称
    info = scrapy.Field()  # 简介

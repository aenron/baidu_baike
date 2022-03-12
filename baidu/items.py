# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company=scrapy.Field()         # 组织机构
    name=scrapy.Field()            # 姓名  1
    zhiwu=scrapy.Field()           # 职务
    introduction=scrapy.Field()    # 简介  1
    photo =scrapy.Field()          # 照片 1
    country=scrapy.Field()         # 国籍
    birthplace=scrapy.Field()      # 出生地
    birthday=scrapy.Field()        # 出生日期
    GraduateSchool=scrapy.Field()  # 毕业院校
    profession=scrapy.Field()      # 职业
    achievement=scrapy.Field()     # 成就
    resume=scrapy.Field()          # 履历
    nation=scrapy.Field()          # 民族
    masterpiece=scrapy.Field()     # 代表作品
    ForeignName=scrapy.Field()     # 外文名
    JobTitle=scrapy.Field()        # 职称
    sex=scrapy.Field()             # 性别
    originate=scrapy.Field()       # 籍贯
    political =scrapy.Field()      # 政治面貌
    polysemant=scrapy.Field()      # 多义词
    other=scrapy.Field()           #其他

import scrapy
import pandas as pd
import urllib
from urllib import parse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from baidu.items import BaiduItem
import requests



def polysemantRedirect(company, name):
    # 获取搜索结果，重定向到目标链接
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    content = company+name
    url = 'https://baike.baidu.com/search/none?word=' + \
        urllib.parse.quote(str(content).encode(
            'utf-8'))+'&pn=0&rn=10&enc=utf8'
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.content, features="lxml")
    try:
        link = soup.find(
            class_="search-list").find_all(class_="result-title")[0]['href']
    except:
        link='https://baike.baidu.com/item/' + urllib.parse.quote(name)
    if link[0] == '/':
        link = 'https://baike.baidu.com'+link
    else:
        pass
    return link


def get_link_list(company_list, name_list):
    url_list = []
    for company, name in zip(company_list, name_list):
        url = polysemantRedirect(company, name)
        url_list.append(url)
    return url_list

class MenSpider(scrapy.Spider):
    name = 'men'
    allowed_domains = ['http://baike.baidu.com']
    start_urls = ['http://baike.baidu.com/']

    def start_requests(self):
        file_path = 'D:/Project/Scrapy/baidu/baidu/spiders/zky.xlsx'
        df = pd.read_excel(file_path)
        name_list = df['姓名']
        company_list = df['组织机构']
        urls = get_link_list(company_list, name_list)

        for url in urls:
            yield scrapy.Request(url)

    def parse(self, response):
        item_tmp = BaiduItem()

        current_url = response.url
        url = parse.unquote(current_url)
        name = url.split('/')[4]
        print(url)
        print(name)

        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        try:
            item_tmp['name'] = soup.find('title').text.split('_')[0]
        except:
            pass
        try:
            item_tmp['introduction'] = "".join(soup.find(class_="para").text.split())
        except:
            item_tmp['introduction'] = ""
        try:
            item_tmp['photo']=soup.find(class_="summary-pic").find('img')['src']
        except:
            pass
        # 基本信息
        left_item = soup.find_all(class_="basicInfo-item name")
        left_value = soup.find_all(class_="basicInfo-item value")
        info_dict={}
        for key, value in zip(left_item, left_value):
            try:
                info_dict["".join(key.text.split())] = "".join(value.text.split())
            except:
                pass

        # 网页分段解析
        para_list = str(BeautifulSoup(data, features="lxml")).split('class="lemma-anchor para-title"')
        catalog = []  # 目录
        idx = []  # 索引
        try:
            for i in soup.find(class_="lemma-catalog").find_all('li'):
                title = str(i.find(class_='text').text)
                catalog.append(title)
                id_ = str(i.find('a')['href'])[1:]
                idx.append(id_)

            item_dict_tmp = {}  # 临时字典，存放分段目录内容
            for i, value in enumerate(idx):
                # 没有子目录
                if len(value) == 1:
                    tmp_list = []
                    for para in BeautifulSoup(para_list[int(i)+1], features="lxml").find_all(class_="para"):
                        txt = str(para.text)
                        tmp_list.append("".join(txt.split()))
                        # print(tmp_dict[catalog[int(i)]]=txt)
                    item_dict_tmp[catalog[i]] = tmp_list
                # 存在子目录
                if len(value) > 1:
                    tmp_list = []
                    tmp_dict = {}
                    item = catalog[i]
                    for para in BeautifulSoup(para_list[int(i)+1], features="lxml").find_all(class_="para"):
                        txt = para.text
                        tmp_list.append("".join(txt.split()))
                    tmp_dict[item] = tmp_list
                    first, end = value[0], value[-1]
                    catalog_idx = idx.index(first)  # 查找对应父项索引值
                    cata_name = catalog[catalog_idx]  # 查找子项对应的父项目录值
                    item_value_list = item_dict_tmp[cata_name]  # 拿出已存储的字典值。存为列表
                    if not isinstance(item_value_list, list):
                        item_value_list = list(item_value_list)
                    item_value_list.append(tmp_dict)
                    item_dict_tmp[cata_name] = item_value_list
        except:
            # 出错时采用备用方法，生成个人履历
            item_dict_tmp = {}
            stage_list = []
            para_list = str(BeautifulSoup(data, features="lxml")).split(
                'class="lemma-anchor para-title"')
            try:
                for i in BeautifulSoup(para_list[1], features="lxml").find_all(class_="para")[1:]:
                    stage = i.text
                    stage_list.append("".join(stage.split()))
            except:
                try:
                    for i in soup.find_all(class_="para")[1:15]:
                        length = len(i.text)
                        # 根据文本长度判断是否属于
                        if 10 < length < 80:
                            stage = i.text
                            stage_list.append("".join(stage.split()))
                except:
                    pass
            item_dict_tmp['履历'] = stage_list


        # 是否头同名人物
        polysemantList = 0
        try:
            polysemantList = len(
                soup.find(class_="polysemantList-wrapper cmn-clearfix").find_all('li'))
        except:
            polysemantList = 0


        # 尝试填充基础信息
        # 格式化数据
        try:
            item_tmp['country']=info_dict['国籍']
        except:
            item_tmp['country']='-'
        try:
            item_tmp['birthplace']=info_dict['出生地']
        except:
            pass
            #item['birthplace']='-'
        try:
            item_tmp['birthday']=info_dict['出生日期']
        except:
            pass
        try:
            item_tmp['GraduateSchool']=info_dict['毕业院校']
        except:
            pass
        try:
            item_tmp['profession']=info_dict['职业']
        except:
            pass
        try:
            item_tmp['achievement']=info_dict['成就']
        except:
            pass
        try:
            item_tmp['nation']=info_dict['民族']
        except:
            pass
        try:
            item_tmp['masterpiece']=info_dict['代表作品']
        except:
            pass
        try:
            item_tmp['ForeignName']=info_dict['外文名']
        except:
            pass
        try:
            item_tmp['JobTitle']=info_dict['职称']
        except:
            pass
        try:
            item_tmp['sex']=info_dict['性别']
        except:
            pass
        try:
            item_tmp['originate']=info_dict['籍贯']
        except:
            pass
        try:
            item_tmp['political']=info_dict['政治面貌']
        except:
            pass
        #分段网页
        try:
            item_tmp['resume'] = item_dict_tmp[list(item_dict_tmp.keys())[0]]
        except:
            pass
        try:
            item_tmp['other'] = item_dict_tmp
        except:
            pass
        try:
            item_tmp['polysemant'] = polysemantList
        except:
            pass

        yield item_tmp

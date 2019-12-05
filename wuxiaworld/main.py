# Your own Python Interpreter
# -*- coding:utf-8 -*-


import requests, os
import pandas as pd
from bs4 import BeautifulSoup


class CollectUrls:
    """搜集特定小说所有章节的url和章节名字"""

    def __init__(self, directory):
        self.directory = directory  # 小说目录页网址
        self.__infos = []

    def collector(self) -> list:
        html = requests.get(self.directory).text
        soup = BeautifulSoup(html, "lxml")

        items = soup.find_all(attrs = {'class': 'chapter-item'})
        for item in items:
            tag_a = item.find('a')
            info = []

            url = 'https://www.wuxiaworld.com' + tag_a['href']
            info.append(url)
            info.append(tag_a.text).strip()

            self.__infos.append(info)

        return self.__infos


class CollectDiv:
    """收集特定小说特定章节的内容"""

    def __init__(self, url):
        self.url = url
        self.r = None

    def collect(self):
        """收集特定章节的内容,并以字符串存入成员变量中"""

        html = requests.get(self.url).text
        soup = BeautifulSoup(html, "lxml")
        self.r = ""

        result_div = soup.find(attrs = {'id': 'chapter-content'})
        result_p = result_div.find_all('p')
        for p in result_p:
            self.r += str(p.text) + '\n'

    def writer(self, file_name: str):
        """把获取的内容以文件的形式存储"""

        with open(file_name, 'w') as f:
            f.write(self.r)


if __name__ == '__main__':
    # 一个简单的没有任何反爬机制应对的爬虫-不涉及多线程、分布式等知识
    # 收集文件中的前三十小说的信息
    novels = pd.read_excel('main.xlsx')

    novel_names = novels.get('novel_name')
    main_urls = novels.get('main_url')  # 小说目录页网址

    num = 0
    while num < 30:
        novel_name = novel_names[num]
        main_url = main_urls[num]

        c = CollectUrls(main_url)
        chapters = c.collector()

        print(novel_name + ' start')

        # 创建特定小说的文件夹
        os.mkdir(novel_name)

        for each_chpt in chapters:
            url = each_chpt[0]
            chpt_name = each_chpt[1]
            try:
                collector = CollectDiv(url)
                collector.collect()
                collector.writer(file_name = novel_name + '/' + chpt_name)
            except Exception as e:
                print(e)
                text = str(novel_name) + ' ' + str(chpt_name) + ' ' + str(url) + '\n'
                with open("missing_chapters.txt", "a") as f:
                    f.write(text)

        num += 1
        print(novel_name + ' done!!!')

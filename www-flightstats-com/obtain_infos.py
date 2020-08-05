# -*- coding: utf-8 -*-

# @author: elucidator7
# @file:   obtain_infos.py
# @time:   2020/8/5 8:10
# @goal:   obtain infos of particular flights

import requests
import re
import xlwt


class Spider:
    """
    目标网址：https://www.flightstats.com/v2/flight-tracker/route/PEK/CTU/?year=2020&month=8&date=4&hour=18
    爬取例如如上网址中所有航班行程的具体信息
    """

    def __init__(self):
        self.header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.100 Safari/537.36"
        }
        self.matching_text1 = r'"sortTime":"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z",' \
                              r'"departureTime":{"timeAMPM":"\d{1,}:\d{2}.M","time24":"\d{2}:\d{2}"},' \
                              r'"arrivalTime":{"timeAMPM":"\d{1,}:\d{2}.M","time24":"\d{2}:\d{2}"},' \
                              r'"carrier":{"fs":".{2}","name":".*?","flightNumber":".{4}"},"operatedBy":.*?,'
        self.matching_text2 = r'"sortTime":"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z","departureTime":{"timeAMPM":"' \
                              r'\d{1,}:\d{2}.M","time24":"(\d{2}:\d{2})"},"arrivalTime":{"timeAMPM":"\d{1,}:\d{2}.M",' \
                              r'"time24":"(\d{2}:\d{2})"},"carrier":{"fs":"(.{2})","name":"(.*?)","flightNumber":' \
                              r'"(.{4})"},"operatedBy":.*?,'
        self.url = None
        self.infos = []
        self.departure_airport, self.arrival_airport = "", ""
        self.date, self.month, self.year = 0, 0, 0
        self.hour = 0

    def initialize(self,
                   departure_airport: str,
                   arrival_airport: str,
                   hour: int, date: int, month: int, year=2020) -> None:
        """
        根据待爬取网址的特点，组合具体的url信息用于爬取
        示例url：https://www.flightstats.com/v2/flight-tracker/route/PEK/CTU/?year=2020&month=8&date=4&hour=18分析，
        需要人为配置的数据有：
        出发地址（例如PEK）目的地址（例如CTU）出发时间（年月日）航班区间（hour=18到零点）
        """
        self.departure_airport, self.arrival_airport = departure_airport, arrival_airport
        self.date, self.month, self.year = date, month, year
        self.hour = hour
        self.url = f"https://www.flightstats.com/v2/flight-tracker/route/{self.departure_airport}/{self.arrival_airport}" \
                   f"/?year={str(self.year)}&month={str(self.month)}&date={str(self.date)}&hour={self.hour}"

    def __request_html(self) -> requests.Response:
        """
        使用requests模块进行对网页内容的获取
        """
        r = requests.get(url=self.url, headers=self.header)
        return r

    def __re_match(self, html_text: str) -> None:
        """
        使用正则表达式去提取所有的航班信息
        """
        compiler1 = re.compile(self.matching_text1)
        compiler2 = re.compile(self.matching_text2)
        res = compiler1.findall(html_text)

        # 整理出infos列表，列表中每一个项是一次航班的信息，
        # 一次航班的信息为一个列表[flight, departure_time, arrival_time, airlines]，
        # 例如：["3U8886", "1540", "1845", "Sichuan Airlines"]
        for r in res:
            result = compiler2.match(r)
            info = [str(result.group(3)) + str(result.group(5)),
                    re.sub(":", "", str(result.group(1))),
                    re.sub(":", "", (result.group(2))),
                    str(result.group(4))]
            self.infos.append(info)

    def __writer(self) -> None:
        """
        根据re_match函数中获取的航班信息列表，
        把信息写入excel文档中
        Sample: 3U8886 \t 1540 \t 1845 \t Sichuan Airlines
        """
        for info in self.infos:
            print(info)

        workbook = xlwt.Workbook(encoding="utf-8")
        sheet1 = workbook.add_sheet(f"{self.departure_airport} to {self.arrival_airport}")
        sheet1.write(0, 0, "Flight")
        sheet1.write(0, 1, "Departure Time")
        sheet1.write(0, 2, "Arrival Time")
        sheet1.write(0, 3, "Airlines")
        for i in range(len(self.infos)):
            """
            根据self.infos的数据依次写入excel文件中
            """
            sheet1.write(i + 1, 0, self.infos[i][0])
            sheet1.write(i + 1, 1, self.infos[i][1])
            sheet1.write(i + 1, 2, self.infos[i][2])
            sheet1.write(i + 1, 3, self.infos[i][3])
        # 保存excel文件
        file_name = rf"{self.departure_airport} to {self.arrival_airport} in {self.date}-{self.month}-{self.year}.xls"
        workbook.save(file_name)

    def run(self) -> None:
        """
        调用initialize函数后调用的函数，
        函数功能：获取html=>正则匹配航班信息=>把航班信息写入excel文档中
        """
        r = self.__request_html()
        self.__re_match(r.text)
        self.__writer()


if __name__ == '__main__':
    spider = Spider()
    # 在initialize方法中写入需要的参数，完成url的配置
    spider.initialize("PEK", "CTU", hour=18, date=6, month=8, year=2020)
    # 运行run()方法完成航班信息获取
    spider.run()

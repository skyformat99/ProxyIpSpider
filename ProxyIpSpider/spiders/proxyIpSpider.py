# -*- coding: utf-8
"""
爬取免费代理IP信息 【附带IP有效性校验脚本 -> 详见 ../script/iPValidityCheck.py】

数据存储在MySQL表中, 结构如下所示:
CREATE TABLE `proxy_ip_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `proxy_ip` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5085 DEFAULT CHARSET=utf8mb4;


@Author YH YR
@Time 2018/10/24 15:16
"""
from scrapy import Request, Selector
from scrapy.spiders import CrawlSpider

from ProxyIpSpider.utils.mysqlUtil import MysqlUtil
from ProxyIpSpider.settings import *


class ProxyIpSpider(CrawlSpider):
    name = 'proxyIpSpider'

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.mysql = MysqlUtil(host, user_name, pass_word, db_name, port)
        self.table_name = 'proxy_ip_info'

        # 三一代理
        self.proxy31_url_list = ['http://31f.cn/http-proxy/', 'http://31f.cn/https-proxy/']

        # 西刺代理
        self.xici_url_list = ['http://www.xicidaili.com/nn/', 'http://www.xicidaili.com/nt/',
                              'http://www.xicidaili.com/wn/', 'http://www.xicidaili.com/wt/']

        # 无忧代理
        self.data5u_url_list = ['http://www.data5u.com/free/index.shtml',
                                'http://www.data5u.com/free/gngn/index.shtml',
                                'http://www.data5u.com/free/gnpt/index.shtml',
                                'http://www.data5u.com/free/gwgn/index.shtml',
                                'http://www.data5u.com/free/gwpt/index.shtml']

    def start_requests(self):
        for data5u_url in self.data5u_url_list:
            yield Request(url=data5u_url, callback=self.parse_data5u_proxy)

        for proxy31_url in self.proxy31_url_list:
            yield Request(url=proxy31_url, callback=self.parse_31_proxy)

        for xici_url in self.xici_url_list:
            yield Request(url=xici_url, callback=self.parse_xici_proxy)

    def parse_xici_proxy(self, response):
        selector = Selector(response)
        ip_selector_list = selector.xpath("//table[@id='ip_list']//tr")
        ip_selector_list.pop(0)
        doc = set()
        for ip_selector in ip_selector_list:
            ip = ip_selector.xpath("./td[2]/text()").extract()[0]
            port = ip_selector.xpath("./td[3]/text()").extract()[0]
            protocol_type = ip_selector.xpath("./td[6]/text()").extract()[0]
            url = '{0}://{1}:{2}'.format(protocol_type.lower(), ip, port)
            doc.add(url)
        self.mysql.insert(self.table_name, ['proxy_ip'], doc)

    def parse_data5u_proxy(self, response):
        selector = Selector(response)
        ip_selector_list = selector.xpath("//div[@class='wlist']/ul/li[2]//ul[@class='l2']")
        doc = set()
        for ip_selector in ip_selector_list:
            ip = ip_selector.xpath("./span[1]/li/text()").extract()[0]
            port = ip_selector.xpath("./span[2]/li/text()").extract()[0]
            protocol_type = ip_selector.xpath("./span[4]/li/text()").extract()[0]
            url = '{0}://{1}:{2}'.format(protocol_type.lower(), ip, port)
            doc.add(url)
        self.mysql.insert(self.table_name, ['proxy_ip'], doc)

    def parse_31_proxy(self, response):
        if 'https-proxy' in response.url:
            protocol_type = 'https'
        else:
            protocol_type = 'http'
        selector = Selector(response)
        ip_selector_list = selector.xpath("//table[@class='table table-striped']//tr")
        ip_selector_list.pop(0)
        doc = set()
        for ip_selector in ip_selector_list:
            ip = ip_selector.xpath("./td[2]/text()").extract()[0]
            port = ip_selector.xpath("./td[3]/text()").extract()[0]
            url = '{0}://{1}:{2}'.format(protocol_type, ip, port)
            doc.add(url)
        self.mysql.insert(self.table_name, ['proxy_ip'], doc)



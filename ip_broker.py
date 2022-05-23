"""
爬取快代理可用的ip
"""
import feapder
from feapder import Request
from fake_useragent import UserAgent
import time
from items.ip_pool_item import IpPoolItem
import datetime
from feapder.db.mysqldb import MysqlDB
# from feapder.core.scheduler   #在此处自定义预警提示

class IPBroker(feapder.Spider):
    # 自定义数据库
    __custom_setting__ = dict(
        REDISDB_IP_PORTS="localhost:6379",
        REDISDB_USER_PASS="",
        REDISDB_DB=0
    )

    def download_midware(self, request):
        """
        下载中间件,对请求做一些处理，如添加cookie、header等
        :param request:请求
        :return:request
        """
        request.header = {
            "User-Agent": UserAgent().chrome
        }
        return request

    def start_requests(self):
        """
        下发任务,url分析
        1.访问url
        2.获取总共页数
        3.url拼接
        4.发送请求
        :return:
        """
        start_url = "https://free.kuaidaili.com/free/inha/{}/"
        pages = self.url_parse(start_url)  # 得到总页数
        for i in range(1, pages + 1):
            yield feapder.Request(url=start_url.format(i))

    def url_parse(self, start_url):
        """
        url拼接
        :param start_url: 起初访问url
        :return: 返回总页数
        """
        request = Request(start_url.format(1))  # 第一页
        response = request.get_response()
        pages = response.xpath('//div/div[@id="list"]/div[@id="listnav"]/ul/li/a/text()').extract()
        return int(pages[-1])

    def parse(self, request, response):
        """
        解析网页，得到网页中的ip等信息
        :param request:
        :param response:
        :return: 爬下来的代理proxies,字典
        """
        ip_pool = {}
        now = datetime.datetime.now()
        total_xpath = response.xpath('//div/table/tbody/tr')
        for item in total_xpath:
            ip_pool['ip'] = item.xpath('./td[@data-title="IP"]/text()').extract_first()  # ip
            ip_pool['port'] = item.xpath('./td[@data-title="PORT"]/text()').extract_first()  # post
            ip_pool['anonymity'] = item.xpath('./td[@data-title="匿名度"]/text()').extract_first()  # 高匿名
            ip_pool['type'] = item.xpath('./td[@data-title="类型"]/text()').extract_first()  # HTTP
            # ip_pool['request_type'] = item.xpath('./td[@data-title="get/post支持"]/text()').extract_first()
            ip_pool['location'] = item.xpath('./td[@data-title="位置"]/text()').extract_first()
            ip_pool['socket'] = f"http://{ip_pool['ip']}:{ip_pool['port']}"
            ip_pool['data'] = now.strftime("%Y-%m-%d %H:%M:%S")
            if ip_pool['anonymity'] == "高匿名":  # 只要高匿名的
                proxies = {
                    "http": f"http://{ip_pool['ip']}:{ip_pool['port']}",
                }
                test = self.test_if_the_url_can_be_used(proxies)  # 传入测试函数，像百度发起访问，查看ip是否可用
                if test:
                    print(ip_pool)
                    item = IpPoolItem(**ip_pool)  # 声明一个item
                    try:
                        sql = db.find(f"select * from ip_pool where data < '{now.strftime('%Y-%m-%d %H:%M:%S')}';",
                                      to_json=True)  # 数据库中不是当前的数据
                        if sql:  # 数据库中有数据
                            for items in sql:
                                proxies = {
                                    "http": f"http://{items['socket']}"
                                }
                                if self.test_if_the_url_can_be_used(proxies=proxies):  # 检测当前数据中哪些可用
                                    # print(item['id'],"可用", item)
                                    pass
                                else:  # 数据库中不可用的数据
                                    dele = db.delete(f"DELETE FROM website WHERE id = {items['id']}")
                                    print("数据库id为:", items['id'], "不可用,已删除",dele)
                            yield item
                            print("入库")
                        else:
                            # 数据库中没数据
                            yield item  # 存入数据库
                            print("已入库")
                    except Exception as e:
                        print(e)
                else:
                    print("----------------------这个不稳定--------------------------")

    def test_if_the_url_can_be_used(self, proxies):
        """
        功能函数，像百度发起访问，查看能否可用
        :param proxies: 爬取到的ip等信息
        :return: True或False
        """
        time.sleep(3)
        request = Request("https://www.baidu.com/", proxies=proxies, timeout=20)
        response = request.get_response()
        try:
            if response.status_code == 200:
                print("这个可以用",proxies.get("http"))
                return True
        except:
            print("错误码",response.status_code)
            return False


if __name__ == '__main__':
    db = MysqlDB()
    while True:
        IPBroker(redis_key="ip:pool",thread_count=10).start()
        time.sleep(24 * 3600)  # 一天

#   数据库查看重复命令
#   select * from ip_pool  where ip in (select ip from ip_pool group by ip having count(ip) > 1);
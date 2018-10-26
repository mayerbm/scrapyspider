import requests
from lxml import etree
from scrapyspider.utils.crud import insert
from scrapyspider.utils.crud import check


def crawl():
    # 该站点半小时刷新一次(差)
    values = []
    for i in range(1, 11):
        url = "http://www.ip3366.net/?stype=1&page=" + str(i)
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"}
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        ips = html.xpath('//tr')
        for each in ips[1:]:
            ip = each.xpath('./td[1]')[0].text
            port = each.xpath('./td[2]')[0].text
            boolean = check(ip, port)
            if boolean:
                values.append((ip, port))
    insert(values)


if __name__ == "__main__":
    crawl()
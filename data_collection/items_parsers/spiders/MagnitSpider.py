import scrapy
from pathlib import Path
import re

from parse_usefull import get_date_from_text
from parse_usefull import get_json_object

class MagnitSpider(scrapy.Spider):
    name = "magnit"

    def __init__(self):
        self.id_lst = get_json_object('magnit_shop_id_list.json')
        self.id_set = set()
        
       
    def build_url(self,page,shop_id):
        return f"https://magnit.ru/shops/{shop_id}/"

    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}
        cookies = {'mg_geo_id':1452}
        for id in self.id_lst:
            url = self.build_url(1,id)
            yield scrapy.Request(url=url,headers=headers,cookies=cookies,callback=self.parse)
    
    def parse(self,response):
        for data in response.xpath('//a[has-class("card-sale swiper-slide")]'):
            g_name = data.xpath('.//div[has-class("card-sale__title")]/p/text()').get()
            old_price = data.xpath('.//div[has-class("label__price label__price_old")]/ span[has-class("label__price-integer")]/text()').get()
            new_price = data.xpath('.//div[has-class("label__price label__price_new")]/ span[has-class("label__price-integer")]/text()').get()
            sale_begin = data.xpath('.//div[has-class("card-sale__date")]/p/text()').get()
            sale_end = data.xpath('.//div[has-class("card-sale__date")]/p[2]/text()').get()
            self.id_set.add(g_name)
            self.log(f'parsed data:  {g_name}, {old_price} , {new_price}, {sale_begin} ')
            if old_price is None or new_price is None:
                continue
            yield {
                "name":g_name,
                "id":"",
                "shop_id": re.search(r"(\d+)",response.url).group(0),
                "begin_date" : get_date_from_text(sale_begin),
                "effective_date" : get_date_from_text(sale_end),
                "price": old_price,
                "discount_price": new_price
            }


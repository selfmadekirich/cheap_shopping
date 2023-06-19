import scrapy
import json
import re
from parse_usefull import get_json_object

class PeterkaSpider(scrapy.Spider):
    name = "peterka"
    def __init__(self):
        self.id_lst = get_json_object("peterka_shop_id_list.json")
        self.id_set = set()
       
    def build_url(self,page,shop_id):
        return f"https://5ka.ru/api/v2/special_offers/?records_per_page=20&page={page}&store={shop_id}&ordering=&price_promo__gte=&price_promo__lte=&categories=&search="

    def start_requests(self):
        for id in self.id_lst:
            url = self.build_url(1,id)
            yield scrapy.Request(url=url, callback=self.parse)    
    
    def parse(self,response):
        data = json.loads(response.text)
        for result in data["results"]:
            if result["plu"] in self.id_set:
                continue
            self.id_set.add(result["plu"])
            yield {
                "name":result["name"],
                "id":result["plu"],
                "shop_id": re.search(r'store=(\w+)',response.url).group(1),
                "begin_date" :  result["promo"]["date_begin"],
                "effective_date" :result["promo"]["date_end"],
                "price":  result["current_prices"]["price_reg__min"],
                "discount_price": result["current_prices"]["price_promo__min"]
            }
        if data["next"]:
            yield scrapy.Request(url=data["next"], callback=self.parse)

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import psycopg2

class ItemsParsersPipeline:
    def process_item(self, item, spider):
        return item

class JsonWriterPipeline:
    
    def __init__(self,p_con) -> None:
        self.p_con = p_con      

    def open_spider(self, spider):
        self.connection = psycopg2.connect(**self.p_con)
        self.cur = self.connection.cursor()


    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            p_con=crawler.settings.get('P_CONN'),
        )    

    def process_item(self, item, spider):
        try:
          self.cur.execute('''insert into etl.load_service_table(item_name,item_id,shop_id,discount_start_date,discount_end_date,item_price,item_discount_price) 
                         values(%s,%s,%s,%s,%s,%s,%s)''',(item['name'],item['id'],item['shop_id'],item['begin_date'],item['effective_date'],item['price'],item['discount_price']))
          self.connection.commit()
          print('Inserted!')
        except Exception:
            print('Error while inserting')
        return item
    
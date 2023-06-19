from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.MagnitSpider import MagnitSpider
 
 
process = CrawlerProcess(get_project_settings())
process.crawl(MagnitSpider)
process.start()

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.PeterkaSpider import PeterkaSpider
 
 
process = CrawlerProcess(get_project_settings())
process.crawl(PeterkaSpider)
process.start()
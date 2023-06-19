import json
import re
from datetime import datetime


def get_json_object(file):
    with open(file, 'r',encoding='utf-8') as f:
      ans = f.read().replace('\n', '').replace('\"','"').replace("\"",'"')
      return json.loads(ans)
    
def get_month(date):
    month = re.search(r"(февраля)|(марта)|(апреля)|(мая)|(июня)|(июля)|(августа)|(сентября)|(октября)|(ноября)|(декабря)|(января)",date)
    months_dct = {"февраля": "02",
                  "марта" : "03" ,
                  "апреля": "04",
                  "мая" : "05" , 
                  "июня" : "06", 
                  "июля" : "07",
                  "августа" : "08",
                  "сентября" : "09",
                  "октября" : "10",
                  "ноября" : "11",
                  "декабря" : "12",
                  "января" : "01"}
    return months_dct[month.group(0)]
    
def get_day(date):
    day = re.search(r"(\d+)",date).group(1)
    if len(day) == 1:
        day = '0'+day
    return day
    
def get_year():
    return str(datetime.now().year)

def get_date_from_text(text):
       return get_year() + "-" +get_month(text) +"-" + get_day(text)



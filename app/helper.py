from ast import literal_eval
import re
from extensions import db
from sqlalchemy import func

def fix_network_type(row):
    return re.sub(r'\n+','',re.sub(r'Pyaterka',"'Пятерочка'",re.sub(r'Magnit',"'Магнит'",row)))

def get_lst_from_row(row):
     t = fix_network_type(row)
     print(t)
     l = literal_eval(fix_network_type(row))
     return [x for x in l]

def get_map_from_req_str(req_str):
    mp = literal_eval(req_str)
    return mp 


def convert_dbset_result_to_json(dbset,dct_keys):
    res = []
    for (x) in dbset:
        lst = get_lst_from_row(x[0])
        step = dict(zip(dct_keys,lst[:len(dct_keys)]))
        res.append(step)
    return res

def get_unique_items_name(itms_lst):
    return [x for x in set(itms_lst)]

def add_shielding_to_ts_query(query):
    return query.replace('(','\(').replace(')','\)')

def build_ts_query_param(items):
    return add_shielding_to_ts_query('|'.join(map(lambda x: re.sub(r"\s+",'&',x.strip()), items)))

def parse_front_geo(geo):
    return geo.split(';')

def build_db_geopoint_param(geo):
    geo = geo.split(';')
    return 'SRID=4326;POINT({0} {1})'.format(geo[0],geo[1])

def get_price_purchase_per_shop(dbset):
    items_purchase_price = {}
    for value in dbset:
        print('here')
        strct = items_purchase_price.get(value['shop_id'],{})
        strct_total = strct.get('total',0)   
        strct_lst = strct.get('lst',[])
        strct_lst.append(value['item'])   
        strct_total += value['price']
        items_purchase_price[value['shop_id']] = {'total':strct_total,'lst':strct_lst}
    return items_purchase_price


def get_minimal_purchase_shop(dbset):
    all_options = get_price_purchase_per_shop(dbset)
    max_goods = 0
    min_price = 9223372036854775807
    min_shop_id = ''
    min_lst = []
    for shop_id, value in all_options.items():
        print(shop_id,value,len(value['lst']))
        goods_cnt = len(value['lst'])
        if max_goods < goods_cnt:
            max_goods = goods_cnt
            min_price = value['total']
            min_shop_id = shop_id
            min_lst = value['lst']
        elif max_goods == goods_cnt:
            if min_price <= value['total']:
                min_price = value['total']
                min_shop_id = shop_id
                min_lst = value['lst']
    
    return {min_shop_id:{'total':min_price,'lst':min_lst}}



def get_price_purchase_by_request(dbset,request):
    match request:
        case 'По магазинам': return get_price_purchase_per_shop(dbset)
        case 'Минимальная стоимость': return get_minimal_purchase_shop(dbset)
    return None 



def get_shop_info(dbset):
    dct_keys = set([x['shop_id'] for x in dbset])
    dct_values = set([(x['shop'],x['type']) for x in dbset])
    return dict(zip(dct_keys,dct_values))


def find_shops_with_user_request(user_location,user_query):
    search_raduis = 1
    ts_query = build_ts_query_param(user_query)
    data = db.session.query(func.public.get_possible_goods(user_location,search_raduis,ts_query)).all()  
    while(len(data) == 0  and search_raduis <= 5):
        search_raduis += 0.5
        data = db.session.query(func.public.get_possible_goods(user_location,search_raduis,ts_query)).all()
    if len(data) == 0:
        return None 
    return data
        
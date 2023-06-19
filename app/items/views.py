from helper import (
    build_db_geopoint_param,
    build_ts_query_param,
    convert_dbset_result_to_json,
    get_shop_info,
    get_price_purchase_by_request,
    get_unique_items_name)

from flask import (
    flash,
    redirect,
    session,
    render_template,
    url_for)
from sqlalchemy import func
from flask import Blueprint, request, jsonify
from extensions import db


items_bp = Blueprint('items', __name__)

def save_date_in_session(session_key,dct_value):
    session[session_key] = dct_value


@items_bp.route('/')
def index():  
    return render_template('index.html')

@items_bp.route('/items',methods=['GET'])
def get_items():
   return render_template('items.html')

@items_bp.route('/items', methods=['POST'])
def items():
    print('Here ' + request.form.get('geo'))
    if not ';' in request.form.get('geo'):
        flash('Не удалось получить геолокацию')
        return redirect(url_for('items.get_items'))
    search_raduis = 1   
    geo = build_db_geopoint_param(request.form.get('geo'))
    ts_query = build_ts_query_param(request.form.get('user_query').split('\n'))
    data = db.session.query(func.public.get_possible_goods(geo,search_raduis,ts_query)).all()  
    while(len(data) == 0):
        search_raduis += 0.5
        data = db.session.query(func.public.get_possible_goods(geo,search_raduis,ts_query)).all()
        if search_raduis > 5:
            return render_template('choice_items.html',items=[])
  
    t = convert_dbset_result_to_json(data,["shop","item","item_id","shop_id",'type',"price"])
    save_date_in_session('items',t)
    save_date_in_session('request',request.form.get('user_choice'))
    return render_template('choice_items.html',items= get_unique_items_name([(x['item'],x['item_id']) for x in t]))


@items_bp.route('/items/min',methods =['POST'])
def min_items():
    request_item_ids = [int(x) for x in request.form.keys()]
    dbset =  session['items'] 
    shop_info = get_shop_info(dbset)
    user_request =  session['request']
    dbset_with_selected_items = filter(lambda x: x['item_id'] in request_item_ids,dbset)
    total_price_per_shop = get_price_purchase_by_request(dbset_with_selected_items,user_request)
    print(total_price_per_shop)
    for key,ind in zip(total_price_per_shop,range(0,len(total_price_per_shop.keys()))):
        total_price_per_shop[key]['shop_addr'] = shop_info[key][0]
        total_price_per_shop[key]['shope_type'] = shop_info[key][1]
        total_price_per_shop[key]['ind'] = ind
    return  render_template('options.html',items= total_price_per_shop,user_cards=False)


 
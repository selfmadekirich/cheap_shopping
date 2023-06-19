from helper import (
    get_map_from_req_str,
    find_shops_with_user_request,
    build_db_geopoint_param,
    convert_dbset_result_to_json,
    get_price_purchase_by_request,
    get_shop_info)
from flask import session,render_template
from flask import Blueprint, request
from extensions import db
from flask_login import login_required,current_user
from models import User_templates,Items,SavedItemsCard

saved_items_bp = Blueprint('saved_items', __name__)

def save_date_in_session(session_key,dct_value):
    session[session_key] = dct_value

@saved_items_bp.route('/cards',methods =['DELETE'])
@login_required
def delete_cards():
    remove_id = request.form.get('removable_id')
    User_templates.query.filter_by(id=remove_id).delete()
    db.session.commit()
    return 'OK'


@saved_items_bp.route('/cards',methods =['GET'])
@login_required
def cards():
    all_users_itms_lst = User_templates.query.filter_by(user_id=current_user.id).all()
    card_items = []
    for x in all_users_itms_lst:
        id = x.id
        name = x.name
        items = [x.item_name for x in Items.query.filter(Items.item_id.in_(x.items)).all()]
        card_items.append(SavedItemsCard(id,name,items))
    return render_template("saved_items_index.html",Card_list=card_items)

@saved_items_bp.route('/cards/options',methods =['POST'])
@login_required
def cards_options():
    card_id = request.form.get('card_id')
    geo = build_db_geopoint_param(request.form.get('geo'))
    request_res = User_templates.query.filter_by(id=card_id).first_or_404()
    items_names = [x.item_name for x in Items.query.filter(Items.item_id.in_(request_res.items)).all()]
    options = find_shops_with_user_request(geo,items_names)
    if options is None:
        return '404'
    t = convert_dbset_result_to_json(options,["shop","item","item_id","shop_id",'type',"price"])
    shop_info = get_shop_info(t)
    total_price_per_shop = get_price_purchase_by_request(t,'По магазинам')
   
    for key,ind in zip(total_price_per_shop,range(0,len(total_price_per_shop.keys()))):
        total_price_per_shop[key]['shop_addr'] = shop_info[key][0]
        total_price_per_shop[key]['shope_type'] = shop_info[key][1]
        total_price_per_shop[key]['ind'] = ind

    return render_template('options.html',items=total_price_per_shop,user_cards=True)

@saved_items_bp.route('/options/shows',methods=['POST'])
def show_options():
    items = session['saved_items']
    return  render_template('options.html',items=items,user_cards=True)



@saved_items_bp.route('/cards',methods=['POST'])
@login_required
def add_user_templates():
    data =  get_map_from_req_str(request.form.get('data'))
    goods_name = data['lst']
    template_name = data['name']
    dbset = session['items']
    dbset_items_ids = set(x['item_id'] for x in filter(lambda x: x['item'] in goods_name,dbset))
    print(dbset_items_ids)
    curr_templ = User_templates(user_id=current_user.id,items=[x for x in dbset_items_ids],name=template_name)
    db.session.add(curr_templ) 
    db.session.commit()
    return "OK"

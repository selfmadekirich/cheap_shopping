from extensions import db,login_manager
from models import User
from werkzeug.security import generate_password_hash,check_password_hash

from flask import (
    request,
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash)

from flask_login import (
    login_user,
    login_required,
    logout_user)

auth_bp = Blueprint('auth', __name__)

def check_if_params_empty(auth_params):
    return  '\n'.join(["Пожалуйста, заполните " + k for k,v in auth_params.items() if v == ''])

def validate_signup_form(auth_params):
    empty_params = check_if_params_empty(auth_params)
    pass_check = ''
    print(empty_params)
    if empty_params == '':
        pass_check = check_passwords_match(auth_params['password'],auth_params['password_rep'])
    valid = (empty_params == '') and (pass_check == '')
    print(valid)
    return valid, empty_params + '\n' + pass_check


def check_passwords_match(pasw,pasw1):
    return 'Пароли не совпадают' if pasw != pasw1 else ''


@auth_bp.route('/signup', methods=['GET'])
def signup(): 
    return render_template('signup.html')

@auth_bp.route('/signup', methods=['POST'])
def signup_post(): 
    auth_params = request.form.to_dict()   
    valid_flg,err = validate_signup_form(auth_params)
    print(valid_flg,err)
    if not valid_flg:
        flash(err)
        return redirect(url_for('auth.signup')) 
    hashed_password = generate_password_hash(request.form.get('password'), method='sha256')
    user = User.query.filter_by(login=request.form.get('username')).first()
    if not user:
        new_user = User(login=request.form.get('username'), pass_hash=hashed_password)
        db.session.add(new_user) 
        db.session.commit()
    else:
        flash('User address already exists')
        return redirect(url_for('auth.signup'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')
   

@auth_bp.route('/login', methods=['POST'])
def login_post():
    login = request.form.get('login')
    passw = request.form.get('password')
    remember = request.form.get('remember')
    user = User.query.filter_by(login=login).first()
    if not user:
        flash('User is not founded')
        return redirect(url_for('auth.login'))

    if not check_password_hash(user.pass_hash,passw):
        flash('Incorrect password')
        return redirect(url_for('auth.login'))
    login_user(user=user,remember=remember)
    return redirect(url_for('items.get_items'))


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return redirect(url_for('items.index'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


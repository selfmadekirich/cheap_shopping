from extensions import db,login_manager
from flask_login import  UserMixin


class User(db.Model,UserMixin):
    id = db.Column(db.BIGINT, primary_key = True)
    login = db.Column(db.String(15), unique = True)
    email = db.Column(db.String(120), unique = True)
    pass_hash = db.Column(db.String(128),nullable=False)
    user_templates = db.relationship('User_templates', backref = 'owner_id', lazy = 'dynamic')

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

class User_templates(db.Model):
    id = db.Column(db.BIGINT, primary_key = True)
    user_id = db.Column(db.BIGINT,db.ForeignKey('user.id'))
    items = db.Column(db.ARRAY(db.BIGINT),nullable = False)
    name = db.Column(db.String(120),nullable=False)

class Items(db.Model):
    __table_args__ = {"schema":"info"}
    item_id = db.Column(db.BIGINT,primary_key=True)
    item_name = db.Column(db.String(120),nullable=False)


class SavedItemsCard:
    def __init__(self,id,name,items):
        self.id = id
        self.items = items
        self.name = name

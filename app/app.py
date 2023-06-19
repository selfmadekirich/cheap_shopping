from flask import Flask
from items import items_bp
from auth import auth_bp
from saved_items import saved_items_bp
from extensions import db,jwt,login_manager,sess



app = Flask(__name__)


app.config.from_object('config')


db.init_app(app)
jwt.init_app(app)
login_manager.init_app(app)
sess.init_app(app)


app.register_blueprint(items_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(saved_items_bp)

app.run(host="0.0.0.0")

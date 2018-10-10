from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

basedir = path.abspath(path.dirname(__file__))

# Configure database
app.config['SECRET_KEY'] = '2aec8317ea23944c6328c3db31ca42ab'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['DEBUG'] = False
db = SQLAlchemy(app)

# Configure authentication
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "site.login"
login_manager.init_app(app)

from mewpy.api.routes import api as api_blueprint
from mewpy.site.routes import site as site_blueprint

app.register_blueprint(site_blueprint)
app.register_blueprint(api_blueprint, url_prefix='/api')

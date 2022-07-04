from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='static')
app.secret_key = 'aiuYbK/Beob0/ABOKlO0p6Rn89xAMQWlFJSAWHV9hYc='
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/vpark?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
db = SQLAlchemy(app)

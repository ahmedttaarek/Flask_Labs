from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///instance/project.db"
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)

from app import views  # Import views after app and db initialization

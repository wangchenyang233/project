from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# 实例化SQLAlchemy
db = SQLAlchemy()

# 实例化Celery
celery = Celery(__name__)

# 实例化CORS
cors = CORS()

# 实例化JWTManager
jwt = JWTManager()

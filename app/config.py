import os
from dotenv import load_dotenv
import redis

load_dotenv()


basedir = os.path.abspath(os.path.dirname(__file__))


SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SECRET_KEY = os.getenv('SECRET_KEY')
JWT_SECRET_KEY = os.getenv('SECRET_KEY')
JWT_TOKEN_LOCATION=['cookies']
JWT_REFRESH_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_SECURE=os.getenv('JWT_COOKIE_SECURE')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
SESSION_TYPE = 'redis'
SESSION_REDIS = redis.from_url(os.getenv('SESSION_REDIS'))

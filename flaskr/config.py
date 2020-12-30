

class Config(object):
    DEBUG= False
    TESTING=False
    
    SECRET_KEY = "asdfgh1234"

    DB_NAME = "production-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "password123"

    APP="src/app.py"
    

class ProductionConfig(Config):
    ENV="production"


class DevelopmentConfig(Config):
    DEBUG= True
    ENV="development"

    DB_NAME = "development-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "password123"

    SESSION_COOKIE_SECURE= False


class TestingConfig(Config):
    TESTING= True
    ENV="development"

    DB_NAME = "development-db"
    DB_USERNAME = "root"
    DB_PASSWORD = "password123"

    SESSION_COOKIE_SECURE= False

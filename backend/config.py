import os

class Settings:
    DB_URL = os.getenv('DB_URL', 'sqlite:///./stablecoin.db')
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
    JWT_ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
    DEBUG = os.getenv('DEBUG', '1') == '1'

settings = Settings()

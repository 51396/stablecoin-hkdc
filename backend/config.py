import os

class Settings:
    DB_URL = os.getenv('DB_URL', 'sqlite:///./stablecoin.db')
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
    JWT_ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
    DEBUG = os.getenv('DEBUG', '1') == '1'
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '0x1857de56F21047537EC4054dE6036B2499028EC7')
    WEB3_PROVIDER_URI = os.getenv('WEB3_PROVIDER_URI', 'http://localhost:8545')

settings = Settings()

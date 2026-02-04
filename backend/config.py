import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Azure SQL Database connection string
    SQL_SERVER = os.environ.get('SQL_SERVER')
    SQL_DATABASE = os.environ.get('SQL_DATABASE')
    SQL_USERNAME = os.environ.get('SQL_USERNAME')
    SQL_PASSWORD = os.environ.get('SQL_PASSWORD')

    # Build connection string only if all variables are set
    if SQL_SERVER and SQL_DATABASE and SQL_USERNAME and SQL_PASSWORD:
        # Encode password to handle special characters
        SQLALCHEMY_DATABASE_URI = (
            f"mssql+pymssql://{SQL_USERNAME}:{quote_plus(SQL_PASSWORD)}@{SQL_SERVER}/{SQL_DATABASE}"
        )
    else:
        # Fallback to SQLite for local development/testing
        SQLALCHEMY_DATABASE_URI = 'sqlite:///theater.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Stripe (Payment Gateway)
    # WAŻNE: Klucze powinny być w zmiennych środowiskowych!
    # Nigdy nie commituj prawdziwych kluczy do repozytorium!
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
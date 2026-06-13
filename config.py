from dotenv import load_dotenv
load_dotenv()
import os

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_USER = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')

    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSION = 'csv'

    REQUIRED_COLUMNS = {
        'tx_id',
        'date',
        'merchant',
        'amount',
        'currency',
        'status',
        'category',
        'account_id'
    }
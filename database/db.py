import mysql.connector
from mysql.connector import Error
from config import Config
import logging
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host = Config.DB_HOST,
            password = Config.DB_PASSWORD,
            port = Config.DB_PORT,
            user = Config.DB_USER,
            database = Config.DB_NAME
        )
        if connection.is_connected():
            return connection
        
    except Error as e:
        logger.error(f'Error Connection to database with error: {e}')
        return None
    
def init_database():
    try:
        conn = mysql.connector.connect(
            host = Config.DB_HOST,
            password = Config.DB_PASSWORD,
            port = Config.DB_PORT,
            user = Config.DB_USER,
            database = Config.DB_NAME
        )
        if conn.is_connected():
            cursor = conn.cursor()

        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}')
        cursor.execute(f'USE {Config.DB_NAME}')

        with open('database/schema.sql', 'r') as f:
            sql_commands = f.read().split(';')
            for commands in sql_commands:
                if commands.strip():
                    cursor.execute(commands)
        conn.commit()
        conn.close()
            
    except Exception as e:
        logger.error('Database Initialization Failed with error {e}')
        return None
    

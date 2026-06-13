import mysql.connector
import json
from mysql.connector import Error
from config import Config
import pandas as pd
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
        logger.error(f'Database Initialization Failed with error: {e}')
        return None
    
def create_job(
    filename,
    filepath,
    raw_count,
    clean_count
):
    conn = get_db_connection()

    if not conn:
        return None

    cursor = conn.cursor()

    query = """
    INSERT INTO job(
        filename,
        file_path,
        status,
        row_count_raw,
        row_count_clean
    )
    VALUES(
        %s,%s,%s,%s,%s
    )
    """

    values = (
        filename,
        filepath,
        'processing',
        raw_count,
        clean_count
    )

    cursor.execute(
        query,
        values
    )

    conn.commit()

    job_id = (
        cursor.lastrowid
    )

    cursor.close()
    conn.close()

    return job_id

def save_transactions(
    job_id,
    cleaned_csv
):
    conn = get_db_connection()

    if not conn:
        return

    cursor = conn.cursor()

    query = """
    INSERT INTO payment_transaction(
        job_id,
        txn_id,
        date,
        merchant,
        amount,
        currency,
        status,
        category,
        account_id,
        is_anomaly,
        anomaly_reason,
        llm_category
    )
    VALUES(
        %s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,
        %s,%s
    )
    """

    for _, row in cleaned_csv.iterrows():

        values = (
            job_id,

            None if pd.isna(
                row.get('txn_id')
            ) else row.get(
                'txn_id'
            ),

            None if pd.isna(
                row.get('date')
            ) else row.get(
                'date'
            ),

            None if pd.isna(
                row.get('merchant')
            ) else row.get(
                'merchant'
            ),

            None if pd.isna(
                row.get('amount')
            ) else row.get(
                'amount'
            ),

            None if pd.isna(
                row.get('currency')
            ) else row.get(
                'currency'
            ),

            None if pd.isna(
                row.get('status')
            ) else row.get(
                'status'
            ),

            None if pd.isna(
                row.get('category')
            ) else row.get(
                'category'
            ),

            None if pd.isna(
                row.get('account_id')
            ) else row.get(
                'account_id'
            ),

            bool(
                row.get(
                    'is_anomaly',
                    False
                )
            ),

            None if pd.isna(
                row.get(
                    'anomaly_reason'
                )
            ) else row.get(
                'anomaly_reason'
            ),

            None if pd.isna(
                row.get('category')
            ) else row.get(
                'category'
            )
        )
        cursor.execute(
            query,
            values
        )
    
    conn.commit()
    cursor.close()
    conn.close()

def save_summary(
    job_id,
    summary
):
    conn = get_db_connection()

    if not conn:
        return

    cursor = conn.cursor()

    query = """
    INSERT INTO job_summary(
        job_id,
        total_spend_usd,
        total_spend_inr,
        top_merchants,
        anomaly_count,
        narrative,
        risk_level
    )
    VALUES(
        %s,%s,%s,%s,
        %s,%s,%s
    )
    """

    values = (
        job_id,
        summary[
            'total_spend_by_currency'
        ].get('USD', 0),

        summary[
            'total_spend_by_currency'
        ].get('INR', 0),

        json.dumps(
            summary[
                'top_3_merchants'
            ]
        ),

        summary[
            'anomaly_count'
        ],

        summary[
            'spending_narrative'
        ],

        summary[
            'risk_level'
        ].upper()
    )

    cursor.execute(
        query,
        values
    )

    conn.commit()

    cursor.close()
    conn.close()

def update_job_status(
    job_id,
    status,
    error_message=None
):
    conn = get_db_connection()

    if not conn:
        return

    cursor = conn.cursor()

    query = """
    UPDATE job
    SET
        status=%s,
        completed_at=NOW(),
        error_message=%s
    WHERE id=%s
    """

    cursor.execute(
        query,
        (
            status,
            error_message,
            job_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()
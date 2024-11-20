# import pymysql
# from pymysql import OperationalError
import psycopg2
from psycopg2 import OperationalError
from config.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    """MySQLデータベースに接続する関数"""
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if connection:
            return connection
    except OperationalError  as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

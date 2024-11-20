from db.db_connection import get_connection
import streamlit as st
from pymysql import OperationalError

# stock
# def get_stock():
#     """やりたいことリストをDBから取得する関数"""
#     conn = get_connection()
    
#     cursor = conn.cursor()

#     # query = "SELECT * FROM stock_transactions"
#     query = "SELECT * FROM users"

#     cursor.execute(query)

#     results = cursor.fetchall()

#     conn.close()

#     return results

def insert_stock(stock_code, transaction_type, quantity, unit_price, transaction_date, user_id):
    conn = get_connection()
    
    if conn != None:
        try:
            cursor = conn.cursor()

            insert_query = "INSERT INTO stock_transactions (stock_code, transaction_type, quantity, unit_price, transaction_date, user_id) VALUES (%s, %s, %s, %s, %s, %s)"
            # データの挿入
            cursor.execute(insert_query, (stock_code, transaction_type, quantity, unit_price, transaction_date, user_id))
            conn.commit()

        except OperationalError as e:
            st.error(f"データ挿入エラー:{e}")

        finally:
            cursor.close()
            conn.close()

def delete_transaction(stock_code, transaction_date, user_id):
    conn = get_connection()
    
    if conn != None:
        try:
            cursor = conn.cursor()

            delete_query = "delete from stock_transactions where stock_code = %s and transaction_date = %s and user_id = %s"
            # データの挿入
            cursor.execute(delete_query, (stock_code, transaction_date, user_id))
            conn.commit()

        except OperationalError as e:
            st.error(f"データ挿入エラー:{e}")

        finally:
            cursor.close()
            conn.close()

def get_hold_stock_by_code(stock_code, user_id):

    conn = get_connection()
    
    if conn != None:
        try:
            cursor = conn.cursor()

            query = "select sum(case when transaction_type = 'buy' then quantity end) - sum(case when transaction_type = 'sell' then quantity end) from stock_transactions where stock_code = %s and user_id = %s group by stock_code, user_id;"
            
            cursor.execute(query, (stock_code, user_id))
            results = cursor.fetchall()
            if results:
                return results[0][0]
            else:
                return 0

        except OperationalError as e:
            st.error(f"データ取得エラー:{e}")

        finally:
            cursor.close()
            conn.close()

def get_hold_stock_by_user(user_id):

    conn = get_connection()
    
    if conn != None:
        try:
            cursor = conn.cursor()

            query = "select st.stock_code, company_name, round(CAST(AVG(st.unit_price) AS numeric),1), sum(case when transaction_type = 'buy' then quantity end) - sum(case when transaction_type = 'sell' then quantity else 0 end) as hold_quantity, sector_name from stock_transactions st join stock s on st.stock_code = s.stock_code where user_id = %s group by st.stock_code, company_name, sector_name;"
            
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            if results:
                return results
            else:
                return ()

        except OperationalError as e:
            st.error(f"データ取得エラー:{e}")

        finally:
            cursor.close()
            conn.close()

def get_stock_name(stock_code):
    conn = get_connection()
    
    if conn != None:
        try:
            cursor = conn.cursor()

            query = "select company_name from stock where stock_code = %s;"
            
            cursor.execute(query, (stock_code,))
            results = cursor.fetchall()
            if results:
                return results[0][0]
            else:
                return None

        except OperationalError as e:
            st.error(f"データ取得エラー:{e}")

        finally:
            cursor.close()
            conn.close()

def get_transactions_by_user(user_id):
    conn = get_connection()
    
    if conn != None:
        try:
            cursor = conn.cursor()

            query = "select st.stock_code, company_name, quantity, unit_price, transaction_date from stock_transactions st join stock s on st.stock_code = s.stock_code where user_id = %s and transaction_type = 'buy' order by transaction_date;"
            
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            if results:
                return results
            else:
                return None

        except OperationalError as e:
            st.error(f"データ取得エラー:{e}")

        finally:
            cursor.close()
            conn.close()

def get_transaction_years_by_user(user_id):
    conn = get_connection()
    
    if conn != None:
        try:
            cursor = conn.cursor()

            query = "select distinct(substring(TO_CHAR(transaction_date, 'YYYY-MM-DD'), 1,4)) as years from stock_transactions where user_id = %s order by years desc;"
            
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            if results:
                return results
            else:
                return None

        except OperationalError as e:
            st.error(f"データ取得エラー:{e}")

        finally:
            cursor.close()
            conn.close()

def get_users():
    conn = get_connection()
    
    if conn != None:
        try:
            cursor = conn.cursor()

            query = "select username, nickname, password, email, id from users;"
            
            cursor.execute(query)
            results = cursor.fetchall()
            if results:
                return results
            else:
                return None

        except OperationalError as e:
            st.error(f"データ取得エラー:{e}")

        finally:
            cursor.close()
            conn.close()

# todo

# def insert_todo(username, record_date, todo_task, recommendation_source, reference_url):
#     """やりたいことをDBに登録する関数"""
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     query = """
#     INSERT INTO todo_list (username, record_date, todo_task, recommendation_source, reference_url)
#     VALUES (?, ?, ?, ?, ?)
#     """
#     cursor.execute(query, (username, record_date, todo_task, recommendation_source, reference_url))
    
#     conn.commit()
#     conn.close()

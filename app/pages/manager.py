import streamlit as st
import psycopg2
import os
import sys
from sidebar import render_sidebar

render_sidebar()

# プロジェクトのルートディレクトリをPYTHONPATHに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# DB接続情報を環境変数から取得
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_name = os.getenv('POSTGRES_DB')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')

# DB接続
def get_db_connection_home():
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    return conn

st.title("管理画面")
st.write(db_user)
st.write(db_password)
st.write(db_name)
st.write(db_host)
st.write(db_port)

try:
    conn = get_db_connection_home()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM example;")
    rows = cursor.fetchall()

    st.write("Database Content:")
    for row in rows:
        st.write(row)
except Exception as e:
    st.error(f"Database connection error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
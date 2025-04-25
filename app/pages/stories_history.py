import streamlit as st
from sqlalchemy.orm import sessionmaker
from db_setup import TextRecord, SessionLocal
from sidebar import render_sidebar

render_sidebar()

st.title("おはなしのきろく")

# データベースセッションの作成
session = SessionLocal()

# TextRecordの全レコードを取得
records = session.query(TextRecord).all()

# レコードを表示
if records:
    for record in records:
        st.write(f"ID: {record.id}")
        st.write(f"作成日時: {record.created_at}")
        st.write(f"入力テキスト: {record.input_text}")
        st.write(f"出力テキスト: {record.output_text}")
        st.write("---")
else:
    st.write("履歴がありません。")

# セッションを閉じる
session.close()
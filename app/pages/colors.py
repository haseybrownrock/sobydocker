import streamlit as st
from sidebar import render_sidebar

render_sidebar()

# Streamlitのページ設定
st.title("いろ作り")

# スライダーでRGB値を取得
r = st.slider('赤 (R)', 0, 255, 0)
g = st.slider('緑 (G)', 0, 255, 0)
b = st.slider('青 (B)', 0, 255, 0)

# RGB値から色を生成
color = f'rgb({r},{g},{b})'

st.markdown(f'<div style="background-color: {color}; width: 640px; height: 100px;"></div>', unsafe_allow_html=True)

# RGB値を表示
st.write(f'RGB: ({r}, {g}, {b})')
import streamlit as st
from PIL import Image, ImageDraw

# Streamlitのページ設定
st.set_page_config(page_title="色作り", layout="centered")

# スライダーでRGB値を取得
r = st.slider('赤 (R)', 0, 255, 0)
g = st.slider('緑 (G)', 0, 255, 0)
b = st.slider('青 (B)', 0, 255, 0)

# RGB値から色を生成
color = (r, g, b)

# RGB値を表示
st.write(f'RGB: ({r}, {g}, {b})')

# 画像アップロード
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 画像を開く
    image = Image.open(uploaded_file)
    
    # 画像に色をオーバーレイ
    overlay = Image.new('RGBA', image.size, color + (128,))  # 透明度128のオーバーレイ
    combined = Image.alpha_composite(image.convert('RGBA'), overlay)
    
    # 画像を表示
    st.image(combined, caption='合成された画像', use_column_width=True)
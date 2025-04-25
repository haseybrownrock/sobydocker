import streamlit as st
from streamlit_option_menu import option_menu

def render_sidebar():
    with st.sidebar:
        st.page_link("main.py", label="ホーム", icon="🏠")
        st.page_link("pages/qa.py", label="しつもんコーナー", icon="❓")
        st.page_link("pages/stories.py", label="おはなしのつづき", icon="📕")
        st.page_link("pages/stories_history.py", label="おはなしのきろく", icon="📚")
        st.page_link("pages/three_stories.py", label="さんだいばなし", icon="😄")
        st.page_link("pages/colors.py", label="いろづくり", icon="🎨")
        st.page_link("pages/recipe.py", label="レシピ生成AI", icon="🍳")
        st.page_link("pages/recipe_photo.py", label="レシピ生成AI＿写真つき", icon="🥘")
        st.page_link("pages/teachers.py", label="せんせいたち", icon="🏫")

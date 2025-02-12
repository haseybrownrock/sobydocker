import streamlit as st
from openai import OpenAI
import os

# OpenAIクライアントの初期化
client = OpenAI()

# セッション状態の初期化
if "ai_text" not in st.session_state:
    st.session_state["ai_text"] = None  # 初期値を None に設定
if "audio_generated" not in st.session_state:
    st.session_state["audio_generated"] = False
if "ready_to_display" not in st.session_state:
    st.session_state["ready_to_display"] = False  # 文章を表示する状態フラグ
if "audio_file_path" not in st.session_state:
    st.session_state["audio_file_path"] = None  # 音声ファイルパスの初期化
if "show_story" not in st.session_state:
    st.session_state["show_story"] = False  # お話を表示するフラグ

st.title("おはなしのつづき")

# ユーザー入力
user_message = st.text_input(label="おはなしのつづきを考えてくれるよ")

# お話生成ボタン
if st.button("おはなしを生成する") and user_message:
    with st.spinner('お話を生成中...'):
        # ChatGPT APIでお話を生成
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "お話の続きを考えてください。200文字ぐらいです。笑える感じも欲しいです"},
                {"role": "system", "content": "冒険する話以外でお願いします。"},
                {"role": "user", "content": user_message},
            ]
        )
        st.session_state["ai_text"] = completion.choices[0].message.content
        st.session_state["audio_generated"] = False  # 新しいお話生成時にリセット
        st.session_state["ready_to_display"] = True  # 表示ボタンを押すまで非表示
        st.session_state["show_story"] = False  # お話表示フラグをリセット

# お話表示
if st.session_state["ready_to_display"] and st.session_state["ai_text"]:

    # 音声ファイルの生成
    if not st.session_state["audio_generated"]:
        with st.spinner('音声を生成中...'):
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=st.session_state["ai_text"],
                speed=1,
                response_format="mp3"
            )
            audio_file_path = "./speech.mp3"
            response.stream_to_file(audio_file_path)
            st.session_state["audio_file_path"] = audio_file_path
            st.session_state["audio_generated"] = True

    # 再生ボタンを追加
    if st.session_state["audio_generated"]:
        st.write("おはなしができたよ!")
        # Streamlitのオーディオプレーヤーを利用
        st.audio(st.session_state["audio_file_path"], format="audio/mp3", start_time=0)

        # お話を表示するボタン
        if st.button("お話を表示する"):
            st.session_state["show_story"] = True

# お話を表示
if st.session_state["show_story"]:
    st.write(st.session_state["ai_text"])
    # 閉じるボタン
    if st.button("閉じる"):
        st.session_state["show_story"] = False
        st.experimental_rerun()  # セッション状態を即座に反映するためにリロード
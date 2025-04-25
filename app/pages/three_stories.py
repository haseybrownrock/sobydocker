import streamlit as st
from openai import OpenAI
import os
from sidebar import render_sidebar

render_sidebar()

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

st.title("さんだいばなし")
st.write("さんだいばなし（三題噺)とは、落語家さんがおきゃくさんから三つのお題をもらい、それを元にその場でお話を作るものです。お話は「だれが」「なにを」「どこで」を含むようにするのがお作法です。")

# ユーザー入力
who_message = st.text_input(label="だれが")
where_message = st.text_input(label="どこで")
what_message = st.text_input(label="何を使って")

ending_options = ["みんなから感謝される", "いやな思いをする", "楽しい思いをする"]
# selected_ending = st.selectbox("どうなる", ending_options)


# お話生成ボタン
if st.button("おはなしを生成する") and who_message:
    with st.spinner('お話を生成中...'):
        # ChatGPT APIでお話を生成
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "文字数は400文字ぐらいです。"},
                {"role": "system", "content": "冒険する話以外でお願いします。"},
                {"role": "user", "content": f"{who_message}が{where_message}という場所で{what_message}を使って何かをするお話を考えてください。"},
                {"role": "system", "content": f"{who_message},{where_message},{what_message}の特徴を必ず活かしてください"},
                 {"role": "system", "content": f"最後、{who_message}はみんなから喜ばれるような展開にしてください。"},
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
import streamlit as st
from openai import OpenAI
from sidebar import render_sidebar

render_sidebar()

client = OpenAI()

st.title("しつもんコーナー")

# ユーザーからの入力を取得
user_message = st.text_input(label="おさるさん、どうしたのピポ？!")

if user_message:
    # API呼び出し中の進行表示
    with st.spinner("考え中ピポ..."):
        response_placeholder = st.empty()
        # ストリーミングでOpenAI APIに問い合わせ
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは優秀な司書で、名前は「ソービィ」です。ただし、口調が子供で必ず末尾にカタカナでピポとつけます。また、回答は小学校低学年にわかる範囲で漢字を使ってください。"},
                {"role": "user", "content": user_message},
            ],
            stream=True
        )
    

        # ストリーミング応答を順次表示
        full_response = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content
            # 出力を逐次更新
            if content is not None:
                full_response += content
                response_placeholder.markdown(full_response)  
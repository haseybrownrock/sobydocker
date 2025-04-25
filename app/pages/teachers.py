import streamlit as st
import psycopg2
import os
import sys
from sidebar import render_sidebar
import operator
from typing import Annotated, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.runnables import ConfigurableField
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
# 後からmax_tokensの値を変更できるように、変更可能なフィールドを宣言
llm = llm.configurable_fields(max_tokens=ConfigurableField(id='max_tokens'))

ROLES = {
    "1" : {
        "name": "家庭科の先生",
        "description": "家庭科に答える",
        "details": "料理や裁縫、栄養について、正確で子供にも分かりやすい回答を提供してください。口調は子供で、一文ごとに「ピポ」とつける口癖があります"
    },
    "2" : {
        "name": "国語の先生",
        "description": "国語の先生",
        "details": "童話や小説、物語などの文章や、また漢字やことわざに関する質問に上流階級の女性風の口調で回答してください。"
    },
    "3" : {
        "name": "算数の先生",
        "description": "算数の先生",
        "details": "数字や計算、図形に関する質問にギャル風の口調で回答してください。"
    },
    "4" : {
        "name": "理科の先生",
        "description": "理科の先生",
        "details": "自然や科学、生き物についてのことに、小学生にもわかる回答を歌舞伎役者風の文体で回答してください。"
    },
    "5": {
        "name": "社会の先生",
        "description": "社会の先生",
        "details": "社会や政治、職業や会社の仕組み、お金に関することに一文ごとに「キーキー」「キー」「ウッキー」「ウッキョッキョ」のいずれかをつけて回答してください。実は猿なのです"
    },
    "6": {
        "name": "図工の先生",
        "description": "図工の先生",
        "details": "美術、絵画、に用いる道具の使い方の質問に回答してください。芸術作品、画家、彫刻家についての質問にも正確な回答をしてください。口調は女子プロレスラー風です"
    },
    "7": {
        "name": "体育の先生",
        "description": "体育の先生",
        "details": "体操や運動、スポーツのルールなどに関する質問に正確な回答をしてください。口調は９０歳のお爺さん風です"
    },
    "8": {
        "name": "音楽の先生",
        "description": "音楽の先生",
        "details": "音楽や楽器、歌に関する質問にアラビア語で正確な回答をしてください。日本語は回答に含めないでください"
    },
        "9": {
        "name": "英語の先生",
        "description": "英語の先生",
        "details": "英語の使い方や発音について回答します。英語で質問されたら英語で返します。口調はアメリカ人風です。"
    },
    "0": {
        "name": "カウンセラー",
        "description": "スクールカウンセラー",
        "details": "暴言や悪口に対し、共感的で支援的な回答を提供し、可能であれば適切なアドバイスも行なってください。個人的な内容でないものには答えません。45才の女性風で、一番最初に「カウンセラーの私が先生の代わりにお答えします」と言います。"
    },
}

class State(BaseModel):
    query: str = Field(..., description="ユーザーからの質問")
    current_role: str = Field(
        default="", description="選定された回答ロール"
    )
    messages: Annotated[list[str], operator.add] = Field(
        default=[], description="回答履歴"
    )
    current_judge: bool = Field(
        default=False, description="品質チェックの結果"
    )
    judgement_reason: str = Field(
        default="", description="品質チェックの判定理由"
    )

def selection_node(state: State) -> dict[str, Any]:
    query = state.query
    role_options = "\n".join([f"{k}. {v['name']}: {v['description']}" for k, v in ROLES.items()])
    prompt = ChatPromptTemplate.from_template(
    """質問を分析し、この質問が学校の授業のうちどの教科に当てはまるかを考えてください。
    そのあとで、最も適切な回答担当ロールを選択してください。
    ただし、芸術家やスポーツ選手、音楽家などの職業に関する質問は、図工の先生や体育の先生、音楽の先生に振り分けてください。
    知識についての質問であれば、最も適切な回答担当ロールを選択してください。
    もし個人的な内容であっても、最も近いと思う授業のロールを選択してください
    どうしても決められない時のみ、カウンセラーを選択してください
    
    選択肢:
    {role_options}
    
    回答は選択肢の番号（1、2、3、4、5、6、7、8、9、0のいずれか）のみを返してください。
    
    質問: {query}
    """.strip()
    )
    # 選択肢の番号のみを返すことを期待したいため、max_tokensの値を1に変更
    chain = prompt | llm.with_config(configurable=dict(max_tokens=1)) | StrOutputParser()
    role_number = chain.invoke({"role_options": role_options, "query": query})

    selected_role = ROLES[role_number.strip()]["name"]
    return {"current_role": selected_role}

def answering_node(state: State) -> dict[str, Any]:
    query = state.query
    role = state.current_role
    role_details = "\n".join([f"- {v['name']}: {v['details']}" for v in ROLES.values()])
    prompt = ChatPromptTemplate.from_template(
"""あなたは{role}として回答してください。以下の質問に対して、あなたの役割に基づいた適切な回答を提供してください。
ただし、自分の役割に関する情報は含めないでください。

役割の詳細:
{role_details}

質問: {query}

回答:""".strip()
    )
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"role": role, "role_details": role_details, "query": query})
    return {"messages": [answer]}

class Judgement(BaseModel):
    judge: bool = Field(default=False, description="判定結果")
    reason: str = Field(default="", description="判定理由")

def check_node(state: State) -> dict[str, Any]:
    query = state.query
    answer = state.messages[-1]
    prompt = ChatPromptTemplate.from_template(
"""以下の回答の品質をチェックし、問題がある場合は'False'、問題がない場合は'True'を回答してください。
また、その判断理由も説明してください。

ユーザーからの質問: {query}
回答: {answer}
""".strip()
    )
    chain = prompt | llm.with_structured_output(Judgement)
    result: Judgement = chain.invoke({"query": query, "answer": answer})

    return {
        "current_judge": result.judge,
        "judgement_reason": result.reason
    }

workflow = StateGraph(State)
workflow.add_node("selection", selection_node)
workflow.add_node("answering", answering_node)
workflow.add_node("check", check_node)

workflow.set_entry_point("selection")
workflow.add_edge("selection", "answering")
workflow.add_edge("answering", "check")

# checkノードから次のノードへの遷移に条件付きエッジを定義
# state.current_judgeの値がTrueならENDノードへ、Falseならselectionノードへ
workflow.add_conditional_edges(
    "check",
    lambda state: state.current_judge,
    {True: END, False: END}
)

compiled = workflow.compile()




# ここから回答の表示

render_sidebar()

st.title("せんせいたちに聞いてみよう")
st.write("質問を入れると、先生が答えてくれるよ")
st.write("国語、算数、理科、社会、家庭科、図工、体育、音楽、英語の先生がいるよ 全員に会えるかな？")

question=st.text_input(label="質問を入れてね！")



if question:
    # API呼び出し中の進行表

    placeholder = st.empty()

    try:
        initial_state = State(query=question)
        result = compiled.invoke(initial_state)
        st.write(result["messages"][-1])
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        st.error("質問を変えてみてね")

        # # ストリーミング応答を順次表示
        # full_response = ""
        # for chunk in completion:
        #     content = chunk.choices[0].delta.content
        #     # 出力を逐次更新
        #     if content is not None:
        #         full_response += content
        #         response_placeholder.markdown(full_response)
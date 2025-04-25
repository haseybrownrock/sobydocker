import streamlit as st
import json
from openai import OpenAI
from pydantic import BaseModel, Field
import io
import os
from PIL import Image
from sidebar import render_sidebar

render_sidebar()

class Ingredient(BaseModel):
    ingredient: str = Field(description="材料", examples=["鶏もも肉"])
    quantity: str = Field(description="分量", examples=["300g"])


class Recipe(BaseModel):
    ingredients: list[Ingredient]
    instructions: list[str] = Field(
        description="手順", examples=[["材料を切ります。", "材料を炒めます。"]]
    )
    in_english: str = Field(description="料理名の英語")

def generate_illustration(dish_name):
    dalle_response = client.images.generate(
        model="dall-e-2",
        prompt=dish_name,
        n=1,
        size="256x256"
    )
    return dalle_response.data[0].url


client = OpenAI()

OUTPUT_RECIPE_FUNCTION = {
    "name": "output_recipe",
    "description": "レシピを出力する",
    "parameters": Recipe.schema(),
}


PROMPT_TEMPLATE = """
料理のレシピを考えてください。

料理名: {dish}

"""

st.title("レシピ生成AI (写真つき)")

dish = st.text_input(label="料理名")

if dish:
    with st.spinner(text="考え中..."):
        messages = [
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(dish=dish),
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=[OUTPUT_RECIPE_FUNCTION],
            function_call={"name": OUTPUT_RECIPE_FUNCTION["name"]},
        )

        response_message = response.choices[0].message
        function_call_args = response_message.function_call.arguments

        recipe = json.loads(function_call_args)

        st.write("## 材料")
        st.table(recipe["ingredients"])

        # 以下の形式のマークダウンの文字列を作成して表示
        #
        # ## 手順
        # 1. 材料を切ります。
        # 2. 材料を炒めます。
        instructions_markdown = "## 手順\n"
        for i, instruction in enumerate(recipe["instructions"]):
            instructions_markdown += f"{i+1}. {instruction}\n"
        st.write(instructions_markdown)

        recipe_en = recipe["in_english"]
        illustration_url = generate_illustration(recipe_en)
        st.image(illustration_url, caption=dish, use_column_width=True)
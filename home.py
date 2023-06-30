import streamlit as st
import openai
from supabase import create_client

openai.api_key = st.secrets.OPENAI_TOKEN
openai_model_version = "gpt-3.5-turbo-0613"

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

st.markdown(
    """
<style>
footer {
    visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

supabase_client = init_connection()


def generate_prompt(food, ingredient, Emotion, keywords, n):
    prompt = f""" 
{food} 메뉴를 개발할 계획입니다. 주재료는 {ingredient}입니다. {keywords}를 {food} 판매 할 계획입니다. 
신메뉴의 이름을 {Emotion}의 감성으로 독창적으로 {n}개 만들어줘

---
단품: {food}
주재료: {ingredient}
감성: {Emotion}
메뉴: {keywords}
"""
    return prompt.strip()
def request_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo-0613",
        messages=[
            {"role":"system","content":"당신은 센스있는 카피라이터 입니다."},
            {"role":"user","content":prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]
def write_prompt_result(prompt, result):
    data = supabase_client.table("prompt_results")\
        .insert({"prompt": prompt, "result": result})\
        .execute()
    print(data)

st.title("AI MENU Copywriter ✍️")

with st.form("form"):
    food = st.text_input("단품, 세트(필수)", placeholder="세트")
    ingredient = st.text_input("주메뉴(필수)", placeholder="소고기")
    Emotion = st.text_input("감성(필수)", placeholder="10대")
    st.text("요리 이름(최대 3개까지 허용)")
    col1, col2, col3 = st.columns(3)
    with col1:
        keyword_one = st.text_input(placeholder="소불고기", label="keyword_one", label_visibility="collapsed")
    with col2:
        keyword_two = st.text_input(placeholder="물냉면", label="keyword_two", label_visibility="collapsed")
    with col3:
        keyword_three = st.text_input(placeholder="맥주", label="keyword_three", label_visibility="collapsed")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not food:
            st.error("단품, 세트를 입력해주세요")
        elif not ingredient:
            st.error("주재료를 입력해주세요")
        elif not Emotion:
            st.error("감성를 입력해주세요")



        else:
            with st.spinner('AI 가 메뉴를 개발중입니다...'):
                keywords = [keyword_one, keyword_two, keyword_three]
                keywords = [x for x in keywords if x]
                prompt = generate_prompt(food, ingredient, Emotion, keywords, n=5)
                response = request_chat_completion(prompt)
                write_prompt_result(prompt, response)
                st.text_area(
                    label="메뉴 개발 결과",
                    value=response,
                    placeholder="아직 생성된 문구가 없습니다.",
                    height=200
                )
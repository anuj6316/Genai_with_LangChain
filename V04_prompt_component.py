from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import PromptTemplate, load_prompt

load_dotenv()

model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash'
)

st.header("Indian Player Info")

# user_prompt = st.text_input("Enter your prompt here")
player_name = st.text_input("Enter a player name")
style_input = st.selectbox("Select Explanation style", ['Overview of life jurney', 'Cricket career with mathematical data', 'Love life'])
length_input = st.selectbox('Select the Size of paragraph', ['Short (1-2) paragraph', 'Medium (3-5) paragraph', 'Long (detailed explanation)'])

# dynamic prompt
# prompt1 = PromptTemplate(
#     template = """
# Please provide me the information about {player_name}, where mainly focus on the player's {style_input} and can you please generate the content in this {length_input} size.
# here make sure of the couple of things:
# 1. Provide a consise information about the player, if there is a need of mathematical reprensation show it.
# 2. Make the information as factual, accurate as possible and try not to imagine anything if don't know somethings just say so.
# """,
# input_variables=['player_name', 'style_input', 'length_input'],
# validate_template=True)

prompt1 = load_prompt('template.json')

if st.button('Summarize'):
    # prompt = prompt1.invoke({
    #     'player_name':player_name,
    #     'style_input':style_input,
    #     'length_input':length_input
    # })
    # result = model.invoke(prompt)

    chains = prompt1 | model
    result = chains.invoke({
        'player_name':player_name,
        'style_input':style_input,
        'length_input':length_input
    })
    st.write(result.content)
    # pass
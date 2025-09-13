import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAI

llm = OpenAI(model=f'GPT-3.5-turbo-instruct')

response = llm.invoke("who won the last ipl?")

print(response)
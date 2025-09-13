import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash'
)

response = model.invoke("what is the capital of India?")
print(response.content)

# lets do the same thing for openai chatmodel
# from langchain_openai import ChatOpenAI

# model = ChatOpenAI(model="gpt-4")

# response = model.invoke("What is the capital of india?")
# print(response.content)
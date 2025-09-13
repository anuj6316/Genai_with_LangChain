"""
Building a simple chatbot where ai will give response only based on the given user prompt
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')

while True:
    user_input = input("User: ")
    if user_input.lower() in ['quit', 'q', 'exit']:
        break
    ai_res = model.invoke(user_input)
    print(f"AI: {ai_res.content}")
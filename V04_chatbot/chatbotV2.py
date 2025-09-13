"""
Here my goal to add history feature add adding user_input and ai_res into a document or chat_history list.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

chat_history = []

print("*"*50)
while True:
    user_input = input('User: ')
    chat_history.append(user_input)
    if user_input.lower() in ['quit', 'q', 'exit']:
        break
    ai_res = model.invoke(chat_history)
    chat_history.append(ai_res.content)
    print(f"AI: {ai_res.content}")

print("="*50)
print(chat_history)
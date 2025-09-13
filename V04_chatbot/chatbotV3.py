"""
Here my goal is to improve the chat_history form V2 by adding tag for who query or response we are storing 
like diffrentiat between which one is system message or human or ai massasges

to achieve this we can use the method/function from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
"""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')

messages = [
    SystemMessage("You are very helpful assistant but you are little rudy."),
]

while True:
    user_input = input("User: ")
    messages.append(HumanMessage(user_input))
    if user_input.lower() in ['quit', 'q', 'exit']:
        break
    ai_res = model.invoke(messages)
    messages.append(AIMessage(ai_res.content))
    print(f"AI: {ai_res.content}")

print(messages)
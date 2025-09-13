"""
Components of langchain
1. Model
2. Prompts
3. Chains
4. Agents
5. Memory
6. Tools
7. Utilities
8. Indexes
9. Embeddings
10. Vector Stores
11. Document Loaders
12. Document Stores
This is a One the components of langchain.


In this we will we seeing how model components helps us to easy change our LLM models very easily. like how we can change our LLM model from openai to google, anthropic, etc.
"""

from pyexpat import model
from dotenv import load_dotenv
import os

load_dotenv()

# 1st let's code our genai model using google quickstart
from google import genai

client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
res = client.models.generate_content(
    model='gemini-2.0-flash',
    contents="who won the last ipl"
)
print(res.text)

# now lets code for samba nova
from openai import OpenAI

sambanova_client = OpenAI(api_key=os.getenv('SAMBANOVA_API_KEY'), base_url="https://api.sambanova.ai/v1")
res = sambanova_client.chat.completions.create(
    model="Llama-4-Maverick-17B-128E-Instruct",
    messages=[{"role":"user","content":"who won the last ipl"}],
)

print(res.choices[0].message.content)


# form the above we can see for the both model we have different syntx so if in future for our if we want to change our model it will be very hatic for us that's where langchain models components comes in
# now lets try to do the same thing using langchian
# for google
from langchain_google_genai import ChatGoogleGenerativeAI
llm_google = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash',
)
ai_msg = llm_google.invoke("who won the last ipl")
# ai_msg
print("*"*25 + 'Google genai LLM response' + "*"*25)
print(ai_msg.content)

# for sambanova
from langchain_sambanova import ChatSambaNovaCloud
llm_sambanova = ChatSambaNovaCloud(
    model="Meta-Llama-3.3-70B-Instruct",
)
ai_msg = llm_sambanova.invoke("Who won the last ipl")
print("*"*25 + "SambaNova LLM response" + "*"*25)
print(ai_msg.content)
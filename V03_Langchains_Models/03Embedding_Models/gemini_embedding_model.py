from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

result = embeddings.embed_query('My name is anuj kumar')
print(str(result))

documents = [
    "my name is anuj kumar",
    "i am 23 years old",
    'i want to become an engineer'
]

docs_result = embeddings.embed_documents(documents)
print(str(docs_result))
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

# Get the API key from environment variables
api_key = os.getenv("HUGGINGFACEHUB_API_KEY")

if not api_key:
    print("Error: HUGGINGFACEHUB_API_KEY not found in .env file")
    print("Please add HUGGINGFACEHUB_API_KEY=your_token_here to your .env file")
    exit(1)

# Set the environment variable for Hugging Face
os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_key

llm = HuggingFaceEndpoint(
    repo_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    task='text-generation',
    max_length=100,
    temperature=0.7
)

model = ChatHuggingFace(llm=llm)

response = model.invoke('What is the capital of india?')
print(response.content)
from langchain_openai import ChatOpenAI
import os
import httpx

# Optional: load from .env
# from dotenv import load_dotenv
# load_dotenv()
client = httpx.Client(verify=False)

llm = ChatOpenAI(
    
    model="gpt-3.5-turbo",
    api_key="",   # ✅ direct
    http_client=client
)
response = llm.invoke("Hi")

print(response.content)
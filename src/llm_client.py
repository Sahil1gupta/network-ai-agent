# src/llm_client.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()   # .env file se OPENAI_API_KEY load karo

API_KEY = os.getenv("OPENAI_API_KEY")


def get_llm(model: str = "gpt-4o"):
    """
    ChatOpenAI object return karo.

    Available models:
    - "gpt-4o"       ← agents ke liye best (use this)
    - "gpt-4o-mini"  ← faster, cheaper, testing ke liye
    - "gpt-3.5-turbo" ← lightest
    """
    return ChatOpenAI(
        model=model,
        api_key=API_KEY,
        temperature=0    # temperature=0 matlab consistent output
                         # temperature=1 matlab creative/random output
                         # agents ke liye hamesha 0 rakho
    )


def get_embeddings():
    """
    OpenAIEmbeddings object return karo.
    text-embedding-3-small = fast aur accurate embedding model
    """
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=API_KEY
    )
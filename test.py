# test.py
from src.llm_client import get_llm

llm = get_llm(model="gpt-4o-mini")   # testing ke liye mini use karo

response = llm.invoke("Say exactly: STC AutoOSS is ready!")
print(response.content)
# Output: STC AutoOSS is ready!
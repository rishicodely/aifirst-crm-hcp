from agent.llm import llm

response = llm.invoke("HIIII")
print(response.content)
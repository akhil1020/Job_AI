from langchain_ollama import OllamaLLM

llm = OllamaLLM(
    model="gemma4",
    base_url="http://127.0.0.1:11434"
)

response = llm.invoke("Explain quantum computing simply")

print(response)
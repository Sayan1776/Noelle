import ollama

def chat(messages, model="deepseek-r1:8b"):
    response = ollama.chat(
        model=model,
        messages=messages,
        options={
            "temperature": 0.3,
            "num_predict": 1024,
            "repeat_penalty": 1.2,
            "num_ctx": 8192,
        }
    )
    return response["message"]["content"]

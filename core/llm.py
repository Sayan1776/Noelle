import ollama

def chat(messages, model="llama3.1"):
    response = ollama.chat(
        model=model,
        messages=messages,
        options={
            "temperature": 0.3,
            "num_predict": 300,
            "repeat_penalty": 1.2
        }
    )
    return response["message"]["content"]

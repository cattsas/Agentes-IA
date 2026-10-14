from dotenv import load_dotenv
from groq import Groq
import os #Obtiene key de groq
from simple_memory import SimpleMemory

load_dotenv()  # Load environment variables from .env file  

MEMORY_MAX_MSG = 10  # Maximum number of messages to store in memory 

api_key = os.environ.get("GROQ_API_KEY")  # Get the API key from environment variable
client = Groq(api_key=api_key)  # Initialize the Groq client with the API key
memory=SimpleMemory(max_messages=MEMORY_MAX_MSG)  # Initialize memory with a maximum of 5 messages

while True:

    user_text=input("Usuario: ").strip()
    if not user_text:
        continue  # Skip empty input

    if user_text.lower() in ["exit", "salir"]:
        print("Saliendo...")
        break

    #Obtener la memoria
    messages = memory.get_memory()
    messages.append(
        {"role": "user", "content": user_text}
    )

    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages
    )

    msg=resp.choices[0].message
    assistant_msg = msg.content or ""  # Extract the assistant's message content
    print(f"Asistente: {assistant_msg}")

    #Actualizar la memoria
    memory.add("user", user_text)
    memory.add("assistant", assistant_msg)
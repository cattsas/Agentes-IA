from dotenv import load_dotenv
from groq import Groq
import os #Obtiene key de groq
from simple_memory import SimpleMemory
import json
from tools import Tools
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()  # Load environment variables from .env file  

MEMORY_MAX_MSG = 10  # Maximum number of messages to store in memory 


api_key = os.environ.get("GROQ_API_KEY")  # Get the API key from environment variable
client = Groq(api_key=api_key)  # Initialize the Groq client with the API key
memory=SimpleMemory(max_messages=MEMORY_MAX_MSG)  # Initialize memory with a maximum of 5 messages
now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))  # Get the current time in Buenos Aires timezone
SYSTEM_PROMPT = f"""Eres un asistente útil y amigable. Responde de manera concisa y clara." \
                Si no sabes la respuesta, di 'No sé'.
Fecha y hora actual:{now.strftime("%Y-%m-%d %H:%M:%S")} (UTC-3, hora local).

Reglas: Siempre que el usuario te pida crear un evento o consultar disponibilidad, debes usar las herramientas de Google Calendar que tienes disponibles.
        Antes de crear el evento, pedir confirmacion al usuario. Si no confirma, no crear el evento.
"""
TOOLS = [{
    "type":"function",
    "function": {   
        "name":"check_availability",
        "description":"Check availability in Google Calendar between two timestamps,in format RFC3339, e.g., 2024-06-01T09:00:00Z",
        "parameters":{  
            
            "type":"object",
            "properties":{
                "time_ini":{
                    "type":"string",
                    "description":"Start time in RFC3339 format"
                    },
                "time_end":{
                    "type":"string",
                    "description":"End time in RFC3339 format"
                            }
            },
            "required":["time_ini","time_end"]
        }
    }

    },
    {
        "type":"function",
        "function": {
            "name":"create_event",
            "description":(
                "Create an event in Google Calendar with a title, description,"
                " start and end time in RFC3339 format and offset."
                "Eg: 2024-06-01T09:00:00-03:00"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Title of the event"
                    },
                    "start": {
                        "type": "string",
                        "description": "Start time in RFC3339 format"
                    },
                    "end": {
                        "type": "string",
                        "description": "End time in RFC3339 format"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the event (optional)"
                    }
                },
                "required": ["summary", "start", "end"]
            }
        }
    }
]

def process_response(client: Groq, memory_messages: list[dict], user_text: str):
    """
    Process the response from the Groq API and handle function calls if present.
    """
    #Obtener la memoria
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory_messages)
    messages.append(
        {"role": "user", "content": user_text}
    )
    while True:  
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=TOOLS

    )

        msg=resp.choices[0].message
        #Si no hay llamados a herramientas, regresar el mensaje del asistente
        if not getattr(msg, "tool_calls", None):
            return  msg.content or ""  # Extract the assistant's message content

        messages.append({
            "role": "assistant", 
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls] 
        })

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or "{}")

            if name == "check_availability":
                tools = Tools()
                result = tools.check_availability(
                    time_ini=args["time_ini"],
                    time_end=args["time_end"]
                )
            elif name == "create_event":
                tools = Tools()
                result = tools.create_event(
                    summary=args["summary"],
                    start=args["start"],
                    end=args["end"],
                    description=args.get("description", "")
                )
            else:
                print("Se llamó a una herramienta desconocida:", name)
                result = {"error": f"Function {name} not recognized."}

            #Agregamos a los mensajes el resultado de la herramienta
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result,ensure_ascii=False)
            })


while True:

    user_text=input("Usuario: ").strip()
    if not user_text:
        continue  # Skip empty input

    if user_text.lower() in ["exit", "salir"]:
        print("Saliendo...")
        break

    assistant_msg = process_response(client, memory.get_memory(), user_text)    
    print(f"Asistente: {assistant_msg}")

    #Actualizar la memoria
    memory.add("user", user_text)
    memory.add("assistant", assistant_msg)
# Agentes-IA

Agente de consola con memoria corta que usa Groq (`openai/gpt-oss-120b`) y puede consultar la disponibilidad de Google Calendar.

## Archivos

- `agent.py`: bucle de chat con el modelo y definición de herramientas.
- `tools.py`: acceso a Google Calendar (`check_availability`).
- `simple_memory.py`: memoria de los últimos N mensajes.

## Instalación

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuración

### 1. Groq
Copia `.env.example` a `.env` y pon tu API key de [Groq](https://console.groq.com/keys):

```
GROQ_API_KEY=...
```

### 2. Google Calendar
1. En [Google Cloud Console](https://console.cloud.google.com/) crea un proyecto y activa **Google Calendar API**.
2. En la pantalla de consentimiento OAuth, añade tu correo como **usuario de prueba**.
3. Crea una credencial **ID de cliente de OAuth → App de escritorio** y descarga el JSON como `credentials.json` en la raíz del proyecto.
4. Ejecuta `python tools.py`. Se abrirá el navegador para autorizar y se generará `token.json`.

`.env`, `credentials.json` y `token.json` contienen secretos y están en `.gitignore`: no los subas al repositorio.

## Uso

```powershell
python agent.py
```

Escribe `exit` o `salir` para terminar.

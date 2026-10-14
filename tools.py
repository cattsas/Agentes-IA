import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class Tools:
    
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/calendar"]
        self.CREDENTIALS_FILE = "credentials.json"
        self.TOKEN_FILE = "token.json"
        
    def get_calendar_service(self):
        creds = None

        #Revisar si existe el token y cargarlo
        if os.path.exists(self.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)

        #No hay credenciales validas, hacer proceso de autorizacion o refrescar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.CREDENTIALS_FILE):
                    raise FileNotFoundError(f"No se encontró el archivo de credenciales!")
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)

            #Guardar el token generado
            with open(self.TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())

        #Regresar el servicio ya hecho
        return build("calendar", "v3", credentials=creds)
    
    def check_availability(self, time_ini:str, time_end:str):
        print(f"Checking availability from {time_ini} to {time_end}")
        body = {
            "timeMin": time_ini,
            "timeMax": time_end,
            "items": [{"id": "primary"}]
        }   
        service = self.get_calendar_service()
        result = service.freebusy().query(body=body).execute()
        busy=result.get("calendars", {}).get("primary", {}).get("busy", [])
        return{
            "calendar_id": "primary",
            "busy": busy,
            "time_ini": time_ini,
            "time_end": time_end,
            "is_available": len(busy) == 0
        }

if __name__ == "__main__":
    tools = Tools()
    time_ini = "2024-06-01T09:00:00Z"
    time_end = "2024-06-01T10:00:00Z"   
    result = tools.check_availability(time_ini, time_end)
    print(result)

from fastapi import FastAPI, Request
import httpx
import uvicorn
import os

app = FastAPI()

# Leemos configuración de variables de entorno
APP_ENV = os.getenv("APP_ENV", "local")
TARGET_URL = os.getenv("TARGET_URL")

@app.get("/")
async def info():
    return {
        "status": "online",
        "environment": APP_ENV,
        "target_configured": TARGET_URL
    }

# Endpoint para recibir (One recibe en v1/dockertwo, Two recibe en v1/dockerone)
# Usaremos una ruta genérica para la demo que acepte ambas
@app.post("/api/v1/{sender}")
async def receive(sender: str, request: Request):
    payload = await request.json()
    print(f"[{APP_ENV}] Recibido de {sender}: {payload}")
    return {"status": "success", "env": APP_ENV, "received_from": sender}

@app.get("/send")
async def trigger():
    payload = {"msg": f"hola soy dockerone en ambiente {APP_ENV}"}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(TARGET_URL, json=payload)
            return {
                "action": "sending_to_target",
                "url": TARGET_URL,
                "response": resp.json()
            }
        except Exception as e:
            return {"error": str(e), "url_attempted": TARGET_URL}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

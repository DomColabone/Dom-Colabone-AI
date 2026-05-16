from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CommandRequest(BaseModel):
    command: str

@app.get("/")
def read_root():
    return {"status": "Online", "service": "Dom Colabone API"}

# Novo endpoint para receber comandos do script de voz
@app.post("/execute")
async def handle_command(request: CommandRequest):
    cmd = request.command.lower()
    
    # Exemplo de lógica no servidor
    if "status" in cmd:
        return {"response": "O sistema está operando normalmente no servidor."}
    
    return {"response": f"Servidor recebeu o comando: {cmd}"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Plateforme Pseudo-code")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeIn(BaseModel):
    code: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run(payload: CodeIn):
    # TODO: brancher l'interpréteur ici
    return {"output": f"Reçu {len(payload.code)} caractères"}
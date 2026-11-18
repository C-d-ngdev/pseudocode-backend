from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.interpreter.interpreter import executer_code

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
    return executer_code(payload.code)
    
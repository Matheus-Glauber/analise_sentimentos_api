from fastapi import FastAPI
from pydantic import BaseModel
import json
import re
from google import genai
from dotenv import load_dotenv
import os 

app = FastAPI()

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

class AnaliseSentimento(BaseModel):
    frase: str

historico_analises = []

client = genai.Client(api_key=api_key)

@app.get("/")
def read_root():
    return {
        "info_modelo": "gemini-2.5-flash-lite",
        "descricao": "O modelo têm o intuito de fazer análises de sentimentos a partir de textos."
        }

@app.post("/")
def create_analysis(analisar: AnaliseSentimento):
    prompt = f"Faça uma análise de sentimento (simples, apenas diga se está feliz, triste, empolgada e etc) na frase entre aspas: \"{analisar.frase}\", retorne uma estrutura de json contendo frase_analisada, sentimento, justificativa_analise (essas são as chaves do json)."
    analise_concluida = client.models.generate_content(
        contents=prompt,
        model="gemini-2.5-flash-lite",
    )

    analise_sanitizada = re.sub(r"```json|```", "", analise_concluida.candidates[0].content.parts[0].text).strip() # type: ignore
    analise_json = json.loads(analise_sanitizada)

    historico_analises.append(analise_json)
    return analise_json

@app.get("/historico")
def read_item():
    return historico_analises

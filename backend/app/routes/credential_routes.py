from fastapi import APIRouter
from pydantic import BaseModel
from app.mdp3 import CredentialGeneratorMDP

router = APIRouter()

class GenerateRequest(BaseModel):
    wordlistPath: str
    usernameOptions: dict
    passwordOptions: dict

@router.post("/api/ml/generate")
async def generate_credentials(data: GenerateRequest):
    try:
        csv_path = "web_text.csv"
        wordlist_path = data.wordlistPath
        generator = CredentialGeneratorMDP(csv_path, wordlist_path)
        credentials = generator.generate_credentials(10)
        return {"credentials": [{"username": u, "password": p} for u, p in credentials.items()]}
    except Exception as e:
        return {"error": str(e)}

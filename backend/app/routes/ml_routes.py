from fastapi import APIRouter, HTTPException
from app.ml.mdp3 import generate_credentials, load_data, extract_and_process_web_data
from app.ml.AI_Wordlist import save_credentials_to_csv
import os

router = APIRouter()

@router.post("/api/ml/generate")
async def generate_credentials_api(payload: dict):
    try:
        # Extract data from payload
        wordlist_path = payload.get("wordlistPath")
        if not wordlist_path or not os.path.exists(wordlist_path):
            raise HTTPException(status_code=400, detail="Invalid wordlist path.")

        wordlist = load_data(wordlist_path)
        web_data = extract_and_process_web_data("https://example.com")  # Replace with actual URL logic if needed

        credentials = generate_credentials(wordlist, web_data)

        save_path = "generated_credentials.csv"
        save_credentials_to_csv(save_path, credentials)

        return {"status": "success", "credentials": credentials}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
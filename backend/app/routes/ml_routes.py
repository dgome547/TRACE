from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import json
from app.ml.mdp3 import CredentialGeneratorMDP, load_data, extract_and_process_web_data
from app.ml.AI_Wordlist import save_credentials_to_csv

router = APIRouter()

@router.post("/api/ml/generate")
async def generate_credentials_api(
    usernameOptions: str = Form(...),
    passwordOptions: str = Form(...),
    files: List[UploadFile] = File(None)
):
    try:
        # Parse JSON options
        username_options = json.loads(usernameOptions)
        password_options = json.loads(passwordOptions)

        print("📥 Username options:", username_options)
        print("📥 Password options:", password_options)

        wordlist_data = []

        if files:
            for file in files:
                content = await file.read()
                # Assume UTF-8 and split by newline for wordlist
                lines = content.decode("utf-8").splitlines()
                wordlist_data.extend(lines)
            print("📁 Parsed wordlist lines:", wordlist_data)
        else:
            print("⚠️ No files uploaded. Proceeding with empty wordlist.")

        # Simulated web scraping
        web_data = extract_and_process_web_data("https://example.com")

        # Generate credentials
        credentials = generate_credentials(wordlist_data, web_data)

        # Save to CSV
        save_path = "generated_credentials.csv"
        save_credentials_to_csv(save_path, credentials)

        return {"status": "success", "credentials": credentials}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
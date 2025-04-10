from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
from app.ml.mdp3 import CredentialGeneratorMDP

router = APIRouter()

# Ensure temp directory exists
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/api/ml/generate")
async def generate_credentials(
    csv_file: UploadFile = File(...),
    wordlist: UploadFile = File(...)
):
    try:
        # Save uploaded CSV file
        csv_path = os.path.join(TEMP_DIR, csv_file.filename)
        with open(csv_path, "wb") as f:
            f.write(await csv_file.read())

        # Save uploaded wordlist
        wordlist_path = os.path.join(TEMP_DIR, wordlist.filename)
        with open(wordlist_path, "wb") as f:
            f.write(await wordlist.read())

        # Run the credential generator
        generator = CredentialGeneratorMDP(csv_path, wordlist_path)
        credentials = generator.generate_credentials(10)

        # Format the response
        response_data = {
            "credentials": [{"username": u, "password": p} for u, p in credentials.items()]
        }
        return JSONResponse(content=response_data)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate credentials: {str(e)}"}
        )

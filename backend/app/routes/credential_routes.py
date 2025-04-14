from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse
from app.ml.mdp3 import CredentialGeneratorMDP
import os
import shutil

router = APIRouter()

@router.post("/api/ml/generate")
async def generate_credentials(
    csv_file: UploadFile = None,
    wordlist: UploadFile = None,
    csv_path: str = Form(""),
    wordlist_path: str = Form(""),
    username_length: int = Form(8),
    password_length: int = Form(12),
    use_numbers: str = Form("true"),
    use_symbols: str = Form("true"),
    use_uppercase: str = Form("true")
):
    # Save uploaded files to temp directory
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    if csv_file:
        csv_path = os.path.join(temp_dir, csv_file.filename)
        with open(csv_path, "wb") as f:
            shutil.copyfileobj(csv_file.file, f)

    if wordlist:
        wordlist_path = os.path.join(temp_dir, wordlist.filename)
        with open(wordlist_path, "wb") as f:
            shutil.copyfileobj(wordlist.file, f)

    # Initialize the generator
    generator = CredentialGeneratorMDP(csv_path, wordlist_path)

    # Apply user settings from form
    generator.update_settings({
        "username_length": username_length,
        "password_length": password_length,
        "use_numbers": use_numbers == "true",
        "use_symbols": use_symbols == "true",
        "use_uppercase": use_uppercase == "true"
    })

    try:
        creds_dict = generator.generate_credentials(10)
        credentials = [{"username": u, "password": p} for u, p in creds_dict.items()]
        return {"credentials": credentials}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to generate credentials: {str(e)}"})

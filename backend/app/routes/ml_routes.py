from fastapi import UploadFile, File, Form, APIRouter
from fastapi.responses import JSONResponse
from app.ml.mdp3 import CredentialGeneratorMDP
from typing import List
import json
import os
import shutil
import tempfile

router = APIRouter()

@router.post("/api/ml/generate")
async def generate_credentials(
    usernameOptions: str = Form(...),
    passwordOptions: str = Form(...),
    files: List[UploadFile] = File(None)
):
    username_opts = json.loads(usernameOptions)
    password_opts = json.loads(passwordOptions)

    # Save uploaded files to temp dir
    temp_dir = tempfile.mkdtemp()
    wordlist_paths = []

    if files:
        for file in files:
            path = os.path.join(temp_dir, file.filename)
            with open(path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            wordlist_paths.append(path)

    # Use default wordlist if none were uploaded
    if not wordlist_paths:
        wordlist_paths = ["data/wordlist.txt"]

    # Create instance of generator
    generator = CredentialGeneratorMDP("dummy.csv", wordlist_paths[0])  # dummy.csv for now

    generator.update_settings({
        "username_length": username_opts.get("length", 8),
        "password_length": password_opts.get("length", 12),
        "use_numbers": username_opts.get("numbers", False) or password_opts.get("numbers", False),
        "use_symbols": username_opts.get("symbols", False) or password_opts.get("symbols", False),
        "use_uppercase": username_opts.get("characters", False) or password_opts.get("characters", False)
    })

    try:
        creds_dict = generator.generate_credentials(10)
        credentials = [{"username": u, "password": p} for u, p in creds_dict.items()]
        return {"credentials": credentials}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to generate credentials: {str(e)}"})
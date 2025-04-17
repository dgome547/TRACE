from fastapi import UploadFile, File, Form, APIRouter
from typing import List
import json

router = APIRouter()

@router.post("/api/ml/generate")
async def generate_credentials(
    usernameOptions: str = Form(...),
    passwordOptions: str = Form(...),
    files: List[UploadFile] = File(None)
):
    username_opts = json.loads(usernameOptions)
    password_opts = json.loads(passwordOptions)

    # Optional file handling
    if files:
        for file in files:
            contents = await file.read()
            # Save or use contents here
            print(f"Received: {file.filename}, {len(contents)} bytes")

    # Call your mdp.py logic here
    print("Username Options:", username_opts)
    print("Password Options:", password_opts)

    return { "message": "Credentials generated!" }
from fastapi import APIRouter, UploadFile, File, Form
from typing import List
import os
import shutil
import time
from app.ml.mdp3 import CredentialGeneratorMDP

router = APIRouter(
    prefix="/api/ml",
    tags=["AI Credential Generator"],
)

@router.post("/generate")
async def generate_credentials(
    username_length: int = Form(...),
    password_length: int = Form(...),
    use_username_chars: bool = Form(...),
    use_username_nums: bool = Form(...),
    use_username_symbols: bool = Form(...),
    use_password_chars: bool = Form(...),
    use_password_nums: bool = Form(...),
    use_password_symbols: bool = Form(...),
    num_to_generate: int = Form(...),
    files: List[UploadFile] = File(...)
):
    # Save uploaded file
    wordlist_folder = "storage/uploads"
    os.makedirs(wordlist_folder, exist_ok=True)
    os.makedirs("storage", exist_ok=True)

    wordlist_path = ""
    for file in files:
        file_location = os.path.join(wordlist_folder, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        wordlist_path = file_location

    web_text_csv_path = "storage/web_text.csv"
    if not os.path.exists(web_text_csv_path):
        with open(web_text_csv_path, "w", encoding="utf-8") as f:
            f.write("id,content,url\n0,demo content,https://example.com\n")

    generator = CredentialGeneratorMDP(
        csv_path=web_text_csv_path,
        wordlist_path=wordlist_path,
        username_length=username_length,
        password_length=password_length,
        use_username_chars=use_username_chars,
        use_username_nums=use_username_nums,
        use_username_symbols=use_username_symbols,
        use_password_chars=use_password_chars,
        use_password_nums=use_password_nums,
        use_password_symbols=use_password_symbols,
    )

    start = time.time()
    credentials = generator.generate_credentials(count=num_to_generate)
    end = time.time()

    response = {
        "credentials": [{"username": u, "password": p} for u, p in credentials.items()],
        "runtime_seconds": round(end - start, 3),
    }
    return response



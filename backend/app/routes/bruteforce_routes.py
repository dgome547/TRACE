from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from app.bruteforcer.bruteforcer import BruteForcer
import os
import shutil
from app.bruteforcer import bruteforcer
from app.bruteforcer.utils import parse_status_codes
router = APIRouter()

@router.post("/api/bruteforce/scan")
async def start_brute_force_scan(
    target_url: str = Form(...),
    wordlist_path: str = Form(""),
    wordlist_file: UploadFile = None,
    max_concurrent_requests: int = Form(5),
    request_timeout: float = Form(5.0),
    output_format: str = Form("json"),
    hide_status: str = Form(""),
    show_only_status: str = Form(""),
):
    # Save uploaded wordlist if provided
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    if wordlist_file:
        wordlist_path = os.path.join(temp_dir, wordlist_file.filename)
        with open(wordlist_path, "wb") as f:
            shutil.copyfileobj(wordlist_file.file, f)

    if not wordlist_path or not os.path.exists(wordlist_path):
        raise HTTPException(status_code=400, detail="No valid wordlist provided.")

    # Parse status code filters
    try:
        hide_status_list = [int(code.strip()) for code in hide_status.split(",") if code.strip()]
        show_only_status_list = [int(code.strip()) for code in show_only_status.split(",") if code.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Status codes must be integers.")

    # Construct configuration dictionary
    config = {
        "target_url": target_url,
        "wordlist_path": wordlist_path,
        "max_concurrent_requests": max_concurrent_requests,
        "request_timeout": request_timeout,
        "output_format": output_format,
        "hide_status": hide_status_list,
        "show_only_status": show_only_status_list
    }

    # Run the brute force scan
    brute_forcer = BruteForcer()
    try:
        result = await brute_forcer.start_scan(config)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Brute force scan failed: {str(e)}"})

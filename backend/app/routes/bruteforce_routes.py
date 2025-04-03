from fastapi import APIRouter, Query
from app.bruteforcer.bruteforcer import run_bruteforce
import os

router = APIRouter()

@router.get("/bruteforce")
def brute_force_api(url: str = Query(..., description="Base URL to scan")):
    wordlist_path = os.path.join("app", "bruteforcer", "wordlist.txt")
    results = run_bruteforce(url, wordlist_path)
    return {"results": results}
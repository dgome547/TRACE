# FastAPI route for handling ML credential generation via uploaded wordlist/csv and user options
from fastapi import UploadFile, File, Form, APIRouter
from fastapi.responses import JSONResponse
from app.ml.mdp3 import CredentialGeneratorMDP
from typing import List
import json
import os
import shutil
import tempfile

# TODO Username, Passowords Regex and length info is not parsed correctly 
# TODO Finalize CSV logic 
# TODO Add support for return of number of usernames generated 
# TODO Add support for return of number of passwords generated 
# TODO Add save wordlist database logic

router = APIRouter()

# Default fallback paths used if user does not upload files
DEFAULT_WORDLIST_PATH = "app/ml/wordlist.txt"
DEFAULT_CSV_PATH = "app/ml/dummy.csv"

# Endpoint to generate credentials using MDP logic based on provided username/password options and optional wordlist/csv files
@router.post("/api/ml/generate")
async def generate_credentials(
    usernameOptions: str = Form(...),
    passwordOptions: str = Form(...),
    files: List[UploadFile] = File(None)
):
    try:
        print("Received request to /api/ml/generate")
        
        # Parse JSON-encoded user options
        print("Raw usernameOptions:", usernameOptions)
        print("Raw passwordOptions:", passwordOptions)
        username_opts = json.loads(usernameOptions)
        password_opts = json.loads(passwordOptions)
        print("Parsed username_opts:", username_opts)
        print("Parsed password_opts:", password_opts)

        # Create a temporary directory to store uploaded files
        # This might need to be changed
        temp_dir = tempfile.mkdtemp()
        csv_path = None
        txt_path = None

        # Save each uploaded file and determine if it's a CSV or TXT
        if files:
            for file in files:
                print("Saving file:", file.filename)
                path = os.path.join(temp_dir, file.filename)
                with open(path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                if file.filename.endswith(".csv"):
                    csv_path = path
                elif file.filename.endswith(".txt"):
                    txt_path = path

        # Use fallback defaults if no files were provided
        if not txt_path:
            print("No .txt file uploaded. Using default wordlist.")
            txt_path = DEFAULT_WORDLIST_PATH
        if not csv_path:
            print("No .csv file uploaded. Using dummy.csv as placeholder.")
            csv_path = DEFAULT_CSV_PATH

        print("Wordlist path:", txt_path)

        # Load the wordlist into memory
        with open(txt_path, 'r') as f:
            wordlist = [line.strip() for line in f.readlines() if line.strip()]

        # Initialize the MDP-based credential generator
        generator = CredentialGeneratorMDP(csv_path, wordlist)

        # Assign user-specified settings to the generator
        generator.username_settings = username_opts
        generator.password_settings = password_opts

        print("Generator created. Running generation...")

        # Run the generator and collect output
        creds_dict = generator.generate_credentials(10)
        print("Generated credentials:", creds_dict)

        # Format results into a list of username/password dicts
        credentials = [{"username": u, "password": p} for u, p in creds_dict.items()]
        
        # Return the credentials as a JSON response
        return {"credentials": credentials}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate credentials: {str(e)}"}
        )
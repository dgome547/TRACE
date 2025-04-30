import os
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import json

# Import the fuzzer module
from app.fuzzer.fuzzer import Fuzzer, FuzzerConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fuzzer_routes")

router = APIRouter(prefix="/api/fuzzer", tags=["fuzzer"])

@router.post("/scan")
async def start_fuzzing(
    target_url: str = Form(...),
    wordlist_file: UploadFile = File(...),
    http_method: str = Form("GET"),
    request_timeout: float = Form(5.0),
    hide_status: Optional[str] = Form(None),
    show_only_status: Optional[str] = Form(None),
    filter_by_content_length: Optional[str] = Form(None),
    cookies: Optional[str] = Form(None),
    additional_parameters: Optional[str] = Form(None),
):
    """
    Start a parameter fuzzing scan with the provided configuration
    
    Args:
        target_url: The target URL with FUZZ placeholder for injection point
        wordlist_file: File with payloads (one per line)
        http_method: HTTP method to use (GET, POST, PUT)
        request_timeout: Timeout for each request in seconds
        hide_status: Comma-separated list of status codes to hide
        show_only_status: Comma-separated list of status codes to show exclusively
        filter_by_content_length: Content length filter expression
        cookies: JSON string of cookies to send with requests
        additional_parameters: JSON string of additional parameters
        
    Returns:
        Results and metrics from the fuzzing operation
    """
    try:
        # Save uploaded wordlist to temporary file
        temp_wordlist = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        try:
            contents = await wordlist_file.read()
            temp_wordlist.write(contents)
            temp_wordlist.close()
            wordlist_path = temp_wordlist.name
        except Exception as e:
            os.unlink(temp_wordlist.name)
            logger.error(f"Error processing wordlist: {e}")
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"Error processing wordlist: {str(e)}"}
            )
        
        # Parse form data
        hide_status_codes = set()
        if hide_status:
            hide_status_codes = set(int(code.strip()) for code in hide_status.split(',') if code.strip())
        
        show_status_codes = set()
        if show_only_status:
            show_status_codes = set(int(code.strip()) for code in show_only_status.split(',') if code.strip())
        
        filter_content_length = []
        if filter_by_content_length:
            # Handle range expressions like ">100", "<500", or "100-500"
            if '-' in filter_by_content_length:
                min_val, max_val = filter_by_content_length.split('-')
                filter_content_length = [int(min_val.strip()), int(max_val.strip())]
            elif filter_by_content_length.startswith('>'):
                min_val = int(filter_by_content_length[1:].strip())
                filter_content_length = [min_val, float('inf')]
            elif filter_by_content_length.startswith('<'):
                max_val = int(filter_by_content_length[1:].strip())
                filter_content_length = [0, max_val]
            else:
                # Single value
                filter_content_length = [int(filter_by_content_length.strip())]
        
        cookie_dict = {}
        if cookies:
            try:
                cookie_dict = json.loads(cookies)
            except json.JSONDecodeError:
                # Try parsing as key-value pairs
                cookie_pairs = cookies.split(';')
                for pair in cookie_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        cookie_dict[key.strip()] = value.strip()
                
        additional_params_dict = {}
        if additional_parameters:
            try:
                additional_params_dict = json.loads(additional_parameters)
            except json.JSONDecodeError:
                # Try parsing as key-value pairs
                param_pairs = additional_parameters.split('&')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        additional_params_dict[key.strip()] = value.strip()
        
        # Create fuzzer configuration
        config = FuzzerConfig(
            target_url=target_url,
            wordlist_path=wordlist_path,
            http_method=http_method,
            cookies=cookie_dict,
            hide_status_codes=hide_status_codes,
            show_status_codes=show_status_codes,
            filter_content_length=filter_content_length,
            additional_parameters=additional_params_dict,
            request_timeout=request_timeout
        )
        
        # Validate configuration before proceeding
        validation_errors = config.validate()
        if validation_errors:
            # Clean up the temporary file
            os.unlink(wordlist_path)
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error", 
                    "errors": validation_errors
                }
            )
        
        # Create fuzzer instance
        fuzzer = Fuzzer()
        
        # Start fuzzing and wait for results (synchronous approach, matching bruteforcer)
        try:
            # Similar to bruteforcer, run the fuzzing operation and wait for results
            result = await fuzzer.start_fuzzing(config)
            
            # Clean up the temporary file after fuzzing is complete
            os.unlink(wordlist_path)
            
            # Return the completed results
            return {
                "status": result.get("status", "error"),
                "results": result.get("results", []),
                "metrics": result.get("metrics", {})
            }
        except Exception as e:
            logger.error(f"Error during fuzzing: {str(e)}")
            # Clean up on error
            os.unlink(wordlist_path)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error during fuzzing: {str(e)}"
                }
            )
        
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Server error: {str(e)}"
            }
        )
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.crawler.crawler import Crawler, crawler_state
from fastapi.responses import JSONResponse
import csv, os, asyncio
from app import state


router = APIRouter()

@router.websocket("/ws/crawler")
async def websocket_crawler(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected.")

    # Use config stored in state.py
    config = state.active_config
    if not config:
        await websocket.send_text("No crawler config received")
        await websocket.close()
        return

    crawler_state["running"] = True
    crawler_state["paused"] = False
    crawler_state["stopped"] = False

    try:
        crawler = Crawler()

        class DummyHttp:
            def fetch(self, url, timeout):
                import requests
                try:
                    return requests.get(url, timeout=timeout)
                except:
                    return None

        await crawler.start_crawling(
            start_url=config["targetUrl"],
            config=config,
            http_handler=DummyHttp(),
            websocket=websocket
        )

        await websocket.close()
        print("Crawler finished and WebSocket closed.")

    except WebSocketDisconnect:
        print(" WebSocket disconnected.")
        crawler_state["stopped"] = True


@router.get("/api/crawler/results")
async def get_crawl_results():
    print(" GET /api/crawler/results called")
    results = []
    try:
        file_path = os.path.abspath("crawl_results.csv")
        # print("Looking for CSV at:", file_path)  # Debug print
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                results.append(row)
        # print("CSV Data fetched:", results)  # Debug print
        return JSONResponse(content=results)
    except Exception as e:
        print("Error reading CSV:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
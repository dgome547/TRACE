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


from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.crawler.crawler import Crawler
from fastapi.responses import JSONResponse
import csv, os, asyncio
import json

def map_frontend_to_crawler_config(frontend_config: dict) -> dict:
    """Maps frontend form keys to crawler internal expected keys."""
    return {
        "depth_limit": int(frontend_config.get("crawlDepth", 1)),
        "timeout": float(frontend_config.get("requestDelay", 5.0)),
        "max_pages": int(frontend_config.get("limitPages", 50)),
        "additional_params": frontend_config.get("additionalParams", {}),
    }

crawler_instance = None
crawler_config = None

router = APIRouter()

@router.post("/api/crawler/start")
async def start_crawler(config: dict):
    global crawler_config
    crawler_config = config
    return {"message": "Crawler config set"}

@router.get("/api/crawler/metrics")
async def get_crawler_metrics():
    try:
        if not os.path.exists("crawl_metrics.json"):
            return JSONResponse(content={
                "start_time": "",
                "running_time": 0,
                "processed_requests": 0,
                "filtered_requests": 0,
                "requests_per_second": 0
            })

        with open("crawl_metrics.json", "r") as f:
            data = json.load(f)
            return JSONResponse(content=data)
    except json.JSONDecodeError:
        return JSONResponse(status_code=500, content={"error": "Failed to parse metrics JSON."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.websocket("/ws/crawler")
async def websocket_crawler(websocket: WebSocket):
    global crawler_instance, crawler_config

    await websocket.accept()
    print("WebSocket connected.")

    if not crawler_config:
        await websocket.send_text("No crawler config received")
        await websocket.close()
        return

    try:
        crawler_instance = Crawler()

        # Import your real HTTP handler
        from app.crawler.httphandler import HttpHandler
        http_handler = HttpHandler()

        # Map frontend config to what Crawler expects
        internal_crawler_config = map_frontend_to_crawler_config(crawler_config)

        # Modify the crawler's _send_update method to send full dictionary
        original_send_update = crawler_instance._send_update

        async def send_update_full(websocket, url, result_entry, config, in_progress):
            progress = min(100, int(crawler_instance.stats["processed_requests"] * 100 / config.get("max_pages", 100)))
            payload = {
                "id": result_entry.get("id", -1),
                "URL": result_entry.get("url", ""),
                "Title": result_entry.get("title", ""),
                "WordCount": result_entry.get("word_count", 0),
                "CharCount": result_entry.get("character_count", 0),
                "LinksFound": result_entry.get("links_found", 0),
                "Error": result_entry.get("error", "false"),
                "progress": progress,
                "stats": {
                    "start_time": str(crawler_instance.stats.get("start_time", "")),
                    "running_time": crawler_instance.stats.get("running_time", 0),
                    "processed_requests": crawler_instance.stats.get("processed_requests", 0),
                    "filtered_requests": crawler_instance.stats.get("filtered_requests", 0),
                    "requests_per_second": crawler_instance.stats.get("requests_per_second", 0)
                }
            }
            await websocket.send_json(payload)

        crawler_instance._send_update = send_update_full

        await crawler_instance.start_crawling(
            start_url=crawler_config["targetUrl"],
            config=internal_crawler_config,
            http_handler=http_handler,
            websocket=websocket
        )

        await websocket.close()
        print("Crawler finished and WebSocket closed.")

    except WebSocketDisconnect:
        print("WebSocket disconnected.")







@router.post("/api/crawler/pause")
async def pause_crawler():
    if crawler_instance:
        await crawler_instance.pause_crawler()
        return {"status": "paused"}
    return {"status": "no crawler running"}, 400

@router.post("/api/crawler/resume")
async def resume_crawler():
    if crawler_instance:
        await crawler_instance.resume_crawler()
        return {"status": "resumed"}
    return {"status": "no crawler running"}, 400

@router.post("/api/crawler/stop")
async def stop_crawler():
    if crawler_instance:
        await crawler_instance.stop_crawler(confirm=True)
        return {"status": "stopped"}
    return {"status": "no crawler running"}, 400

@router.get("/api/crawler/results")
async def get_crawl_results():
    results = []
    try:
        with open("crawl_results.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Map and convert fields as required
                mapped_row = {
                    "id": int(row.get("ID", 0)),
                    "URL": row.get("URL", ""),
                    "Title": row.get("Title", ""),
                    "WordCount": int(row.get("WordCount", 0)),
                    "CharCount": int(row.get("CharacterCount", 0)),
                    "LinksFound": int(row.get("LinksFound", 0)),
                    "Error": row.get("Error", "false")
                }
                results.append(mapped_row)
        return JSONResponse(content=results)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



        #LAST WORKING
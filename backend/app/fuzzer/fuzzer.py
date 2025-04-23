import asyncio
import time
import logging
import json
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime
from .httphandler import HttpHandler
from app.crawler.utils import valid_url



class FuzzerConfig:
    def __init__(self,
                 target_urls: List[str],
                 payloads_path: str,
                 request_timeout: float = 5.0,
                 rate_limit: float = 0.5,
                 export_format: str = "json"):
        self.target_urls = target_urls
        self.payloads_path = payloads_path
        self.request_timeout = request_timeout
        self.rate_limit = rate_limit
        self.export_format = export_format

class FuzzResult:
    def __init__(self, id: int, url: str, payload: str, status_code: int, content_length: int, response_time: float):
        self.id = id
        self.url = url
        self.payload = payload
        self.status_code = status_code
        self.content_length = content_length
        self.response_time = response_time
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "payload": self.payload,
            "status_code": self.status_code,
            "content_length": self.content_length,
            "response_time": round(self.response_time, 3),
            "timestamp": self.timestamp
        }

class Fuzzer:
    def __init__(self):
        self.results = []
        self.state = {"running": False, "paused": False, "stopped": False}
        self.stats = {"start_time": None, "end_time": None, "total_requests": 0}

    def load_payloads(self, path: str) -> List[str]:
        try:
            with open(path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"Failed to load payloads: {e}")
            return []

    async def start_fuzzing(self, config: FuzzerConfig, websocket=None):
        self.state["running"] = True
        self.stats["start_time"] = datetime.now()
        http_handler = HttpHandler(rate_limit=config.rate_limit)
        payloads = self.load_payloads(config.payloads_path)
        task_id = 1

        for url in config.target_urls:
            for payload in payloads:
                if self.state["stopped"]:
                    break
                while self.state["paused"]:
                    await asyncio.sleep(1)

                fuzzed_url = url.replace("FUZZ", payload)
                start = time.time()
                response = await http_handler.fetch(fuzzed_url, config.request_timeout)
                end = time.time()

                if response:
                    result = FuzzResult(task_id, fuzzed_url, payload, response.status_code, len(response.content), end - start)
                    self.results.append(result)
                    self.stats["total_requests"] += 1
                    if websocket:
                        await websocket.send_json({"type": "fuzz_result", "data": result.to_dict()})
                task_id += 1

        self.stats["end_time"] = datetime.now()
        self.state["running"] = False
        if config.export_format == "json":
            self.export_to_json()
        else:
            self.export_to_csv()

    def export_to_json(self, filename="fuzz_results.json"):
        with open(filename, 'w') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)

    def export_to_csv(self, filename="fuzz_results.csv"):
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].to_dict().keys())
            writer.writeheader()
            for r in self.results:
                writer.writerow(r.to_dict())

    async def stop_fuzzing(self):
        self.state["stopped"] = True
        return {"status": "stopped"}

    async def pause_fuzzing(self):
        self.state["paused"] = True
        return {"status": "paused"}

    async def resume_fuzzing(self):
        if self.state["paused"]:
            self.state["paused"] = False
            return {"status": "resumed"}
        return {"status": "error", "message": "Fuzzer is not paused."}

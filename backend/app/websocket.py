from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio
import time
from app.bruteforcer.bruteforcer import BruteForcer

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.scan_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.scan_tasks:
            self.scan_tasks[client_id].cancel()
            del self.scan_tasks[client_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def start_scan(self, client_id: str, config: dict):
        brute_forcer = BruteForcer()
        start_time = time.time()
        total_words = 0
        processed_words = 0
        successful_attempts = 0

        # Count total words in wordlist
        with open(config['wordlist_path'], 'r') as f:
            total_words = sum(1 for _ in f)

        async def update_progress():
            while True:
                elapsed_time = time.time() - start_time
                progress = (processed_words / total_words) * 100 if total_words > 0 else 0
                
                # Calculate estimated time remaining
                if processed_words > 0:
                    time_per_word = elapsed_time / processed_words
                    remaining_words = total_words - processed_words
                    estimated_remaining = remaining_words * time_per_word
                else:
                    estimated_remaining = 0

                # Format time strings
                elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                remaining_str = time.strftime("%H:%M:%S", time.gmtime(estimated_remaining))

                await self.send_message(client_id, {
                    "progress": round(progress, 2),
                    "elapsed_time": elapsed_str,
                    "estimated_time_remaining": remaining_str,
                    "attempts_made": processed_words,
                    "successful_attempts": successful_attempts
                })
                await asyncio.sleep(1)

        async def scan_task():
            try:
                # Start progress updates
                progress_task = asyncio.create_task(update_progress())
                
                # Run the scan
                async for result in brute_forcer.scan_with_updates(config):
                    processed_words += 1
                    if result.get('status_code') in config.get('show_only_status', []):
                        successful_attempts += 1
                        await self.send_message(client_id, {
                            "message": f"[SUCCESS] Found: {result.get('url')} - Status: {result.get('status_code')}"
                        })
                    elif result.get('status_code') not in config.get('hide_status', []):
                        await self.send_message(client_id, {
                            "message": f"[INFO] Trying: {result.get('url')} - Status: {result.get('status_code')}"
                        })

                # Clean up
                progress_task.cancel()
                await self.send_message(client_id, {
                    "message": "[INFO] Scan completed successfully"
                })
                
            except Exception as e:
                await self.send_message(client_id, {
                    "message": f"[ERROR] Scan failed: {str(e)}"
                })
            finally:
                self.disconnect(client_id)

        # Start the scan task
        self.scan_tasks[client_id] = asyncio.create_task(scan_task())

    async def handle_pause(self, client_id: str):
        if client_id in self.scan_tasks:
            # Implement pause logic here
            await self.send_message(client_id, {
                "message": "[INFO] Scan paused"
            })

    async def handle_resume(self, client_id: str):
        if client_id in self.scan_tasks:
            # Implement resume logic here
            await self.send_message(client_id, {
                "message": "[INFO] Scan resumed"
            })

    async def handle_stop(self, client_id: str):
        if client_id in self.scan_tasks:
            self.scan_tasks[client_id].cancel()
            await self.send_message(client_id, {
                "message": "[INFO] Scan stopped"
            })
            self.disconnect(client_id)

manager = WebSocketManager() 
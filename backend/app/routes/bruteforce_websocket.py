from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import your BruteForcer class
from app.bruteforcer.bruteforcer import BruteForcer
from app.bruteforcer.utils import load_wordlist

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bruteforce_websocket")

router = APIRouter(prefix="/api/bruteforce", tags=["bruteforce"])

# Store active websocket connections
active_connections: List[WebSocket] = []

# Store running scan tasks
scan_tasks = {}

class WebSocketManager:
    """Manager for WebSocket connections."""
    
    @staticmethod
    async def connect(websocket: WebSocket):
        await websocket.accept()
        active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(active_connections)}")
        
    @staticmethod
    def disconnect(websocket: WebSocket):
        active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Remaining connections: {len(active_connections)}")
    
    @staticmethod
    async def broadcast(message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        for connection in active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")


class WebsocketAdapter:
    """Adapter to make websocket communication compatible with BruteForcer."""
    
    def __init__(self, websocket: WebSocket = None):
        self.websocket = websocket
        self.connected = True
        self.sent_messages = []
    
    async def send_json(self, data: Dict[str, Any]):
        """Process a JSON message."""
        self.sent_messages.append(data)
        
        # Format the message for frontend
        formatted_message = self._format_message(data)
        
        if self.websocket and self.connected:
            try:
                await self.websocket.send_json(formatted_message)
            except Exception as e:
                logger.error(f"Error sending websocket message: {e}")
                self.connected = False
        
        # Also broadcast to all other connected clients
        try:
            await WebSocketManager.broadcast(formatted_message)
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
    
    def _format_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format messages for frontend display."""
        if data.get("type") == "result":
            return self._format_result_message(data.get("data", {}))
        elif data.get("type") == "stats":
            return self._format_stats_message(
                data.get("data", {}), 
                data.get("progress", 0)
            )
        else:
            # Pass through other message types
            return {
                "type": "terminal_output",
                "message_type": "other",
                "content": data,
                "display": {
                    "color": "white",
                    "text": str(data)
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def _format_result_message(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format a result message for frontend display."""
        status = result.get("status_code", 0)
        url = result.get("url", "unknown")
        content_length = result.get("content_length", 0)
        response_time = result.get("response_time", 0)
        payload = result.get("payload", "")
        error = result.get("error", None)
        
        # Determine message type and color based on status
        if status == 0 or error:
            msg_type = "error"
            color = "red"
            prefix = "ERROR"
        elif 200 <= status < 300:
            msg_type = "success"
            color = "green"
            prefix = str(status)
        elif 300 <= status < 400:
            msg_type = "redirect"
            color = "blue"
            prefix = str(status)
        elif 400 <= status < 500:
            msg_type = "client_error"
            color = "yellow"
            prefix = str(status)
        else:
            msg_type = "server_error"
            color = "red"
            prefix = str(status)
            
        # Create the formatted message
        formatted_message = {
            "type": "terminal_output",
            "message_type": msg_type,
            "content": {
                "prefix": prefix,
                "url": url,
                "payload": payload,
                "content_length": content_length,
                "response_time": round(response_time, 3),
                "error": error
            },
            "display": {
                "color": color,
                "text": f"[{prefix}] {url} - Length: {content_length}, Time: {response_time:.3f}s" + 
                       (f" - Error: {error}" if error else "")
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return formatted_message
    
    def _format_stats_message(self, stats: Dict[str, Any], progress: float) -> Dict[str, Any]:
        """Format a stats message for frontend display."""
        # Create the formatted message
        formatted_message = {
            "type": "terminal_output",
            "message_type": "stats",
            "content": {
                "progress": progress,
                "processed_requests": stats.get("processed_requests", 0),
                "filtered_requests": stats.get("filtered_requests", 0),
                "requests_per_second": stats.get("requests_per_second", 0),
                "running_time": stats.get("running_time", "00:00:00"),
                "raw_running_time": stats.get("raw_running_time", 0)
            },
            "display": {
                "color": "gray",
                "text": (
                    f"Progress: {progress:.1f}% | "
                    f"Processed: {stats.get('processed_requests', 0)} | "
                    f"Time: {stats.get('running_time', '00:00:00')} | "
                    f"Req/sec: {stats.get('requests_per_second', 0):.2f}"
                ),
                "progress_bar": {
                    "value": progress,
                    "max": 100
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return formatted_message


async def run_bruteforce_scan(websocket_adapter, scan_config):
    """Run a bruteforce scan in the background."""
    brute_forcer = BruteForcer()
    
    try:
        # Start the scan with our websocket adapter
        scan_output = await brute_forcer.start_scan(scan_config, websocket_adapter)
        
        # Send completion notification
        await websocket_adapter.send_json({
            "type": "terminal_output",
            "message_type": "info",
            "content": {
                "status": "completed",
                "message": "Scan completed"
            },
            "display": {
                "color": "green",
                "text": "Scan completed successfully!"
            },
            "timestamp": datetime.now().isoformat()
        })
        
        return scan_output
    except Exception as e:
        logger.error(f"Error during scan: {e}")
        
        # Send error notification
        await websocket_adapter.send_json({
            "type": "terminal_output",
            "message_type": "error",
            "content": {
                "status": "error",
                "message": str(e)
            },
            "display": {
                "color": "red",
                "text": f"Scan failed with error: {e}"
            },
            "timestamp": datetime.now().isoformat()
        })
        
        return {"status": "error", "message": str(e)}


@router.websocket("/ws")
async def bruteforce_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time bruteforce updates."""
    client_id = id(websocket)
    websocket_manager = WebSocketManager()
    
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "start_scan":
                    config = message.get("config", {})
                    
                    # Create websocket adapter
                    websocket_adapter = WebsocketAdapter(websocket)
                    
                    # Inform client that scan is starting
                    await websocket.send_json({
                        "type": "terminal_output",
                        "message_type": "info",
                        "content": {
                            "status": "starting",
                            "message": "Starting scan"
                        },
                        "display": {
                            "color": "blue",
                            "text": "Starting bruteforce scan..."
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Start scan in background task
                    task = asyncio.create_task(run_bruteforce_scan(websocket_adapter, config))
                    scan_tasks[client_id] = task
                
                elif message.get("type") == "stop_scan":
                    if client_id in scan_tasks:
                        # Cancel the running task
                        scan_tasks[client_id].cancel()
                        scan_tasks.pop(client_id)
                        
                        await websocket.send_json({
                            "type": "terminal_output",
                            "message_type": "info",
                            "content": {
                                "status": "stopped",
                                "message": "Scan stopped"
                            },
                            "display": {
                                "color": "yellow",
                                "text": "Scan stopped by user"
                            },
                            "timestamp": datetime.now().isoformat()
                        })
                
                elif message.get("type") == "ping":
                    # Respond to ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON data"
                })
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        
        # Cancel any running tasks for this client
        if client_id in scan_tasks:
            scan_tasks[client_id].cancel()
            scan_tasks.pop(client_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


# Modified scan endpoint to support WebSocket initialization
@router.post("/scan/websocket")
async def start_scan_with_websocket(
    background_tasks: BackgroundTasks,
    config: Dict[str, Any]
):
    """
    Start a brute force scan with WebSocket updates.
    This endpoint returns immediately and the scan continues in the background.
    """
    try:
        # Validate configuration
        if "target_url" not in config or not config["target_url"]:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Target URL is required", "field": "target_url"}
            )
        
        if "wordlist_path" not in config or not config["wordlist_path"]:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Wordlist path is required", "field": "wordlist_path"}
            )
        
        # Create a WebSocket adapter for broadcast only (no specific client)
        websocket_adapter = WebsocketAdapter()
        
        # Start scan in background task
        background_tasks.add_task(run_bruteforce_scan, websocket_adapter, config)
        
        return {
            "status": "running",
            "message": "Scan started in background. Connect to WebSocket for real-time updates."
        }
    
    except Exception as e:
        logger.error(f"Error starting scan: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error starting scan: {str(e)}"}
        )
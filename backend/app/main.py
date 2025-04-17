from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.routes import routes, crawler_routes, bruteforce_routes
from app import state


app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(bruteforce_routes.router)
app.include_router(crawler_routes.router)

# Define config schema to receive from frontend
class CrawlerConfig(BaseModel):
    targetUrl: str
    crawlDepth: int
    pageLimit: int
    urlPatterns: str
    userAgent: str
    requestDelay: int
    proxy: str

# Store config globally in state.py
@app.post("/api/crawler")
async def store_crawler_config(config: CrawlerConfig):
    state.active_config = {
        "targetUrl": config.targetUrl,
        "depth_limit": config.crawlDepth,
        "timeout": config.requestDelay
    }
    print(" Received config from frontend:", state.active_config)
    return {"status": "Config stored"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.routes import routes, crawler_routes, ml_routes
from fastapi.responses import Response
from app import state

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PLS change for security. (This allows anyone to use the API)
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(crawler_routes.router)
app.include_router(ml_routes.router)


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)  # No Content

# Define config schema to receive from frontend
class CrawlerConfig(BaseModel):
    targetUrl: str
    crawlDepth: int
    pageLimit: int
    urlPatterns: str
    userAgent: str
    requestDelay: int
    proxy: str

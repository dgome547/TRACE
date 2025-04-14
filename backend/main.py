from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import crawler_routes, credential_routes  # Make sure these files exist
from app import state  # Optional: if you’re storing global config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. Lock this down later!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crawler_routes.router)
app.include_router(credential_routes.router)

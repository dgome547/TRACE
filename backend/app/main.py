from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import routes, crawler_routes, credential_routes  # <- Add your credential router here
from app import state

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router)
app.include_router(crawler_routes.router)
app.include_router(credential_routes.router)  # <- Plug in your MDP generation route

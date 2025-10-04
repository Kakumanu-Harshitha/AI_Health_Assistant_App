from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .sql import create_db_and_tables

# --- CORRECTED IMPORTS ---
# We do not need to import llm_service here, as it's used by other services
from . import auth
from . import query_service
from . import dashboard_service

app = FastAPI(title="AI Health Assistant API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Event
@app.on_event("startup")
def on_startup():
    print("--- 🚀 Backend App Starting Up ---")
    create_db_and_tables()
    print("--- ✨ Startup Complete ---")

# --- CORRECTED ROUTER INCLUSION ---
# The incorrect line for llm_service.router has been removed
app.include_router(auth.router)
app.include_router(query_service.router)
app.include_router(dashboard_service.router)

# Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Health Assistant API"}


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .sql import create_db_and_tables
from . import auth
from . import query_service
from . import dashboard_service

app = FastAPI(title="AI Health Assistant API")

# CORS Middleware to allow requests from the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Event to create database tables
@app.on_event("startup")
def on_startup():
    print("--- 🚀 Backend App Starting Up ---")
    create_db_and_tables()
    print("--- ✨ Startup Complete ---")

# Include the routers from other service files
app.include_router(auth.router)
app.include_router(query_service.router)
app.include_router(dashboard_service.router)

# Root Endpoint for health checks
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Health Assistant API"}

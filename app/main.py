from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.api import ingest_api, quiz_api, answer_api

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Peblo Quiz Engine")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Inject modularized API routes
app.include_router(ingest_api.router)
app.include_router(quiz_api.router)
app.include_router(answer_api.router)

import os
# Create frontend directory unconditionally
os.makedirs("frontend", exist_ok=True)
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
def read_root():
    return {"message": "Welcome to Peblo Quiz Engine API"}

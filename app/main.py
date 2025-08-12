from fastapi import FastAPI, status, HTTPException, Depends
import psycopg2
from typing import List
import time
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from .routers import posts, users, auth

# watch_limit = 23254s

models.Base.metadata.create_all(bind=engine) # Create all tables in the database

app = FastAPI() # Initialize FastAPI application

app.include_router(posts.router)  # Include posts router
app.include_router(users.router)  # Include users router
app.include_router(auth.router)  # Include authentication router

# Database connection setup using psycopg2
max_retries = 5
retries = 0

while retries < max_retries:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="firstinstance",
            cursor_factory=RealDictCursor  # gives dict-like results
        )
        cursor = conn.cursor()
        print("Connected to the database successfully!")
        break
    except Exception as error:
        print("Error connecting to the database:", error)
        print("Retrying in 2 seconds...\n")
        time.sleep(2)
        retries += 1

if retries == max_retries:
    raise Exception("Could not connect to the database after several attempts.")

@app.get("/root", status_code=status.HTTP_200_OK)  # This endpoint is just a test endpoint
def read_root():
    return {"message": "Hello, Ranchi!"}



from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from app import models
from app.database import engine
from app.routers import post, user, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="kyoebrn98",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Successfully connect to database")
        break
    except Exception as error:
        print("Failed to connect to database")
        print(f"Error: {error}")
        time.sleep(2)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Welcome to my api!"}

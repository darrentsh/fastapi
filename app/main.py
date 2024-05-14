from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel

from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas, utils
from .database import engine, get_db
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)

app = FastAPI()



while True:
    try:
        conn = psycopg2.connect(
            host = "localhost", 
            database = "fastapi", 
            user = "postgres", 
            password = "kyoebrn98",
            cursor_factory = RealDictCursor
            )
        cursor = conn.cursor()
        print('Successfully connect to database')
        break
    except Exception as error:
        print("Failed to connect to database")
        print(f'Error: {error}')
        time.sleep(2)

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/")
def root():
    return {"message": "Welcome to my api!"}

@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = f'Cannot find post with id {id}')
    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = f'post with id {id} does not exist')
    post.delete(synchronize_session = False)
    db.commit()
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, udpated_post: schemas.PostUpdate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    db.commit()
    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = f'post with id {id} does not exist')
    post_query.update(udpated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg
import time

app = FastAPI()

class Post(BaseModel):
    Title: str
    Content: str
    Published: bool = True
    Rating: Optional[int] = None

max_retries = 5
retries = 0
while retries < max_retries:
    try:
        conn = psycopg.connect(
            "host=localhost dbname=fastapi user=postgres password=firstinstance",
            row_factory=psycopg.rows.dict_row
        )
        cursor = conn.cursor()
        print("Connected to the database successfully!")
        break  # Exit the loop if connection is successful
    except Exception as error:
        print("Error connecting to the database:", error)
        print("Retrying in 2 seconds...")
        print()
        time.sleep(2)
        retries += 1

if retries == max_retries:
    raise Exception("Could not connect to the database after several attempts.")

my_posts = [{"Title": "Title of first post", "Content": "Content of first post", "id": 1}, 
            {"Title": "Title of second post", "Content": "Content of second post", "id": 2}]

post_id_counter = 3

@app.get("/") # This endpoint returns a welcome message
def read_root():
    return {"message": "Hello, Ranchi!"}

@app.get("/posts") # This endpoint returns all posts
def get_posts():
    cursor.execute("SELECT * FROM posts;")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED) # This endpoint creates a new post
def create_post(post: Post):
    cursor.execute("INSERT INTO posts (title, content, published, rating) " \
                   "VALUES (%s, %s, %s, %s) RETURNING *;", (post.Title, post.Content, 
                                                            post.Published, post.Rating))
    new_post = cursor.fetchone()
    conn.commit()  # Commit the transaction to save changes
    return {"data": new_post}

@app.get("/posts/{post_id}") # This endpoint retrieves a specific post by its ID
def get_a_post(post_id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s;", (post_id,))
    post = cursor.fetchone()
    if post:
        return {"requested post": post}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id {post_id} not found")

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT) # This endpoint deletes a post by its ID
def delete_post(post_id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *;", (post_id,))
    deleted_post = cursor.fetchone()
    conn.commit()  # Commit the transaction to save changes
    if not deleted_post:
        # No post was deleted
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {post_id} not found"
        )
    return {"deleted post": deleted_post}

@app.put("/posts/{post_id}", status_code=status.HTTP_202_ACCEPTED) # This endpoint updates an existing post by its ID
def update_post(post_id: int, post: Post):
    cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s, rating = %s " \
                   "WHERE id = %s RETURNING *;", (post.Title, post.Content, 
                                                  post.Published, post.Rating, post_id))
    updated_post = cursor.fetchone()
    conn.commit()  # Commit the transaction to save changes
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} not found")
    return {"data": updated_post}
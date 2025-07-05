from fastapi import FastAPI, Response, status, HTTPException
from fastapi import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Post(BaseModel):
    Title: str
    Content: str
    Published: bool = True
    Rating: Optional[int] = None

my_posts = [{"Title": "Title of first post", "Content": "Content of first post", "id": 1}, 
            {"Title": "Title of second post", "Content": "Content of second post", "id": 2}]

post_id_counter = 3

@app.get("/")
def read_root():
    return {"message": "Hello, Ranchi!"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    global post_id_counter
    post_dict = post.dict()
    post_dict['id'] = post_id_counter
    my_posts.append(post_dict)
    post_id_counter += 1
    return {"data": post_dict}

@app.get("/posts/{post_id}")
def get_a_post(post_id: int, response: Response):
    for post in my_posts:
        if post['id'] == post_id:
            return {"requested post": post}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id {post_id} not found")

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    global my_posts
    original_length = len(my_posts)
    my_posts = [post for post in my_posts if post['id'] != post_id]

    if len(my_posts) == original_length:
        # No post was deleted
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {post_id} not found"
        )

    return

@app.put("/posts/{post_id}", status_code=status.HTTP_202_ACCEPTED)
def update_post(post_id: int, post: Post):
    for index, existing_post in enumerate(my_posts):
        if existing_post['id'] == post_id:
            updated_post = post.dict()
            updated_post['id'] = post_id
            my_posts[index] = updated_post
            return {"data": updated_post}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id {post_id} not found")


# https://youtu.be/0sOvCWFmrtA?si=qayl0VSyhTg8dgED&t=4967
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Ranchi!"}

@app.get("/posts")
def get_posts():
    return {"data": "This is your posts data"}

@app.post("/create-post")
def create_post():
    return {"message": "Post created successfully"}

https://youtu.be/0sOvCWFmrtA?si=G7Z6XnL4f5oXTCyd&t=3710



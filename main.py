from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Urban Twin API is running!"}
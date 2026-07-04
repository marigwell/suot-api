from fastapi import FastAPI

app = FastAPI()

# GET endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Suot API"}


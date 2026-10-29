from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/health")
async def read_health():
    return {"message": "Service is healthy"}
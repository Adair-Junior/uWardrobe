from fastapi import FastAPI

app = FastAPI(
    title="uWardrobe API",
    description="Backend API for the uWardrobe application.",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
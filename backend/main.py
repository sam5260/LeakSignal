from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import Base, engine
from api import upload, dashboard, hosts, alerts

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LeakSignal PT1 API",
    description="Backend for LeakSignal Prototype 1",
    version="1.0.0"
)

# Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In dev, allow all. Restrict in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(hosts.router)
app.include_router(alerts.router)

@app.get("/")
def read_root():
    return {"status": "success", "message": "LeakSignal API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

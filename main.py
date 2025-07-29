from fastapi import FastAPI
from contextlib import asynccontextmanager

from routes import health, tasks, conversations
from db.session import engine
from db.base import Base
from services.background_worker import start_background_worker
from settings import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)

    # Start background task worker
    start_background_worker()

    yield  # App is now running

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# Register routes
app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(conversations.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

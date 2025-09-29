import uvicorn

from fastapi import FastAPI
from contextlib import asynccontextmanager
from logging import getLogger

from app.core.logging import init_logging
from app.routes import auth, comment, job
from app.core.middleware import JWTMiddleware

# Initialization
init_logging()
logger = getLogger(__name__)

inference_model = {}
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    # TODO: Load ML model here
    yield
    logger.info("Shutting down application")
    inference_model.clear()


app = FastAPI(lifespan=lifespan)

# Routes
app.include_router(auth.router, prefix="/api")
app.include_router(comment.router, prefix="/api/public")
app.include_router(job.router, prefix="/api/public")

# Middlewares
app.add_middleware(JWTMiddleware)


@app.get("/health")
def health_check():
    return {"status": "UP"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)

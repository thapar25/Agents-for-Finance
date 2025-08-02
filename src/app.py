from fastapi import FastAPI
from api.routes import router
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from agents.utils.sql_models import create_db_and_tables
import argparse
import os


async def create_logs_table():
    """Create the logs table if it doesn't exist"""
    try:
        await create_db_and_tables()
        print("✅ Logs table created/verified successfully")

    except Exception as e:
        print(f"❌ Error creating logs table: {e}")
        # Don't raise the exception to prevent app startup failure


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up FastAPI application...")
    await create_logs_table()
    yield
    # Shutdown
    print("🛑 Shutting down FastAPI application...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, tags=["API"])


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


def parse_args():
    parser = argparse.ArgumentParser(description="FastAPI Finance Application")

    # Check if running in Docker (common environment variable set by Docker)
    is_docker = os.getenv("DOCKER_ENV") is not None

    default_host = "0.0.0.0" if is_docker else "127.0.0.1"

    parser.add_argument(
        "--host",
        type=str,
        default=default_host,
        help=f"Host to bind to (default: {default_host})",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )

    return parser.parse_args()


if __name__ == "__main__":
    import uvicorn

    args = parse_args()
    uvicorn.run("app:app", host=args.host, port=args.port, reload=args.reload)

from fastapi import FastAPI
from api.routes import router
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from agents.utils.sql_models import create_db_and_tables


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", reload=True)

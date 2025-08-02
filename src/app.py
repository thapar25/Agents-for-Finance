from fastapi import FastAPI
from api.routes import router
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from agents.utils.services import AsyncSessionLocal


async def create_logs_table():
    """Create the logs table if it doesn't exist"""
    try:
        async with AsyncSessionLocal() as session:
            # Create logs table to match the structure used in log_to_db function
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    user_input TEXT NOT NULL,
                    agent_output LONGTEXT NOT NULL,
                    start_time DATETIME,
                    end_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_session_id (session_id),
                    INDEX idx_created_at (created_at),
                    INDEX idx_start_time (start_time)
                )
            """)
            
            await session.execute(create_table_sql)
            await session.commit()
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
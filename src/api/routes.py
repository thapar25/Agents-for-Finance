from fastapi import APIRouter, BackgroundTasks
from agents.simple_agent import stateful_agent
from agents.utils.services import log_to_db
from agents.utils.models import ChatRequest
from datetime import datetime

router = APIRouter(
    prefix="/api",
)


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.post("/chat")
async def get_chat_response(request: ChatRequest, background_tasks: BackgroundTasks):
    """Process user message and return agent response (no streaming)"""
    start_time = datetime.now()
    config = {"configurable": {"thread_id": request.session_id}}
    response = await stateful_agent.ainvoke(
        {"messages": {"role": "user", "content": request.user_message}}, config=config
    )
    end_time = datetime.now()

    # Add background task to log to database
    background_tasks.add_task(
        log_to_db,
        request.session_id,
        request.user_message,
        response,
        start_time,
        end_time,
        created_at=datetime.now(),
    )
    return {"response": response}

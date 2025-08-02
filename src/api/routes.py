from fastapi import APIRouter, BackgroundTasks, HTTPException
from agents.simple_agent import stateful_agent
from agents.utils.services import log_to_db, serialize_agent_response
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
    try:
        response = await stateful_agent.ainvoke(
            {"messages": {"role": "user", "content": request.user_message}},
            config=config,
        )
    except Exception as e:
        print(f"Error occurred while invoking stateful_agent: {e}")
        response = {"error": str(e)}
        raise HTTPException(
            status_code=503, detail=f"The AI service is currently unavailable.{e}"
        )
    end_time = datetime.now()
    serialized_response = serialize_agent_response(response)

    # Add background task to log to database
    background_tasks.add_task(
        log_to_db,
        session_id=request.session_id,
        user_input=request.user_message,
        agent_output={"response": serialized_response},
        start_time=start_time,
        end_time=end_time,
    )
    return {"response": serialized_response}

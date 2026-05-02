from fastapi import APIRouter, Depends, Request
from src.schemas.chat import ChatQuestion, ChatResponse  # importas desde schemas
from src.config.chatbot_client import get_chatbot, ChatbotClient, generate_chatbot_session_id
from src.api.routes.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/ask", response_model=ChatResponse)
async def ask_librarian(
    body: ChatQuestion,
    request: Request,
    current_user = Depends(get_current_user),
    chatbot: ChatbotClient = Depends(get_chatbot)
):
    browser_session = request.cookies.get("session_id", "default")
    chatbot_session_id = generate_chatbot_session_id(current_user.id, browser_session)

    result = await chatbot.ask(body.question, session_id=chatbot_session_id)

    return {
        "answer": result["answer"],
        "confidence": result["confidence"],
        "source": result["source"],
        "entities": result.get("entities", {})
    }
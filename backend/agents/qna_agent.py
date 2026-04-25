from backend.services.qna_service import rag_answer

async def qna_agent(message: str) -> str:
    return await rag_answer(message)
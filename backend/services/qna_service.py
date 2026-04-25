from backend.services.azure_ai import answer_question_safe, smalltalk_response
from backend.services.chitchat import is_chitchat
from backend.services.rag_store import rag_search


async def rag_answer(question: str) -> str:
    question = question.strip()

    # ✅ 1. Chit-chat
    if is_chitchat(question):
        return await smalltalk_response(question)

    # ✅ 2. RAG search
    retrieved_chunks = await rag_search(question)

    # ✅ 3. Fallback to small-talk
    if not retrieved_chunks:
        return await smalltalk_response(question)

    # ✅ 4. Grounded answer
    context = "\n\n".join(retrieved_chunks)
    return await answer_question_safe(question, context)
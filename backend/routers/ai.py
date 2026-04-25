from fastapi import APIRouter, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.experiment import Experiment
from backend.services.azure_ai import generate_experiment_from_topic,generate_experiment_summary,generate_experiment_review_comment
import uuid, json
from ..services.audit_service import log_event
#from backend.agents.orchestrator_graph import build_orchestrator
from backend.services.qna_service import rag_answer
router = APIRouter(prefix="/ai", tags=["ai"])
from pydantic import BaseModel
#from backend.services.rag_store import search
from backend.services.azure_ai import answer_question_safe, smalltalk_response
from backend.services.chitchat import is_chitchat   
from backend.services.rag_store import rag_search
from backend.agents.orchestrator_graph import build_orchestrator
class RAGQuery(BaseModel):
    question: str
class SummaryRequest(BaseModel):
    text: str
    

def generate_id():
    year = datetime.now().strftime("%y")  # 2-digit year
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"EXP-{year}-{unique_part}"


#  1. AI GENERATION FROM TOPIC

@router.post("/generate_experiment")
def generate_experiment(payload: dict):
    try:
        topic = payload.get("topic")
        if not topic:
            raise HTTPException(status_code=400, detail="Topic missing.")

        # ✅ Call Azure AI
        ai_output = generate_experiment_from_topic(topic)

        experiment_id = generate_id()

        # ✅ Convert AI keys to ELN sections
        sections = []
        for key, value in ai_output.items():
            if key.lower() == "title":
                continue
            sections.append({
                "id": uuid.uuid4().hex,
                "type": key,
                "content": value,
            })

        db = SessionLocal()
        exp = Experiment(
            experiment_id=experiment_id,
            title=ai_output.get("title", "AI Experiment"),
            author="AI-Agent",
            status="NEW",
            sections=json.dumps(sections),
            updated_at=datetime.utcnow()
        )
        db.add(exp)
        db.commit()
        log_event(db=db,user=exp.author,action="CREATE",entity="experiment",                       
            entity_id=exp.experiment_id,details="Experiment created." )
        return {"experiment_id": experiment_id}

    except Exception as e:
        print("🔥 AI GENERATION ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# ✅ 2. AI GENERATION FROM JSON FILE

@router.post("/generate_from_json")
def generate_from_json(payload: dict):
    try:
        raw = payload["json_raw"]
        loaded = json.loads(raw)

        # ✅ If JSON file is a list, take the first element
        if isinstance(loaded, list):
            data = loaded[0]
        else:
            data = loaded

        title = data.get("title") or data.get("Title") or "Imported Experiment"
        author = data.get("Author", "JSON-Import")
        experiment_id = generate_id()

        # ✅ Convert each field into an ELN section
        sections = []
        for key, value in data.items():
            sections.append({
                "id": uuid.uuid4().hex,
                "type": key.replace("_", " ").title(),
                "content": str(value)
            })

        db = SessionLocal()
        exp = Experiment(
            experiment_id=experiment_id,
            title=title,
            author=author,
            status="NEW",
            sections=json.dumps(sections),
            updated_at=datetime.utcnow()
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)
        log_event(db=db,user=exp.author,action="CREATE",entity="experiment",                       
            entity_id=exp.experiment_id,details="Experiment created." )
        return {"experiment_id": experiment_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. AI EXPERIMENT SUMMARIZATION

@router.post("/summarize_experiment")
def summarize_experiment(req: SummaryRequest):
    #print("got in the summary block")
    """
    Summarizes the entire experiment text.
    NOTE: This endpoint only handles text summarization — no chemistry logic.
    """

    full_text = req.text.strip()
    #print(16*"=")
    #print(full_text)
    if not full_text:
        raise HTTPException(status_code=400, detail="Experiment text is empty.")
    ai_output = generate_experiment_summary(full_text)
    #print(ai_output)   
    ##print(10*"_")
    summary = json.dumps(ai_output)
    
    
    return {"summary": summary}


@router.post("/review_comment")
def review_comment(req: SummaryRequest):
    print("review block envoked")
    full_text = req.text.strip()

    if not full_text:
        raise HTTPException(status_code=400, detail="Experiment text is empty.")

    # ✅ Call your existing Azure AI summary function
    comment = generate_experiment_review_comment(full_text)
    print("comment from LLM: ",comment)
    return {"review": comment}
    
# HOME PAGE RAG AGENT
@router.post("/rag_chat")
async def rag_chat(req: RAGQuery):
    question = req.question.strip()
    
# ✅ 1. If chit-chat → use small-talk AI
    if is_chitchat(question):
        answer = await smalltalk_response(question)
        return {"answer": answer}

    # ✅ 2. Use RAG for document-grounded questions
    retrieved_chunks = await rag_search(question)

    # ✅ 3. If no relevant chunks → fallback to small-talk
    if not retrieved_chunks:
        answer = await smalltalk_response(question)
        return {"answer": answer}

    # ✅ 4. Normal RAG answer (grounded)
    context = "\n\n".join(retrieved_chunks)
    answer = await answer_question_safe(question, context)

    return {"answer": answer}

graph = build_orchestrator()

@router.post("/chat")        
async def chat(req: RAGQuery):
    try:
        final_state = None

        # ✅ LangGraph 1.1.6: use astream()
        async for event in graph.astream(
            {
                "message": req.question,
                "user": "system",
            }
        ):
            # Each event is { node_name: state }
            for _, state in event.items():
                final_state = state

        # ✅ Defensive check
        if not final_state or "response" not in final_state:
            return {
                "answer": "⚠️ No response generated by the system."
            }

        return {
            "answer": final_state["response"]
        }

    except Exception as e:
        print("❌ Orchestrator error:", e)

    return {
            "answer": "❌ Internal error while processing your request."
        }


@router.post("/rag_chat1")
async def rag_chat(req: RAGQuery):
    
    answer = await rag_answer(req.question)
    return {"answer": answer}

#async def chat(req: RAGQuery, user=Depends(get_user)): WHEN WE HAVE PROPER AUTHETICATION AND USER BASE


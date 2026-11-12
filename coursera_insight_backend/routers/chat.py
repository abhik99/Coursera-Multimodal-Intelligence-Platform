from fastapi import APIRouter, HTTPException
from schemas import ChatRequest

router = APIRouter(prefix="/chat", tags=["AI Chat"])

_pipeline = None

def get_pipeline():
    """Lazily load RAG pipeline on first chat request to keep server boot light and instant."""
    global _pipeline
    if _pipeline is None:
        from AI_RAG.pipeline import RAGPipeline
        _pipeline = RAGPipeline(top_k=5, min_similarity=0.40)
    return _pipeline

@router.post("/")
def chat(request: ChatRequest):
    """Answer a question using only retrieved content from pgvector."""
    try:
        pipeline = get_pipeline()
        # Route the frontend's question with course context to pipeline
        result = pipeline.answer(request.question, course_title=request.course_title)
        
        return {
            "course_id": request.course_id,
            "question": request.question,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "evidence": result["evidence"] 
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
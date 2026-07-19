"""FastAPI entrypoint for the AI Document Analyzer."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import DocumentAnalyzer
from .schemas import AnalyzeRequest, AnalyzeResponse

app = FastAPI(
    title="AI Document Analyzer",
    description="Classify, summarize and extract entities from documents using an LLM.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = DocumentAnalyzer()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a document and return type, summary, entities and sentiment."""
    return analyzer.analyze(
        text=request.text,
        language=request.language,
        summarize=request.summarize,
    )

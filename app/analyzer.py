"""Core analysis logic.

Uses an LLM when an API key is configured, and transparently falls back to a
lightweight rule-based analyzer so the service is fully runnable offline
(useful for demos, CI and local testing).
"""
from __future__ import annotations

import json
import os
import re
from typing import List

from .schemas import AnalyzeResponse, DocumentType, Entity

_SYSTEM_PROMPT = (
    "You are a document-understanding engine. Given raw text, respond with a "
    "compact JSON object containing: document_type (invoice|resume|contract|"
    "email|other), language (ISO code), summary (<=40 words), entities (list of "
    "{label,value}) and sentiment (positive|neutral|negative). Return JSON only."
)


class DocumentAnalyzer:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        self._api_key = os.getenv("OPENAI_API_KEY")

    # -- public API -----------------------------------------------------
    def analyze(self, text: str, language: str = "auto", summarize: bool = True) -> AnalyzeResponse:
        if self._api_key:
            try:
                return self._analyze_with_llm(text, summarize)
            except Exception:  # pragma: no cover - network/credential issues
                pass
        return self._analyze_rule_based(text, language, summarize)

    # -- LLM path -------------------------------------------------------
    def _analyze_with_llm(self, text: str, summarize: bool) -> AnalyzeResponse:
        from openai import OpenAI  # imported lazily so the dep is optional

        client = OpenAI(api_key=self._api_key)
        completion = client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text[:12000]},
            ],
            temperature=0,
        )
        payload = json.loads(completion.choices[0].message.content)
        entities = [Entity(**e) for e in payload.get("entities", []) if "label" in e]
        return AnalyzeResponse(
            document_type=DocumentType(payload.get("document_type", "other")),
            language=payload.get("language", "en"),
            summary=payload.get("summary") if summarize else None,
            entities=entities,
            sentiment=payload.get("sentiment"),
            token_usage=getattr(completion.usage, "total_tokens", 0),
        )

    # -- offline fallback ----------------------------------------------
    def _analyze_rule_based(self, text: str, language: str, summarize: bool) -> AnalyzeResponse:
        doc_type = self._classify(text)
        entities = self._extract_entities(text)
        summary = None
        if summarize:
            first = re.split(r"(?<=[.!?])\s+", text.strip())
            summary = " ".join(first[:2])[:280]
        return AnalyzeResponse(
            document_type=doc_type,
            language="en" if language == "auto" else language,
            summary=summary,
            entities=entities,
            sentiment=self._sentiment(text),
            token_usage=0,
        )

    @staticmethod
    def _classify(text: str) -> DocumentType:
        t = text.lower()
        if any(k in t for k in ("invoice", "amount due", "total due", "vat")):
            return DocumentType.invoice
        if any(k in t for k in ("curriculum vitae", "resume", "work experience", "skills")):
            return DocumentType.resume
        if any(k in t for k in ("agreement", "hereby", "party", "terms and conditions")):
            return DocumentType.contract
        if any(k in t for k in ("subject:", "dear ", "regards", "sincerely")):
            return DocumentType.email
        return DocumentType.other

    @staticmethod
    def _extract_entities(text: str) -> List[Entity]:
        entities: List[Entity] = []
        for email in set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)):
            entities.append(Entity(label="EMAIL", value=email))
        for amount in set(re.findall(r"(?:€|\$|EUR|USD)\s?\d[\d.,]*", text)):
            entities.append(Entity(label="AMOUNT", value=amount.strip()))
        for date in set(re.findall(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b", text)):
            entities.append(Entity(label="DATE", value=date))
        return entities[:25]

    @staticmethod
    def _sentiment(text: str) -> str:
        pos = len(re.findall(r"\b(great|excellent|thank|good|happy|pleased)\b", text, re.I))
        neg = len(re.findall(r"\b(bad|delay|problem|issue|angry|refund|complaint)\b", text, re.I))
        if pos > neg:
            return "positive"
        if neg > pos:
            return "negative"
        return "neutral"

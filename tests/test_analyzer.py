"""Offline tests for the rule-based fallback (no API key required)."""
from app.analyzer import DocumentAnalyzer
from app.schemas import DocumentType


def test_classifies_invoice():
    analyzer = DocumentAnalyzer()
    result = analyzer.analyze("INVOICE\nTotal due: €1,240.00\nVAT included")
    assert result.document_type == DocumentType.invoice
    assert any(e.label == "AMOUNT" for e in result.entities)


def test_extracts_email():
    analyzer = DocumentAnalyzer()
    result = analyzer.analyze("Dear team, please contact me at hi@example.com. Regards")
    assert result.document_type == DocumentType.email
    assert any(e.label == "EMAIL" for e in result.entities)


def test_summary_present():
    analyzer = DocumentAnalyzer()
    text = "First sentence here. Second sentence here. Third one."
    result = analyzer.analyze(text, summarize=True)
    assert result.summary

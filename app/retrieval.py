"""Small transparent term retrieval with provider-safe seminar handling."""
from __future__ import annotations
import re
from collections import Counter
from typing import Any

STOP = {"the", "and", "for", "with", "what", "how", "are", "does", "from", "this", "that", "about", "can", "you", "ist", "und", "der", "die", "das", "was", "wie", "von", "mit", "für", "ein", "eine", "sind", "gibt", "kann", "ich"}
CONTACT_URL = "https://www.svg-baden.de/"
SENSITIVE = ("legal", "insurance advice", "insured", "compliance", "law", "recht", "versicherung", "arbeitschutz", "arbeitsschutz", "gefährdungsbeurteilung", "risk assessment", "safety advice", "sicherheitsberatung")

def terms(text: str) -> list[str]:
    return [w for w in re.findall(r"[\wäöüß-]+", text.lower()) if len(w) > 2 and w not in STOP]

def retrieve(question: str, sources: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    q = Counter(terms(question))
    if not q:
        return []
    ranked = []
    for source in sources:
        body = Counter(terms(source["title"] + " " + source["text"]))
        score = sum(min(count, body.get(word, 0)) for word, count in q.items())
        if score:
            ranked.append((score, source))
    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [item[1] for item in ranked[:limit]]

def is_sensitive_question(question: str) -> bool:
    q = question.lower()
    return any(word in q for word in SENSITIVE)

def make_answer(question: str, matches: list[dict[str, Any]]) -> tuple[str, bool]:
    if not matches:
        return ("I couldn't find enough information in the available published sources to answer that. Please check the relevant SVG-Baden page or contact SVG-Baden through its official website.", True)
    snippets = [f"**{s['title']}**: {s['text'][:560]}" for s in matches]
    answer = "\n\n".join(snippets)
    if is_sensitive_question(question):
        answer += "\n\nThis is only a summary of published information, not legal, insurance, occupational-safety, or compliance advice. Please ask an SVG-Baden specialist."
    return answer, False

def seminar_results(sources: list[dict[str, Any]], provider_filter: str = "SVG-Baden") -> list[dict[str, Any]]:
    """No listing unless actual course details and provider are verified in corpus."""
    results = []
    for source in sources:
        if source.get("type") != "seminar" or not source.get("course_title"):
            continue
        if provider_filter == "SVG-Baden" and source.get("provider") != "SVG-Baden":
            continue
        results.append(source)
    return results

import json
from pathlib import Path
import unittest
from app.sources import load_sources, parse_source_json, SourceDataError
from app.retrieval import retrieve, make_answer, seminar_results
from app.llm_client import get_config

ROOT = Path(__file__).resolve().parents[1]

class TestAppCore(unittest.TestCase):
    def test_source_parsing_and_attribution(self):
        sources = load_sources(ROOT / "data/sources.json")
        self.assertGreaterEqual(len(sources), 4)
        self.assertTrue(all(s["url"].startswith("https://www.svg-baden.de/") for s in sources))
        self.assertTrue(all(s["retrieved_at"] for s in sources))

    def test_malformed_source_data_is_reported(self):
        with self.assertRaises(SourceDataError):
            parse_source_json('{"sources": "bad"}')

    def test_retrieval_finds_matching_source(self):
        sources = load_sources(ROOT / "data/sources.json")
        self.assertEqual(retrieve("digital occupational safety training", sources)[0]["id"], "digital-safety")

    def test_provider_labeling_does_not_mislabel_other_regions(self):
        other = {"type":"seminar", "course_title":"A", "provider":"SVG Nord"}
        baden = {"type":"seminar", "course_title":"B", "provider":"SVG-Baden"}
        self.assertEqual(seminar_results([other, baden], "SVG-Baden"), [baden])
        self.assertEqual(seminar_results([other, baden], "All providers"), [other, baden])

    def test_no_answer_when_corpus_has_no_match(self):
        answer, no_answer = make_answer("What is the moon made of?", [])
        self.assertTrue(no_answer and "couldn't find enough information" in answer)

    def test_citations_follow_retrieved_sources(self):
        sources = load_sources(ROOT / "data/sources.json")
        matches = retrieve("fleet management partner", sources)
        answer, _ = make_answer("What services are described?", matches)
        self.assertTrue(matches and all(s["url"].startswith("https://") for s in matches))
        self.assertIn("SVG-Baden", answer)

    def test_answer_excerpt_ends_at_sentence_boundary(self):
        source = {"id": "long", "title": "Long source", "url": "https://www.svg-baden.de/", "retrieved_at": "2026-10-26", "provider": "SVG-Baden", "text": "First sentence ends here. " + "Long following sentence " * 60 + "."}
        answer, no_answer = make_answer("first sentence", [source])
        self.assertFalse(no_answer)
        self.assertIn("First sentence ends here.", answer)
        self.assertNotIn("Long following sentence Long following", answer)

    def test_missing_api_key_is_supported(self):
        key, model = get_config({})
        self.assertFalse(key)
        self.assertTrue(model)


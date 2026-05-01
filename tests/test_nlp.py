"""Tests for NLP intent scoring service."""
import sys, os
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only-32chars!")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.nlp import score, score_batch


class TestScore:
    def test_empty_string_returns_zero(self):
        assert score("") == 0.0

    def test_none_returns_zero(self):
        assert score(None) == 0.0

    def test_irrelevant_text_returns_low(self):
        result = score("The weather is nice today")
        assert result == 0.0

    def test_high_intent_signals(self):
        result = score("I'm looking to buy a new CRM tool, can anyone recommend one?")
        assert result >= 0.5, f"Expected high intent, got {result}"

    def test_medium_intent_signals(self):
        result = score("I'm looking for an alternative to HubSpot")
        assert 0.2 <= result <= 0.8, f"Expected medium intent, got {result}"

    def test_low_intent_signals(self):
        result = score("anyone tried Notion for project management?")
        assert 0.05 <= result <= 0.5, f"Expected low intent, got {result}"

    def test_score_is_capped_at_one(self):
        # Load up with every possible signal
        text = (
            "looking to buy, ready to purchase, need a solution, "
            "can anyone recommend, what tool do you use, best software for, "
            "where can i find, looking for, need help with, struggling with, "
            "any recommendations, alternative to, how do you handle, switch from"
        )
        result = score(text)
        assert result <= 1.0

    def test_score_is_float(self):
        result = score("I need help with my project")
        assert isinstance(result, float)

    def test_case_insensitive(self):
        lower = score("i need help with marketing")
        upper = score("I NEED HELP WITH MARKETING")
        assert lower == upper

    def test_multiple_signals_increase_score(self):
        single = score("need")
        multiple = score("I need help, looking for a tool, any recommendations?")
        assert multiple > single


class TestScoreBatch:
    def test_batch_returns_list(self):
        results = score_batch(["hello", "need help", ""])
        assert isinstance(results, list)
        assert len(results) == 3

    def test_batch_matches_individual(self):
        texts = ["looking to buy a CRM", "nice weather", "need help with marketing"]
        batch = score_batch(texts)
        individual = [score(t) for t in texts]
        assert batch == individual

    def test_empty_batch(self):
        assert score_batch([]) == []

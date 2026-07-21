from __future__ import annotations

import unittest

from sitekapinda.models import BusinessCandidate
from sitekapinda.scoring import classify_website, score_candidate


class ScoringTests(unittest.TestCase):
    def test_missing_website_scores_higher_than_present_website(self) -> None:
        base = {
            "place_id": "synthetic-score-001",
            "name": "Fictional Luma Hair Studio",
            "category": "kuafor",
            "city": "Example City",
            "district": "Demo District",
            "phone": "+90 000 000 0101",
            "rating": 4.5,
            "review_count": 50,
            "source": "synthetic_fixture",
        }
        missing = score_candidate(BusinessCandidate(**base, website_url=None))
        present = score_candidate(BusinessCandidate(**base, website_url="https://example.com"))

        self.assertGreater(missing.score, present.score)
        self.assertTrue(missing.eligible)

    def test_social_or_free_builder_website_is_weak(self) -> None:
        self.assertEqual(classify_website("https://instagram.com/example"), "weak")
        self.assertEqual(classify_website("https://sites.google.com/view/example"), "weak")
        self.assertEqual(classify_website("http://example.com"), "weak")


if __name__ == "__main__":
    unittest.main()

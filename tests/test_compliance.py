from __future__ import annotations

import unittest

from sitekapinda.compliance import screen_candidate, validate_generated_html
from sitekapinda.models import BusinessCandidate


class ComplianceTests(unittest.TestCase):
    def test_rejects_regulated_verticals(self) -> None:
        result = screen_candidate(
            BusinessCandidate(
                place_id="synthetic-regulated-1",
                name="Fictional Dental Clinic",
                category="dis klinigi",
                city="Example City",
            )
        )

        self.assertFalse(result.allowed)
        self.assertTrue(any(reason.startswith("regulated_or_sensitive_keyword") for reason in result.reasons))

    def test_generated_html_requires_noindex_and_safe_claims(self) -> None:
        html = """
        <html><head><meta name="robots" content="noindex,nofollow"></head>
        <body>
          Bu sayfa SiteKapında tarafından hazırlanmış bir önizleme sayfasıdır.
          İşletme sahibinin onayı olmadan resmi site olarak yayına alınmayacaktır.
          SEO garantili.
        </body></html>
        """

        result = validate_generated_html(html)

        self.assertFalse(result.allowed)
        self.assertIn("forbidden_claim:seo garantili", result.reasons)


if __name__ == "__main__":
    unittest.main()

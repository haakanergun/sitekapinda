from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path

from sitekapinda.demo_layouts import layout_for_category
from sitekapinda.models import BusinessCandidate
from sitekapinda.page_generation import PageGenerator, render_demo_html
from sitekapinda.scoring import score_candidate


SYNTHETIC_CATEGORIES = (
    "restoran",
    "guzellik salonu",
    "kafe",
    "berber",
    "oto yikama",
    "cicekci",
    "pet kuaforu",
    "spor salonu",
    "ozel kurs",
    "temizlik firmasi",
    "oto servis",
    "hali yikama",
)

# A valid, transparent 1x1 PNG used only to prove packaged files are copied byte-for-byte.
ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def candidate_for(
    category: str,
    place_id: str = "synthetic-test-001",
    source: str = "mock",
) -> BusinessCandidate:
    return BusinessCandidate(
        place_id=place_id,
        name="Örnek Yerel İşletme",
        category=category,
        city="İstanbul",
        district="Kadıköy",
        phone="+90 216 555 0101",
        website_url=None,
        rating=4.6,
        review_count=78,
        source=source,
    )


class PageGenerationTests(unittest.TestCase):
    def test_generates_noindex_raster_only_responsive_demo(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            candidate = candidate_for("kuafor", "mock-kuafor-001")
            scored = score_candidate(candidate)
            page = PageGenerator(Path(temp)).generate(scored)
            html_text = page.path.read_text(encoding="utf-8")
            page_dir = page.path.parent
            brand_kit = json.loads((page_dir / "brand-kit.json").read_text(encoding="utf-8"))
            page_manifest = json.loads((page_dir / "page-manifest.json").read_text(encoding="utf-8"))
            prompt_manifest = json.loads((page_dir / "image-prompts.json").read_text(encoding="utf-8"))
            desktop = page_dir / "assets" / "hero-desktop.png"
            mobile = page_dir / "assets" / "hero-mobile.png"
            asset_names = sorted(item.name for item in (page_dir / "assets").iterdir())

            self.assertTrue(desktop.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertTrue(mobile.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))

        self.assertIn('name="robots" content="noindex,nofollow,noarchive"', html_text)
        self.assertIn("SiteKapında tarafından hazırlanmış bir önizleme", html_text)
        self.assertIn("İşletme sahibinin onayı olmadan", html_text)
        self.assertNotIn("SEO garantili", html_text)
        self.assertNotIn("<svg", html_text)
        self.assertNotIn(".svg", html_text)
        self.assertIn('<picture class="hero-media">', html_text)
        self.assertIn('media="(max-width: 720px)" srcset="assets/hero-mobile.png"', html_text)
        self.assertIn('src="assets/hero-desktop.png"', html_text)
        self.assertIn('class="mobile-menu"', html_text)
        self.assertIn("min-height: 44px", html_text)
        self.assertEqual(asset_names, ["hero-desktop.png", "hero-mobile.png"])
        self.assertEqual(brand_kit["business"]["place_id"], "mock-kuafor-001")
        self.assertEqual(page_manifest["layout_family"], "beauty-studio")
        self.assertEqual(page_manifest["asset_paths"]["hero_image"], "assets/hero-desktop.png")
        self.assertEqual(page_manifest["asset_paths"]["hero_mobile"], "assets/hero-mobile.png")
        self.assertTrue(
            all(value == "deterministic_raster_fallback" for value in page_manifest["asset_provenance"].values())
        )
        self.assertTrue(
            any("aracınıza" in note and "araciniza" in note for note in prompt_manifest["safety_notes"])
        )
        self.assertTrue(
            all("aracınıza" in item["prompt"] and "araciniza" in item["prompt"] for item in prompt_manifest["prompts"])
        )

    def test_copies_matching_packaged_desktop_and_mobile_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            place_id = "synthetic-restaurant-001"
            source_dir = root / "packaged" / place_id
            source_dir.mkdir(parents=True)
            desktop_bytes = ONE_PIXEL_PNG + b"desktop-slot"
            mobile_bytes = ONE_PIXEL_PNG + b"mobile-slot"
            (source_dir / "hero-desktop.png").write_bytes(desktop_bytes)
            (source_dir / "hero-mobile.png").write_bytes(mobile_bytes)

            page = PageGenerator(root / "output", demo_assets_dir=root / "packaged").generate(
                score_candidate(candidate_for("restoran", place_id))
            )
            page_dir = page.path.parent
            manifest = json.loads((page_dir / "page-manifest.json").read_text(encoding="utf-8"))

            self.assertEqual((page_dir / "assets" / "hero-desktop.png").read_bytes(), desktop_bytes)
            self.assertEqual((page_dir / "assets" / "hero-mobile.png").read_bytes(), mobile_bytes)
            self.assertEqual(
                manifest["asset_provenance"]["hero-desktop.png"],
                "packaged_demo_asset:synthetic-restaurant-001/hero-desktop.png",
            )
            self.assertEqual(
                manifest["asset_provenance"]["hero-mobile.png"],
                "packaged_demo_asset:synthetic-restaurant-001/hero-mobile.png",
            )

    def test_reuses_packaged_desktop_when_mobile_slot_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            place_id = "synthetic-beauty-002"
            source_dir = root / "packaged" / place_id
            source_dir.mkdir(parents=True)
            desktop_bytes = ONE_PIXEL_PNG + b"desktop-only"
            (source_dir / "hero-desktop.png").write_bytes(desktop_bytes)

            page = PageGenerator(root / "output", demo_assets_dir=root / "packaged").generate(
                score_candidate(candidate_for("guzellik salonu", place_id))
            )
            page_dir = page.path.parent
            manifest = json.loads((page_dir / "page-manifest.json").read_text(encoding="utf-8"))

            self.assertEqual((page_dir / "assets" / "hero-desktop.png").read_bytes(), desktop_bytes)
            self.assertEqual((page_dir / "assets" / "hero-mobile.png").read_bytes(), desktop_bytes)
            self.assertEqual(
                manifest["asset_provenance"]["hero-mobile.png"],
                "reused_packaged_demo_asset:synthetic-beauty-002/hero-desktop.png",
            )

    def test_all_synthetic_categories_use_multiple_mobile_ready_families(self) -> None:
        families: set[str] = set()
        compositions: set[str] = set()

        for index, category in enumerate(SYNTHETIC_CATEGORIES, start=1):
            with self.subTest(category=category):
                layout = layout_for_category(category)
                html_text = render_demo_html(
                    score_candidate(candidate_for(category, f"synthetic-category-{index:02d}"))
                )
                families.add(layout.family)
                compositions.add(layout.composition)
                self.assertIn(f'data-layout-family="{layout.family}"', html_text)
                self.assertIn(f'data-layout-composition="{layout.composition}"', html_text)
                self.assertIn('<nav class="desktop-nav"', html_text)
                self.assertIn('<details class="mobile-menu">', html_text)
                self.assertIn("@media (max-width: 720px)", html_text)
                self.assertIn("hero-mobile.png", html_text)
                self.assertIn("hero-desktop.png", html_text)
                self.assertIn('class="final-cta"', html_text)

        self.assertGreaterEqual(len(families), 5)
        self.assertGreaterEqual(len(compositions), 5)

    def test_restaurant_uses_premium_split_conversion_structure(self) -> None:
        html_text = render_demo_html(
            score_candidate(candidate_for("restoran", "synthetic-restaurant-001"))
        )

        self.assertIn('data-layout-family="dining"', html_text)
        self.assertIn('class="hero hero--split"', html_text)
        self.assertIn('class="trust-strip"', html_text)
        self.assertIn('class="sector sector-menu"', html_text)
        self.assertIn('class="sector sector-story"', html_text)
        self.assertIn('id="contact"', html_text)

    def test_dynamic_candidate_fields_are_escaped(self) -> None:
        candidate = BusinessCandidate(
            place_id="escape-test",
            name='<script>alert("x")</script>',
            category="restoran",
            city="İstanbul",
            district='Kadıköy\"><img src=x onerror=alert(1)>',
            phone="+90 (216) 555 01 01",
            source="mock",
        )
        html_text = render_demo_html(score_candidate(candidate))

        self.assertNotIn('<script>alert("x")</script>', html_text)
        self.assertNotIn('<img src=x onerror=alert(1)>', html_text)
        self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", html_text)
        self.assertIn('href="tel:+902165550101"', html_text)

    def test_synthetic_fixture_contact_actions_are_inert(self) -> None:
        html_text = render_demo_html(
            score_candidate(
                candidate_for(
                    "restoran",
                    "synthetic-restaurant-001",
                    source="synthetic_fixture",
                )
            )
        )

        self.assertNotIn("tel:", html_text)
        self.assertNotIn("wa.me", html_text)
        self.assertGreaterEqual(html_text.count('href="#contact"'), 3)


if __name__ == "__main__":
    unittest.main()

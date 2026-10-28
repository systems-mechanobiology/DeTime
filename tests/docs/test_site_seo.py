# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("check_site_seo", ROOT / "scripts/check_site_seo.py")
assert SPEC is not None and SPEC.loader is not None
SEO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SEO)


class SiteSeoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.site = Path(self.temp_dir.name)
        self.write_page("index.html", SEO.SITE_URL, "DeTime", "DeTime decomposition toolkit")
        self.write_page("quickstart/index.html", SEO.SITE_URL + "quickstart/", "Quickstart", "Run DeTime")
        (self.site / "404.html").write_text(
            '<head><meta name="robots" content="noindex, follow"></head>', encoding="utf-8"
        )
        (self.site / "google123abc.html").write_text(
            "google-site-verification: google123abc.html", encoding="utf-8"
        )
        self.write_sitemap([SEO.SITE_URL, SEO.SITE_URL + "quickstart/"])

    def write_page(self, relative: str, canonical: str, title: str, description: str) -> None:
        path = self.site / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f'<html><head><title>{title}</title><link rel="canonical" href="{canonical}">'
            f'<meta name="description" content="{description}"></head>'
            "<body><h1>Documentation</h1></body></html>", encoding="utf-8"
        )

    def write_sitemap(self, urls: list[str]) -> None:
        (self.site / "sitemap.xml").write_text(
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(f"<url><loc>{url}</loc></url>" for url in urls) + "</urlset>",
            encoding="utf-8",
        )

    def test_valid_site_excludes_verification_and_404(self) -> None:
        self.assertEqual(SEO.check_site(self.site), (2, []))

    def test_rejects_duplicate_overview_metadata(self) -> None:
        self.write_page("quickstart/index.html", SEO.SITE_URL + "quickstart/", "DeTime", "DeTime decomposition toolkit")
        _, errors = SEO.check_site(self.site)
        self.assertTrue(any("duplicate title" in item for item in errors))
        self.assertTrue(any("duplicate description" in item for item in errors))

    def test_rejects_personal_intro_canonical(self) -> None:
        self.write_page("index.html", "https://zipengwu.me/detime/", "DeTime", "DeTime decomposition toolkit")
        self.assertTrue(any("canonical must be exactly" in item for item in SEO.check_site(self.site)[1]))

    def test_rejects_missing_and_extra_sitemap_urls(self) -> None:
        self.write_sitemap([SEO.SITE_URL, SEO.SITE_URL + "404.html"])
        errors = SEO.check_site(self.site)[1]
        self.assertTrue(any("missing canonical pages" in item for item in errors))
        self.assertTrue(any("noncanonical or noncontent URLs" in item for item in errors))

    def test_rejects_indexable_error_page(self) -> None:
        (self.site / "404.html").write_text("<head></head>", encoding="utf-8")
        self.assertIn("404.html: missing noindex", SEO.check_site(self.site)[1])

    def test_rejects_accidental_noindex_on_documentation(self) -> None:
        path = self.site / "quickstart/index.html"
        path.write_text(path.read_text().replace("</head>", '<meta name="robots" content="none, follow"></head>'))
        self.assertTrue(any("noindex directive" in item for item in SEO.check_site(self.site)[1]))

    def test_rejects_missing_description(self) -> None:
        path = self.site / "quickstart/index.html"
        path.write_text(path.read_text().replace('<meta name="description" content="Run DeTime">', ""))
        self.assertTrue(any("nonempty description" in item for item in SEO.check_site(self.site)[1]))

    def test_missing_build_is_an_error(self) -> None:
        count, errors = SEO.check_site(self.site / "missing")
        self.assertEqual(count, 0)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()

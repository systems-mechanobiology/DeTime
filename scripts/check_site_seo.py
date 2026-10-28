# SPDX-License-Identifier: BSD-3-Clause
"""Check generated documentation metadata, not search rankings or index status."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree


SITE_URL = "https://systems-mechanobiology.github.io/DeTime/"


class PageMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_head = False
        self.in_title = False
        self.titles: list[str] = []
        self.descriptions: list[str] = []
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "head":
            self.in_head = True
        if tag == "h1":
            self.h1_count += 1
        if not self.in_head:
            return
        if tag == "title":
            self.in_title = True
            self.titles.append("")
        if tag == "link" and values.get("rel") == "canonical":
            self.canonicals.append(values.get("href") or "")
        if tag == "meta" and values.get("name") == "description":
            self.descriptions.append(values.get("content") or "")
        if tag == "meta" and values.get("name") == "robots":
            self.robots.append(values.get("content") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "head":
            self.in_head = False

    def handle_data(self, data: str) -> None:
        if self.in_head and self.in_title:
            self.titles[-1] += data


def check_site(site_dir: Path, site_url: str = SITE_URL) -> tuple[int, list[str]]:
    errors: list[str] = []
    titles: dict[str, list[str]] = defaultdict(list)
    descriptions: dict[str, list[str]] = defaultdict(list)
    expected_urls: set[str] = set()
    count = 0
    if not (site_dir / "index.html").is_file():
        return 0, [f"{site_dir}: missing index.html; run mkdocs build first"]

    for path in sorted(site_dir.rglob("*.html")):
        relative = path.relative_to(site_dir).as_posix()
        text = path.read_text(encoding="utf-8")
        # Preserve Search Console's exact verification response outside the sitemap.
        if re.fullmatch(r"google[0-9a-f]+\.html", relative) and text.strip() == (
            f"google-site-verification: {relative}"
        ):
            continue
        page = PageMetadata()
        page.feed(text)
        robots = {token.strip().lower() for value in page.robots for token in value.split(",")}
        if relative == "404.html":
            if "noindex" not in robots:
                errors.append("404.html: missing noindex")
            continue

        count += 1
        url_path = relative.removesuffix("index.html") if path.name == "index.html" else relative
        expected_url = urljoin(site_url, url_path)
        expected_urls.add(expected_url)
        if page.canonicals != [expected_url]:
            errors.append(f"{relative}: canonical must be exactly {expected_url}")
        if "noindex" in robots or "none" in robots:
            errors.append(f"{relative}: indexable documentation has a noindex directive")
        if page.h1_count != 1:
            errors.append(f"{relative}: expected one H1, got {page.h1_count}")
        for values, label, seen in (
            (page.titles, "title", titles),
            (page.descriptions, "description", descriptions),
        ):
            if len(values) != 1 or not values[0].strip():
                errors.append(f"{relative}: expected one nonempty {label}")
            else:
                seen[values[0].strip()].append(relative)

    for label, values in (("title", titles), ("description", descriptions)):
        for value, pages in values.items():
            if len(pages) > 1:
                errors.append(f"duplicate {label} {json.dumps(value)}: {', '.join(pages)}")

    try:
        sitemap = ElementTree.parse(site_dir / "sitemap.xml")
        urls = [(node.text or "").strip() for node in sitemap.findall(".//{*}loc")]
        if len(urls) != len(set(urls)):
            errors.append("sitemap.xml: duplicate URLs")
        missing = sorted(expected_urls - set(urls))
        extra = sorted(set(urls) - expected_urls)
        if missing:
            errors.append(f"sitemap.xml: missing canonical pages: {missing}")
        if extra:
            errors.append(f"sitemap.xml: noncanonical or noncontent URLs: {extra}")
    except (OSError, ElementTree.ParseError) as exc:
        errors.append(f"sitemap.xml: {exc}")
    return count, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, default=Path("site"))
    args = parser.parse_args()
    count, errors = check_site(args.site_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"SEO build checks passed for {count} documentation pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

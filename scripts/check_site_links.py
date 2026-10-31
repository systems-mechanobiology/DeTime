# SPDX-License-Identifier: BSD-3-Clause
"""Validate local files and HTML fragments in the built MkDocs site."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


SITE_URL = "https://systems-mechanobiology.github.io/DeTime/"


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: set[str] = set()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("id", "name" if tag == "a" else "id"):
            if values.get(key):
                self.targets.add(values[key])
        attribute = "href" if tag in {"a", "link"} else "src"
        if tag in {"a", "link", "img", "script", "iframe", "source"} and values.get(attribute):
            self.references.append(values[attribute])


def check_site_links(site_dir: Path, site_url: str = SITE_URL) -> tuple[int, list[str]]:
    root = site_dir.resolve()
    if not (root / "index.html").is_file():
        return 0, [f"{site_dir}: missing index.html; run mkdocs build first"]
    base = urlsplit(site_url)
    prefix = base.path.rstrip("/") + "/"
    pages: dict[Path, Links] = {}
    for path in root.rglob("*.html"):
        parsed = Links()
        parsed.feed(path.read_text(encoding="utf-8"))
        pages[path] = parsed

    checked = 0
    errors: list[str] = []
    for path, parsed in sorted(pages.items()):
        relative = path.relative_to(root).as_posix()
        page_url = urljoin(site_url, relative)
        for reference in sorted(set(parsed.references)):
            resolved = urlsplit(urljoin(page_url, reference))
            if resolved.scheme not in {"http", "https"} or resolved.netloc != base.netloc:
                continue
            if not resolved.path.startswith(prefix):
                continue
            target = (root / unquote(resolved.path[len(prefix):])).resolve()
            if not target.is_relative_to(root):
                errors.append(f"{relative}: link escapes site: {reference}")
                continue
            if target.is_dir() or resolved.path.endswith("/"):
                target = target / "index.html"
            checked += 1
            if not target.is_file():
                errors.append(f"{relative}: missing local target: {reference}")
            elif resolved.fragment and target.suffix == ".html":
                fragment = unquote(resolved.fragment)
                if not fragment.startswith(":~:text=") and fragment not in pages[target].targets:
                    errors.append(f"{relative}: missing HTML fragment: {reference}")
    return checked, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, default=Path("site"))
    args = parser.parse_args()
    checked, errors = check_site_links(args.site_dir)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"{len(errors)} errors in {checked} local links and assets.")
        return 1
    print(f"Local links, assets and HTML fragments passed: {checked} references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

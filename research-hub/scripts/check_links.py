#!/usr/bin/env python3
"""Check a static site directory for broken internal links and missing local assets.

Usage: python3 scripts/check_links.py <site_dir>

Scans every .html file, extracts local href/src references (relative links,
anchor links, and local css/js/image assets), and verifies each resolves to an
existing file. External http(s)/mailto/tel links are skipped. Exits non-zero if
any internal link is broken or any referenced local asset is missing.
"""
import os
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, unquote


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag not in ("a", "link", "script", "img", "source", "video", "audio"):
            return
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append((tag, value))


def is_external(url):
    return urlparse(url).scheme in ("http", "https", "mailto", "tel", "data", "javascript")


def resolve(base_file, url):
    # strip fragment
    url = url.split("#", 1)[0]
    if not url:
        return None
    joined = urljoin("file://" + os.path.abspath(base_file), url)
    parsed = urlparse(joined)
    if parsed.scheme == "file":
        return unquote(parsed.path)
    return None


def main():
    if len(sys.argv) < 2:
        print("usage: check_links.py <site_dir>")
        return 2
    site = sys.argv[1]
    if not os.path.isdir(site):
        print("error: not a directory:", site)
        return 2

    problems = []
    checked = 0
    for root, _dirs, files in os.walk(site):
        for fn in sorted(files):
            if not fn.endswith((".html", ".htm")):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as fh:
                html = fh.read()
            parser = LinkCollector()
            parser.feed(html)
            for tag, url in parser.links:
                if is_external(url) or url.startswith("#"):
                    continue
                target = resolve(path, url)
                if target is None:
                    continue
                checked += 1
                if not os.path.exists(target):
                    problems.append((path, url, target))

    if problems:
        print("BROKEN internal links / missing local assets:")
        for src, url, target in problems:
            print(f"  {os.path.relpath(src, site)} -> {url}  (resolved: {target})")
        print(f"\n{len(problems)} broken link(s) found.")
        return 1

    print(f"OK: {checked} internal links/assets checked, none broken.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

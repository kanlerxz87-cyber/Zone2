"""Shared HTML context segmentation. Split BEFORE stripping tags.

Stripping first collapses a page into one unit, allowing a disclosure's 'earn' to
exempt an unrelated product price. Keep program economics in their own row/block.
"""
from __future__ import annotations
import html
import re


def context_units(document: str) -> list[str]:
    chunks=re.split(r'</(?:tr|p|li|div|section|blockquote|h[1-6])\s*>|<br\s*/?>',document,flags=re.I)
    return [html.unescape(re.sub(r'<[^>]+>',' ',chunk)) for chunk in chunks]

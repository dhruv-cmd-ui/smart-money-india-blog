"""Tiny markdown-subset -> HTML converter. Supports '## heading', '**bold**', and paragraphs.
Deliberately minimal (no dependency) since the content is LLM/template-generated in a known shape.
"""
import html
import re


def to_html(text: str) -> str:
    blocks = [b.strip() for b in text.strip().split("\n\n") if b.strip()]
    out = []
    for block in blocks:
        if block.startswith("## "):
            out.append(f"<h2>{_inline(block[3:].strip())}</h2>")
        elif block.startswith("# "):
            out.append(f"<h2>{_inline(block[2:].strip())}</h2>")
        else:
            paragraph = block.replace("\n", " ")
            out.append(f"<p>{_inline(paragraph)}</p>")
    return "\n".join(out)


def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="sponsored nofollow">\1</a>', escaped)
    # Autolink bare URLs (not already inside an href or tag).
    return re.sub(r'(?<![">(])(https?://[^\s<)]+)', r'<a href="\1" rel="sponsored nofollow">\1</a>', escaped)

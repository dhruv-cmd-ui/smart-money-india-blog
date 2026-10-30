"""Tiny markdown-subset -> HTML converter. Supports headings, **bold**, [links](url), bullet/numbered lists
and paragraphs. Also flattens stray LaTeX that LLMs sometimes emit. Deliberately dependency-free since the
content is LLM-generated in a known shape.
"""
import html
import re

_LIST_ITEM = re.compile(r"^\s*(?:([*\-\u2022])|(\d+[.)]))\s+(?!\*)")
_HEADING = re.compile(r"^\s*#{1,4}\s+(.*)$")


def _tex(expr: str) -> str:
    """Best-effort conversion of simple LaTeX math to readable plain text."""
    expr = re.sub(r"\\(?:text|mathbf|mathrm|textbf)\{([^{}]*)\}", r"\1", expr)
    for _ in range(3):
        expr = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", expr)
    for tex, plain in ((r"\left", ""), (r"\right", ""), (r"\times", "\u00d7"), (r"\approx", "\u2248"),
                       (r"\cdot", "\u00b7"), (r"\div", "\u00f7"), (r"\%", "%"), (r"\\", " "), (r"\,", " "), (r"\ ", " ")):
        expr = expr.replace(tex, plain)
    return re.sub(r"\s+", " ", expr.replace("{", "").replace("}", "")).strip()


def _clean_math(text: str) -> str:
    text = re.sub(r"\$\$(.+?)\$\$", lambda m: "\n\n" + _tex(m.group(1)) + "\n\n", text, flags=re.S)
    return re.sub(r"\$([^$\n]*\\[^$\n]*)\$", lambda m: _tex(m.group(1)), text)


def to_html(text: str) -> str:
    text = _clean_math(text)
    out = []
    for block in (b.strip() for b in text.strip().split("\n\n")):
        if not block:
            continue
        para, items, ordered = [], [], False

        def flush():
            nonlocal para, items, ordered
            if para:
                out.append(f"<p>{_inline(' '.join(para))}</p>")
            if items:
                tag = "ol" if ordered else "ul"
                out.append(f"<{tag}>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + f"</{tag}>")
            para, items = [], []

        for line in block.split("\n"):
            heading = _HEADING.match(line)
            item = _LIST_ITEM.match(line)
            if heading:
                flush()
                out.append(f"<h2>{_inline(heading.group(1).strip())}</h2>")
            elif item:
                if para:
                    flush()
                ordered = item.group(2) is not None
                items.append(line[item.end():].strip())
            elif line.strip():
                if items:
                    flush()
                para.append(line.strip())
        flush()
    return "\n".join(out)


def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?<![*\w])\*([^*\s][^*\n]*?)\*(?![*\w])", r"<i>\1</i>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="sponsored nofollow">\1</a>', escaped)
    # Autolink bare URLs (not already inside an href or tag).
    return re.sub(r'(?<![">(])(https?://[^\s<)]*[^\s<).,;:!?])', r'<a href="\1" rel="sponsored nofollow">\1</a>', escaped)

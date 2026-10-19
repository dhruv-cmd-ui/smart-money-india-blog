"""Writes/updates the static site in ../site/docs: article page, index, sitemap, RSS feed."""
import json
from datetime import datetime, timezone
from pathlib import Path

from mini_markdown import to_html

SITE_DIR = Path(__file__).resolve().parent.parent / "docs"
ARTICLES_DIR = SITE_DIR / "articles"
SITE_BASE_URL = "https://dhruv-cmd-ui.github.io/smart-money-india-blog"
SITE_NAME = "Smart Money India"
DISCLAIMER = (
    "Educational content only — not investment advice. Not a SEBI-registered advisor. "
    "Please consult a certified financial advisor before investing. This page may contain "
    "affiliate links; we may earn a commission at no extra cost to you."
)

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | {site_name}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; line-height: 1.65; color: #1a1a1a; }}
  h1 {{ font-size: 1.8rem; }}
  h2 {{ font-size: 1.3rem; margin-top: 2em; }}
  nav a {{ margin-right: 16px; }}
  footer {{ margin-top: 3em; padding-top: 1em; border-top: 1px solid #ddd; font-size: 0.85rem; color: #666; }}
  .disclaimer {{ font-size: 0.8rem; color: #888; margin-top: 2em; }}
</style>
</head>
<body>
<nav><a href="../index.html">{site_name}</a></nav>
<h1>{title}</h1>
<p><em>Published {date}</em></p>
{body_html}
<p class="disclaimer">{disclaimer}</p>
<footer>&copy; {year} {site_name}</footer>
</body>
</html>
"""

INDEX_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{site_name} — Personal Finance for India</title>
<meta name="description" content="Practical, India-specific personal finance and investing guides.">
<link rel="alternate" type="application/rss+xml" title="{site_name}" href="rss.xml">
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; line-height: 1.65; }}
  li {{ margin-bottom: 10px; }}
</style>
</head>
<body>
<h1>{site_name}</h1>
<p>Practical, India-specific personal finance and investing guides.</p>
<ul>
{article_list}
</ul>
</body>
</html>
"""


def _article_url(slug: str) -> str:
    return f"{SITE_BASE_URL}/articles/{slug}.html"


def write_article(slug: str, title: str, description: str, body_markdown: str) -> Path:
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    html_page = PAGE_TEMPLATE.format(
        title=title,
        description=description,
        url=_article_url(slug),
        site_name=SITE_NAME,
        date=now.strftime("%Y-%m-%d"),
        body_html=to_html(body_markdown),
        disclaimer=DISCLAIMER,
        year=now.year,
    )
    out_path = ARTICLES_DIR / f"{slug}.html"
    out_path.write_text(html_page, encoding="utf-8")
    return out_path


def _load_manifest() -> list:
    manifest_path = SITE_DIR / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return []


def _save_manifest(entries: list) -> None:
    (SITE_DIR / "manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")


def update_index_sitemap_rss(slug: str, title: str, description: str) -> None:
    entries = _load_manifest()
    entries = [e for e in entries if e["slug"] != slug]
    entries.insert(0, {
        "slug": slug,
        "title": title,
        "description": description,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "url": _article_url(slug),
    })
    _save_manifest(entries)

    article_list = "\n".join(
        f'<li><a href="articles/{e["slug"]}.html">{e["title"]}</a> — {e["date"]}</li>'
        for e in entries
    )
    (SITE_DIR / "index.html").write_text(
        INDEX_TEMPLATE.format(site_name=SITE_NAME, article_list=article_list),
        encoding="utf-8",
    )

    urls = "\n".join(
        f"  <url><loc>{e['url']}</loc><lastmod>{e['date']}</lastmod></url>" for e in entries
    )
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    (SITE_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    items = "\n".join(
        f"    <item><title>{e['title']}</title><link>{e['url']}</link>"
        f"<description>{e['description']}</description>"
        f"<pubDate>{e['date']}</pubDate><guid>{e['url']}</guid></item>"
        for e in entries
    )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
        f"    <title>{SITE_NAME}</title>\n    <link>{SITE_BASE_URL}/index.html</link>\n"
        f"    <description>India personal finance guides</description>\n{items}\n"
        "  </channel></rss>\n"
    )
    (SITE_DIR / "rss.xml").write_text(rss, encoding="utf-8")

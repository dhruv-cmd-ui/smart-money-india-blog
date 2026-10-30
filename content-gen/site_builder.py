"""Writes/updates the static site in ../docs: article pages, home page, books page, sitemap, RSS feed.

All pages share docs/assets/style.css. Article bodies are kept between <!--BODY--> markers so every
page can be re-rendered from the manifest whenever the design or the "more guides" lists change.
"""
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from mini_markdown import to_html

SITE_DIR = Path(__file__).resolve().parent.parent / "docs"
ARTICLES_DIR = SITE_DIR / "articles"
LINKS_PATH = Path(__file__).resolve().parent.parent / "config" / "affiliate_links.json"
SITE_BASE_URL = "https://dhruv-cmd-ui.github.io/smart-money-india-blog"
SITE_NAME = "Smart Money India"
TOOLKIT_URL = "https://payhip.com/b/IbWAZ"
DISCLAIMER = (
    "Educational content only — not investment advice. Not a SEBI-registered advisor. "
    "Please consult a certified financial advisor before investing. This page may contain "
    "affiliate links; as an Amazon Associate I earn from qualifying purchases."
)

# Static pages (not in manifest.json) that should still appear in the sitemap and RSS feed.
EXTRA_PAGES = [
    {
        "title": "Recommended Personal Finance Books for Indian Readers",
        "description": "Hand-picked personal finance and investing books worth reading before you invest.",
        "date": "2026-10-30",
        "url": f"{SITE_BASE_URL}/books.html",
    },
]

# (affiliate_links.json key, title, author, blurb, emoji)
BOOKS = [
    ("amazon_psychology_of_money", "The Psychology of Money", "Morgan Housel",
     "Why behaviour matters more than knowledge when it comes to money. The best first finance book for most people.", "🧠"),
    ("amazon_rich_dad", "Rich Dad Poor Dad", "Robert Kiyosaki",
     "Assets vs liabilities, simply explained. Take the mindset, be sceptical of the specific advice.", "🏠"),
    ("amazon_millionaire_next_door", "The Millionaire Next Door (Hindi edition)", "Thomas J. Stanley & William D. Danko",
     "How real millionaires live below their means. Available in Hindi.", "💼"),
    ("amazon_trading_in_the_zone", "Trading in the Zone", "Mark Douglas",
     "The psychology of discipline and risk for anyone who trades actively.", "🎯"),
]

# slug -> emoji shown on the article's card/banner.
EMOJI = {
    "emergency-fund-india": "🐷", "sip-vs-lumpsum": "📈", "best-tax-saving-investments-80c": "🧾",
    "credit-score-improve-india": "📊", "index-funds-beginners-india": "🌱", "health-insurance-sum-insured": "❤️",
    "retirement-planning-30s-india": "🏖️", "home-loan-prepayment-strategy": "🏡", "mutual-fund-direct-vs-regular": "🧮",
    "first-salary-financial-plan": "💼", "nps-vs-mutual-funds-retirement": "🏦", "gold-investment-options-india": "🪙",
    "term-insurance-how-much-cover": "☂️", "debt-funds-explained-india": "🛡️", "budgeting-methods-compared": "📒",
}

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%%</title>
<meta name="description" content="%%DESC%%">
<link rel="canonical" href="%%URL%%">
<meta property="og:type" content="%%OGTYPE%%">
<meta property="og:title" content="%%OGTITLE%%">
<meta property="og:description" content="%%DESC%%">
<meta property="og:url" content="%%URL%%">
<meta property="og:image" content="%%OGIMAGE%%">
<meta name="twitter:card" content="summary_large_image">
%%EXTRAHEAD%%<link rel="alternate" type="application/rss+xml" title="Smart Money India" href="%%ROOT%%rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="%%ROOT%%assets/style.css">
</head>
<body>
<header class="site-header"><div class="wrap">
  <a class="brand" href="%%ROOT%%index.html"><span class="brand-mark">₹</span>Smart Money India</a>
  <nav class="nav">
    <a href="%%ROOT%%index.html#guides">Guides</a>
    <a href="%%ROOT%%books.html">Books</a>
    <a class="cta" href="%%TOOLKIT%%" rel="noopener">Get the Toolkit</a>
  </nav>
</div></header>
"""

FOOTER = """<footer class="site-footer"><div class="wrap">
  <div class="cols">
    <div><h4>Smart Money India</h4><div style="max-width:340px">Plain-language personal finance guides for Indian readers. A new guide every day.</div></div>
    <div><h4>Explore</h4><a href="%%ROOT%%index.html#guides">All guides</a><a href="%%ROOT%%books.html">Recommended books</a><a href="%%TOOLKIT%%">Wealth Toolkit (Excel)</a></div>
    <div><h4>Follow</h4><a href="%%ROOT%%rss.xml">RSS feed</a></div>
  </div>
  <small>%%DISCLAIMER%%<br>&copy; %%YEAR%% Smart Money India</small>
</div></footer>
</body>
</html>
"""

TOOLKIT_BAND = """<div class="band">
  <div><h2>The Ultimate Wealth Toolkit</h2>
  <p>Three Excel templates in one bundle: a budget tracker, a SIP calculator and a net-worth tracker. Open in Excel, type your numbers, done.</p></div>
  <a class="btn btn-primary" href="%%TOOLKIT%%" rel="noopener">Get the toolkit</a>
</div>"""


def _fill(template: str, **kw) -> str:
    kw.setdefault("TOOLKIT", TOOLKIT_URL)
    kw.setdefault("YEAR", str(datetime.now(timezone.utc).year))
    kw.setdefault("DISCLAIMER", DISCLAIMER)
    for k, v in kw.items():
        template = template.replace(f"%%{k}%%", v)
    return template


def _article_url(slug: str) -> str:
    return f"{SITE_BASE_URL}/articles/{slug}.html"


def _palette(slug: str) -> int:
    return sum(ord(c) for c in slug) % 6


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _read_minutes(body_html: str) -> int:
    words = len(re.sub(r"<[^>]+>", " ", body_html).split())
    return max(1, round(words / 200))


def _card(entry: dict, root: str) -> str:
    slug = entry["slug"]
    return (
        f'<a class="card" href="{root}articles/{slug}.html">'
        f'<div class="banner g{_palette(slug)}">{EMOJI.get(slug, "💰")}</div>'
        f'<div class="body"><span class="tag">Guide</span><h3>{_esc(entry["title"])}</h3>'
        f'<p>{_esc(entry["description"])}</p><span class="meta">{entry["date"]}</span></div></a>'
    )


def _book_cards(root_unused: str = "") -> str:
    links = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
    out = []
    for i, (key, title, author, blurb, emoji) in enumerate(BOOKS):
        url = links.get(key, "")
        if not url or "ADD_YOUR" in url:
            continue
        out.append(
            f'<a class="book" href="{_esc(url)}" rel="sponsored nofollow noopener" target="_blank">'
            f'<div class="cover g{i % 6}">{emoji}</div><h3>{_esc(title)}</h3><div class="by">{_esc(author)}</div>'
            f"<p>{_esc(blurb)}</p><span class=\"buy\">View on Amazon.in &rarr;</span></a>"
        )
    return "\n".join(out)


def render_article(slug: str, title: str, description: str, date: str, body_html: str, entries: list) -> str:
    related = [e for e in entries if e["slug"] != slug][:3]
    related_html = "".join(_card(e, "../") for e in related)
    page = HEAD + """<section class="article-hero"><div class="wrap">
  <div class="crumbs"><a href="../index.html">Home</a> &rsaquo; <a href="../index.html#guides">Guides</a></div>
  <h1>%%H1%%</h1>
  <div class="meta">%%DATE%% &middot; %%MINS%% min read</div>
</div></section>
<article class="article">
<div class="prose">
<!--BODY-->%%BODY%%<!--/BODY-->
</div>
<div class="cta-box"><div><strong>Want to put this into practice?</strong><span>Get ready-made Excel templates for budgeting, SIPs and net worth.</span></div>
<a class="btn" href="%%TOOLKIT%%" rel="noopener">Get the toolkit</a></div>
<p class="disclaimer">%%DISCLAIMER%%</p>
</article>
<section class="related"><div class="wrap"><h2 class="section-title">More guides</h2><p class="section-sub">Keep going. One good decision at a time.</p>
<div class="grid">%%RELATED%%</div></div></section>
""" + FOOTER
    return _fill(
        page,
        TITLE=_esc(f"{title} | {SITE_NAME}"), DESC=_esc(description), URL=_article_url(slug),
        OGTYPE="article", OGTITLE=_esc(title), OGIMAGE=f"{SITE_BASE_URL}/pins/{slug}.png", EXTRAHEAD="",
        ROOT="../", H1=_esc(title), DATE=date, MINS=str(_read_minutes(body_html)), BODY=body_html, RELATED=related_html,
    )


def _extract_body(page_html: str) -> str:
    m = re.search(r"<!--BODY-->(.*?)<!--/BODY-->", page_html, re.S)
    if m:
        return m.group(1)
    # Legacy (pre-redesign) pages: body sits between the "Published" line and the disclaimer.
    m = re.search(r"<p><em>Published [^<]*</em></p>\n(.*?)<p class=\"disclaimer\">", page_html, re.S)
    return m.group(1).strip() if m else ""


def write_article(slug: str, title: str, description: str, body_markdown: str) -> Path:
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = ARTICLES_DIR / f"{slug}.html"
    out_path.write_text(
        render_article(slug, title, description, date, to_html(body_markdown), _load_manifest()), encoding="utf-8"
    )
    return out_path


def _load_manifest() -> list:
    manifest_path = SITE_DIR / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return []


def _save_manifest(entries: list) -> None:
    (SITE_DIR / "manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")


def render_index(entries: list) -> str:
    featured = entries[0] if entries else None
    feat_html = ""
    if featured:
        s = featured["slug"]
        feat_html = (
            f'<div class="wrap"><a class="featured" href="articles/{s}.html">'
            f'<div class="banner g{_palette(s)}">{EMOJI.get(s, "💰")}</div>'
            f'<div class="body"><span class="tag">Latest guide</span><h2>{_esc(featured["title"])}</h2>'
            f'<p>{_esc(featured["description"])}</p><span class="more">Read the guide &rarr;</span></div></a></div>'
        )
    page = HEAD + """<section class="hero"><div class="wrap">
  <span class="eyebrow">FREE &bull; INDIA-FOCUSED &bull; NO JARGON</span>
  <h1>Smart money decisions, <span>made simple.</span></h1>
  <p class="lead">Clear, practical guides on investing, insurance, tax and budgeting, written for Indian readers. A new guide every day.</p>
  <a class="btn btn-primary" href="#guides">Browse the guides</a><a class="btn btn-ghost" href="books.html">Recommended books</a>
  <div class="chips"><span class="chip">New guide daily</span><span class="chip">Rupee examples</span><span class="chip">Educational, not advice</span></div>
</div></section>
%%FEATURED%%
<section id="guides"><div class="wrap"><h2 class="section-title">All guides</h2><p class="section-sub">Start anywhere. Each guide takes about five minutes.</p>
<div class="grid">%%CARDS%%</div></div></section>
<section style="padding-top:0"><div class="wrap"><h2 class="section-title">Books worth reading</h2><p class="section-sub">Our short list for building good money habits.</p>
<div class="books">%%BOOKS%%</div></div></section>
<section style="padding-top:0"><div class="wrap">""" + TOOLKIT_BAND + """</div></section>
""" + FOOTER
    return _fill(
        page,
        TITLE=_esc(f"{SITE_NAME}: Personal Finance Guides for India"),
        DESC="Practical, India-specific personal finance and investing guides. A new guide every day.",
        URL=f"{SITE_BASE_URL}/", OGTYPE="website", OGTITLE=_esc(SITE_NAME),
        OGIMAGE=f"{SITE_BASE_URL}/pin-image.png",
        EXTRAHEAD='<meta name="p:domain_verify" content="dbfb7ad96e16ce00515dd5459bea91ec"/>\n',
        ROOT="", FEATURED=feat_html, CARDS="".join(_card(e, "") for e in entries[1:] or entries), BOOKS=_book_cards(),
    )


def render_books_page() -> str:
    page = HEAD + """<section class="article-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Home</a> &rsaquo; Books</div>
  <h1>Recommended personal finance books</h1>
  <div class="meta">Worth reading before you invest your first rupee</div>
</div></section>
<section class="books-page"><div class="wrap"><div class="books">%%BOOKS%%</div>
<p class="disclaimer">As an Amazon Associate I earn from qualifying purchases. Educational content only; not investment advice. Not a SEBI-registered advisor.</p>
</div></section>
""" + FOOTER
    return _fill(
        page,
        TITLE=_esc(f"Recommended Personal Finance Books | {SITE_NAME}"),
        DESC="Hand-picked personal finance and investing books for Indian readers.",
        URL=f"{SITE_BASE_URL}/books.html", OGTYPE="website", OGTITLE="Recommended Personal Finance Books",
        OGIMAGE=f"{SITE_BASE_URL}/pin-image.png", EXTRAHEAD="", ROOT="", BOOKS=_book_cards(),
    )


def rebuild_all(entries: list) -> None:
    """Re-render every page from the manifest so design changes and 'more guides' lists stay current."""
    for e in entries:
        path = ARTICLES_DIR / f"{e['slug']}.html"
        if not path.exists():
            continue
        body = _extract_body(path.read_text(encoding="utf-8"))
        if body:
            path.write_text(render_article(e["slug"], e["title"], e["description"], e["date"], body, entries), encoding="utf-8")
    (SITE_DIR / "index.html").write_text(render_index(entries), encoding="utf-8")
    (SITE_DIR / "books.html").write_text(render_books_page(), encoding="utf-8")


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
    rebuild_all(entries)

    feed_entries = entries + EXTRA_PAGES
    urls = "\n".join(
        f"  <url><loc>{e['url']}</loc><lastmod>{e['date']}</lastmod></url>" for e in feed_entries
    )
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    (SITE_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    items = "\n".join(
        f"    <item><title>{e['title']}</title><link>{e['url']}</link>"
        f"<description>{e['description']}</description>"
        f"<pubDate>{e['date']}</pubDate><guid>{e['url']}</guid></item>"
        for e in feed_entries
    )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
        f"    <title>{SITE_NAME}</title>\n    <link>{SITE_BASE_URL}/index.html</link>\n"
        f"    <description>India personal finance guides</description>\n{items}\n"
        "  </channel></rss>\n"
    )
    (SITE_DIR / "rss.xml").write_text(rss, encoding="utf-8")

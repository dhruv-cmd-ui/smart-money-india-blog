"""Picks the next topic, drafts an article (Gemini free tier if GEMINI_API_KEY is set,
otherwise a template-based fallback so the whole pipeline is testable for free with no key),
and publishes it into ../site/docs via site_builder.
"""
import argparse
import json
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

from generate_pin_image import make_pin  # noqa: E402
from site_builder import update_index_sitemap_rss, write_article  # noqa: E402

TOPICS_PATH = Path(__file__).resolve().parent / "topics.json"
STATE_PATH = Path(__file__).resolve().parent / "state.json"
LINKS_PATH = Path(__file__).resolve().parent.parent / "config" / "affiliate_links.json"

# Topic slug -> (link_key in affiliate_links.json, book title, one-line reason). Topics not listed
# (insurance, tax, credit score, loans) fall back to the general books page CTA only.
BOOK_FOR_TOPIC = {
    slug: ("amazon_psychology_of_money", "The Psychology of Money", "why investor behaviour matters more than the product you pick")
    for slug in (
        "sip-vs-lumpsum", "index-funds-beginners-india", "mutual-fund-direct-vs-regular",
        "retirement-planning-30s-india", "nps-vs-mutual-funds-retirement",
        "gold-investment-options-india", "debt-funds-explained-india",
    )
}
BOOK_FOR_TOPIC.update({
    slug: ("amazon_millionaire_next_door", "The Millionaire Next Door (Hindi edition)", "how everyday savers actually build wealth by spending less than they earn")
    for slug in ("emergency-fund-india", "first-salary-financial-plan", "budgeting-methods-compared")
})

PROMPT_TEMPLATE = """Write a {word_count}-word educational personal-finance article for an Indian retail\
 investor audience, on the topic: "{title}".

Angle to cover: {angle}

Rules:
- Plain, practical, India-specific (rupees, SEBI/Indian context where relevant).
- No stock-specific buy/sell/target recommendations — stay educational, not advisory.
- Structure: a short intro paragraph, 3-4 "## Subheading" sections, a short conclusion paragraph.
- Use **bold** sparingly for key terms only.
- Do not include a title heading (the page already shows the title) — start directly with the intro paragraph.
- Do not include a disclaimer (the page already appends one).
"""


def load_affiliate_link(link_key: str) -> str | None:
    links = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
    url = links.get(link_key, "")
    if not url or "ADD_YOUR" in url:
        return None
    return url


def pick_topic() -> dict:
    topics = json.loads(TOPICS_PATH.read_text(encoding="utf-8"))
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}

    order = state.get("order")
    cursor = state.get("cursor", 0)
    if not order or len(order) != len(topics) or cursor >= len(order):
        order = list(range(len(topics)))
        random.shuffle(order)
        cursor = 0

    topic = topics[order[cursor]]
    state["order"] = order
    state["cursor"] = cursor + 1
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return topic


def draft_with_gemini(topic: dict, api_key: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = PROMPT_TEMPLATE.format(word_count=600, title=topic["title"], angle=topic["angle"])
    response = model.generate_content(prompt)
    return response.text.strip()


def draft_fallback(topic: dict) -> str:
    """Free, offline, template-based draft used when no GEMINI_API_KEY is configured.
    Keeps the pipeline fully runnable at zero cost even without an API key."""
    return (
        f"{topic['angle']}\n\n"
        f"## Why This Matters\n\n"
        f"For most Indian households, decisions like this compound over years, not days — "
        f"getting the basics right early matters more than optimizing every last detail.\n\n"
        f"## The Practical Approach\n\n"
        f"Start with the simplest version of the plan that you'll actually stick to, then refine "
        f"it once it becomes a habit. Complexity that you abandon after a month is worse than a "
        f"simple plan you follow for years.\n\n"
        f"## Common Mistakes to Avoid\n\n"
        f"The most frequent mistake isn't picking the 'wrong' option — it's delaying the decision "
        f"entirely while waiting for a perfect answer that doesn't exist.\n\n"
        f"## Bottom Line\n\n"
        f"Revisit this decision periodically as your income and goals change, rather than setting "
        f"it once and never checking back in."
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Write files but don't rely on live Gemini quota state persisting is still fine to commit")
    args = parser.parse_args()

    topic = pick_topic()
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key:
        body = draft_with_gemini(topic, api_key)
        source = "gemini"
    else:
        body = draft_fallback(topic)
        source = "fallback-template"

    book = BOOK_FOR_TOPIC.get(topic["slug"])
    book_url = load_affiliate_link(book[0]) if book else None
    if book_url:
        body += f"\n\n**Further reading:** [{book[1]}]({book_url}) explains {book[2]}. (affiliate link — we may earn a commission)"

    cta_link = load_affiliate_link("amazon_books")
    if cta_link:
        body += f"\n\nIf you want to go deeper on this topic, here are some recommended reads: {cta_link} (affiliate link — we may earn a commission)."

    description = topic["angle"][:150]
    out_path = write_article(topic["slug"], topic["title"], description, body)
    update_index_sitemap_rss(topic["slug"], topic["title"], description)
    pin_path = make_pin(topic["slug"], topic["title"], description)

    print(f"Generated article via {source}: {topic['title']}")
    print(f"Written to: {out_path}")
    print(f"Pinterest image: {pin_path}")
    if args.dry_run:
        print("Dry run flag set — note files were still written locally; nothing is pushed until you commit/push.")


if __name__ == "__main__":
    main()

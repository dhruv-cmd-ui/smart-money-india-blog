# Stream 3 — Automated SEO Blog (GitHub Pages, free)

Publishes one new India-personal-finance article per day, fully automated via GitHub Actions, hosted free on GitHub Pages. Articles are drafted with the Google Gemini free-tier API when a key is configured — and with a built-in offline template fallback when it isn't, so the whole pipeline runs and is testable at **zero cost even before you get an API key**.

## How it works

- `.github/workflows/publish.yml` runs daily, executes `content-gen/generate_article.py`, and commits the new page.
- `content-gen/topics.json` is the rotating topic list (15 to start — add more anytime, same shape).
- `content-gen/generate_article.py` picks the next topic (shuffled, no-repeat, same rotation pattern as Stream 1), drafts it via Gemini (or the offline fallback), converts it to HTML, and writes it into `site/docs/articles/<slug>.html`, updating `site/docs/index.html`, `sitemap.xml`, and `rss.xml`.
- `rss.xml` is important: **Stream 5** (Make.com distribution) reads this feed to auto-cross-post new articles to Pinterest/Telegram, so don't rename or move it.
- `config/affiliate_links.json` works exactly like Stream 1's — fill in real links once approved, and the generator appends a CTA line automatically; until then, articles publish without it.

## Setup — steps only you can do

### 1. Get a free Gemini API key (optional but recommended for real article quality)
1. Go to **aistudio.google.com** → sign in with a Google account → **Get API key** → **Create API key**.
2. This is free with a daily quota generous enough for 1 article/day.
3. Without this key, the bot still runs daily and publishes articles — just using the simpler offline template instead of an AI-drafted one.

### 2. Create a new GitHub repo and push this folder
```
git remote add origin https://github.com/<your-username>/<new-repo>.git
git branch -M main
git push -u origin main
```
Add repo secret (optional): **Settings → Secrets and variables → Actions → New repository secret** → `GEMINI_API_KEY`.

### 3. Turn on GitHub Pages
**Settings → Pages → Source: Deploy from a branch → Branch: `main`, folder: `/docs`** → Save. The site files already live at repo-root `/docs`, so no extra steps — GitHub Pages redeploys automatically every time the daily workflow commits a new article.

### 4. Update the site's base URL
Open `content-gen/site_builder.py` and replace `SITE_BASE_URL = "https://REPLACE_WITH_YOUR_USERNAME.github.io/REPLACE_WITH_YOUR_REPO"` with your actual Pages URL once you know it (shown in Settings → Pages after the first deploy). This matters for the sitemap/RSS links to be correct.

### 5. Sign up for Amazon Associates India (optional, monetization)
Apply at **associates.amazon.in** using your blog's URL once it's live. Then fill in `config/affiliate_links.json`.

### 6. Test it
**Actions → Publish blog article → Run workflow**, then check the Pages URL to confirm the new article shows up.

## Local testing

```
pip install -r requirements.txt
python content-gen/generate_article.py --dry-run
```
Open the generated file under `site/docs/articles/` in a browser to preview.

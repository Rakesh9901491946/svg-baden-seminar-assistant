# SVG Baden Seminar & Services Assistant

An independent portfolio demo of how an AI assistant could help SVG Baden employees find answers in publicly described services and seminar information. **This is not an official SVG Baden product.**

> Demo uses public information only. Do not enter customer, employee, health, insurance, or other personal data.

The app retrieves relevant excerpts from a small local JSON corpus and shows the original source links. Without an API key it works in retrieval-only mode. With an optional Groq key it can generate a concise grounded summary from only the retrieved excerpts. Questions and responses are not written to a database, file, or analytics service.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Optional Groq configuration (never commit a real key):

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "..."
GROQ_MODEL = "openai/gpt-oss-20b"
```

Alternatively set `GROQ_API_KEY` and `GROQ_MODEL` in the environment. The provider/model are configurable. The default model name is a default only; verify current availability in Groq's [official model list](https://console.groq.com/docs/models). Groq lists open-weight GPT-OSS models and its [free-tier rate limits](https://console.groq.com/docs/rate-limits); exact limits depend on the account and model. This project does not ask to enable paid billing or switch to a paid provider. Never paste secrets into chat, source code, Git, logs, or screenshots.

## Architecture

- `app.py`: responsive Streamlit interface, consent notices, answer and source cards.
- `app/sources.py`: JSON loading and source validation.
- `app/retrieval.py`: transparent keyword retrieval, no-answer fallback, sensitive-topic guardrails, provider-safe seminar filtering.
- `app/llm_client.py`: optional bounded Groq-compatible API client with error handling and no fallback provider.
- `data/sources.json`: attributed source excerpts, URLs and retrieval date.
- `refresh_corpus.py`: validates a manually refreshed corpus. It performs no network requests.
- `tests/`: unit coverage for parsing, attribution, provider filtering, retrieval, citations, no-answer behavior and missing keys.

## Data sources and refresh

This initial corpus was assembled from user-provided PDF captures of these public pages:

- [SVG-Baden homepage](https://www.svg-baden.de/)
- [About SVG-Baden](https://www.svg-baden.de/ueber-uns)
- [Seminar portal](https://www.svg-baden.de/seminar-portal)
- [Digital occupational safety management system](https://www.svg-baden.de/arbeitssicherheit/digitales-arbeitsschutzmanagementsystem)

The captures were reviewed on 2026-10-26. Automated fetching was unavailable in the build environment, so this project does not scrape the site. To refresh, check the site's current terms and `robots.txt` manually, review each source page, update `data/sources.json` with concise attributed text, URLs, and the date reviewed, then run `python refresh_corpus.py`. Do not invent facts or add records lacking source evidence.

The supplied seminar portal capture showed 17 results with titles, dates and locations but did not provide individual course providers, prices or direct course URLs in the extracted capture. Because providers vary by regional organization, this pilot intentionally does not display partial seminar listings. Use the live portal to verify each course and its actual organizer.

## Limitations and safety

- This demo is informational and is not legal, insurance, occupational-safety, or compliance advice. Questions in those areas receive a specialist referral.
- Responses are restricted to retrieved source text; unsupported questions receive a no-answer message and official-site referral.
- The corpus is a small sample, not an official or complete knowledge base. Source pages and seminars can change.
- The optional hosted model receives the question and retrieved public excerpts. Do not enter personal or confidential information.
- App questions/responses remain in the active Streamlit session for rendering but are not persisted by this code to a DB, file, or analytics service. Hosting infrastructure may have its own operational logs; review provider privacy terms before a real pilot.

## Tests

```bash
pytest -q
```

## Deploy

1. Create a **public** GitHub repository named `svg-baden-seminar-assistant` under your account and push this project to `main`.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), choose **New app**, select that repository, branch `main`, and `app.py`.
3. In the app settings, add `GROQ_API_KEY` and optionally `GROQ_MODEL` under **Secrets**. This is optional: without a key, retrieval-only mode remains available. Do not enable paid billing for this demo.
4. Deploy and verify the public app URL.

For a real pilot, evaluate answer grounding, correct provider attribution, successful routing to specialists, and time to find an answer. Do not claim performance or savings until measured.

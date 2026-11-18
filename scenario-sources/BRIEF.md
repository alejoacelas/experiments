# Research brief (shared by all area agents)

Today is 2026-11-18. Read RUBRIC.md first. You own ONE area (given in your prompt). Work only inside
/home/user/experiments/scenario-sources/ and write only: primary/<area>/..., areas/<area>.json.

## Goal
We want the forecasts made by people/institutions with real incentives to be right, as inputs for a rich,
concrete narrative of how the world is experienced in 2026–2031. For your area:

1. List the 3–5 macro trends in your area that will most shape lived experience over the next ~5 years.
2. Build a COMPREHENSIVE list (aim 12–20) of forward-looking sources covering those trends. Prefer, in order:
   market prices; binding capital/contract commitments; forecasts filed under legal/regulatory scrutiny;
   statutory projections with published track records; scored forecasting platforms. Include well-known
   unincentivised sources too (so we can score them low explicitly). Use the LATEST edition — search to
   confirm what the latest is as of Nov 2026 and read its date off the document itself.
3. Score each on the three rubric dimensions with evidence. Be a tough grader; use the anchors literally.
4. Pick the top 4–5 (tier "top"): highest combined score, but they must cover different trends/mechanisms
   (don't pick four near-duplicates). Everything else is tier "considered".
5. DOWNLOAD primary documents:
   - top sources: every relevant primary document of the latest edition (main report + key appendices /
     data tables; for company-based sources the latest filing/transcript for each of the main companies;
     for market/price sources a dated data snapshot via API/CSV).
   - considered sources: the main document, best effort.
   Save to primary/<area>/<source-id>/<sensible-filename>. For every PDF run `pdftotext file.pdf file.pdf.txt`
   (default mode, keeps page breaks). For HTML keep the .html. For XLSX also save a .txt/.csv rendering.
   Record status honestly:
     full      = the complete official file is saved locally and readable (check `pdfinfo` page count / file size)
     partial   = only part saved (summary, excerpt, text capture via a fetch tool, some volumes of a set)
     failed    = blocked/404 after real attempts;   paywalled = requires purchase/login
   Download tips: `curl -L --fail -m 300 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"`.
   If 403: retry with extra headers (Accept, Referer), then try Playwright (`require('playwright')`, chromium is
   preinstalled, do not install) to fetch/download, then as last resort capture text with a web fetch tool and save
   it as .txt with status "partial". SEC EDGAR needs a descriptive UA: use "scenario-research-bot admin@example.com"
   (never put any real person's name/email in any request). Files up to ~300 MB are fine.
6. PULL QUOTES (top sources only): 3–5 per source. Each must be
   - VERBATIM from a file you downloaded (copy from the .txt; never from memory or a search snippet),
   - CONCRETE: a named place/company/programme + a number + a date beats any abstract statement. We want things a
     writer can drop into a scene: "X will build Y MW at Z by 2029", "premiums assumed to rise N% in 2027",
     "headcount of N by FY2028", "N aircraft delivered per year from 2028".
   - 15–60 words, self-contained; use " [...] " to skip text within one passage.
   - For price/data sources a quote is a data reading copied exactly as it appears in the saved file
     (e.g. a CSV row or JSON field), with as-of date in `locator`.
   At least one quote per top source should show how the source treats AI (if it does).
   Also fill ai_evidence.ai_passage with the single most telling verbatim AI passage for EVERY source where you
   downloaded a document (or null + note what terms you searched).
7. Run `python3 tools/verify.py areas/<area>.json` from the scenario-sources dir and fix until it reports 0 failed,
   0 docs missing. Fix page WARNs too.

## Output file: areas/<area>.json
{
 "area_id": "<area>", "area_name": "...",
 "trends": [{"trend": "...", "why_it_shapes_daily_life": "..."}],
 "sources": [{
   "id": "kebab-case", "name": "...", "publisher": "...",
   "kind": "market price | binding commitment | regulated filing | statutory projection | scored forecast | expert report | survey",
   "covers_trends": ["..."],
   "what_it_forecasts": "one concrete sentence",
   "horizon": "e.g. annual to 2046",
   "latest_edition": {"title": "...", "date": "YYYY-MM-DD", "url": "..."},
   "update_cadence": "...",
   "accuracy": {"score": 1-5, "tests_passed": ["T1","T3"], "why": "2–3 sentences, cite who loses what / who attacks it / track-record study (with url if any) / known bias"},
   "richness": {"score": 1-5, "why": "1–2 sentences naming the kinds of specifics inside"},
   "ai": {"score": 1-5, "why": "1–2 sentences: edition date + how AI enters the numbers"},
   "ai_evidence": {"updated_2026": true, "ai_treatment": "none | qualitative | partial quantification | quantified driver",
                   "ai_passage": {"text": "...", "doc_local_path": "primary/...", "page": 12} or null,
                   "search_note": "terms searched if none found"},
   "tier": "top | considered",
   "why_top_or_not": "one sentence",
   "primary_docs": [{"title": "...", "url": "...", "local_path": "primary/<area>/<id>/file.pdf",
                     "status": "full|partial|failed|paywalled", "bytes": 0, "pages": 0, "note": ""}],
   "quotes": [{"text": "...", "doc_local_path": "primary/...", "page": 0, "locator": "section/table name",
               "url": "public url of the doc", "worldbuilding_use": "what concrete scenario input this gives (≤20 words)"}]
 }]
}
local paths are relative to scenario-sources/. Validate the JSON parses.

## Rules
- Rigor over volume: an unverifiable claim is worse than a gap. If you could not confirm an edition date or
  download a doc, say so in the note fields. Never invent numbers, dates, URLs or quotes.
- Do not commit, push or touch git. Do not write outside your area's paths. Do not spawn further agents.
- Your final message: ≤15 lines — top picks with scores, download counts (full/partial/failed), verify.py result,
  and anything surprising (e.g. a famous source that turned out stale or silent on AI).

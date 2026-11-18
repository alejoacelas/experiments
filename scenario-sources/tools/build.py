#!/usr/bin/env python3
"""Build the artifact page from areas/*.json (+ final_scores.json overrides).
Re-checks every downloaded file on disk and re-verifies every quote; unverified quotes are not rendered.
Usage: python3 tools/build.py  -> writes site/index.html and manifest.json"""
import json, os, re, glob, html, subprocess, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import squash, load_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA_ORDER = ["macro", "ai-compute", "energy", "labor", "health", "housing-cities", "climate-insurance",
              "fiscal-government", "geopolitics", "demographics-education", "mobility-tech"]
E = lambda s: html.escape(str(s if s is not None else ""), quote=True)

ANCHORS = {
 "accuracy": {5: "Passes 4–5 of the five tests, no known directional bias. A known, measurable bias costs one point at any level.",
              4: "Passes 3 tests, or 4–5 with a known, measurable bias.",
              3: "Passes 2 tests: accountable with a track record but no money at stake, or money at stake on a much shorter instrument.",
              2: "Passes 1 test: interested party, long-dated vendor roadmap, unscored panel or survey.",
              1: "Passes none: marketing, advocacy, unscored scenarios."},
 "richness": {5: "Names entities, places, dates and quantities and explains its assumptions. Dozens of liftable facts.",
              4: "Disaggregated by sector, region or product with narrated drivers; some named specifics.",
              3: "Several series with brief commentary; few named specifics.",
              2: "A handful of headline series; minimal narrative.",
              1: "A single price or probability with no reasoning."},
 "ai": {5: "2026 edition and AI is a quantified, separately identified driver, or the instrument visibly re-prices on AI news.",
        4: "2026 edition; AI analysed as a material driver with partial quantification.",
        3: "2026 edition; AI acknowledged qualitatively but numbers unmoved, or a live price that embeds AI inseparably.",
        2: "2025–26 edition with no AI treatment, or a method that structurally cannot respond. A 2025 edition that does treat AI is capped at 3.",
        1: "Latest edition pre-2025 with no AI treatment."},
}
DIM_LABEL = {"accuracy": "Accuracy conditions", "richness": "Worldbuilding richness", "ai": "AI responsiveness"}
DIM_SHORT = {"accuracy": "Accuracy", "richness": "Richness", "ai": "AI"}
TESTS = {"T1": "Stakes", "T2": "Adversaries", "T3": "Feedback", "T4": "Horizon fit", "T5": "Pipeline"}


def file_info(lp):
    p = os.path.join(ROOT, lp) if lp and not os.path.isabs(lp) else lp
    if not p or not os.path.isfile(p):
        return None
    info = {"bytes": os.path.getsize(p), "pages": None}
    if p.lower().endswith(".pdf"):
        try:
            out = subprocess.run(["pdfinfo", p], capture_output=True, text=True, timeout=60).stdout
            m = re.search(r"Pages:\s+(\d+)", out)
            info["pages"] = int(m.group(1)) if m else 0
        except Exception:
            info["pages"] = 0
    return info


def check_doc(doc):
    st = (doc.get("status") or "failed").lower()
    fi = file_info(doc.get("local_path"))
    if st in ("full", "partial"):
        if not fi or fi["bytes"] < 500 or fi["pages"] == 0:
            st = "failed"
            doc["note"] = ((doc.get("note") or "") + " [file missing or unreadable on re-check]").strip()
    doc["status"] = st if st in ("full", "partial", "failed", "paywalled") else "failed"
    if fi:
        doc["bytes"], doc["pages"] = fi["bytes"], fi["pages"]
    return doc


def verify_quote(q):
    txt = load_text(q.get("doc_local_path", "") or "")
    if txt is None:
        return False
    whole = squash(txt)
    segs = [x for x in re.split(r"\s*\[\.\.\.\]\s*|\s*\[…\]\s*", q.get("text", "")) if squash(x)]
    return bool(segs) and all(squash(x) in whole for x in segs)


def load():
    over = {}
    op = os.path.join(ROOT, "final_scores.json")
    if os.path.exists(op):
        over = json.load(open(op))
    areas = []
    for aid in AREA_ORDER:
        f = os.path.join(ROOT, "areas", aid + ".json")
        if not os.path.exists(f):
            continue
        a = json.load(open(f))
        a["area_id"] = aid
        if aid in over.get("_areas", {}):
            a.update(over["_areas"][aid])
        for s in a["sources"]:
            o = over.get(aid + "/" + s["id"], {})
            for dim in ("accuracy", "richness", "ai"):
                s.setdefault(dim, {})
                if dim in o:
                    note = o[dim].pop("note", None)
                    s[dim].update(o[dim])
                    if note:
                        s[dim]["why"] = (s[dim].get("why", "") + " Calibration note: " + note).strip()
            for k in ("tier", "why_top_or_not", "name", "what_it_forecasts", "drop_quotes", "quote_order"):
                if k in o:
                    s[k] = o[k]
            s["primary_docs"] = [check_doc(d) for d in s.get("primary_docs", []) + o.get("extra_docs", [])]
            good = []
            for i, q in enumerate(s.get("quotes", [])):
                if i in s.get("drop_quotes", []):
                    continue
                q["verified"] = verify_quote(q)
                if q["verified"]:
                    good.append(q)
            s["unverified_quotes"] = len([q for q in s.get("quotes", []) if not q.get("verified")]) - len(s.get("drop_quotes", []))
            s["quotes"] = good
            s["total"] = sum(int(s[d].get("score", 0) or 0) for d in ("accuracy", "richness", "ai"))
        a["sources"].sort(key=lambda s: (-(s.get("tier") == "top"), -s["total"], -int(s["accuracy"].get("score", 0) or 0)))
        areas.append(a)
    return areas


def meter(dim, s, compact=False):
    d = s.get(dim, {})
    sc = int(d.get("score", 0) or 0)
    tip = f"{DIM_LABEL[dim]}: {sc} of 5\nAnchor: {ANCHORS[dim].get(sc, '')}\n\n{d.get('why', '')}"
    if dim == "accuracy" and d.get("tests_passed"):
        tip += "\n\nTests passed: " + ", ".join(f"{t} {TESTS.get(t, '')}" for t in d["tests_passed"])
    segs = "".join(f'<i class="{"on" if i < sc else ""}"></i>' for i in range(5))
    if compact:
        return (f'<button type="button" class="m c" data-tip="{E(tip)}" aria-label="{E(DIM_LABEL[dim])} {sc} of 5">'
                f'<span class="segs">{segs}</span><b>{sc}</b></button>')
    return (f'<button type="button" class="m" data-tip="{E(tip)}" aria-label="{E(DIM_LABEL[dim])} {sc} of 5. Explanation on hover or focus.">'
            f'<span class="ml">{E(DIM_LABEL[dim])}</span><span class="segs">{segs}</span><b>{sc}</b></button>')


def fmt_bytes(n):
    if not n:
        return ""
    return f"{n/1e6:.1f} MB" if n >= 1e6 else f"{max(1, round(n/1e3))} kB"


STATUS = {"full": ("✓", "in full"), "partial": ("◐", "partial"), "failed": ("✕", "not obtained"), "paywalled": ("▣", "paywalled")}


def uniq_docs(sources):
    seen, out = set(), []
    for s in sources:
        for d in s.get("primary_docs", []):
            k = d.get("local_path") or d.get("url") or id(d)
            if k in seen:
                continue
            seen.add(k)
            out.append(d)
    return out


def doc_counts(sources):
    docs = uniq_docs(sources)
    return sum(d["status"] == "full" for d in docs), len(docs)


def norm_kind(k):
    k = (k or "").lower()
    for key in ("market price", "binding commitment", "regulated filing", "statutory projection", "scored forecast", "expert report", "survey"):
        if key in k:
            return key
    return "expert report"


def is_data(t):
    letters = sum(c.isalpha() for c in t)
    return letters / max(1, len(t)) < 0.45 or t.count(",") > 8 and letters / max(1, len(t)) < 0.6


def doc_title_for(s, lp):
    for d in s.get("primary_docs", []):
        if d.get("local_path") == lp:
            return d.get("title") or os.path.basename(lp)
    return os.path.basename(lp or "")


def fmt_date(d):
    try:
        return datetime.date.fromisoformat(d[:10]).strftime("%-d %b %Y")
    except Exception:
        return d or "undated"


def card(a, s):
    le = s.get("latest_edition", {}) or {}
    full, tot = doc_counts([s])
    quotes = ""
    qparts = []
    for q in s["quotes"]:
        loc = []
        if isinstance(q.get("page"), int) and q["page"] > 0:
            loc.append(f"p. {q['page']}")
        if q.get("locator"):
            loc.append(q["locator"])
        title = doc_title_for(s, q.get("doc_local_path"))
        link = q.get("url") or next((d.get("url") for d in s["primary_docs"] if d.get("local_path") == q.get("doc_local_path")), "")
        src = f'<a href="{E(link)}" target="_blank" rel="noopener">{E(title)}</a>' if link else E(title)
        qparts.append(f'<figure class="q{" data" if is_data(q["text"]) else ""}"><blockquote>{E(q["text"])}</blockquote>'
                   f'<figcaption><span class="cite">{src}{" · " + E(" · ".join(loc)) if loc else ""}</span>'
                   f'<span class="use"><b>Scenario input</b> {E(q.get("worldbuilding_use", ""))}</span></figcaption></figure>')
    quotes = "".join(qparts[:3])
    if len(qparts) > 3:
        quotes += f'<details class="moreq"><summary>{len(qparts) - 3} more quote{"s" if len(qparts) > 4 else ""} from this source</summary><div class="mq">{"".join(qparts[3:])}</div></details>'
    if not quotes:
        quotes = '<p class="noq">No quote passed verbatim verification for this source.</p>'
    docs = ""
    for d in s["primary_docs"]:
        ic, lab = STATUS[d["status"]]
        bits = [x for x in [f"{d['pages']} pp" if d.get("pages") else "", fmt_bytes(d.get("bytes")) if d["status"] in ("full", "partial") else ""] if x]
        t = f'<a href="{E(d.get("url"))}" target="_blank" rel="noopener">{E(d.get("title"))}</a>' if d.get("url") else E(d.get("title"))
        path = f'<code>{E(d["local_path"])}</code>' if d.get("local_path") and d["status"] in ("full", "partial") else ""
        note = f'<span class="dn">{E(d["note"])}</span>' if d.get("note") else ""
        docs += (f'<li class="st-{d["status"]}"><span class="stt"><span aria-hidden="true">{ic}</span> {lab}</span>'
                 f'<span class="dt">{t}{" · " + " · ".join(bits) if bits else ""}{path}{note}</span></li>')
    ed = f'<a href="{E(le.get("url"))}" target="_blank" rel="noopener">{E(fmt_date(le.get("date")))}</a>' if le.get("url") else E(fmt_date(le.get("date")))
    return f'''<article class="src" id="{E(a["area_id"])}-{E(s["id"])}">
<div class="side">
<h4>{E(s["name"])}</h4>
<p class="pub">{E(s.get("publisher"))}</p>
<dl class="meta"><div><dt>Type</dt><dd>{E(s.get("kind"))}</dd></div><div><dt>Edition</dt><dd>{ed}</dd></div><div><dt>Reaches</dt><dd>{E(s.get("horizon"))}</dd></div></dl>
<div class="scores">{meter("accuracy", s)}{meter("richness", s)}{meter("ai", s)}</div>
<details class="docs"><summary><span class="frac">{full} of {tot}</span> primary documents downloaded in full</summary><ul>{docs}</ul></details>
</div>
<div class="main">
<p class="what">{E(s.get("what_it_forecasts"))}</p>
{quotes}
</div>
</article>'''


def considered_table(a, rest):
    rows = ""
    for s in rest:
        le = s.get("latest_edition", {}) or {}
        full, tot = doc_counts([s])
        nm = f'<a href="{E(le.get("url"))}" target="_blank" rel="noopener">{E(s["name"])}</a>' if le.get("url") else E(s["name"])
        rows += (f'<tr><td class="cn">{nm}<span class="ck">{E(s.get("kind"))} · {E(fmt_date(le.get("date")))}</span></td>'
                 f'<td>{meter("accuracy", s, True)}</td><td>{meter("richness", s, True)}</td><td>{meter("ai", s, True)}</td>'
                 f'<td class="num">{full}/{tot}</td><td class="cw">{E(s.get("why_top_or_not"))}</td></tr>')
    return (f'<details class="cons"><summary>{len(rest)} more sources scored in this area</summary><div class="tw"><table>'
            f'<thead><tr><th>Source</th><th>Accuracy</th><th>Richness</th><th>AI</th><th class="num">Docs in full</th><th>Why it is not a top pick</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></details>')


def build():
    areas = load()
    all_src = [s for a in areas for s in a["sources"]]
    tops = [s for s in all_src if s.get("tier") == "top"]
    full_all, tot_all = doc_counts(all_src)
    full_top, tot_top = doc_counts(tops)
    nq = sum(len(s["quotes"]) for s in tops)
    ud = uniq_docs(all_src)
    total_bytes = sum(d.get("bytes") or 0 for d in ud if d["status"] in ("full", "partial"))
    total_pages = sum(d.get("pages") or 0 for d in ud if d["status"] == "full")
    partial_all = sum(d["status"] == "partial" for d in ud)
    kinds = {}
    for x in all_src:
        kinds.setdefault(norm_kind(x.get("kind")), []).append(x)
    order = ["market price", "binding commitment", "regulated filing", "statutory projection", "scored forecast", "expert report", "survey"]
    KLAB = {"market price": "Market prices", "binding commitment": "Binding commitments (contracts, statutes, enacted budgets)", "regulated filing": "Regulated filings",
            "statutory projection": "Official projections", "scored forecast": "Scored forecasts", "expert report": "Expert reports", "survey": "Surveys"}
    avg = lambda xs, d: sum(int(x[d].get("score", 0) or 0) for x in xs) / len(xs)
    kind_rows = "".join(
        f'<tr><td>{KLAB[k]}</td><td class="num">{len(kinds[k])}</td><td class="num">{avg(kinds[k], "accuracy"):.1f}</td>'
        f'<td class="num">{avg(kinds[k], "richness"):.1f}</td><td class="num">{avg(kinds[k], "ai"):.1f}</td></tr>' for k in order if k in kinds)
    all3 = sum(all(int(x[d].get("score", 0) or 0) >= 4 for d in ("accuracy", "richness", "ai")) for x in all_src)
    ai_silent = sum(int(x["ai"].get("score", 0) or 0) <= 2 for x in all_src)
    missing_all = tot_all - full_all - partial_all

    nav = "".join(f'<a href="#{E(a["area_id"])}">{E(a["area_name"])}</a>' for a in areas)
    glance = ""
    for a in areas:
        t = [s for s in a["sources"] if s.get("tier") == "top"]
        for i, s in enumerate(t):
            full, tot = doc_counts([s])
            ar = f'<th scope="rowgroup" rowspan="{len(t)}" class="ga"><a href="#{E(a["area_id"])}">{E(a["area_name"])}</a></th>' if i == 0 else ""
            glance += (f'<tr class="{"gs" if i == 0 else ""}">{ar}<td class="cn"><a href="#{E(a["area_id"])}-{E(s["id"])}">{E(s["name"])}</a></td>'
                       f'<td>{meter("accuracy", s, True)}</td><td>{meter("richness", s, True)}</td><td>{meter("ai", s, True)}</td>'
                       f'<td class="num">{full}/{tot}</td></tr>')
    sections = ""
    for a in areas:
        t = [s for s in a["sources"] if s.get("tier") == "top"]
        rest = [s for s in a["sources"] if s.get("tier") != "top"]
        fa, ta = doc_counts(a["sources"])
        trends = "".join(f'<li><b>{E(x.get("trend"))}</b> {E(x.get("why_it_shapes_daily_life"))}</li>' for x in a.get("trends", []))
        sections += f'''<section class="area" id="{E(a["area_id"])}">
<header class="ah"><h3>{E(a["area_name"])}</h3>
<p class="ac">{len(a["sources"])} sources scored · {len(t)} shown · <span class="frac">{fa} of {ta}</span> primary documents downloaded in full</p></header>
{f'<p class="take">{E(a["takeaway"])}</p>' if a.get("takeaway") else ""}
<details class="trends"><summary>Trends these sources need to cover</summary><ul>{trends}</ul></details>
{"".join(card(a, s) for s in t)}
{considered_table(a, rest) if rest else ""}
</section>'''

    def anchors(dim):
        return "".join(f'<li><b>{k}</b><span>{E(ANCHORS[dim][k])}</span></li>' for k in (5, 4, 3, 2, 1))

    tpl = open(os.path.join(ROOT, "tools", "page.html")).read()
    fp = os.path.join(ROOT, "tools", "findings.html")
    tpl = tpl.replace("{{FINDINGS}}", open(fp).read() if os.path.exists(fp) else "")
    tpl = tpl.replace("{{KIND_ROWS}}", kind_rows).replace("{{ALL3}}", str(all3)).replace("{{AI_SILENT}}", str(ai_silent))
    page = (tpl.replace("{{NAV}}", nav).replace("{{GLANCE}}", glance).replace("{{SECTIONS}}", sections)
            .replace("{{N_ALL}}", str(len(all_src))).replace("{{N_TOP}}", str(len(tops))).replace("{{N_AREAS}}", str(len(areas)))
            .replace("{{FULL_ALL}}", str(full_all)).replace("{{TOT_ALL}}", str(tot_all))
            .replace("{{FULL_TOP}}", str(full_top)).replace("{{TOT_TOP}}", str(tot_top))
            .replace("{{PARTIAL_ALL}}", str(partial_all)).replace("{{MISSING_ALL}}", str(missing_all))
            .replace("{{NQ}}", str(nq)).replace("{{GB}}", f"{total_bytes/1e9:.2f}").replace("{{PAGES}}", f"{total_pages:,}")
            .replace("{{A_ACC}}", anchors("accuracy")).replace("{{A_RICH}}", anchors("richness")).replace("{{A_AI}}", anchors("ai")))
    os.makedirs(os.path.join(ROOT, "site"), exist_ok=True)
    open(os.path.join(ROOT, "site", "index.html"), "w").write(page)
    manifest = [{"area": a["area_id"], "source": s["id"], "tier": s.get("tier"), **{k: d.get(k) for k in ("title", "url", "local_path", "status", "bytes", "pages", "note")}}
                for a in areas for s in a["sources"] for d in s["primary_docs"]]
    json.dump(manifest, open(os.path.join(ROOT, "manifest.json"), "w"), indent=1)
    unv = sum(max(0, s.get("unverified_quotes", 0)) for s in tops)
    print(f"areas={len(areas)} sources={len(all_src)} top={len(tops)} docs full={full_all}/{tot_all} (top {full_top}/{tot_top}) "
          f"quotes rendered={nq} dropped-unverified={unv} bytes={total_bytes/1e9:.2f}GB page={len(page)/1e3:.0f}kB")


if __name__ == "__main__":
    build()

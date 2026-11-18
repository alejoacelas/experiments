#!/usr/bin/env python3
"""Verify that every quote in an area JSON appears verbatim in the downloaded primary document.
Usage: python3 tools/verify.py areas/<area>.json
Matching ignores case, whitespace and punctuation (so line-wraps/hyphenation don't matter) but the
word sequence must be exact. Use ' [...] ' inside a quote to skip text; every segment must match."""
import json, sys, re, os, unicodedata, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def squash(s):
    s = unicodedata.normalize('NFKC', s).lower()
    return re.sub(r'[^0-9a-z]+', '', s)
def load_text(path):
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    cand = p + '.txt' if os.path.exists(p + '.txt') else p
    if not os.path.exists(cand): return None
    raw = open(cand, 'rb').read().decode('utf-8', 'ignore')
    if cand.lower().endswith(('.html', '.htm')):
        raw = re.sub(r'(?is)<(script|style).*?</\1>', ' ', raw); raw = html.unescape(re.sub(r'<[^>]+>', ' ', raw))
    return raw
def main(f):
    d = json.load(open(f)); bad = 0; n = 0; docs_missing = 0
    for s in d['sources']:
        for doc in s.get('primary_docs', []):
            lp = doc.get('local_path')
            if doc.get('status') in ('full', 'partial'):
                p = lp if lp and os.path.isabs(lp) else os.path.join(ROOT, lp or '')
                if not lp or not os.path.exists(p) or os.path.getsize(p) < 500:
                    print(f"DOC MISSING/EMPTY [{s['id']}] {lp}"); docs_missing += 1
        qs = list(s.get('quotes', []))
        ap = (s.get('ai_evidence') or {}).get('ai_passage')
        if isinstance(ap, dict) and ap.get('text'): qs.append(ap)
        for q in qs:
            n += 1
            txt = load_text(q.get('doc_local_path', ''))
            if txt is None:
                print(f"FAIL [{s['id']}] doc not found: {q.get('doc_local_path')}"); bad += 1; continue
            pages = txt.split('\f'); whole = squash(txt)
            segs = [x for x in re.split(r'\s*\[\.\.\.\]\s*|\s*\[…\]\s*', q['text']) if squash(x)]
            ok = all(squash(x) in whole for x in segs)
            if not ok:
                print(f"FAIL [{s['id']}] not found verbatim: {q['text'][:90]!r}"); bad += 1; continue
            pg = q.get('page')
            if isinstance(pg, int) and len(pages) > 1:
                lo, hi = max(0, pg - 2), min(len(pages), pg + 1)
                if squash(segs[0]) not in squash(''.join(pages[lo:hi])):
                    actual = [i + 1 for i, t in enumerate(pages) if squash(segs[0]) in squash(t)]
                    print(f"WARN [{s['id']}] page {pg} wrong, found on {actual[:5]}: {q['text'][:60]!r}")
    print(f"{f}: {n} quotes checked, {bad} failed, {docs_missing} docs missing")
    return 1 if bad or docs_missing else 0
if __name__ == '__main__': sys.exit(main(sys.argv[1]))

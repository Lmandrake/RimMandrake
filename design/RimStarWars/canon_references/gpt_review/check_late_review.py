#!/usr/bin/env python3
"""Proof of CANON_LATE_ENTRIES_VET_ARRIVED_AFTER_PARTY: the 55 creature entries added after the 119-entry review get the
same method (GPT batches, every claim checked on Wookieepedia, verified edits merged, ruled conflicts flagged).
Offline; exit 0 only if every clause holds.
  LATE_SLUGS.txt          the frozen late set: INDEX.md creature rows absent from REVIEWED_SLUGS.txt
  late_NN.md              GPT's answer per batch of 5 (run_canon_review.py --late)
  late_wiki_cache.json    Wookieepedia wikitext of every page a verdict cites (late_wiki.py)
  LATE_VERIFICATION_LOG.md  | entry | claim | VERDICT | page | quote |  - a VERIFIED/REFUTED quote must be in its page
  LATE_CLAIM_MAP.json     [{id, entry, rows}] - every ERRORS/ENRICHMENT/cross-entry line of late_NN.md (late_bullets.py) points at its log rows
  page continuity         read from each page's own {{Top}} header: no page of Legends or non-canon status is labelled canon in an entry
  LATE_MERGES.json        {"owner_item": ID, "rows": [{entry, text, claim, ruled}]} - each text is in the entry now; owner_item is a ledger item filed in an earlier commit than the candidate
A quote may be flat page text or raw wikitext; only the raw form can reach the {{Top}} header and the infobox lines.
usage: check_late_review.py"""
import json, os, re, sys, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(LIB, "..", "..", ".."))
bad = []


def need(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        bad.append(msg)


def flat(s):
    """wikitext and a quote compared as plain words: [[A|b]] -> b, '' and {{...}} refs dropped, case and spaces folded"""
    s = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", " ", s, flags=re.S)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", " ", s)
    s = s.replace("'''", "").replace("''", "")
    s = re.sub(r"[^\w%.,;:()'-]+", " ", s.lower().replace("’", "'"))
    return re.sub(r"\s+", " ", s).strip()


rows = [l for l in open(os.path.join(LIB, "INDEX.md"), encoding="utf-8") if l.startswith("| [")]
creature = [re.match(r"\| \[([^\]]+)\]", l).group(1) for l in rows if l.split("|")[2].strip() == "creature"]
old = open(os.path.join(HERE, "REVIEWED_SLUGS.txt")).read().split()
late = open(os.path.join(HERE, "LATE_SLUGS.txt")).read().split()
need(len(old) == 119 and len(creature) >= 174, f"instrument sees {len(creature)} creature rows and the 119 old slugs")
need(late == [s for s in creature if s not in old] and len(late) == 55,
     f"LATE_SLUGS.txt holds the {len(late)} creature rows the 119-entry review never saw, in INDEX order")

nb = (len(late) + 4) // 5
small = [n for n in range(1, nb + 1)
         if not os.path.exists(os.path.join(HERE, f"late_{n:02d}.md")) or os.path.getsize(os.path.join(HERE, f"late_{n:02d}.md")) < 2000]
need(not small, f"{nb} GPT batches late_01..late_{nb:02d} on disk, none a stub; missing/stub: {small}")
squash = lambda t: re.sub(r"[\s_-]+", "", t.lower())  # slug "ithorianreek" is the answer's "Ithorian reek"
answered = [s for n in range(1, nb + 1) if n not in small for s in late[(n - 1) * 5:n * 5]
            if squash(s) not in squash(open(os.path.join(HERE, f"late_{n:02d}.md"), encoding="utf-8").read())]
need(not answered, f"every batch answers each of its entries by name; unanswered: {answered}")

cache = json.load(open(os.path.join(HERE, "late_wiki_cache.json"), encoding="utf-8"))
flatc = {t: flat(v["wikitext"]) for t, v in cache.items() if v.get("exists")}
need(len(flatc) >= 80, f"wiki cache holds {len(flatc)} real pages (instrument can see)")
lp = os.path.join(HERE, "LATE_VERIFICATION_LOG.md")
need(os.path.exists(lp), "LATE_VERIFICATION_LOG.md exists")
log = open(lp, encoding="utf-8").read() if os.path.exists(lp) else ""
need(len(re.findall(r"^## Late batch \d\d$", log, re.M)) == nb, f"verification log holds all {nb} batches")
vrows = []
for ln in log.splitlines():
    m = re.match(r"^\| ([a-z_]+) \| (.+?) \| (VERIFIED|REFUTED|UNVERIFIABLE)[^|]* \| ([^|]*) \| (.*) \|$", ln)
    if m:
        vrows.append(m.groups())
need(len(vrows) >= 3 * len(late), f"{len(vrows)} verification rows (at least 3 per entry)")
miss = [s for s in late if s not in {r[0] for r in vrows}]
need(not miss, f"every late entry has verification rows; missing: {miss}")
unq = []
for e, claim, v, page, quote in vrows:
    if v == "UNVERIFIABLE":
        continue
    p = page.strip()
    p = p[:1].upper() + p[1:]
    q = re.findall(r'"([^"]+)"', quote)
    # continuity and size and colour sit in the {{Top}} header and the infobox, which flat() drops, so a quote may also match the raw wikitext
    if p not in flatc or not q or any(not (x in cache[p]["wikitext"] and (len(x) >= 11 or x.startswith("{{Top"))) and (len(flat(x)) < 12 or flat(x) not in flatc[p]) for x in q):
        unq.append(f"{e}: {claim[:50]}")
need(not unq, f"every VERIFIED/REFUTED row quotes its cited page's wikitext word for word; failing: {unq[:8]} ({len(unq)})")
ver = sum(1 for r in vrows if r[2] != "UNVERIFIABLE")
need(ver >= len(late), f"{ver} rows were decided on the page, not left UNVERIFIABLE")
need(flat("4.2 meters") in flatc.get("Rancor", ""), "sanity probe: the quote matcher finds the rancor's height through [[meter]]s markup")
need("|height=2 [[meter]]s" in cache["Gundark"]["wikitext"], "sanity probe: an infobox line is readable raw in the cache")
need(not any(flat("purple polka-dot wings of the rancor") in v for v in flatc.values()), "sanity probe: an invented quote is not found")

mp = os.path.join(HERE, "LATE_MERGES.json")
need(os.path.exists(mp), "LATE_MERGES.json exists")
mg = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"owner_item": "NONE_FILED", "rows": []}
entry = lambda s: open(os.path.join(LIB, s, "description.md"), encoding="utf-8").read()
need(len(mg["rows"]) >= 20, f"{len(mg['rows'])} verified edits merged")
gone = [r["entry"] for r in mg["rows"] if r["text"] not in entry(r["entry"])]
need(not gone, f"each merged edit's text is in its entry's description.md; missing: {gone}")
verified = {(r[0], r[1]) for r in vrows if r[2] == "VERIFIED" or r[2] == "REFUTED"}
orphan = [r["entry"] for r in mg["rows"] if (r["entry"], r["claim"]) not in verified]
need(not orphan, f"each merge names a VERIFIED/REFUTED claim of the log; orphans: {orphan}")
ruled = {re.match(r"\| \[([^\]]+)\]", l).group(1) for l in rows if l.split("|")[6].strip() == "yes"}  # gen_index's "ruled" column
ruled &= set(late)
need({"rancor", "taozin"} <= ruled, f"sanity probe: ruled entries are seen ({sorted(ruled)})")
wrong = [r["entry"] for r in mg["rows"] if r.get("ruled") != (r["entry"] in ruled)]
need(not wrong, f"each merge says truly whether its entry is ruled; wrong: {wrong}")

item = mg["owner_item"]
events = []
evdir = os.path.join(ROOT, "infrastructure/state/ledger/events")
for f in os.listdir(evdir):
    if f.endswith(".jsonl"):
        for ln in open(os.path.join(evdir, f), errors="ignore"):
            if item in ln:
                events.append(json.loads(ln))
filed = " ".join(e.get("spec", "") + " " + e.get("text", "") + " " + e.get("title", "") for e in events)
need(any(e.get("event") == "file" and e.get("id") == item for e in events), f"ruled conflicts are filed as {item}")
conf = mg.get("ruled_conflicts", [])
miss = [c["entry"] for c in conf if c["entry"] not in filed] + [r["entry"] for r in mg["rows"] if r["ruled"] and r["entry"] not in filed]
need(not miss, f"each of {len(conf)} ruled conflicts and every edit on a ruled entry is named in {item}; missing: {miss}")
def top(t):
    m = re.search(r"\{\{Top([^{}]*)\}\}", cache[t]["wikitext"][:800]) if cache.get(t, {}).get("exists") else None
    return m.group(1) if m else ""


def not_canon(t):
    """the page's own header says it is Legends (|leg, or canon=<its canon twin>) or non-canon (|ncc); a /Legends title is too"""
    h = top(t)
    return t.endswith("/Legends") or bool(re.search(r"\|(leg|ncc)\b|\|canon=", h))


def cited(line):
    return [(lambda x: x[:1].upper() + x[1:])(urllib.parse.unquote(x).replace("_", " ")) for x in re.findall(r"starwars\.fandom\.com/wiki/([^\s)\]`>]+)", line)]


def mislabels(text):
    """lines of an entry that call a page canon when that page's header says it is not"""
    out, pages = [], [p for ln in text.splitlines() for p in cited(ln)]
    for ln in text.splitlines():
        for p in cited(ln):
            if p in cache and not_canon(p) and re.search(r"^### Canon\b|\(canon\b", ln):
                out.append(ln)
        for p in re.findall(r"(?:CANON page|canon page) `([^`]+)`", ln):
            if p in cache and not_canon(p):
                out.append(ln)
        if pages and all(p in cache and not_canon(p) for p in pages) and re.search(r"canon text|canon says|also canon|canon-attested", ln):
            out.append(ln)
    return out


need(not_canon("Torton") and not not_canon("Rancor") and not_canon("Maalraas") and not not_canon("Nighthunter"),
     "sanity probe: page headers read Torton and Maalraas as Legends, Rancor and Nighthunter as canon")
need(mislabels("### Canon — https://starwars.fandom.com/wiki/Torton") and not mislabels("### Canon — https://starwars.fandom.com/wiki/Rancor"),
     "sanity probe: the label scan flags a planted canon heading on Torton and passes the same line on Rancor")
lab = {s: mislabels(entry(s)) for s in late}
lab = {s: v for s, v in lab.items() if v}
need(not lab, f"no late entry labels a Legends or non-canon page as canon; mislabelled: {sorted(lab)}")
owed = {(s, p) for s in late for p in cited(entry(s)) if p in cache and not_canon(p) and not p.endswith("/Legends")}
need(len(owed) >= 10, f"sanity probe: {len(owed)} unsuffixed pages of Legends or non-canon status are cited by late entries")
hdr = {(r[0], r[3].strip()) for r in vrows if r[2] == "VERIFIED" and "{{Top" in r[4]}
need(not owed - hdr, f"each has a VERIFIED row quoting its header; missing: {sorted(owed - hdr)}")
dodge = [f"{r[0]}: {r[1][:50]}" for r in vrows if r[2] == "UNVERIFIABLE" and re.search(r"\b(is|are)\b.*\bLegends\b", r[1])
         and any(s == r[0] for s, _ in owed)]
need(not dodge, f"no row leaves a header-decidable continuity claim UNVERIFIABLE; left: {dodge}")

sys.path.insert(0, HERE)
from late_bullets import bullets
said = [b for n in range(1, nb + 1) if n not in small for b in bullets(n, late)]
need(len(said) >= 500 and {b["section"] for b in said} == {"ERRORS", "ENRICHMENT", "CROSS"}, f"sanity probe: parser sees {len(said)} GPT statements in all three sections")
cmp = os.path.join(HERE, "LATE_CLAIM_MAP.json")
cm = json.load(open(cmp, encoding="utf-8")) if os.path.exists(cmp) else []
byid = {c["id"]: c for c in cm}
need(not [b["id"] for b in said if b["id"] not in byid], f"every GPT statement has a map entry; unmapped: {[b['id'] for b in said if b['id'] not in byid][:8]}")
known, words, uses, badmap = {(r[0], r[1]) for r in vrows}, lambda s: set(re.findall(r"[a-z]{4,}", s.lower())), {}, []
rowwords = {(r[0], r[1]): r[1] + " " + r[3] + " " + r[4] for r in vrows}
for b in said:
    c = byid.get(b["id"])
    if not c:
        continue
    keys = [(c["entry"], x) for x in c["rows"]]
    if not keys or (b["entry"] and c["entry"] != b["entry"]) or c["entry"] not in late or any(k not in known for k in keys):
        badmap.append(b["id"])
    elif not words(b["text"]) & words(" ".join(rowwords[k] for k in keys)):
        badmap.append(b["id"] + " shares no word")
    for k in keys:
        uses[k] = uses.get(k, 0) + 1
need(not badmap, f"each map entry points at real rows of its own entry that share a word with the statement; bad: {badmap[:8]} ({len(badmap)})")
over = [k for k, v in uses.items() if v > 5]
need(not over, f"no log row stands in for more than 5 statements; over: {over[:5]}")
print("PROVEN" if not bad else f"{len(bad)} FAILED")
sys.exit(1 if bad else 0)

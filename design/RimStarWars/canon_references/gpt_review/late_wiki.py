#!/usr/bin/env python3
"""Wookieepedia wikitext cache for the late-entry review (CANON_LATE_ENTRIES_VET_ARRIVED_AFTER_PARTY).
Every starwars.fandom.com/wiki/<Title> link in a LATE_SLUGS.txt entry, plus any title given on the command line (kept in late_wiki_extra.txt), is
fetched once through the MediaWiki parse API (unauthenticated, no size cap; tool_traps.md) and kept in
late_wiki_cache.json as {title: {"exists": bool, "wikitext": str}}, redirects followed. The verification log's quotes
are checked against this file by check_late_review.py, so the proof needs no network.
usage: late_wiki.py [extra titles...]   |   late_wiki.py --grep TITLE REGEX   (print matching lines of a cached page)"""
import json, os, re, sys, time, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "late_wiki_cache.json")
API = "https://starwars.fandom.com/api.php"


def norm(t):
    t = urllib.parse.unquote(t).replace("_", " ").strip()
    return t[:1].upper() + t[1:]


def fetch(title):
    q = urllib.parse.urlencode({"action": "parse", "page": title, "format": "json", "prop": "wikitext", "redirects": 1})
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "RimMandrake canon review (offline cache)"})
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=40))
            break
        except Exception as e:  # network hiccup: retry, then record it as a failure, never as a missing page
            err = e
            time.sleep(2)
    else:
        raise SystemExit(f"fetch failed for {title}: {err}")
    if "error" in d:
        return {"exists": False, "wikitext": "", "why": d["error"].get("code", "")}
    return {"exists": True, "wikitext": d["parse"]["wikitext"]["*"], "resolved": d["parse"]["title"]}


def titles():
    out = []
    for s in open(os.path.join(HERE, "LATE_SLUGS.txt")).read().split():
        t = open(os.path.join(LIB, s, "description.md"), errors="ignore").read()
        for m in re.findall(r'https?://starwars\.fandom\.com/wiki/([^\s\]>`"#?,;]+)', t):
            while m and (m[-1] in ".:" or (m[-1] == ")" and m.count("(") < m.count(")"))):
                m = m[:-1]  # prose punctuation after the URL, or the close of a markdown link
            out.append(norm(m))
    return out


def load():
    return json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}


if __name__ == "__main__":
    if sys.argv[1:2] == ["--grep"]:
        page = load()[norm(sys.argv[2])]
        for ln in page["wikitext"].splitlines():
            if re.search(sys.argv[3], ln, re.I):
                print(ln[:400])
        sys.exit(0)
    cache = load()
    xf = os.path.join(HERE, "late_wiki_extra.txt")  # titles a verifier needed beyond the entries' own links
    extra = list(dict.fromkeys((open(xf).read().splitlines() if os.path.exists(xf) else []) + [norm(a) for a in sys.argv[1:]]))
    open(xf, "w").write("".join(t + "\n" for t in extra if t))
    want = list(dict.fromkeys(titles() + extra))
    cache = {t: v for t, v in cache.items() if t in want}  # a mis-parsed title from an older run is not a page
    new = [t for t in want if t not in cache]
    for t in new:
        cache[t] = fetch(t)
        print(t, "ok" if cache[t]["exists"] else "MISSING", len(cache[t]["wikitext"]), flush=True)
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    print(f"{len(want)} titles wanted, {len(new)} fetched, {sum(1 for v in cache.values() if v['exists'])} cached pages")

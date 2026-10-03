#!/usr/bin/env python3
"""Fill EMPTY manufacturer / era / owners cells of DROIDS_INDEX.md from Wookieepedia infoboxes.

Resumable: API responses cached in /tmp/claude-1000/droid_canon_cache/, processed-row list in
cache/done.json, index checkpointed every 50 rows. Only empty cells are written. A MISSING page
marks the empty cells '?'; a page whose infobox simply lacks the field leaves the cell blank.
Pages are fetched from each row's own source URL (never a guessed title).
Usage: droid_canon_fill.py [--limit N]
"""
import argparse, json, os, re, sys, time, urllib.parse, subprocess, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.normpath(os.path.join(ROOT, "../../../design/RimStarWars/canon_references/DROIDS_INDEX.md"))
CACHE = "/tmp/claude-1000/droid_canon_cache"
API = "https://starwars.fandom.com/api.php"
COLS = {"man": 2, "era": 3, "own": 4}
_last = [0.0]


def curl(url):
    for attempt in range(6):
        wait = 0.5 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        r = subprocess.run(["curl", "-s", "--max-time", "30", "-w", "\n%{http_code}", url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        body, _, code = r.stdout.rpartition("\n")
        if code == "429" or code == "000" or not code.startswith("2"):
            time.sleep(min(60, 5 * 2 ** attempt))
            continue
        return body
    raise RuntimeError("API failing: " + url)


def cached(kind, key, url):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, kind + "_" + hashlib.md5(key.encode()).hexdigest() + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    d = json.loads(curl(url))
    # a transient API error (ratelimited, internal_api_error) must never be cached as an answer;
    # only a genuine missing page is a stable result
    if "error" in d and d["error"].get("code") != "missingtitle":
        raise RuntimeError("API error %s for %s" % (d["error"], url))
    with open(p + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh)
    os.replace(p + ".tmp", p)  # atomic: a kill mid-write cannot leave a corrupt cache file
    return d


def wikitext(title):
    d = cached("page", title, f"{API}?action=parse&page={urllib.parse.quote(title)}&format=json&prop=wikitext&redirects=1")
    if "error" in d:
        return None
    return d["parse"]["wikitext"]["*"]


def infobox(w):
    m = re.search(r"\{\{\s*(DroidSeries|Droid)\s*\n", w) or re.search(r"\{\{\s*(DroidSeries|Droid)\s*\|", w)
    if not m:
        return None
    i, depth, start = m.start(), 0, m.start()
    j = i
    while j < len(w) - 1:
        if w[j:j + 2] == "{{":
            depth += 1; j += 2
        elif w[j:j + 2] == "}}":
            depth -= 1; j += 2
            if depth == 0:
                break
        else:
            j += 1
    body = w[i + 2:j - 2]
    f, cur = {}, None
    # split on top-level pipes at line starts
    for line in body.split("\n"):
        mm = re.match(r"\|\s*(\w+)\s*=(.*)", line)
        if mm:
            cur = mm.group(1).lower(); f[cur] = mm.group(2)
        elif cur:
            f[cur] += "\n" + line
    return f


def clean(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\{\{\s*(?:C|Cite|Film|TCW|Databank)[^{}]*\}\}", "", s, flags=re.I)
    for _ in range(3):
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[(?:File|Image):[^\]]*\]\]", "", s)
    s = re.sub(r"\[\[([^\]|]*)\|([^\]]*)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"'{2,}", "", s)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return s


def items(s):
    out = []
    for line in clean(s).split("\n"):
        line = line.strip().lstrip("*").strip()
        for part in re.split(r"\s*;\s*", line):
            part = part.replace("|", "/").strip()
            if part and part not in out:
                out.append(part)
    return out


def extract(f):
    r = {}
    if "manufacturer" in f:
        v = items(f["manufacturer"])
        if v: r["man"] = "; ".join(v)
    if "affiliation" in f:
        v = items(f["affiliation"])
        if v: r["own"] = "; ".join(v)
    first = " ".join(items(f.get("firstmade", f.get("birth", "")))).strip()
    ret = " ".join(items(f.get("retired", f.get("death", "")))).strip()
    if first or ret:
        # a faction name in a date field is not a date
        if not re.search(r"\d", ret): ret = ""
        if not re.search(r"\d", first): first = ""
        e = first + (" retired " + ret if ret else "")
        if e.strip(): r["era"] = e.strip()
    return r


def probe():
    for q, want in (("R2-series astromech droid", "Industrial Automaton"),
                    ("B1 battle droid", "Baktoid Combat Automata"),
                    ("IG-86 sentinel droid", "Holowan")):
        d = cached("search", q, f"{API}?action=query&list=search&srsearch={urllib.parse.quote(q)}&format=json")
        hits = d["query"]["search"]
        ok = False
        for h in hits[:3]:
            w = wikitext(h["title"])
            f = infobox(w) if w else None
            if f and want in extract(f).get("man", ""):
                ok = True; break
        print(f"probe {q!r}: {'OK' if ok else 'FAIL'}")
        if not ok:
            sys.exit("PROBE FAILED - aborting")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=300)
    a = ap.parse_args()
    probe()
    os.makedirs(CACHE, exist_ok=True)
    dp = os.path.join(CACHE, "done.json")
    done = set(json.load(open(dp))) if os.path.exists(dp) else set()
    lines = open(INDEX, encoding="utf-8", newline="").read().split("\n")
    rows = {}
    for n, l in enumerate(lines):
        if l.startswith("| ") and l.count("|") == 9 and not l.startswith("| name |"):
            c = l[2:-2].split(" | ")
            if len(c) == 8: rows[n] = c
    todo = [n for n, c in rows.items() if c[0] not in done and any(not c[i].strip() for i in COLS.values())]
    print("rows needing work (not yet processed):", len(todo))
    filled = {k: 0 for k in COLS}; q = {k: 0 for k in COLS}
    def save():
        with open(INDEX + ".tmp", "w", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(lines))
        os.replace(INDEX + ".tmp", INDEX)
        with open(dp + ".tmp", "w", encoding="utf-8") as fh:
            json.dump(sorted(done), fh)
        os.replace(dp + ".tmp", dp)
    cnt = 0
    for n in todo[:a.limit]:
        c = rows[n]
        m = re.search(r"\[wiki\]\(([^)]*)\)", c[7])
        if m:
            title = urllib.parse.unquote(m.group(1).split("/wiki/", 1)[-1]).replace("_", " ")
            w = wikitext(title)
            if w is None:
                for k, i in COLS.items():
                    if not c[i].strip(): c[i] = "?"; q[k] += 1
            else:
                f = infobox(w)
                if f:
                    r = extract(f)
                    for k, i in COLS.items():
                        if not c[i].strip() and k in r:
                            c[i] = r[k]; filled[k] += 1
            lines[n] = "| " + " | ".join(c) + " |"
        done.add(c[0]); cnt += 1
        if cnt % 50 == 0:
            save(); print("checkpoint", cnt, filled, q, flush=True)
    save()
    print("DONE chunk", cnt, "filled", filled, "marked?", q, "remaining", len(todo) - cnt)


if __name__ == "__main__":
    main()

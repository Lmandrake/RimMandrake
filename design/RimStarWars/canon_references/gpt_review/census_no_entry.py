#!/usr/bin/env python3
"""Census of in-game RSW_/RM_ creature races with a canon name but no canon-library entry
(CANON_FAUNA_FLORA_GPT_REVIEW_1). Source of races: every ThingDef under src/ whose defName is RSW_/RM_
and that has a <race> node or an animal/insect base. A race HAS an entry when its stripped name equals a
library slug (growth suffixes Juv/Alpha/Albino etc. are not stripped: see BASE below) or its defName occurs
in any entry's description.md. The rest are asked of Wookieepedia (query API with redirects, then
action=parse wikitext of each hit): a page carrying a creature/plant/species infobox is a CANON NAME hit.
Writes CENSUS_NO_ENTRY.md and census_no_entry.json next to itself; Wookieepedia answers cached in
census_wiki_cache.json so the proof reruns offline. usage: census_no_entry.py [--refresh]"""
import glob, json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(LIB, "..", "..", ".."))
API = "https://starwars.fandom.com/api.php"
CACHE = os.path.join(HERE, "census_wiki_cache.json")
ANIMAL_BASE = re.compile(r"Animal|Insect|Wolf|Creature|BasePawn")
LIFE_SUFFIX = re.compile(r"(Juv|Juvenile|Calf|Larva|Pup|Hatchling|Alpha|Matriarch|Queen|Albino|Swimmer)$")
INFOBOX = re.compile(r"\{\{\s*(Creature|Plant|Species|Fauna|Flora|Fungus|Sentient|Lifeform)\b", re.I)

ALIASES = {"RSW_Vapaad": "vaapad"}  # donor spelling transposes the letters; the entry says so
VARIANT_OF = {"RSW_ElderSando": "sandoaquamonster", "RSW_StormSando": "sandoaquamonster", "RSW_FeralNerf": "nerf",
              "RSW_CrimsonOpee": "opeeseakiller", "RSW_ThornbackColo": "coloclawfish", "RSW_AbyssalColo": "coloclawfish"}
# Agent reading of each Wookieepedia hit against our def's own description (2026-10-31).
VERDICT = {
    "RSW_SarlaccSwimmer": ("MISSING ENTRY", "our sarlacc-mod creature is the canon sarlacc family; the library has no `sarlacc` entry at all"),
    "RM_FireHawk": ("NAME COLLISION", "canon Firehawk: rare bird of Tenoo; ours is an invented Pyrelands raptor, same word, unrelated animal"),
    "RM_FireWasp": ("NAME COLLISION", "Legends fire wasp: six-legged stinging insect; ours is an invented heatproof swarm scavenger"),
    "RM_Kirruk": ("NAME COLLISION", "Legends kirruk: domesticated reptile quadruped of Ossus; ours is an invented soarer"),
    "RM_Peeper": ("NAME COLLISION", "Legends peepers: birds of Belsavis; ours is an invented goo-margin browser"),
    "RSW_Screecher": ("NAME COLLISION", "Legends screecher: animal of Kirtania; ours is a Biomes-team-port polluted corvid, wrongly in the RSW_ tier"),
    "RSW_Basilisk": ("NAME COLLISION", "Wookieepedia Basilisk is a planet (war droid homeworld); ours is a Biomes-team-port six-legged lizard, not canon, wrongly in the RSW_ tier"),
}

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())

def races():
    out = {}
    for f in glob.glob(os.path.join(ROOT, "src/**/*.xml"), recursive=True):
        try: r = ET.parse(f).getroot()
        except Exception: continue
        if r.tag != "Defs": continue
        for t in r:
            n = t.findtext("defName")
            if t.tag != "ThingDef" or not n or t.get("Abstract") == "True": continue
            if not re.match(r"(RSW|RM)_", n): continue
            base = t.get("ParentName") or ""
            if t.find("race") is None and not ANIMAL_BASE.search(base): continue
            out.setdefault(n, {"label": t.findtext("label") or "", "file": os.path.relpath(f, ROOT), "desc": (t.findtext("description") or "")[:160]})
    return out

def api(params):
    u = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    for i in range(4):
        try: return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if i == 3: raise
            time.sleep(2 + i * 3)

def probe_titles(titles, cache):
    todo = [t for t in titles if t not in cache]
    for i in range(0, len(todo), 40):
        part = todo[i:i + 40]
        q = api({"action": "query", "titles": "|".join(part), "redirects": 1})["query"]
        fwd = {}
        for k in ("normalized", "redirects"):
            for x in q.get(k, []): fwd[x["from"]] = x["to"]
        pages = {p["title"]: p for p in q["pages"].values()}
        for t in part:
            f = t; seen = 0
            while f in fwd and seen < 5: f = fwd[f]; seen += 1
            p = pages.get(f)
            cache[t] = {"title": f, "exists": bool(p and "missing" not in p and "invalid" not in p)}
        print("probed", i + len(part), "/", len(todo), flush=True)
        json.dump(cache, open(CACHE, "w"), indent=0, sort_keys=True)

def wikitext_kind(title, cache):
    k = "parse:" + title
    if k not in cache:
        d = api({"action": "parse", "page": title, "prop": "wikitext"})
        w = d.get("parse", {}).get("wikitext", {}).get("*", "")
        m = INFOBOX.search(w)
        tmpl = re.search(r"\{\{\s*(Top|Legends|Canon|Eras)[^}]*\}\}", w)
        dis = bool(re.search(r"\{\{\s*(Disambig|Disambiguation)", w, re.I))
        cache[k] = {"infobox": m.group(1).lower() if m else None, "legends_page": title.endswith("/Legends") or "{{Top|leg" in w.replace(" ", "")[:400].lower() or "|legends" in w[:200].lower(),
                    "disambig": dis, "first": re.sub(r"\s+", " ", re.sub(r"\{\{[^}]*\}\}|\[\[File:[^\]]*\]\]", "", w))[:200]}
    return cache[k]

def main():
    cache = {} if "--refresh" in sys.argv or not os.path.exists(CACHE) else json.load(open(CACHE))
    slugs = {norm(d): d for d in os.listdir(LIB) if os.path.isfile(os.path.join(LIB, d, "description.md"))}
    blob = {d: open(os.path.join(LIB, d, "description.md"), errors="ignore").read() for d in slugs.values()}
    R = races()
    matched, rest = {}, {}
    for n, v in sorted(R.items()):
        bare = n.split("_", 1)[1]
        cands = {norm(bare), norm(LIFE_SUFFIX.sub("", bare)), norm(v["label"])}
        hit = next((slugs[c] for c in cands if c in slugs), None)
        if not hit:
            hit = next((d for d, t in blob.items() if re.search(r"\b" + re.escape(n) + r"\b", t)), None)
        hit = hit or ALIASES.get(n) or VARIANT_OF.get(n)
        if hit: matched[n] = hit
        else: rest[n] = v
    def titles_for(n, v):
        bare = LIFE_SUFFIX.sub("", n.split("_", 1)[1])
        spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", bare)
        ts = {spaced, spaced.capitalize(), bare.capitalize()}
        lab = re.sub(r"\s*\(.*?\)", "", v["label"]).strip()
        if lab: ts |= {lab.capitalize(), lab.title()}
        return sorted(t for t in ts if t)
    allt = sorted({t for n, v in rest.items() for t in titles_for(n, v)})
    probe_titles(allt, cache)
    rows = []
    for n, v in rest.items():
        best = None
        for t in titles_for(n, v):
            c = cache[t]
            if not c["exists"]: continue
            k = wikitext_kind(c["title"], cache)
            if k["infobox"] and not k["disambig"]:
                best = (c["title"], k); break
            leg = c["title"] + "/Legends"
            probe_titles([leg], cache)
            if cache[leg]["exists"]:
                k2 = wikitext_kind(cache[leg]["title"], cache)
                if k2["infobox"]: best = (cache[leg]["title"], k2); break
            best = best or (c["title"], k)
        rows.append({"defName": n, "label": v["label"], "file": v["file"], "wiki": best[0] if best else None,
                     "infobox": best[1]["infobox"] if best else None, "legends": best[1]["legends_page"] if best else None,
                     "disambig": best[1]["disambig"] if best else None})
    json.dump(cache, open(CACHE, "w"), indent=0, sort_keys=True)
    canon = [r for r in rows if r["infobox"]]
    other = [r for r in rows if r["wiki"] and not r["infobox"]]
    json.dump({"races": len(R), "matched": matched, "canon_named_no_entry": canon, "page_not_lifeform": other,
               "no_page": [r["defName"] for r in rows if not r["wiki"]]}, open(os.path.join(HERE, "census_no_entry.json"), "w"), indent=1, sort_keys=True)
    md = ["# Census: in-game creatures with a canon name and no library entry (CANON_FAUNA_FLORA_GPT_REVIEW_1)", "",
          f"Generated by `census_no_entry.py` from every RSW_/RM_ race ThingDef under `src/`. {len(R)} races; {len(matched)} joined to a library entry "
          f"(by name, label, a defName cited in an entry, or the alias/variant tables); {len(rows)} left, each asked of Wookieepedia. "
          "A fuzzy opensearch of all pageless names added nothing but people, places and ships.", "",
          "| defName | our label | Wookieepedia page | verdict | why |", "|---|---|---|---|---|"]
    for r in canon + [x for x in other if x["defName"] in VERDICT]:
        v = VERDICT.get(r["defName"], ("UNJUDGED", "new hit: read it"))
        md.append(f"| `{r['defName']}` | {r['label']} | {r['wiki']} | {v[0]} | {v[1]} |")
    md += ["", "## Same word as a canon page, but the page is no lifeform (no action)", ""]
    md += [f"- `{r['defName']}` ({r['label']}): {r['wiki']}" for r in other if r["defName"] not in VERDICT]
    md += ["", "## Variants joined to their canon base entry", ""]
    md += [f"- `{k}` -> `{v}`" for k, v in sorted(VARIANT_OF.items())]
    md += [f"", f"{len(rows) - len(canon) - len(other)} other races have no Wookieepedia page: invented names (the RM_ tier's norm) or donor names; plants are out of this census's scope.", ""]
    open(os.path.join(HERE, "CENSUS_NO_ENTRY.md"), "w").write("\n".join(md))
    print("races", len(R), "matched", len(matched), "canon", len(canon), "otherpage", len(other), "nopage", len(rows) - len(canon) - len(other))
main()

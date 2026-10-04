#!/usr/bin/env python3
"""canon_gapfill — pull Wookieepedia reference images (canon AND /Legends) for creatures our
mods ship that have no canon-library entry, or an entry with no images.

    python3 canon_gapfill.py census                 list race defs and their entry state
    python3 canon_gapfill.py run [--budget S] [--only name,...] [--max-img N]

For each base creature (juvenile / larva / pupa / spawned variants fold into the parent):
  1. resolve a Wookieepedia title by search (label and defName-derived name), accepting only an
     exact title match whose wikitext carries a creature/species infobox — a guessed title
     that returns MISSING proves nothing, so a miss is recorded as "no title match", never
     "not canon";
  2. read the canon page and the /Legends page, take infobox images first, then File: links
     from appearance sections, then any other File: link;
  3. download up to --max-img into <slug>/ as wookieepedia_<canon|legends>_<n>.<ext>, and write
     a skeleton description.md (sourced lead text + Source URLs + Candidate images with page,
     URL and caption). Visual brief / Must show are left OWED: no agent has viewed the images.
Existing entries are only ever APPENDED to (images + a Candidate images block), never rewritten.

Resumable: state in /tmp (a program reads it); report rows appended to the --report file.
Polite: ~1 s between API calls. Sanity probe: bantha must resolve with images, or the run stops.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
API = "https://starwars.fandom.com/api.php"
WIKI = "https://starwars.fandom.com/wiki/"
UA = "RimMandrake-canon-library/1.0 (personal reference research; contact lukas.mandrake@gmail.com)"
STATE = Path("/tmp/canon_gapfill_state.json")
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
VARIANT_RE = re.compile(r"(Juv|Larvae|Larva|Pupa|Spawned|Spawn|Fry|Adult)$")
SKIP_FILE_RE = re.compile(r"(\.svg|\.ogg|\.gif|\.mp4|logo|icon|symbol|Premium|cite|_map|Map\.|Galaxy_map)", re.I)
APPEAR_RE = re.compile(r"(biology|appearance\b|description|characteristics|anatomy)", re.I)

_last = [0.0]


def _get(params: dict, raw_url: str | None = None) -> bytes:
    wait = 1.0 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    url = raw_url or (API + "?" + urllib.parse.urlencode({**params, "format": "json"}))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                _last[0] = time.time()
                return r.read()
        except Exception:  # noqa: BLE001 - retry, then give up loudly
            _last[0] = time.time()
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def api(**params) -> dict:
    return json.loads(_get(params))


def norm(s: str) -> str:
    s = re.sub(r"/Legends$", "", s).lower()
    s = re.sub(r"[^a-z0-9]", "", s)
    return s[:-1] if s.endswith("s") and len(s) > 4 else s


def camel_words(dn: str) -> str:
    base = re.sub(r"^(RSW_|RUT_|RM_)", "", dn)
    base = re.sub(r"Race$", "", base)
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", base).strip()


def slug_for(label: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", re.sub(r"^(rsw|rut|rm|aa|a)_", "", label.strip().lower()).replace(" ", ""))


# ──────────────────────────────────────────────────────────── census ──

def census() -> list[dict]:
    sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
    import art_sheet as S  # the sheet's own matcher: what it finds is what the owner sees
    rows = {}
    for p in (REPO / "src/RimStarWars").rglob("*.xml"):
        if "/Defs/" not in str(p):
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for td in root.iter("ThingDef"):
            if td.get("Abstract", "").lower() == "true":
                continue
            dn, race = td.findtext("defName"), td.find("race")
            if not dn or race is None or race.findtext("intelligence") == "Humanlike":
                continue
            rows[dn] = {"defName": dn, "label": (td.findtext("label") or "").strip(),
                        "file": str(p.relative_to(REPO))}
    out = []
    for dn, r in sorted(rows.items()):
        ce = S.canon_entry(r["label"], dn)
        r["entry"] = ce.get("key")
        r["nimg"] = len(ce.get("images", [])) if ce else 0
        out.append(r)
    return out


def base_creatures(rows: list[dict]) -> list[dict]:
    """Fold variants into their parent defName; keep the parent's label."""
    by = {r["defName"]: r for r in rows}
    groups: dict[str, dict] = {}
    for r in rows:
        dn = r["defName"]
        parent = VARIANT_RE.sub("", dn)
        parent = re.sub(r"Alpha$|^RSW_Alpha|Queen$", "", parent) if parent not in by else parent
        key = parent if parent in by else dn
        g = groups.setdefault(key, {**by.get(key, r), "variants": []})
        if dn != key:
            g["variants"].append(dn)
    return list(groups.values())


# ─────────────────────────────────────────────────────────── wiki ──

def wikitext(title: str) -> tuple[str, str] | None:
    try:
        d = api(action="parse", page=title, prop="wikitext", redirects=1)
    except Exception:  # noqa: BLE001
        return None
    if "parse" not in d:
        return None
    return d["parse"]["title"], d["parse"]["wikitext"]["*"]


def is_creature(wt: str) -> bool:
    return bool(re.search(r"\{\{\s*(Species|Creature|Fauna)\b", wt[:4000], re.I))


def resolve(names: list[str]) -> dict:
    """{'canon': (title, wt) | None, 'legends': (title, wt) | None, 'tried': [...]}"""
    tried, found = [], {"canon": None, "legends": None}
    for n in dict.fromkeys(x for x in names if x):
        tried.append(n)
        try:
            hits = [h["title"] for h in api(action="query", list="search", srsearch=n, srlimit=10)["query"]["search"]]
        except Exception:  # noqa: BLE001
            continue
        want = norm(n)
        for t in hits:
            if norm(t) != want:
                continue
            slot = "legends" if t.endswith("/Legends") else "canon"
            if found[slot]:
                continue
            got = wikitext(t)
            if got and is_creature(got[1]):
                found[slot] = got
        # an exact canon title implies a possible /Legends sibling the search did not rank
        for slot, sfx in (("legends", "/Legends"),):
            if found["canon"] and not found[slot]:
                got = wikitext(found["canon"][0] + sfx)
                if got and is_creature(got[1]):
                    found[slot] = got
        if found["canon"] or found["legends"]:
            break
    found["tried"] = tried
    return found


def strip_wiki(s: str) -> str:
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    for _ in range(3):
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[(?:File|Image):[^\[\]]*(?:\[\[[^\]]*\]\][^\[\]]*)*\]\]", "", s)
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"'''?", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def sections(wt: str) -> list[tuple[str, str]]:
    parts = re.split(r"^(==+[^=\n]+==+)\s*$", wt, flags=re.M)
    out = [("lead", parts[0])]
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip("= ").strip(), parts[i + 1] if i + 1 < len(parts) else ""))
    return out


def images_in(wt: str) -> list[dict]:
    """Ordered candidate images: infobox first, then appearance sections, then the rest."""
    seen, out = set(), []

    def add(name: str, cap: str, rank: int):
        name = name.strip().replace("_", " ")
        if not name or name in seen or SKIP_FILE_RE.search(name) or not name.lower().endswith(IMG_EXT):
            return
        seen.add(name)
        out.append({"file": name, "caption": strip_wiki(cap)[:200], "rank": rank})

    m = re.search(r"\|\s*image\s*=\s*(.*)", wt[:5000])
    if m:
        for f in re.findall(r"(?:File|Image):([^|\]]+)", m.group(1)):
            add(f, "infobox image", 0)
    for sec, body in sections(wt):
        rank = 1 if APPEAR_RE.search(sec) or sec == "lead" else (3 if re.search(r"behind|appearances|sources|notes", sec, re.I) else 2)
        for fm in re.finditer(r"\[\[(?:File|Image):([^|\]]+)((?:\|[^\[\]]*(?:\[\[[^\]]*\]\][^\[\]]*)*)*)\]\]", body):
            opts = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", fm.group(2) or "")
            cap = opts.split("|")[-1] if opts else ""
            if re.fullmatch(r"\s*(thumb|left|right|\d+px|upright.*)\s*", cap or ""):
                cap = ""
            add(fm.group(1), cap, rank)
        for gm in re.finditer(r"<gallery[^>]*>(.*?)</gallery>", body, re.S):
            for line in gm.group(1).splitlines():
                if "|" in line or line.strip():
                    f, _, cap = line.partition("|")
                    add(re.sub(r"^(File|Image):", "", f.strip()), cap, rank + 1)
    return sorted(out, key=lambda x: x["rank"])


def image_url(name: str) -> str | None:
    d = api(action="query", titles="File:" + name, prop="imageinfo", iiprop="url|size")
    for p in d.get("query", {}).get("pages", {}).values():
        ii = p.get("imageinfo")
        if ii:
            return ii[0]["url"]
    return None


# ─────────────────────────────────────────────────────────── entry ──

def lead_text(title: str, wt: str) -> str:
    keep = []
    for sec, body in sections(wt):
        if sec == "lead" or APPEAR_RE.search(sec):
            t = strip_wiki(body)
            if t:
                keep.append((f"**{sec}** " if sec != "lead" else "") + t)
    txt = "\n\n".join(keep)
    return (txt[:2400] + " …[truncated by script; rest UNREAD here, not absent]") if len(txt) > 2400 else txt


def fetch_images(found: dict, d: Path, max_img: int) -> list[dict]:
    pools = []
    for slot in ("canon", "legends"):
        if found.get(slot):
            title, wt = found[slot]
            pools.append([{**c, "slot": slot, "page": title} for c in images_in(wt)])
    # interleave so both canon and Legends get represented, best-ranked first
    order, i = [], 0
    while any(i < len(p) for p in pools):
        for p in pools:
            if i < len(p):
                order.append(p[i])
        i += 1
    order.sort(key=lambda c: c["rank"])
    got, seen_urls = [], set()
    existing = {p.name for p in d.iterdir()} if d.exists() else set()
    for c in order:
        if len(got) >= max_img:
            break
        try:
            url = image_url(c["file"])
        except Exception:  # noqa: BLE001
            continue
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        ext = Path(c["file"]).suffix.lower()  # the URL ends /revision/latest: take the file name's
        ext = ".jpg" if ext == ".jpeg" else ext
        n = 1
        while any(x.startswith(f"wookieepedia_{c['slot']}_{n}.") for x in existing):
            n += 1
        try:
            b = _get({}, raw_url=url)
        except Exception:  # noqa: BLE001
            continue
        if len(b) < 2000:
            continue
        # the CDN serves WebP whatever the file is named: name the file by its real bytes
        ext = ".webp" if b[:4] == b"RIFF" and b[8:12] == b"WEBP" else ".png" if b[:4] == b"\x89PNG" else ext
        fname = f"wookieepedia_{c['slot']}_{n}{ext}"
        d.mkdir(parents=True, exist_ok=True)
        (d / fname).write_bytes(b)
        existing.add(fname)
        got.append({**c, "url": url, "saved": fname})
    return got


def cand_lines(got: list[dict]) -> str:
    out = []
    for g in got:
        lab = "CANON page" if g["slot"] == "canon" else "LEGENDS page (non-canon continuity)"
        cap = g["caption"] or "(no caption on the page)"
        out.append(f"- `{g['saved']}` — {lab} `{g['page']}`; wiki caption: {cap}. "
                   f"File: `{g['file']}` — {g['url']}")
    return "\n".join(out)


def write_new_entry(cr: dict, d: Path, found: dict, got: list[dict]) -> None:
    name = (found.get("canon") or found.get("legends"))[0].replace("/Legends", "")
    dn = cr["defName"] + (" (variants: " + ", ".join(f"`{v}`" for v in cr["variants"]) + ")" if cr["variants"] else "")
    src, urls = [], []
    for slot in ("canon", "legends"):
        if found.get(slot):
            t, wt = found[slot]
            u = WIKI + urllib.parse.quote(t.replace(" ", "_"))
            urls.append(f"- {u} ({'canon' if slot == 'canon' else 'Legends'}; wikitext pulled via the API {time.strftime('%Y-%m-%d')})")
            src.append(f"### {'Canon' if slot == 'canon' else 'Legends'} — {u}\n\n{lead_text(t, wt)}")
    body = f"""# {name}

**defName**: `{cr['defName']}` — in-repo label "{cr['label']}"; {dn.split(' ', 1)[1] if cr['variants'] else 'no variants'}

> Skeleton entry written by `canon_gapfill.py` on {time.strftime('%Y-%m-%d')}: sourced text is the page lead
> and appearance sections, mechanically stripped of markup. Images are downloaded and captioned
> from the pages, but **no agent has viewed them yet** — the visual brief is owed.

## Sourced text (Wookieepedia)
{chr(10).join(src)}

## Visual brief
OWED — images pulled 2026-10-04, not yet viewed. On appearance, trust the images over the prose;
images from the Legends page are Legends continuity and say so in their caption below.

## Must show
(owed — distil from the visual brief once it is written; add no claim the brief does not make)

## Engine limits
not yet assessed

## Source URLs
{chr(10).join(urls)}

## Candidate images
{cand_lines(got) if got else '(none downloadable from either page)'}

## ruling
(empty — owner has not reviewed this creature yet)
"""
    d.mkdir(parents=True, exist_ok=True)
    (d / "description.md").write_text(body)


def append_existing(d: Path, got: list[dict]) -> None:
    p = d / "description.md"
    txt = p.read_text()
    block = f"\n### Added {time.strftime('%Y-%m-%d')} by canon_gapfill.py (not yet viewed)\n{cand_lines(got)}\n"
    m = re.search(r"^## ruling", txt, re.M)
    txt = txt[:m.start()] + block.lstrip("\n") + "\n" + txt[m.start():] if m else txt + block
    p.write_text(txt)


# ───────────────────────────────────────────────────────────── run ──

def process(cr: dict, max_img: int, force_slug: str | None = None) -> dict:
    names = [cr["label"], camel_words(cr["defName"])]
    found = resolve(names)
    rec = {"defName": cr["defName"], "label": cr["label"], "entry_before": cr["entry"],
           "img_before": cr["nimg"], "tried": found["tried"],
           "canon": found["canon"][0] if found["canon"] else None,
           "legends": found["legends"][0] if found["legends"] else None}
    if not (found["canon"] or found["legends"]):
        rec.update(status="no title match", img_after=cr["nimg"])
        return rec
    slug = cr["entry"] or force_slug or slug_for(cr["label"])
    d = HERE / slug
    got = fetch_images(found, d, max_img)
    if cr["entry"]:
        if got:
            append_existing(d, got)
    else:
        write_new_entry(cr, d, found, got)
    rec.update(status="filled" if got else "page found, no usable image", slug=slug,
               img_after=cr["nimg"] + len(got), slots=sorted({g["slot"] for g in got}))
    return rec


def report_row(r: dict) -> str:
    src = []
    if r.get("canon"):
        src.append(f"canon `{r['canon']}`")
    if r.get("legends"):
        src.append(f"Legends `{r['legends']}`")
    note = r["status"] if r["status"] != "no title match" else "no exact Wookieepedia title for: " + ", ".join(r["tried"])
    return (f"| {r['label']} | `{r['defName']}` | {r['entry_before'] or '—'} | {r['img_before']} → {r['img_after']} | "
            f"{'; '.join(src) or '—'} | {note} |\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["census", "run"])
    ap.add_argument("--budget", type=int, default=480)
    ap.add_argument("--only", default="")
    ap.add_argument("--max-img", type=int, default=4)
    ap.add_argument("--report", default=str(REPO / "Transient/canon_image_gapfill_2026-10-04.md"))
    a = ap.parse_args()
    rows = census()
    if a.verb == "census":
        for r in rows:
            print(f"{r['defName']}\t{r['label']}\t{r['entry'] or '-'}\t{r['nimg']}")
        print(f"{len(rows)} race defs; {sum(1 for r in rows if not r['entry'])} without an entry; "
              f"{sum(1 for r in rows if r['entry'] and not r['nimg'])} entries without images")
        return 0
    st = json.loads(STATE.read_text()) if STATE.exists() else {"done": {}}
    if "probe" not in st:  # sanity probe: an instrument that finds nothing must first prove it can find something
        pr = resolve(["bantha"])
        n = len(images_in(pr["canon"][1])) if pr["canon"] else 0
        print(f"SANITY PROBE bantha: canon={pr['canon'][0] if pr['canon'] else None} "
              f"legends={pr['legends'][0] if pr['legends'] else None} candidate images={n}", flush=True)
        if not pr["canon"] or n == 0:
            print("PROBE FAILED — instrument cannot see a known subject; stopping", flush=True)
            return 2
        st["probe"] = n
    todo = [c for c in base_creatures(rows) if not c["entry"] or c["nimg"] == 0]
    if a.only:
        want = {x.strip() for x in a.only.split(",")}
        todo = [c for c in todo if c["defName"] in want or c["label"] in want]
    t0 = time.time()
    for c in todo:
        if c["defName"] in st["done"]:
            continue
        if time.time() - t0 > a.budget:
            print("BUDGET REACHED", flush=True)
            STATE.write_text(json.dumps(st))
            return 3
        r = process(c, a.max_img)
        st["done"][c["defName"]] = r
        STATE.write_text(json.dumps(st))
        with open(a.report, "a") as fh:
            fh.write(report_row(r))
        print(f"{r['status']:>28}  {c['defName']}  {r['img_before']}->{r['img_after']}  "
              f"canon={r['canon']} legends={r['legends']}", flush=True)
    left = [c["defName"] for c in todo if c["defName"] not in st["done"]]
    print(f"DONE {len(todo) - len(left)}/{len(todo)}  (probe bantha candidate images={st['probe']})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

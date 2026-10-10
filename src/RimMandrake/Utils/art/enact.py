#!/usr/bin/env python3
"""enact.py — `art.py enact <decisions.json>`: carry out a ruled review sheet in ONE pass.

Owner, 2026-10-08: "after a successful art review sheet, I often will say very clearly, delete these things,
accept these things, regenerate these things, and cut this animal from the biome ... What is taking so long?"
(Transient/art_pipeline_latency_2026-10-08.md §B5, fixes F3 + F5.)

    art.py enact <decisions.json> [--apply] [--hold <subject>]... [--mark-done <row>]... [--no-deploy]

Without --apply it is a DRY RUN: the full plan is printed and nothing changes. Steps, in order:

  1 INGEST    the sheet's rulings into the art ledger (ingest.py; content-idempotent, repo-relative `via`).
              The ✕ purges are NOT run by ingest (it would release keeps) — step 4 does them.
  2 INSTALL   every keep/pick: per-graphic picks win over the row pick; a `_byname` column on a row with
              several graphics is ambiguous and becomes a CONFLICT. Each facing goes to the slot the ledger
              says is live for that texPath (any of our mods shipping it). A slot that is not ours (donor art
              IN GAME) is left alone. A render picked for a graphic no slot of ours ships goes to OUR path: into a
              Graphic_Random folder of ours as <base>_<letter>.png, or — when the row's def texPaths donor art —
              to <category>/<row>/<row> in that def's mod with the def's texPath moved there (never "already live").
              Variants he TICKED (not the default tick) ship too: folder files, or <res>V_<L> + alternateGraphics.
              A folder this run fills sheds the pictures he did not keep (retired: archived in the store). Anything
              with nowhere to go is a TODO. Authorised by the sheet's keep ruling.
  3 QUEUE     every `redo` row via fill_queue.py at priority 0 (ruled work first), his note verbatim as
              owner_note, the picked/in-game column as canon_reference. A row whose job already exists (its
              note verbatim, or the same target_def filed after his click) is reported, never re-filed. A FAILED
              job is re-filed (failed/ -> pending/, manifest parked in _requeued_manifests/, at most
              REFILE_CAP times) unless the same id has since run or a later job of the row covers its facing; a
              DONE render that is neither live nor purged/rejected is listed as AWAITING OWNER PICK — a row is
              "already handled" only when every job is pending/active or its render shipped or was rejected.
              Reference: "based on (b)" -> column b; a note dropping the art (or a ✕) -> none; else the in-game
              picture. A note that also asks for a rename/description stays OPEN (TODO) until --mark-done records
              the def half — an art job alone never "follows" it. A catch row (RM_XCatch) is not filed while RM_X is
              being redrawn; catch jobs drawn before RM_X was settled are withdrawn (artpipe _withdrawn/), and once
              RM_X is picked the catch is filed with RM_X's picture as its reference.
  4 PURGE     every ✕ except protected pictures — live in a mod, owner-kept, or the row's own pick/variants.
              Those are listed as CONFLICTS, one line each, and are never deleted. A ✕ on a picture of the row's OWN
              pick/variant column wins for that picture (it is neither installed nor kept), and a keep that this same
              row of this same file recorded is released by the purge rather than blocking it.
  5 CUT       a row whose decision is `cut`, or `hold` with a note saying cut / not needed, is removed from
              THIS sheet's biome only (inline BiomeDef rosters and every PatchOperation whose own xpath targets
              it, read as XML elements). Our own defs are then deleted with the products/eggs/meat they alone
              use, and their textures retired through the ledger — only when NOTHING else in src/ names them.
              Donor defs are never touched (their roster row is ours; anything more needs a patch: TODO).
  6 TODO      a note on a row that is not a redo and has no queued job is NOT guessed at: it is a TODO line,
              until `--mark-done <row> [--evidence <sha>]` records it as done (an `enact_done` ledger event;
              written even on a dry run, because it records work already done by hand). Evidence starting
              "OWNER:" records the rest of the note as a question for him: it is listed as a CONFLICT.
  7 DEPLOY    only the touched mods (`deploy_custom_mods.py --apply --mod <m>`, or `--compose biomes` for a
              folded biome mod). A plan that would write a DLL while RimWorldWin64 runs is skipped and said so.
  8 SUMMARY   counts per action, CONFLICTS, TODOs; art is visible after the next game restart.

Idempotent: every step compares against the current state, so a second run after success is a no-op.
--hold <subject> (repeatable, case-insensitive substring of the row key) skips those rows in every step.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import ingest as I  # noqa: E402

WRITER_TAG = "script:src/RimMandrake/Utils/art/enact.py"
CUT_NOTE = re.compile(r"\bcut\b|\bno longer needed\b|\bnot needed\b|\bremove (it|this|them) from\b", re.I)
# a note that also asks for a DEF edit (name / description): an art job carries only the picture, so such a note is not
# "followed" until --mark-done records the def half (Weeping Stones 2026-10-10: 9 renames/descriptions dropped silently)
DEF_ASK = re.compile(r"\b(re-?nam(e|ed|ing)|call (it|them)|descriptions?|describe)\b", re.I)
# a note that rejects the art in front of him: the row's in-game picture must not ride along as the redraw's reference
DROP_ART = re.compile(r"\b(drop|remove|lose|ditch|scrap)\b[^.]{0,40}\bart\b|\bredo (it )?completely\b"
                      r"|\btotal regen\b|\bstart (over|fresh)\b", re.I)
# "based on (b)" / "based on the current (b)": the column he named IS the reference
BASED_ON = re.compile(r"\b(?:based on|starting from|working from)\s+(?:the\s+)?(?:current\s+)?\(([a-zA-Z])\)", re.I)
CATCH_SUFFIX = "Catch"      # RM_HulduCatch is the catch of RM_Huldu: drawn from it, so filed only once it is settled
FACING_PREF = ("east", "south", "north", "single", "west")
LISTS = ("wildAnimals", "wildPlants", "fishTypes")
DEF_TYPES_WITH_ART = ("graphicData", "bodyGraphicData", "dessicatedBodyGraphicData", "femaleGraphicData")


# ───────────────────────────────────────────────────────────── helpers ──

def artpipe_dirs() -> dict:
    env = os.environ.get("ENACT_ARTPIPE_ROOT")
    if env:
        r = Path(env)
        return {k: r / k for k in ("pending", "active", "done", "failed")}
    sys.path.insert(0, str(HERE.parent / "artpipe"))
    import common as C  # noqa: E402
    return {"pending": C.DEFAULT_PENDING, "active": C.DEFAULT_ACTIVE, "done": C.DEFAULT_DONE,
            "failed": C.DEFAULT_FAILED}


REFILE_CAP = 3  # parked manifests per job id — same cap as requeue_flakes.py --max


def artpipe_aux() -> dict:
    """The state dir's _artsrc/ (finished renders), _requeued_manifests/ (re-file history), _withdrawn/ (jobs taken
    back: never rendered, re-filed or installed)."""
    root = artpipe_dirs()["failed"].parent
    return {"artsrc": root / "_artsrc", "parked": root / "_requeued_manifests", "withdrawn": root / "_withdrawn"}


def withdrawn_ids() -> set:
    d = artpipe_aux()["withdrawn"]
    return {f.stem for f in d.glob("*.json") if not f.name.endswith(".manifest.json")} if d.is_dir() else set()


def withdraw(j: dict, reason: str) -> None:
    """<state>/<id>.json -> _withdrawn/<id>.json with why; its manifest moves with it. An ACTIVE job is the daemon's
    and is never moved (the caller lists it instead)."""
    d, aux = artpipe_dirs(), artpipe_aux()
    src = d[j["_state"]] / f"{j['id']}.json"
    aux["withdrawn"].mkdir(parents=True, exist_ok=True)
    body = json.loads(src.read_text())
    body.update(withdrawn_reason=reason, withdrawn_from=j["_state"],
                withdrawn_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), withdrawn_by=WRITER_TAG)
    dst = aux["withdrawn"] / src.name
    dst.write_text(json.dumps(body, indent=1))
    man = d[j["_state"]] / f"{j['id']}.manifest.json"
    if man.exists():
        man.rename(aux["withdrawn"] / man.name)
    src.unlink()


def job_render_sha(j: dict) -> str | None:
    """sha256 of a done job's PNG in _artsrc/<id>/<id>.png (None when absent)."""
    f = artpipe_aux()["artsrc"] / j["id"] / f"{j['id']}.png"
    try:
        return L.sha256_file(f)
    except OSError:
        return None


def times_refiled(jid: str) -> int:
    d = artpipe_aux()["parked"]
    return len(list(d.glob(f"{jid}.manifest*.json"))) if d.is_dir() else 0


def job_defs(j: dict) -> set:
    """Every def a job is a picture of: target_def, and the originals fill_queue mapped away from (a row ruled
    under RSW_Ultracactus files a job whose target_def is our RM_UltrissPad, target_original the ruled name)."""
    orig = j.get("target_original") or []
    if isinstance(orig, str):
        orig = [x for x in re.split(r"[;,]", orig) if x.strip()]
    return {d.strip() for d in [j.get("target_def") or "", *orig] if d and d.strip()}


def classify_jobs(match: list[dict], jobs: list[dict], idx: L.Index) -> dict:
    """Sort a row's matching jobs: live (pending/active), shipped/rejected done renders, renders AWAITING a pick,
    and failed jobs to RE-FILE (or over the cap). A failed job is covered when its id has since run again, or any
    other job of the same target_def and facing was filed strictly later (the newer ask supersedes it)."""
    out = {"live": [], "handled": [], "awaiting": [], "refile": [], "capped": []}
    alive_ids = {j["id"] for j in jobs if j["_state"] != "failed"}
    for j in match:
        st = j["_state"]
        if st in ("pending", "active"):
            out["live"].append(j)
        elif st == "done":
            sha = job_render_sha(j)
            if sha and (idx.live_anywhere(sha) or idx.is_purged(sha) or idx.rejection(sha)):
                out["handled"].append(j)
            else:
                out["awaiting"].append(j)
        elif st == "failed":
            if j["id"] in alive_ids:
                continue
            c = str(j.get("created") or "")
            if any(k["id"] != j["id"] and job_defs(k) & job_defs(j)
                   and k.get("facing") == j.get("facing") and str(k.get("created") or "") > c for k in jobs):
                continue
            (out["capped"] if times_refiled(j["id"]) >= REFILE_CAP else out["refile"]).append(j)
    return out


def refile(j: dict) -> None:
    """failed/<id>.json -> pending/<id>.json; its manifest parked (requeue_flakes.py's move)."""
    d, aux = artpipe_dirs(), artpipe_aux()
    src = d["failed"] / f"{j['id']}.json"
    man = d["failed"] / f"{j['id']}.manifest.json"
    aux["parked"].mkdir(parents=True, exist_ok=True)
    if man.exists():
        man.rename(aux["parked"] / f"{j['id']}.manifest.{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json")
    src.rename(d["pending"] / src.name)


def load_jobs() -> list[dict]:
    out = []
    for state, d in artpipe_dirs().items():
        if not d.is_dir():
            continue
        for f in d.glob("*.json"):
            if f.name.endswith(".manifest.json"):
                continue
            try:
                j = json.loads(f.read_text())
            except (OSError, ValueError):
                continue
            if isinstance(j, dict):
                j["_state"] = state
                out.append(j)
    return out


def rel_for(graphic: str, facing: str) -> str:
    """Snapshot column key -> the file under Textures/ it stands for."""
    if graphic.startswith("_flip:"):
        return f"{graphic[6:]}{facing}.png"
    if facing == "single":
        return f"{graphic}.png"
    return f"{graphic}_{facing}.png"


def slots_for(idx: L.Index, rel: str) -> list[tuple[str, str, str]]:
    """Every (mod, rel, live sha) of OURS shipping exactly this file."""
    return [(m, r, ev["sha"]) for (m, r), ev in idx.live.items() if r == rel and ev.get("sha")]


_TEXPATHS: dict = {}


def src_texpaths(src) -> set:
    """Every <texPath> any XML under src/ names (cached per src root; one grep, not a python walk)."""
    key = str(src)
    if key not in _TEXPATHS:
        import subprocess
        out = subprocess.run(["grep", "-rhoE", "--include=*.xml", r"<texPath>[^<]+</texPath>", key],
                             capture_output=True, text=True).stdout
        _TEXPATHS[key] = {re.sub(r"</?texPath>", "", ln).strip() for ln in out.splitlines()}
    return _TEXPATHS[key]


def def_points_at(src, rel: str) -> bool:
    """A def of ours already names this file (minus its facing suffix) as a texPath: donor art that is live."""
    base = re.sub(r"(_(east|north|south|west))?\.png$", "", rel)
    return base in src_texpaths(src)


_DEFS: dict = {}


def our_defs_cached(src) -> dict:
    key = str(src)
    if key not in _DEFS:
        _DEFS[key] = our_defs(Path(src))
    return _DEFS[key]


def reset_caches() -> None:
    _TEXPATHS.clear()
    _DEFS.clear()


def defs_naming(src, names: set, texpath: str) -> list[dict]:
    """Our def blocks (one of `names`) that name `texpath` as a <texPath>."""
    pat = re.compile(r"<texPath>\s*" + re.escape(texpath) + r"\s*</texPath>")
    defs = our_defs_cached(src)
    return [dict(ent, defName=n) for n in sorted(names) for ent in defs.get(n, []) if pat.search(ent["text"])]


def folder_slots(idx: L.Index, g: str) -> list[tuple[str, str, str]]:
    """Every live (mod, rel, sha) of ours INSIDE the folder `g` (a Graphic_Random texPath: Things/Plant/RM_X/*.png)."""
    return [(m, r, ev["sha"]) for (m, r), ev in idx.live.items() if r.startswith(g + "/") and ev.get("sha")]


def own_slot(idx: L.Index, src, g: str, facing: str, letter: str, row: str, names: set,
             variant: bool = False) -> dict | None:
    """Where a picked/variant picture of ours goes when no slot of ours ships `g` at this facing:
      folder  — `g` is a Graphic_Random folder of ours: <g>/<base>_<letter>.png beside the pictures already there;
      rebind  — a def of ours (the row's) texPaths DONOR art at `g`: the picture goes to our own path
                <g's category>/<row>/<row>[V_<letter>] in that def's mod, and the def's texPath is moved to it.
    Variant of a multi-facing graphic: <g>V_<letter>_<facing>.png, wired as an alternateGraphics entry (the GorgV_G
    convention). None: nowhere to put it (TODO)."""
    fs = folder_slots(idx, g)
    if fs and facing == "single":
        return {"mod": fs[0][0], "rel": f"{g}/{g.rsplit('/', 1)[-1]}_{letter.lower()}.png", "kind": "folder", "graphic": g}
    if variant and facing != "single":
        base_slots = slots_for(idx, rel_for(g, facing)) or slots_for(idx, rel_for(g, "east"))
        if base_slots:
            res = f"{g}V_{letter}"
            return {"mod": base_slots[0][0], "rel": rel_for(res, facing), "kind": "alt", "graphic": g, "res": res}
    if g.count("/") < 2:
        return None
    hits = defs_naming(src, names, g)
    if not hits:
        return None
    new_res = "/".join(g.split("/")[:-2] + [row, row])
    if variant:
        if facing == "single":
            return None
        res = f"{new_res}V_{letter}"
        return {"mod": mod_of(hits[0]["file"]), "rel": rel_for(res, facing), "kind": "alt", "graphic": new_res,
                "res": res, "rebind": {"old": g, "new": new_res}}
    return {"mod": mod_of(hits[0]["file"]), "rel": rel_for(new_res, facing), "kind": "rebind", "graphic": g,
            "rebind": {"old": g, "new": new_res}}


def rebind_defs(src, names: set, old: str, new: str) -> list[Path]:
    """Move every <texPath>old</texPath> inside our defs named `names` to `new`. A placeholder <color> tint in that same
    graphic block (a vanilla animal recoloured to stand in for ours) is dropped: our own painted art draws untinted."""
    touched = []
    hits = defs_naming(src, names, old)
    by_file: dict = {}
    for h in hits:
        by_file.setdefault(h["file"], []).append(h["span"])
    for f, spans in by_file.items():
        text = f.read_text(encoding="utf-8")
        for s, e in sorted(spans, key=lambda x: -x[0]):
            body = text[s:e]
            out, pos = [], 0
            for d, tag, bs, be in element_spans(body):
                if tag not in DEF_TYPES_WITH_ART or bs < pos:
                    continue
                blk = body[bs:be]
                if not re.search(r"<texPath>\s*" + re.escape(old) + r"\s*</texPath>", blk):
                    continue
                blk2 = re.sub(r"<texPath>\s*" + re.escape(old) + r"\s*</texPath>", f"<texPath>{new}</texPath>", blk)
                blk2 = re.sub(r"\n[ \t]*<color>[^<]*</color>[ \t]*(?=\n)", "", blk2)
                out.append(body[pos:bs] + blk2)
                pos = be
            out.append(body[pos:])
            text = text[:s] + "".join(out) + text[e:]
        f.write_text(text, encoding="utf-8")
        touched.append(f)
    reset_caches()
    return touched


def add_alternate_graphic(src, names: set, base_texpath: str, alt_texpath: str) -> list[Path]:
    """Add <alternateGraphics><li><texPath>alt</texPath></li> to our PawnKindDef(s) in `names` whose body texPath is
    `base_texpath`; alternateGraphicChance becomes n/(n+1) so base + n variants are equally likely. Idempotent."""
    touched = []
    defs = our_defs_cached(src)
    pat = re.compile(r"<texPath>\s*" + re.escape(base_texpath) + r"\s*</texPath>")
    for n in sorted(names):
        for ent in defs.get(n, []):
            if ent["tag"] != "PawnKindDef" or not pat.search(ent["text"]):
                continue
            f = ent["file"]
            text = f.read_text(encoding="utf-8")
            s, e = ent["span"]
            body = text[s:e]
            if re.search(r"<texPath>\s*" + re.escape(alt_texpath) + r"\s*</texPath>", body):
                continue
            ind = re.search(r"\n([ \t]*)<defName>", body)
            ind = ind.group(1) if ind else "    "
            li = f"{ind}  <li>\n{ind}    <texPath>{alt_texpath}</texPath>\n{ind}  </li>\n"
            if "</alternateGraphics>" in body:
                body = re.sub(r"([ \t]*)</alternateGraphics>", lambda m: li + m.group(0), body, count=1)
            else:
                anchor = re.search(r"<race>[^<]*</race>[^\n]*\n", body) or re.search(r"<defName>[^<]*</defName>[^\n]*\n", body)
                body = (body[:anchor.end()] + f"{ind}<alternateGraphicChance>0</alternateGraphicChance>\n"
                        f"{ind}<alternateGraphics>\n{li}{ind}</alternateGraphics>\n" + body[anchor.end():])
            n_alt = len(re.findall(r"<li>\s*<texPath>", body[body.find("<alternateGraphics>"):body.find("</alternateGraphics>")]))
            chance = round(n_alt / (n_alt + 1), 3)
            if "<alternateGraphicChance>" in body:
                body = re.sub(r"<alternateGraphicChance>[^<]*</alternateGraphicChance>",
                              f"<alternateGraphicChance>{chance}</alternateGraphicChance>", body, count=1)
            f.write_text(text[:s] + body + text[e:], encoding="utf-8")
            touched.append(f)
            reset_caches()
            defs = our_defs_cached(src)
    return touched


def first_by_facing(col: dict, skip=()) -> str | None:
    for f in FACING_PREF:
        s = (col or {}).get(f)
        if s and s not in skip:
            return s
    return None


def is_held(row: str, holds) -> bool:
    rl = row.lower()
    return any(h.lower() in rl for h in holds)


def row_names(row: str, v: dict, census_rows: dict) -> set[str]:
    names = {row}
    if v.get("carriedFrom"):
        names.add(v["carriedFrom"])
    for k in list(names):
        names |= set((census_rows.get(k) or {}).get("defNames") or [])
        names |= set((census_rows.get(k) or {}).get("donors") or [])
    return names


def census_rows_for(biome: str) -> dict:
    p = Path(os.environ.get("ENACT_CENSUS") or L.REPO_ROOT / "Transient" / "biome_ffar" / "census.json")
    try:
        c = json.loads(p.read_text())
    except (OSError, ValueError):
        return {}
    return {r["key"]: r for r in ((c.get("biomes") or {}).get(biome) or {}).get("rows") or []}


# ───────────────────────────────────────── XML: element spans by text ──

TAG_RE = re.compile(r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<\?.*?\?>|<(/?)([A-Za-z_][\w.\-]*)([^>]*?)(/?)>", re.S)


def element_spans(text: str):
    """[(depth, tag, start, end)] for every element, end exclusive, by a tag tokenizer (keeps formatting)."""
    out, stack = [], []
    for m in TAG_RE.finditer(text):
        if m.group(2) is None:
            continue
        close, tag, _attrs, selfclose = m.group(1), m.group(2), m.group(3), m.group(4)
        if close:
            while stack:
                t, s = stack.pop()
                if t == tag:
                    out.append((len(stack), tag, s, m.end()))
                    break
        elif selfclose:
            out.append((len(stack), tag, m.start(), m.end()))
        else:
            stack.append((tag, m.start()))
    return out


def line_extent(text: str, s: int, e: int) -> tuple[int, int]:
    """Widen [s,e) to whole lines when the span sits alone on them."""
    ls = text.rfind("\n", 0, s) + 1
    le = text.find("\n", e)
    le = len(text) if le < 0 else le + 1
    if text[ls:s].strip() == "" and text[e:le].strip() == "":
        return ls, le
    return s, e


def remove_entry_lines(text: str, region: tuple[int, int], name: str) -> tuple[str, int]:
    """Remove `<name ...>c</name>` lines (with a trailing comment) inside region. -> (text, removed)."""
    s, e = region
    pat = re.compile(r"^[ \t]*<" + re.escape(name) + r"(\s[^>]*)?>[^<]*</" + re.escape(name)
                     + r">[ \t]*(<!--.*?-->)?[ \t]*\r?\n", re.M)
    seg = text[s:e]
    seg2, n = pat.subn("", seg)
    return text[:s] + seg2 + text[e:], n


# ───────────────────────────────────────────────────────────── rosters ──

def roster_sites(src: Path, biome: str, names: set[str]) -> list[dict]:
    """Every place in src/ that puts one of `names` on `biome`'s roster: inline in the BiomeDef, or the
    <value> of a PatchOperation whose OWN xpath targets Defs/BiomeDef[defName="biome"]/<list>."""
    import xml.etree.ElementTree as ET
    xp_re = re.compile(r'BiomeDef\s*\[\s*defName\s*=\s*"' + re.escape(biome)
                       + r'"\s*\]\s*/\s*(wildAnimals|wildPlants|fishTypes)\s*$')
    out = []
    for f in sorted(src.rglob("*.xml")):
        fs = str(f)
        if "/archive" in fs.lower() or ("/Defs/" not in fs and "/Patches/" not in fs):
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if biome not in text or not any(n in text for n in names):
            continue
        try:
            ET.fromstring(text.encode("utf-8"))
        except ET.ParseError:
            out.append({"file": f, "error": "unparseable XML"})
            continue
        spans = element_spans(text)
        if "/Defs/" in fs:
            for d, tag, s, e in spans:
                if tag != "BiomeDef":
                    continue
                body = text[s:e]
                if not re.search(r"<defName>\s*" + re.escape(biome) + r"\s*</defName>", body):
                    continue
                for d2, t2, s2, e2 in spans:
                    if t2 in LISTS and s <= s2 and e2 <= e and d2 == d + 1:
                        for n in names:
                            if re.search(r"<" + re.escape(n) + r"[\s>]", text[s2:e2]):
                                out.append({"file": f, "kind": "inline", "list": t2, "name": n, "region": (s2, e2)})
        else:
            for m in re.finditer(r"<xpath>(.*?)</xpath>", text, re.S):
                xm = xp_re.search(m.group(1).strip())
                if not xm:
                    continue
                vend = text.find("</value>", m.end())
                if vend < 0:
                    continue
                region = (m.end(), vend)
                for n in names:
                    if re.search(r"<" + re.escape(n) + r"[\s>]", text[region[0]:region[1]]):
                        out.append({"file": f, "kind": "patch", "list": xm.group(1), "name": n, "region": region})
    return out


# ──────────────────────────────────────────────────────── our def index ──

def our_defs(src: Path) -> dict:
    """defName -> [{file, tag, span, text}] for every top-level def in src/**/Defs (not abstract-only)."""
    out: dict = {}
    for f in sorted(src.rglob("*.xml")):
        fs = str(f)
        if "/Defs/" not in fs or "/archive" in fs.lower():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        for d, tag, s, e in element_spans(text):
            if d != 1:
                continue
            body = text[s:e]
            m = re.search(r"<defName>\s*([\w.\-]+)\s*</defName>", body)
            if m:
                out.setdefault(m.group(1), []).append({"file": f, "tag": tag, "span": (s, e), "text": body})
    return out


def word_refs(src: Path, name: str, exclude: dict) -> list[str]:
    """Files under src/ (xml, cs, py, json, csv, md) naming `name` as a whole word OUTSIDE the excluded spans
    ({file: [(s,e)...]}). -> ['path:line', ...]."""
    pat = re.compile(r"(?<![\w])" + re.escape(name) + r"(?![\w])")
    hits = []
    for f in src.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in (".xml", ".cs", ".py", ".json", ".csv", ".md", ".txt"):
            continue
        if "/archive" in str(f).lower():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if name not in text:
            continue
        ex = exclude.get(f, [])
        for m in pat.finditer(text):
            if any(s <= m.start() < e for s, e in ex):
                continue
            hits.append(f"{f.relative_to(src.parent)}:{text.count(chr(10), 0, m.start()) + 1}")
    return hits


def plan_cut(src: Path, biome: str, names: set[str]) -> dict:
    """The full cut of `names` from `biome`: roster lines, then our defs nothing else needs, then their art."""
    sites = roster_sites(src, biome, names)
    defs = our_defs(src)
    exclude: dict = {}
    for st in sites:
        if "region" in st:
            exclude.setdefault(st["file"], []).append(st["region"])
    deleted: dict = {}           # defName -> [entries]
    kept: dict = {}              # defName -> refs
    donors = sorted(n for n in names if n not in defs)
    queue = sorted(n for n in names if n in defs)
    seen = set()
    while queue:
        n = queue.pop(0)
        if n in seen:
            continue
        seen.add(n)
        ex = {k: list(v) for k, v in exclude.items()}
        for dn, ents in list(deleted.items()) + [(n, defs[n])]:
            for ent in ents:
                ex.setdefault(ent["file"], []).append(ent["span"])
        # roster lines are only ours to remove in THIS biome: an inline/patch site that names it elsewhere
        # is a reference, so the def stays
        refs = word_refs(src, n, ex)
        if refs:
            if n in names:
                kept[n] = refs
            continue
        deleted[n] = defs[n]
        for ent in defs[n]:
            ex.setdefault(ent["file"], []).append(ent["span"])
        # what this def alone used: our defs it names (eggs, products, meat, leather, kinds)
        for ent in defs[n]:
            refs_in = set(re.findall(r">\s*([\w.\-]+)\s*<", ent["text"])) | set(re.findall(r"<([\w.\-]+)[\s>/]", ent["text"]))
            for ref in sorted(refs_in):
                if ref and ref in defs and ref not in seen and ref not in deleted and ref != n:
                    queue.append(ref)
    # textures of deleted defs, only when no surviving XML still names the texPath
    tex = set()
    ex_all: dict = {}
    for ents in deleted.values():
        for ent in ents:
            ex_all.setdefault(ent["file"], []).append(ent["span"])
            for m in re.finditer(r"<texPath>\s*([^<\s]+)\s*</texPath>", ent["text"]):
                tex.add(m.group(1))
    tex_retire, tex_kept = [], {}
    for tp in sorted(tex):
        refs = [r for r in word_refs(src, tp, ex_all) if r.endswith(".xml") or ".xml:" in r]
        if refs:
            tex_kept[tp] = refs
        else:
            tex_retire.append(tp)
    return {"sites": sites, "deleted": deleted, "kept": kept, "donors": donors,
            "tex_retire": tex_retire, "tex_kept": tex_kept}


def apply_cut(plan: dict) -> list[Path]:
    """Write the cut: roster lines, then def blocks (highest offset first per file)."""
    touched = set()
    by_file: dict = {}
    for st in plan["sites"]:
        if "region" in st:
            by_file.setdefault(st["file"], []).append(("roster", st["region"], st["name"]))
    for ents in plan["deleted"].values():
        for ent in ents:
            by_file.setdefault(ent["file"], []).append(("def", ent["span"], None))
    for f, ops in by_file.items():
        text = f.read_text(encoding="utf-8")
        for kind, (s, e), name in sorted(ops, key=lambda o: -o[1][0]):
            if kind == "roster":
                text, _n = remove_entry_lines(text, (s, e), name)
            else:
                a, b = line_extent(text, s, e)
                text = text[:a] + text[b:]
        f.write_text(text, encoding="utf-8")
        touched.add(f)
    return sorted(touched)


# ──────────────────────────────────────────────────────────── the plan ──

def effective_picks(v: dict, srow: dict) -> tuple[dict, list[str]]:
    """{graphic: letter} he chose for each graphic of the row, and [(letter, why)] picks that cannot be placed
    (a by-name render on a row with several graphics). Per-graphic picks win over the row pick."""
    cols = srow.get("columns") or {}
    gof = dict(srow.get("graphic_of") or {})
    graphics = sorted({g for g in gof.values() if g != "_byname"}) or ([srow["res"]] if srow.get("res") else [])
    for l in cols:
        gof.setdefault(l, graphics[0] if len(graphics) == 1 else "_byname")
    picks = dict(v.get("picks") or {})
    dec = (v.get("decision") or "").strip()
    out, conflicts = {}, []

    def assign(letter, why):
        if letter not in cols:
            return
        g = gof.get(letter)
        if g == "_byname":
            if len(graphics) == 1:
                g = graphics[0]
            else:
                return "ambiguous"
        if g and g not in out:
            out[g] = letter
        return None

    for g, l in picks.items():
        if g == "_byname":
            continue
        if l in cols:
            out[g] = l
    if "_byname" in picks:
        if assign(picks["_byname"], "byname pick") == "ambiguous":
            conflicts.append((picks["_byname"], f"pick {picks['_byname']} is a by-name render and the row has "
                                                f"{len(graphics)} graphics; it does not say which one it replaces"))
    if dec in cols:
        g = gof.get(dec)
        if g == "_byname" and len(graphics) > 1:
            missing = [x for x in graphics if x not in out]
            if missing and dec != picks.get("_byname"):
                conflicts.append((dec, f"row pick {dec} is a by-name render and the row has {len(graphics)} graphics; "
                                       f"no per-graphic pick for {', '.join(x.rsplit('/', 1)[-1] for x in missing)}"))
        else:
            assign(dec, "row pick")
    return out, conflicts


def gof_resolved(srow: dict, letter: str) -> str | None:
    """The graphic a column stands for; a by-name render resolves only on a row with one graphic."""
    gof = srow.get("graphic_of") or {}
    graphics = sorted({g for g in gof.values() if g != "_byname"}) or ([srow["res"]] if srow.get("res") else [])
    g = gof.get(letter) or (graphics[0] if len(graphics) == 1 else None)
    if g == "_byname":
        g = graphics[0] if len(graphics) == 1 else None
    return g


def catch_source(row: str, decs: dict) -> str | None:
    """RM_HulduCatch -> RM_Huldu, when that creature is a row of the same sheet."""
    if row.endswith(CATCH_SUFFIX) and len(row) > len(CATCH_SUFFIX):
        s = row[:-len(CATCH_SUFFIX)]
        return s if isinstance(decs.get(s), dict) and decs[s].get("at") else None
    return None


def source_settled(src_row: str, decs: dict, snap: dict, jobs: list[dict], idx: L.Index, census: dict) -> tuple:
    """(settled, reference sha or None, why). A creature is settled once he has PICKED its picture: a letter on the
    sheet, or a render of the redraw he asked for that is now live in a mod. While it is being redrawn, anything drawn
    from it (its catch) would copy a picture he is about to replace."""
    sv = decs[src_row]
    dec = (sv.get("decision") or "").strip()
    srow = (snap.get("rows") or {}).get(src_row) or {}
    cols = srow.get("columns") or {}
    if dec in cols:
        xed = set(sv.get("purge") or [])
        letter = (sv.get("picks") or {}).get("_byname") or dec
        return True, first_by_facing(cols.get(letter) or {}, xed), f"{src_row} pick {letter}"
    if dec == "cut" or (dec == "hold" and CUT_NOTE.search(I.open_note(sv) or "")):
        return False, None, f"{src_row} is cut from this sheet"
    names = row_names(src_row, sv, census)
    mine = [j for j in jobs if job_defs(j) & names and str(j.get("created") or "") >= (sv.get("at") or "")[:19]]
    for j in mine:
        if j["_state"] == "done":
            sha = job_render_sha(j)
            if sha and idx.live_anywhere(sha):
                return True, sha, f"{src_row} render {j['id']} is live"
    states = sorted({j["_state"] for j in mine})
    return False, None, (f"{src_row} is being redrawn ({len(mine)} job(s) {'/'.join(states) or 'not yet filed'}) and "
                         f"no render of it is picked yet")


def owner_questions(idx: L.Index, sheet: str, row: str, note: str, past: list[str]) -> list[str]:
    """The OWNER: questions --mark-done recorded on this row, for its open note, a followed note, or the row itself."""
    notes = {note or "", *past, ""}
    out = []
    for e in idx.events:
        ev = str(e.get("evidence") or "")
        if e.get("type") == "enact_done" and e.get("sheet") == sheet and e.get("row") == row \
                and ev.startswith("OWNER:") and (e.get("note") or "") in notes:
            q = ev[6:].strip()
            if q and q not in out:
                out.append(q)
    return out


def pending_def_halves(v: dict, sheet: str, row: str, done_marks: set) -> list[str]:
    """Followed notes whose followers are ONLY art jobs, that also ask for a rename/description, with no enact_done."""
    out = []
    for f in v.get("notes_followed") or []:
        if not isinstance(f, dict):
            continue
        nt, by = str(f.get("note") or "").strip(), f.get("followed_by") or []
        if nt and by and not any(b in ("mark-done", "cut") for b in by) and DEF_ASK.search(nt) \
                and (sheet, row, nt) not in done_marks and nt not in out:
            out.append(nt)
    return out


def keep_ruling(idx: L.Index, row: str, letter: str, sha: str):
    for r in reversed(idx.rulings):
        tg = r.get("target") or {}
        if (r.get("by") == "owner" and r.get("trust") in L.TRUST_PROTECTS and L.normalise_verdict(r.get("verdict")) == "keep"
                and tg.get("row") == row and tg.get("column") == letter and sha in (tg.get("shas") or [])):
            return r
    return None


def build_plan(decisions: Path, holds=(), idx: L.Index | None = None, jobs: list[dict] | None = None,
               stale: dict | None = None) -> dict:
    doc = json.loads(decisions.read_text())
    snap_path = Path(doc.get("snapshot") or "")
    if not snap_path.is_absolute():
        snap_path = L.REPO_ROOT / snap_path
    snap = json.loads(snap_path.read_text())
    biome = doc.get("biome") or snap.get("biome")
    sheet = doc.get("sheetId") or snap.get("sheetId") or decisions.stem
    idx = idx or L.Index()
    jobs = load_jobs() if jobs is None else jobs
    census = census_rows_for(biome)
    src = L.src_root()
    done_ev = {(e.get("sheet"), e.get("row"), e.get("note")): e.get("evidence") or "" for e in idx.events
               if e.get("type") == "enact_done"}
    done_marks = set(done_ev)
    P = {"decisions": decisions, "sheet": sheet, "biome": biome, "held": [], "install": [], "installed_already": [],
         "retire": [], "blocked": [], "withdraw": [],
         "install_after_ingest": [], "queue": [], "queued_already": [], "refile": [], "awaiting_pick": [], "purge": [], "purged_already": 0,
         "cuts": [], "todo": [], "done": [], "conflicts": [], "in_game_not_ours": 0, "followed": {}}
    decs = doc.get("decisions") or {}
    wd_ids = withdrawn_ids()
    by_id = {j["id"]: j for j in jobs}

    def refs_sha(j: dict, sha: str | None) -> bool:
        """The job (or the east master it derives from) attaches `sha` as reference."""
        for k in (j, by_id.get(j.get("derive_from") or "")):
            if k and sha and any(sha in str(x) for x in [k.get("reference") or ""] + list(k.get("canon_reference") or [])):
                return True
        return False
    for row, v in decs.items():
        if not isinstance(v, dict) or not v.get("at"):
            continue
        decided = bool(v.get("decidedAt")) or not v.get("purgeTouched")
        if row in (stale or {}):
            P["conflicts"].append(f"{row}: letter(s) {', '.join(stale[row])} were clicked before the sheet's columns were "
                                  f"rebuilt and cannot be verified against the snapshot he saw — nothing ingested or done "
                                  f"for this row; re-confirm it on the current sheet")
            continue
        if is_held(row, holds):
            P["held"].append(row)
            continue
        srow = (snap.get("rows") or {}).get(row) or {}
        cols = srow.get("columns") or {}
        dec = (v.get("decision") or "").strip()
        note = I.open_note(v)        # a note already followed is history, never an open request
        past = I.followed_notes(v)
        # a note "followed" only by jobs since WITHDRAWN (drawn too early, e.g. a catch before its creature) is open again
        reopened = [str(f.get("note") or "").strip() for f in (v.get("notes_followed") or []) if isinstance(f, dict)
                    and f.get("followed_by") and all(b in wd_ids or any(w.startswith(b + "_") for w in wd_ids)
                                                     for b in f["followed_by"])]
        if not note and reopened:
            note = reopened[-1]
            past = [x for x in past if x != note]
        names = row_names(row, v, census)
        xed = {s for s in (v.get("purge") or []) if s}     # his ✕ on this row: purged in step 4, never kept/installed
        # ── 5 cut
        is_cut = decided and (dec == "cut" or (dec == "hold" and CUT_NOTE.search(note or "")))
        if is_cut:
            P["cuts"].append({"row": row, "names": names, "note": note, "raw_note": v.get("note")})
        # ── 2 install
        protect_here = set()
        folders: dict = {}
        picks: dict = {}
        if decided and not is_cut and dec != "redo":
            picks, conf = effective_picks(v, srow)
            for letter, c in conf:
                shas = [x for x in (cols.get(letter) or {}).values() if x and x not in xed]
                protect_here |= set(shas)
                if shas and all(idx.live_anywhere(x) for x in shas):
                    P["installed_already"] += [(row, idx.live_anywhere(x)[0], letter) for x in shas]
                else:
                    P["conflicts"].append(f"{row}: {c} — nothing installed for it")
            for g, letter in sorted(picks.items()):
                lab = (srow.get("labels") or {}).get(letter, "")
                for facing, sha in sorted((cols.get(letter) or {}).items()):
                    if not sha or sha in xed:       # he picked the column but ✕'d this facing: step 4 purges it
                        continue
                    protect_here.add(sha)
                    rel = rel_for(g, facing)
                    if idx.is_purged(sha):      # he picked it, and (on this or another sheet) purged it: his call
                        P["conflicts"].append(f"{row}: pick {letter} {facing} {sha[:12]} was purged by you — it cannot "
                                              f"be installed")
                        continue
                    anywhere = idx.live_anywhere(sha)
                    if anywhere:
                        # already shipping — at its own slot or as a graphic variant (RM_Fuzz_a, LongtailGorgV_I):
                        # never copy it over the base slot as well
                        P["installed_already"].append((row, anywhere[0], rel))
                        continue
                    slots = slots_for(idx, rel)
                    if not slots:
                        if str(lab).startswith("IN GAME"):
                            P["in_game_not_ours"] += 1
                        elif (sheet, row, note) in done_marks or (sheet, row, "") in done_marks:
                            pass        # --mark-done: the row was carried out by hand (the pick was a reference)
                        elif str(lab).startswith("donor original") and def_points_at(src, rel):
                            # he picked the DONOR picture itself and our def's texPath already names it: nothing to do
                            P["installed_already"].append((row, "def texPath (donor art)", rel))
                        elif (own := own_slot(idx, src, g, facing, letter, row, names)):
                            # a render he picked for a graphic no slot of ours ships (a donor texPath, or a
                            # Graphic_Random folder): it goes to OUR path, never "already live" (bug 2026-10-10:
                            # 6 creatures stayed vanilla Warg/Tortoise/Cobra/Squirrel/Muffalo, 7 plants on old A)
                            rul = keep_ruling(idx, row, letter, sha)
                            P["install"].append({"row": row, "mod": own["mod"], "rel": own["rel"], "sha": sha,
                                                 "letter": letter, "ruling": rul["id"] if rul else None,
                                                 "kind": own["kind"], "rebind": own.get("rebind"), "names": names})
                            if own["kind"] == "folder":
                                folders.setdefault(g, {"mod": own["mod"], "keep": set()})["keep"].add(sha)
                        else:
                            P["todo"].append(f"{row}: pick {letter} {rel} has no slot in any of our mods "
                                             f"(donor art? needs an override texture or a def texPath)")
                        continue
                    for mod, r, live in slots:
                        if live == sha:
                            P["installed_already"].append((row, mod, r))
                            continue
                        mine_at = I.ts(v.get("at"))
                        # an owner keep of that live picture from ANOTHER row, or from a LATER ruling on this row in
                        # another decisions file (re-enacting an old file must not undo his newer pick)
                        prot = [k for k in idx.protected(live) if (k.get("target") or {}).get("row") != row
                                or (k.get("via") != I.rel_via(decisions) and mine_at and I.ts(k.get("at"))
                                    and I.ts(k.get("at")) > mine_at)]
                        if prot:
                            P["conflicts"].append(f"{row}: {mod.rsplit('/', 1)[-1]}/{r} holds {live[:12]}, owner-kept "
                                                  f"on {Path(prot[0].get('via') or '').name or 'another ruling'}; "
                                                  f"pick {letter} not installed")
                            continue
                        rul = keep_ruling(idx, row, letter, sha)
                        P["install"].append({"row": row, "mod": mod, "rel": r, "sha": sha, "letter": letter,
                                             "ruling": rul["id"] if rul else None})
            for vl in v.get("variants") or []:
                protect_here |= {s for s in (cols.get(vl) or {}).values() if s and s not in xed}
            # ── 2b variants he TICKED (not the sheet's default tick): shipped beside the pick, never only protected
            # (bug 2026-10-10: Bladderquill/Shadefern/Steamfrond/Verdimoss/Weepmat B and Fanback C were never shipped)
            explicit = [] if v.get("variantsDefault") else [x for x in (v.get("variants") or []) if x in cols]
            for g in list(folders):
                for vl in explicit:
                    folders[g]["keep"] |= {s for s in (cols.get(vl) or {}).values() if s and s not in xed}
            for vl in explicit:
                gv = gof_resolved(srow, vl)
                if not gv or picks.get(gv) == vl:
                    continue            # the pick itself, or a letter of another graphic (a per-graphic pick)
                for facing, sha in sorted((cols.get(vl) or {}).items()):
                    if not sha or sha in xed or idx.is_purged(sha):
                        continue
                    if idx.live_anywhere(sha):
                        P["installed_already"].append((row, idx.live_anywhere(sha)[0], f"variant {vl}"))
                        continue
                    own = own_slot(idx, src, gv, facing, vl, row, names, variant=True)
                    if not own:
                        P["todo"].append(f"{row}: ticked variant {vl} {facing} has no slot it can ship in")
                        continue
                    rul = keep_ruling(idx, row, vl, sha)
                    P["install"].append({"row": row, "mod": own["mod"], "rel": own["rel"], "sha": sha, "letter": vl,
                                         "ruling": rul["id"] if rul else None, "kind": own["kind"],
                                         "rebind": own.get("rebind"), "names": names, "variant": True,
                                         "alt": (own["graphic"], own["res"]) if own["kind"] == "alt" else None})
            # a folder this run adds to ends up holding exactly his pick + ticked variants: the rest leaves the game
            for g, fo in folders.items():
                for m, r, live in folder_slots(idx, g):
                    if live not in fo["keep"]:
                        P["retire"].append({"row": row, "mod": m, "rel": r, "sha": live})
        # ── 3 queue / 6 todo
        if decided and not is_cut and (dec == "redo" or note):
            at = v.get("at") or ""
            # a note reopened because its art jobs were withdrawn still owes its picture, even when --mark-done
            # recorded its rename/description half
            fulfilled = False if note and note in reopened else ((sheet, row, note) in done_marks) if note else \
                bool(past or any(d[0] == sheet and d[1] == row for d in done_marks))
            match = [j for j in jobs if job_defs(j) & names and
                     ((note and note in I._note_text(j.get("owner_note"))) or
                      any(t in I._note_text(j.get("owner_note")) for t in past) or
                      str(j.get("created") or "") >= at[:19])]
            earlier = [j for j in jobs if job_defs(j) & names and j["_state"] in ("pending", "active")
                       and j not in match]
            src_row = catch_source(row, decs) if dec == "redo" else None
            cstate = None
            if src_row:
                settled, ref_sha, why = source_settled(src_row, decs, snap, jobs, idx, census)
                # jobs drawn before the creature was settled (none carries it as reference) are superseded: withdrawn,
                # never awaiting his pick (bug 2026-10-10: 8 catches rendered from no source at all)
                stale = [j for j in match if not (settled and refs_sha(j, ref_sha))]
                for j in stale:
                    if j["_state"] == "active":
                        P["conflicts"].append(f"{row}: job {j['id']} is rendering now, drawn before {src_row} was settled "
                                              f"— withdraw it once it finishes")
                    else:
                        P["withdraw"].append({"row": row, "job": j, "why": f"drawn before {src_row} was settled ({why})"})
                match = [j for j in match if j not in stale]
                if not settled:
                    P["blocked"].append(f"{row}: not filed — waiting for {src_row} to be settled ({why})")
                    cstate = "blocked"
                elif not match:
                    qnote = note or (past[-1] if past else "")
                    P["queue"].append({"row": row, "names": names, "note": qnote, "srow": srow, "v": v,
                                       "ref_shas": [ref_sha] if ref_sha else [], "source": src_row})
                    cstate = "queued"
            if cstate:
                pass
            elif earlier and not any(j["_state"] != "failed" for j in match):
                P["queued_already"].append(f"{row}: {len(earlier)} job(s) pending, filed BEFORE his latest note — "
                                           f"check they cover {note[:60]!r}")
            elif match:
                cj = classify_jobs(match, jobs, idx)
                for j in cj["refile"]:
                    P["refile"].append({"row": row, "job": j})
                for j in cj["capped"]:
                    P["conflicts"].append(f"{row}: job {j['id']} failed after {REFILE_CAP} re-files — needs its spec "
                                          f"looked at, not another retry")
                if cj["awaiting"]:
                    P["awaiting_pick"].append(f"{row}: {len(cj['awaiting'])} render(s) done, not installed — "
                                              + ", ".join(j["id"] for j in cj["awaiting"][:4])
                                              + (" …" if len(cj["awaiting"]) > 4 else ""))
                carried = [j["id"] for j in match if note and note in I._note_text(j.get("owner_note"))]
                if carried and not cj["capped"]:
                    if DEF_ASK.search(note) and (sheet, row, note) not in done_marks:
                        # the job draws the picture; the rename/description half is still owed — the note stays open
                        P["todo"].append(f"{row}: def half of the note not enacted (the art job carries only the "
                                         f"picture) — {note[:110]!r} (`--mark-done {row}` once the def edit is done)")
                    else:
                        P["followed"][row] = {"note": v.get("note"), "by": carried + (
                            ["mark-done"] if (sheet, row, note) in done_marks else [])}
                if not (cj["refile"] or cj["capped"] or cj["awaiting"]):
                    states = sorted({j["_state"] for j in match})
                    P["queued_already"].append(f"{row}: {len(match)} job(s) {'/'.join(states)}")
            elif dec == "redo" and fulfilled:
                # his note on this row was already carried out (mark-done / moved to notes_followed): a leftover
                # "redo" letter must not re-fire it. Only a NEW open note (not marked done) queues again.
                P["done"].append(f"{row}: note already carried out — redo not re-queued")
            elif dec == "redo":
                P["queue"].append({"row": row, "names": names, "note": note, "srow": srow, "v": v})
                if note and DEF_ASK.search(note) and (sheet, row, note) not in done_marks:
                    P["todo"].append(f"{row}: def half of the note not enacted (the art job carries only the "
                                     f"picture) — {note[:110]!r} (`--mark-done {row}` once the def edit is done)")
            elif (sheet, row, note) in done_marks and done_ev[(sheet, row, note)].startswith("OWNER:"):
                pass            # listed with every other OWNER question below (step 6c)
            elif (sheet, row, note) in done_marks:
                P["done"].append(f"{row}: {note[:70]}")
                P["followed"][row] = {"note": v.get("note"), "by": ["mark-done"]}
            else:
                P["todo"].append(f"{row}: note not enacted — {note[:110]!r} (art or def edit? `--mark-done {row}` when done)")
        # ── 6c every --mark-done --evidence "OWNER: <question>" on this row is a CONFLICT, whatever else the row has
        # (jobs, a followed note, a pick): bug 2026-10-10, 11 of 14 Rot rename questions on rows with art jobs were
        # recorded in the ledger and never shown to him
        if decided and not is_cut:
            for q in owner_questions(idx, sheet, row, note, past):
                line = f"{row}: {q}"
                if line not in P["conflicts"]:
                    P["conflicts"].append(line)
        # ── 6b a note already moved to notes_followed by an ART JOB alone, whose rename/description half nobody did
        if decided and not is_cut:
            for nt in pending_def_halves(v, sheet, row, done_marks):
                P["todo"].append(f"{row}: def half of a followed note not enacted (followed by art job only) — "
                                 f"{nt[:110]!r} (`--mark-done {row}` once the def edit is done)")
        # ── 4 purge
        for sha in v.get("purge") or []:
            if idx.is_purged(sha):
                P["purged_already"] += 1
                continue
            live = idx.live_anywhere(sha)
            kept_all = idx.protected(sha)
            # a keep minted by THIS row of THIS file (pick or default variant) does not protect a picture the same row
            # ✕'d: ingest used to record both (fixed there; this releases the keeps it already wrote)
            kept = [k for k in kept_all if not ((k.get("target") or {}).get("row") == row
                                                and k.get("via") == I.rel_via(decisions))]
            # a ✕ on a picture that ships ONLY inside a Graphic_Random folder of ours (a random variant the sheet showed
            # as its own column, owner card 2026-10-10 "Put them on the sheet"): it leaves the folder, then is purged —
            # unless it is the folder's last picture, a pick/variant here, or kept by another ruling
            row_folders = {g for g in (srow.get("graphic_of") or {}).values() if g and folder_slots(idx, g)}
            fl = [(m, r) for (m, r), ev in idx.live.items() if ev.get("sha") == sha]
            if fl and not kept and sha not in protect_here and all(
                    r.rsplit("/", 1)[0] in row_folders
                    and any(x[2] not in xed for x in folder_slots(idx, r.rsplit("/", 1)[0]))
                    for _m, r in fl):
                for m, r in fl:
                    P["retire"].append({"row": row, "mod": m, "rel": r, "sha": sha, "xed": True})
                P["purge"].append({"row": row, "sha": sha, "note": note, "release": bool(kept_all)})
                continue
            if live or kept or sha in protect_here:
                why = (f"live at {live[0]}" if live else
                       f"owner-kept ({Path(kept[0].get('via') or '').name or kept[0]['id']})" if kept else
                       "it is this row's own pick/variant")
                P["conflicts"].append(f"{row}: ✕ {sha[:12]} not purged — {why}")
                continue
            P["purge"].append({"row": row, "sha": sha, "note": note, "release": bool(kept_all)})
    for c in P["cuts"]:
        c["plan"] = plan_cut(src, biome, c["names"])
    return P


# ───────────────────────────────────────────── freshness for the sheet ──

RULINGS_DIR = L.REPO_ROOT / "infrastructure" / "state" / "art_rulings"


def ruled_decisions_for(sheet_id: str) -> Path | None:
    """The newest ingested ruling file (art_rulings/*.decisions.json) whose sheetId is SHEET_ID."""
    best = None
    for f in sorted(RULINGS_DIR.glob("*.decisions.json")):
        try:
            if json.loads(f.read_text()).get("sheetId") == sheet_id:
                best = f
        except (OSError, ValueError):
            continue
    return best


def ruling_status(decisions: Path, idx: L.Index | None = None, jobs: list[dict] | None = None) -> dict:
    """Per ruled row: is his ruling reflected? From the same plan `enact` would carry out, so the sheet can never
    say "done" for something enact still owes. state is one of
      reflected   the pick is live / the cut is done / the note is marked done / nothing was asked
      redrawn     renders filed for THIS ruling (after his click, or carrying his note) finished, awaiting his pick
      awaiting    its jobs are pending or running
      refiled     its jobs failed and are back in the queue
      conflict    needs him (listed on enact's CONFLICTS)
      not_acted   NOT YET ACTED ON — enact still owes it
    """
    decisions = Path(decisions)
    doc = json.loads(decisions.read_text())
    P = build_plan(decisions, (), idx or L.Index(), jobs)
    def mine(lst, row):
        return [x for x in lst if (x.get("row") if isinstance(x, dict) else str(x).split(":", 1)[0]) == row]
    rows = {}
    for row, v in (doc.get("decisions") or {}).items():
        if not isinstance(v, dict) or not v.get("at"):
            continue
        when = (v.get("decidedAt") or v.get("at") or "")[:16].replace("T", " ")
        st, detail = "reflected", "nothing further was asked"
        conf, todo = mine(P["conflicts"], row), mine(P["todo"], row)
        q, rf, aw = mine(P["queue"], row), mine(P["refile"], row), mine(P["awaiting_pick"], row)
        qa, dn = mine(P["queued_already"], row), mine(P["done"], row)
        inst, pur = mine(P["install"], row) + mine(P["retire"], row), mine(P["purge"], row)
        bl, wdr = mine(P["blocked"], row), mine(P["withdraw"], row)
        cut = [c for c in P["cuts"] if c["row"] == row]
        noslot = [t for t in todo if "has no slot in any of our mods" in t]
        todo = [t for t in todo if t not in noslot]
        conf = conf + [t.replace(" (donor art? needs an override texture or a def texPath)",
                                 " — your pick is donor art no mod of ours ships; showing it means re-pointing that def")
                       for t in noslot]
        if todo or q or inst or pur or wdr or any(c["plan"]["sites"] or c["plan"]["deleted"] for c in cut):
            st = "not_acted"
            detail = "; ".join([t.split(": ", 1)[1].split(" (art or def edit?")[0] for t in todo]
                               + (["redraw not yet filed"] if q else []) + (["pick not yet installed"] if inst else [])
                               + (["✕ not yet purged"] if pur else []) + (["cut not yet done"] if cut and st else [])
                               + (["early renders not yet withdrawn"] if wdr else []))
        elif conf:
            st, detail = "conflict", "; ".join(c.split(": ", 1)[1] for c in conf)
        elif bl:
            st, detail = "awaiting", "; ".join(x.split(": ", 1)[1] for x in bl)
        elif rf:
            st, detail = "refiled", "failed, re-filed: " + ", ".join(x["job"]["id"] for x in rf[:4])
        elif any("pending" in x or "active" in x for x in qa):
            st, detail = "awaiting", "awaiting render: " + "; ".join(x.split(": ", 1)[1] for x in qa)
        elif aw:
            st, detail = "redrawn", "redrawn after your ruling: " + "; ".join(x.split(": ", 1)[1] for x in aw)
        elif dn:
            st, detail = "reflected", "def edit done: " + "; ".join(x.split(": ", 1)[1] for x in dn)
        elif cut:
            st, detail = "reflected", "cut from this biome"
        elif qa:
            st, detail = "reflected", "redraw shipped or rejected: " + "; ".join(x.split(": ", 1)[1] for x in qa)
        elif any(r == row for r, *_ in P["installed_already"]):
            st, detail = "reflected", "your pick is live in game files"
        rows[row] = {"state": st, "detail": detail[:300], "when": when, "decision": (v.get("decision") or "").strip(),
                     "note": I.open_note(v)[:200],
                     "followed": I.followed_notes(v)[-3:]}
    n_ok = sum(1 for r in rows.values() if r["state"] in ("reflected", "redrawn"))
    return {"file": str(decisions), "rows": rows, "total": len(rows), "reflected": n_ok}


# ──────────────────────────────────────────────────────────── applying ──

def redo_ref_shas(q: dict, idx: L.Index | None = None) -> list[str]:
    """The ONE picture a redraw attaches as anatomy guidance, or none:
      * a catch: its settled creature (q["ref_shas"]);
      * "based on (b)": the column he named;
      * otherwise the row's in-game picture — never when his note rejects the art in front of him ("drop the art",
        "remove the turtle art", "redo completely"), and never a picture he ✕'d, purged or rejected.
    (bug 2026-10-10: Ambrosia/Loomu/Vizhik redraws carried the very art he dropped; Vellak's "(b)" carried nothing)"""
    idx = idx or L.cached_index()
    if q.get("source"):
        return [s for s in q.get("ref_shas") or [] if s and L.store_has(s) and not idx.is_purged(s)][:1]
    srow, v, note = q["srow"], q["v"], q.get("note") or ""
    cols, labels = srow.get("columns") or {}, srow.get("labels") or {}
    bad = set(v.get("purge") or [])
    m = BASED_ON.search(note)
    if m and m.group(1).upper() in cols:
        s = first_by_facing(cols[m.group(1).upper()], bad)
        return [s] if s and L.store_has(s) and not idx.is_purged(s) else []
    if DROP_ART.search(note):
        return []
    ref_letter = next((l for l, lab in sorted(labels.items()) if str(lab).startswith("IN GAME")), None)
    if not ref_letter:
        return []
    col = cols.get(ref_letter) or {}
    if any(s in bad for s in col.values()):
        return []
    s = first_by_facing(col, bad)
    # a plain redo keeps the picture he sent back as anatomy guidance (the redo verdict itself records it as rejected,
    # so a ledger-rejection filter would strip every reference); only his ✕, a purge or words in the note drop it
    return [s] if s and L.store_has(s) and not idx.is_purged(s) else []


def next_version(base: str) -> int:
    """1, or past every <base>_v<n> already withdrawn or rendered: a re-filed redraw never reuses a withdrawn job's id
    (its render dir in _artsrc/ would be overwritten and the two would be indistinguishable)."""
    aux, n = artpipe_aux(), 1
    while any(d.is_dir() and any(d.glob(f"{base}_v{n}*")) for d in (aux["withdrawn"], aux["artsrc"])):
        n += 1
    return n


def job_rows(P: dict) -> list[dict]:
    rows = []
    idx = L.cached_index()
    for q in P["queue"]:
        srow, v, row = q["srow"], q["v"], q["row"]
        refs = [str(L.store_path(s)) for s in redo_ref_shas(q, idx)]
        facings = sorted({f for c in (srow.get("columns") or {}).values() for f in c
                          if f in ("east", "north", "south")}, key=["east", "south", "north"].index)
        note = q["note"]
        label = (srow.get("subject_key") or row).replace("_", " ")
        src_ref = q.get("source") and refs
        guide = (f"the attached image is the settled {q['source']} this is drawn from — match its anatomy, markings and "
                 f"colours exactly" if src_ref else
                 "the attached image is the picture he sent back, anatomy guidance only, not a sprite to copy"
                 if refs else "no reference is attached: draw it fresh from the note")
        base = f"enact_{L.det_id(P['sheet'], row, note, v.get('at'), *(q.get('ref_shas') or []))[:8]}_{L.subject_key(row)}"
        rows.append({"id": f"{base}_v{next_version(base)}",
                     "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1", "target_def": row,
                     "prompt": (f"Owner's note, verbatim, overrides everything below: \"{note}\" " if note else "")
                     + f"RimWorld sprite of the {label}, painterly vanilla-RimWorld house style; redraw it — {guide}.",
                     "canvas_w": 256, "canvas_h": 256, "facings": facings, "priority": 0,
                     "owner_note": note, "canon_reference": refs, "biome_neutral": True})
    return rows


def deploy(mods: set[str], dry_run: bool) -> list[str]:
    """Deploy only these mod folders (src/<Tier>/<Mod>). -> report lines."""
    if not mods:
        return []
    import importlib
    sys.path.insert(0, str(HERE.parent))
    dcm = importlib.import_module("deploy_custom_mods")
    folded = dcm.folded()
    names = sorted({Path(m).name for m in mods})
    plain = [n for n in names if n not in folded]
    composed = sorted({n for n in names if n in folded})
    out = []
    game = game_running()
    script = str(HERE.parent / "deploy_custom_mods.py")
    calls = ([["--mod", n] for n in plain] and [sum((["--mod", n] for n in plain), [])]) + \
            ([["--compose", "biomes"]] if composed else [])
    for args in calls:
        label = " ".join(args)
        if dry_run:
            out.append(f"would deploy: {label}" + (f" (folded: {', '.join(composed)})" if "--compose" in args else ""))
            continue
        plan = subprocess.run([sys.executable, script] + args, capture_output=True, text=True, cwd=str(L.REPO_ROOT))
        if game and ".dll" in plan.stdout.lower():
            out.append(f"SKIPPED deploy {label}: its plan writes a DLL and RimWorldWin64 is running")
            continue
        r = subprocess.run([sys.executable, script, "--apply"] + args, capture_output=True, text=True,
                           cwd=str(L.REPO_ROOT))
        tail = (r.stdout.strip().splitlines() or [""])[-1]
        out.append(f"deployed {label}: rc={r.returncode} {tail[:120]}")
    return out


def game_running() -> bool:
    try:
        r = subprocess.run(["tasklist.exe", "/FI", "IMAGENAME eq RimWorldWin64.exe"], capture_output=True,
                           text=True, timeout=20)
        return "RimWorldWin64" in r.stdout
    except (OSError, subprocess.SubprocessError):
        return True      # cannot tell: treat as running (never write a DLL blind)


def enact(decisions: Path, *, apply: bool = False, holds=(), mark_done=(), no_deploy: bool = False,
          redo_jobs_out: Path | None = None, done_evidence: str = "") -> dict:
    decisions = Path(decisions)
    doc = json.loads(decisions.read_text())
    held_rows = [r for r in (doc.get("decisions") or {}) if is_held(r, holds)]
    # 1 ingest (dry-run counts what would be added)
    ing = I.ingest(decisions, dry_run=not apply, defer_redo_jobs=True, purge=False, skip_rows=held_rows)
    if not ing.get("ok"):
        return {"ok": False, "error": ing.get("error"), "ingest": ing}
    idx = L.Index()
    P = build_plan(decisions, holds, idx, stale=ing.get("stale_rows"))
    R = {"ok": True, "apply": apply, "ingest_new": ing.get("rulings", 0) + ing.get("rejected", 0),
         "installed": 0, "rebound": 0, "alts_added": 0, "retired": 0, "withdrawn": 0, "queued_jobs": 0, "refiled": 0, "purged": 0, "cut_rows": 0, "defs_deleted": 0, "textures_retired": 0,
         "deploy": [], "notes_cleared": [], "conflicts": list(P["conflicts"]), "todo": list(P["todo"]), "plan": P}
    touched_mods: set[str] = set()
    sheet = P["sheet"]
    # 6 mark-done
    # --mark-done is a RECORD that a note was enacted by hand, so it is written even on a dry run
    for row in mark_done:
        v = (doc.get("decisions") or {}).get(row) or {}
        note = I.open_note(v)
        halves = pending_def_halves(v, sheet, row, {(e.get("sheet"), e.get("row"), e.get("note")) for e in idx.events
                                                    if e.get("type") == "enact_done"}) if not note else []
        if halves:
            # the rename/description half of a note an art job already took off the open list
            w = L.Writer({e["id"] for e in idx.events})
            for nt in halves:
                w.add({"type": "enact_done", "id": L.det_id("enact_done", sheet, row, nt), "sheet": sheet, "row": row,
                       "note": nt, "by": "agent", "evidence": done_evidence or "", "via": I.rel_via(decisions)})
            w.flush()
            R["todo"] = [t for t in R["todo"] if not t.startswith(f"{row}: def half of")]
            if (done_evidence or "").startswith("OWNER:") and f"{row}: {done_evidence[6:].strip()}" not in R["conflicts"]:
                R["conflicts"].append(f"{row}: {done_evidence[6:].strip()}")
            P["done"].append(f"{row}: def half of {len(halves)} followed note(s) marked now")
            continue
        if not note:
            had = [t for t in R["todo"] if t.startswith(f"{row}: pick ") and "has no slot in any of our mods" in t]
            if not had:
                R["conflicts"].append(f"--mark-done {row}: that row carries no note — nothing recorded")
                continue
            # a donor-pick TODO (no note): record it under note "" so the plan stops raising it
            w = L.Writer({e["id"] for e in idx.events})
            w.add({"type": "enact_done", "id": L.det_id("enact_done", sheet, row, ""), "sheet": sheet, "row": row,
                   "note": "", "by": "agent", "evidence": done_evidence or "", "via": I.rel_via(decisions)})
            w.flush()
            R["todo"] = [t for t in R["todo"] if t not in had]
            P["done"].append(f"{row}: donor pick marked done")
            continue
        ev = {"type": "enact_done", "id": L.det_id("enact_done", sheet, row, note), "sheet": sheet, "row": row,
              "note": note, "by": "agent", "evidence": done_evidence or "", "via": I.rel_via(decisions)}
        w = L.Writer({e["id"] for e in idx.events})
        new = w.add(ev)
        w.flush()
        R["todo"] = [t for t in R["todo"] if not t.startswith(f"{row}: note not enacted")
                     and not t.startswith(f"{row}: def half of the note")
                     and not (t.startswith(f"{row}: pick ") and "has no slot in any of our mods" in t)]
        if new:
            P["done"].append(f"{row}: {note[:70]} (marked now)")
        if not (done_evidence or "").startswith("OWNER:"):
            P["followed"][row] = {"note": v.get("note"), "by": ["mark-done"]}
        elif f"{row}: {done_evidence[6:].strip()}" not in R["conflicts"]:
            R["conflicts"].append(f"{row}: {done_evidence[6:].strip()}")
    if not apply:
        R["installed"] = len(P["install"])
        R["rebound"] = len({(i["row"], i["rebind"]["old"]) for i in P["install"] if i.get("rebind")})
        R["alts_added"] = len({(i["row"], i["alt"][1]) for i in P["install"] if i.get("alt")})
        R["retired"] = len(P["retire"])
        R["withdrawn"] = len(P["withdraw"])
        R["queued_jobs"] = len(P["queue"])
        R["refiled"] = len(P["refile"])
        R["purged"] = len(P["purge"])
        R["cut_rows"] = sum(1 for c in P["cuts"] if c["plan"]["sites"] or c["plan"]["deleted"])
        R["defs_deleted"] = sum(len(c["plan"]["deleted"]) for c in P["cuts"])
        R["textures_retired"] = sum(len(c["plan"]["tex_retire"]) for c in P["cuts"])
        for i in P["install"]:
            touched_mods.add(i["mod"])
        for c in P["cuts"]:
            for st in c["plan"]["sites"]:
                touched_mods.add(mod_of(st["file"]))
    else:
        # 2 install (picks, then ticked variants), then the def edits that make the game draw them
        src = L.src_root()
        rebinds, alts, ok_rows = {}, {}, set()
        for i in P["install"]:
            rid = i["ruling"] or (keep_ruling(L.cached_index(), i["row"], i["letter"], i["sha"]) or {}).get("id")
            if not rid:
                R["conflicts"].append(f"{i['row']}: no keep ruling names {i['sha'][:12]} for pick {i['letter']} — not installed")
                continue
            try:
                r = L.install(i["mod"], i["rel"], i["sha"], ruling_id=rid)
                if r["status"] in ("installed", "already-live"):
                    R["installed"] += r["status"] == "installed"
                    touched_mods.add(i["mod"])
                    ok_rows.add(i["row"])
                    if i.get("rebind"):
                        rebinds[(i["row"], i["rebind"]["old"], i["rebind"]["new"])] = i
                    if i.get("alt"):
                        alts[(i["row"], i["alt"][0], i["alt"][1])] = i
            except L.Refused as e:
                R["conflicts"].append(f"{i['row']}: install {i['rel']} refused — {e}")
        for (row, old, new), i in sorted(rebinds.items()):
            for f in rebind_defs(src, i["names"], old, new):
                R["rebound"] += 1
                touched_mods.add(mod_of(f))
        for (row, base, res), i in sorted(alts.items()):
            for f in add_alternate_graphic(src, i["names"], base, res):
                R["alts_added"] += 1
                touched_mods.add(mod_of(f))
        # 2c a folder this run filled sheds the pictures he did not keep (archived in the store, never deleted)
        for rt in P["retire"]:
            if rt["row"] not in ok_rows and not rt.get("xed"):    # a ✕'d random-folder picture leaves on its own
                continue
            try:
                L.retire(L.src_root().parent / rt["mod"] / "Textures" / rt["rel"], reason=WRITER_TAG)
                R["retired"] += 1
                touched_mods.add(rt["mod"])
            except L.Refused as e:
                R["conflicts"].append(f"{rt['row']}: {rt['rel']} not retired — {e}")
        # 3a jobs drawn too early are withdrawn (never rendered, re-filed or offered for a pick)
        for w in P["withdraw"]:
            try:
                withdraw(w["job"], w["why"])
                R["withdrawn"] += 1
            except OSError as e:
                R["conflicts"].append(f"{w['row']}: withdraw of {w['job']['id']} failed — {e}")
        # 3 queue
        rows = job_rows(P)
        if rows:
            jp = redo_jobs_out or (L.REPO_ROOT / "Transient" / f"enact_{sheet}_{time.strftime('%Y%m%d_%H%M%S')}_jobs.json")
            jp.parent.mkdir(parents=True, exist_ok=True)
            jp.write_text(json.dumps(rows, indent=1))
            fq = [sys.executable, str(HERE.parent / "artpipe" / "fill_queue.py"), "--input", str(jp)]
            d = artpipe_dirs()
            fq += ["--pending-dir", str(d["pending"]), "--active-dir", str(d["active"]),
                   "--done-dir", str(d["done"]), "--failed-dir", str(d["failed"])]
            r = subprocess.run(fq, capture_output=True, text=True, cwd=str(L.REPO_ROOT))
            if r.returncode == 0:
                R["queued_jobs"] = len(rows)
                for q in P["queue"]:
                    if q["note"] and not (DEF_ASK.search(q["note"]) and q["row"] not in P["followed"]
                                          and any(x.startswith(f"{q['row']}: def half of the note") for x in R["todo"])):
                        P["followed"][q["row"]] = {"note": q["v"].get("note"),
                                                   "by": [r["id"] for r in rows if r["target_def"] == q["row"]]}
            else:
                R["conflicts"].append(f"fill_queue refused {jp.name}: {(r.stderr or r.stdout).strip()[-300:]}")
        # 3b re-file failed jobs
        for rf in P["refile"]:
            try:
                refile(rf["job"])
                R["refiled"] += 1
            except OSError as e:
                R["conflicts"].append(f"{rf['row']}: re-file of {rf['job']['id']} failed — {e}")
        # 4 purge
        for p in P["purge"]:
            try:
                L.purge(p["sha"], owner_said=p["note"] or f"reject+purge on sheet {sheet}",
                        via=I.rel_via(decisions), release_keep=bool(p.get("release")))
                R["purged"] += 1
            except L.Refused as e:
                R["conflicts"].append(f"{p['row']}: ✕ {p['sha'][:12]} not purged — {e}")
        # 5 cut
        for c in P["cuts"]:
            pl = c["plan"]
            if c.get("note"):
                P["followed"][c["row"]] = {"note": c["raw_note"], "by": ["cut"]}
            if not (pl["sites"] or pl["deleted"]):
                continue
            files = apply_cut(pl)
            R["cut_rows"] += 1
            R["defs_deleted"] += len(pl["deleted"])
            for f in files:
                touched_mods.add(mod_of(f))
            for tp in pl["tex_retire"]:
                for (mod, rel), ev in list(L.cached_index().live.items()):
                    if L.parse_texfile(rel)["res"] != tp or not ev.get("sha"):
                        continue
                    try:
                        L.retire(L.src_root().parent / mod / "Textures" / rel, reason=WRITER_TAG)
                        R["textures_retired"] += 1
                        touched_mods.add(mod)
                    except L.Refused as e:
                        R["conflicts"].append(f"{c['row']}: texture {rel} kept — {e}")
    # 6b a followed note comes OFF the open notes (owner, 2026-10-08)
    if apply and P["followed"]:
        R["notes_cleared"] = clear_followed(decisions, P["followed"])
    # 7 deploy
    if not no_deploy:
        R["deploy"] = deploy(touched_mods, dry_run=not apply)
    R["touched_mods"] = sorted(Path(m).name for m in touched_mods)
    return R


def clear_followed(decisions: Path, followed: dict) -> list[str]:
    """Move each followed note out of its row's `note` into `notes_followed` (his exact words, when, and by what).
    Re-reads the file immediately before writing and only touches a row whose note STILL equals the followed text,
    so a note he typed meanwhile survives; atomic replace, same JSON layout the sheet's sidecar writes. The bytes are
    re-read once more just before the replace: if his sidecar saved in between, the merge is redone on the new
    content (never replaced over it); after 4 lost races it gives up and the note stays open for the next run."""
    import tempfile
    path = Path(decisions)
    when = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    for _attempt in range(4):
        raw = path.read_bytes()
        doc = json.loads(raw.decode("utf-8"))
        cleared = []
        for row, f in sorted(followed.items()):
            v = (doc.get("decisions") or {}).get(row)
            txt = f.get("note") or ""
            if not isinstance(v, dict) or not txt.strip() or (v.get("note") or "").strip() != txt.strip():
                continue
            v.setdefault("notes_followed", []).append({"note": v["note"], "at": v.get("at"), "followed_by": f["by"], "when": when})
            v["note"] = ""
            cleared.append(row)
        if not cleared:
            return []
        payload = (json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".enact-", suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(payload)
                fh.flush()
                os.fsync(fh.fileno())
            if path.read_bytes() != raw:
                continue
            os.replace(tmp, path)
            return cleared
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    return []


def mod_of(f) -> str:
    """'src/<Tier>/<Mod>' (repo-relative) for a file under src/."""
    root = L.src_root()
    p = Path(f).resolve()
    try:
        parts = p.relative_to(root.resolve()).parts
    except ValueError:
        return str(f)
    return f"{root.name}/{parts[0]}/{parts[1]}"


def report(R: dict) -> str:
    if not R.get("ok"):
        return f"REFUSED: {R.get('error')}"
    P = R["plan"]
    mode = "APPLIED" if R["apply"] else "DRY RUN (nothing changed; --apply to do it)"
    L_ = [f"art enact {P['sheet']} ({P['biome']}) — {mode}"]
    L_.append(f"  ingest     {R['ingest_new']} new ruling/rejected event(s)")
    L_.append(f"  install    {R['installed']} file(s); {len(P['installed_already'])} already live; "
              f"{P['in_game_not_ours']} in-game donor picture(s) left as they are")
    for i in P["install"][:60]:
        L_.append(f"     {i['row']}: {'variant ' if i.get('variant') else ''}{i['letter']} -> "
                  f"{i['mod'].rsplit('/', 1)[-1]}/{i['rel']}"
                  + (f"  (def texPath {i['rebind']['old']} -> {i['rebind']['new']})" if i.get("rebind") else "")
                  + (f"  (alternateGraphics {i['alt'][1]})" if i.get("alt") else "")
                  + ("" if i["ruling"] else "  (ruling recorded by this ingest)"))
    if P["retire"]:
        L_.append(f"  retire     {R['retired']} picture(s) a filled folder no longer keeps")
        for rt in P["retire"]:
            L_.append(f"     {rt['row']}: {rt['mod'].rsplit('/', 1)[-1]}/{rt['rel']}")
    if P["withdraw"] or P["blocked"]:
        L_.append(f"  withdraw   {R['withdrawn']} job(s) drawn too early; {len(P['blocked'])} row(s) blocked")
        for w in P["withdraw"]:
            L_.append(f"     {w['row']}: {w['job']['id']} ({w['job']['_state']}) — {w['why'][:90]}")
        for b in P["blocked"]:
            L_.append(f"     blocked: {b}")
    L_.append(f"  queue      {R['queued_jobs']} redraw row(s) to file; {len(P['queued_already'])} already queued/rendered")
    for q in P["queue"]:
        L_.append(f"     {q['row']}: {q['note'][:90]!r}")
    for q in P["queued_already"]:
        L_.append(f"     already: {q}")
    L_.append(f"  re-file    {R['refiled']} failed job(s) back to pending/")
    for rf in P["refile"]:
        L_.append(f"     {rf['row']}: {rf['job']['id']}")
    L_.append(f"AWAITING OWNER PICK ({len(P['awaiting_pick'])}) — rendered for his note, neither installed nor rejected:")
    L_ += [f"  {a}" for a in P["awaiting_pick"]] or ["  none"]
    L_.append(f"  purge      {R['purged']} picture(s); {P['purged_already']} already purged")
    L_.append(f"  cut        {R['cut_rows']} row(s), {R['defs_deleted']} def(s) deleted, {R['textures_retired']} texture(s) retired")
    for c in P["cuts"]:
        pl = c["plan"]
        what = [f"{st['kind']} {st['list']} {st['name']} in {Path(st['file']).name}" for st in pl["sites"] if "region" in st]
        L_.append(f"     {c['row']} ({c['note'][:40]!r}): " + ("; ".join(what) or "not on this biome's roster (already cut)"))
        for dn in pl["deleted"]:
            L_.append(f"        delete def {dn}")
        for dn, refs in pl["kept"].items():
            L_.append(f"        keep def {dn}: still named by {', '.join(refs[:3])}{' …' if len(refs) > 3 else ''}")
        for dn in pl["donors"]:
            if any(st.get("name") == dn for st in pl["sites"]):
                L_.append(f"        {dn} is a donor def: only our roster line is removed")
        for tp in pl["tex_retire"]:
            L_.append(f"        retire texture {tp}")
    if P["held"]:
        L_.append(f"  held       {len(P['held'])} row(s): {', '.join(P['held'])}")
    if R.get("notes_cleared"):
        L_.append(f"  notes followed, taken off the open notes ({len(R['notes_cleared'])}): " + ", ".join(R["notes_cleared"]))
    elif P["followed"]:
        L_.append(f"  notes followed ({len(P['followed'])}) — would be taken off the open notes on --apply: " + ", ".join(sorted(P["followed"])))
    if P["done"]:
        L_.append(f"  notes done {len(P['done'])}: " + "; ".join(d.split(':')[0] for d in P["done"]))
    for d in R["deploy"]:
        L_.append(f"  deploy     {d}")
    L_.append(f"CONFLICTS ({len(R['conflicts'])}) — need the owner, nothing was done to them:")
    L_ += [f"  {c}" for c in R["conflicts"]] or ["  none"]
    L_.append(f"TODO ({len(R['todo'])}):")
    L_ += [f"  {t}" for t in R["todo"]] or ["  none"]
    if R["installed"] or R["textures_retired"]:
        L_.append("Art changes are visible after the next game restart (the engine does not hot-swap textures).")
    return "\n".join(L_)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("decisions")
    ap.add_argument("--apply", action="store_true", help="do it (default: dry run, prints the plan)")
    ap.add_argument("--dry-run", action="store_true", help="the default; accepted for clarity")
    ap.add_argument("--hold", action="append", default=[], help="skip rows whose key contains this (repeatable)")
    ap.add_argument("--mark-done", action="append", default=[], help="record a row's note as enacted by hand")
    ap.add_argument("--evidence", default="", help="with --mark-done: the commit/file that did it")
    ap.add_argument("--no-deploy", action="store_true")
    a = ap.parse_args(argv)
    if a.apply and a.dry_run:
        ap.error("--apply and --dry-run together")
    R = enact(Path(a.decisions), apply=a.apply, holds=a.hold, mark_done=a.mark_done, no_deploy=a.no_deploy,
              done_evidence=a.evidence)
    print(report(R))
    return 0 if R.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())

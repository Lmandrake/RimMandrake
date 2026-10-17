#!/usr/bin/env python3
"""art_sheet.py — the all-versions comparison sheet (design §3), built from the art ledger.

    python3 art_sheet.py --doubles --out Transient/art_doubles_compare_2026-10-04.html
    python3 art_sheet.py --res swanimals/Nuna/Nuna_f [--res ...] --out <html>
    python3 art_sheet.py --subjects RM_SluiceBox Bed [--jobs <artpipe job id>...] --name sluice_box [--label "Sluice box"]
        ANY game art that is not a biome roster (buildings, items, junk, gear, a batch of renders): the same gated,
        scaled sheet as --biome, written to Transient/biome_ffar/<name>_sheet_<date>.html (so serve, refresh, remap and
        enact treat it like any other sheet). Never hand-roll a generator for game art: serve_gated, sheet_to_artifact
        and the commit hook refuse an unstamped sheet whose pictures are game art.

One row per body graphic of a creature (group = the creature); columns are every picture set
the ledger knows for it: each mod shipping it today (the runtime winner marked from the live
ModsConfig.xml load order), artpipe render families, every historical state in git, and the
donor original. S/E/N stacked in each column. Masks and corpse (dessicated) textures never
enter the main grid; masks sit in a folded strip. Canon references show beside the row as
REFERENCE, never pickable. Prior rulings show with their trust (a flawed-sheet ruling is struck
through). Every picture shown is archived in the art store first.

The sheet writes a SNAPSHOT (row -> column -> facing -> sha) to infrastructure/state/art/sheets/;
decisions are column letters resolved through it by `art.py ingest`. Per-picture "purge" is the
owner's reject+purge. Prefill = his latest keep that resolves to a column, else the runtime-live column.
Built on the review-sheets template; gated by check_sheet.py. Generating the SHEET is always
safe; the DECISIONS file is only written when absent (never over his rulings).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger as L  # noqa: E402
import subject as S  # noqa: E402  (ART_SUBJECT_RESOLVER_1: the one name->art matcher)
import placeholder_detect as PD  # noqa: E402
import sheet_slots as SLOTS  # noqa: E402  (what each picture is FOR: the slot vocabulary, DESIGN 2026-10-10 §3.1)
import scaled_review_gate as SG  # noqa: E402  (the hard gate: a sheet failing a scaled-review requirement is never written)

SKILL = Path.home() / ".claude" / "skills" / "review-sheets" / "assets"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from game_paths import MODS_CONFIG as _MC  # noqa: E402
MODSCONFIG = Path(_MC)
CANON = L.REPO_ROOT / "design" / "RimStarWars" / "canon_references"
FACINGS = ("south", "east", "north", "west", "single")
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"   # >26 sets: lowercase continues
NEAR = 10   # dHash bits: at or under this on every facing = near-duplicate (shown folded, never hidden)
PH_NOSELECT = "placeholder — not selectable"
_GEO_CACHE: dict = {}


def geo_placeholder(faces: dict) -> str:
    """Owner rule 2026-10-07 22:33 PDT: "make sure that at no time can geometric placeholder art ever remain a
    viable Variant or selection". A set is a placeholder when EVERY archived picture in it is a flat geometric
    shape (placeholder_detect.placeholder_reason); returns the reason, '' for real art or an empty set."""
    shas = [s for s in (faces or {}).values() if s]
    if not shas:
        return ""
    why = []
    for s in shas:
        if s not in _GEO_CACHE:
            try:
                _GEO_CACHE[s] = PD.placeholder_reason(L.store_get(s)) or "" if L.store_has(s) else ""
            except Exception:                           # noqa: BLE001  unreadable = not judged here
                _GEO_CACHE[s] = ""
        if not _GEO_CACHE[s]:
            return ""
        why.append(_GEO_CACHE[s])
    return why[0]


# ─────────────────────────────────────────────────────────── load order ──

FULL_LIST = L.REPO_ROOT / "infrastructure" / "state" / "modlists" / "ModsConfig.FULL.LATEST.xml"
MIN_REAL_LIST = 200   # a live list shorter than this is a swapped-in test list, not what the owner plays


def _active(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    return [li.text.strip().lower() for li in root.find("activeMods") if (li.text or "").strip()]


def load_order():
    """packageId(lower) -> load index, plus a fingerprint line. The LIVE ModsConfig.xml when it is the
    owner's real list; when a small test list is swapped in (it decides nothing about what he plays),
    the captured FULL.LATEST list instead — otherwise every one of our mods reads 'not loaded' and no
    column can be IN GAME."""
    act, src = [], None
    if MODSCONFIG.is_file():
        act, src = _active(MODSCONFIG), "live ModsConfig.xml"
    if len(act) < MIN_REAL_LIST and FULL_LIST.is_file():
        live_n = len(act)
        act = _active(FULL_LIST)
        src = f"ModsConfig.FULL.LATEST.xml (live list has {live_n} mods — a test list)"
    if not act:
        return {}, "no mod list readable — runtime winner UNMEASURED"
    return {p: i for i, p in enumerate(act)}, f"{src}: {len(act)} active"


def _composed() -> dict:
    """source folder -> the composed mod's packageId, for entries a *.compose.json ships inside a unified mod
    (wave <= compose_wave). Their own packageIds are never on the load list: the unified mod is."""
    if not hasattr(_composed, "m"):
        _composed.m = {}
        for f in (L.REPO_ROOT / "src").glob("*/*.compose.json"):
            try:
                d = json.loads(f.read_text())
                pid = d["about"]["packageId"].lower()
                for e in d["entries"]:
                    if e.get("wave", 99) <= d.get("compose_wave", -1):
                        _composed.m[str((f.parent / e["source"]).relative_to(L.REPO_ROOT))] = pid
            except (OSError, ValueError, KeyError, TypeError):
                continue
    return _composed.m


def package_id(mod: str) -> str:
    if mod.rstrip("/") in _composed():
        return _composed()[mod.rstrip("/")]
    about = L.REPO_ROOT / mod / "About" / "About.xml"
    try:
        el = ET.parse(about).getroot().find("packageId")
        return (el.text or "").strip().lower()
    except (ET.ParseError, OSError, AttributeError):
        return ""


# ─────────────────────────────────────────────────────────────── canon ──

_WORLD = None


def _world():
    global _WORLD
    if _WORLD is None:
        _WORLD = S.World()
    return _WORLD


def canon_entry(*names: str) -> dict:
    """The canon-library entry for the first of NAMES that has one ({} if none). Default on every
    sheet (owner rule 2026-10-04): reference images + Must show are shown on each row.
    ART_SUBJECT_RESOLVER_1: a NAME that is literally an entry dir is taken as is; any other (a defName, an alias
    word) goes through subject.resolve_canon, exact matches only (base species stays canon_base's job)."""
    d = None
    for n in names:
        if n and (CANON / n.lower()).is_dir():
            d = CANON / n.lower()
            break
        r = S.resolve_canon(n, _world()) if n else None
        if r and r["match"] == "exact" and r["slug"] and (CANON / r["slug"]).is_dir():
            d = CANON / r["slug"]
            break
    if d is None:
        return {}
    txt = (d / "description.md").read_text(errors="replace") if (d / "description.md").exists() else ""
    secs = {}
    for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", txt, re.S | re.M):
        secs[m.group(1).strip().lower()] = m.group(2).strip()
    # the donor's sprite kept in the entry is not a canon reference (it is the donor column)
    imgs = sorted(p for p in d.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
                  and not p.name.startswith("donor_"))
    return {"brief": secs.get("visual brief", ""), "must": secs.get("must show", ""),
            "ruling": secs.get("ruling", ""), "images": imgs, "dir": str(d.relative_to(L.REPO_ROOT)),
            "key": d.name}


VARIANT_WORDS = {"alpha", "juv", "juvenile", "feral", "mature", "elder", "young", "adult", "baby", "calf", "pup", "wild"}


def canon_state(key: str, world: "S.World | None" = None) -> str:
    """The row tag when no canon entry matched (subject.canon_status: ART_SUBJECT_RESOLVER_1)."""
    return S.canon_status(key, world or _world())


def canon_base(key: str, label: str = "", census_entries: dict | None = None) -> tuple[dict, str]:
    """For a Star Wars (RSW_) row with no exact canon entry: drop life-stage/variant words (WraidAlpha,
    FeralNerf, 'young faa scalefish') and match the remainder EXACTLY to an entry dir, or to the entry of
    the census row for that base defName. Never a substring/prefix match (AA_Lockjaw must not find jawa,
    RM_ShaleGorgerJuv must not find gorg). Returns (entry, base name) or ({}, '')."""
    if not key.startswith("RSW_"):
        return {}, ""
    # ART_SUBJECT_RESOLVER_1: the variant vocabulary and word split are subject.py's, not a private copy.
    for name in (key, label or ""):
        words = S.words(S.stem(name)) if name == key else (name or "").split()
        base = [w for w in words if w.lower() not in S.VARIANT_WORDS]
        if not base or len(base) == len(words):
            continue
        name = "".join(base).lower()
        if (CANON / name).is_dir():
            return canon_entry(name), name
        e = (census_entries or {}).get("RSW_" + "".join(w[:1].upper() + w[1:] for w in base))
        if e:
            return canon_entry(Path(e).name), Path(e).name
    return {}, ""


# ───────────────────────────────────────────────────────────── thumbs ──

def thumb(sha: str, imgdir: Path, src_bytes: bytes | None = None, size: int = 200) -> str:
    from PIL import Image
    out = imgdir / f"{sha[:20]}.webp"
    if not out.exists():
        b = src_bytes if src_bytes is not None else L.store_get(sha)
        im = Image.open(BytesIO(b)).convert("RGBA")
        im.thumbnail((size, size), Image.LANCZOS)
        imgdir.mkdir(parents=True, exist_ok=True)
        im.save(out, "WEBP", quality=88, method=6)
    return f"{imgdir.name}/{out.name}"


def full_image(sha: str, imgdir: Path) -> str:
    """The archived picture at its FULL resolution, alone, as a PNG beside the thumbs (owner, 2026-10-15: clicking
    a candidate must open the full-resolution drawing by itself, never the 160 px thumbnail). Lossless: PNG bytes
    are copied unchanged; anything else is re-encoded to PNG at its own size."""
    out = imgdir / f"{sha[:20]}_full.png"
    if not out.exists():
        b = L.store_get(sha)
        imgdir.mkdir(parents=True, exist_ok=True)
        if b[:8] == b"\x89PNG\r\n\x1a\n":
            out.write_bytes(b)
        else:
            from PIL import Image
            Image.open(BytesIO(b)).save(out, "PNG")
    return f"{imgdir.name}/{out.name}"


# ──────────────────────────────────────────────────────────── columns ──

GENERIC_DIRS = {"plant", "plants", "things", "thing", "item", "items", "building", "buildings", "animal", "animals",
                "pawn", "pawns", "terrain", "filth", "mote", "motes", "projectile", "weapon", "weapons", "apparel"}
FAM_RE = re.compile(r"_(north|east|south|west)(_r\d+)?$")


def _def_slots(name: str) -> list[dict]:
    """sheet_slots for one def from the live dump; [] when unreadable (the row then shows unlabelled lanes, never fails)."""
    try:
        import gametex as GT
        return GT.def_slots(name)
    except (SystemExit, Exception) as e:                    # noqa: BLE001
        if not _EXTRA_WARNED:
            _EXTRA_WARNED.append(1)
            print(f"WARNING: slots UNMEASURED ({type(e).__name__}: {e})", file=sys.stderr)
        return []


def game_extra_texpaths(names) -> dict:
    """{texPath: role} the game also draws for any of NAMES (gametex.def_extra_texpaths over the live def dump);
    {} when the dump is unreadable — the row then shows what the census found, never fails."""
    out = {}
    try:
        import gametex as GT
        for n in names:
            if n:
                for t, role in GT.def_extra_texpaths(n).items():
                    out.setdefault(t, role)
    except (SystemExit, Exception) as e:                    # noqa: BLE001
        if not _EXTRA_WARNED:
            _EXTRA_WARNED.append(1)
            print(f"WARNING: alternate/young graphics UNMEASURED ({type(e).__name__}: {e})", file=sys.stderr)
    return out


_EXTRA_WARNED: list = []
COPY_BITS = 2   # dHash bits: a random-folder picture this close to one already shown is a re-encoded copy of it


def shown_base(key: str, ruled: dict | None, prev_rows: dict) -> set:
    """The pictures the owner has been SHOWN on row KEY: the columns of the snapshot his decisions were saved against
    (the page he ruled on); for a sheet he never saved, the baseline the previous build carried (`shownBase`), else
    the previous build's columns. A random-folder picture outside it is labelled "in game now, never shown"."""
    if ruled is not None:
        row = (ruled.get("rows") or {}).get(key) or {}
        return {sh for f in (row.get("columns") or {}).values() for sh in f.values()}
    row = prev_rows.get(key) or {}
    if "shownBase" in row:
        return set(row["shownBase"])
    return {sh for f in (row.get("columns") or {}).values() for sh in f.values()}


def _ph(idx, sha: str):
    return next((v.get("ph") for v in idx.variants.get(sha) or [] if v.get("ph")), None)


def random_folder_variants(idx: L.Index, res: str, skip_mods=()) -> dict:
    """{mod: {variant name: {facing: sha}}} for every mod of ours where `res` is a FOLDER (Graphic_Random /
    Graphic_Collection texPath): each picture directly inside it, masks excluded (`_<facing>m`, `<name>_m`, and
    `<name>m` beside a `<name>`). A mod shipping a file AT `res` (skip_mods) is not a folder there."""
    pre = res.rstrip("/") + "/"
    raw = defaultdict(dict)                    # mod -> {stem: {facing: sha}}
    for (mod, rel), ev in idx.live.items():
        if mod in skip_mods or not rel.startswith(pre) or "/" in rel[len(pre):] or not ev.get("sha"):
            continue
        if not rel.lower().endswith(".png"):
            continue
        pt = L.parse_texfile(rel)
        if pt["mask"]:
            continue
        raw[mod].setdefault(pt["res"][len(pre):], {})[pt["facing"]] = ev["sha"]
    out = {}
    for mod, vs in raw.items():
        names = set(vs)
        keep = {n: f for n, f in vs.items()
                if not ((n.endswith("_m") and n[:-2] in names) or (n.endswith("m") and n[:-1] in names))}
        if keep:
            out[mod] = keep
    return out


def build_row(idx: L.Index, res: str, order: dict, slots: dict, former=()) -> dict:
    """`former`: earlier texture paths of the SAME picture (a renamed mod folder) — their git history and bound renders
    join this row, labelled with the old path."""
    resset = {res, *former}
    parts = res.split("/")
    # the creature word is the folder (swanimals/Wraid/Wraid_j -> Wraid) unless that folder is a generic
    # category (Things/Plant/RM_Shadespire): then the file name. A generic word like "plant" joined every
    # *_plant_* render to every plant row (49 foreign renders on RM_Shadespire, 2026-10-04).
    word = parts[-2] if len(parts) > 1 and parts[-2].lower() not in GENERIC_DIRS else parts[-1]
    # render alias: the FILE STEM minus tier prefix, never the folder (art_resolution_rootcause §5.4 / B0)
    wl = S.stem(parts[-1]).lower()   # subject.stem: donor tiers (RG_, AB_ ...) and Plant_ too
    cols = []          # {kind, label, detail, faces:{facing: sha}, date, live, winner}

    # 1. every mod shipping it today
    live = defaultdict(dict)
    for (mod, rel), ev in idx.live.items():
        pt = L.parse_texfile(rel)
        if pt["res"] == res and not pt["mask"]:
            live[mod][pt["facing"]] = ev["sha"]
    # 1a. a texPath with no file of its own in a mod is a FOLDER there (Graphic_Random / Graphic_Collection): the game
    # draws EVERY picture in it at random, so each one is its own column (owner card 2026-10-10, "Put them on the
    # sheet": CrimsonCap b-f, Boomshroom B/C, Flakespire b, FruitingBody A-C drew in game and were never shown)
    folder = random_folder_variants(idx, res, skip_mods=set(live))
    first_git = {}
    for sha in {s for f in live.values() for s in f.values()} | \
            {s for vs in folder.values() for f in vs.values() for s in f.values()}:
        gs = sorted((v for v in idx.variants[sha] if v.get("kind") == "git"), key=lambda v: v.get("date", ""))
        if gs:
            first_git[sha] = gs[0]
    ranks = {m: order.get(package_id(m), -1) for m in list(live) + list(folder)}
    # game copies of this texPath (donor / other mods, ingested by gametex.py bound by texPath): one per mod
    dons, don_meta = defaultdict(dict), {}
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("kind") == "donor" and v.get("res") == res and not v.get("mask"):
                pkg = (v.get("donor_pkg") or "?").lower()
                if v.get("random_variant"):          # one picture of a donor Graphic_Random folder: its own column
                    pkg = f"{pkg}#{v['random_variant']}"
                dons[pkg].setdefault(v.get("facing"), sha)
                m = don_meta.setdefault(pkg, {"mod": v.get("donor_mod") or pkg, "how": v.get("how"),
                                              "random_of": v.get("random_of"), "bound_by": v.get("bound_by"),
                                              "loc": v.get("loc", ""), "random_variant": v.get("random_variant")})
                if v.get("donor_mod"):
                    m["mod"] = v["donor_mod"]
    dranks = {p: order.get(p.split("#")[0], order.get(p.split("#")[0] + "_steam", -1)) for p in dons}
    allr = list(ranks.values()) + list(dranks.values())
    top = max(allr) if allr and max(allr) >= 0 else None
    winner = next((m for m in ranks if top is not None and ranks[m] == top), None)
    dwinner = next((p for p in dranks if top is not None and dranks[p] == top), None) if winner is None else None
    dwin_pkg = dwinner.split("#")[0] if dwinner else None   # every picture of the winning copy's random folder draws
    for mod in sorted(live, key=lambda m: -ranks[m]):
        f = live[mod]
        g = [first_git[s] for s in f.values() if s in first_git]
        g.sort(key=lambda v: v.get("date", ""))
        lastg = g[-1] if g else {}
        cols.append({"kind": "live", "mod": mod, "faces": dict(f), "date": lastg.get("date", ""),
                     "label": f"{'IN GAME — ' if mod == winner else 'shipped, shadowed — ' if ranks[mod] >= 0 else 'shipped, not loaded — '}{mod.split('/')[-1]}",
                     "detail": (f"load index {ranks[mod]}" + (" (last loaded, wins)" if mod == winner else "")
                                + (f" · bytes from {lastg.get('commit')} {lastg.get('date')}: {lastg.get('subject', '')}" if lastg else "")),
                     "commit_subjects": [v.get("subject", "") for v in g],
                     "winner": mod == winner})
    for mod in sorted(folder, key=lambda m: -ranks[m]):
        vs = folder[mod]
        for i, (vname, f) in enumerate(sorted(vs.items()), 1):
            g = sorted((first_git[s] for s in f.values() if s in first_git), key=lambda v: v.get("date", ""))
            lastg = g[-1] if g else {}
            where = ("IN GAME — " if mod == winner else "shipped, shadowed — " if ranks[mod] >= 0
                     else "shipped, not loaded — ")
            cols.append({"kind": "live", "mod": mod, "faces": dict(f), "date": lastg.get("date", ""),
                         "label": f"{where}random variant {vname} ({i} of {len(vs)}) — {mod.split('/')[-1]}",
                         "detail": (f"Graphic_Random folder {res}: the game draws one of its {len(vs)} pictures at random"
                                    f" · load index {ranks[mod]}"
                                    + (f" · bytes from {lastg.get('commit')} {lastg.get('date')}: {lastg.get('subject', '')}" if lastg else "")),
                         "commit_subjects": [v.get("subject", "") for v in g],
                         "winner": mod == winner, "random_variant": vname, "random_of": len(vs)})

    # 2. artpipe render families: bound by collected.jsonl dest, or alias by creature word
    fams = defaultdict(dict)
    fam_jobs = defaultdict(dict)
    fam_meta = {}
    fam_ts = {}
    _fc = failed_canon_jobs()
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("kind") != "artpipe":
                continue
            job = v.get("job", "")
            bound = v.get("res") in resset
            alias = any(len(S.norm(w)) >= 4 and S.token_match(job, S.norm(w)) for w in S.join_stems(parts[-1]))
            if not (bound or alias):
                continue
            fam = FAM_RE.sub("", job)
            if not bound and _slot_of_family(fam) not in (None, *resset):
                continue      # filed FOR another graphic (job `slot`: Boarwolf_j, not Boarwolf): its slot's lane takes it
            fac = v.get("facing")
            if fac not in FACINGS:
                fm = re.search(r"_(north|east|south|west)(_r\d+)?$", job)
                fac = fm.group(1) if fm else "single"
            if fac not in fams[fam] or (job == fam_jobs[fam].get(fac) and (v.get("ts") or "") > fam_ts.get((fam, fac), "")):
                fams[fam][fac] = sha                 # a job re-registered with new bytes (a re-seat): its NEWEST bytes show
                fam_ts[(fam, fac)] = v.get("ts") or ""
            fam_jobs[fam].setdefault(fac, job)
            fam_meta[fam] = {"bound": bound or fam_meta.get(fam, {}).get("bound", False), "date": v.get("date", ""),
                             "prompt": v.get("prompt", ""), "derive": v.get("derive_from"), "item": v.get("item")}
    for fam, faces in sorted(fams.items(), key=lambda kv: fam_meta[kv[0]]["date"], reverse=True):
        if not fam_meta[fam]["bound"] and (NOT_BODY_JOB.search(fam) or FLIP_FAM_RE.match(fam)):
            continue          # a flight frame joined by name is not a body candidate (flipbook_cols shows it)
        m = fam_meta[fam]
        cols.append({"kind": "artpipe", "faces": faces, "date": m["date"],
                     "label": f"render {fam}" + (FAILED_CANON_BADGE if _is_failed_canon(fam, _fc) else ""),
                     "detail": (f"{m['date']} · {'collected to this texPath' if m['bound'] else 'joined by creature name only (not bound to this graphic)'}"
                                f" · derive_from {'yes' if m['derive'] else 'no'} · {m['item'] or ''}"),
                     "prompt": m["prompt"][:240], "bound": m["bound"], **canon_advice_fields(fam_jobs[fam])})

    # 3. every historical state in git, per mod path, as an observed set
    hist = defaultdict(list)       # mod -> [(date, commit, subject, facing, sha)]
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("kind") == "git" and v.get("res") in resset and not v.get("mask"):
                hist[v.get("mod", "?") + ("" if v.get("res") == res else " — old path")].append((v.get("date", ""), v.get("commit", ""), v.get("subject", ""),
                                               v.get("facing"), sha))
    for mod, evs in hist.items():
        state = {}
        bycommit = defaultdict(list)
        for e in sorted(evs):
            bycommit[(e[0], e[1], e[2])].append(e)
        for (date, commit, subj), es in sorted(bycommit.items()):
            for e in es:
                state[e[3]] = e[4]
            cols.append({"kind": "git", "mod": mod, "faces": dict(state), "date": date,
                         "label": f"history {mod.split('/')[-1]} {date}",
                         "detail": f"{commit} {date}: {subj}"})

    # 4. game copies from other mods: the one the game draws first (IN GAME), then donor originals
    wi = 0
    for pkg in sorted(dons, key=lambda p: (-dranks[p], p)):
        m = don_meta[pkg]
        win = pkg.split("#")[0] == dwin_pkg
        how = "AssetBundle extract" if m["how"] == "assetbundle-extract" else "loose PNG in the game's mod folders"
        col = {"kind": "donor", "faces": dons[pkg], "date": "", "winner": win,
               "ours": pkg.startswith("mandrake."),   # our own deployed copy is not a donor original
               "label": (f"IN GAME — {m['mod']}" if win else
                         f"our deployed art — {m['mod']}" if pkg.startswith("mandrake.") else f"donor original — {m['mod']}"),
               "detail": (f"load index {dranks[pkg]}" + (" (last loaded, wins)" if win else
                          " (shadowed by a later mod)" if dranks[pkg] >= 0 else " (not in the measured load order)")
                          + f" · {pkg} · {how}"
                          + ((f" · random variant {m['random_variant']} of {m['random_of']} in the folder" if m.get("random_variant")
                              else f" · 1 of {m['random_of']} random variants") if m.get("random_of") else "")
                          + (f" · bound: {m['bound_by']}" if m.get("bound_by") else ""))}
        if m.get("random_variant"):
            col["random_variant"], col["random_of"] = m["random_variant"], m.get("random_of")
        if win:
            cols.insert(wi, col)
            wi += 1
        else:
            cols.append(col)

    # drop purged pictures; fold exact duplicates into the first column carrying them
    out, seen, donor_purged = [], {}, False
    for c in cols:
        was = bool(c["faces"])
        c["faces"] = {f: s for f, s in c["faces"].items() if not idx.is_purged(s)}
        if not c["faces"]:
            if was and c["kind"] == "donor" and not c.get("ours"):
                donor_purged = True      # a donor ORIGINAL the owner purged: shown and rejected (gate req 4)
            continue
        key = tuple(sorted(c["faces"].items()))
        if key in seen:
            seen[key].setdefault("also", []).append(f"{c['label']} — {c['detail']}")
            continue
        seen[key] = c
        out.append(c)
    # near-duplicates (perceptual) fold under their parent, shown on expand
    ph = {s: (idx.variants[s][0].get("ph") or "") for c in out for s in c["faces"].values()}
    for i, c in enumerate(out):
        if c["kind"] == "live":
            continue
        for p in out[:i]:
            if p.get("near_of"):
                continue
            common = [f for f in c["faces"] if f in p["faces"]]
            if common and len(common) == len(c["faces"]) and all(
                    ph.get(c["faces"][f]) and ph.get(p["faces"][f]) and
                    L.hamming(ph[c["faces"][f]], ph[p["faces"][f]]) <= NEAR for f in common):
                c["near_of"] = p
                break
    # masks: folded strip, never in the grid
    masks = defaultdict(dict)
    for (mod, rel), ev in idx.live.items():
        pt = L.parse_texfile(rel)
        if pt["res"] == res and pt["mask"]:
            masks[mod.split("/")[-1]][pt["facing"]] = ev["sha"]
    subj = sorted({s["subject"] for s in slots.get(res, [])})
    return {"res": res, "word": word, "cols": out, "masks": masks, "subjects": subj, "donorPurged": donor_purged}


def prefill_for(row: dict, rulings: list[dict]) -> tuple[str, str, bool]:
    """(letter, why, contested). Latest ruled owner keep that resolves to a column; then an
    owner ruling cited in the commit that installed a live column's bytes (inferred); else the
    runtime-live column."""
    letter = {id(c): c["letter"] for c in row["cols"]}
    by_sha = {}
    for c in row["cols"]:
        for s in c["faces"].values():
            by_sha.setdefault(s, c)
    keeps = [r for r in rulings if r.get("verdict") == "keep" and r.get("trust") == "ruled" and r.get("by") == "owner"]
    for r in sorted(keeps, key=lambda r: r.get("at") or "", reverse=True):
        for s in (r.get("target") or {}).get("shas", []):
            if s in by_sha:
                return letter[id(by_sha[s])], f"your keep of {(r.get('at') or '')[:10]}", False
    pat = re.compile(r"owner|approved|ruling", re.I)
    for c in [c for c in row["cols"] if c["kind"] == "live"]:
        # the live bytes' own commit, or a look-alike parent: a mechanical sweep (the halo
        # zeroing) rewrote approved art without changing how it looks
        subs = list(c.get("commit_subjects", [])) + [d["detail"] for d in row["cols"] if d.get("near_of") is c]
        hit = next((s for s in subs if pat.search(s)), None)
        if hit:
            return c["letter"], f"inferred: the commit that installed it (or its look-alike parent) cites your approval (“{hit[:110]}”)", True
    if any(c.get("standin") for c in row["cols"]):
        # a texture-manifest row whose IN GAME picture is a vanilla stand-in: the sheet exists to judge the new
        # render named for that texture, so the agent's prefill is that render (and its scale panel is the one shown)
        ren = next((c for c in row["cols"] if c["kind"] == "artpipe"), None)   # already filtered by render_match
        if ren:
            return ren["letter"], "inferred: newest render named for this texture — the game shows only a vanilla stand-in", True
    win = next((c for c in row["cols"] if c.get("winner")), None) or (row["cols"][0] if row["cols"] else None)
    return (win["letter"] if win else ""), "no resolvable keep of yours — prefilled to what the game shows now", True


# ─────────────────────────────────────────────────────────── the page ──

DOUBLES_BODY = r"""
window.itemBody = it => {
  const d = (typeof DEC !== 'undefined' && DEC[it.id]) || {};
  const purge = new Set(d.purge || []);
  const facings = it.facings;
  const cell = (c, f) => {
    const s = c.faces[f];
    if (!s) return `<div class="ac-cell ac-gap" title="no ${f} in this set">—</div>`;
    const t = it.thumbs[s];
    const p = purge.has(s);
    const btn = c.purgeable ? `<button class="ac-purge${p ? ' on' : ''}" title="reject + PURGE: delete this picture from the art store so it never appears again" onclick="event.stopPropagation();artTogglePurge('${it.id}','${s}')">${p ? '✕ purging' : '✕'}</button>` : '';
    return `<div class="ac-cell${p ? ' ac-purged' : ''}"><div class="thumb ac-thumb" data-zoom="${t}" data-cap="${esc(it.label)} · ${c.letter} · ${f}"><img src="${t}" loading="lazy" alt=""></div>${btn}</div>`;
  };
  const col = c => `<div class="ac-col ac-${c.kind}${c.winner ? ' ac-win' : ''}${d.decision === c.letter ? ' ac-picked' : ''}">
      <div class="ac-head"><b>${c.letter}</b> ${esc(c.label)}</div>
      ${facings.map(f => cell(c, f)).join('')}
      ${(c.canonAdvice || []).length ? `<div class="bs-grader${c.canonFlag ? ' flag' : ''}" title="the canon grader's reading — ADVICE ONLY, it decides nothing">${c.canonAdvice.map(esc).join('<br>')}</div>` : ''}
      <div class="ac-detail" title="${esc(c.detail)}${c.prompt ? '\n\nprompt: ' + esc(c.prompt) : ''}">${esc(c.detail)}</div>
      ${c.also ? `<details class="ac-also"><summary>${c.also.length} identical elsewhere</summary>${c.also.map(a => `<div>${esc(a)}</div>`).join('')}</details>` : ''}
    </div>`;
  const main = it.cols.filter(c => !c.near_of), near = it.cols.filter(c => c.near_of);
  /* Canon reference beside the variants on EVERY row (owner rule 2026-10-04): images + Must show
     always visible; the visual brief scrolls in place; no entry = said on the row. */
  const canon = it.canon ? `<div class="ac-col ac-canoncol"><div class="ac-head"><b>canon</b> reference — not pickable</div>
      <div class="ac-canon-imgs">${it.canon.imgs.map(u => `<div class="thumb ac-cthumb" data-zoom="${u}" data-cap="canon reference · ${esc(it.canon.dir)}"><img src="${u}" loading="lazy" alt=""></div>`).join('') || '<span class="sub">entry has no images</span>'}</div>
      <div class="ac-brief"><b>Must show</b><pre>${esc(it.canon.must || '(entry lists none)')}</pre><b>Visual brief</b><pre class="ac-vb">${esc(it.canon.brief)}</pre>${it.canon.ruling ? `<b>Ruling</b><pre>${esc(it.canon.ruling)}</pre>` : ''}<span class="sub">${esc(it.canon.dir)}</span></div></div>`
    : `<div class="ac-col ac-canoncol ac-nocanon"><div class="ac-head"><b>canon</b></div><div class="sub">${esc(it.noCanon || 'no canon-library entry')}</div></div>`;
  const flawed = it.flawed ? `<div class="ac-flawed"><b>Your 2026-10-03 desert sheet:</b> ${esc(it.flawed.decision || '(no decision)')}${it.flawed.note ? ' — “' + esc(it.flawed.note) + '”' : ''} <span class="sub">⚠ made against a flawed sheet (its “current” column showed corpse textures for 65 of 109 rows) — shown, authorises nothing</span></div>` : '';
  const ctx = it.context ? `<div class="ac-ctx">${esc(it.context)}</div>` : '';
  const rul = it.rulings.length ? `<div class="ac-rulings">${it.rulings.map(r => `<div class="ac-r ac-t-${r.trust}" title="${esc(r.why || '')}">${esc(r.at)} <b>${esc(r.verdict)}</b> <span class="sub">${esc(r.trust)} · ${esc(r.sheet)}</span> ${r.note ? '“' + esc(r.note) + '”' : ''}</div>`).join('')}</div>` : '';
  const masks = it.masks.length ? `<details class="ac-masks"><summary>masks (not judged here — they follow the body pick)</summary><div class="ac-canon-imgs">${it.masks.map(m => `<div class="thumb ac-thumb" data-zoom="${m.t}" data-cap="mask ${esc(m.mod)} ${m.f}"><img src="${m.t}" loading="lazy" alt=""></div>`).join('')}</div></details>` : '';
  return `<div class="ac-body"><div class="effect">${esc(it.effect)}</div>
    <div class="marks">${it.flags.map(f => `<span class="mark contested">${esc(f)}</span>`).join('')}${it.contested ? '<span class="mark inferred">⚠ prefill inferred — ' + esc(it.prefillWhy) + '</span>' : '<span class="mark absent">prefill: ' + esc(it.prefillWhy) + '</span>'}</div>
    ${ctx}${flawed}${rul}${window.artFollowedHtml(d)}
    <div class="ac-grid"><div class="ac-col ac-facings"><div class="ac-head">&nbsp;</div>${facings.map(f => `<div class="ac-cell ac-flabel">${f}</div>`).join('')}</div>${main.map(col).join('')}${canon}</div>
    ${near.length ? `<details class="ac-near"><summary>${near.length} near-duplicate set(s) (dHash ≤ ${it.near} on every facing) — folded, not hidden</summary><div class="ac-grid">${near.map(c => col(c)).join('')}</div></details>` : ''}
    ${masks}</div>`;
};
"""

COMMON_JS = r"""
/* Notes he wrote that were already FOLLOWED (enact moves them out of the note box into notes_followed): history, not
   an open request, so a reload cannot resubmit them. */
window.artFollowedHtml = d => {
  const f = (d && d.notes_followed) || [];
  return f.length ? `<div class="ac-followed" style="font-size:12px;opacity:.75;margin:3px 0">${f.map(x => `followed: “${esc(x.note)}” <span class="sub">(${esc((x.followed_by || []).slice(0, 2).join(', '))}${(x.followed_by || []).length > 2 ? ' …' : ''} · ${esc(String(x.when || '').slice(0, 10))})</span>`).join('<br>')}</div>` : '';
};
/* A row collapsed as "already ruled elsewhere" wraps its .ac-body in <details class="bs-ruled">. Repaint replaces that
   OUTER element and marks the row open: replacing only the inner .ac-body nested a fresh CLOSED <details> inside the
   open one on every click (owner, 2026-10-15: "Clicking anything on the Murrelith kept closing their art"). */
window.artRepaint = id => {
  const it = byId.get(id);
  const row = document.querySelector(`.row[data-id="${cssEsc(id)}"]`);
  const node = row && (row.querySelector('details.bs-ruled') || row.querySelector('.ac-body'));
  if (!node || !it) return;
  if (it.ruledElsewhere) it.ruledOpen = true;     // he is working in this row: it never re-collapses this session
  node.outerHTML = window.itemBody(it);
};
window.artTogglePurge = (id, sha) => {
  if (frozen) return;
  const it = byId.get(id); if (!it) return;
  const rec = DEC[id] || (DEC[id] = { decision: '', note: '', prefill: prefillOf(it) });
  const s = new Set(rec.purge || []);
  if (s.has(sha)) s.delete(sha); else s.add(sha);
  rec.purge = [...s]; rec.purgeTouched = true;
  queue(id); patchRow(id); paintCounts();
};
addEventListener('DOMContentLoaded', () => {
  /* A decision click is recorded as decidedAt, so a row touched ONLY to purge or annotate
     never turns its prefill into a ruling at ingest (art_sheet.py docstring). */
  /* A save strips placeholder letters from HIS variant list; it never writes a default list (no pre-ticks). On a biome
     sheet every saved record is schema 2 (decisions_v2.py), stamped with the inventory revision it was made against. */
  const origQueue = window.queue;
  if (typeof origQueue === 'function') window.queue = function (id) {
    const it = byId.get(id);
    if (it && DEC[id]) {
      window.artEnsureVariants(it, DEC[id]);
      if (window.SLX && it.graphics && it.graphics.some(g => g.lane)) { window.SLX.v2(DEC[id]); if (it.rev) DEC[id].rev = it.rev; }
    }
    return origQueue.apply(this, arguments);
  };
  const orig = window.setDecision;
  if (typeof orig === 'function') window.setDecision = function (id, key, opts) {
    const it_ = byId.get(id);
    if (it_ && window.artNoSelect(it_).has(key)) { if (typeof showErr === 'function') showErr('Set ' + key + ' is placeholder art — it cannot be picked.'); return; }
    orig(id, key, opts);
    if (DEC[id]) {
      DEC[id].decidedAt = new Date().toISOString();
      /* the right-hand letter / redo buttons ARE the primary slot's choice: keep the slot record in step */
      const g = window.SLX && it_ && (it_.graphics || []).find(x => x.primary && x.lane === 'slot');
      if (g) {
        const k = DEC[id].decision, S = window.SLX; S.v2(DEC[id]);
        if (k && k.length === 1) DEC[id].slots[g.key] = { state: 'pick', pick: k, slot_id: (g.slot || {}).id || null, at: DEC[id].decidedAt };
        else if (k === 'redo') DEC[id].slots[g.key] = { state: 'redraw', slot_id: (g.slot || {}).id || null, at: DEC[id].decidedAt };
        else delete DEC[id].slots[g.key];
      }
      queue(id);
    }
  };
  /* The template's patchRow repaints only the buttons; the picked-column frame and the purge
     marks live in the row body, so repaint that too (also covers undo/redo). */
  const origPatch = window.patchRow;
  if (typeof origPatch === 'function') window.patchRow = function (id) { origPatch(id); window.artRepaint(id); };
});
/* Column letters are per row: the pick buttons show only the letters this row has (template hook). */
window.itemOptions = it => OPTS.filter(o => !(o.key.length === 1 && /[A-Za-z]/.test(o.key)) || (it.letters || []).includes(o.key));
"""

STYLE = r"""
<style>
.ac-grid{display:flex;gap:8px;overflow-x:auto;padding:6px 0 4px;align-items:flex-start}
.ac-col{flex:0 0 auto;width:132px;border:1px solid var(--line);border-radius:6px;padding:4px;background:#0f1216}
.ac-col.ac-facings{width:44px;border:none;background:none}
.ac-col.ac-win{border-color:var(--info)}
.ac-col.ac-picked{border-color:var(--ok);box-shadow:0 0 0 2px #5ac37f55}
.ac-col.ac-artpipe .ac-head{color:#d9b8ff}.ac-col.ac-git .ac-head{color:#9fb3c8}.ac-col.ac-donor .ac-head{color:#e8b64c}
.ac-head{font-size:11px;line-height:1.25;height:2.6em;overflow:hidden;color:var(--ink)}
.ac-head b{font-size:13px;color:var(--accent)}
.ac-cell{position:relative;height:124px;display:flex;align-items:center;justify-content:center;margin:2px 0}
.ac-flabel{font-size:11px;color:var(--dim);writing-mode:vertical-rl}
.ac-gap{color:#3a4250;font-size:20px}
.ac-thumb{width:120px;height:120px;flex:0 0 120px}
.ac-purge{position:absolute;top:2px;right:2px;font-size:10px;padding:0 4px;border-radius:3px;border:1px solid #5a2a2a;background:#1a0f0f;color:#e06c6c;cursor:pointer;opacity:.55}
.ac-purge:hover,.ac-purge.on{opacity:1}
.ac-purge.on{background:#e06c6c;color:#000}
.ac-purged .ac-thumb{outline:3px solid #e06c6c;opacity:.45}
.ac-detail{font-size:10.5px;color:var(--dim);height:3.9em;overflow:hidden;line-height:1.3}
.bs-grader{font-size:10.5px;line-height:1.3;color:var(--dim);margin-top:3px;max-width:340px;white-space:normal}
.bs-grader.flag{color:#e8c070;border-left:2px solid #c9902c;padding-left:4px}
.ac-also,.ac-near,.ac-masks,.ac-canon{font-size:11.5px;color:var(--dim);margin-top:4px}
.ac-canon-imgs{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0}
.ac-brief pre{white-space:pre-wrap;font:inherit;color:#c3cad6;margin:2px 0 6px;max-height:16em;overflow:auto}
.ac-rulings{font-size:11.5px;margin:4px 0}
.ac-r{color:#c3cad6}.ac-t-flawed-sheet{text-decoration:line-through;color:#8a7070}
.ac-t-prefill{color:#5f6b7a}
.ac-canoncol{width:300px;background:#14110c;border-color:#5a4a2a}
.ac-canoncol .ac-head{color:#e8b64c}
.ac-cthumb{width:136px;height:136px;flex:0 0 136px}
.ac-vb{max-height:9em!important}
.ac-nocanon{width:170px;font-size:11.5px}
.ac-flawed{font-size:12px;margin:4px 0;padding:3px 6px;border-left:3px solid #b07a3a;background:#1a140c;color:#d8c7a8}
.ac-ctx{font-size:11.5px;color:var(--dim);margin:2px 0}
</style>
"""

RENDER = '<script id="RENDER">' + DOUBLES_BODY + COMMON_JS + "</script>" + STYLE


def pick_options(n: int) -> list[dict]:
    """Column letters (per row: the same letter is a different picture on every row, so no group bulk),
    then redo / hold. Only 'hold' gets an all-rows button."""
    opts = [{"key": LETTERS[i], "label": LETTERS[i], "hotkey": str(i + 1) if i < 9 else "",
             "color": "#5ac37f", "counts": "in", "bulk": False} for i in range(n)]
    return opts + [{"key": "redo", "label": "redo", "hotkey": "r", "color": "#e8b64c",
                    "counts": "out", "bulk": False},
                   {"key": "hold", "label": "hold", "hotkey": "h", "color": "#98a2b3", "counts": "out"}]


def generate(resources: list[str], out_html: Path, title: str, sheet_id: str, brief: str,
             meta: dict | None = None, invented_extra: list[str] | None = None) -> dict:
    """META (optional) per texPath: group, subject_keys, canon_names, flags, flawed (the 10-03
    verdict), context (one line). Canon reference images + Must show are shown on EVERY row by
    default (owner rule 2026-10-04); a row without a canon entry says so."""
    meta = meta or {}
    idx = L.Index()
    slots = L.scan_def_slots()
    order, fp = load_order()
    imgdir = out_html.parent / (out_html.stem + "_img")
    rows, items, snap_rows = [], [], {}
    for res in resources:
        rows.append(build_row(idx, res, order, slots))
    maxcols = 0
    for row in rows:
        for i, c in enumerate(row["cols"]):
            c["letter"] = LETTERS[i]
            c["purgeable"] = c["kind"] != "live" and not (c["kind"] == "donor" and c.get("winner"))   # the game's own art
        maxcols = max(maxcols, len(row["cols"]))
    for row in rows:
        word = row["word"]
        m = meta.get(row["res"], {})
        keys = {word.lower(), L.subject_key(word)} | {L.subject_key(k) for k in m.get("subject_keys", [])}
        rul = idx.subject_rulings(keys)
        letter, why, contested = prefill_for(row, rul)
        facings = [f for f in FACINGS if any(f in c["faces"] for c in row["cols"])]
        thumbs = {}
        for c in row["cols"]:
            for s in c["faces"].values():
                if not L.store_has(s):
                    raise SystemExit(f"BYTES_MISSING {s} — every shown picture must be archived first")
                thumbs[s] = thumb(s, imgdir)
        masks = []
        for mod, faces in row["masks"].items():
            for f, s in sorted(faces.items()):
                masks.append({"mod": mod, "f": f, "t": thumb(s, imgdir)})
        cnames = list(m.get("canon_names", [])) + [word] + list(row["subjects"])
        ce = canon_entry(*cnames)
        canon = None
        if ce:
            seen_c = {}
            for p in ce["images"]:
                seen_c.setdefault(L.sha256_file(p), p.read_bytes())
            # the ledger's canon images for the same entry (same files normally; union by sha)
            for s_, vs in idx.variants.items():
                for v in vs:
                    if (v.get("kind") == "canon" and (v.get("subject_key") or "").lower() == ce["key"]
                            and not v.get("is_donor_sprite") and s_ not in seen_c and L.store_has(s_)):
                        seen_c[s_] = None
            canon = {"dir": ce["dir"], "brief": ce["brief"][:2500], "must": ce["must"][:1500],
                     "ruling": ce["ruling"][:800] if "(empty" not in ce["ruling"] else "",
                     "imgs": [thumb(sh, imgdir, b, 260) for sh, b in seen_c.items()]}
        rid = row["res"]
        shadow = [c for c in row["cols"] if c["kind"] == "live"]
        flags = list(m.get("flags", []))
        if len(shadow) > 1:
            flags.append(f"SHADOWED: {len(shadow)} of our mods ship this texPath")
        nonwin_mixed = [c for c in row["cols"] if c["kind"] == "live" and len({c["faces"].get(f) is None for f in facings}) > 1]
        if nonwin_mixed:
            flags.append("SET INCOMPLETE")
        n_hist = sum(1 for c in row["cols"] if c["kind"] == "git")
        n_rend = sum(1 for c in row["cols"] if c["kind"] == "artpipe")
        item = {
            "id": rid, "group": m.get("group", word), "label": f"{m.get('name', word)} — {rid.split('/')[-1]}",
            "context": m.get("context", ""), "flawed": m.get("flawed"),
            "noCanon": None if canon else ("no canon-library entry (looked for: " + ", ".join(dict.fromkeys(c for c in cnames if c)) + ")"),
            "effect": (f"{', '.join(row['subjects']) or 'no def of ours names this texPath'} · "
                       f"{len(row['cols'])} distinct sets: {len(shadow)} shipped now, {n_rend} renders, "
                       f"{n_hist} history states — pick the column the game should show"),
            "prefill": letter, "prefillWhy": why, "contested": contested,
            "facings": facings, "thumbs": thumbs, "letters": [c["letter"] for c in row["cols"]],
            "cols": [{k: (v if k != "near_of" else v["letter"]) for k, v in c.items()
                      if k in ("letter", "kind", "label", "detail", "faces", "winner", "also", "prompt", "purgeable", "near_of", "placeholder", "ours")}
                     for c in row["cols"]],
            "near": NEAR, "masks": masks, "canon": canon, "flags": flags,
            "rulings": [{"at": (r.get("at") or "")[:10], "verdict": r.get("raw_verdict") or r.get("verdict"),
                         "trust": r.get("trust"), "sheet": Path(r.get("source_file") or "").name.replace(".decisions.json", ""),
                         "note": (r.get("note") or r.get("blanket_said") or "")[:240], "why": r.get("why_not_protecting", "")}
                        for r in sorted(rul, key=lambda r: r.get("at") or "") if r.get("trust") != "prefill"
                        and not (m.get("flawed") and r.get("trust") == "flawed-sheet")],
        }
        items.append(item)
        snap_rows[rid] = {"subject_key": word.lower(), "res": rid,
                          "columns": {c["letter"]: c["faces"] for c in row["cols"]},
                          "labels": {c["letter"]: c["label"] for c in row["cols"]}}

    snapshot = {"sheetId": sheet_id, "built": L.now(), "loadOrder": fp, "rows": snap_rows}
    snapshot["snapshotId"] = hashlib.sha1(json.dumps(snap_rows, sort_keys=True).encode()).hexdigest()[:16]
    snap_path = L.ledger_dir() / "sheets" / f"{sheet_id}.snapshot.json"
    snap_path.parent.mkdir(parents=True, exist_ok=True)
    snap_path.write_text(json.dumps(snapshot, indent=1, sort_keys=True))

    opts = pick_options(maxcols)
    decisions_path = out_html.parent / (out_html.stem + ".decisions.json")
    cfg = {
        "sheetId": sheet_id, "title": title,
        "subtitle": f"{len(items)} graphics · {sum(len(i['cols']) for i in items)} picture sets · {fp}",
        "briefHtml": brief,
        "criterion": ("Columns ordered: what the game shows now first (by live load order), then the other shipped copy, "
                      "renders newest first, history oldest first, donor last. The order ranks RECENCY and RUNTIME, not quality."),
        "invented": list(invented_extra or []) + [
            "Renders are joined to a creature by its NAME in the job id when no collect record binds them to a texPath; "
            "such columns say 'joined by creature name only' and may belong to a different graphic of the same creature.",
            "Where no ruling of yours names exact pictures, the prefill trusts a COMMIT MESSAGE that says the art was approved "
            "(e.g. 'Wire approved Pyrelands creature render wave'); those rows carry an ⚠ mark.",
            "History columns are OBSERVED states of one mod's files after each commit — they were real files, never a ruled set.",
        ],
        "posture": {"mode": "pick-one", "explain": "Each row: pick the ONE column the game should show. The winner goes into the "
                    "owning (override) mod and the losing copy is archived — nothing is installed until you see that plan. "
                    "✕ on a picture = reject + PURGE: it is deleted from the art store and never offered again."},
        "options": opts, "groupLabel": "creature", "media": True,
        "decisionsFile": decisions_path.name, "decisionsPath": str(decisions_path), "sheetPath": str(out_html),
    }
    tpl = (SKILL / "sheet_template.html").read_text()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(cfg, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(items).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("<!-- ══ FILL IN #3 (optional)", RENDER + "\n<!-- ══ FILL IN #3 (optional)", 1)
    tpl = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", tpl, count=1, flags=re.S)
    out_html.write_text(tpl)
    wrote_dec = False
    if not decisions_path.exists():
        decisions_path.write_text(json.dumps({
            "sheetId": sheet_id, "posture": "pick-one", "snapshot": _rel(snap_path),
            "snapshotId": snapshot["snapshotId"], "criterion": cfg["criterion"],
            "reviewStatus": {"state": "prefill", "by": None, "at": None,
                             "evidence": "generated by art_sheet.py; no human has ruled"},
            "decisions": {it["id"]: {"decision": it["prefill"], "note": "", "prefill": it["prefill"]} for it in items},
        }, indent=1))
        wrote_dec = True
    return {"html": str(out_html), "decisions": str(decisions_path), "wrote_decisions": wrote_dec,
            "snapshot": str(snap_path), "rows": len(items), "sets": sum(len(i["cols"]) for i in items),
            "images": len(list(imgdir.glob("*.webp")))}


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(L.REPO_ROOT))
    except ValueError:
        return str(p)


def doubles(idx: L.Index) -> list[str]:
    by = defaultdict(lambda: defaultdict(set))
    for (mod, rel), ev in idx.live.items():
        by[rel][mod].add(ev["sha"])
    res = set()
    for rel, mods in by.items():
        if len(mods) > 1 and len({s for ss in mods.values() for s in ss}) > 1:
            pt = L.parse_texfile(rel)
            res.add(pt["res"])
    return sorted(res)


DOUBLES_BRIEF = """<p><b>The 45 doubled texture paths.</b> Two of our mods ship the same texture path with
<i>different</i> pictures, and the game shows whichever mod loads <b>last</b> — today that is SWBestiary,
so its older port art is what you see in game, shadowing override art that was wired on your 2026-09-13→17
approvals. Creatures: Nuna, Iriaz, Dalgo, Bantha, Eopie (your ruling 2026-10-04: a short compare sheet first,
winner to the override mod, loser archived).</p>
<p><b>Per row, pick the column the game should show.</b> Columns hold every picture set we have for that graphic:
<b>IN GAME</b> (blue frame) is what the game draws now; <b>shipped, shadowed</b> is the copy losing the race;
<b>render</b> columns are artpipe outputs; <b>history</b> columns are earlier states of our files from git;
<b>donor original</b> is the donor mod's own sprite. Facings are stacked south / east / north so a set whose
facings are different animals shows as a broken column. Masks and corpse textures are not judged here.</p>
<p><b>✕ on any non-live picture</b> = reject + purge: it is deleted from the art store and drops off every future
sheet. Your note box is the most useful control on the row. Nothing installs from this sheet: your picks become
ledger rulings, then you see an install plan.</p>"""


# ─────────────────────────── per-biome sheet (BIOME_FLORAFAUNA_ART_REVIEW_1, owner rulings 2026-10-04) ──
#
#   python3 src/RimMandrake/Utils/art/art_sheet.py --refresh --biome first3
#     --refresh = art.py backfill artpipe (~45 s, finished renders into the ledger) + gametex.py ingest (game copies of
#     every row's texPath, ~10 s; ~65 s more when its /tmp/rm_gametex index must be rebuilt) + biome_census.py; the sheets then
#     take ~4 min for the first three biomes (thumbnails are cached by sha, so a re-run only renders new pictures)
#
# One sheet per biome from Transient/biome_ffar/census.json (biome_census.py). One item per census row (flora AND
# fauna); within a row, one section per body graphic (body / swimming / flying …) holding every picture set the
# ledger knows for it (build_row, recomputed live on every run, so finished renders appear on a re-run), plus
# renders found by the row's NAME that no graphic binds yet. Canon images + Must show beside every canon row; a
# row with no entry says so. Census twins become two-way "related" links; linked rows share a group + colour band
# and sit together. Desert sitting 1 picks (census prior_selection) prefill the matching graphic. Letters are kept
# STABLE across re-runs (read back from the previous snapshot), so a decisions file the owner has touched still
# resolves; an untouched prefill decisions file is regenerated.

CENSUS = L.REPO_ROOT / "Transient" / "biome_ffar" / "census.json"
BIOME_OUT = L.REPO_ROOT / "Transient" / "biome_ffar"
BIOME_SLUG = {"RM_LongShade": "desert", "RM_Stillsand": "deep_desert", "RM_BlueDesert": "blue_desert",
              "desert": "desert", "deep_desert": "deep_desert", "blue_desert": "blue_desert"}   # others: _stem(key).lower()
TIER_RE = S.TIER_RE
NOT_BODY_JOB = re.compile(r"dess?icc?at|corpse|_mote|halo|filth|skeleton|print|mask|_icon\b", re.I)
PAIR_COLOURS = ["#e8b64c", "#5ac3c3", "#c38ae8", "#e07a5f", "#7fc35a", "#5a8ae8", "#e85aa8", "#c3b85a"]
_ROW_SLOTS: dict = {}
# a lane the live dump names no slot for: its label from the census role (DESIGN §3.1)
FALLBACK_SLOT = {"swimming graphic": ("SWIMMING", "swimming"), "flying graphic": ("FLYING", "flying"),
                 "young plant": ("PLANT · YOUNG (immature)", "plant_young"), "leafless plant": ("PLANT · LEAFLESS", "leafless"),
                 "alternate graphic (the game picks it at random)": ("ADULT · ALTERNATE (random pool)", "alternate"),
                 "wing-beat flight frames": ("FLYING", "flying")}
SLOT_DESC = {"adult": "what every grown animal looks like", "adult_female": "what every grown female looks like",
             "young": "an earlier life stage, drawn until it grows up", "young_female": "an earlier life stage (female)",
             "flying": "wing-beat frames, shown while airborne — plays as a loop",
             "flying_female": "wing-beat frames for females — plays as a loop",
             "swimming": "drawn while it swims", "swimming_female": "drawn while a female swims",
             "alternate": "one of the pictures the game picks at random for the adult",
             "grown": "the mature plant", "plant_young": "the immature plant before it matures (immatureGraphicPath)",
             "leafless": "the plant out of season (leaflessGraphicPath)", "item": "the item as it lies on the ground",
             "body": "the picture the game draws for it"}
ROLE_TEXT = {"body": "body", "swimming": "swimming graphic", "flying": "flying graphic",
             "plant_immature": "young plant", "plant_leafless": "leafless plant",
             "alternate": "alternate graphic (the game picks it at random)", None: "renders found by NAME"}
SIT1 = "desert sitting 1"


def _stem(n: str) -> str:
    return S.stem(n)


def _human(row: dict) -> str:
    if row.get("label"):
        return row["label"]
    s = _stem(row["key"])
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s).replace("_", " ").lower()


def _tier(row: dict) -> tuple[str, str]:
    k = row["key"]
    if (row.get("canon") or {}).get("entry"):
        return "canon", "canon Star Wars creature (has a canon-library entry)"
    if k.startswith("RSW_"):
        return "sw", "Star Wars tier (RSW_), no canon-library entry"
    if k.startswith(("RM_", "RUT_", "rut_")):
        return "ours", "our own design (franchise-free RM_/RUT_)"
    return "donor", "a donor mod's def, not one of ours"


def _layer(row: dict) -> str:
    parts = []
    if isinstance(row.get("layer"), str) and row["layer"]:
        parts.append(row["layer"])
    for p in row.get("placements") or []:
        if p.get("layer") == "inline_RM" or (p.get("source") == "inline" and not p.get("patch_mod")):
            parts.append("in this biome's own roster")
        else:
            parts.append(f"added by the {p.get('patch_mod') or 'patch'} layer")
    return " + ".join(dict.fromkeys(parts))


def _short(c: dict) -> str:
    """One readable line for a set's header; the full provenance is its tooltip."""
    lab = c.get("label", "")
    if c.get("random_variant"):
        return (("IN GAME now, NEVER SHOWN · " if c.get("neverShown") else
                 f"IN GAME · copy of {c['copyOf']} · " if c.get("copyOf") else "IN GAME · ") if c.get("winner") else
                "not drawn · ") + f"random {c['random_variant']} ({c.get('random_of') or '?'} in folder) · ✕ removes it"
    if c.get("kind") == "live":
        return ("IN GAME · " if c.get("winner") else "not loaded · " if "not loaded" in lab else "shadowed copy · ") + lab.split("— ")[-1]
    if c.get("kind") == "artpipe":
        return f"render {(c.get('date') or '')[:10]} · {lab.removeprefix('render ')}"
    if c.get("kind") == "git":
        return f"history {(c.get('date') or '')[:10]} · {lab.removeprefix('history ').rsplit(' ', 1)[0]}"
    if c.get("kind") == "kept":
        return "KEPT · your ruled pick, no longer found · " + lab
    if c.get("kind") == "donor" and c.get("oursRender"):
        return ("IN GAME · " if c.get("winner") else "our art, shadowed · ") + lab.split(" — ")[0]
    if c.get("kind") == "donor":
        if c.get("winner"):
            return "IN GAME · " + lab.split("— ", 1)[-1]
        return "donor original · " + lab.split("— ", 1)[-1].removeprefix("donor original ")
    return lab


def _prefill_short(source: str, why: str) -> str:
    if source == "inferred" and why.startswith("inferred: newest render named for this texture"):
        return "the new render (the game shows a vanilla stand-in)"
    if source == "inferred" and why.startswith("inferred: newest render"):
        return "newest render found by name"
    if "no resolvable keep" in why:
        return "what the game shows now (no pick of yours)"
    if why.startswith("inferred"):
        return "a commit says you approved it"
    if source == "none":
        return "hold — no art yet" if "no art" in why else why
    return why[:80]


def _fkey(c: dict) -> tuple:
    return tuple(sorted(c["faces"].items()))


OVERRIDES = Path(__file__).resolve().parent / "sheet_row_overrides.json"


# A render the daemon filed failed_canon BEFORE the grader became an advisor (owner, 2026-10-15). The grader never
# blocks now; the badge only marks those old records, and every render's own grade shows as `canonAdvice`.
FAILED_CANON_BADGE = " — grader flagged (advisory)"
_CA_CACHE: dict = {}


def canon_advice(job: str) -> dict | None:
    """The canon ADVISOR's verdict on one artpipe job, from its done/ (else failed/) manifest:
    {verdict, text} with text = canon_check.advisory_text (score + flagged lines). None when ungraded/absent."""
    import os
    root = Path(os.environ.get("ARTPIPE_STATE_DIR") or "/mnt/d/Luke/dev/_artpipe")
    key = (str(root), job)
    if key in _CA_CACHE:
        return _CA_CACHE[key]
    out = None
    for d in ("done", "failed"):
        mp = root / d / f"{job}.manifest.json"
        if not mp.is_file():
            continue
        try:
            m = json.loads(mp.read_text())
        except (OSError, ValueError):
            break
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "artpipe"))
        import canon_check  # noqa: E402 — lazily: only sheets with artpipe renders need it
        c = canon_check.normalize(m.get("canon_check"))
        if c and c.get("status") == "graded":
            out = {"verdict": c["verdict"], "text": canon_check.advisory_text(c)}
        break
    _CA_CACHE[key] = out
    return out


def canon_advice_fields(jobs_by_facing: dict) -> dict:
    """Column fields for the grader's advice on a render set: canonAdvice = ["south: grader flag (advisory) 4/5: ✗ …"],
    canonFlag = any facing FAILed. Advisory only — the owner decides; nothing here gates a pick."""
    order = {f: i for i, f in enumerate(FACINGS)}
    lines, flag = [], False
    for fac, job in sorted(jobs_by_facing.items(), key=lambda kv: order.get(kv[0], 99)):
        a = canon_advice(job)
        if a and a["text"]:
            lines.append(f"{fac}: {a['text']}")
            flag = flag or a["verdict"] == "FAIL"
    return {"canonAdvice": lines, "canonFlag": flag} if lines else {}


_FC_CACHE: dict = {}


def failed_canon_jobs() -> set:
    """Job ids the artpipe canon gate filed as failed_canon (failed/<job>.manifest.json). The render still exists in
    _artsrc and is a CANDIDATE: the gate has false-failed before (owner accepted such a render). Read at build time."""
    import os
    root = Path(os.environ.get("ARTPIPE_STATE_DIR") or "/mnt/d/Luke/dev/_artpipe") / "failed"
    if root in _FC_CACHE:
        return _FC_CACHE[root]
    out = _FC_CACHE[root] = set()
    if root.is_dir():
        for m in root.glob("*.manifest.json"):
            try:
                if json.loads(m.read_text()).get("worker_status") == "failed_canon":
                    out.add(m.name[:-len(".manifest.json")])
            except (OSError, ValueError):
                pass
    return out


def _is_failed_canon(fam: str, fc: set) -> bool:
    return any(j == fam or FAM_RE.sub("", j) == fam for j in fc)


_JOB_TARGETS: dict | None = None
_JOB_SLOTS: dict | None = None


def job_slots() -> dict:
    """job id (lower) -> the sheet SLOT (lane key) a finished artpipe job was filed for (fill_queue `slot`, written by
    enact since 2026-10-10): such a render is offered in that slot, never in the unassigned lane."""
    global _JOB_SLOTS
    if _JOB_SLOTS is None:
        import os
        _JOB_SLOTS = {}
        root = Path(os.environ.get("ARTPIPE_STATE_DIR") or "/mnt/d/Luke/dev/_artpipe") / "done"
        if root.is_dir():
            for f in root.glob("*.json"):
                if f.name.endswith(".manifest.json"):
                    continue
                try:
                    j = json.loads(f.read_text())
                except (OSError, ValueError):
                    continue
                if isinstance(j, dict) and j.get("id") and isinstance(j.get("slot"), str):
                    _JOB_SLOTS[str(j["id"]).lower()] = j["slot"]
    return _JOB_SLOTS


def _slot_of_family(fam: str) -> str | None:
    """The `slot` an artpipe job family (id minus facing suffix) was filed for, or None."""
    global _FAM_SLOTS
    if _FAM_SLOTS is None:
        _FAM_SLOTS = {}
        for j, s in job_slots().items():
            _FAM_SLOTS.setdefault(FAM_RE.sub("", j), s)
    return _FAM_SLOTS.get(fam.lower())


_FAM_SLOTS: dict | None = None


def job_targets() -> dict:
    """job id -> target_def for every finished artpipe job (done/<id>.json). A render filed under a NEW name (the
    owner renamed the creature: regen_gt_ookala_v2_* for RM_CanopySwinger) still names the def it is a picture of,
    so it joins its row by that def even when no word of the row's name is in the job id. Read once per process."""
    global _JOB_TARGETS
    if _JOB_TARGETS is None:
        import os
        _JOB_TARGETS = {}
        root = Path(os.environ.get("ARTPIPE_STATE_DIR") or "/mnt/d/Luke/dev/_artpipe") / "done"
        if root.is_dir():
            for f in root.glob("*.json"):
                if f.name.endswith(".manifest.json"):
                    continue
                try:
                    j = json.loads(f.read_text())
                except (OSError, ValueError):
                    continue
                if isinstance(j, dict) and j.get("id") and j.get("target_def"):
                    _JOB_TARGETS[str(j["id"]).lower()] = j["target_def"]
    return _JOB_TARGETS


def name_render_cols(idx: L.Index, words, exact, defs=(), exact_any=False) -> list[dict]:
    """Artpipe render families whose job name carries one of WORDS (word-bounded, >= 4 chars), is one of
    EXACT (artpipe_state_jobs), or whose job was filed for one of DEFS (its target_def — survives a rename).
    Corpse/mote/mask/filth jobs are not body art and never join — except, with EXACT_ANY (a texture-manifest row,
    which names the one texture it is about, e.g. a dessicated corpse), a family listed in EXACT."""
    keys = [S.norm(w) for w in words if w and len(S.norm(w)) >= 4]
    exact = {e.lower() for e in exact}
    defs = {d for d in defs if d}
    targets = job_targets() if defs else {}
    fams, meta, jobs_of, seen_ts = defaultdict(dict), {}, defaultdict(dict), {}
    for sha, vs in idx.variants.items():
        if idx.is_purged(sha):
            continue
        for v in vs:
            if v.get("kind") != "artpipe":
                continue
            job = v.get("job", "")
            fam = FAM_RE.sub("", job)
            fl = fam.lower()
            if exact_any and fl in exact:
                pass
            elif NOT_BODY_JOB.search(fl) or not (fl in exact or any(S.token_match(fl, k) for k in keys)
                                                 or targets.get(job.lower()) in defs):
                continue
            fac = v.get("facing")
            if fac not in FACINGS:
                fm = FAM_RE.search(job)
                fac = fm.group(1) if fm else "single"
            vts = v.get("ts") or ""
            if fac not in fams[fam] or (job == jobs_of[fam].get(fac) and vts > seen_ts.get((fam, fac), "")):
                fams[fam][fac] = sha                 # a job re-registered with new bytes (a re-seat): its NEWEST bytes show
                seen_ts[(fam, fac)] = vts
            jobs_of[fam].setdefault(fac, job)
            meta[fam] = {"date": v.get("date", ""), "prompt": v.get("prompt", ""), "item": v.get("item")}
    fc = failed_canon_jobs()
    slots_of = job_slots()
    return [{"kind": "artpipe", "faces": f, "date": meta[k]["date"], "family": k,
             "jobSlot": next((slots_of[j] for j in slots_of if FAM_RE.sub("", j) == k.lower()), None),
             "label": f"render {k}" + (FAILED_CANON_BADGE if _is_failed_canon(k, fc) else ""),
             "detail": f"{meta[k]['date']} · found by NAME — not wired to any graphic of ours yet · {meta[k]['item'] or ''}",
             "prompt": (meta[k]["prompt"] or "")[:240], "bound": False, **canon_advice_fields(jobs_of[k])}
            for k, f in sorted(fams.items(), key=lambda kv: meta[kv[0]]["date"], reverse=True)]


# FLYER_FLIPBOOK_ART_1: a wing-beat is a whole-animal flip-book, `<prefix><N>_<facing>` for N = 1..8. Each frame
# is its own artpipe job (`<seq>_<N>_<facing>`), so by name they would show as eight one-frame sets nobody can
# judge. They are joined into ONE set per sequence (faces keyed "N_facing"), drawn as a frames grid with a looping
# playback per facing, and picked as a whole.
FLIP_FAM_RE = re.compile(r"^(?P<seq>.*fl(?:y|ight|ying)\w*?)_(?P<n>\d{1,2})$", re.I)
FLIP_RES_RE = re.compile(r"^(?P<prefix>.*_fly(?:ing)?_?)(?P<n>\d{1,2})$", re.I)
FLIP_FACINGS = ("east", "south", "north")
FLIP_ROLE = "wing-beat flight frames"


def flip_key(n, facing) -> str:
    return f"{int(n)}_{facing}"


def flipbook_cols(idx: L.Index, words, exact, prefixes=()) -> list[dict]:
    """Flip-book sets for a row: artpipe frame sequences found by name (word-bounded, like name_render_cols), and
    live frame sets under any of the row's flyingAnimationFramePathPrefix values."""
    keys = [S.norm(w) for w in words if w and len(S.norm(w)) >= 4]
    exact = {e.lower() for e in exact}
    seqs, meta = defaultdict(dict), {}
    for sha, vs in idx.variants.items():
        if idx.is_purged(sha):
            continue
        for v in vs:
            if v.get("kind") != "artpipe":
                continue
            job = v.get("job", "")
            fm = FLIP_FAM_RE.match(FAM_RE.sub("", job))
            fac = v.get("facing") if v.get("facing") in FLIP_FACINGS else (FAM_RE.search(job) or [None, None])[1]
            if not fm or fac not in FLIP_FACINGS:
                continue
            seq = fm.group("seq")
            sl = seq.lower()
            if not (sl in exact or any(S.token_match(sl, k) for k in keys)):
                continue
            seqs[seq].setdefault(flip_key(fm.group("n"), fac), sha)
            m = meta.setdefault(seq, {"date": "", "prompt": v.get("prompt", ""), "item": v.get("item")})
            m["date"] = max(m["date"], v.get("date", "") or "")
    out = [{"kind": "artpipe", "faces": f, "date": meta[k]["date"], "label": f"flight frames {k}", "seq": k,
            "detail": f"{meta[k]['date']} · {len(f)} frames · {meta[k]['item'] or ''}",
            "prompt": (meta[k]["prompt"] or "")[:240], "bound": False}
           for k, f in sorted(seqs.items(), key=lambda kv: meta[kv[0]]["date"], reverse=True)]
    for pre in prefixes:
        faces = {}
        for (mod, rel), ev in idx.live.items():
            pt = L.parse_texfile(rel)
            fm = FLIP_RES_RE.match(pt["res"])
            if fm and not pt["mask"] and pt["res"].startswith(pre) and pt["facing"] in FLIP_FACINGS:
                faces.setdefault(flip_key(fm.group("n"), pt["facing"]), ev["sha"])
        if faces:
            out.insert(0, {"kind": "live", "faces": faces, "date": "", "winner": True, "bound": True, "prefix": pre,
                           "label": f"IN GAME — {pre.rsplit('/', 1)[-1]}", "prompt": "",
                           "detail": f"the flip-book the game draws now ({len(faces)} frames under {pre})"})
    return out


def flip_layout(cols: list[dict]) -> tuple[list[str], int, list[str]]:
    """(face keys in grid order, frame count, facings present) for a flip-book graphic."""
    keys = {k for c in cols for k in c["faces"]}
    n = max([int(k.split("_")[0]) for k in keys] + [0])
    fac = [f for f in FLIP_FACINGS if any(k.endswith("_" + f) for k in keys)]
    return [flip_key(i, f) for f in fac for i in range(1, n + 1)], n, fac


def _assign_letters(cols: list[dict], prev: dict, reserved=()) -> None:
    """Reuse the remembered letter for a column whose pictures are unchanged; new columns take the next letter
    never used on this row before (remembered or reserved). Letters are append-only: a set keeps its letter for
    good and a vanished set's letter is never handed to another set."""
    back = {}
    for l, f in (prev or {}).items():
        back.setdefault(tuple(sorted(f.items())), l)
    used = set((prev or {}).keys()) | set(reserved or ())
    for c in cols:
        l = back.get(_fkey(c))
        if l and l not in {d.get("letter") for d in cols}:
            c["letter"] = l
    free = (l for l in LETTERS if l not in used)
    for c in cols:
        if not c.get("letter"):
            c["letter"] = next(free)


def _merge_memory(ruled_rows: dict, prev_rows: dict) -> dict:
    """Letter memory per row: the ruled snapshot's letters win; a later snapshot adds only letters (and sets)
    the ruled one did not have. Every letter either ever carried stays reserved."""
    out = {}
    for k in set(ruled_rows) | set(prev_rows):
        r, p = ruled_rows.get(k) or {}, prev_rows.get(k) or {}
        cols = dict(r.get("columns") or {})
        labels, gof = dict(r.get("labels") or {}), dict(r.get("graphic_of") or {})
        have = {tuple(sorted(f.items())) for f in cols.values()}
        for l, f in (p.get("columns") or {}).items():
            if l not in cols and tuple(sorted(f.items())) not in have:
                cols[l] = f
                have.add(tuple(sorted(f.items())))
                if l in (p.get("labels") or {}):
                    labels[l] = p["labels"][l]
                if l in (p.get("graphic_of") or {}):
                    gof[l] = p["graphic_of"][l]
        reserved = set(r.get("reserved") or []) | set(p.get("reserved") or []) | set(r.get("columns") or {}) \
            | set(p.get("columns") or {})
        out[k] = {"columns": cols, "labels": labels, "graphic_of": gof, "reserved": sorted(reserved, key=LETTERS.index),
                  "subject_key": r.get("subject_key") or p.get("subject_key"), "res": r.get("res") or p.get("res")}
    return out


def _kept_cols(cols: list[dict], mem: dict, used: set) -> list[dict]:
    """A set the owner's decision names (decision / pick / variant letter) that this rebuild no longer finds
    keeps its letter as a KEPT column with the very pictures he ruled on, so the letter still resolves."""
    have = {c["letter"] for c in cols}
    out = []
    for l in sorted(used - have, key=LETTERS.index):
        f = (mem.get("columns") or {}).get(l)
        if not f:
            continue
        lab = (mem.get("labels") or {}).get(l) or f"set {l}"
        if lab.startswith("IN GAME"):          # it no longer is (gate req 15 refuses a kept set claiming to be installed)
            lab = "WAS in game, no longer installed — " + lab[len("IN GAME — "):]
        out.append({"kind": "kept", "letter": l, "faces": dict(f), "label": lab, "date": "", "winner": False,
                    "prompt": "", "bound": False,
                    "detail": "no longer among this row's current pictures — kept because your decision names it "
                              "(the exact pictures you ruled on)"})
    return out


RECOMMEND: dict = {}     # artpipe job family -> the agent's one-line reason (art_sheet --recommend FAM=WHY)


def _recommended(g: dict):
    """(letter, why) of the column whose render family the agent recommends (--recommend), else None."""
    for c in g["cols"]:
        m = re.match(r"render (\S+)", c.get("label") or "")
        if m and m.group(1) in RECOMMEND:
            return c["letter"], f"agent recommends: {RECOMMEND[m.group(1)]}"
    return None


def _graphic_prefill(g: dict, rulings: list[dict]):
    """(key, why, source) — source: sit1 | ruled | inferred | none."""
    rec = _recommended(g)
    if rec:
        return rec[0], rec[1], "inferred"
    p = g.get("prior")
    if p:
        pf = set((p.get("picked_faces") or {}).values())
        for c in g["cols"]:
            if pf and pf & set(c["faces"].values()):
                return c["letter"], f"your earlier pick ({SIT1}): {p.get('picked_label') or p.get('decision')}", "sit1"
        dec = (p.get("decision") or "").strip()
        if dec in ("redo", "hold"):
            return dec, f"your earlier ruling ({SIT1}): {dec}", "sit1"
    if not g["cols"]:
        return "", "", "none"
    if g["res"] is None:
        return g["cols"][0]["letter"], "inferred: newest render found by name — nothing of ours ships art for this yet", "inferred"
    letter, why, contested = prefill_for({"cols": g["cols"]}, rulings)
    if p:
        why = f"your {SIT1} pick is no longer among these pictures — " + why
    return letter, why, ("inferred" if contested else "ruled")


BIOME_BODY = r"""
(function () {  // freshness banner (built at, how many prior rulings are reflected) — always visible under the title
  const add = () => { let fr = ''; try { fr = JSON.parse(document.getElementById('CONFIG').textContent).freshness || ''; } catch (e) {}
    if (!fr || document.getElementById('freshBanner')) return;
    const h = document.querySelector('header .hrow'); if (!h) return;
    const d = document.createElement('div'); d.id = 'freshBanner'; d.className = 'bs-fresh-banner'; d.innerHTML = fr;
    h.insertAdjacentElement('afterend', d); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add();
})();

/* Layout (owner complaint 2026-10-04, "poorly constructed"): one compact strip per graphic. Each picture
   set is a card whose facings sit SIDE BY SIDE; cards wrap across the width, so a row is about one
   thumbnail tall. Provenance is a tooltip, never wallpaper. Letters are row-local; the pick buttons on
   the right show only this row's letters. */
const FACE_ABBR = { south: 'S', east: 'E', north: 'N', west: 'W', single: '' };
const faceAbbr = f => f in FACE_ABBR ? FACE_ABBR[f] : f.replace(/^(\d+)_(\w).*$/, (m, n, d) => n + d.toUpperCase());
if (!window.__bsAnim) window.__bsAnim = setInterval(() => document.querySelectorAll('.bs-play[data-anim]').forEach(el => {
  const fr = el.dataset.anim.split('|'), i = ((+el.dataset.i || 0) + 1) % fr.length;
  /* advance only once the current frame has loaded: a frame that 404s (the gate's image-less scratch copy) must not
     re-request every 66 ms, which kept headless Edge's virtual clock from ever settling (req 13 hang, 2026-10-07) */
  const im = el.querySelector('img'); if (!im || !im.complete || !im.naturalWidth) return;
  el.dataset.i = i; im.src = fr[i];
}), 66);
/* ═══ SLOTS (DESIGN 2026-10-10 §3; owner rulings by question card 2026-10-10) ═══════════════════════════════════════
   Every picture lives in a labelled SLOT — what the game draws it as. Click a picture to USE it for that slot (click it
   again to take that back), or say `redraw this slot`; a slot left alone keeps its in-game art on return. ✕ is four different things and the sheet
   says which: `✕ not for this slot` (deletes nothing), `retire` (a live picture: it stays in game until its replacement
   is installed), `leave the random pool` (pool slots only), and the small per-picture ✕ that deletes from the art store.
   A variant tick (`in random pool`) exists only where the game truly draws from a random pool and is NEVER pre-ticked;
   renders found by name must be labelled (`this is:`) before they can be used; a catch row's creature renders are
   reference only. Records are schema 2 (decisions_v2.py). SLX is pure logic over (item, record): no DOM, node-tested. */
window.artNoSelect = it => new Set((it.graphics || []).flatMap(g => g.cols.filter(c => c.noSelect).map(c => c.letter)));
window.artEnsureVariants = (it, rec) => {
  if (rec && Array.isArray(rec.variants) && !rec.variantsDefault) { const ns = window.artNoSelect(it); rec.variants = rec.variants.filter(l => !ns.has(l)); }
};
const SLX = window.SLX = {};
const _ok = (msg) => ({ ok: true, msg: msg || '' }), _no = m => ({ ok: false, msg: m });
SLX.lane = (it, gk) => (it.graphics || []).find(g => g.key === gk);
SLX.v2 = rec => {
  if (!rec) return rec;
  if ((+rec.schema || 1) < 2) {
    rec.schema = 2;
    if (Array.isArray(rec.variants) && rec.variants.length) {
      if (rec.variantsDefault) rec.legacyVariantsDefault = rec.variants; else rec.legacyVariants = rec.variants;
    }
    delete rec.variants; delete rec.variantsDefault;
  }
  rec.slots = rec.slots || {};
  return rec;
};
SLX.assigned = rec => (rec && rec.assign) || {};
/* lanes as shown: a render he labelled moves into that slot's lane (and becomes usable there) */
SLX.view = (it, rec) => {
  const asg = SLX.assigned(rec);
  const lanes = (it.graphics || []).map(g => ({ g, cols: g.cols.filter(c => !(g.lane === 'unassigned' && asg[c.letter] && SLX.lane(it, asg[c.letter]))) }));
  for (const l of lanes) {
    if (l.g.lane !== 'slot') continue;
    for (const g of it.graphics || []) if (g.lane === 'unassigned') for (const c of g.cols)
      if (asg[c.letter] === l.g.key) l.cols.push(Object.assign({}, c, { assignedHere: true }));
  }
  return lanes;
};
SLX.colIn = (it, rec, gk, L) => { const l = SLX.view(it, rec).find(x => x.g.key === gk); return l ? l.cols.find(c => c.letter === L) : null; };
/* owner provenance (owner 2026-10-12; decisions_v2.decision_is_his): the page seeds every row's `decision` with the agent's
   prefill. That seed is a SUGGESTION, never an answer: it reads as decided only once his click stamped it (decidedAt), it
   was carried from his earlier ruling, or it overrides the prefill. */
SLX.decisionIsHis = rec => {
  const d = ((rec || {}).decision || '').trim();
  if (!d) return false;
  if (rec.decidedAt || rec.carriedRuledAt) return true;
  if (!('prefill' in rec)) return !!rec.at;          /* never seeded by a prefilling page: a saved letter is his */
  return rec.prefill != null && rec.prefill !== '' && d !== rec.prefill;
};
SLX.prefillOnly = rec => (!SLX.decisionIsHis(rec) && ((rec || {}).decision || '').trim()) || '';
SLX.state = (it, rec, g) => {
  const s = ((rec || {}).slots || {})[g.key];
  if (s && s.state && !s.migrated) return s;
  if (g.primary && SLX.decisionIsHis(rec)) {
    const d = rec.decision;
    if (d === 'redo') return { state: 'redraw' };
    if (d && d.length === 1) return { state: 'pick', pick: d };
  }
  const p = ((rec || {}).picks || {})[g.key];
  if (p) return { state: 'pick', pick: p };
  return s && s.state ? s : { state: '' };
};
SLX.inGame = g => g.cols.filter(c => c.winner && !c.purgedLive);
SLX.list = (rec, key, gk) => new Set((((rec || {})[key] || {})[gk]) || []);
SLX.putList = (rec, key, gk, set) => { rec[key] = rec[key] || {}; const a = [...set].sort(); if (a.length) rec[key][gk] = a; else delete rec[key][gk]; };
SLX.setSlot = (it, rec, g, st) => {
  SLX.v2(rec);
  const now = new Date().toISOString();
  if (!st || !st.state) delete rec.slots[g.key];
  else rec.slots[g.key] = Object.assign({ slot_id: (g.slot || {}).id || null, at: now }, st);
  if (g.primary) {
    rec.decision = !st || !st.state ? '' : st.state === 'pick' ? st.pick : st.state === 'redraw' ? 'redo'
      : st.state === 'accept' ? ((SLX.inGame(g)[0] || {}).letter || '') : '';
    rec.decidedAt = now;
  } else if (rec.picks && rec.picks[g.key] !== undefined) {
    if (st && st.state === 'pick') rec.picks[g.key] = st.pick; else delete rec.picks[g.key];
  }
};
SLX.pick = (it, rec, gk, L) => {
  const g = SLX.lane(it, gk);
  if (!g) return _no('no such slot');
  if (g.lane === 'reference') return _no('These are pictures of the LIVING creature, shown for reference — they cannot be used as the catch.');
  if (g.lane === 'unassigned') return _no('Say what render ' + L + ' is first (the "this is" box) — an unassigned render cannot be used.');
  const c = SLX.colIn(it, rec, gk, L);
  if (!c) return _no('Set ' + L + ' is not in this slot.');
  if (c.noSelect) return _no('Set ' + L + ' is placeholder art — it cannot be picked.');
  if (c.purgedLive) return _no('You purged set ' + L + '; it cannot be picked.');
  const cur = SLX.state(it, rec, g);
  if (cur.state === 'pick' && cur.pick === L) { SLX.setSlot(it, rec, g, null); return _ok('took back ' + L); }
  SLX.v2(rec);
  /* pick and ✕ of one set cannot both stand: using it clears its ✕ marks (DESIGN §3.3 guard 2) */
  for (const k of ['reject', 'retire']) { const s = SLX.list(rec, k, gk); s.delete(L); SLX.putList(rec, k, gk, s); }
  const shas = new Set(Object.values(c.faces || {}));
  if (rec.purge) rec.purge = rec.purge.filter(x => !shas.has(x));
  SLX.setSlot(it, rec, g, { state: 'pick', pick: L, set_id: c.setId });
  return _ok();
};
SLX.slotButton = (it, rec, gk, state) => {
  const g = SLX.lane(it, gk);
  if (!g || g.lane !== 'slot') return _no('not a slot');
  const cur = SLX.state(it, rec, g);
  SLX.setSlot(it, rec, g, cur.state === state ? null : { state });
  return _ok();
};
/* the only picture(s) the game draws in this slot are all being sent away and nothing new is picked: the slot becomes a
   REDRAW and the old picture stays in game until the new one is installed (owner ruling, question card 2026-10-10) */
SLX._maybeRedraw = (it, rec, g) => {
  const gone = new Set([...SLX.list(rec, 'reject', g.key), ...SLX.list(rec, 'retire', g.key), ...((SLX.poolRec(rec, g.key).remove) || [])]);
  const live = SLX.inGame(g).filter(c => !gone.has(c.letter));
  const st = SLX.state(it, rec, g);
  if (SLX.inGame(g).length && !live.length && st.state !== 'pick' && !(SLX.poolRec(rec, g.key).add || []).length) {
    SLX.setSlot(it, rec, g, { state: 'redraw' });
    return 'Nothing would be left in "' + ((g.slot || {}).label || 'this slot') + '": it becomes a REDRAW, and ' + SLX.inGame(g).map(c => c.letter).join(', ') + ' stays in game until the new picture is installed.';
  }
  return '';
};
SLX.reject = (it, rec, gk, L) => {
  const g = SLX.lane(it, gk);
  if (!g || g.lane !== 'slot') return _no('not a slot');
  SLX.v2(rec);
  const s = SLX.list(rec, 'reject', gk);
  if (s.has(L)) { s.delete(L); SLX.putList(rec, 'reject', gk, s); return _ok(); }
  s.add(L); SLX.putList(rec, 'reject', gk, s);
  const st = SLX.state(it, rec, g);
  if (st.state === 'pick' && st.pick === L) SLX.setSlot(it, rec, g, null);
  const pr = SLX.poolRec(rec, gk); if ((pr.add || []).includes(L)) SLX.putPool(it, rec, g, Object.assign({}, pr, { add: pr.add.filter(x => x !== L) }));
  return _ok(SLX._maybeRedraw(it, rec, g));
};
SLX.retire = (it, rec, gk, L) => {
  const g = SLX.lane(it, gk);
  if (!g || g.lane !== 'slot') return _no('not a slot');
  SLX.v2(rec);
  const s = SLX.list(rec, 'retire', gk);
  if (s.has(L)) { s.delete(L); SLX.putList(rec, 'retire', gk, s); return _ok(); }
  s.add(L); SLX.putList(rec, 'retire', gk, s);
  { const st = SLX.state(it, rec, g); if (st.state === 'pick' && st.pick === L) SLX.setSlot(it, rec, g, null); }
  /* retire + replace in ONE pass (owner 2026-10-12): with another set in use here, the retired picture leaves the game in
     the same enact that installs the replacement; with none, the slot is a redraw and it stays until replaced */
  const st2 = SLX.state(it, rec, g);
  if (st2.state === 'pick' && st2.pick !== L) return _ok(L + ' leaves the game in this same pass, replaced by ' + st2.pick + '.');
  return _ok(SLX._maybeRedraw(it, rec, g) || (L + ' stays in game until its replacement is installed — use another set here to replace it in this same pass.'));
};
SLX.poolRec = (rec, gk) => (((rec || {}).pool || {})[gk]) || { add: [], remove: [] };
SLX.putPool = (it, rec, g, p) => {
  rec.pool = rec.pool || {};
  if (!p.baseline) p.baseline = SLX.inGame(g).map(c => c.setId).filter(Boolean).sort();
  if (!(p.add || []).length && !(p.remove || []).length) delete rec.pool[g.key]; else rec.pool[g.key] = p;
};
SLX.poolToggle = (it, rec, gk, L) => {
  const g = SLX.lane(it, gk);
  if (!g || !g.pool) return _no('Set ' + L + ' is not in a random pool — the game never draws it at random, so it cannot be a variant.');
  const c = SLX.colIn(it, rec, gk, L);
  if (!c) return _no('no such set');
  if (c.noSelect) return _no('Set ' + L + ' is placeholder art — it cannot be kept as a variant.');
  SLX.v2(rec);
  const p = JSON.parse(JSON.stringify(SLX.poolRec(rec, gk)));
  p.add = p.add || []; p.remove = p.remove || [];
  let msg = '';
  if (c.winner) {          /* a member the game draws now: leave / rejoin the pool */
    if (p.remove.includes(L)) p.remove = p.remove.filter(x => x !== L); else p.remove.push(L);
  } else {
    if (p.add.includes(L)) p.add = p.add.filter(x => x !== L);
    else { p.add.push(L); const r = SLX.list(rec, 'reject', gk); r.delete(L); SLX.putList(rec, 'reject', gk, r); }
  }
  SLX.putPool(it, rec, g, p);
  if (c.winner && p.remove.includes(L)) {
    const st = SLX.state(it, rec, g); if (st.state === 'pick' && st.pick === L) SLX.setSlot(it, rec, g, null);
    msg = SLX._maybeRedraw(it, rec, g);
  }
  return _ok(msg);
};
SLX.addable = (rec, g, cols) => cols.filter(c => !c.winner && !c.noSelect && !c.purgedLive && !(c.kind === 'donor' && !c.ours && !c.oursRender)
  && !SLX.list(rec, 'reject', g.key).has(c.letter));
SLX.poolAddAll = (it, rec, gk) => {
  const g = SLX.lane(it, gk);
  if (!g || !g.pool) return _no('not a random pool');
  SLX.v2(rec);
  const l = SLX.view(it, rec).find(x => x.g.key === gk);
  const p = JSON.parse(JSON.stringify(SLX.poolRec(rec, gk)));
  p.add = [...new Set([...(p.add || []), ...SLX.addable(rec, g, l.cols).map(c => c.letter)])].sort();
  p.remove = p.remove || [];
  SLX.putPool(it, rec, g, p);
  return _ok();
};
SLX.assign = (it, rec, L, target) => {
  SLX.v2(rec);
  rec.assign = rec.assign || {};
  if (!target) delete rec.assign[L]; else rec.assign[L] = target;
  /* un-assigning a render takes back any use of it */
  for (const g of it.graphics || []) { const st = SLX.state(it, rec, g); if (st.state === 'pick' && st.pick === L && rec.assign[L] !== g.key && g.lane === 'slot' && !g.cols.some(c => c.letter === L)) SLX.setSlot(it, rec, g, null); }
  return _ok();
};
SLX.purgeToggle = (it, rec, sha) => {
  for (const g of it.graphics || []) {
    const st = SLX.state(it, rec, g);
    if (st.state !== 'pick') continue;
    const c = SLX.colIn(it, rec, g.key, st.pick);
    if (c && Object.values(c.faces || {}).includes(sha) && !(rec.purge || []).includes(sha))
      return _no('That picture is part of ' + st.pick + ', your pick for "' + ((g.slot || {}).label || 'this slot') + '" — take the pick back first (pick and delete cannot both stand).');
  }
  const s = new Set(rec.purge || []);
  if (s.has(sha)) s.delete(sha); else s.add(sha);
  rec.purge = [...s]; rec.purgeTouched = true;
  return _ok();
};
SLX.setAsk = (rec, path, value) => {
  SLX.v2(rec);
  rec.asks = rec.asks || {};
  const [k, sub] = path.split('.');
  if (sub) {
    const o = Object.assign({}, rec.asks[k] || {});
    if (value === '' || value == null || value === false) delete o[sub]; else o[sub] = value;
    if (Object.keys(o).length) rec.asks[k] = o; else delete rec.asks[k];
  } else if (value === '' || value == null || value === false || (Array.isArray(value) && !value.length)) delete rec.asks[k];
  else rec.asks[k] = value;
  if (!Object.keys(rec.asks).length) delete rec.asks;
  return _ok();
};
/* an old schema-1 variant tick (legacyVariants) is answered IN its row (owner, 2026-10-10: "handle it within the biome
   sheets themselves"): keep = it is his (ships on a random pool, else protects its pictures), drop = not his. Clicking the
   lit answer again takes it back. Stored as legacyRuled{L: {v, at}}; read by decisions_v2.legacy_answers. */
SLX.legacyState = (rec, L) => ((((rec || {}).legacyRuled || {})[L]) || {}).v || '';
SLX.legacyRule = (rec, L, v) => {
  if (v !== 'confirm' && v !== 'drop') return _no('keep or drop only');
  if (!((rec || {}).legacyVariants || []).includes(L)) return _no(L + ' is not an old tick on this row');
  rec.legacyRuled = Object.assign({}, rec.legacyRuled || {});
  if (SLX.legacyState(rec, L) === v) delete rec.legacyRuled[L];
  else rec.legacyRuled[L] = { v, at: new Date().toISOString() };
  if (!Object.keys(rec.legacyRuled).length) delete rec.legacyRuled;
  return _ok();
};
SLX.legacyOpen = rec => ((rec || {}).legacyVariants || []).filter(L => !SLX.legacyState(rec, L));
SLX.legacyHtml = (it, rec, L, pool) => {
  const st = SLX.legacyState(rec, L), id = esc(it.id);
  const tip = pool === undefined ? 'an old variant tick from before 2026-10-10 that may have been the machine\'s default, not yours. keep = it is yours (on a random pool it ships as one of the pictures the game picks at random; elsewhere it only protects its pictures from deletion). drop = not yours: it ships nothing and protects nothing. Unanswered = ships nothing, pictures stay protected.'
    : pool ? 'old variant tick from before 2026-10-10 (may have been the machine\'s default). keep = it ships as one of the pictures the game picks at random for this slot. drop = it ships nothing. Unanswered = ships nothing, pictures stay protected.'
    : 'old variant tick from before 2026-10-10 (may have been the machine\'s default). This slot has no random pool, so keep = only protects its pictures from deletion; drop = no protection. Nothing else changes either way.';
  const b = (v, lab, cls) => `<button class="sl-b sl-oldb ${st === v ? cls : ''}" data-act="legacy" data-id="${id}" data-l="${L}" data-v="${v}" title="${esc(tip)}">${lab}</button>`;
  const head = st === 'confirm' ? '✓ old tick kept' : st === 'drop' ? 'old tick dropped' : 'was ticked before — keep?';
  return `<span class="sl-oldq sl-old-${st || 'open'}" title="${esc(tip)}"><i class="sl-old">${pool === undefined ? esc(L) + ': ' : ''}${head}</i>${b('confirm', 'keep', 'on')}${b('drop', 'drop', 'bad')}</span>`;
};
SLX.needsYou = (it, rec) => {
  const out = [];
  /* no "accept unchanged" control (owner 2026-10-12): a slot he leaves alone keeps what the game draws when he returns the
     sheet, so only a required slot with NOTHING in game needs his answer */
  for (const g of it.graphics || []) if (g.lane === 'slot' && (g.slot || {}).required && !SLX.state(it, rec, g).state && !SLX.inGame(g).length) out.push((g.slot || {}).label || g.key);
  const un = (it.graphics || []).filter(g => g.lane === 'unassigned').flatMap(g => g.cols).filter(c => !SLX.assigned(rec)[c.letter]);
  if (un.length) out.push(un.length + ' render' + (un.length === 1 ? '' : 's') + ' unassigned');
  return out;
};
SLX.conflicts = (it, rec) => {
  const out = [], purge = new Set((rec || {}).purge || []);
  for (const g of it.graphics || []) {
    const st = SLX.state(it, rec, g);
    if (st.state !== 'pick') continue;
    const c = SLX.colIn(it, rec, g.key, st.pick);
    if (c && Object.values(c.faces || {}).some(x => purge.has(x))) out.push(st.pick + ' is your pick AND marked ✕ delete — choose one');
    if (!c && g.lane === 'slot' && g.primary && (it.graphics || []).some(x => x.lane === 'unassigned' && x.cols.some(y => y.letter === st.pick)))
      out.push('your row pick ' + st.pick + ' is an unassigned render — say what it is (the "this is" box)');
    else if (!c && g.lane === 'slot' && !(it.graphics || []).some(x => x.cols.some(y => y.letter === st.pick)))
      out.push('your pick ' + st.pick + ' for ' + ((g.slot || {}).label || 'this slot') + ' is no longer on the sheet (its pictures were deleted) — pick again or redraw');
  }
  /* an old ✕ on the ONLY picture the game draws in a slot now means REDRAW (owner ruling by question card 2026-10-10) —
     shown for him to confirm, never filed on his behalf */
  for (const g of it.graphics || []) {
    if (g.lane !== 'slot' || SLX.state(it, rec, g).state) continue;
    const ig = SLX.inGame(g);
    if (ig.length && ig.every(c => Object.values(c.faces || {}).every(x => purge.has(x))))
      out.push(ig.map(c => c.letter).join(', ') + ' is the only picture of ' + ((g.slot || {}).label || 'this slot') + ' and is marked ✕ — that now means REDRAW (it stays in game until replaced): click "redraw this slot" to confirm');
  }
  return out;
};
const _itemBody = it => {
  const d = (typeof DEC !== 'undefined' && DEC[it.id]) || {};
  const purge = new Set(d.purge || []);
  const legacy = new Set(d.legacyVariants || []);
  const A = (act, extra, label, cls, title) => `<button class="sl-b ${cls || ''}" data-act="${act}" data-id="${esc(it.id)}"${extra} title="${esc(title || '')}">${label}</button>`;
  const cell = (c, f) => {
    const s = c.faces[f];
    if (!s) return `<div class="bs-cell bs-gap" title="no ${f} picture in this set">—</div>`;
    const t = it.thumbs[s];
    if (!t) return `<div class="bs-cell bs-gap" title="picture not archived">?</div>`;
    const p = purge.has(s);
    const btn = c.purgeable ? `<button class="ac-purge${p ? ' on' : ''}" title="DELETE this one picture from the art store so it never appears again (deletes bytes — not the same as 'not for this slot')" data-act="purge" data-id="${esc(it.id)}" data-sha="${s}">${p ? '✕ deleting' : '✕'}</button>` : '';
    const ab = faceAbbr(f);
    return `<div class="bs-cell${p ? ' ac-purged' : ''}"><div class="thumb ac-thumb" data-zoom="${(it.fulls || {})[s] || t}" data-cap="${esc(it.label)} · ${c.letter} · ${f} · full resolution"><img src="${t}" loading="lazy" alt=""></div>${ab ? `<span class="bs-face">${ab}</span>` : ''}${btn}</div>`;
  };
  /* flip-book (wing-beat) sets: one grid row per facing, a looping playback cell first, then frames 1..N */
  const faces = (c, g) => {
    if (!g.flip) return `<div class="bs-faces">${g.facings.map(f => cell(c, f)).join('')}</div>`;
    const rows = g.flipFacings.map(face => {
      const ks = g.facings.filter(k => k.endsWith('_' + face));
      const fr = ks.map(k => c.faces[k] && it.thumbs[c.faces[k]]).filter(Boolean);
      const play = fr.length ? `<div class="bs-cell bs-play" title="${face}: the frames looping at half game speed" data-anim="${fr.join('|')}"><img src="${fr[0]}" alt=""><span class="bs-face">▶${FACE_ABBR[face]}</span></div>` : '<div class="bs-cell bs-gap">—</div>';
      return play + ks.map(k => cell(c, k)).join('');
    }).join('');
    return `<div class="bs-faces bs-frames" style="grid-template-columns:repeat(${g.nframes + 1},auto)">${rows}</div>`;
  };
  const slotLanes = (it.graphics || []).filter(g => g.lane === 'slot');
  const col = (c, g) => {
    const st = SLX.state(it, d, g);
    const picked = st.state === 'pick' && st.pick === c.letter;
    const rej = SLX.list(d, 'reject', g.key).has(c.letter), ret = SLX.list(d, 'retire', g.key).has(c.letter);
    const pr = SLX.poolRec(d, g.key), inAdd = (pr.add || []).includes(c.letter), leaves = (pr.remove || []).includes(c.letter);
    const tip = `${c.label}\n${c.detail}${c.ppc ? `\n\nresolution: ${c.srcPx[0]}×${c.srcPx[1]} px over the ${it.scale.kind === 'plant' ? 'quad' : 'drawSize'} = ${c.ppc} px/cell` : ''}${c.also ? '\n\nidentical copies:\n' + c.also.join('\n') : ''}${c.prompt ? '\n\nprompt: ' + c.prompt : ''}`;
    const X = ` data-g="${esc(g.key)}" data-l="${c.letter}"`;
    const badges = [c.winner ? `<i class="sl-ig">IN GAME${g.pool ? ' · in pool' : ''}</i>` : '',
      c.assignedHere ? '<i class="sl-asg">labelled by you</i>' : '',
      legacy.has(c.letter) ? SLX.legacyHtml(it, d, c.letter, !!g.pool) : '',
      c.placeholder ? `<i class="bs-ph" title="${esc(c.placeholder)}">PLACEHOLDER</i>` : '',
      c.purgedLive ? `<i class="bs-ph" title="You purged this picture. The game still shows it until a replacement is installed.">you purged this — still live until replaced</i>` : ''].join('');
    const head = `<div class="bs-head${g.lane === 'slot' && !c.purgedLive && !c.noSelect ? ' bs-pick' : ''}"${g.lane === 'slot' && !c.purgedLive && !c.noSelect ? ` data-act="pick" data-id="${esc(it.id)}"${X}` : ''} title="${esc(tip)}${g.lane === 'slot' ? '\n\nclick to use this set for ' + ((g.slot || {}).label || 'this slot') : ''}"><b>${c.letter}</b>${c.near_of ? `<i class="bs-nearof" title="near-duplicate of set ${c.near_of} (dHash within ${NEAR_BITS} bits on every facing)">≈${c.near_of}</i>` : ''}<span>${esc(c.short)}</span>${c.also ? `<i class="sub">+${c.also.length}</i>` : ''}</div>`;
    let foot = '', note = '';
    if (c.noSelect) foot = '<i class="bs-novar">placeholder — cannot be used or kept</i>';
    else if (g.lane === 'reference') foot = '<i class="bs-novar">reference only</i>';
    else if (g.lane === 'unassigned') {
      const cur = SLX.assigned(d)[c.letter] || '';
      const opts = slotLanes.map(x => `<option value="${esc(x.key)}"${cur === x.key ? ' selected' : ''}>${esc((x.slot || {}).label || x.key)}</option>`).join('')
        + `<option value="not_needed"${cur === 'not_needed' ? ' selected' : ''}>not needed — none of these</option>`;
      foot = `<label class="sl-this">this is: <select data-act="assign" data-id="${esc(it.id)}"${X}><option value="">— choose —</option>${opts}</select></label>${c.hint ? `<i class="sl-hint" title="what its job name suggests — a hint, never applied for you">looks like: ${esc(c.hint)}</i>` : ''}`;
    } else if (!c.purgedLive) {
      const verbs = [A('pick', X, picked ? '✓ using this' : 'use this', picked ? 'on' : '', 'use this set for ' + ((g.slot || {}).label || 'this slot') + ' (click again to take it back)')];
      if (c.winner && g.pool) verbs.push(A('pool', X, leaves ? '✕ leaves the pool' : 'leave the random pool', leaves ? 'bad' : '', 'take this picture OUT of the random pool the game draws from (it is archived, never deleted)'));
      else if (c.winner) verbs.push(A('retire', X, ret ? '✕ retiring' : '✕ retire', ret ? 'bad' : '', 'retire this live picture from the game — it stays until its replacement is installed'));
      else {
        if (g.pool) verbs.push(A('pool', X, inAdd ? '✓ in random pool' : '+ random pool', inAdd ? 'pool' : '', 'add this set to the random pool the game draws from (never pre-ticked)'));
        verbs.push(A('reject', X, rej ? '✕ not for this slot' : '✕ not for this slot', rej ? 'bad' : '', 'this set is wrong for this slot — deletes nothing'));
      }
      foot = verbs.join('');
      if (ret && c.winner && st.state === 'pick' && st.pick !== c.letter) note = `<div class="sl-warn sl-replaced">${esc(c.letter)} leaves the game in this same pass, replaced by ${esc(st.pick)}</div>`;
      else if ((ret || leaves || rej) && c.winner) note = `<div class="sl-warn">${esc(c.letter)} stays in game until the new picture is installed</div>`;
    }
    return `<div class="bs-set ac-${c.kind}${c.winner ? ' ac-win' : ''}${picked ? ' ac-picked' : ''}${(rej || ret || leaves) ? ' sl-rej' : ''}${inAdd ? ' bs-isvar' : ''}${c.noSelect ? ' bs-phcol' : ''}">
      ${head}${badges ? `<div class="sl-badges">${badges}</div>` : ''}
      ${faces(c, g)}${note}
      ${(c.canonAdvice || []).length ? `<div class="bs-grader${c.canonFlag ? ' flag' : ''}" title="the canon grader's reading — ADVICE ONLY, it decides nothing">${c.canonAdvice.map(esc).join('<br>')}</div>` : ''}
      <div class="bs-foot">${foot}${g.primary && c.ppc ? `<i class="bs-ppc" title="resolution of this set: ${c.srcPx[0]} px wide over ${fmt(it.scale.kind === 'plant' ? it.scale.quad : (it.scale.drawSize||[])[0])} cells = ${c.ppc} px per cell (enhanced zoom resolves 128–256)">${c.ppc} px/cell</i>` : ''}</div>
    </div>`;
  };
  const chip = (g, cols) => {
    if (g.lane === 'reference') return '<span class="sl-chip ref">reference only</span>';
    if (g.lane === 'unassigned') { const n = cols.filter(c => !SLX.assigned(d)[c.letter]).length; return n ? `<span class="sl-chip need">${n} unassigned</span>` : '<span class="sl-chip done">all labelled</span>'; }
    const st = SLX.state(it, d, g), ig = SLX.inGame(g).map(c => c.letter).join(', ');
    const pr = SLX.poolRec(d, g.key), pool = ((pr.add || []).length ? ' · pool + ' + pr.add.join(', ') : '') + ((pr.remove || []).length ? ' · ' + pr.remove.join(', ') + ' leave the pool' : '');
    if (st.state === 'pick' && !cols.some(c => c.letter === st.pick)) return `<span class="sl-chip bad" title="the pick recorded for this slot names a set that is not in this slot">your pick ${esc(st.pick)} is not in this slot</span>`;
    if (st.state === 'pick') { const rt = [...SLX.list(d, 'retire', g.key)].filter(x => x !== st.pick); return `<span class="sl-chip done">using ${esc(st.pick)}${rt.length ? ' · ' + esc(rt.join(', ')) + ' retired in the same pass' : ''}${esc(pool)}</span>`; }
    if (st.state === 'accept') return `<span class="sl-chip done">accepted unchanged${ig ? ' (' + esc(ig) + ')' : ''}${esc(pool)}</span>`;
    if (st.state === 'redraw') return `<span class="sl-chip redraw">${it.dependsOn ? 'redraw waits for ' + esc(it.dependsOn) : 'redraw queued'}${ig ? ' · ' + esc(ig) + ' stays until replaced' : ''}</span>`;
    if (st.state === 'not_drawn') return '<span class="sl-chip done">not drawn</span>';
    if (g.primary && SLX.prefillOnly(d)) return `<span class="sl-chip pf" title="the agent's guess, seeded into the row — it is NOT your answer and never counts as decided. Click a picture to use it; leave the slot alone and returning the sheet keeps what the game draws now.">agent prefill ${esc(SLX.prefillOnly(d))} — not your answer${ig ? ' · returning keeps ' + esc(ig) : ''}</span>`;
    if (pool) return `<span class="sl-chip done">${esc(pool.slice(3))}</span>`;
    return (g.slot || {}).required && !SLX.inGame(g).length ? '<span class="sl-chip need">needs you — nothing in game</span>'
      : '<span class="sl-chip" title="leave it alone and returning the sheet keeps what the game draws now">unchanged — kept when you return the sheet</span>';
  };
  const sec = l => {
    const g = l.g, sl = g.slot || {};
    const ordered = l.cols.slice().sort((a, b) => LETTER_ORDER.indexOf(a.letter) - LETTER_ORDER.indexOf(b.letter));
    const st = SLX.state(it, d, g);
    const stub = c => `<details class="bs-nearstub"${st.pick === c.letter ? ' open' : ''}><summary title="set ${c.letter} looks almost the same as set ${c.near_of} — click to show it"><b>${c.letter}</b><span>≈ ${c.near_of}</span><span class="sub">near-<br>duplicate<br>▸ show</span></summary>${col(c, g)}</details>`;
    const btns = g.lane !== 'slot' ? '' : `<div class="sl-btns">${A('slot', ` data-g="${esc(g.key)}" data-v="redraw"`, it.dependsOn ? 'redraw from ' + esc(it.dependsOn) + ' (starts once it is settled)' : 'redraw this slot', st.state === 'redraw' ? 'on' : '', 'a new picture for this slot; the current one stays in game until it is installed')}${!sl.required && SLX.inGame(g).length ? '' : ''}${g.pool ? A('pooladdall', ` data-g="${esc(g.key)}"`, 'add all new renders to the pool', '', 'put every new render of ours in this slot into the random pool (nothing is ever pre-ticked)') : ''}<span class="sub">click a picture to use it</span></div>`;
    const prior = g.prior ? `<div class="bs-prior" title="${esc(g.prior.was)}">${esc(g.prior.text)}${g.prior.note ? ' — “' + esc(g.prior.note) + '”' : ''}</div>` : '';
    return `<div class="sl-lane sl-${g.lane} sl-k-${esc(sl.kind || 'x')}" data-lane="${esc(g.key)}">
      <div class="sl-head"><b>${esc(sl.label || g.role)}</b>${chip(g, l.cols)}</div>
      <div class="sl-desc">${esc(sl.desc || '')}${g.res && g.lane === 'slot' ? ` <span class="sub" title="${esc(g.res)}">· ${esc(g.res.replace(/^_flip:/, '').split('/').pop())}</span>` : ''}${(sl.also || []).length ? ` <span class="sub">· also used by: ${esc(sl.also.join(', ').toLowerCase())}</span>` : ''}${g.pool ? ' <span class="sl-poolnote">random pool — the game picks one of these at random</span>' : ''}</div>
      ${btns}${prior}
      <div class="bs-strip">${ordered.map(c => c.near_of ? stub(c) : col(c, g)).join('') || '<span class="sub">no pictures</span>'}</div></div>`;
  };
  const lanes = SLX.view(it, d).filter(l => l.cols.length || l.g.lane === 'slot');
  const need = SLX.needsYou(it, d), confl = SLX.conflicts(it, d);
  const shownL = new Set(lanes.flatMap(l => l.cols.map(c => c.letter)));
  const legacyUnshown = (d.legacyVariants || []).filter(L => !shownL.has(L));
  const rowHead = `<div class="sl-rowhead">${need.length ? `<span class="sl-chip need">needs you: ${esc(need.join(' · '))}</span>` : confl.length ? '' : '<span class="sl-chip done">nothing here needs you — unchanged slots keep what the game draws</span>'}${confl.map(x => `<span class="sl-chip bad">${esc(x)}</span>`).join('')}${SLX.legacyOpen(d).length ? `<span class="sl-chip old" title="old variant ticks from before 2026-10-10 that may have been the machine's default: each ships nothing until you say keep (its keep / drop is on the picture)">old tick ${esc(SLX.legacyOpen(d).join(', '))}: keep or drop?</span>` : ''}${legacyUnshown.map(L => SLX.legacyHtml(it, d, L)).join('')}</div>`;
  const donorAbs = it.donorAbsent ? `<div class="bs-canonp"><div class="bs-head bs-chead"><b>donor column</b><span>${esc(it.donorAbsent)}</span></div></div>` : '';
  const canon = it.canon ? `<div class="bs-canonp"><div class="bs-head bs-chead"><b>canon</b><span>${it.canon.base ? 'entry for the base species: ' + esc(it.canon.base) : 'reference — not pickable'}</span></div>
      <div class="bs-cimgs">${it.canon.imgs.map(u => `<div class="thumb bs-cthumb" data-zoom="${u}" data-cap="canon reference · ${esc(it.canon.dir)}"><img src="${u}" loading="lazy" alt=""></div>`).join('') || '<span class="sub">entry has no images</span>'}</div>
      <div class="bs-must"><b>Must show</b><pre>${esc(it.canon.must || '(this entry lists no Must show)')}</pre>${it.canon.ruling ? `<b>Your ruling on the entry</b><pre>${esc(it.canon.ruling)}</pre>` : ''}<details><summary>visual brief</summary><pre>${esc(it.canon.brief)}</pre></details></div></div>` : '';
  const links = it.related.length ? `<div class="bs-links">related (judged separately): ${it.related.map(r => `<a href="#" data-jump="${esc(r.id)}">${esc(r.label)} <span class="sub">${esc(r.id)}</span></a> <span class="sub">${esc(r.why)}</span>`).join(' · ')}</div>` : '';
  const elsewhere = it.elsewhere.length ? `<div class="sub">also related, not in this biome: ${it.elsewhere.map(esc).join(', ')}</div>` : '';
  const purgedNote = it.purgedHidden ? `<div class="sub" title="pictures you rejected with the purge mark; they no longer appear on any sheet">${it.purgedHidden} purged picture${it.purgedHidden === 1 ? '' : 's'} hidden</div>` : '';
  const noart = it.noArt ? `<div class="bs-noart">NO ART YET — nothing found after searching every source:<div style="font-size:11px;font-weight:normal;opacity:.85;margin-top:3px;word-break:break-word">${esc(it.noArtWhy)}</div></div>` : '';
  const rline = r => `<div class="ac-r bs-r ac-t-${r.trust}" title="${esc(r.at + ' ' + r.verdict + ' · ' + r.trust + ' · ' + r.sheet + (r.note ? '\n“' + r.note + '”' : ''))}">${esc(r.at)} <b>${esc(r.verdict)}</b> <span class="sub">${esc(r.trust)} · ${esc(r.sheet)}</span> ${r.note ? '“' + esc(r.note) + '”' : ''}</div>`;
  const rs = it.rulings.slice().reverse();
  const rul = rs.length ? `<div class="ac-rulings">${rs.slice(0, 2).map(rline).join('')}${rs.length > 2 ? `<details><summary class="sub">${rs.length - 2} older ruling(s)</summary>${rs.slice(2).map(rline).join('')}</details>` : ''}</div>` : '';
  const ds = it.desc || {};
  const dtext = ds.description || '';
  const desc = !ds.def ? `<div class="bs-desc sub">in-game description: UNMEASURED — no ThingDef of this row in the live def dump</div>`
    : dtext.length > 260 ? `<details class="bs-desc" title="${esc(ds.source)}"><summary><b>${esc(ds.label)}</b> — <span class="bs-dclamp">${esc(dtext)}</span></summary></details>`
    : `<div class="bs-desc" title="${esc(ds.source)}"><b>${esc(ds.label)}</b> — ${esc(dtext || '(the def has no description)')}</div>`;
  const pf = it.prefillSource === 'sit1' ? '' : it.contested ? '<span class="mark inferred" title="' + esc(it.prefillWhy) + '">⚠ agent prefill: ' + esc(it.prefillShort) + '</span>' : '<span class="mark absent">prefill: ' + esc(it.prefillShort) + '</span>';
  const re = it.ruledElsewhere;
  const reHead = re ? `<summary class="bs-ruledsum" title="You already ruled on this subject on another sheet, so it needs no pick here. Expand to see the pictures and change your mind.">Already ruled on <b>${esc(re.sheet)}</b>: ${esc(re.pick)}${re.label ? ' — ' + esc(re.label) : ''}${re.note ? ' · “' + esc(re.note) + '”' : ''} <span class="sub">${esc(re.at)} · expand to change your mind</span></summary>` : '';
  const inner = `<div class="ac-body bs-body" style="${it.band ? 'border-left:6px solid ' + it.band + ';padding-left:8px' : ''}">
    <div class="bs-meta"><div class="effect">${esc(it.effect)}</div>
    ${it.fresh ? `<div class="bs-fresh bs-fresh-${it.fresh.state}">${esc(it.fresh.text)}</div>` : ''}
    <div class="marks"><span class="mark bs-tier bs-${it.tier}">${esc(it.tierText)}</span>${it.canonTag ? `<span class="mark bs-nocanon">${esc(it.canonTag)}</span>` : ''}${it.flags.filter(f => f !== 'NO ART YET').map(f => `<span class="mark contested">${esc(f)}</span>`).join('')}${pf}</div>
    ${desc}${links}${elsewhere}${rul}${window.artFollowedHtml(d)}${purgedNote}${noart}</div>
    <div class="bs-content"><div class="bs-graphics">${rowHead}${lanes.map(sec).join('')}${window.artAsksHtml(it, d)}</div>${scaleBlock(it)}${donorAbs}${canon}</div></div>`;
  return re ? `<details class="bs-ruled"${it.ruledOpen || d.at || d.decidedAt ? ' open' : ''}>${reHead}${inner}</details>` : inner;
};
/* requests that used to be typed into the note get their own fields (owner rulings by question card 2026-10-10: rename,
   description, make N more based on X, missing facings, size, move biome/tier, cut). The note stays for everything else.
   Each ask is its own work item in `art.py enact`, so "followed" is per ask. */
window.artAsksHtml = (it, d) => {
  const a = d.asks || {}, id = esc(it.id);
  const lanes = (it.graphics || []).filter(g => g.lane === 'slot');
  const letters = [...new Set(SLX.view(it, d).filter(l => l.g.lane === 'slot').flatMap(l => l.cols.map(c => c.letter)))].sort((x, y) => LETTER_ORDER.indexOf(x) - LETTER_ORDER.indexOf(y));
  const sel = (path, opts, cur, blank) => `<select data-act="ask" data-id="${id}" data-k="${path}">${blank !== undefined ? `<option value="">${esc(blank)}</option>` : ''}${opts.map(([v, t]) => `<option value="${esc(v)}"${String(cur ?? '') === String(v) ? ' selected' : ''}>${esc(t)}</option>`).join('')}</select>`;
  const inp = (path, cur, ph, type, w) => `<input data-act="ask" data-id="${id}" data-k="${path}" type="${type || 'text'}" value="${esc(cur ?? '')}" placeholder="${esc(ph || '')}" style="width:${w || 140}px">`;
  const laneOpts = lanes.map(g => [g.key, (g.slot || {}).label || g.key]);
  const btn3 = (path, cur, vals) => vals.map(([v, t]) => `<button class="sl-b${cur === v ? ' on' : ''}" data-act="askset" data-id="${id}" data-k="${path}" data-v="${v}">${t}</button>`).join('');
  const more = (a.more || []).map((m, i) => `<div class="sl-more">make <b>${esc(m.n)}</b> new <b>${esc(((lanes.find(g => g.key === m.slot) || {}).slot || {}).label || m.slot)}</b>${m.base ? ' based on <b>' + esc(m.base) + '</b>' : ''}${m.how ? ' — “' + esc(m.how) + '”' : ''} <button class="sl-b bad" data-act="moredel" data-id="${id}" data-v="${i}">remove</button></div>`).join('');
  const fa = a.facings || {};
  const set = Object.keys(a).filter(k => a[k] && (!Array.isArray(a[k]) || a[k].length));
  const biomes = ((typeof CFG !== 'undefined' && CFG.biomes) || []).map(b => [b.key, b.label]);
  return `<details class="sl-asks"${set.length ? ' open' : ''}><summary>Requests${set.length ? ': ' + esc(set.join(', ')) : ' — rename · description · more art · missing facings · size · move / cut'} <span class="sub">(the note box stays for anything else)</span></summary>
    <div class="sl-grid">
      <b>Name</b><div>${inp('rename.name', (a.rename || {}).name, 'new name (blank = keep)', 'text', 220)} <label><input type="checkbox" data-act="askcheck" data-id="${id}" data-k="rename.suggest"${(a.rename || {}).suggest ? ' checked' : ''}> suggest names for me</label></div>
      <b>Description</b><div>${btn3('describe', a.describe, [['keep', 'keep'], ['improve', 'improve'], ['rewrite', 'rewrite to match the chosen art']])}</div>
      <b>More art</b><div>${more}<span class="sl-addmore">make ${inp('_more.n', '2', '', 'number', 48)} new ${sel('_more.slot', laneOpts, (lanes[0] || {}).key)} versions based on ${sel('_more.base', letters.map(l => [l, l]), '', '—')} how: ${inp('_more.how', '', 'how should they differ', 'text', 200)} <button class="sl-b" data-act="moreadd" data-id="${id}">add</button></span></div>
      <b>Missing facings</b><div>draw ${['south', 'east', 'north'].map(f => `<label><input type="checkbox" data-act="facing" data-id="${id}" data-v="${f}"${(fa.faces || []).includes(f) ? ' checked' : ''}> ${f}</label>`).join(' ')} of ${sel('facings.slot', laneOpts, fa.slot, '— slot —')} from ${sel('facings.from', letters.map(l => [l, l]), fa.from, '—')}</div>
      <b>Size</b><div>body size ${inp('size.bodySize', (a.size || {}).bodySize, '', 'number', 70)} · drawn size × ${inp('size.drawScale', (a.size || {}).drawScale, '', 'number', 70)} · which pictures / what exactly: ${inp('size.scope', (a.size || {}).scope, 'e.g. adult and corpse, triple the length', 'text', 220)}</div>
      <b>Belongs</b><div>move to ${sel('move.biome', biomes, (a.move || {}).biome, 'this biome')} · tier ${sel('move.tier', [['RM', 'RM'], ['RSW', 'RSW'], ['RUT', 'RUT']], (a.move || {}).tier, 'unchanged')} · <button class="sl-b${a.cut ? ' bad' : ''}" data-act="askset" data-id="${id}" data-k="cut" data-v="1">${a.cut ? '✕ cut from this biome' : 'cut from this biome'}</button></div>
    </div></details>`;
};
const fmt = x => (x == null ? '?' : (+x).toFixed(3).replace(/\.?0+$/, ''));
/* Click-to-zoom shows the FULL-RESOLUTION file (owner, 2026-10-15), at its own pixel size up to the window, with its
   dimensions and a link that opens it alone in a new tab. Overrides the template's openZoom by global name. */
openZoom = function (src, cap) {
  const z = document.getElementById('zoom'), im = document.getElementById('zimg'), zc = document.getElementById('zcap');
  im.style.maxWidth = '94vw'; im.style.maxHeight = '86vh';
  im.onload = () => { zc.innerHTML = ''; zc.append(cap + ` · ${im.naturalWidth}×${im.naturalHeight} px `);
    const a = document.createElement('a'); a.href = src; a.target = '_blank'; a.rel = 'noopener'; a.textContent = 'open alone ↗';
    a.onclick = e => e.stopPropagation(); zc.append(a); };
  im.src = src; zc.textContent = cap; z.classList.add('on');
};
function scaleBlock(it) {
  const s = it.scale; if (!s) return '';
  if (s.status === 'none') return `<div class="bs-scale"><div class="bs-head bs-schead"><b>in-game size</b><span>none — drawn only in the UI</span></div><div class="bs-scsrc" title="${esc(s.source)}">MEASURED · ${esc(s.source)}</div></div>`;
  const size = s.kind === 'thing'
    ? `<b>${(s.footprint||[1,1]).join('×')}-cell</b> ${esc((s.category||'thing').toLowerCase())} <span class="sub">drawSize ${fmt((s.drawSize||[])[0])}×${fmt((s.drawSize||[])[1])} on its footprint (outlined), south facing</span>`
    : s.kind === 'plant'
    ? `<b>${fmt(s.quad)}-cell</b> plant <span class="sub">= drawSize.x ${fmt((s.drawSize||[])[0])} × visualSize.max ${fmt(s.visualMax)}</span>${s.mesh > 1 ? ` · <b>×${s.mesh}</b> per cell` : ''}`
    : `<b>${fmt(s.cells)} cells</b> <span class="sub">adult drawSize ${fmt((s.drawSize||[])[0])}×${fmt((s.drawSize||[])[1])}</span> · bodySize ${fmt(s.bodySize)}`;
  const sizeTip = s.kind === 'thing' ? 'graphicData.drawSize centred on the def\'s size footprint as placed (south rotation), moved by drawOffset — what the engine draws' : s.kind === 'plant' ? `Plant.Print draws a SQUARE quad of drawSize.x × visualSizeRange (max at maturity)${s.mesh > 1 ? `; maxMeshCount ${s.mesh} prints ${s.mesh} quads on a ${Math.round(Math.sqrt(s.mesh))}×${Math.round(Math.sqrt(s.mesh))} sub-grid of ONE cell` : '; one mesh, centred, lifted so its base sits on the cell edge'}` : 'the adult (last) life stage bodyGraphicData.drawSize — what the engine draws';
  const q = s.kind === 'plant' ? s.quad : (s.drawSize || [])[0];
  const vcls = !s.ppc ? '' : s.ppc < 64 ? 'bs-low' : s.ppc < 120 ? 'bs-mid' : s.ppc > 256 ? 'bs-over' : 'bs-ok';
  const res = s.img ? `<div class="bs-scl bs-scres ${vcls}" title="${esc(s.verdict)}. Enhanced zoom (owner, 2026-10-04) resolves 128–256 px per cell of the draw size; below 128 reads soft at max zoom, below 64 loses detail. Shown: set ${esc(s.set)} (${esc(s.by)}, ${esc(s.face)} facing).">set <b>${esc(s.set)}</b> · ${s.srcPx[0]}px ÷ ${fmt(q)} = <b>${s.ppc} px/cell</b> <span class="sub">${s.ppc < 64 ? 'below 64 floor' : s.ppc < 120 ? 'soft at max zoom' : s.ppc > 256 ? 'above 256 max zoom' : 'in the 128–256 zoom range'} · ${esc(s.by)}</span></div>` : `<div class="sub">${esc(s.why || '')}</div>`;
  const pic = s.img ? `<div class="bs-scimg" data-zoom="${s.full}" data-cap="${esc(it.label)} · set ${esc(s.set)} · max zoom ${s.zoomFullPpc || '?'} px/cell (human | this), then normal play 32 and zoomed out 18 px/cell, each also ×4 nearest"><img src="${s.img}" alt=""></div>` : '';
  /* every candidate set at true scale beside the vanilla human (owner, 2026-10-15), not only the picked one */
  const pg = (it.graphics || []).find(g => g.primary);
  const each = (pg ? pg.cols : []).filter(c => c.scale && c.scale.img);
  const all = each.length > 1 ? `<details class="bs-scall" open><summary class="sub">every set at its true scale beside the human (${each.length}) — click one to enlarge</summary>${each.map(c => `<div class="bs-scone${c.letter === s.set ? ' on' : ''}" data-zoom="${c.scale.full}" data-cap="${esc(it.label)} · set ${esc(c.letter)} · ${esc(c.scale.face)} · max zoom ${c.scale.zoomFullPpc || '?'} px/cell (human | this), then normal play 32 and zoomed out 18"><b>${esc(c.letter)}</b> <span class="sub">${c.scale.ppc} px/cell</span><img src="${c.scale.img}" loading="lazy" alt=""></div>`).join('')}</details>` : '';
  const refs = (s.refs || []).length ? `<details class="bs-scall bs-refs" open><summary class="sub"><b>installed canon twin, reference only</b> — not pickable, never installed from here; same true scale beside the human</summary>${s.refs.map(r => r.missing ? `<div class="sub">missing: ${esc(r.path)}</div>` : `<div class="bs-scone" data-zoom="${r.full}" data-cap="REFERENCE ONLY (not pickable) · ${esc(r.path)}"><span class="sub">${esc(r.path.split('/').pop())}</span><img src="${r.img}" loading="lazy" alt=""></div>`).join('')}</details>` : '';
  return `<div class="bs-scale"><div class="bs-head bs-schead"><b>in-game size</b><span>vanilla human beside it at the same scale · max zoom ${s.zoomPpc ? s.zoomPpc + ' px/cell' : ''}${s.zoomFitted ? ' (shrunk to fit)' : ''}${s.zoomCropped ? ' (cropped, not shrunk)' : ''} + normal play 32 · click to enlarge</span></div>${pic}${all}${refs}
    <div class="bs-scl bs-scsize" title="${esc(sizeTip)}">${size}</div>${res}
    <div class="bs-scsrc ${s.status === 'measured' ? '' : 'bs-fallback'}" title="${esc(s.source)}">${s.status === 'measured' ? 'MEASURED' : 'FALLBACK'} · ${esc(s.source)}</div></div>`;
}

const LETTER_ORDER = "%LETTERS%";
const NEAR_BITS = %NEAR%;
/* every control on a row: one delegated handler. Each act edits the row's record through SLX, then saves + repaints. */
window.__moreDraft = window.__moreDraft || {};
window.artAct = (el, ev) => {
  if (frozen) return;
  const id = el.dataset.id, it = byId.get(id);
  if (!it) return;
  const act = el.dataset.act, g = el.dataset.g, L = el.dataset.l, v = el.dataset.v, k = el.dataset.k;
  if (k && k.startsWith('_more.')) { (window.__moreDraft[id] = window.__moreDraft[id] || {})[k.slice(6)] = el.value; return; }
  const rec = DEC[id] || (DEC[id] = { decision: '', note: '', prefill: prefillOf(it) });
  let r = { ok: true };
  if (act === 'pick') r = SLX.pick(it, rec, g, L);
  else if (act === 'slot') r = SLX.slotButton(it, rec, g, v);
  else if (act === 'reject') r = SLX.reject(it, rec, g, L);
  else if (act === 'retire') r = SLX.retire(it, rec, g, L);
  else if (act === 'pool') r = SLX.poolToggle(it, rec, g, L);
  else if (act === 'pooladdall') r = SLX.poolAddAll(it, rec, g);
  else if (act === 'assign') r = SLX.assign(it, rec, L, el.value);
  else if (act === 'purge') r = SLX.purgeToggle(it, rec, el.dataset.sha);
  else if (act === 'legacy') r = SLX.legacyRule(rec, L, v);
  else if (act === 'ask') { const num = el.type === 'number'; r = SLX.setAsk(rec, k, num ? (el.value === '' ? '' : +el.value) : el.value.trim()); }
  else if (act === 'askcheck') r = SLX.setAsk(rec, k, el.checked);
  else if (act === 'askset') { const cur = k.includes('.') ? ((rec.asks || {})[k.split('.')[0]] || {})[k.split('.')[1]] : (rec.asks || {})[k]; r = SLX.setAsk(rec, k, k === 'cut' ? !cur : (cur === v ? '' : v)); }
  else if (act === 'facing') { const fa = Object.assign({}, (rec.asks || {}).facings || {}); const s = new Set(fa.faces || []); el.checked ? s.add(v) : s.delete(v); fa.faces = [...s]; r = SLX.setAsk(rec, 'facings', fa.faces.length ? fa : ''); }
  else if (act === 'moreadd') {
    const dr = window.__moreDraft[id] || {}, lanes = (it.graphics || []).filter(x => x.lane === 'slot');
    const m = { slot: dr.slot || (lanes[0] || {}).key, n: Math.max(1, Math.min(8, +(dr.n || 2))), base: dr.base || null, how: (dr.how || '').trim() };
    r = SLX.setAsk(rec, 'more', [...(((rec.asks || {}).more) || []), m]);
    delete window.__moreDraft[id];
  } else if (act === 'moredel') { const ms = (((rec.asks || {}).more) || []).slice(); ms.splice(+v, 1); r = SLX.setAsk(rec, 'more', ms); }
  else return;
  if (!r.ok) { if (typeof showErr === 'function') showErr(r.msg); return; }
  if (r.msg && typeof banner === 'function') { try { banner('info', esc(r.msg)); } catch (e) {} }
  rec.at = new Date().toISOString();
  queue(id); patchRow(id); paintCounts();
};
document.addEventListener('click', e => {
  const a = e.target.closest('[data-act]');
  if (a && a.tagName !== 'SELECT' && a.tagName !== 'INPUT') { e.preventDefault(); e.stopPropagation(); window.artAct(a, e); return; }
  const j = e.target.closest('[data-jump]');
  if (j) {
    e.preventDefault(); e.stopPropagation();
    const node = document.querySelector(`.row[data-id="${cssEsc(j.dataset.jump)}"]`);
    if (node) { node.scrollIntoView({ block: 'center' }); node.classList.add('bs-flash'); setTimeout(() => node.classList.remove('bs-flash'), 1500); }
    else alert('That row is hidden by the current filter.');
  }
}, true);
document.addEventListener('change', e => { const a = e.target.closest('select[data-act],input[data-act]'); if (a) { e.stopPropagation(); window.artAct(a, e); } }, true);
/* `#q=<text>` in the URL opens the sheet filtered to matching rows (for a link to one row, and for screenshots); it is
   not saved as his filter */
addEventListener('load', () => setTimeout(() => {
  const m = (location.hash || '').match(/^#q=(.+)$/), q = document.getElementById('q');
  if (m && q && typeof render === 'function') { q.value = decodeURIComponent(m[1]); render(); }
}, 50));
/* rebuilt-sheet notice: poll the served page every ~60 s; when its build stamp (the gate stamp, else a hash of the HTML) differs
   from what this tab loaded, show a banner. NEVER auto-reloads: an unsaved note would be lost. */
(() => {
  const fp = t => { const m = t.match(/<meta name="scaled-review-gate" content="([^"]*)">/); if (m) return m[1];
    let h = 2166136261; for (let i = 0; i < t.length; i += 7) { h ^= t.charCodeAt(i); h = Math.imul(h, 16777619); } return 'h' + (h >>> 0) + ':' + t.length; };
  const get = () => fetch(location.href, { cache: 'no-store' }).then(r => r.ok ? r.text() : null).then(t => t && fp(t)).catch(() => null);
  let base = null, shown = false;
  const banner = () => { if (shown) return; shown = true; const d = document.createElement('div');
    d.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:#b8860b;color:#000;padding:10px 14px;font:600 15px sans-serif;display:flex;gap:14px;align-items:center;box-shadow:0 2px 8px #000';
    d.innerHTML = '<span>This sheet was rebuilt with new content — reload (your picks are saved)</span><button style="font:600 14px sans-serif;padding:4px 12px;cursor:pointer">Reload now</button><button style="font:14px sans-serif;padding:4px 10px;cursor:pointer">dismiss</button>';
    d.children[1].onclick = () => location.reload(); d.children[2].onclick = () => d.remove(); document.body.appendChild(d); };
  get().then(f => { base = f; });
  setInterval(() => get().then(f => { if (f && base && f !== base) banner(); }), 60000);
})();
window.itemBody = it => { try { return _itemBody(it); } catch (e) { return `<div class="bs-noart">row render error (this row only; the sheet is intact): ${esc(String(e && e.message || e))}</div>`; } };
"""

BIOME_STYLE = """<style>
.bs-fresh-banner{font-size:12.5px;padding:6px 10px;margin:4px 0;border:1px solid #6b5a3a;border-radius:6px;background:#2a2116;color:#e9dcc0;max-height:30vh;overflow:auto}
.bs-fresh{font-size:12px;padding:2px 6px;border-radius:4px;margin:2px 0;display:inline-block}
.bs-fresh-reflected,.bs-fresh-redrawn{background:#1f3a24;color:#9fe0a8}
.bs-fresh-awaiting,.bs-fresh-refiled{background:#3a3218;color:#f0d68a}
.bs-fresh-conflict{background:#4a2f10;color:#ffc070}
.bs-fresh-not_acted{background:#a01818;color:#fff;font-weight:700}
</style>
<style>
.bs-body{display:flex;gap:14px;align-items:flex-start}
.bs-meta{flex:0 0 300px;min-width:0}
.bs-meta .effect{font-size:12px}
.bs-r{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bs-content{flex:1;min-width:0;display:flex;flex-wrap:wrap;gap:10px;align-items:flex-start}
@media (max-width:1450px){.bs-body{display:block}.bs-meta{margin-bottom:4px}
  .bs-cell,.bs-cell .ac-thumb{width:72px;height:72px;flex-basis:72px}}
.bs-graphics{flex:1 1 340px;min-width:0;display:flex;flex-wrap:wrap;gap:6px 16px;align-items:flex-start}
.bs-g{max-width:100%;min-width:0}
.bs-gh{font-size:12px;color:#d8c7a8;margin:2px 0}
.bs-strip{display:flex;flex-wrap:wrap;gap:6px;align-items:flex-start}
.bs-set{border:1px solid var(--line);border-radius:6px;padding:3px;background:#0f1216;max-width:100%}
.bs-set.ac-win{border-color:var(--info)}
.bs-set.ac-picked{border-color:var(--ok);box-shadow:0 0 0 2px #5ac37f66}
.bs-head{display:flex;gap:5px;align-items:baseline;font-size:11px;line-height:1.3;height:1.35em;overflow:hidden;color:var(--ink);width:0;min-width:100%;box-sizing:border-box;padding:0 2px}
.bs-head span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.bs-head b{font-size:13px;color:var(--accent)}
.bs-head i{font-style:normal;flex:none}
.bs-set.ac-artpipe .bs-head span{color:#d9b8ff}.bs-set.ac-git .bs-head span{color:#9fb3c8}.bs-set.ac-donor .bs-head span{color:#e8b64c}
.bs-set.ac-win .bs-head span{color:#8ac3e8;font-weight:600}
.bs-pick{cursor:pointer}.bs-set:hover{border-color:#3d4653}.bs-set.ac-picked:hover{border-color:var(--ok)}
.bs-faces{display:flex;gap:3px;cursor:default}
.bs-frames{display:grid;gap:3px}
.bs-play{outline:2px solid #e8b64c;outline-offset:-2px}
.bs-cell{position:relative;width:86px;height:86px;display:flex;align-items:center;justify-content:center}
.bs-cell .ac-thumb{width:86px;height:86px;flex:0 0 86px}
/* the wing-beat playback frame is a bare <img> (no .ac-thumb): a wide flight sprite at natural size overflowed its cell
   and sat on top of the set's footer, so the variant button under it could not be clicked (DESIGN 2026-10-10 §2) */
.bs-cell{overflow:hidden}
.bs-play img{max-width:100%;max-height:100%;object-fit:contain;pointer-events:none}
.bs-gap{color:#3a4250;font-size:18px;border:1px dashed #222a33;border-radius:5px}
.bs-face{position:absolute;left:3px;bottom:2px;font-size:9.5px;color:#8a95a5;background:#0b0d10cc;border-radius:2px;padding:0 3px;pointer-events:none}
.bs-nearstub{align-self:stretch}
.bs-nearstub>summary{list-style:none;cursor:pointer;height:100%;min-height:60px;box-sizing:border-box;width:58px;border:1px dashed #3d4653;border-radius:6px;padding:3px;font-size:10.5px;color:var(--dim);display:flex;flex-direction:column;gap:2px;line-height:1.25}
.bs-nearstub>summary::-webkit-details-marker{display:none}
.bs-nearstub>summary b{font-size:13px;color:var(--accent)}
.bs-nearstub[open]{display:flex;gap:4px}.bs-nearstub[open]>summary{width:auto;min-height:0;height:auto}
.bs-nearstub[open]>summary .sub{display:none}
.bs-nearof{color:#9fb3c8;font-size:10.5px}
.bs-grader{font-size:10.5px;line-height:1.3;color:var(--dim);margin-top:3px;max-width:340px;white-space:normal}
.bs-grader.flag{color:#e8c070;border-left:2px solid #c9902c;padding-left:4px}
.bs-foot{display:flex;flex-wrap:wrap;gap:3px 6px;align-items:center;justify-content:space-between;margin-top:3px;width:0;min-width:100%}
.bs-var{font-size:10.5px;padding:1px 7px;border-radius:4px;border:1px solid #2f4a35;background:#0f1612;color:#7fae86;cursor:pointer;opacity:.75}
.bs-var:hover{opacity:1}.bs-var.on{background:#2f7a45;color:#fff;border-color:#5ac37f;opacity:1}
.bs-set.bs-isvar{border-style:dashed;border-color:#5ac37f}
.bs-desc{font-size:12px;line-height:1.4;color:#d8cdb8;margin:4px 0;padding:3px 6px;border-left:3px solid #6a5a3a;background:#15120d}
.bs-desc b{color:#e8d6a8}
details.bs-desc>summary{cursor:pointer;list-style:none}
details.bs-desc>summary::-webkit-details-marker{display:none}
details.bs-desc:not([open]) .bs-dclamp{display:-webkit-inline-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden;vertical-align:top}
details.bs-desc:not([open])>summary::after{content:" ▸ more";color:#e8b64c;font-size:11px}
details.bs-desc[open]>summary::after{content:" ▴ less";color:#e8b64c;font-size:11px}
.bs-canonp{flex:0 0 300px;border:1px solid #5a4a2a;background:#14110c;border-radius:6px;padding:3px 5px}
.bs-chead span{color:#e8b64c}.bs-chead b{color:#e8b64c}
.bs-cimgs{display:flex;gap:4px;flex-wrap:wrap;margin:3px 0}
.bs-cthumb{width:68px;height:68px;flex:0 0 68px}
.bs-must{font-size:11.5px;color:#c3cad6;max-height:112px;overflow:auto}
.bs-must pre{white-space:pre-wrap;font:inherit;margin:1px 0 4px}
.bs-must summary{cursor:pointer;color:var(--dim)}
.bs-prior{font-size:11.5px;color:#9fe0a8;margin:1px 0 2px}
.bs-links{font-size:12px;margin:3px 0;color:#d8c7a8}.bs-links a{color:#e8b64c}
.bs-noart{display:inline-block;font-size:12.5px;font-weight:700;color:#000;background:#e06c6c;padding:4px 10px;border-radius:5px;margin:5px 0 0}
.bs-tier{border-color:#5a4a2a}.bs-canon{background:#3a2c10;color:#e8b64c}.bs-ours{background:#10283a;color:#8ac3e8}
.bs-phcol{opacity:.45;filter:grayscale(1);cursor:not-allowed}.bs-phcol .bs-head{cursor:not-allowed}.bs-novar{font-size:.8em;color:#888}
.bs-ph{background:#b3261e;color:#fff;font-style:normal;font-weight:700;padding:1px 5px;border-radius:3px;margin-left:4px;font-size:.8em}.bs-sw{background:#2a1a3a;color:#c38ae8}.bs-donor{background:#222;color:#aaa}
.mark.bs-nocanon{color:#b9a27a;border-color:#4a3f2a;background:#15120c}
.row.bs-flash{outline:3px solid #e8b64c}
.bs-scale{flex:0 1 auto;width:min-content;min-width:350px;max-width:100%;box-sizing:border-box;border:1px solid #3a4a3a;background:#10140f;border-radius:6px;padding:3px 5px;font-size:11.5px}
.bs-schead b{color:#9fe0a8;flex:none}.bs-schead span{color:#8aa58a}
.bs-scimg{overflow-x:auto;cursor:zoom-in;margin:3px 0 2px}
.bs-scall{display:flex;flex-direction:column;gap:3px;margin:4px 0}
.bs-scone{cursor:zoom-in;overflow-x:auto;border-left:3px solid transparent;padding-left:4px}
.bs-scone.on{border-left-color:#d9a441}
.bs-scone img{display:block;max-width:none;width:auto;height:auto;image-rendering:pixelated}
.bs-scimg img{display:block;max-width:none;width:auto;height:auto;image-rendering:pixelated}
.bs-scsize{color:#d8c7a8}
.bs-scl{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bs-scale>.bs-scl,.bs-scale>.bs-scsrc,.bs-scale>.bs-head{width:0;min-width:100%;box-sizing:border-box}
.bs-scres b{color:#fff}.bs-scres.bs-low b{color:#e06c6c}.bs-scres.bs-mid b{color:#e8b64c}.bs-scres.bs-over b{color:#8ac3e8}.bs-scres.bs-ok b{color:#9fe0a8}
.bs-scsrc{color:#7f8a7f;font-size:10.5px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.bs-scsrc.bs-fallback{color:#e06c6c}
.bs-set{position:relative}
.bs-ppc{font-style:normal;white-space:nowrap;color:#9fe0a8;background:#0b0d10d9;border-radius:3px;padding:0 4px;font-size:10px;pointer-events:auto}
/* a subject already ruled on another sheet: dimmed pick column until expanded */
.row:has(.bs-ruled:not([open])) .ctrl{opacity:.35}
.bs-ruledsum{cursor:pointer;color:#9fb6c9;padding:2px 0;font-size:12px}
.bs-ruled[open]>.bs-ruledsum{margin-bottom:6px}
/* right-hand pick column: only this row's letters, readable redo/hold */
.row .ctrl{width:200px}
.row .opts{flex-wrap:wrap}
.row .opts button{flex:0 0 auto;min-width:30px;padding:3px 0}
.row .opts button[data-set="redo"]{margin-left:auto}
.row .opts button[data-set="redo"],.row .opts button[data-set="hold"]{flex:1 1 40%;padding:4px 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row .opts button[data-set="redo"]{order:98}.row .opts button[data-set="hold"]{order:99}
.row .opts::after{content:"";order:97;flex-basis:100%;height:0}
@media (max-width:1400px){.bs-canonp{flex-basis:240px}.bs-cthumb{width:56px;height:56px;flex-basis:56px}}
/* ── slots (DESIGN 2026-10-10): one labelled lane per picture the game draws ── */
.bs-graphics{flex-direction:column;flex-wrap:nowrap;align-items:stretch}
.sl-rowhead{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:2px 0}
.sl-lane{border:1px solid #2c333d;border-left:4px solid #6a7484;border-radius:6px;padding:4px 7px 6px;background:#12151a}
.sl-k-adult,.sl-k-grown,.sl-k-item,.sl-k-body{border-left-color:#e8b64c}.sl-k-adult_female{border-left-color:#e07ab0}
.sl-k-young,.sl-k-young_female,.sl-k-plant_young{border-left-color:#7fc35a}.sl-k-flying,.sl-k-flying_female{border-left-color:#5ac3c3}
.sl-k-swimming,.sl-k-swimming_female{border-left-color:#5a8ae8}.sl-k-alternate,.sl-k-leafless{border-left-color:#c38ae8}
.sl-unassigned{border-left-color:#8a6a3a;border-style:dashed}.sl-reference{border-left-color:#555;opacity:.9;background:#101010}
.sl-head{display:flex;gap:10px;align-items:center;justify-content:space-between}
.sl-head>b{font-size:13.5px;letter-spacing:.04em;color:#f0e2c0}
.sl-desc{font-size:11.5px;color:#a9b2bf;margin:1px 0 3px}
.sl-poolnote{color:#9fb6ff;font-size:11px}
.sl-chip{font-size:11.5px;padding:1px 8px;border-radius:10px;border:1px solid #3d4653;color:#c3cad6;background:#181c22;white-space:nowrap}
.sl-chip.need{border-color:#b8862b;color:#ffd27a;background:#2a2010}
.sl-chip.pf{border-style:dashed;border-color:#6b7380;color:#aab3c0;background:transparent}
.sl-warn.sl-replaced{color:#9fd7a8}.sl-chip.done{border-color:#2f7a45;color:#9fe0a8;background:#102016}
.sl-chip.redraw{border-color:#b85a2b;color:#ffb08a;background:#2a1610}.sl-chip.bad{border-color:#b3261e;color:#fff;background:#5a1a16;white-space:normal}
.sl-chip.ref{color:#9fb6c9}.sl-chip.old{border-color:#7a6aa8;color:#d6c8ff;background:#1c1830}
.sl-oldq{display:inline-flex;gap:3px;align-items:center;margin-right:4px}.sl-oldq .sl-oldb{font-size:10.5px;padding:0 6px}
.sl-old-confirm .sl-old{background:#173a22;color:#9fe0a8}.sl-old-drop .sl-old{background:#22262c;color:#8a95a5;text-decoration:line-through}
.sl-btns{display:flex;flex-wrap:wrap;gap:5px;align-items:center;margin:2px 0 4px}
.sl-b{font-size:11px;padding:2px 8px;border-radius:4px;border:1px solid #3d4653;background:#161a20;color:#c3cad6;cursor:pointer}
.sl-b:hover{border-color:#8a95a5;color:#fff}.sl-b.on{background:#2f7a45;border-color:#5ac37f;color:#fff}
.sl-b.bad{background:#7a2420;border-color:#e06c6c;color:#fff}.sl-b.pool{background:#2a4a8a;border-color:#6a9ae8;color:#fff}
.sl-badges{display:flex;flex-wrap:wrap;gap:3px;margin:1px 0 2px;font-size:10px}
.sl-badges i{font-style:normal;padding:0 5px;border-radius:3px}
.sl-ig{background:#173a5a;color:#9fd0ff}.sl-asg{background:#203a20;color:#9fe0a8}.sl-old{background:#2c2440;color:#d6c8ff}
.bs-set.sl-rej{border-color:#e06c6c}.bs-set.sl-rej .bs-faces{opacity:.55}
.sl-warn{font-size:11px;color:#ffb08a;margin:2px 0;max-width:280px}
.sl-this{font-size:11px;color:#d8c7a8}.sl-this select{font-size:11px;max-width:190px}
.sl-hint{font-size:10.5px;color:#e8b64c;font-style:normal}
.sl-asks{border:1px solid #2c333d;border-radius:6px;padding:3px 7px;background:#121417;font-size:12px}
.sl-asks>summary{cursor:pointer;color:#e8d6a8}
.sl-grid{display:grid;grid-template-columns:110px 1fr;gap:5px 10px;align-items:center;margin:5px 0}
.sl-grid b{color:#e8b64c;font-size:12px}.sl-grid input,.sl-grid select{font-size:11.5px;background:#0d1014;color:#e6e6e6;border:1px solid #3d4653;border-radius:3px;padding:1px 4px}
.sl-more{font-size:11.5px;margin:1px 0}
.sl-lane .bs-set{min-width:200px}.bs-foot .sl-b{padding:1px 6px}
</style>
"""


def _fill_template(cfg: dict, items: list, render: str, title: str) -> str:
    tpl = (SKILL / "sheet_template.html").read_text()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(cfg, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(items).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("<!-- ══ FILL IN #3 (optional)", render + "\n<!-- ══ FILL IN #3 (optional)", 1)
    return re.sub(r"<title>.*?</title>", f"<title>{title}</title>", tpl, count=1, flags=re.S)


def _clusters(rows: list[dict]):
    """Two-way related links from census twins (only between rows on this sheet) + union-find clusters."""
    of = {}
    for r in rows:
        for dn in [r["key"], r.get("port")] + list(r.get("defNames") or []):
            if dn:
                of.setdefault(dn, r["key"])
    rel, elsewhere = defaultdict(dict), defaultdict(list)
    for r in rows:
        for t in r.get("twins") or []:
            o = of.get(t["defName"])
            if o and o != r["key"]:
                why = t.get("relation", "").replace("_", " ")
                rel[r["key"]].setdefault(o, why)
                rel[o].setdefault(r["key"], why)
            elif not o:
                elsewhere[r["key"]].append(f"{t['defName']} ({t.get('relation', '').replace('_', ' ')})")
    parent = {r["key"]: r["key"] for r in rows}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, bs in rel.items():
        for b in bs:
            parent[find(a)] = find(b)
    return rel, elsewhere, find


BIOME_BRIEF = """<p><b>{label}</b> — every flora and fauna row of this biome ({n} rows), one row per species. Each row shows
<b>every picture we hold</b> for it: <b>IN GAME</b> (blue frame) is what the game draws now; <b>shipped, shadowed</b> is a copy losing
the load-order race; <b>render</b> columns are artpipe outputs (newest first); <b>history</b> columns are earlier states of our files
from git; <b>donor original</b> is the donor mod's own sprite. Each set shows its facings side by side (S, E, N);
hover a set's header for where it came from.</p>
<p><b>Every picture lives in a labelled SLOT</b> — what the game draws it as (ADULT · MALE, ADULT · FEMALE, YOUNG, FLYING,
PLANT · GROWN, CATCH ITEM …). <b>Click a picture to use it for that slot</b> (click again to take it back), or <b>redraw this
slot</b>. A slot you leave alone keeps what the game draws now once you return the sheet; there is no accept button.
The ✕ verbs say what they do: <b>✕ not for this slot</b> deletes nothing;
<b>✕ retire</b> takes a live picture out of the game: with another set in use in that slot it leaves in the same pass, otherwise
the slot is redrawn and it stays until the new picture is installed; <b>leave the random
pool</b> exists only where the game picks among pictures at random; the small ✕ on one picture deletes it from the art store.
<b>+ random pool</b> appears only on a real random pool and is never pre-ticked. Renders found by name sit under <b>RENDERS NOT YET
ASSIGNED</b> until you say what each one is. <b>Requests</b> (rename, description, more art, missing facings, size, move/cut) have
their own fields; the note box is for anything else.</p>
<p><b>Canon rows</b> show the canon-library reference images and the entry's <b>Must show</b> list beside the pictures. A canon creature and
our own (franchise-free) stand-in for it are <b>separate rows</b>, each judged on its own, but grouped together under one coloured band
with a <b>related</b> link both ways. A stand-in's Star Wars twin (RSW_) is always its own full row in the band, even where the biome
never casts it. Rows you already ruled on in <b>desert sitting 1</b> are prefilled with that pick and say so
(green line naming the set). The counter separates rows <b>you</b> decided from rows still holding the agent's
prefill. Nothing installs from this sheet: your picks become ledger rulings, then you see an install plan.</p>"""


SUBJECTS_LEAD = """<p><b>{label}</b> — {n} rows of game art (not a biome roster), one row per subject. Each row shows
<b>every picture we hold</b> for it, with its <b>in-game size</b> beside it: the art at true scale next to a vanilla human, on its
footprint where it is a building. <b>IN GAME</b> (blue frame) is what the game draws now; <b>render</b> columns are artpipe outputs;
<b>history</b> columns are earlier states of our files from git. Hover a set's header for where it came from.</p>"""


# Ground colour behind the scaled portrayal (owner 2026-10-05: "You also did not include the scaled portrayal on that
# sheet"): the panel is UNCONDITIONAL, on every biome sheet. The colour is MEASURED per biome by measure_ground():
# the mean opaque RGB of the texture of the biome's lowest-fertility terrain (terrainsByFertility, first threshold =
# the dominant ground at low fertility) from the def dump -> TerrainDef.texturePath -> an installed texture (our src/,
# vanilla bundle_textures by basename, then the Steam Mods / workshop folders). Where nothing can be measured the panel
# uses scale_panel's default tan and the sheet's progress record lists the biome. Hand measurements below predate the
# function and are kept as overrides only where they were taken from the texture the owner named.
SCALE_BIOMES = {"RM_LongShade": None, "RM_Stillsand": (126, 110, 91), "RM_BlueDesert": (155, 164, 172),
                # Abyss: AB_ForsakenSands.png (near-black, 25,25,35); Cauldron: RM_CauldronSoil -> Soil.png (93,76,61);
                # Contagion: GU_AlienSand/GU_AlienSandFine mean (fine sand dominates fertility < 0.2)
                "RM_Abyss": (24, 24, 34), "RM_Cauldron": (93, 76, 61), "RM_Contagion": (145, 113, 115)}
STEAM_ROOTS = [Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"),
               Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")]
_GROUND: dict = {}
GROUND_LOG: dict = {}


def _find_terrain_png(tex_path: str):
    base = tex_path.replace("\\", "/")
    hits = list((L.REPO_ROOT / "src").glob(f"**/Textures/{base}.png"))
    if hits:
        return hits[0]
    van = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/ludeon.rimworld.core") / (base.split("/")[-1] + ".png")
    if van.is_file():
        return van
    for root in STEAM_ROOTS:
        if root.is_dir():
            for mod in root.iterdir():
                for sub in ("Textures", "1.6/Textures", "Common/Textures"):
                    f = mod / sub / (base + ".png")
                    if f.is_file():
                        return f
    return None


def measure_terrain(terrain: str):
    """(rgb, source) — mean opaque RGB of one TerrainDef's texture (def dump -> texturePath -> installed PNG)."""
    import sqlite3
    from PIL import Image
    import scale_panel
    db = sqlite3.connect(str(scale_panel.DB))
    tr = db.execute("select json from defs where def_name=? and def_type='TerrainDef'", (terrain,)).fetchone()
    tp = ((json.loads(tr[0]).get("fields") or {}).get("texturePath")) if tr else None
    f = _find_terrain_png(tp) if tp else None
    if not f:
        return None, f"terrain {terrain}: texture {tp or 'not in dump'} not found"
    px = [q for q in Image.open(f).convert("RGBA").getdata() if q[3] > 8]
    if not px:
        return None, f"terrain {terrain}: {f.name} has no opaque pixel"
    return tuple(round(sum(q[i] for q in px) / len(px)) for i in range(3)), f"{terrain} -> {tp} ({f.name}, mean of {len(px)} opaque px)"


SUBJECT_GROUND = "Soil"   # a subjects sheet has no biome: its panels sit on vanilla Soil, measured like any biome ground


def measure_ground(biome: str):
    """(rgb, source) — mean opaque RGB of the biome's low-fertility ground texture — or (None, why it is unmeasurable)."""
    if biome in _GROUND:
        return _GROUND[biome]
    import sqlite3
    from PIL import Image
    why = ""
    try:
        import scale_panel
        db = sqlite3.connect(str(scale_panel.DB))
        r = db.execute("select json from defs where def_name=? and def_type='BiomeDef'", (biome,)).fetchone()
        tbf = sorted(((json.loads(r[0]).get("fields") or {}).get("terrainsByFertility") or []),
                     key=lambda t: t.get("min", 0)) if r else []
        if not tbf:
            why = "BiomeDef has no terrainsByFertility in the def dump"
        for t in tbf:
            tr = db.execute("select json from defs where def_name=? and def_type='TerrainDef'", (t.get("terrain"),)).fetchone()
            tp = ((json.loads(tr[0]).get("fields") or {}).get("texturePath")) if tr else None
            f = _find_terrain_png(tp) if tp else None
            if not f:
                why = f"terrain {t.get('terrain')}: texture {tp or 'not in dump'} not found"
                continue
            im = Image.open(f).convert("RGBA")
            px = [p for p in im.getdata() if p[3] > 8]
            if not px:
                continue
            rgb = tuple(round(sum(p[i] for p in px) / len(px)) for i in range(3))
            _GROUND[biome] = (rgb, f"{t.get('terrain')} -> {tp} ({f.name}, mean of {len(px)} opaque px)")
            return _GROUND[biome]
    except Exception as e:                                  # noqa: BLE001
        why = f"{type(e).__name__}: {e}"
    _GROUND[biome] = (None, why or "no terrain texture measurable")
    return _GROUND[biome]


SCALE_FACE = ("east", "south", "single", "west", "north")
THING_FACE = ("south", "single", "east", "north", "west")   # a building/item is shown as placed: south, unrotated footprint
SCALE_RENDER_VERSION = 6   # 2 = max-zoom primary scene (owner 2026-10-04: enhanced zoom, "don't down-resolve")


def _img_px(sha: str):
    from PIL import Image
    try:
        return Image.open(L.store_path(sha)).size
    except Exception:                                       # noqa: BLE001
        return None


def _panel_for(row: dict, size: dict, sha: str, imgdir: Path):
    """Render (or reuse) the true-scale panel of ONE archived picture: (measurement json, composite, full-size)."""
    import scale_panel as SP
    stem = re.sub(r"[^A-Za-z0-9_]", "_", row["key"]) + "_" + sha[:10] + "_" + hashlib.sha1(
        json.dumps([SCALE_RENDER_VERSION, SP.TERRAIN, size.get("drawSize"), size.get("quad"), size.get("mesh"),
                    size.get("color")] + ([size.get("footprint"), size.get("offset")] if size.get("kind") == "thing" else [])
                   ).encode()).hexdigest()[:6]
    comp, full, mj = imgdir / f"scale_{stem}.png", imgdir / f"scale_{stem}_full.png", imgdir / f"scale_{stem}.json"
    try:
        m = json.loads(mj.read_text()) if comp.exists() and full.exists() else None
    except (OSError, ValueError):
        m = None
    if m is None:
        m = SP.render_panel(L.store_get(sha), size, comp, full)
        mj.write_text(json.dumps(m))
    return m, comp, full


def _scale_for(R, row: dict, gitems: list, prefill_letter: str, dec: dict | None, imgdir: Path) -> dict:
    """In-game size (cells, with its SOURCE) + a true-scale panel of the set the owner picked (else the
    prefill), and px/cell for every set of the body graphic. See scale_panel.py for the measurement."""
    import scale_panel as SP
    size = R.size(row)
    out = {"status": size["status"], "source": size["source"], "kind": size.get("kind"),
           "cells": round(size["cells"], 3), "bodySize": size.get("bodySize"), "mesh": size.get("mesh"),
           "drawSize": size.get("drawSize"), "visualMax": size.get("visualMax"), "quad": size.get("quad")}
    if size.get("kind") == "thing":
        out.update({"footprint": size.get("footprint"), "category": size.get("category"), "offset": size.get("offset")})
    if size["status"] == "none":     # MEASURED no world size (UI-only def): the resolver exempts the row, not the author
        out.update({"def": size.get("def"), "why": "no world size — " + size["source"]})
        return out
    faces_order = THING_FACE if size.get("kind") == "thing" else SCALE_FACE
    prim = next((g for g in gitems if g["primary"]), None)
    if prim is None:
        out["why"] = "no picture to scale"
        return out
    qx = (size.get("drawSize") or [None])[0] if size.get("kind") == "animal" else size.get("quad")
    sets = []
    for c in prim["cols"]:
        f = next((f for f in faces_order if f in c["faces"] and L.store_has(c["faces"][f])), None)
        px = _img_px(c["faces"][f]) if f else None
        c["ppc"] = round(px[0] / qx) if (px and qx) else None
        c["srcPx"] = list(px) if px else None
        sets.append((c["letter"], f, px))
    want = (dec or {}).get("decision") or ""
    by = "your pick"
    if not (dec or {}).get("decidedAt") or want not in [c["letter"] for c in prim["cols"]]:
        want, by = prefill_letter, "prefill"
    col = next((c for c in prim["cols"] if c["letter"] == want), None) or prim["cols"][0]
    if col["letter"] != want:
        by = "first set (no pick, no prefill)"
    f = next((f for f in faces_order if f in col["faces"] and L.store_has(col["faces"][f])), None)
    if not f:
        out["why"] = f"set {col['letter']} has no archived picture"
        return out
    m, comp, full = _panel_for(row, size, col["faces"][f], imgdir)
    # EVERY candidate gets its own true-scale panel beside the vanilla human (owner, 2026-10-15), not only the picked
    # set: each primary column carries {img, full, ppc, face}; the gate checks every shown column has one on disk
    for c in prim["cols"]:
        cf = next((x for x in list(faces_order) + sorted(c["faces"]) if x in c["faces"] and L.store_has(c["faces"][x])), None)
        if not cf:
            continue
        cm, cc, cfull = (m, comp, full) if c is col else _panel_for(row, size, c["faces"][cf], imgdir)
        c["scale"] = {"img": f"{imgdir.name}/{cc.name}", "full": f"{imgdir.name}/{cfull.name}", "face": cf,
                      "ppc": cm["pxPerCell"], "zoomFullPpc": cm.get("zoomFullPpc")}
    out.update({"img": f"{imgdir.name}/{comp.name}", "full": f"{imgdir.name}/{full.name}", "set": col["letter"],
                "by": by, "face": f, "srcPx": m["srcPx"], "ppc": m["pxPerCell"], "verdict": SP.ppc_verdict(m["pxPerCell"]),
                "zoomPpc": m.get("zoomPpc"), "zoomFitted": m.get("zoomFitted"), "zoomCropped": m.get("zoomCropped"), "zoomFullPpc": m.get("zoomFullPpc"),
                "sets": [{"l": l, "ppc": (round(px[0] / qx) if px and qx else None), "px": (px[0] if px else None)}
                         for l, _f, px in sets]})
    out["refs"] = _reference_panels(row, size, imgdir)
    return out


def _reference_panels(row: dict, size: dict, imgdir: Path) -> list[dict]:
    """Read-only REFERENCE pictures of a row (census field `reference_textures`: repo-relative PNG paths, e.g. the installed
    canon twin of a base it will reskin), each at the row's true scale beside the vanilla human. They are rendered here
    ONLY: never a graphic, column, letter, snapshot entry, decision or enact target, and never put in the art store."""
    import scale_panel as SP
    out = []
    for ent in row.get("reference_textures") or []:
        # an entry is a repo-relative path (shown at the row's size) or {path, size: {drawSize, footprint, source}}: a
        # composite with its own true size, e.g. several pieces laid out as the code draws them (a joined weir wall)
        rel = ent["path"] if isinstance(ent, dict) else ent
        esize = SP.runtime_size(row["key"] + " reference", ent["size"]) if isinstance(ent, dict) and ent.get("size") else size
        f = L.REPO_ROOT / rel
        if not f.is_file():
            out.append({"path": rel, "missing": True})
            continue
        b = f.read_bytes()
        stem = "ref_" + re.sub(r"[^A-Za-z0-9_]", "_", row["key"]) + "_" + hashlib.sha256(b).hexdigest()[:10] + "_" + hashlib.sha1(
            json.dumps([SCALE_RENDER_VERSION, SP.TERRAIN, esize.get("drawSize"), esize.get("quad"), esize.get("mesh")]).encode()
        ).hexdigest()[:6]
        comp, full = imgdir / f"scale_{stem}.png", imgdir / f"scale_{stem}_full.png"
        if not (comp.exists() and full.exists()):
            SP.render_panel(b, esize, comp, full)
        out.append({"path": rel, "img": f"{imgdir.name}/{comp.name}", "full": f"{imgdir.name}/{full.name}"})
    return out


def _subject_names(name: str) -> set[str]:
    """Every spelling of ONE subject: the normalised stem ('RSW_Plant_Nysyllin_Wild' -> 'nysyllin_wild' -> 'nysyllinwild')
    and, when the name carries a variant word ('WraidAlpha'), the base species ('wraid'). Matching goes through subject.py
    so a tier prefix, a Plant_ prefix or a variant word never makes a ruled subject look new."""
    out = {S.norm(S.stem(name))}
    v = S.variant_stripped(name)
    if v:
        out.add(S.norm(v))
    out.discard("")
    return out


def ruled_elsewhere(sheet_dir: Path, sheet_id: str, labels: dict | None = None) -> list[dict]:
    """Rows the owner has ALREADY ruled on some OTHER sheet in sheet_dir (owner, 2026-10-05: "a lot of redundant
    creatures from other forms listed on here as well that I've already reviewed").

    A ruling is a row of another *.decisions.json that the sidecar wrote (savedBy + writeCount, or reviewStatus
    ruled), carrying an owner `at` stamp and a decision (a purge-only touch is not a ruling). Each entry:
    {names, sheet, sheet_id, row, decision, label, note, at}. The pick's label comes from that sheet's snapshot."""
    out = []
    for f in sorted(sheet_dir.glob("*.decisions.json")):
        if f.name == sheet_id + ".decisions.json":
            continue
        try:
            doc = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        rs = doc.get("reviewStatus") if isinstance(doc.get("reviewStatus"), dict) else {}
        if not ((doc.get("savedBy") and int(doc.get("writeCount") or 0) > 0) or rs.get("state") == "ruled"):
            continue
        snap = {}
        sp = doc.get("snapshot")
        if sp:
            sp = Path(sp) if Path(sp).is_absolute() else L.REPO_ROOT / sp
            try:
                snap = json.loads(sp.read_text()).get("rows") or {}
            except (OSError, ValueError):
                snap = {}
        nice = (labels or {}).get(doc.get("biome") or "") or f.name.replace(".decisions.json", "")
        for row, v in (doc.get("decisions") or {}).items():
            if not isinstance(v, dict) or not v.get("at") or not (v.get("decision") or "").strip():
                continue
            if not (v.get("decidedAt") or not v.get("purgeTouched")):
                continue
            dec = v["decision"].strip()
            lab = ((snap.get(row) or {}).get("labels") or {}).get(dec, "")
            out.append({"names": _subject_names(row), "sheet": nice, "sheet_id": f.stem.replace(".decisions", ""),
                        "row": row, "decision": dec, "label": lab, "note": (v.get("note") or "").strip(),
                        "at": v.get("at")})
    return out


def ruled_elsewhere_for(row_names: set[str], entries: list[dict]) -> dict | None:
    """The newest other-sheet ruling on any spelling of this subject, or None."""
    hit = [e for e in entries if e["names"] & row_names]
    return max(hit, key=lambda e: e["at"] or "") if hit else None


def _job_created(job_id: str) -> str:
    """The artpipe job's `created` stamp (ISO), or '' if the job file is not found in any state dir."""
    import os
    root = Path(os.environ.get("ARTPIPE_STATE_DIR") or "/mnt/d/Luke/dev/_artpipe")
    for d in ("done", "active", "pending", "failed"):
        p = root / d / f"{job_id}.json"
        try:
            return str(json.loads(p.read_text()).get("created") or "")
        except (OSError, ValueError):
            continue
    return ""


def ruling_predates_jobs(entry: dict | None, jobs) -> bool:
    """True when a subjects sheet NAMES a render (--jobs) filed after his ruling elsewhere: the sheet exists to judge
    that new art (typically the redraw his ruling asked for), so the row must not collapse as already ruled."""
    if not entry or not jobs:
        return False
    newest = max((_epoch(c) for c in (_job_created(j) for j in jobs) if c), default=None)
    return newest is not None and newest != float("inf") and newest > _epoch(entry.get("at") or "")


def _epoch(ts: str) -> float:
    """ISO time (with Z, +hh:mm or +hhmm) -> epoch seconds; unparseable -> +inf (never 'new')."""
    import datetime
    t = (ts or "").replace("Z", "+00:00")
    if re.search(r"[+-]\d{4}$", t):
        t = t[:-2] + ":" + t[-2:]
    try:
        return datetime.datetime.fromisoformat(t).timestamp()
    except ValueError:
        return float("inf")


def new_sets_since(gitems, idx, when: str) -> list[str]:
    """Letters of columns whose every picture the ledger first recorded AFTER `when` (his ruling elsewhere). A row
    with such columns holds unruled candidates, so it must not collapse as already ruled (Murrelith, 2026-10-15:
    ruled `redo` on feverwood 10-08, redrawn 10-15, and the redraw sheet hid it behind "already ruled")."""
    t0 = _epoch(when)
    if t0 == float("inf"):
        return []
    return sorted({c["letter"] for g in gitems for c in g["cols"]
                   if c.get("faces") and all(_first_seen(idx, s_) > t0 for s_ in c["faces"].values() if s_)})


def _first_seen(idx, sha: str) -> float:
    """When the ledger first recorded this picture (earliest variant event); unknown -> -inf (never 'new')."""
    ts = [_epoch(v.get("ts")) for v in idx.variants.get(sha, ()) if v.get("ts")]
    ts = [t for t in ts if t != float("inf")]
    return min(ts) if ts else float("-inf")


FRESH_TEXT = {"reflected": "✓ reflected", "redrawn": "✓ redrawn after your ruling", "awaiting": "⏳ awaiting render",
              "refiled": "⏳ failed, re-filed", "conflict": "⚠ needs your call", "not_acted": "NOT YET ACTED ON"}


def _fresh_mark(fresh, key):
    if not fresh or "rows" not in fresh:
        return None
    r = fresh["rows"].get(key)
    if not r:
        return None
    said = r["decision"] + (f" — “{r['note']}”" if r["note"] else "")
    return {"state": r["state"], "text": f"your ruling {r['when']}: {said} · {FRESH_TEXT[r['state']]}: {r['detail']}"}


def _fresh_banner(fresh, sheet_rows) -> str:
    import html as _h
    built = time.strftime("%Y-%m-%d %H:%M %Z")
    if not fresh:
        return f"<b>Built {built}.</b> No prior ruling of yours is on record for this sheet."
    if "rows" not in fresh:
        return f"<b>Built {built}.</b> <span style='color:#ff6b6b'>Freshness UNMEASURED: {_h.escape(fresh.get('error', ''))}</span>"
    rows = fresh["rows"]
    bad = {k: r for k, r in rows.items() if r["state"] not in ("reflected", "redrawn")}
    off = [k for k in rows if k not in sheet_rows]
    out = (f"<b>Built {built}.</b> {fresh['reflected']} of {fresh['total']} of your prior rulings fully reflected "
           f"(source: {_h.escape(Path(fresh['file']).name)}).")
    if bad:
        out += "<ul style='margin:4px 0 0 18px'>" + "".join(
            f"<li><span class='bs-fresh bs-fresh-{r['state']}'>{FRESH_TEXT[r['state']]}</span> <b>{_h.escape(k)}</b> — "
            f"{_h.escape(r['detail'][:200])}{' (row no longer on this biome)' if k in off else ''}</li>"
            for k, r in sorted(bad.items(), key=lambda kv: (kv[1]['state'] != 'not_acted', kv[0]))) + "</ul>"
    return out


def generate_biome(biome: str, census_path: Path = CENSUS, out_html: Path | None = None,
                   date: str | None = None, thumb_size: int = 160, sheet_only: bool = False,
                   allow_failing: str | None = None) -> dict:
    _FC_CACHE.clear()          # the gate reads the failed-canon record fresh; a cache from earlier in a long refresh run would disagree with it
    census = json.loads(Path(census_path).read_text())
    b = census["biomes"].get(biome)
    if b is None:
        raise SystemExit(f"biome {biome!r} not in {census_path} (have: {', '.join(census.get('biome_order', []))})")
    date = date or time.strftime("%Y-%m-%d")
    slug = BIOME_SLUG.get(biome) or b.get("slug") or _stem(biome).lower()
    out_html = Path(out_html) if out_html else BIOME_OUT / f"{slug}_sheet_{date}.html"
    sheet_id = out_html.stem
    imgdir = out_html.parent / "img"
    snap_path = L.ledger_dir() / "sheets" / f"{sheet_id}.snapshot.json"
    prev = json.loads(snap_path.read_text()) if snap_path.is_file() else {}
    prev_rows = prev.get("rows") or {}
    decisions_path = out_html.parent / (out_html.stem + ".decisions.json")
    old = json.loads(decisions_path.read_text()) if decisions_path.is_file() else None
    # FRESHNESS (owner, 2026-10-08: "how can I trust anything on the review sheet if I don't know if it's up to
    # date?"): every prior ruling on this sheet is graded by the plan `art.py enact` would carry out — reflected only
    # when a render filed for that ruling, a live pick, a done cut or a marked def edit exists
    fresh = None
    try:
        import enact as _EN
        _rf = _EN.ruled_decisions_for(sheet_id)
        if _rf:
            fresh = _EN.ruling_status(_rf, idx=L.Index())
    except Exception as e:                                  # noqa: BLE001
        fresh = {"error": f"{type(e).__name__}: {e}"}
    untouched = old is not None and not old.get("savedBy") and not old.get("writeCount") and \
        (old.get("reviewStatus") or {}).get("state") == "prefill"
    # letters are kept stable only once a human has written to the decisions file; until then every row
    # is lettered A, B, C … afresh, with no gaps left by columns that have since disappeared
    # Memory = the snapshot the owner RULED on (by the decisions file's snapshotId, from git history if a later
    # rebuild overwrote it) first, then any letter a later rebuild added. Letters are append-only per row: a set
    # keeps its letter for good, a vanished set's letter is never reused, and a vanished set a decision still
    # names is carried forward as a "kept" column so the letter keeps resolving to the same pictures.
    ruled = None
    if old is not None and not untouched:
        ruled = L.snapshot_by_id(snap_path, old.get("snapshotId")) or None
        if ruled is None and old.get("snapshotId"):
            print(f"WARNING {decisions_path.name}: its snapshot {old.get('snapshotId')} is not on disk or in git "
                  f"history — letters kept from the latest snapshot only", file=sys.stderr)
    letter_memory = _merge_memory((ruled or {}).get("rows") or {}, prev_rows) if (old is not None and not untouched) else {}
    used_letters = {k: L.decision_letters(v) for k, v in ((old or {}).get("decisions") or {}).items()} \
        if letter_memory else {}
    idx = L.Index()
    slots = L.scan_def_slots()
    order, fp = load_order()
    rows = b["rows"]
    # FRESHNESS BY CONSTRUCTION (ART_SHEET_REDESIGN_FRESH_OR_REFUSE): the census is a CACHED location list (census.json was
    # an Oct-7 capture while this was written; the GSS sheet of 2026-10-11 showed a pre-rename texPath from an Oct-4 one).
    # Every row of ours — creatures and plants alike — takes its texPaths from the src XML NOW; the census only fills in
    # donor/vanilla rows, which have no src XML. Gate req 15 then re-measures the built sheet against disk.
    import sheet_freshness as FR
    _fw = _world()
    for r in rows:
        _new, _notes = FR.fresh_resources(r, _fw)
        if _notes:
            r.setdefault("art", {})["resources"] = _new
            for n in _notes:
                print(f"art_sheet: {n}", file=sys.stderr)
    _elsewhere = ruled_elsewhere(out_html.parent, sheet_id, {k: v.get("label", k) for k, v in census["biomes"].items()})
    _own_touched = {k for k, v in ((old or {}).get("decisions") or {}).items() if isinstance(v, dict) and v.get("at")}
    scale_res = None
    if True:                              # owner 2026-10-05: the scaled portrayal is on EVERY biome sheet
        import scale_panel
        _rgb, _src = measure_terrain(b["ground_terrain"]) if b.get("ground_terrain") else measure_ground(biome)
        _rgb = SCALE_BIOMES.get(biome) or _rgb
        if _rgb:
            scale_panel.set_terrain(_rgb)
        else:
            scale_panel.set_terrain(scale_panel.DEFAULT_TERRAIN)
        scale_res = scale_panel.Resolver()
        GROUND_LOG[biome] = {"rgb": list(_rgb) if _rgb else None, "source": _src if not SCALE_BIOMES.get(biome) else "hand-measured override"}
        _gp = BIOME_OUT / "scale_ground_measured.json"
        try:
            _g = json.loads(_gp.read_text()) if _gp.is_file() else {}
            if _g.get(biome) != GROUND_LOG[biome]:
                _g[biome] = GROUND_LOG[biome]
                _gp.write_text(json.dumps(_g, indent=1, sort_keys=True))
        except (OSError, ValueError):
            pass
    # the in-game label + description on every row (owner, Vapaad note 2026-10-04: "Your sheets need to include
    # the animal descriptions as well for reference") — from the live dump, post-patch
    try:
        import scale_panel
        desc_res = scale_res or scale_panel.Resolver()
    except Exception as e:                                  # noqa: BLE001
        print(f"WARNING: no def dump for descriptions ({e}) — rows say UNMEASURED", file=sys.stderr)
        desc_res = None
    rel, elsewhere, find = _clusters(rows)
    # per-row overrides (sheet_row_overrides.json): the NEW in-game name of a donor row being ported, and extra
    # artpipe job families (new renders filed under another name, legacy crags_* sets) to show on that row
    _ov = (json.loads(OVERRIDES.read_text()) if OVERRIDES.is_file() else {}).get(biome, {})
    for r in rows:
        o = _ov.get(r["key"])
        if o:
            r["artpipe_state_jobs"] = sorted(set(r.get("artpipe_state_jobs") or []) | set(o.get("jobs") or []))
    labels = {r["key"]: (f"{_ov[r['key']]['new_label']} (new name; was {r['key']})" if r["key"] in _ov and _ov[r["key"]].get("new_label") else _human(r)) for r in rows}

    census_canon = {cr["key"]: (cr.get("canon") or {}).get("entry") for bb in census["biomes"].values()
                    for cr in bb["rows"] if (cr.get("canon") or {}).get("entry")}
    _ph_shared = PD.shared_map(census)
    built, purged_hidden, hidden_kept = [], {}, {}
    _base_of = {}          # row -> the pictures the owner has been shown on it (shown_base), kept in the snapshot
    donor_purged = set()
    # only bytes an artpipe render MADE are ours: donor art copied into one of our mods is still the donor's original
    ours_shas = {s_ for s_, vv in idx.variants.items() if any(v.get("kind") == "artpipe" for v in vv)}
    for r in rows:
        graphics, seen = [], set()
        for res in (r.get("art") or {}).get("resources") or []:
            if res.get("role") == "flying" and FLIP_RES_RE.match(res["res"] + "1"):
                continue          # a flip-book prefix: its frames join one set below, never per-frame columns
            br = build_row(idx, res["res"], order, slots, res.get("former") or ())
            if r.get("render_match"):     # a texture row keeps only the renders meant for it (art_sheet --textures)
                br["cols"] = [c for c in br["cols"] if c["kind"] != "artpipe" or re.search(r["render_match"], c["label"], re.I)]
                # the renders the manifest NAMES for this texture are its candidates, in its own slot — a corpse/
                # dessicated texture included (name_render_cols would otherwise park them as unassigned)
                if res is (r.get("art") or {}).get("resources", [None])[0]:
                    have_f = {_fkey(c) for c in br["cols"]}
                    for c in name_render_cols(idx, [], r.get("artpipe_state_jobs") or [], exact_any=True):
                        if _fkey(c) not in have_f and re.search(r["render_match"], c["label"], re.I):
                            c["bound"] = True
                            c["detail"] = f"{c['date']} · named for this texture by the sheet's texture manifest"
                            br["cols"].append(c)
            if (r.get("standin") or {}).get("res") == res["res"]:
                br["cols"].append(standin_col(r["standin"]))
            if br.get("donorPurged"):
                donor_purged.add(r["key"])
            cols = [c for c in br["cols"] if _fkey(c) not in seen]
            seen.update(_fkey(c) for c in cols)
            p = res.get("prior_selection")
            graphics.append({"res": res["res"], "role": ROLE_TEXT.get(res.get("role"), res.get("role") or "graphic"),
                             "cols": cols, "prior_raw": p, "joined_by": res.get("joined_by")})
        # every OTHER graphic the game draws for the row's defs (live dump): alternateGraphics and a plant's
        # young/leafless graphic — a picture the game can draw is on the row (owner card 2026-10-10)
        _have_res = {g["res"] for g in graphics}
        for xres, xrole in game_extra_texpaths([r["key"], r.get("port"), *(r.get("defNames") or [])]).items():
            if xres in _have_res or xres.lower().endswith(("_dessicated", "_desiccated", "_corpse")):
                continue
            _have_res.add(xres)
            br = build_row(idx, xres, order, slots)
            cols = [c for c in br["cols"] if _fkey(c) not in seen]
            seen.update(_fkey(c) for c in cols)
            if cols:
                graphics.append({"res": xres, "role": ROLE_TEXT.get(xrole, xrole), "cols": cols, "prior_raw": None,
                                 "joined_by": "live-def-dump"})
        have = {s for g in graphics for c in g["cols"] for s in c["faces"].values()}
        words = {w for x in [r["key"], r.get("port")] + list(r.get("defNames") or []) if x for w in S.join_stems(x)}
        words |= {(r.get("label") or "").replace(" ", "")}
        prefixes = [res["res"] for res in (r.get("art") or {}).get("resources") or []
                    if res.get("role") == "flying" and FLIP_RES_RE.match(res["res"] + "1")]
        # the live def dump names every slot the game draws: flip-book prefixes (male AND female) come from it too
        row_slots = []
        for _n in dict.fromkeys([r["key"], r.get("port"), *(r.get("defNames") or [])]):
            if _n:
                row_slots += [x for x in _def_slots(_n) if x["id"] not in {y["id"] for y in row_slots}]
        for x in row_slots:
            if x["res"].startswith("_flip:") and x["res"][6:] not in prefixes:
                prefixes.append(x["res"][6:])
        flips = [c for c in flipbook_cols(idx, words, r.get("artpipe_state_jobs") or [], prefixes)
                 if not (set(c["faces"].values()) & have)]
        flip_shas = {s for c in flips for s in c["faces"].values()}
        named = [c for c in name_render_cols(idx, words, r.get("artpipe_state_jobs") or [],
                                             defs={r["key"], r.get("port"), *(r.get("defNames") or [])},
                                             exact_any=bool(r.get("render_match")))
                 if _fkey(c) not in seen
                 and (not (set(c["faces"].values()) & (have | flip_shas))
                      # a render the row NAMES (artpipe_state_jobs) that shares only some pictures (its east is a copy of
                      # the live east) is still a different set; it is dropped only when everything in it is shown already
                      or (FAM_RE.sub("", (c.get("family") or "")).lower() in {FAM_RE.sub("", j).lower() for j in (r.get("artpipe_state_jobs") or [])}
                          and not set(c["faces"].values()) <= (have | flip_shas)))
                 and (not r.get("render_match") or re.search(r["render_match"], c.get("label", ""), re.I))]
        if flips:
            # one lane per flip-book (a male and a female sequence are different slots, DESIGN §1 PekoPeko): a live
            # set goes to its own prefix; a render sequence whose name says female to the female prefix, else the first
            fem = next((x["res"][6:] for x in row_slots if x["kind"] == "flying_female"), None)
            lanes = {}
            for c in flips:
                pre = c.get("prefix") or (fem if fem and re.search(r"(?:^|_)(f|female)(?:_|$)", c.get("seq") or "", re.I)
                                          else (prefixes[0] if prefixes else r["key"]))
                lanes.setdefault(pre, []).append(c)
            for pre in sorted(lanes, key=lambda x: (x == fem, x)):
                graphics.append({"res": "_flip:" + pre, "role": FLIP_ROLE, "cols": lanes[pre], "prior_raw": None,
                                 "flip": True})
        # a render filed FOR a slot (its job carries `slot`) goes straight to that slot's lane
        for c in list(named):
            lane = next((g for g in graphics if c.get("jobSlot") and g["res"] == c["jobSlot"]), None)
            if lane is not None:
                lane["cols"].append(c)
                named.remove(c)
        # a catch row: renders of the LIVING creature are reference only, never a pickable catch picture
        _src = r["key"][:-len("Catch")] if r["key"].endswith("Catch") and len(r["key"]) > 5 else None
        if _src and named:
            ref = [c for c in named if "catch" not in (c.get("family") or c.get("label") or "").lower()]
            named = [c for c in named if c not in ref]
            if ref:
                graphics.append({"res": "_reference:" + _src, "role": "reference", "cols": ref, "prior_raw": None,
                                 "reference": True})
        if named:
            graphics.append({"res": None, "role": ROLE_TEXT[None], "cols": named, "prior_raw": None})
        # req 14: a picture the ledger has PURGED (his reject+purge, on any sheet) is never shown as a column
        n_hidden = 0
        for g in graphics:
            kept_cols = []
            for c in g["cols"]:
                live = {f: sh for f, sh in c["faces"].items() if not idx.is_purged(sh)}
                if c.get("winner") and len(live) < len(c["faces"]):
                    # purged but STILL what the game shows today: keep it as the IN GAME column, flagged, never pickable
                    c["purgedLive"] = True
                    kept_cols.append(c)
                    continue
                n_hidden += len(c["faces"]) - len(live)
                if c["kind"] == "donor" and not c.get("ours") and not live:
                    donor_purged.add(r["key"])   # a donor ORIGINAL the owner purged: shown and rejected (gate req 4)
                if live:
                    c["faces"] = live
                    kept_cols.append(c)
            g["cols"] = kept_cols
        purged_hidden[r["key"]] = n_hidden
        graphics = [g for g in graphics if g["cols"]] or graphics[:0]
        # primary = first body graphic with pictures, else first graphic; name renders are offered to it too
        prim = next((g for g in graphics if g["res"] and g["role"] == "body"), graphics[0] if graphics else None)
        if prim is not None and graphics.index(prim) != 0:
            graphics.remove(prim)
            graphics.insert(0, prim)
        # a RANDOM POOL lane: the game draws one of several pictures at random (a Graphic_Random folder, or the adult body
        # plus its alternateGraphics). Only there can a set be a variant (owner, by question card 2026-10-10)
        _has_alt = any(g["role"] == ROLE_TEXT["alternate"] for g in graphics)
        for gi_, g in enumerate(graphics):
            g["pool"] = bool(g["res"]) and not g.get("flip") and (
                any(c.get("random_variant") for c in g["cols"]) or g["role"] == ROLE_TEXT["alternate"]
                or (_has_alt and gi_ == 0))
        allcols = [c for g in graphics for c in g["cols"]]
        mem = letter_memory.get(r["key"]) or {}
        # every picture an earlier build of this sheet put on this row (ruled snapshot + latest): a random-folder
        # picture outside it is labelled "in game now, never shown"
        _shown_before = shown_base(r["key"], ruled, prev_rows)
        _base_of[r["key"]] = _shown_before
        _assign_letters(allcols, mem.get("columns"), mem.get("reserved"))
        kept = _kept_cols(allcols, mem, used_letters.get(r["key"]) or set())
        _k = [c for c in kept if not any(idx.is_purged(sh) for sh in c["faces"].values())]
        for c in kept:      # a set he picked that has since been purged is hidden from the page but its letter stays in the snapshot
            if c not in _k:
                hidden_kept.setdefault(r["key"], []).append((c, (mem.get("graphic_of") or {}).get(c["letter"])))
        purged_hidden[r["key"]] += len(kept) - len(_k)
        kept = _k
        for c in kept:
            gk = (mem.get("graphic_of") or {}).get(c["letter"])
            g = next((g for g in graphics if (g["res"] or "_byname") == gk), None)
            if g is None and gk and gk.startswith("_flip:"):
                g = next((x for x in graphics if x.get("flip")), None)
            if g is None and gk in (None, "_byname"):
                # a by-name render he ruled on that is no longer found by name: it stays UNASSIGNED (never offered as
                # the body: DESIGN §1, Sketto's flight renders sat in the body strip)
                g = next((x for x in graphics if x["res"] is None), None)
                if g is None:
                    g = {"res": None, "role": ROLE_TEXT[None], "cols": [], "prior_raw": None}
                    graphics.append(g)
            if g is None:
                g = graphics[0] if graphics else None
            if g is None:
                g = {"res": gk if gk and gk != "_byname" else None, "role": "body", "cols": [], "prior_raw": None}
                graphics.append(g)
            g["cols"].append(c)
            allcols.append(c)
        # a render bound to a lane only by its NAME whose job name says it is a picture of something ELSE (a flight frame
        # in a body lane, a young render in the adult lane, a catch in a creature lane) is not offered as that slot's
        # picture: it goes to UNASSIGNED until he says what it is (DESIGN §1: Sketto's sketto_fly_* in the body strip,
        # PekoPeko's single flight frame picked as the female body)
        _slot_kind = {x["res"]: x["kind"] for x in row_slots}
        _slot_base = {}
        for x in row_slots:
            _slot_base.setdefault(x["res"].rsplit("/", 1)[-1], []).append(x["kind"])
        _unas = None
        for gi_, g in enumerate(list(graphics)):
            if not g["res"] or g.get("flip") or g.get("reference"):
                continue
            kd = _slot_kind.get(g["res"]) or (lambda b_: b_[0] if len(b_) == 1 else None)(_slot_base.get(g["res"].rsplit("/", 1)[-1], [])) \
                or ("adult" if gi_ == 0 and r["kind"] == "fauna" else None)
            if not kd:
                continue
            for c in list(g["cols"]):
                if c.get("kind") != "artpipe" or c.get("winner") or c.get("jobSlot") == g["res"]:
                    continue
                h = SLOTS.hint(c.get("family") or c.get("label") or "")
                wrong = (h == "flight frame — not a body" and not kd.startswith("flying")) or \
                        (h == "young" and kd in ("adult", "adult_female", "grown")) or \
                        (h == "catch item" and kd != "item")
                if wrong:
                    if _unas is None:
                        _unas = next((x for x in graphics if x["res"] is None), None)
                        if _unas is None:
                            _unas = {"res": None, "role": ROLE_TEXT[None], "cols": [], "prior_raw": None}
                            graphics.append(_unas)
                    g["cols"].remove(c)
                    _unas["cols"].append(c)
        graphics = [g for g in graphics if g["cols"] or g is graphics[0]]
        for c in allcols:
            # a "donor" column whose bytes an artpipe render made is our art under a donor-ported texPath
            # (TheRot's RotSporeKit/... carries rot_*_v2 renders): it must not read as donor-only (gate req 3)
            if c["kind"] == "donor" and set(c["faces"].values()) & ours_shas:
                jobs = sorted({v.get("job", "") for s_ in c["faces"].values() for v in idx.variants.get(s_, [])
                               if v.get("kind") == "artpipe" and v.get("job")})
                c["oursRender"] = True
                c["label"] = "our deployed art" + (" (render %s)" % FAM_RE.sub("", jobs[0]) if jobs else "") + " — " + \
                    c.get("label", "").split("— ", 1)[-1]
            c["purgeable"] = c["kind"] not in ("live", "kept") and not (c["kind"] == "donor" and c.get("winner"))   # the game's own art
            if c.get("random_variant") and c.get("winner"):
                # one picture of a random folder the game draws: he keeps it or ✕s it (enact retires a ✕'d one
                # from the folder); a picture this sheet never showed him says so
                c["purgeable"] = not (c["kind"] == "donor" and not c.get("ours"))
                if _shown_before and not (set(c["faces"].values()) & _shown_before):
                    # a re-encoded copy of a picture already on the row (dHash within COPY_BITS) is not "never shown"
                    hit = next((o for sh in c["faces"].values() for o in _shown_before
                                if _ph(idx, sh) and _ph(idx, o) and L.hamming(_ph(idx, sh), _ph(idx, o)) <= COPY_BITS), None)
                    copy_of = (next((d["letter"] for d in allcols if hit in d["faces"].values()), "shown before")
                               if hit else None)
                    if copy_of:
                        c["copyOf"] = copy_of
                        c["label"] = f"in game now, a re-encoded copy of set {copy_of} — " + c["label"]
                    else:
                        c["neverShown"] = True
                        c["label"] = "in game now, never shown — " + c["label"]
            if c.get("purgedLive"):
                c["purgeable"] = False
        try:   # placeholder_detect: a row drawn by script-flat shapes or borrowed vanilla textures has no art of ours
            _pv = PD.classify_row(r, _ph_shared)
        except Exception as e:                              # noqa: BLE001
            _pv = {"verdict": "UNMEASURED", "reasons": [f"{type(e).__name__}: {e}"]}
        if _pv["verdict"] == "PLACEHOLDER":
            for c in allcols:
                if c["kind"] == "live":
                    c["placeholder"] = "; ".join(_pv["reasons"])[:400]
        for c in allcols:   # GEOMETRIC placeholder sets are shown greyed and can never be picked or kept as a variant
            _g = geo_placeholder(c["faces"])
            if _g:
                c["placeholder"], c["noSelect"] = _g, True
        for g in graphics:
            letters = {id(c) for c in allcols}
            for c in g["cols"]:
                if c.get("near_of") is not None and id(c["near_of"]) not in letters:
                    c.pop("near_of")
        _ROW_SLOTS[r["key"]] = row_slots
        built.append((r, graphics))

    maxl = max([LETTERS.index(c["letter"]) + 1 for _, gs in built for g in gs for c in g["cols"]] + [1])
    items, snap_rows, prefills = [], {}, {}
    cluster_ids, n_sit1 = {}, 0
    for r, graphics in built:
        key = r["key"]
        keys = {L.subject_key(x) for x in [key] + list(r.get("defNames") or []) + [_stem(key)] if x}
        rul = idx.subject_rulings(keys)
        gitems, picks, prim_pf = [], {}, ("", "", "none")
        thumbs, fulls, missing = {}, {}, 0
        for gi, g in enumerate(graphics):
            g["prior"] = g.pop("prior_raw", None)
            pf = _graphic_prefill(g, rul)
            gkey = g["res"] or "_byname"
            if gi == 0:
                prim_pf = pf
            elif g["res"] is not None and pf[0]:
                picks[gkey] = pf[0]
            elif g["res"] is None and _recommended(g) and not _recommended(graphics[0]):
                prim_pf = pf      # a recommended render found by name only: it is the row's suggested answer
            facings = [f for f in FACINGS if any(f in c["faces"] for c in g["cols"])]
            flip = {}
            if g.get("flip"):
                facings, nfr, ffac = flip_layout(g["cols"])
                flip = {"flip": True, "nframes": nfr, "flipFacings": ffac}
            for c in g["cols"]:
                for f, s in list(c["faces"].items()):
                    if s in thumbs:
                        continue
                    if not L.store_has(s):
                        missing += 1
                        continue
                    thumbs[s] = thumb(s, imgdir, size=thumb_size)
                    fulls[s] = full_image(s, imgdir)
            pr = g["prior"]
            prior = None
            if pr:
                was = f"{SIT1} recorded: {pr.get('decision')} — {pr.get('picked_label') or ''}".strip(" —")
                pf_shas = set((pr.get("picked_faces") or {}).values())
                hit = next((c for c in g["cols"] if pf_shas and pf_shas & set(c["faces"].values())), None)
                dec = (pr.get("decision") or "").strip()
                if hit:
                    text = f"your {SIT1} pick is set {hit['letter']} here ({_short(hit)})"
                elif dec in ("redo", "hold"):
                    text = f"your {SIT1} ruling: {dec}"
                else:
                    text = f"your {SIT1} pick is not among these pictures any more"
                prior = {"text": text, "note": pr.get("note", ""), "was": was}
            # the SLOT this lane is (DESIGN §3.1): from the live dump by texPath, else from the census role
            _sl = next((x for x in _ROW_SLOTS.get(key) or [] if x["res"] == g["res"]), None) if g["res"] else None
            if _sl is None and g["res"] and not g.get("reference"):
                # the census can name an older folder for the same picture (swanimals/PekoPeko/PekoPeko_f vs the dump's
                # RimStarWars/SWBestiary/PekoPeko/PekoPeko_f): one slot whose FILE name matches is that slot
                _bn = [x for x in _ROW_SLOTS.get(key) or [] if x["res"].rsplit("/", 1)[-1] == g["res"].rsplit("/", 1)[-1]]
                _sl = _bn[0] if len(_bn) == 1 else None
            if g.get("reference"):
                lane, slot_ = "reference", {"label": f"REFERENCE — the living creature ({g['res'].split(':', 1)[1]}), "
                                                     "not pickable here", "kind": "reference", "required": False,
                                            "desc": "its renders, shown so you can see what the catch should be a dead one of"}
            elif g["res"] is None:
                lane, slot_ = "unassigned", {"label": "RENDERS NOT YET ASSIGNED", "kind": "unassigned", "required": False,
                                             "desc": "made for this subject, but nobody has said which picture of it they "
                                                     "are — say what each one is before it can be used"}
            else:
                lane = "slot"
                if _sl:
                    slot_ = {"id": _sl["id"], "label": _sl["label"], "kind": _sl["kind"], "also": _sl.get("also") or [],
                             "required": bool(_sl["required"]) or gi == 0}
                else:
                    lab, kd = FALLBACK_SLOT.get(g["role"], (None, None))
                    if not lab:
                        kd = {"fauna": "adult", "flora": "grown", "fish": "item"}.get(r["kind"], "body")
                        lab = {"adult": "ADULT", "grown": "PLANT · GROWN", "item": "ITEM"}.get(kd, "BODY") if gi == 0 \
                            else f"ANOTHER GRAPHIC · {g['res'].rsplit('/', 1)[-1]}"
                    if key.endswith("Catch") and gi == 0:
                        lab, kd = "CATCH ITEM", "item"
                    slot_ = {"label": lab, "kind": kd, "required": gi == 0, "also": []}
                slot_["desc"] = SLOT_DESC.get(slot_["kind"], "")
                if _sl and _sl.get("pool"):
                    g["pool"] = True
            gitems.append({
                "key": gkey, "res": g["res"], "role": g["role"], "primary": gi == 0, "facings": facings,
                "pool": bool(g.get("pool")) and lane == "slot", "lane": lane, "slot": slot_,
                "prior": prior, **flip,
                "cols": [{k: (v if k != "near_of" else v["letter"]) for k, v in c.items()
                          if k in ("letter", "kind", "label", "detail", "faces", "winner", "also", "prompt", "purgeable", "near_of", "placeholder", "purgedLive", "noSelect", "neverShown", "copyOf", "canonAdvice", "canonFlag")}
                         | {"short": _short(c), "setId": SLOTS.set_id(c["faces"]),
                            "hint": SLOTS.hint(c.get("family") or c.get("seq") or c.get("label") or "") if lane == "unassigned" else ""}
                         for c in g["cols"]]})
        letter, why, source = prim_pf
        _nosel = {c["letter"] for g in gitems for c in g["cols"] if c.get("noSelect")}
        picks = {k: v for k, v in picks.items() if v not in _nosel}
        needs_art = bool(gitems) and (letter in _nosel or not [c for c in gitems[0]["cols"] if not c.get("noSelect")])
        if needs_art:   # never prefill a placeholder: the row needs art
            letter, why, source = "redo", ("NEEDS ART — the current art is a geometric placeholder, which can never be "
                                           "picked or kept as a variant"), "none"
        no_art = not graphics
        if no_art:
            letter, why, source = "hold", "no art yet — held until a picture exists", "none"
        if source == "sit1":
            n_sit1 += 1
        ce = canon_entry(Path(r["canon"]["entry"]).name) if (r.get("canon") or {}).get("entry") else {}
        base = (r["canon"].get("base") or "") if ce else ""
        if not ce:
            ce, base = canon_base(key, r.get("label") or "", census_canon)
        canon = None
        if ce:
            seen_c = {}
            for p in ce["images"]:
                seen_c.setdefault(L.sha256_file(p), p.read_bytes())
            canon = {"dir": ce["dir"], "brief": ce["brief"][:2500], "must": ce["must"][:1500],
                     "ruling": ce["ruling"][:800] if "(empty" not in ce["ruling"] else "", "base": base,
                     "imgs": [thumb(sh, imgdir, bb, 260) for sh, bb in seen_c.items()]}
        root = find(key)
        clustered = bool(rel.get(key))
        if clustered and root not in cluster_ids:
            cluster_ids[root] = len(cluster_ids)
        tier, tier_text = _tier(r)
        if base:
            tier, tier_text = "canon", f"canon Star Wars creature (entry for the base species: {base})"
        canon_tag = (canon_state(key) or "no canon-library entry for this subject — judge on its own") if not canon else ""
        flags = []
        # a row the owner decided whose pictures changed since the snapshot he ruled on (a redo landed, a pick was
        # installed under new bytes, or the row was renamed and its decision carried over under `carriedFrom`)
        _od = ((old or {}).get("decisions") or {}).get(key) or {}
        _when = _od.get("decidedAt") or _od.get("carriedRuledAt") or _od.get("at")
        if _when:
            # a set is new when none of its pictures was in the ledger before his ruling (first-recorded time; the
            # snapshot id cannot tell, because a rebuild that only ADDS columns keeps the ruled snapshot's id)
            _t0 = _epoch(_when)
            _new = [c["letter"] for g in gitems for c in g["cols"]
                    if c["faces"] and all(_first_seen(idx, s_) > _t0 for s_ in c["faces"].values() if s_)]
            if _new:
                flags.append(f"NEW — awaiting your ruling: NEW ART since your {_when[:10]} ruling: column(s) {', '.join(sorted(set(_new)))}")
        if _od.get("carriedFrom"):
            _ai = _od.get("agentInference") or {}
            flags.append(f"your ruling carried over from {_od['carriedFrom']} (renamed row)"
                         + (f" — pick shown is the in-game set, an agent inference: {_ai.get('basis', '')}" if _ai else ""))
        if no_art:
            flags.append("NO ART YET")
        if needs_art:
            flags.append("NEEDS ART — placeholder only")
        _bad = sorted({x for x in [_od.get("decision")] + list((_od.get("picks") or {}).values()) + list(_od.get("variants") or [])
                       if x in _nosel})
        if _bad:
            flags.append(f"your ruling names placeholder set(s) {', '.join(_bad)} — a placeholder is not selectable; "
                         "ingest turns it into a regen request")
        if missing:
            flags.append(f"{missing} picture(s) not archived — not shown")
        n_sets = sum(len(g["cols"]) for g in gitems)
        plc = r.get("placements") or []
        # donor-sourced row with no donor original on disk and none recorded as purged: say so explicitly, naming the
        # donor mod and texPath (SHEET_DONOR_COLUMN_FALSE_PASS_1) — the gate counts this note as the donor column shown
        donor_absent = ""
        if (r.get("donors") or tier == "donor") and key not in donor_purged and not any(
                c.get("kind") == "donor" and not c.get("ours") and not SG._is_ours_label(c.get("label"))
                for g in gitems for c in g["cols"]):
            donor_absent = ("donor original not on disk (mod absent): " + (", ".join(r.get("donors") or ["donor tier"]))[:120]
                            + " · texPath " + (", ".join(x["res"] for x in (r.get("art") or {}).get("resources") or [])[:200] or "unknown"))
        item = {
            "donorAbsent": donor_absent,
            "id": key, "kind": r["kind"], "label": labels[key].capitalize(),
            "_root": root, "_clustered": clustered,
            "effect": (f"{r['kind']} · {_layer(r)} · commonality {r.get('commonality_max')} · "
                       + (f"{n_sets} picture set(s)" + (f" across {len(gitems)} graphics" if len(gitems) > 1 else "")
                          if gitems else "no pictures")),
            "tier": tier, "tierText": tier_text, "canonTag": canon_tag, "flags": flags,
            "fresh": _fresh_mark(fresh, key),
            "prefillShort": _prefill_short(source, why),
            "prefill": letter, "prefillWhy": why, "prefillSource": source,
            "contested": source in ("inferred", "none"), "inferred": source == "inferred",
            "prefillPicks": picks, "graphics": gitems, "thumbs": thumbs, "fulls": fulls, "canon": canon,
            "letters": [c["letter"] for g in gitems if g["primary"] for c in g["cols"]
                        if not c.get("purgedLive") and not c.get("noSelect")],
            "dependsOn": (key[:-len("Catch")] if key.endswith("Catch") and key[:-len("Catch")] in {x["key"] for x in rows}
                          else None),
            "related": [{"id": o, "label": labels[o], "why": w} for o, w in sorted(rel.get(key, {}).items())],
            "elsewhere": elsewhere.get(key, []),
            "noArt": no_art, "purgedHidden": purged_hidden.get(key, 0), "donorPurged": key in donor_purged,
            "noArtWhy": ((r.get("art") or {}).get("searched") or "searched by graphic and by name: " + ", ".join(sorted(w for w in {_stem(key)} | set(r.get("defNames") or []) if w))
                         + ("; artpipe jobs on record: " + ", ".join(r.get("artpipe_state_jobs") or []) if r.get("artpipe_state_jobs") else "")),
            "rulings": [{"at": (x.get("at") or "")[:10], "verdict": x.get("raw_verdict") or x.get("verdict"),
                         "trust": x.get("trust"), "sheet": Path(x.get("source_file") or "").name.replace(".decisions.json", ""),
                         "note": (x.get("note") or x.get("blanket_said") or "")[:240]}
                        for x in sorted(rul, key=lambda x: x.get("at") or "") if x.get("trust") not in ("prefill",)],
        }
        item["desc"] = desc_res.describe(r) if desc_res is not None else {}
        # a subject the owner already ruled on another sheet renders collapsed at the bottom (never deleted), unless he
        # has himself touched this row on THIS sheet
        _re = None if key in _own_touched else ruled_elsewhere_for(
            set().union(*[_subject_names(x) for x in [key] + list(r.get("defNames") or []) if x]), _elsewhere)
        if _re and b.get("subjects") and ruling_predates_jobs(_re, r.get("artpipe_state_jobs") or []):
            _re = None                    # a named render newer than his ruling: this sheet exists to judge it
        if _re and r.get("reopen"):
            _re = None                    # --reopen: re-shown on purpose (he asked for the row explained before judging)
        if _re and new_sets_since(gitems, idx, _re.get("at") or ""):
            _re = None                    # pictures he has never ruled on (a redraw landed): the row is open work
            item["reopenedByNewSets"] = True   # the gate (req 7) must agree this row is deliberately live
        if _re:
            item["ruledElsewhere"] = {"sheet": _re["sheet"], "sheetId": _re["sheet_id"], "pick": _re["decision"],
                                      "label": _re["label"], "note": _re["note"][:300], "at": (_re["at"] or "")[:10]}
        if scale_res is not None:
            item["scale"] = _scale_for(scale_res, r, gitems, letter, (old or {}).get("decisions", {}).get(key), imgdir)
            if item["scale"].get("status") == "fallback":     # req 2: a FALLBACK size is allowed but must be flagged
                item["flags"].append(f"{SG.SIZE_FALLBACK_FLAG} — {item['scale'].get('source')}")
        items.append(item)
        prefills[key] = (letter, picks)
        snap_rows[key] = {"subject_key": _stem(key).lower(), "res": (gitems[0]["res"] if gitems else None),
                          "columns": {c["letter"]: c["faces"] for g in gitems for c in g["cols"]},
                          "labels": {c["letter"]: c["label"] for g in gitems for c in g["cols"]},
                          "graphic_of": {c["letter"]: g["key"] for g in gitems for c in g["cols"]},
                          "pools": sorted(g["key"] for g in gitems if g.get("pool")),
                          "reserved": sorted(set((letter_memory.get(key) or {}).get("reserved") or [])
                                             | {c["letter"] for g in gitems for c in g["cols"]}, key=LETTERS.index),
                          "shownBase": sorted(_base_of.get(key) or ())}

    for key, cs in hidden_kept.items():
        sr = snap_rows.get(key)
        if sr is None:
            continue
        for c, gk in cs:
            sr["columns"].setdefault(c["letter"], c["faces"])
            sr["labels"].setdefault(c["letter"], c.get("label", ""))
            sr["graphic_of"].setdefault(c["letter"], gk or "_byname")
            sr["reserved"] = sorted(set(sr["reserved"]) | {c["letter"]}, key=LETTERS.index)
    # a row the owner ruled on that has left this biome's census keeps its snapshot entry (not shown on the page),
    # so his decision letters still resolve to the pictures he ruled on
    touched_rows = {k for k, v in ((old or {}).get("decisions") or {}).items() if isinstance(v, dict) and v.get("at")}
    for key, ls in used_letters.items():
        mem = letter_memory.get(key)
        if key in snap_rows or not mem or not ((ls & set(mem.get("columns") or {})) or key in touched_rows):
            continue
        snap_rows[key] = {"subject_key": mem.get("subject_key") or _stem(key).lower(), "res": mem.get("res"),
                          "columns": mem["columns"], "labels": mem.get("labels") or {},
                          "graphic_of": mem.get("graphic_of") or {}, "reserved": mem.get("reserved") or [],
                          "rowGone": "not in this biome's census any more — kept so the owner's ruled letters resolve"}

    # order + groups: per kind, unlinked rows first, then each linked cluster as its own band
    kinds = ["fauna", "flora", "fish"]
    kinds += sorted({it["kind"] for it in items} - set(kinds))
    ordered = []
    for k in kinds:
        ks = sorted([it for it in items if it["kind"] == k], key=lambda it: it["label"].lower())
        for it in ks:
            if not it["_clustered"]:
                it["group"] = k.capitalize()
                ordered.append(it)
        roots = []
        for it in ks:
            if it["_clustered"] and it["_root"] not in roots:
                roots.append(it["_root"])
        for root in roots:
            mem = [it for it in items if it["_clustered"] and it["_root"] == root]
            mem.sort(key=lambda it: ({"canon": 0, "sw": 1, "ours": 2, "donor": 3}[it["tier"]], it["id"]))
            band = PAIR_COLOURS[cluster_ids[root] % len(PAIR_COLOURS)]
            gname = "Related: " + " ↔ ".join(f"{it['label']} ({it['id']})" for it in mem)
            for it in mem:
                if it in ordered:
                    continue
                it["group"], it["band"] = gname, band
                ordered.append(it)
    for it in ordered:
        it.pop("_root", None)
        it.pop("_clustered", None)
    # already-ruled subjects sink to the bottom under one group, in their old order
    ordered = [it for it in ordered if not it.get("ruledElsewhere")] + \
        [dict(it, group="Already ruled on another sheet", band=None) for it in ordered if it.get("ruledElsewhere")]
    n_collapsed = sum(1 for it in ordered if it.get("ruledElsewhere"))

    snap = {"sheetId": sheet_id, "built": L.now(), "loadOrder": fp, "census": _rel(Path(census_path)),
            "census_git_head": census.get("git_head"), "biome": biome, "rows": snap_rows}
    new_id = hashlib.sha1(json.dumps(snap_rows, sort_keys=True).encode()).hexdigest()[:16]
    superset = bool(prev_rows) and all(
        snap_rows.get(rk, {}).get("columns", {}).get(l) == f
        for rk, pr in prev_rows.items() for l, f in (pr.get("columns") or {}).items())
    snap["snapshotId"] = prev.get("snapshotId") if superset and prev.get("snapshotId") else new_id
    for it in ordered:
        it["rev"] = snap["snapshotId"]     # the inventory revision a schema-2 record is saved against

    opts = pick_options(maxl)
    n_canon = sum(1 for it in ordered if it["canon"])
    n_link = sum(1 for it in ordered if it["related"])
    n_noart = [it["id"] for it in ordered if it["noArt"]]
    cfg = {
        "sheetId": sheet_id, "title": b.get("title") or f"{b.get('label', biome)} — flora & fauna art",
        "subtitle": (f"{len(ordered)} rows · {n_canon} canon · {n_link} linked · {n_sit1} prefilled from {SIT1} · "
                     f"{len(n_noart)} NO ART YET" + (f" · {n_collapsed} already ruled on another sheet (collapsed at the bottom)" if n_collapsed else "") + (f" · IN GAME judged on {fp.split(':')[0]}" if "FULL.LATEST" in fp else "")),
        "briefHtml": b.get("lead_html", "") + (SUBJECTS_LEAD.format(label=b.get("label", biome), n=len(ordered))
                      + BIOME_BRIEF.split("</p>", 1)[1]) if b.get("subjects")
                     else BIOME_BRIEF.format(label=b.get("label", biome), n=len(ordered)),
        "criterion": ("Rows: fauna, flora, fish, alphabetical; related rows banded together. Columns: what the game shows "
                      "now first, then shadowed copies, renders newest first, history oldest first, donor last. "
                      "The order ranks RECENCY and RUNTIME, never quality or worth."),
        "invented": [
            "Renders are joined to a row by its NAME (defName stem, label, artpipe job names) when nothing binds them to a "
            "texture path; such columns say 'found by NAME' and could belong to a namesake.",
            "Related links come from the census's twin detection (same stem, shared texture, or a 'copied from' comment) — "
            "a name match, not a ruling that the two are the same creature.",
            "Where you have no pick and no keep, the prefill trusts a commit message citing your approval (⚠), else what the "
            "game shows now; a row with only name-found renders is prefilled to the newest render (⚠).",
        ],
        "posture": {"mode": "pick-one", "explain": "Each SLOT of a row (adult, female, young, flying, grown, catch …): click "
                    "the picture to use, or redraw; a slot you leave alone keeps its in-game art when you return the sheet. Nothing "
                    "installs until you see that plan. '✕ not for this "
                    "slot' deletes nothing; the small ✕ on one picture deletes it from the art store."},
        "options": opts, "groupLabel": "group", "media": True,
        "freshness": _fresh_banner(fresh, {it["id"] for it in ordered}),
        "decisionsFile": decisions_path.name, "decisionsPath": str(decisions_path), "sheetPath": str(out_html),
        "schema": 2, "biomes": [{"key": k, "label": v.get("label", k)} for k, v in census["biomes"].items()],
    }
    render = '<script id="RENDER">' + BIOME_BODY.replace("%LETTERS%", LETTERS).replace("%NEAR%", str(NEAR)) + COMMON_JS + "</script>" + STYLE + BIOME_STYLE
    out_html.parent.mkdir(parents=True, exist_ok=True)
    # THE GATE (rimworld-review-sheets): build to <sheet>.gate.tmp, check every requirement, and only then move the
    # HTML (stamped) into place. A failure raises GateFailed with the previous sheet, snapshot and decisions untouched.
    prefill_doc = json.dumps({
        "sheetId": sheet_id, "posture": "pick-one", "snapshot": _rel(snap_path), "snapshotId": snap["snapshotId"],
        "criterion": cfg["criterion"], "biome": biome,
        "reviewStatus": {"state": "prefill", "by": None, "at": None,
                         "evidence": "generated by art_sheet.py --biome; rows marked sit1 carry the owner's desert sitting 1 picks, no human has ruled on this sheet"},
        "decisions": {k: ({"decision": l, "note": "", "prefill": l} | ({"picks": p} if p else {}))
                      for k, (l, p) in prefills.items()},
    }, indent=1)
    will_write = not sheet_only and (old is None or untouched)
    # a FIRST build has no decisions file yet, and check_sheet (req 9) wants one: the gate reads the prefill it is
    # about to write, staged beside it, so a new biome sheet can pass on its first build (FLYER_FLIPBOOK_ART_1 note)
    gate_dec = decisions_path
    if will_write:
        gate_dec = decisions_path.with_name(decisions_path.stem + ".gate.tmp.json")
        gate_dec.write_text(prefill_doc)
    gate_ctx = {"sheet_id": sheet_id, "sheet_dir": out_html.parent, "snap": snap, "snap_path": snap_path,
                "decisions": old, "decisions_path": gate_dec, "biome": biome, "census_rows": rows,
                "subjects_sheet": bool(b.get("subjects")),
                "ground": GROUND_LOG.get(biome)}
    _html = FR.embed(_fill_template(cfg, ordered, render, cfg["title"]),
                     FR.build_manifest(ordered, out_html.parent, rows, {"textures_manifest": b["textures_manifest"]} if b.get("textures_manifest") else {}))
    try:
        gate_checks = SG.enforce(_html, gate_ctx, out_html, allow_failing)
    finally:
        if gate_dec != decisions_path:
            gate_dec.unlink(missing_ok=True)
    snap_path.parent.mkdir(parents=True, exist_ok=True)
    snap_path.write_text(json.dumps(snap, indent=1, sort_keys=True))
    SG.commit(out_html.with_name(out_html.stem + ".gate.tmp.html"), out_html)

    # decisions: written when absent, or regenerated while it is still the untouched prefill
    wrote = False
    if sheet_only:
        if old is not None and old.get("snapshotId") != snap["snapshotId"]:
            print(f"WARNING --sheet-only: columns changed (snapshot {old.get('snapshotId')} -> {snap['snapshotId']}) and "
                  f"{decisions_path.name} was NOT rewritten — its letters may now point at different sets", file=sys.stderr)
    elif will_write:
        decisions_path.write_text(prefill_doc)
        wrote = True
    elif old.get("snapshotId") != snap["snapshotId"]:
        # letters are stable, so only a letter his decisions USE naming different pictures is a problem
        base = ruled or prev
        bad = L.letter_mismatches(old, base, snap) if base else [("?", "?")]
        if bad:
            print(f"WARNING {decisions_path.name}: the owner has touched it and these decision letters now name "
                  f"different pictures than in snapshot {old.get('snapshotId')}: "
                  + ", ".join(f"{r}:{l}" for r, l in bad[:20]) + " — ingest will refuse until reconciled", file=sys.stderr)
    return {"biome": biome, "html": _rel(out_html), "decisions": _rel(decisions_path), "wrote_decisions": wrote,
            "gate": ("PASS " if all(c.ok for c in gate_checks) else "OVERRIDE (unstamped, bannered) ") + SG.GATE_VERSION, "snapshot": _rel(snap_path), "snapshotId": snap["snapshotId"], "census_rows": len(rows), "rows": len(ordered),
            "ruled_rows_gone_kept_in_snapshot": sorted(k for k, v in snap_rows.items() if v.get("rowGone")),
            "collapsed_ruled_elsewhere": n_collapsed, "canon_rows": n_canon, "canon_rows_with_images": sum(1 for it in ordered if it["canon"] and it["canon"]["imgs"]),
            "canon_rows_with_must_show": sum(1 for it in ordered if it["canon"] and it["canon"]["must"]),
            "linked_rows": n_link, "prefilled_sit1": n_sit1, "no_art": n_noart,
            "sets": sum(len(g["cols"]) for it in ordered for g in it["graphics"]),
            "images": len(list(imgdir.glob("*.webp")))}


# ─────────────────────────────────────────────── any game art (not a biome) ──

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _job(job_id: str) -> dict:
    root = SG.artpipe_dir()
    for d in ("done", "pending", "active", "failed"):
        f = root / d / f"{job_id}.json"
        if f.is_file():
            return json.loads(f.read_text())
    raise SystemExit(f"artpipe job {job_id!r} not found under {root}/{{done,pending,active,failed}}")


def _subject_canon(name: str, jobs=()) -> str | None:
    """The canon entry dir (repo-relative) for a --subjects row: the def's own entry (canon_entry's exact resolve), else
    the entry its artpipe jobs were generated against (their canon_reference images live in it). None if neither."""
    ce = canon_entry(name)
    if ce:
        return ce["dir"]
    for j in jobs:
        try:
            refs = _job(j).get("canon_reference") or []
        except SystemExit:
            continue
        for ref in ([refs] if isinstance(refs, str) else refs):
            d = CANON / Path(ref).parent.name       # by entry name: the job may have been filed from another clone
            if Path(ref).parent.parent.name == CANON.name and (d / "description.md").exists():
                return str(d.relative_to(L.REPO_ROOT))
    return None


def subject_row(R, name: str, jobs=()) -> dict:
    """A census-shaped row for ONE def of any kind, from the live def dump: its world texPath (a pawn's adult body, a
    thing's graphicData) or, for a UI-only def, its icon — so build_row finds every picture the ledger holds for it."""
    td = R._def(name, "ThingDef")
    res, kind, label = [], "other", name
    if td:
        label = td.get("label") or name
        gd = td.get("graphicData") or {}
        if td.get("race"):
            kind = "fauna"
            _kn, kd = R._kind_for(name)
            for st in reversed((kd or {}).get("lifeStages") or []):
                tp = ((st or {}).get("bodyGraphicData") or {}).get("texPath")
                if tp:
                    res.append({"res": tp, "role": "body"})
                    break
        else:
            kind = "flora" if (td.get("plant") or td.get("category") == "Plant") else (td.get("category") or "thing").lower()
            if gd.get("texPath"):
                res.append({"res": gd["texPath"], "role": "body"})
        if not res and td.get("uiIconPath"):
            res.append({"res": td["uiIconPath"], "role": "icon"})
    else:
        for t in R.UI_TYPES:
            d = R._def(name, t)
            if d is not None:
                kind, label = t.replace("Def", "").lower(), d.get("label") or name
                if d.get("iconPath"):
                    res.append({"res": d["iconPath"], "role": "icon"})
                break
    # OUR OWN defs: the repo's XML is the truth, the dump is a capture that goes stale on every texture rename
    # (GSS_OWNER_WALK_STALE_NOW_COLUMN: a 2026-10-04 dump kept the pre-rename MessyConduit/ texPaths, so the "now" column
    # showed Oct-3 renders of a texture no longer on disk). Prefer src's texPath for non-creature defs.
    # a def NEWER than the dump (a fresh port, no game load since) is not in it at all: the repo's texPaths are the only
    # source, or the row loses its IN GAME column (donor_pack_port sheet 2026-10-14: 9 new RSW_ ports showed renders only)
    if (td and not td.get("race")) or not res:
        try:
            import subject as _S
            src_tp = sorted(_S.World().tex_by_def.get(name, ()))
        except Exception:                                   # noqa: BLE001
            src_tp = []
        if src_tp and {r["res"] for r in res if r["role"] == "body"} != set(src_tp):
            print(f"art_sheet: {name}: dump texPath {[r['res'] for r in res]} is STALE; using src {src_tp}", file=sys.stderr)
            res = [r for r in res if r["role"] != "body"] + [{"res": t, "role": "body"} for t in src_tp]
    for r in res:
        r.update({"joined_by": "def", "subjects": [name]})
    return {"key": name, "kind": kind, "port": None, "donors": [], "pairing": {}, "placements": [], "label": label,
            "defNames": [name], "commonality_max": None, "twins": [], "artpipe_state_jobs": sorted(set(jobs)),
            "canon": {"entry": _subject_canon(name, jobs), "match": None, "images": [], "has_must_show": False,
                      "ruled": False, "wookieepedia": None, "canon_missing_entry": False},
            "art": {"resources": res, "searched": f"live def dump: {name} " + ("found" if (td or res) else "NOT in the dump")}}


def subjects_census(name: str, defs, jobs=(), label: str | None = None, lead_html: str = "", reopen=()) -> tuple[Path, str]:
    """Write Transient/biome_ffar/<name>.subjects.json: a one-entry census (key SUBJECTS_<name>) holding a row per def,
    plus a row per artpipe job's target_def carrying that job. `lead_html` (--lead) is the sheet's purpose paragraph:
    what he is judging and what skipping does; it is kept in the census, so refresh_sheets rebuilds keep it.
    Returns (census path, census key)."""
    if not NAME_RE.match(name or ""):
        raise SystemExit(f"--name {name!r}: lower-case letters, digits and _ only (it becomes <name>_sheet_<date>.html)")
    import scale_panel
    R = scale_panel.Resolver()
    by_def: dict = {d: [] for d in defs}
    for j in jobs:
        # JOB=DEF binds a job whose spec names no target_def (older renders) to the def it is for
        j, _, bound = j.partition("=")
        td = bound or _job(j).get("target_def")
        if not td:
            raise SystemExit(f"artpipe job {j} names no target_def — bind it as --jobs {j}=<DefName>")
        by_def.setdefault(td, []).append(j)
    rows = [subject_row(R, d, js) for d, js in by_def.items()]
    for _r in rows:                       # --reopen: his earlier ruling could not judge it; show the row open, not collapsed
        if _r["key"] in set(reopen):
            _r["reopen"] = True
    key = f"SUBJECTS_{name}"
    path = BIOME_OUT / f"{name}.subjects.json"
    # the census is exactly the subjects named now; a row the owner already ruled on that is left out keeps its
    # snapshot entry (generate_biome's rowGone), so his letters still resolve
    census = {"schema": 1, "generated": L.now(), "git_head": None, "biome_order": [key],
              "biomes": {key: {"label": label or name.replace("_", " ").capitalize(), "slug": name, "subjects": True,
                               "ground_terrain": SUBJECT_GROUND, "title": f"{label or name.replace('_', ' ').capitalize()} — game art",
                               "lead_html": lead_html or "", "rows": rows}}}
    path.write_text(json.dumps(census, indent=1))
    return path, key


def standin_col(sd: dict) -> dict:
    """The IN GAME column for a texture-manifest stand-in: the game's own picture (Core art lives in resources.assets,
    which no ledger step imports), read from the manifest's files into the art store. Never purgeable (winner)."""
    faces = {}
    for fac, f in sorted((sd.get("faces") or {}).items()):
        b = Path(f).read_bytes()
        sha = L.sha256_bytes(b)
        L.store_put_bytes(b, sha)
        faces[fac] = sha
    return {"kind": "donor", "faces": faces, "date": "", "winner": True, "ours": False, "standin": True,
            "label": "IN GAME — " + sd.get("label", sd["res"]), "detail": sd.get("source", "")}


def textures_census(name: str, manifest: Path, label: str | None = None) -> tuple[Path, str]:
    """A census from a TEXTURE manifest: art C# draws with no def naming it (a mod's cords, decals, overlays).
    Manifest {"rows": [{key, label, part, look, variant, section, resources: [texPath], former: [old texPath],
    size: {drawSize, footprint, source}, render_match?, standin?, reference_textures?}], "lead_html"?, "ground_terrain"?}.
    reference_textures: read-only pictures beside the row (repo-relative PNG, or {path, size} at their own true size). standin =
    {res, label, source, faces: {facing: png}} — the picture the game draws today when the row's texture is an
    engine/vanilla one no ledger holds (Core's resources.assets): shown as that resource's IN GAME column. ground_terrain is the
    TerrainDef the panels sit on (default vanilla Soil) — the biome ground where the art will be seen. Each row's size is the one its code sets
    (scale_panel honours runtimeSize); rows of the same part are linked across looks so they band together."""
    if not NAME_RE.match(name or ""):
        raise SystemExit(f"--name {name!r}: lower-case letters, digits and _ only")
    m = json.loads(Path(manifest).read_text())
    by_part = defaultdict(list)
    for mr in m["rows"]:
        by_part[(mr.get("section"), mr.get("part"))].append(mr["key"])
    rows = []
    for mr in m["rows"]:
        res = [{"res": x, "role": "body", "joined_by": "texture manifest", "subjects": [mr["key"]],
                "former": [f for f in mr.get("former") or [] if f.rsplit("/", 1)[-1] == x.rsplit("/", 1)[-1]]}
               for x in mr["resources"]]
        sz = mr["size"]
        rows.append({"key": mr["key"], "kind": "building", "port": None, "donors": [], "pairing": {}, "placements": [],
                     "label": mr["label"], "defNames": [], "commonality_max": None,
                     "twins": [{"defName": k, "relation": "same_part_other_look"}
                               for k in by_part[(mr.get("section"), mr.get("part"))] if k != mr["key"]],
                     "artpipe_state_jobs": sorted(mr.get("jobs") or []), "render_match": mr.get("render_match"),
                     "standin": mr.get("standin"),
                     "reference_textures": mr.get("reference_textures") or [],
                     "runtimeSize": sz,
                     "runtimeDesc": {"def": mr["key"], "label": mr["label"],
                                     "description": f"{mr.get('part')} · look {mr.get('look')} · texture "
                                                    + ", ".join(mr["resources"]) + f" · drawn at {sz['drawSize'][0]:g}×{sz['drawSize'][1]:g} cells",
                                     "source": "texture manifest " + Path(manifest).name},
                     "canon": {"entry": None, "match": None, "images": [], "has_must_show": False, "ruled": False,
                               "wookieepedia": None, "canon_missing_entry": False},
                     "art": {"resources": res, "searched": "texture manifest (drawn by C#, no def): " + ", ".join(mr["resources"])}})
    key = f"SUBJECTS_{name}"
    path = BIOME_OUT / f"{name}.subjects.json"
    lab = label or name.replace("_", " ").capitalize()
    census = {"schema": 1, "generated": L.now(), "git_head": None, "biome_order": [key],
              "biomes": {key: {"label": lab, "slug": name, "subjects": True,
                               "ground_terrain": m.get("ground_terrain") or SUBJECT_GROUND,
                               "title": f"{lab} — game art", "lead_html": m.get("lead_html", ""), "rows": rows,
                               "textures_manifest": str(Path(manifest).resolve())}}}
    path.write_text(json.dumps(census, indent=1))
    return path, key


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doubles", action="store_true", help="every texPath shipped by >1 of our mods with different bytes")
    ap.add_argument("--biome", action="append", default=[],
                    help="build the per-biome sheet for this census biome key (repeatable); 'first3' = the first three in census order")
    ap.add_argument("--census", default=str(CENSUS))
    ap.add_argument("--refresh", action="store_true",
                    help="with --biome: first pull finished artpipe renders into the ledger (art.py backfill artpipe) "
                         "and re-run biome_census.py, so new renders show on the sheets")
    ap.add_argument("--date", help="date stamp in the biome sheet's file name (default today)")
    ap.add_argument("--sheet-only", action="store_true",
                    help="with --biome: rewrite the HTML only, never the decisions file — use while a sheet is being "
                         "reviewed live (an untouched-prefill decisions file is otherwise regenerated)")
    ap.add_argument("--allow-failing", metavar="REASON",
                    help="with --biome: if the gate fails, still write the sheet UNSTAMPED with a red banner naming what fails — "
                         "only for replacing a sheet that is itself unusable (blank). Never for a sheet that merely fails a requirement.")
    ap.add_argument("--subjects", nargs="*", default=[], metavar="DEF",
                    help="any game art by defName (buildings, items, gear, creatures, plants, UI defs): a gated, scaled sheet")
    ap.add_argument("--recommend", nargs="*", default=[], metavar="FAMILY=WHY",
                    help="with --subjects/--jobs: prefill the column of this render family (job id minus facing) with "
                         "the agent's reason — a suggestion shown as the agent prefill, never his answer")
    ap.add_argument("--jobs", nargs="*", default=[], metavar="JOB", help="artpipe job ids; each joins its target_def's row; JOB=DEF binds a job with no target_def")
    ap.add_argument("--textures", metavar="MANIFEST",
                    help="a texture manifest (art C# draws with no def): one row per texture, sized by the code that draws it")
    ap.add_argument("--name", help="with --subjects/--jobs: the sheet's name (lower_snake); file <name>_sheet_<date>.html")
    ap.add_argument("--label", help="with --subjects/--jobs: the sheet's human title")
    ap.add_argument("--lead", default="", help="with --subjects/--jobs: purpose paragraph (HTML) shown above the rows — "
                    "what he is judging and what skipping does")
    ap.add_argument("--reopen", nargs="*", default=[], metavar="DEF", help="with --subjects: rows to show OPEN even though he ruled them on another sheet (he asked to see them again)")
    ap.add_argument("--res", action="append", default=[])
    ap.add_argument("--out")
    ap.add_argument("--title", default="Art: all versions compared")
    ap.add_argument("--sheet-id")
    a = ap.parse_args(argv)
    if a.textures:
        if not a.name:
            ap.error("--textures needs --name")
        cpath, key = textures_census(a.name, Path(a.textures), a.label)
        a.biome, a.census = [key], str(cpath)
    elif a.subjects or a.jobs:
        for spec in a.recommend:
            fam, _, why = spec.partition("=")
            RECOMMEND[fam.strip()] = why.strip() or "the agent's pick"
        if not a.name:
            ap.error("--subjects/--jobs need --name")
        cpath, key = subjects_census(a.name, a.subjects, a.jobs, a.label, a.lead, a.reopen)
        a.biome, a.census = [key], str(cpath)
    if a.biome:
        if a.refresh:
            import subprocess
            here = Path(__file__).resolve().parent
            for cmd in ([sys.executable, str(here / "art.py"), "backfill", "artpipe"],
                        # the game's own copies of every row's texPath (donor/vanilla art), bound by texPath
                        [sys.executable, str(here / "gametex.py"), "ingest", "--census", str(a.census)],
                        [sys.executable, str(here / "biome_census.py"), "--out", str(Path(a.census).parent)]):
                print("refresh:", " ".join(cmd[1:]), flush=True)
                if subprocess.run(cmd, cwd=str(L.REPO_ROOT)).returncode:
                    raise SystemExit(f"refresh step failed: {cmd[1:]}")
        keys = []
        for k in a.biome:
            keys += json.loads(Path(a.census).read_text())["biome_order"][:3] if k == "first3" else [k]
        rc = 0
        for k in keys:
            try:
                r = generate_biome(k, Path(a.census), Path(a.out) if a.out and len(keys) == 1 else None, a.date,
                                   sheet_only=a.sheet_only, allow_failing=a.allow_failing)
            except SG.GateFailed as e:
                print(f"GATE FAILED for {k}: sheet NOT written; the previous sheet (if any) is untouched\n"
                      + SG.report(e.sheet, e.checks), file=sys.stderr)
                rc = 3
                continue
            print(json.dumps(r, indent=1))
        return rc
    if not a.out:
        ap.error("--out is required without --biome")
    idx = L.Index()
    res = list(a.res)
    brief = "<p>Pick, per row, the column the game should show. ✕ purges a picture for good.</p>"
    if a.doubles:
        res = doubles(idx) + res
        brief = DOUBLES_BRIEF
        if a.title == ap.get_default("title"):
            a.title = "Art doubles: pick the winner"
    out = Path(a.out)
    if not out.is_absolute():
        out = L.REPO_ROOT / out
    sid = a.sheet_id or out.stem
    r = generate(res, out, a.title, sid, brief)
    print(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

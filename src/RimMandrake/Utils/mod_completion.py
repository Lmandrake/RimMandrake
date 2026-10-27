#!/usr/bin/env python3
"""mod_completion.py -- how done is a mod, COMPUTED from evidence (item MOD_COMPLETION_MEASURE_HOW_DONE_IS_DONE).

    python3 src/RimMandrake/Utils/mod_completion.py <Mod> [<Mod>...] [--json OUT] [--md OUT] [--asof YYYY-MM-DD]

<Mod> is a folder under src/RimMandrake (GimmeSomeSlack, FlowWorks, ...). Nothing here is SET by anyone: the old
maturity dashboard failed because agents set levels by command. Every number below is folded from evidence on disk:

  inventory  player-facing defs in <Mod>/Defs (ThingDef minus motes/projectiles/ethereal, TerrainDef grouped into
             depth families, JobDef, RecipeDef, HediffDef, ThoughtDef, Need/Mental*, the mod's own liquid/fluid
             defs) + every bool switch in the mod's ModSettings (the mod's mechanics; "enabled"/debug excluded).
  works      latest status of every MOD-class row in the mod's proof/validation result JSONs (rows: id/status/
             class) and every ledger `verify` event at L2+ on an item attributed to the mod, credited to an
             inventory entry when the row/event text names its defName, settings key, or multi-word label.
             Latest-wins per (script,row) and per (item,criterion). Player-truth tables are read when present.
             An OWNER L3+ pass whose words name the whole mod credits every name present in the mod at its sha.
  art        artledger fold (live slots of the mod): owner keep / owner reject / donor / placeholder / unreviewed,
             plus human-timestamped review-sheet slot rulings (*.decisions.json; prefills ignored) and "owner-walked"
             (present at an owner whole-mod walk's sha, unchanged since); in-use = a def texPath or a C# literal
             reaches the slot; regen loops from art_eval/regen_rounds.json.
  owner      open items attributed to the mod that wait on the owner (needs=owner or for=OWNER), with ages.
  trends     ISO-week series: bugs filed, code reviews run vs defects they filed, live proof runs vs MOD fails,
             refiled/regression items. Signal from the last two weeks against the two before.

Item -> mod attribution: id keywords (MOD_KEYS; FlowWorks also takes flowworks_lane.json patterns), the title key in
the title's first 40 chars, or a closing commit that touches this mod and no other. TESTENV_* items are not bugs. Known blind spots: design/RimMandrake/
mod_completion_pilot_2026-10-26.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src" / "RimMandrake"
LEDGER = REPO / "infrastructure" / "state" / "ledger" / "events"
CODE_REVIEW = REPO / "infrastructure" / "state" / "code_review"
LANE = REPO / "infrastructure" / "state" / "flowworks_lane.json"
REGEN_ROUNDS = REPO / "infrastructure" / "state" / "art_eval" / "regen_rounds.json"
TRUTHS_GLOB = str(REPO / "design" / "RimMandrake" / "player_truth*.json")

# Keyword attribution of ledger items to a mod. Hose/pit/ladder items filed under GSS_ before the hoses moved
# belong to FlowWorks now (the hoses ship there): HOSE_TOKENS wins over GSS keywords.
MOD_KEYS = {
    "GimmeSomeSlack": [r"GSS", r"GIMME_?SOME_?SLACK|GIMMESOMESLACK", r"(^|_)SLACK(_|$)", r"(^|_)CORDS?(_|$)",
                       r"(^|_)AERIAL(_|$)", r"(^|_)OVERHEAD(_|$)", r"(^|_)MASTS?(_|$)", r"FALLEN_(WIRE|LINE|CORD)",
                       r"POWER_THEFT", r"TAP_?CLAMP", r"(^|_)RESTRING(_|$)"],
    "FlowWorks": [r"(^|_)(HOSES?|PITS?|LADDERS?|PIPES?|PONDS?|CANALS?|PUMPS?|TANKS?|WEIRS?|LIQUIDS?)(_|$)"],
}
HOSE_TOKENS = re.compile(r"(^|_)(HOSES?|PITS?|LADDERS?|PIPES?|PONDS?|CANALS?|PUMPS?|TANKS?)(_|$)")
TITLE_KEYS = {"GimmeSomeSlack": re.compile(r"gimme some slack|\bGSS\b", re.I),
              "FlowWorks": re.compile(r"flow ?works", re.I)}

BUGGY_KINDS = {"bug", "defect", "MOD", "fix", "code", "perf", "finding", "modcheck-failure"}
OPEN_STATES = {"open"}
EXCLUDED_THING_CATEGORIES = {"Mote", "Ethereal", "Projectile", "Gas", "Attachment", "PsychicEmitter"}
PLAYER_DEF_TYPES = {"ThingDef", "TerrainDef", "JobDef", "RecipeDef", "HediffDef", "ThoughtDef", "NeedDef",
                    "MentalStateDef", "MentalBreakDef"}
DEPTH_SUFFIX = re.compile(r"_?(Brim|Half|Superdeep|Trace|DeepStill|Deep|Shallow|Mid|Empty|Abyss|VeryShallow|Thin)$")
LEVEL_RANK = {"L0": 0, "L1": 1, "L2": 2, "GREEN-MIN": 2, "GREEN-FULL": 3, "L3": 3, "L4": 4}


def iso_week(ts: str) -> str:
    d = dt.date.fromisoformat(ts[:10])
    return (d - dt.timedelta(days=d.weekday())).isoformat()


def ts_of_name(p: Path) -> str | None:
    m = re.search(r"(20\d\d)(\d\d)(\d\d)T?(\d\d)?", p.name)
    if not m:
        return None
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}T{m.group(4) or '00'}:00:00"


# ---------------------------------------------------------------- inventory

def _short_type(tag: str, cls: str | None) -> str:
    t = cls or tag
    return t.rsplit(".", 1)[-1]


def read_defs(mod: str) -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(SRC / mod / "Defs" / "**" / "*.xml"), recursive=True)):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as e:
            print(f"warning: unparsable {f}: {e}", file=sys.stderr)
            continue
        for el in root:
            if not isinstance(el.tag, str):
                continue
            if el.get("Abstract", "").lower() == "true":
                continue
            name = el.findtext("defName")
            if not name:
                continue
            tex = [t.text.strip() for t in el.iter("texPath") if t.text] + \
                  [t.text.strip() for t in el.iter("texture") if t.text]
            out.append({"type": _short_type(el.tag, el.get("Class")), "defName": name.strip(),
                        "label": (el.findtext("label") or "").strip(), "category": (el.findtext("category") or ""),
                        "thingClass": el.findtext("thingClass") or "", "parent": el.get("ParentName") or "",
                        "tex": tex, "file": os.path.relpath(f, REPO)})
    return out


def read_switches(mod: str) -> list[dict]:
    """Bool ModSettings fields = the mod's behaviour switches (GSS: 'every behaviour has its own switch')."""
    out, seen = [], set()
    for f in sorted(glob.glob(str(SRC / mod / "Source" / "**" / "*.cs"), recursive=True)):
        if "SelfTest" in f:
            continue
        text = open(f, encoding="utf-8", errors="replace").read()
        if not re.search(r":\s*ModSettings\b", text):
            continue
        for m in re.finditer(r'Scribe_Values\.Look\(\s*ref\s+(\w+)\s*,\s*"(\w+)"\s*,\s*(true|false)\s*\)', text):
            key = m.group(2)
            if key in seen or key == "enabled" or key.lower().startswith("debug"):
                continue
            seen.add(key)
            out.append({"type": "Switch", "defName": key, "label": "", "file": os.path.relpath(f, REPO), "tex": []})
    return out


def inventory(mod: str) -> tuple[list[dict], list[dict], dict]:
    defs = read_defs(mod)
    raw = Counter(d["type"] for d in defs)
    inv, fams = [], {}
    for d in defs:
        t = d["type"]
        custom_liquid = t.endswith("LiquidDef") or t.endswith("FluidDef") or t.endswith("LiquidBodyDef")
        if t not in PLAYER_DEF_TYPES and not custom_liquid:
            continue
        if t == "ThingDef":
            if d["category"] in EXCLUDED_THING_CATEGORIES or "Mote" in d["thingClass"] or not d["label"]:
                continue
        if t == "TerrainDef":
            stem = DEPTH_SUFFIX.sub("", d["defName"]) or d["defName"]
            fam = fams.get(stem)
            if fam is None:
                fam = {"type": "TerrainFamily", "defName": stem, "label": re.sub(
                    r"\b(deep|shallow|brim|half|trace|superdeep)\b", "", d["label"], flags=re.I).strip(),
                       "members": [], "tex": [], "file": d["file"]}
                fams[stem] = fam
                inv.append(fam)
            fam["members"].append(d["defName"])
            fam["tex"] += d["tex"]
            continue
        d = dict(d)
        d["members"] = [d["defName"]]
        inv.append(d)
    sw = read_switches(mod)
    for s in sw:
        s["members"] = [s["defName"]]
    inv += sw
    return inv, defs, {"raw_def_types": dict(raw), "switches": len(sw)}


# ---------------------------------------------------------------- ledger

def read_ledger() -> list[dict]:
    evs = []
    for f in sorted(LEDGER.glob("*.jsonl")):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                evs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    evs.sort(key=lambda e: e.get("ts", ""))
    return evs


def fold_items(evs: list[dict]) -> dict:
    items = {}
    for e in evs:
        i = e.get("id")
        if not i:
            continue
        ev = e.get("event")
        if ev == "file":
            it = items.setdefault(i, {"id": i, "state": "open", "verifies": [], "notes": []})
            it.update({k: e.get(k) for k in ("title", "kind", "needs", "for", "spec", "why", "caused_by", "seat")})
            it["filed"] = e.get("ts")
            it["state"] = "open"
        it = items.get(i)
        if it is None:
            continue
        if ev == "close":
            it["state"], it["closed"], it["close_sha"] = "closed", e.get("ts"), e.get("sha")
        elif ev in ("drop", "supersede"):
            it["state"], it["closed"] = ev, e.get("ts")
        elif ev == "needs":
            it["needs"] = e.get("needs", it.get("needs"))
        elif ev == "reassign":
            it["for"] = e.get("to", it.get("for"))
        elif ev == "verify":
            it["verifies"].append(e)
        elif ev == "implemented":
            it["criteria"] = e.get("criteria")
    return items


def commits_touching(mod: str) -> set[str]:
    try:
        out = subprocess.run(["git", "-C", str(REPO), "log", "--format=%H", "--", f"src/RimMandrake/{mod}"],
                             capture_output=True, text=True, timeout=120).stdout
    except subprocess.TimeoutExpired:
        return set()
    return set(out.split())


MOD_ROOT = re.compile(r"^src/([^/]+)/([^/]+)/")    # every src root counts (RimStarWars, RimUtinni, Jawa, ...)
SHARED_DIRS = {"Utils", "rimflow", "Bridge"}           # under src/RimMandrake only


def touched_mods(paths) -> set[str]:
    """Mods a commit's paths touch: a RimMandrake mod by its bare name, any other root as root/name, shared dirs out."""
    mods = set()
    for m in map(MOD_ROOT.match, paths):
        if m:
            root, name = m.groups()
            if root != "RimMandrake":
                mods.add(f"{root}/{name}")
            elif name not in SHARED_DIRS:
                mods.add(name)
    return mods


def only_this_mod(sha: str, mod: str) -> bool:
    """A close commit is evidence of the mod only when the mod is the one mod it touches (run 2 credited GSS with
    a bridge-tool fix and a Pyrelands selftest fix because their commits also carried GSS files)."""
    try:
        out = subprocess.run(["git", "-C", str(REPO), "show", "--name-only", "--format=", sha],
                             capture_output=True, text=True, timeout=60).stdout
    except subprocess.TimeoutExpired:
        return False
    return touched_mods(out.splitlines()) == {mod}


def attribute(items: dict, mod: str, all_mods: list[str]) -> set[str]:
    pats = [re.compile(p) for p in MOD_KEYS.get(mod, [])]
    if mod == "FlowWorks" and LANE.exists():
        lane = json.loads(LANE.read_text())["id_patterns"]
        pats += [re.compile(p) for p in lane if "GSS_" not in p and "CORD_" not in p]
    touched = commits_touching(mod)
    tk = TITLE_KEYS.get(mod)
    mine = set()
    for i, it in items.items():
        # the title key must sit in the title's subject position (first 40 chars): run 3 credited GSS with a
        # bridge-tool bug and a Pyrelands selftest bug whose titles mention GSS only as the site of the run
        hit = any(p.search(i) for p in pats) or bool(tk and tk.search((it.get("title") or "")[:40]))
        if mod == "GimmeSomeSlack" and HOSE_TOKENS.search(i):
            hit = False
        if mod == "FlowWorks" and not hit and HOSE_TOKENS.search(i) and re.search(r"GSS|SLACK", i):
            hit = True
        if not hit and it.get("close_sha"):
            s = str(it["close_sha"])
            full = next((c for c in touched if c.startswith(s)), None) if len(s) >= 7 else None
            if full and only_this_mod(full, mod):
                hit = True
        if hit:
            mine.add(i)
    return mine


# ---------------------------------------------------------------- evidence

def owner_mod_walks(evs: list[dict], mod: str) -> list[dict]:
    """Owner-run L3+ verify events whose words name the whole mod ("GimmeSomeSlack all looks great! Verified.").
    Run 1 missed these: the text names no def, so no entry was credited although the owner walked every station."""
    name_re = re.compile(re.escape(mod) + "|" + TITLE_KEYS.get(mod, re.compile("$^")).pattern, re.I)
    out = []
    for e in evs:
        if e.get("event") != "verify" or LEVEL_RANK.get(e.get("level") or "", 0) < 3:
            continue
        if str(e.get("result")).lower() != "pass":
            continue
        if not (e.get("seat") == "OWNER" or "owner" in str(e.get("ranBy") or "").lower()):
            continue
        if name_re.search(str(e.get("ownerSaid") or "") + " " + str(e.get("why") or "")) and e.get("sha"):
            out.append(e)
    return out


def names_at(sha: str, mod: str) -> set[str]:
    """Every defName and quoted identifier in the mod's tree at a commit: what existed when the owner walked it."""
    try:
        out = subprocess.run(["git", "-C", str(REPO), "grep", "-h", "-o", "-E",
                              r"<defName>[^<]+</defName>|\"[A-Za-z_][A-Za-z0-9_]*\"", sha, "--",
                              f"src/RimMandrake/{mod}/Defs", f"src/RimMandrake/{mod}/Source"],
                             capture_output=True, text=True, timeout=120).stdout
    except subprocess.TimeoutExpired:
        return set()
    return {re.sub(r"</?defName>|\"", "", x) for x in out.split()}


def changed_since(sha: str, mod: str) -> set[str] | None:
    try:
        r = subprocess.run(["git", "-C", str(REPO), "diff", "--name-only", sha, "HEAD", "--",
                            f"src/RimMandrake/{mod}/Textures"], capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode:
        return None
    pre = f"src/RimMandrake/{mod}/Textures/"
    return {x[len(pre):] for x in r.stdout.split()}


def proof_runs(mod: str, extra_paths: set[str]) -> list[dict]:
    paths = {os.path.realpath(p) for p in glob.glob(str(SRC / mod / "**" / "*.json"), recursive=True)}
    paths |= {os.path.realpath(p) for p in extra_paths}      # one file named two ways counts once
    runs = []
    for p in sorted(paths):
        pp = Path(p)
        try:
            d = json.loads(pp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict) or not isinstance(d.get("rows"), list):
            continue
        started = d.get("started") or ts_of_name(pp) or dt.datetime.fromtimestamp(pp.stat().st_mtime).isoformat()
        offline = d.get("mode") == "offline" or d.get("offline") is True
        script = d.get("script") or re.sub(r"_?\d{8}T.*$", "", pp.stem)
        rows = []
        for r in d["rows"]:
            if not isinstance(r, dict) or "status" not in r:
                continue
            rows.append({"id": str(r.get("id")), "status": str(r.get("status")).upper(),
                         "class": str(r.get("class") or "MOD").upper(), "text": json.dumps(r, default=str)})
        runs.append({"path": os.path.relpath(p, REPO), "script": script, "started": str(started),
                     "level": "L1" if offline else "L2", "rows": rows})
    runs.sort(key=lambda r: r["started"])
    return runs


def player_truths(mod: str) -> list[dict]:
    out = []
    for p in glob.glob(TRUTHS_GLOB):
        try:
            d = json.loads(Path(p).read_text())
        except Exception:
            continue
        for t in d.get("truths", []) if isinstance(d, dict) else []:
            if t.get("mod", mod) == mod:
                out.append({"source": os.path.relpath(p, REPO), **t})
    return out


def snake(name: str) -> str | None:
    """RM_FallenWireShock / fallenWireShock -> fallen_wire_shock: proof row ids are snake_case."""
    core = re.sub(r"^(RM|RSW|RUT)_", "", name)
    parts = [p for p in re.split(r"_|(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", core) if p]
    return "_".join(p.lower() for p in parts) if len(parts) >= 2 else None


def matcher(entry: dict):
    toks = set(entry.get("members", [])) | {entry["defName"]}
    toks |= {sn for t in list(toks) if (sn := snake(t))}
    # a defName/key is matched whole (underscore is part of the name); a snake form is matched between
    # non-alphanumerics so it is found inside a row id like P7_fallen_wire_shock_live
    pats = [re.compile(r"(?<![A-Za-z0-9_])" + re.escape(t) + r"(?![A-Za-z0-9_])") if t != t.lower() or "_" not in t
            else re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", re.I)
            for t in toks if len(t) >= 4]
    lab = (entry.get("label") or "").strip().lower()
    lab_pat = re.compile(r"\b" + re.escape(lab) + r"\b", re.I) if len(lab.split()) >= 2 else None

    def m(text: str) -> str | None:
        for p in pats:
            if p.search(text):
                return "name"
        if lab_pat and lab_pat.search(text):
            return "label"
        return None
    return m


def judge_works(inv, runs, verifies, truths, walks=()):
    # latest status per (script,row) among MOD rows; per (item,criterion) among L2+ verify events
    latest_rows = {}
    for r in runs:
        for row in r["rows"]:
            if row["class"] not in ("MOD", "NONE", ""):
                continue
            latest_rows[(r["script"], row["id"])] = {**row, "started": r["started"], "level": r["level"],
                                                     "path": r["path"]}
    latest_ver = {}
    for v in verifies:
        latest_ver[(v["id"], v.get("criterion") or "")] = v
    out = []
    for e in inv:
        m = matcher(e)
        ev = []
        for k, row in latest_rows.items():
            how = m(row["text"])
            if how:
                ev.append({"src": "row", "key": f"{k[0]}:{k[1]}", "status": row["status"], "level": row["level"],
                           "when": row["started"], "how": how, "path": row["path"]})
        for k, v in latest_ver.items():
            text = json.dumps({x: v.get(x) for x in ("why", "criterion", "evidence", "config", "title_")}) \
                + " " + (v.get("_title") or "")
            how = m(text)
            if how:
                st = {"pass": "PASS", "fail": "FAIL"}.get(str(v.get("result")).lower(), str(v.get("result")).upper())
                ev.append({"src": "verify", "key": f"{k[0]}:{k[1]}", "status": st, "level": v.get("level") or "L?",
                           "when": v.get("ts"), "how": how})
        for t in truths:
            how = m(json.dumps(t))
            if how:
                ev.append({"src": "truth", "key": t.get("id"), "status": str(t.get("status")).upper(),
                           "level": "L1", "when": t.get("checked"), "how": how})
        for w in walks:
            if e["defName"] in w["names"] or set(e.get("members", [])) & w["names"]:
                ev.append({"src": "owner-walk", "key": f"{w['id']}:{w.get('criterion') or ''}", "status": "PASS",
                           "level": w.get("level"), "when": w.get("ts"), "how": "owner named the whole mod"})
        l2 = [x for x in ev if LEVEL_RANK.get(x["level"], 0) >= 2]
        fails = [x for x in l2 if x["status"] in ("FAIL", "PARTIAL", "ERROR")]
        passes = [x for x in l2 if x["status"] == "PASS"]
        if fails:
            status = "broken"
        elif passes:
            status = "works"
        elif any(x["status"] == "PASS" for x in ev):
            status = "offline-only"
        else:
            status = "unverified"
        out.append({"defName": e["defName"], "type": e["type"], "label": e.get("label", ""),
                    "members": len(e.get("members", [])), "status": status,
                    "by_label_only": bool(ev) and all(x["how"] == "label" for x in ev),
                    "owner_walk_only": bool(passes) and all(x["src"] == "owner-walk" for x in passes),
                    "n_pass": len(passes), "n_fail": len(fails),
                    "fails": [f"{x['key']} ({x['when'][:10] if x['when'] else '?'})" for x in fails][:4],
                    "last_pass": max((x["when"] or "" for x in passes), default="")[:10]})
    return out


# ---------------------------------------------------------------- art

SHEET_ROOTS = (REPO / "Transient", REPO / "infrastructure" / "state")
KEEP_STATES, DROP_STATES = {"pick", "keep", "accept"}, {"reject", "redo", "retire", "out"}


def sheet_rulings(mod: str) -> dict:
    """Human rulings from review-sheet sidecars, per texture path prefix (latest wins).
    Only slot entries carrying their own timestamp count: an entry whose decision merely equals its prefill, with
    no decidedAt, is an agent guess (review-sheets skill), and the 2026-10-11 GSS sheet holds 147 of those."""
    pre = f"RimMandrake/{mod}/"
    out = {}
    for root in SHEET_ROOTS:
        for f in root.rglob("*.decisions.json"):
            try:
                d = json.loads(f.read_text())
            except (OSError, ValueError):
                continue
            dec = d.get("decisions") if isinstance(d, dict) else None
            if not isinstance(dec, dict):
                continue
            for v in dec.values():
                if not isinstance(v, dict) or not (v.get("decidedAt") or v.get("at")):
                    continue
                for slot, sv in (v.get("slots") or {}).items():
                    if not slot.startswith(pre) or not isinstance(sv, dict):
                        continue
                    st = str(sv.get("state") or "").lower()
                    verdict = "keep" if st in KEEP_STATES else "drop" if st in DROP_STATES else None
                    at = str(sv.get("at") or v.get("decidedAt") or v.get("at"))
                    if verdict and (slot not in out or at >= out[slot]["at"]):
                        out[slot] = {"verdict": verdict, "at": at, "sheet": f.name}
    return out


def source_literals(mod: str) -> set[str]:
    """Texture paths and bare names the mod's C# loads directly. GSS draws its cords from code, composing
    `Dir + "Strand_Jawa"`, so a full-path literal alone missed them (r4): bare quoted names are kept too and are
    matched against a slot's file stem."""
    lits = set()
    for f in (SRC / mod / "Source").rglob("*.cs") if (SRC / mod / "Source").exists() else []:
        if "SelfTest" in f.parts or "/obj/" in str(f):
            continue
        lits |= set(re.findall(r'"([A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)*)/?"', f.read_text(errors="replace")))
    return lits


def art_report(mod: str, defs: list[dict], walks=()) -> dict:
    sys.path.insert(0, str(SRC / "Utils" / "art"))
    try:
        import artledger as A  # noqa
    except Exception as e:  # pragma: no cover
        return {"error": f"artledger unavailable: {e}"}
    idx = A.cached_index()
    key = f"src/RimMandrake/{mod}"
    live = {r: ev for (m, r), ev in idx.live.items() if m == key}
    def_tex = {t for d in defs for t in d["tex"]}
    lits = source_literals(mod)  # C# literals widen "in use"; only def texPaths can be "missing"
    texpaths = def_tex | {x for x in lits if "/" in x}
    names = {x for x in lits if "/" not in x and len(x) >= 4}
    sheets = sheet_rulings(mod)
    walked = set()  # live rels present at an owner whole-mod walk and unchanged since
    walk_note = []
    for w in walks:
        ch = changed_since(w["sha"], mod)
        if ch is None:
            continue
        at_walk = set(subprocess.run(["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", w["sha"], "--",
                                      f"src/RimMandrake/{mod}/Textures"], capture_output=True, text=True,
                                     timeout=120).stdout.split())
        pre = f"src/RimMandrake/{mod}/Textures/"
        walked |= {x[len(pre):] for x in at_walk} - ch
        walk_note.append(f"{w['id']}@{w['sha'][:10]}")

    def sheet_of(rel: str):
        best = None
        for slot, r in sheets.items():
            if rel.startswith(slot) and (best is None or len(slot) > len(best[0])):
                best = (slot, r)
        return best[1] if best else None

    def in_use(rel: str) -> bool:
        stem = re.sub(r"(_(north|south|east|west|a|b|c|d|m|[0-9]+))*\.png$", "", rel, flags=re.I)
        stem = re.sub(r"^Textures/", "", stem)
        if stem.rsplit("/", 1)[-1] in names:
            return True
        return any(stem == t or stem.startswith(t + "/") or stem.startswith(t + "_") or t.startswith(stem)
                   for t in texpaths if t.count("/") >= 2)  # a bare namespace literal is not a texture

    rows = Counter()
    lists = defaultdict(list)
    sub_rulings = {}
    for r in idx.rulings:
        sk = A.canonical_subject(r.get("subject_key") or "")
        if sk and r.get("by") == "owner":
            cur = sub_rulings.get(sk)
            if cur is None or r.get("ts", "") >= cur.get("ts", ""):
                sub_rulings[sk] = r
    for rel, ev in sorted(live.items()):
        sha = ev.get("sha")
        reason = str(ev.get("reason") or "")
        subj = A.canonical_subject(A.subject_of_rel(rel)) if hasattr(A, "subject_of_rel") else ""
        sr = sub_rulings.get(subj)
        sh = sheet_of(rel)
        if sh and reason != "backfill-observed" and sh["at"] < str(ev.get("ts") or "")[:10]:
            sh = None  # the art was replaced after the sheet ruled on it; that ruling was about other pixels
        if idx.protected(sha):
            cls = "owner-kept"
        elif idx.rejection(sha) or (sr and sr.get("verdict") in ("redo", "reject", "out", "replace-donor")):
            cls = "owner-rejected"
        elif sh and sh["verdict"] == "drop":
            cls = "owner-rejected-sheet"
        elif sh and sh["verdict"] == "keep":
            cls = "owner-kept-sheet"
        elif sr and sr.get("verdict") in ("keep", "accept", "in", "confirm"):
            cls = "owner-kept-subject"
        elif rel in walked:
            cls = "owner-walked"
        elif "donor" in reason:
            cls = "donor"
        elif ev.get("placeholder") or "placeholder" in reason:
            cls = "placeholder"
        else:
            cls = "unreviewed"
        use = in_use(rel)
        rows[(cls, use)] += 1
        lists[cls].append(rel)
    regen = {}
    if REGEN_ROUNDS.exists():
        rr = json.loads(REGEN_ROUNDS.read_text())
        names = {d["defName"] for d in defs}
        regen = {k: v for k, v in rr.items() if k.split("__")[0] in names and isinstance(v, int) and v >= 2}
    total = len(live)
    accepted = sum(v for (c, u), v in rows.items() if c.startswith("owner-kept"))
    used = sum(v for (c, u), v in rows.items() if u)
    accepted_used = sum(v for (c, u), v in rows.items() if c.startswith("owner-kept") and u)
    walked_used = sum(v for (c, u), v in rows.items() if c == "owner-walked" and u)
    # unresolved texPaths: no live slot under that path
    rels = list(live)
    # only the mod's own texture namespace can be missing here; other paths are vanilla's or another mod's
    missing = sorted(t for t in def_tex if t.startswith(f"RimMandrake/{mod}/") and not any(r.startswith(t) for r in rels)
                     and not (SRC / mod / "Textures" / (t + ".png")).exists()
                     and not list((SRC / mod / "Textures").glob(t + "*")))
    return {"live_slots": total, "in_use": used, "accepted": accepted, "accepted_in_use": accepted_used,
            "walked_in_use": walked_used, "walks": walk_note, "sheet_rulings": len(sheets),
            "by_class": {f"{c}{'' if u else ' (not referenced by a def texPath or C# literal)'}": v
                         for (c, u), v in sorted(rows.items())},
            "rejected_sheet_still_live": lists.get("owner-rejected-sheet", [])[:20],
            "rejected_still_live": lists.get("owner-rejected", [])[:20],
            "donor": lists.get("donor", [])[:20], "placeholder": lists.get("placeholder", [])[:20],
            "regen_looping": regen, "texpaths_without_art": missing[:30], "n_texpaths": len(def_tex)}


# ---------------------------------------------------------------- trends

def code_review_weeks(mod: str) -> Counter:
    c = Counter()
    seen = set()
    pref = f"src/RimMandrake/{mod}/"
    for f in CODE_REVIEW.glob("*.jsonl"):
        for line in open(f, encoding="utf-8"):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("verdict") == "pruned" or not str(d.get("path", "")).startswith(pref):
                continue
            k = (d["path"], d.get("sha256"))
            if k in seen:
                continue
            seen.add(k)
            c[iso_week(d["ts"])] += 1
    return c


def is_bug(i: str, it: dict) -> bool:
    """A defect in the mod. TESTENV_* items are the test environment's own hazards (monolith letters, fixture
    vitals), filed as kind bug: they measure the harness, not the mod, so they are not counted."""
    return it.get("kind") in BUGGY_KINDS and not i.startswith("TESTENV_")


def trends(mod_items: dict, items: dict, runs: list[dict], cr: Counter, asof: dt.date) -> dict:
    weeks = defaultdict(lambda: Counter())
    refiled = []
    for i, it in mod_items.items():
        if not it.get("filed"):
            continue
        w = iso_week(it["filed"])
        text = " ".join(str(it.get(k) or "") for k in ("title", "why", "spec"))
        bug = is_bug(i, it)
        if bug:
            weeks[w]["bugs_filed"] += 1
            if re.search(r"code[- ]review|full-file review", text, re.I):
                weeks[w]["code_review_defects"] += 1
            if re.search(r"\blive\b|walk|round \d|proof|in[- ]game|bridge", text, re.I):
                weeks[w]["live_found_bugs"] += 1
        cb = it.get("caused_by")
        regress = re.search(r"AGAIN|STILL|TWICE|REOPEN|REGRESS|RETURNS|PASSED_LAST_WEEK", i)
        if bug and ((cb and items.get(cb, {}).get("state") == "closed" and cb in mod_items) or regress):
            weeks[w]["refiled"] += 1
            refiled.append(i)
    for r in runs:
        if r["level"] != "L2":
            continue
        w = iso_week(r["started"])
        weeks[w]["live_runs"] += 1
        weeks[w]["live_mod_fail_rows"] += sum(1 for x in r["rows"] if x["class"] == "MOD" and x["status"] == "FAIL")
        weeks[w]["live_mod_rows"] += sum(1 for x in r["rows"] if x["class"] == "MOD")
    for it in mod_items.values():
        for v in it["verifies"]:
            if LEVEL_RANK.get(v.get("level") or "", 0) >= 2:
                w = iso_week(v["ts"])
                weeks[w]["verify_l2"] += 1
                if str(v.get("result")).lower() != "pass":
                    weeks[w]["verify_l2_notpass"] += 1
    for w, n in cr.items():
        weeks[w]["code_reviews"] += n
    series = [{"week": w, **dict(weeks[w])} for w in sorted(weeks)]
    # signal: bugs filed in the last 14 days against the 14 before (rolling dates, not ISO weeks: a Monday
    # as-of made a 1-day partial week scale x7 in run 1)
    filed = [dt.date.fromisoformat(it["filed"][:10]) for i, it in mod_items.items()
             if it.get("filed") and is_bug(i, it)]
    recent = sum(1 for d in filed if 0 <= (asof - d).days < 14)
    prior = sum(1 for d in filed if 14 <= (asof - d).days < 28)
    if recent <= 2:
        sig = "quiet"
    elif recent < 0.7 * prior:
        sig = "slowing"
    else:
        sig = "still finding"
    return {"series": series, "signal": sig, "recent_2wk_bugs": recent, "prior_2wk_bugs": prior,
            "refiled": refiled}


# ---------------------------------------------------------------- report

def report(mod: str, evs, items, all_mods, asof: dt.date) -> dict:
    inv, defs, raw = inventory(mod)
    mine_ids = attribute(items, mod, all_mods)
    mod_items = {i: items[i] for i in mine_ids}
    verifies = []
    extra = set()
    for it in mod_items.values():
        for v in it["verifies"]:
            if LEVEL_RANK.get(v.get("level") or "", 0) >= 2:
                verifies.append({**v, "_title": it.get("title") or ""})
            evp = str(v.get("evidence") or "")
            for part in re.split(r"[\s,;]+", evp):
                if part.endswith(".json") and (REPO / part).is_file():
                    extra.add(str(REPO / part))
    runs = proof_runs(mod, extra)
    truths = player_truths(mod)
    walks = []
    for w in owner_mod_walks(evs, mod):
        walks.append({**w, "names": names_at(w["sha"], mod)})
    works = judge_works(inv, runs, verifies, truths, walks)
    st = Counter(w["status"] for w in works)
    st_type = defaultdict(Counter)
    for w in works:
        st_type[w["type"]][w["status"]] += 1
    art = art_report(mod, defs, walks)
    now = dt.datetime.combine(asof, dt.time(23, 59))
    waiting = []
    for i, it in mod_items.items():
        if it["state"] != "open":
            continue
        if (it.get("needs") == "owner" or it.get("for") == "OWNER") and it.get("filed"):
            age = (now - dt.datetime.fromisoformat(it["filed"][:19])).days
            waiting.append({"id": i, "age_days": age, "kind": it.get("kind"), "title": (it.get("title") or "")[:110]})
    waiting.sort(key=lambda x: -x["age_days"])
    open_bugs = sorted(i for i, it in mod_items.items() if it["state"] == "open" and is_bug(i, it))
    tr = trends(mod_items, items, runs, code_review_weeks(mod), asof)
    n = len(works)
    pct_works = round(100 * st["works"] / n, 1) if n else 0.0
    pct_art = round(100 * art.get("accepted_in_use", 0) / art["in_use"], 1) if art.get("in_use") else 0.0
    pct_walked = round(100 * art.get("walked_in_use", 0) / art["in_use"], 1) if art.get("in_use") else 0.0
    return {"mod": mod, "asof": asof.isoformat(), "inventory": {"entries": n, **raw,
            "by_type": dict(Counter(w["type"] for w in works))},
            "works": {"counts": dict(st), "by_type": {k: dict(v) for k, v in st_type.items()},
                      "label_only_credit": sum(1 for w in works if w["status"] == "works" and w["by_label_only"]),
                      "owner_walk_only_credit": sum(1 for w in works if w["status"] == "works" and w["owner_walk_only"]),
                      "owner_walks": [f"{w['id']} {w.get('level')} {str(w.get('ts'))[:10]} @{w['sha']}: "
                                      f"{w.get('ownerSaid')}" for w in walks],
                      "entries": works, "proof_runs": len(runs), "l2_runs": sum(1 for r in runs if r["level"] == "L2"),
                      "verify_l2_events": len(verifies), "player_truths": len(truths)},
            "art": art, "waiting_on_owner": waiting, "open_bug_items": open_bugs,
            "items": {"attributed": len(mod_items), "open": sum(1 for x in mod_items.values() if x["state"] == "open")},
            "trends": tr,
            "headline": {"pct_verified_working": pct_works, "pct_broken": round(100 * st["broken"] / n, 1) if n else 0,
                         "pct_art_accepted_of_in_use": pct_art, "pct_art_only_seen_in_owner_walk": pct_walked, "settledness": tr["signal"],
                         "open_bugs": len(open_bugs), "waiting_on_owner": len(waiting)}}


def to_md(r: dict) -> str:
    h, w, a, t = r["headline"], r["works"], r["art"], r["trends"]
    L = [f"### {r['mod']} (as of {r['asof']})", "",
         f"**Headline:** {h['pct_verified_working']}% of {r['inventory']['entries']} inventory entries verified "
         f"working at L2+ ({h['pct_broken']}% with a failing latest L2 row); art explicitly accepted {h['pct_art_accepted_of_in_use']}% "
         f"of in-use slots (+{h['pct_art_only_seen_in_owner_walk']}% only seen, unchanged, in an owner whole-mod walk); settledness **{h['settledness']}** (bugs filed last 2 wk {t['recent_2wk_bugs']} "
         f"vs prior 2 wk {t['prior_2wk_bugs']}); {h['open_bugs']} open bug items; {h['waiting_on_owner']} items "
         f"waiting on the owner. No composite score: the parts do not share a unit.", "",
         f"**1. Inventory** {r['inventory']['entries']} entries: {r['inventory']['by_type']}. Raw def types: "
         f"{r['inventory']['raw_def_types']}.", "",
         f"**2. Works** {w['counts']} from {w['l2_runs']} live proof runs ({w['proof_runs']} result files), "
         f"{w['verify_l2_events']} L2+ verify events, {w['player_truths']} player truths; "
         f"{w['label_only_credit']} 'works' credited by label match only, "
         f"{w.get('owner_walk_only_credit', 0)} only by an owner whole-mod walk "
         f"({'; '.join(w.get('owner_walks') or []) or 'none'}).", ""]
    L.append("| type | works | broken | offline-only | unverified |")
    L.append("|---|---|---|---|---|")
    for k, v in sorted(w["by_type"].items()):
        L.append(f"| {k} | {v.get('works', 0)} | {v.get('broken', 0)} | {v.get('offline-only', 0)} | "
                 f"{v.get('unverified', 0)} |")
    br = [e for e in w["entries"] if e["status"] == "broken"]
    un = [e["defName"] for e in w["entries"] if e["status"] == "unverified"]
    L += ["", f"Broken ({len(br)}): " + "; ".join(f"{e['defName']} <- {', '.join(e['fails'][:2])}" for e in br[:15])
          + (" ..." if len(br) > 15 else ""), "",
          f"Unverified ({len(un)}): " + ", ".join(un[:60]) + (" ..." if len(un) > 60 else ""), ""]
    L += [f"**3. Art** {a.get('live_slots')} live texture slots, {a.get('in_use')} reached by a def texPath or C# literal; "
          f"owner-accepted {a.get('accepted')} ({a.get('accepted_in_use')} in use). By class: {a.get('by_class')}. "
          f"Regen-looping (>=2 rounds): {a.get('regen_looping') or 'none'}. texPaths with no art: "
          f"{len(a.get('texpaths_without_art', []))} of {a.get('n_texpaths')} {a.get('texpaths_without_art', [])[:8]}.", ""]
    wo = r["waiting_on_owner"]
    L += [f"**4. Waiting on owner** {len(wo)}: " + "; ".join(f"{x['id']} ({x['age_days']} d)" for x in wo[:12]), ""]
    L += ["**5. Settledness (ISO week starting)**", "",
          "| week | bugs filed | code reviews | defects from code review | live runs | MOD fail rows / MOD rows | "
          "L2 verifies not-pass / all | live-found bugs | refiled |", "|---|---|---|---|---|---|---|---|---|"]
    for s in t["series"][-8:]:
        L.append(f"| {s['week']} | {s.get('bugs_filed', 0)} | {s.get('code_reviews', 0)} | "
                 f"{s.get('code_review_defects', 0)} | {s.get('live_runs', 0)} | {s.get('live_mod_fail_rows', 0)} / "
                 f"{s.get('live_mod_rows', 0)} | {s.get('verify_l2_notpass', 0)} / {s.get('verify_l2', 0)} | "
                 f"{s.get('live_found_bugs', 0)} | {s.get('refiled', 0)} |")
    L += ["", f"Refiled/regression items: {len(t['refiled'])} {t['refiled'][:8]}", ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mods", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--md")
    ap.add_argument("--asof", default=dt.date.today().isoformat())
    a = ap.parse_args(argv)
    for m in a.mods:
        if not (SRC / m / "Defs").is_dir():
            ap.error(f"no such mod with Defs: src/RimMandrake/{m}")
    asof = dt.date.fromisoformat(a.asof)
    # --asof replays the ledger up to that day (proof result files and git state are still read as of now)
    evs = [e for e in read_ledger() if str(e.get("ts") or "")[:10] <= a.asof]
    items = fold_items(evs)
    reps = [report(m, evs, items, a.mods, asof) for m in a.mods]
    md = "\n\n".join(to_md(r) for r in reps)
    if a.json:
        Path(a.json).write_text(json.dumps(reps, indent=1, default=str))
    if a.md:
        Path(a.md).write_text(md)
    for r in reps:
        print(r["mod"], json.dumps(r["headline"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

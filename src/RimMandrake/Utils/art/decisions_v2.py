#!/usr/bin/env python3
"""decisions_v2.py — biome art sheet decisions, schema 2 (DESIGN 2026-10-10 §3.5), and the one-off migration of schema-1
files. Every reader of a decisions record (enact, ingest, artledger.decision_letters) goes through here.

A schema-2 record keeps every schema-1 field it had (`decision`, `picks`, `purge`, `note` …) and adds:

  schema: 2                     version gate: a reader that does not know 2 must refuse the record (enact does)
  rev                           the sheet's snapshotId when the row was saved (its inventory revision)
  slots{lane: {state, pick, set_id, slot_id, at}}
                                state: pick | accept (keep what the game shows, unchanged) | redraw | not_drawn.
                                An absent lane = unreviewed, unchanged (never a choice of his).
  pool{lane: {add: [L], remove: [L], baseline: [set_id]}}
                                his random-pool edits, only on a lane that IS a random pool; baseline = the pool's
                                membership (set ids) when he edited it — enact refuses if the live pool has moved.
  reject{lane: [L]}             ✕ not for this slot (deletes nothing)
  retire{lane: [L]}             retire a LIVE picture from the game. With another set picked in that lane it leaves in
                                the SAME enact as the pick's install (owner 2026-10-12, one pass); with none the lane is a
                                redraw and the picture stays until its replacement is installed
  purge: [sha]                  delete from the art store (unchanged from schema 1)
  assign{L: lane|"not_needed"|"other_subject:<def>"}
                                an unassigned (found-by-name) render he labelled; only then is it pickable
  asks{rename: {name, suggest}, describe: keep|improve|rewrite, more: [{slot, n, base, how}],
       facings: {slot, from, faces}, size: {bodySize, drawScale, scope}, move: {biome, tier}, cut: bool}
  setIds{L: set_id}             every letter the record names -> the pictures it meant (sheet_slots.set_id)
  legacyVariants: [L]           schema-1 variant ticks that may have been the machine's default laundered into his
                                (bug 2026-10-10): NOTHING ships from them until he says keep on that picture in its
                                biome sheet row; until then they only protect their pictures from deletion
  legacyRuled{L: {v, at}}       his answer per legacy tick, clicked in the row: v = confirm (keep) | drop
  legacyVariantsDefault: [L]    the machine's own pre-tick list (`variantsDefault`): never his, never protects
  quarantine: [L]               letters the migration could not resolve against the snapshot he saved against

Owner provenance (owner 2026-10-12; `decision_is_his`, `owner_view`): a row's `decision` letter is HIS only when his
click stamped it (`decidedAt`), it was carried from his earlier ruling (`carriedRuledAt`), or it overrides the prefill.
The page seeds every row's `decision` with the agent's prefill, and a row saved for a note or a ✕ carries that seed to
disk: it is the agent's guess, never a decision, and every consumer reads records through `owner_view`.

Returned sheets (owner 2026-10-12: "I never return a sheet without reviewing every item, so please assume "accept
unchanged" is true if I didn't change anything"): there is no accept control. `--returned "<his words>"` stamps
`returned{at, said, by}` on the file when he says the sheet is done; every slot he left alone then keeps what the game
draws (enact does nothing to it; ingest records it as his keep of the in-game set, `raw_verdict: returned-unchanged`).

Migration (`migrate_doc`) resolves every letter against the snapshot the file was SAVED against (its snapshotId, from
git history when a later rebuild replaced it), never today's sheet.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sheet_slots as SL  # noqa: E402

SCHEMA = 2
STATES = ("pick", "accept", "redraw", "not_drawn")
CONFIRM_SHEET = "old_ticks_confirm_2026-10-10"


def schema_of(v) -> int:
    try:
        return int((v or {}).get("schema") or 1)
    except (TypeError, ValueError):
        return 99


def refuse_unknown(doc: dict) -> str | None:
    """Error text when any record (or the file) carries a schema this build does not know."""
    if schema_of(doc) > SCHEMA:
        return f"decisions file is schema {doc.get('schema')}; this build reads 1 and 2 only"
    bad = sorted(r for r, v in (doc.get("decisions") or {}).items() if isinstance(v, dict) and schema_of(v) > SCHEMA)
    return f"rows {', '.join(bad[:8])} are schema > {SCHEMA}; this build cannot read them" if bad else None


def slot_picks(v: dict) -> dict:
    """{lane: letter} he picked per lane: schema-2 `slots` win; schema-1 `picks` fill the lanes slots do not name."""
    out = {g: L for g, L in (v.get("picks") or {}).items() if L}
    for g, s in (v.get("slots") or {}).items():
        if not isinstance(s, dict):
            continue
        if s.get("state") == "pick" and s.get("pick"):
            out[g] = s["pick"]
        elif g in out and s.get("state") in ("accept", "redraw", "not_drawn"):
            out.pop(g)
    return out


def slot_states(v: dict) -> dict:
    return {g: s.get("state") for g, s in (v.get("slots") or {}).items() if isinstance(s, dict) and s.get("state") in STATES}


def lists(v: dict, key: str) -> dict:
    return {g: [x for x in ls if x] for g, ls in (v.get(key) or {}).items() if isinstance(ls, list)}


def owner_pool_adds(v: dict, confirmed: set | None = None) -> list[str]:
    """Letters HE put in a random pool. Schema 1: explicit `variants` (never a `variantsDefault` list). Schema 2:
    `pool[*].add` plus each legacy tick he kept (legacy_answers)."""
    if schema_of(v) < 2:
        return [] if v.get("variantsDefault") else [x for x in (v.get("variants") or []) if x]
    out = [x for p in (v.get("pool") or {}).values() if isinstance(p, dict) for x in (p.get("add") or [])]
    out += [x for x in (v.get("legacyVariants") or []) if confirmed and x in confirmed]
    out += [x for x in (v.get("variants") or []) if x and not v.get("variantsDefault")]   # an old page saved after migration
    return list(dict.fromkeys(out))


def owner_pool_removes(v: dict) -> dict:
    return {g: list(p.get("remove") or []) for g, p in (v.get("pool") or {}).items() if isinstance(p, dict) and p.get("remove")}


def protect_letters(v: dict, confirmed: set | None = None, dropped: set | None = None) -> list[str]:
    """Letters whose pictures are protected from deletion: his pool adds, and legacy ticks not yet ruled (unknown is
    never treated as 'delete'). A machine-default tick protects nothing."""
    out = owner_pool_adds(v, confirmed)
    out += [x for x in (v.get("legacyVariants") or []) if not (dropped and x in dropped)]
    return list(dict.fromkeys(out))


def letters(v: dict) -> set:
    """Every column letter a record names (letter stability: kept columns, mismatch checks)."""
    if not isinstance(v, dict):
        return set()
    out = {(v.get("decision") or "").strip()} | set((v.get("picks") or {}).values()) | set(v.get("variants") or [])
    out |= set(v.get("legacyVariants") or [])
    for s in (v.get("slots") or {}).values():
        if isinstance(s, dict) and s.get("pick"):
            out.add(s["pick"])
    for p in (v.get("pool") or {}).values():
        if isinstance(p, dict):
            out |= set(p.get("add") or []) | set(p.get("remove") or [])
    for key in ("reject", "retire"):
        for ls in (v.get(key) or {}).values():
            out |= set(ls or [])
    out |= set((v.get("assign") or {}).keys())
    for m in ((v.get("asks") or {}).get("more") or []):
        if isinstance(m, dict) and m.get("base"):
            out.add(m["base"])
    return {x for x in out if isinstance(x, str) and len(x) == 1 and x.isalpha()}


def decision_is_his(v) -> bool:
    """The row's `decision` letter is the owner's (see the module docstring), never the agent's seeded prefill."""
    if not isinstance(v, dict):
        return False
    d = (v.get("decision") or "").strip()
    if not d:
        return False
    if v.get("decidedAt") or v.get("carriedRuledAt"):
        return True
    if "prefill" not in v:          # never seeded by a prefilling page: a saved (`at`) letter is his (pre-2026-10-04 files)
        return bool(v.get("at"))
    pf = v.get("prefill")
    return pf not in (None, "") and d != pf


def owner_view(v):
    """A record as the owner left it: a seeded prefill `decision` he never clicked is blanked (a copy; the original is
    untouched). Every consumer that acts on `decision` reads through this."""
    if not isinstance(v, dict) or decision_is_his(v) or not (v.get("decision") or "").strip():
        return v
    return {**v, "decision": "", "prefillOnly": (v.get("decision") or "").strip()}


def returned(doc: dict) -> dict | None:
    """The owner's return of the whole sheet ({at, said, by}), or None. Only `mark_returned` writes it."""
    r = (doc or {}).get("returned")
    return r if isinstance(r, dict) and r.get("at") and r.get("said") else None


def mark_returned(path: Path, said: str, apply: bool = False, at: str | None = None) -> dict:
    """Stamp his return of the sheet: every slot he left alone keeps its in-game art. `said` must be his words."""
    said = (said or "").strip()
    if len(said) < 8:
        return {"ok": False, "error": "--returned needs his words (the sentence where he said the sheet is done)"}
    doc = json.loads(path.read_text())
    if not (doc.get("savedBy") and int(doc.get("writeCount") or 0) > 0):
        return {"ok": False, "error": f"{path.name}: the sidecar never wrote this file — nothing of his landed; refusing to "
                                      f"stamp a return over the generator's prefill"}
    at = at or time.strftime("%Y-%m-%dT%H:%M:%S%z")
    doc["returned"] = {"at": at, "said": said, "by": "owner"}
    rs = doc.get("reviewStatus") if isinstance(doc.get("reviewStatus"), dict) else {}
    doc["reviewStatus"] = {**rs, "state": "ruled", "by": "owner", "at": at,
                           "evidence": "sheet returned (decisions_v2 --returned, his words in `returned.said`); slots he "
                                       "left alone keep their in-game art"}
    if apply:
        path.write_text(json.dumps(doc, indent=2) + "\n")
    return {"ok": True, "file": str(path), "returned": doc["returned"], "applied": apply}


def accept_looks(path: Path, said: str, prefer: dict | None = None, apply: bool = False, at: str | None = None,
                 snapshot: dict | None = None) -> dict:
    """His "take every look" answer on a subject sheet: in EVERY lane of every row that holds a render, pick that render
    (one pick per lane, so all looks of one def are accepted together). Owner, 2026-10-21, LINE_JOINS sheet: *"Just accept
    the art and go on. You had it so that I had to choose between "use this" for each art style... when actually all four
    art styles could be chosen together."* A lane holding several renders needs PREFER {row: letter} naming one of them,
    else the row is reported and left unchanged. His `assign` of a render to a lane it was NOT filed for (the old sheet
    offered one lane only) is dropped and kept under `assignSuperseded`. `said` must be his words."""
    said = (said or "").strip()
    if len(said) < 8:
        return {"ok": False, "error": "--accept-looks needs his words (the sentence where he accepted the art)"}
    doc = json.loads(path.read_text())
    if snapshot is None:
        import artledger as L
        snapshot = json.loads((L.REPO_ROOT / doc["snapshot"]).read_text())
    if doc.get("snapshotId") and snapshot.get("snapshotId") and doc["snapshotId"] != snapshot["snapshotId"]:
        return {"ok": False, "error": f"decisions are against snapshot {doc['snapshotId']}, the sheet is "
                                      f"{snapshot['snapshotId']}: run remap_decisions.py first"}
    at = at or time.strftime("%Y-%m-%dT%H:%M:%S%z")
    prefer = prefer or {}
    picked, unresolved = {}, {}
    decs = doc.setdefault("decisions", {})
    for row, srow in sorted((snapshot.get("rows") or {}).items()):
        gof, labels, cols = srow.get("graphic_of") or {}, srow.get("labels") or {}, srow.get("columns") or {}
        lanes: dict = {}
        for letter, g in sorted(gof.items()):
            if g and not g.startswith("_") and str(labels.get(letter, "")).startswith("render") and letter in cols:
                lanes.setdefault(g, []).append(letter)
        if not lanes:
            continue
        choice = {}
        for g, ls in sorted(lanes.items()):
            want = [x for x in prefer.get(row, []) if x in ls]
            if len(ls) == 1 or len(want) == 1:
                choice[g] = want[0] if want else ls[0]
            else:
                unresolved.setdefault(row, {})[g] = ls
        if row in unresolved:
            continue
        v = dict(decs.get(row) or {})
        stale = {k: x for k, x in (v.get("assign") or {}).items() if gof.get(k) not in (None, "_byname") and gof.get(k) != x}
        if stale:
            v["assignSuperseded"] = {**(v.get("assignSuperseded") or {}), **stale}
            v["assign"] = {k: x for k, x in (v.get("assign") or {}).items() if k not in stale}
        slots = dict(v.get("slots") or {})
        for g, letter in choice.items():
            slots[g] = {"state": "pick", "pick": letter, "set_id": SL.set_id(cols[letter]), "slot_id": f"{row}/look:{g}",
                        "at": at}
        prim = srow.get("res")
        v.update({"schema": 2, "rev": snapshot.get("snapshotId"), "slots": slots, "at": at, "decidedAt": at,
                  "decision": choice.get(prim) or choice[sorted(choice)[0]],
                  "acceptedLooks": {"at": at, "said": said, "by": "owner", "via": "decisions_v2 --accept-looks"}})
        decs[row] = v
        picked[row] = choice
    if apply and picked:
        doc["savedAt"], doc["savedBy"] = at, "decisions_v2 --accept-looks (owner's words)"
        path.write_text(json.dumps(doc, indent=2) + "\n")
    return {"ok": not unresolved, "picked": picked, "unresolved": unresolved, "applied": apply and bool(picked)}


def asks_of(v: dict) -> dict:
    a = v.get("asks") if isinstance(v.get("asks"), dict) else {}
    return {k: x for k, x in a.items() if x not in (None, "", [], {}, False)}


# ───────────────────────────────────────────────────────────── confirmations ──

def confirm_path() -> Path:
    """The retired standalone old-ticks sheet's decisions file (2026-10-10, replaced by the in-row control the same day).
    Still read so an answer given there is never lost or asked again; fold_old_sheet_answers copies them into the rows."""
    import os
    import artledger as L
    if os.environ.get("ART_OLD_TICKS_CONFIRM"):          # selftests point it at a fixture
        return Path(os.environ["ART_OLD_TICKS_CONFIRM"])
    return L.REPO_ROOT / "Transient" / CONFIRM_SHEET / f"{CONFIRM_SHEET}.decisions.json"


def biome_dir() -> Path:
    import os
    import artledger as L
    if os.environ.get("ART_BIOME_SHEETS_DIR"):           # selftests point it at a fixture
        return Path(os.environ["ART_BIOME_SHEETS_DIR"])
    return L.REPO_ROOT / "Transient" / "biome_ffar"


def confirm_key(sheet: str, row: str, letter: str) -> str:
    return f"{sheet}|{row}|{letter}"


def row_answers(v: dict) -> dict:
    """{letter: "confirm"|"drop"} he clicked in the biome sheet row (legacyRuled), legacy letters only."""
    if not isinstance(v, dict):
        return {}
    lv = set(v.get("legacyVariants") or [])
    return {L: a["v"] for L, a in (v.get("legacyRuled") or {}).items()
            if L in lv and isinstance(a, dict) and a.get("v") in ("confirm", "drop")}


def legacy_answers(v: dict, conf: dict | None = None) -> tuple[set, set]:
    """(kept, dropped) legacy letters of record V: his click in the row wins; CONF (one confirmations() entry, e.g. an
    answer from the retired old-ticks sheet) fills letters the row has not answered."""
    ans = {L: d for d in ("confirm", "drop") for L in ((conf or {}).get(d) or set())}
    ans.update(row_answers(v))
    return {L for L, d in ans.items() if d == "confirm"}, {L for L, d in ans.items() if d == "drop"}


def _old_sheet_answers(p: Path) -> dict:
    out: dict = {}
    if not p.is_file():
        return out
    try:
        doc = json.loads(p.read_text())
    except (OSError, ValueError):
        return out
    for k, v in (doc.get("decisions") or {}).items():
        if not isinstance(v, dict) or not v.get("decidedAt"):
            continue
        d = (v.get("decision") or "").strip()
        parts = k.split("|")
        if len(parts) != 3 or d not in ("confirm", "drop"):
            continue
        out[(parts[0], parts[1], parts[2])] = d
    return out


def confirmations(path: Path | None = None, biomes: Path | None = None) -> dict:
    """{(sheet, row): {"confirm": {L}, "drop": {L}}} — his clicks only: every biome decisions file's in-row answers
    (legacyRuled), with the retired old-ticks sheet's answers filling letters a row has not answered."""
    ans = _old_sheet_answers(Path(path) if path else confirm_path())
    bd = Path(biomes) if biomes else biome_dir()
    for f in sorted(bd.glob("*.decisions.json")) if bd.is_dir() else []:
        try:
            doc = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        sid = doc.get("sheetId") or f.name.replace(".decisions.json", "")
        for row, v in (doc.get("decisions") or {}).items():
            for L, d in row_answers(v).items():
                ans[(sid, row, L)] = d
    out: dict = {}
    for (sid, row, L), d in ans.items():
        out.setdefault((sid, row), {"confirm": set(), "drop": set()})[d].add(L)
    return out


def fold_old_sheet_answers(apply: bool = False, path: Path | None = None, biomes: Path | None = None) -> dict:
    """Copy every answer he gave on the retired old-ticks sheet into its biome row's legacyRuled (never over an answer
    the row already has). Atomic per file, re-read before replace so a sheet save in between is never lost."""
    import os
    import tempfile
    old = _old_sheet_answers(Path(path) if path else confirm_path())
    bd = Path(biomes) if biomes else biome_dir()
    res = {"answers_on_old_sheet": len(old), "folded": 0, "already": 0, "no_row": [], "files": []}
    by_sheet: dict = {}
    for (sid, row, L), d in old.items():
        by_sheet.setdefault(sid, []).append((row, L, d))
    for sid, items in sorted(by_sheet.items()):
        f = bd / f"{sid}.decisions.json"
        if not f.is_file():
            res["no_row"] += [f"{sid}|{r}|{L}" for r, L, _ in items]
            continue
        for _attempt in range(4):
            raw = f.read_bytes()
            doc = json.loads(raw.decode("utf-8"))
            n = 0
            for row, L, d in items:
                v = (doc.get("decisions") or {}).get(row)
                if not isinstance(v, dict) or L not in (v.get("legacyVariants") or []):
                    res["no_row"].append(f"{sid}|{row}|{L}")
                    continue
                if L in row_answers(v):
                    res["already"] += 1
                    continue
                v.setdefault("legacyRuled", {})[L] = {"v": d, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                                                     "from": CONFIRM_SHEET}
                n += 1
            if not n or not apply:
                break
            fd, tmp = tempfile.mkstemp(dir=str(f.parent), prefix=".fold-", suffix=".tmp")
            try:
                with os.fdopen(fd, "wb") as fh:
                    fh.write((json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
                if f.read_bytes() != raw:
                    continue
                os.replace(tmp, f)
                break
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
        res["folded"] += n
        if n:
            res["files"].append(f.name)
    return res


# ───────────────────────────────────────────────────────────── migration ──

def _gof(row: dict) -> dict:
    gof = dict(row.get("graphic_of") or {})
    graphics = sorted({g for g in gof.values() if g != "_byname" and not g.startswith("_reference")}) or (
        [row["res"]] if row.get("res") else [])
    for l in (row.get("columns") or {}):
        gof.setdefault(l, graphics[0] if len(graphics) == 1 else "_byname")
    return gof


def resolve_cols(row: str, versions: list[dict], click_order: int | None = None) -> tuple[dict, dict]:
    """({letter: faces}, {letter: [differing faces]}) for ROW over every snapshot version of the sheet. Letters are
    append-only (a set keeps its letter for good), so a letter resolves when every version that carries it names the
    SAME pictures; a letter two versions disagree on is ambiguous and is quarantined, never guessed."""
    seen: dict = {}
    for snap in versions:
        r = ((snap.get("rows") or {}).get(row) or {})
        for l, f in (r.get("columns") or {}).items():
            seen.setdefault(l, [])
            if f not in seen[l]:
                seen[l].append(f)
    ok, amb = {}, {}
    for l, fs in seen.items():
        big = max(fs, key=len)
        # a facing purged later drops out of a set's faces: a set that only LOST pictures is still the same set
        if all(all(big.get(k) == x for k, x in f.items()) for f in fs):
            ok[l] = big
        else:
            amb[l] = fs
    return ok, amb


def migrate_record(v: dict, ruled_row: dict | None, rev: str | None, cols_override: dict | None = None) -> tuple[dict, dict]:
    """(schema-2 record, report) for one schema-1 record, resolved against RULED_ROW (the snapshot row he saw) —
    COLS_OVERRIDE, when given, is the letter -> pictures map resolved over every version of that snapshot."""
    if not isinstance(v, dict) or schema_of(v) >= 2:
        return v, {}
    rr = dict(ruled_row or {})
    if cols_override is not None:
        rr["columns"] = cols_override
    cols = rr.get("columns") or {}
    gof = _gof(rr)
    graphics = sorted({g for g in gof.values() if g != "_byname" and not g.startswith("_reference")})
    n = dict(v)
    rep = {"legacy": [], "machine_default": [], "quarantine": [], "byname_pick_unassigned": []}
    n["schema"] = SCHEMA
    n["migratedFrom"] = 1
    if rev:
        n.setdefault("rev", rev)
    named = letters(v)
    set_ids, quarantine = {}, []
    for l in sorted(named):
        if l in cols:
            set_ids[l] = SL.set_id(cols[l])
        else:
            quarantine.append(l)
    if set_ids:
        n["setIds"] = set_ids
    if quarantine:
        n["quarantine"] = quarantine
        rep["quarantine"] = quarantine
    slots = {}
    dec = (v.get("decision") or "").strip()
    decided = bool(v.get("decidedAt")) or not v.get("purgeTouched")
    if v.get("at") and decided:
        prim = rr.get("res") or (graphics[0] if graphics else None)
        if dec in cols and str(gof.get(dec)).startswith("_reference"):
            rep["byname_pick_unassigned"].append(dec)
        elif dec in cols and gof.get(dec) != "_byname":
            slots[gof[dec]] = {"state": "pick", "pick": dec, "set_id": set_ids.get(dec), "migrated": True}
        elif dec in cols and len(graphics) == 1:
            slots[graphics[0]] = {"state": "pick", "pick": dec, "set_id": set_ids.get(dec), "migrated": True}
            n.setdefault("assign", {})[dec] = graphics[0]
        elif dec in cols:
            rep["byname_pick_unassigned"].append(dec)
        elif dec == "redo" and prim:
            slots[prim] = {"state": "redraw", "migrated": True}
        for g, l in (v.get("picks") or {}).items():
            if not l or l not in cols:
                continue
            if g == "_byname":
                if len(graphics) == 1:
                    slots.setdefault(graphics[0], {"state": "pick", "pick": l, "set_id": set_ids.get(l), "migrated": True})
                    n.setdefault("assign", {})[l] = graphics[0]
                else:
                    rep["byname_pick_unassigned"].append(l)
                continue
            slots[g] = {"state": "pick", "pick": l, "set_id": set_ids.get(l), "migrated": True}
    if slots:
        n["slots"] = slots
    vs = [x for x in (v.get("variants") or []) if x]
    if v.get("variantsDefault"):
        n["legacyVariantsDefault"] = vs
        rep["machine_default"] = vs
    elif vs:
        n["legacyVariants"] = vs
        rep["legacy"] = vs
    n.pop("variants", None)
    n.pop("variantsDefault", None)
    return n, {k: x for k, x in rep.items() if x}


def migrate_doc(doc: dict, ruled_snap: dict | None, versions: list[dict] | None = None) -> tuple[dict, dict]:
    """(schema-2 doc, {row: report}) — every schema-1 record migrated against RULED_SNAP (the snapshot he saved
    against); VERSIONS (every version of that sheet's snapshot) resolve letters a superset rebuild added under the
    same snapshotId after the first version was written."""
    out = json.loads(json.dumps(doc))
    reports = {}
    rows = (ruled_snap or {}).get("rows") or {}
    rev = doc.get("snapshotId")
    vers = [x for x in (versions or []) if x] or ([ruled_snap] if ruled_snap else [])
    for row, v in (doc.get("decisions") or {}).items():
        if not isinstance(v, dict) or schema_of(v) >= 2:
            continue
        key = row if any(row in (x.get("rows") or {}) for x in vers) else (v.get("carriedFrom") or row)
        cols, amb = resolve_cols(key, vers)
        nv, rep = migrate_record(v, rows.get(key) or {}, rev, cols)
        if amb and set(amb) & letters(v):
            nv.setdefault("quarantine", [])
            nv["quarantine"] = sorted(set(nv["quarantine"]) | (set(amb) & letters(v)))
            rep = dict(rep, quarantine=nv["quarantine"], ambiguous=sorted(set(amb) & letters(v)))
        out["decisions"][row] = nv
        if rep:
            reports[row] = rep
    out["schema"] = SCHEMA
    out.setdefault("migrations", []).append({"from": 1, "to": SCHEMA, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                                             "by": "script:src/RimMandrake/Utils/art/decisions_v2.py",
                                             "against_snapshot": (ruled_snap or {}).get("snapshotId")})
    return out, reports


def ruled_snapshot(doc: dict, decisions_path: Path) -> dict | None:
    import artledger as L
    sp = Path(doc.get("snapshot") or "")
    if not sp.is_absolute():
        sp = L.REPO_ROOT / sp
    return L.snapshot_by_id(sp, doc.get("snapshotId")) if doc.get("snapshotId") else (
        json.loads(sp.read_text()) if sp.is_file() else None)


def snapshot_versions(doc: dict) -> list[dict]:
    """The versions (disk + git history) of the sheet snapshot this decisions file was SAVED against — every build that
    kept its snapshotId (a rebuild that only adds sets keeps the id) — then the snapshot on disk now, which is what
    enact resolves letters against today. Builds under an older id are not used: before his first save a rebuild
    re-letters every row."""
    import artledger as L
    sp = Path(doc.get("snapshot") or "")
    if not sp.is_absolute():
        sp = L.REPO_ROOT / sp
    allv = [d for _t, d in L.snapshot_versions(sp)]
    same = [d for d in allv if d.get("snapshotId") == doc.get("snapshotId")]
    now = json.loads(sp.read_text()) if sp.is_file() else None
    return same + ([now] if now and now not in same else [])


def migrate_file(path: Path, apply: bool = False) -> dict:
    """Migrate one decisions file in place (atomic, re-read before replace so a save of his in between is never lost)."""
    import os
    import tempfile
    path = Path(path)
    for _attempt in range(4):
        raw = path.read_bytes()
        doc = json.loads(raw.decode("utf-8"))
        if schema_of(doc) >= 2 and not any(isinstance(v, dict) and schema_of(v) < 2 for v in (doc.get("decisions") or {}).values()):
            return {"file": path.name, "migrated": 0, "already": True, "reports": {}}
        ruled = ruled_snapshot(doc, path)
        new, reports = migrate_doc(doc, ruled, snapshot_versions(doc))
        res = {"file": path.name, "migrated": sum(1 for v in (doc.get("decisions") or {}).values()
                                                  if isinstance(v, dict) and schema_of(v) < 2),
               "ruled_snapshot": (ruled or {}).get("snapshotId"), "reports": reports}
        if not apply:
            return res
        payload = (json.dumps(new, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".migrate-", suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(payload)
                fh.flush()
                os.fsync(fh.fileno())
            if path.read_bytes() != raw:
                continue
            os.replace(tmp, path)
            return res
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    return {"file": path.name, "error": "lost 4 races with the sheet's sidecar; not migrated"}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="migrate biome art decisions files to schema 2 (dry run unless --apply); "
                                             "--fold-old-ticks copies the retired old-ticks sheet's answers into the rows")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--fold-old-ticks", action="store_true")
    ap.add_argument("--returned", metavar="HIS_WORDS",
                    help="stamp the owner's return of each file's sheet (his words); unchanged slots keep their in-game art")
    ap.add_argument("--accept-looks", metavar="HIS_WORDS",
                    help="pick the render in EVERY look lane of every row (all looks together); his words")
    ap.add_argument("--prefer", nargs="*", default=[], metavar="ROW=LETTER",
                    help="with --accept-looks: the render to take in a lane that holds several")
    a = ap.parse_args(argv)
    if a.accept_looks:
        pref: dict = {}
        for x in a.prefer:
            r_, _, l_ = x.partition("=")
            pref.setdefault(r_, []).append(l_)
        rc = 0
        for f in a.files:
            r = accept_looks(Path(f), a.accept_looks, pref, apply=a.apply)
            print(json.dumps(r, indent=1))
            rc |= 0 if r["ok"] else 1
        return rc
    if a.returned:
        rc = 0
        for f in a.files:
            r = mark_returned(Path(f), a.returned, apply=a.apply)
            print(json.dumps(r))
            rc |= 0 if r["ok"] else 1
        return rc
    if a.fold_old_ticks:
        print(json.dumps(fold_old_sheet_answers(apply=a.apply), indent=1))
        return 0
    for f in a.files:
        r = migrate_file(Path(f), apply=a.apply)
        rep = r.get("reports") or {}
        print(f"{r['file']}: {'already schema 2' if r.get('already') else r.get('error') or str(r['migrated']) + ' record(s)'}"
              f" · legacy ticks on {sum(1 for x in rep.values() if x.get('legacy'))} row(s)"
              f" · quarantined letters on {sum(1 for x in rep.values() if x.get('quarantine'))} row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

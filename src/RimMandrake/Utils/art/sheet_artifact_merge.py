#!/usr/bin/env python3
"""sheet_artifact_merge.py — fold the owner's picks from a claude.ai Artifact (built by sheet_to_artifact.py) into the
sheet's decisions.json, exactly as the sheet's own sidecar would have written them had he clicked on the tailnet page.

    python3 src/RimMandrake/Utils/art/sheet_artifact_merge.py <picks.json|dir> <x>.decisions.json [--sheet <x>.html]
                                                             [--apply] [--allow-stale]

<picks.json> is whatever the parent got back from the artifact's `picks` collection (an ArtifactData read, a dump
directory of one JSON per document, or the page's own "copy my picks" text): every object carrying a `rowId` is one
row's document (layout: sheet_to_artifact.py's docstring). Dry run by default; --apply writes.

WHAT IT WRITES, per row, mirroring art_sheet.py's SLX.setSlot / setDecision:
  - slots[<lane key>] = {state: pick|redraw, pick?, set_id?, slot_id, at}; a cleared lane is removed;
  - the primary slot drives `decision` (letter / "redo" / ""), and "hold" is decision "hold" with no primary slot;
    `decidedAt` is stamped only when the PRIMARY choice moved — a note-only or second-slot-only row never turns the
    agent's prefill into his decision (decisions_v2.decision_is_his);
  - a second slot keeps the legacy `picks` map in step when the record has one; a picked set loses its reject/retire
    marks and its purge entries, as on the sheet;
  - note, `remoteDone` (his "done" tick), schema 2, the sheet rev, and `via` = {route: "claude-artifact-db",
    by: "owner", ts} — the record is HIS input that came by the remote route, never an agent guess.
The file-level stamp is savedBy "artifact-db-merge" (what apply_blanket_ruling and decisions_v2.mark_returned accept),
written through the review-sheets sidecar's own DecisionsFile (per-row merge, cross-process lock, frozen/corrupt/
truncation refusals) and serve_gated.guard_ops (a note enact already followed is not re-opened).

REFUSES (exit 2, nothing written): an empty input, two documents for one row, a row the sheet does not have, a document
from another sheet, a letter that is not a usable set of that slot, a lane that is not a slot, and a document made on
an older build of the row (`rev` differs: the letters may name other pictures — run remap_decisions.py, or pass
--allow-stale after checking). A frozen decisions file exits 5. Re-running on the same input changes nothing.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ROUTE = "claude-artifact-db"
STAMP = "artifact-db-merge"
PICK_STATES = {"pick", "redraw", ""}


class Refused(Exception):
    pass


def find_docs(obj, out: list) -> list:
    """Every dict carrying a string rowId, wherever the dump nests it (ArtifactData wraps documents in data/docs)."""
    if isinstance(obj, dict):
        if isinstance(obj.get("rowId"), str):
            out.append(obj)
            return out
        for v in obj.values():
            find_docs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            find_docs(v, out)
    return out


def load_input(p: Path) -> list[dict]:
    files = sorted(p.glob("*.json")) if p.is_dir() else [p]
    docs: list = []
    for f in files:
        try:
            find_docs(json.loads(f.read_text(encoding="utf-8")), docs)
        except json.JSONDecodeError as exc:
            raise Refused(f"{f} is not JSON ({exc})")
    if not docs:
        raise Refused(f"{p}: no picks found (no object with a rowId) — an empty read is not 'he picked nothing'")
    seen: dict = {}
    for d in docs:
        if d["rowId"] in seen and seen[d["rowId"]] != d:
            raise Refused(f"two different documents for row {d['rowId']} — refusing to guess which he meant")
        seen[d["rowId"]] = d
    return list(seen.values())


def sheet_items(sheet: Path) -> tuple[dict, dict]:
    import scaled_review_gate as SG
    html = sheet.read_text(encoding="utf-8")
    items = SG._json_block(html, "ITEMS")
    if not isinstance(items, list):
        raise Refused(f"{sheet} has no readable ITEMS block")
    return (SG._json_block(html, "CONFIG") or {}), {it["id"]: it for it in items if isinstance(it, dict) and it.get("id")}


def _v2(rec: dict) -> dict:
    """SLX.v2: schema 2, legacy variants parked, slots present."""
    if int(rec.get("schema") or 1) < 2:
        rec["schema"] = 2
        if isinstance(rec.get("variants"), list) and rec["variants"]:
            rec["legacyVariantsDefault" if rec.get("variantsDefault") else "legacyVariants"] = rec["variants"]
        rec.pop("variants", None)
        rec.pop("variantsDefault", None)
    rec.setdefault("slots", {})
    return rec


def validate(body: dict, sheet_id: str, it: dict | None, allow_stale: bool) -> None:
    rid = body["rowId"]
    if it is None:
        raise Refused(f"row {rid}: the sheet has no such row")
    if body.get("sheetId") and sheet_id and body["sheetId"] != sheet_id:
        raise Refused(f"row {rid}: document is from sheet {body['sheetId']}, not {sheet_id}")
    if body.get("rev") != it.get("rev") and not allow_stale:
        raise Refused(f"row {rid}: picked on rev {body.get('rev')}, the sheet row is now rev {it.get('rev')} — the "
                      f"letters may name other pictures (remap_decisions.py, or --allow-stale after checking)")
    lanes = {g.get("key"): g for g in it.get("graphics") or []}
    for key, st in (body.get("slots") or {}).items():
        g = lanes.get(key)
        if g is None or (g.get("lane") or "slot") != "slot":
            raise Refused(f"row {rid}: {key!r} is not a pickable slot of this row")
        state = (st or {}).get("state") or ""
        if state not in PICK_STATES:
            raise Refused(f"row {rid}: slot state {state!r} is not one of pick/redraw/(cleared)")
        if state == "pick":
            c = next((c for c in g.get("cols") or [] if c.get("letter") == st.get("pick")), None)
            if c is None or c.get("noSelect") or c.get("purgedLive"):
                raise Refused(f"row {rid}: {st.get('pick')!r} is not a usable set of slot {key}")
    pick = body.get("pick") or ""
    if pick not in ("", "hold", "redo") and not (len(pick) == 1 and pick.isalpha()):
        raise Refused(f"row {rid}: primary pick {pick!r} is not a letter, redo, hold or empty")


def merge_row(rec_in: dict | None, body: dict, it: dict) -> dict:
    """The record the sheet's sidecar would hold after his clicks. Pure: rec_in is not modified."""
    rec = _v2(copy.deepcopy(rec_in) if isinstance(rec_in, dict) else {"decision": "", "note": ""})
    ts = body.get("ts") or body.get("pickedAt")
    at = body.get("pickedAt") or ts
    lanes = {g.get("key"): g for g in it.get("graphics") or []}
    prim = next((g for g in it.get("graphics") or [] if g.get("primary") and (g.get("lane") or "slot") == "slot"), None)
    prim_moved = False
    if body.get("pickedAt"):                       # only a pick/redraw/hold action touches choices
        for key, st in (body.get("slots") or {}).items():
            g = lanes[key]
            state = (st or {}).get("state") or ""
            old = rec["slots"].get(key)
            if state == "pick":
                c = next(c for c in g.get("cols") or [] if c.get("letter") == st["pick"])
                new = {"state": "pick", "pick": st["pick"], "set_id": c.get("setId"),
                       "slot_id": (g.get("slot") or {}).get("id"), "at": at}
                for k in ("reject", "retire"):     # pick and x of one set cannot both stand
                    lst = (rec.get(k) or {}).get(key)
                    if isinstance(lst, list) and st["pick"] in lst:
                        lst = [x for x in lst if x != st["pick"]]
                        if lst:
                            rec[k][key] = lst
                        else:
                            del rec[k][key]
                shas = set((c.get("faces") or {}).values())
                if isinstance(rec.get("purge"), list) and shas & set(rec["purge"]):
                    rec["purge"] = [x for x in rec["purge"] if x not in shas]
            elif state == "redraw":
                new = {"state": "redraw", "slot_id": (g.get("slot") or {}).get("id"), "at": at}
            else:
                new = None
            same = (old is None and new is None) or (old and new and old.get("state") == new["state"]
                                                      and old.get("pick") == new.get("pick") and not old.get("migrated"))
            if not same:
                if new is None:
                    rec["slots"].pop(key, None)
                else:
                    rec["slots"][key] = new
            if g is prim:
                d = "" if new is None else new["pick"] if new["state"] == "pick" else "redo"
                if d != (rec.get("decision") or "") or not same:
                    rec["decision"], prim_moved = d, True
            elif isinstance(rec.get("picks"), dict) and key in rec["picks"]:
                if new and new["state"] == "pick":
                    rec["picks"][key] = new["pick"]
                else:
                    del rec["picks"][key]
        pick = body.get("pick") or ""
        if pick == "hold" and rec.get("decision") != "hold":
            rec["decision"], prim_moved = "hold", True
            if prim is not None:
                rec["slots"].pop(prim.get("key"), None)
        elif pick != "hold" and rec.get("decision") == "hold" and not prim_moved:
            rec["decision"], prim_moved = "", True        # he took the hold back without picking
        if prim_moved:
            rec["decidedAt"] = at
            rec["at"] = at
    if (body.get("note") or "") != (rec.get("note") or ""):
        rec["note"] = body.get("note") or ""
    if bool(body.get("done")) != bool(rec.get("remoteDone")):
        rec["remoteDone"] = bool(body.get("done"))
    if it.get("rev"):
        rec["rev"] = it["rev"]
    return rec


HIS_KEYS = ("decision", "decidedAt", "slots", "picks", "reject", "retire", "purge", "note", "remoteDone")


def _his(r: dict | None) -> dict:
    """The parts of a record his clicks can change; equal before and after = nothing to write."""
    r = r or {}
    return {k: r.get(k) or None for k in HIS_KEYS}


def plan(docs: list[dict], decisions: dict, sheet_id: str, items: dict, allow_stale: bool) -> dict:
    ops = {}
    for body in sorted(docs, key=lambda d: d["rowId"]):
        it = items.get(body["rowId"])
        validate(body, sheet_id, it, allow_stale)
        old = decisions.get(body["rowId"])
        followed = {str(f.get("note") or "").strip() for f in (old or {}).get("notes_followed") or [] if isinstance(f, dict)}
        if str(body.get("note") or "").strip() in followed - {""}:
            body = dict(body, note="")             # enact already followed this note: never re-open it (guard_ops)
        new = merge_row(old, body, it)
        if _his(new) == _his(old):
            continue                                       # nothing he did differs from the file: a re-run is a no-op
        new["via"] = {"route": ROUTE, "by": "owner", "ts": body.get("ts"), "doc": body.get("rowId")}
        ops[body["rowId"]] = new
    return ops


def _sidecar():
    import serve_gated
    spec = importlib.util.spec_from_file_location("review_sheets_sidecar", str(serve_gated.SERVE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.STAMP_BY = STAMP                       # the file-level stamp names this route, not the sheet's sidecar
    return mod, serve_gated.guard_ops


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("picks", help="the artifact's picks: a JSON file or a directory of them")
    ap.add_argument("decisions", help="the sheet's .decisions.json")
    ap.add_argument("--sheet", help="the sheet .html (default: beside the decisions file)")
    ap.add_argument("--apply", action="store_true", help="write (default: dry run)")
    ap.add_argument("--allow-stale", action="store_true", help="accept documents made on an older row rev")
    a = ap.parse_args(argv)
    dpath = Path(a.decisions)
    sheet = Path(a.sheet) if a.sheet else dpath.with_name(dpath.name.replace(".decisions.json", ".html"))
    try:
        if not dpath.is_file():
            raise Refused(f"{dpath} does not exist")
        if not sheet.is_file():
            raise Refused(f"no sheet at {sheet} (pass --sheet): picks are checked against the sheet's rows")
        doc = json.loads(dpath.read_text(encoding="utf-8"))
        if doc.get("frozen") is True:
            print(f"REFUSED: {dpath.name} is frozen ({doc.get('frozenOn')}): {doc.get('frozenMeaning') or ''}",
                  file=sys.stderr)
            return 5
        cfg, items = sheet_items(sheet)
        docs = load_input(Path(a.picks))
        ops = plan(docs, doc.get("decisions") or {}, cfg.get("sheetId") or doc.get("sheetId") or "", items,
                   a.allow_stale)
    except Refused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    old = doc.get("decisions") or {}
    for rid, rec in ops.items():
        o = old.get(rid) or {}
        bits = []
        if (o.get("decision") or "") != (rec.get("decision") or ""):
            bits.append(f"decision {o.get('decision') or '-'} -> {rec.get('decision') or '-'}")
        if o.get("slots") != rec.get("slots"):
            bits.append("slots " + ", ".join(f"{k.rsplit('/', 1)[-1]}={v.get('state')}{':' + v['pick'] if v.get('pick') else ''}"
                                             for k, v in sorted(rec["slots"].items())))
        if (o.get("note") or "") != (rec.get("note") or ""):
            bits.append(f"note {rec.get('note')!r:.60}")
        if bool(o.get("remoteDone")) != bool(rec.get("remoteDone")):
            bits.append(f"done={rec.get('remoteDone')}")
        print(f"  {rid}: " + ("; ".join(bits) or "provenance only"))
    print(f"{len(docs)} document(s), {len(ops)} row(s) change, {len(docs) - len(ops)} unchanged")
    if not ops:
        return 0
    if not a.apply:
        print("dry run — pass --apply to write")
        return 0
    side, guard = _sidecar()
    df = side.DecisionsFile(str(dpath))
    try:
        res = df.write_ops(guard(ops, df.read().get("decisions") or {}))
    except side.Frozen:
        print(f"REFUSED: {dpath.name} was frozen meanwhile", file=sys.stderr)
        return 5
    except (side.Corrupt, side.Truncating) as exc:
        print(f"REFUSED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {res['applied']} row(s) to {dpath} (writeCount {res['writeCount']}, savedBy {STAMP}, "
          f"decided {res['decidedCount']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

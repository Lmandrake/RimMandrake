#!/usr/bin/env python3
"""apply_assignment_verdicts.py — the CONSUMER side of the fauna/flora assignment sheets.

The generators (gen_fauna_assignment_sheet.py / gen_flora_assignment_sheet.py) write the
sheet and its PRE-FILL. This reads the decisions file back and amends the roster JSONs
under design/Jawa/worldbuilding/biomes/rosters/ — but only for rows whose decision
DIFFERS from the landed prefill. Rows the owner left alone are never touched.

🔴 THE GUARD THAT MATTERS (review-sheets skill §8). A pre-fill and a reviewed file look
identical. Only the sidecar can stamp savedBy/writeCount/savedAt, so this tool REFUSES to
run without them: an agent's own guesses must never be applied as the owner's verdicts.

Normal path: owner reviews -> owner freezes (§7) -> this runs.

    python3 apply_assignment_verdicts.py                    # report only, both sheets
    python3 apply_assignment_verdicts.py --apply            # write the rosters
    python3 apply_assignment_verdicts.py fauna_assignment_register.decisions.json --apply
    python3 apply_assignment_verdicts.py --selftest         # synthetic end-to-end proof

ROW-ID SCHEME (emitted by the two generators; see the header block in each)
    f:<sheet>:<defName>    a fauna[] row              keep|adjust|move|evict|open
    e:<sheet>:<defName>    an evictions[] row         (flagged ones only)
    p:<sheet>:<defName>    a flora[] row              keep|thin|purge|defer|drop
    purge:<sheet>          the per-biome flora_purged[] SUMMARY row (one per biome)
    nd:<sheet>:<index>     new_defs[<index>] — the NEW-ART/DEF ledger
    c:<sheet>:<index>      confidence[<index>] — an unsettled claim
    h:<defName>            _global.json ruled.in_jokes_kept_reskinned — no home landed

⚠️ <sheet> is the roster's `sheet` FIELD, not its filename, and it is not a valid path
component: `the_grey_sea.json` carries sheet "terminator_sea + the_grey_deep" and
`dune_sea_deep_desert.json` carries "dune_sea + deep_desert". Resolve it by loading every
roster and indexing on the field. It also contains ':'-free spaces and '+', so parse a row
id as prefix / rsplit(':', 1) — never str.split(':').

Exit codes: 0 ok · 2 no sidecar stamp · 3 not frozen · 4 validator went red
            5 a verdict could not be resolved (nothing was written)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ROSTERS = os.path.join(ROOT, "design", "Jawa", "worldbuilding", "biomes", "rosters")
DEFAULT_DECISIONS = [
    os.path.join(HERE, "fauna_assignment_register.decisions.json"),
    os.path.join(HERE, "flora_assignment_register.decisions.json"),
]

SIDECAR_KEYS = ("savedBy", "writeCount", "savedAt")

RC_OK, RC_NO_SIDECAR, RC_NOT_FROZEN, RC_VALIDATOR, RC_UNRESOLVED = 0, 2, 3, 4, 5

# NEW-ART ledger verdict -> the status written onto the new_defs entry.
LEDGER_STATUS = {
    "keep": "commission",
    "thin": "commission (reduced scope — see owner_note)",
    "purge": "drop",
    "drop": "drop",
    "defer": "defer",
    "adjust": "commission (reduced scope — see owner_note)",
    "evict": "drop",
    "move": "defer",
    "open": "defer",
}
CLOSING = {"keep", "adjust", "thin", "move", "evict", "purge", "drop"}


class Refuse(Exception):
    """A guard refused. Nothing is written."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


# ─────────────────────────────────────────────────────────────────────────────
# loading
# ─────────────────────────────────────────────────────────────────────────────

def load_rosters(rosters_dir: str) -> tuple[dict, dict]:
    """-> ({sheet field: {path, doc}}, {'path':..., 'doc':...} for _global.json)."""
    by_sheet: dict[str, dict] = {}
    glob_entry: dict = {}
    for name in sorted(os.listdir(rosters_dir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(rosters_dir, name)
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        if name == "_global.json":
            glob_entry = {"path": path, "doc": doc, "dirty": False}
            continue
        sheet = doc.get("sheet")
        if not sheet:
            continue
        if sheet in by_sheet:
            raise Refuse(RC_UNRESOLVED,
                         f"two rosters both carry sheet {sheet!r}: "
                         f"{by_sheet[sheet]['path']} and {path}")
        by_sheet[sheet] = {"path": path, "doc": doc, "dirty": False}
    return by_sheet, glob_entry


def load_decisions(path: str, allow_unfrozen: bool) -> dict:
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    # ── schema guard ─────────────────────────────────────────────────────────
    # The sheets were rebuilt 2026-09-09 to the owner's rulings: new row ids
    # (fauna:/flora:/homeless:/ledger:/q:), new verdict keys (in/move/out/later)
    # and two extra per-row lanes (sizeBin, art). This applier predates that
    # schema and would map its verdicts wrongly — refuse rather than guess.
    ids = list((doc.get("decisions") or {}).keys())
    if any(i.split(":", 1)[0] in ("fauna", "flora", "homeless", "ledger", "q")
           for i in ids):
        raise Refuse(RC_NO_SIDECAR, (
            f"🔴 REFUSING {os.path.basename(path)}: this decisions file uses the "
            "2026-09-09 rulings schema (fauna:/flora:/homeless:/ledger: row ids, "
            "in/move/out/later verdicts, sizeBin and art lanes).\n"
            "   apply_assignment_verdicts.py has not been rewritten for it yet — "
            "applying with the old mapping would corrupt the rosters. Rewrite the "
            "applier against the new generators' header blocks first."))
    missing = [k for k in SIDECAR_KEYS if not doc.get(k)]
    if missing:
        raise Refuse(RC_NO_SIDECAR, (
            f"🔴 REFUSING {os.path.basename(path)}: sidecar keys absent ({', '.join(missing)}).\n"
            "   This file is still the generator's PRE-FILL — the agent's own guesses. Only\n"
            "   serve_sheet.py stamps savedBy/writeCount/savedAt, and a generator cannot forge\n"
            "   them, so their absence means no review has ever landed on disk (review-sheets\n"
            "   skill §8).\n"
            "   Recovery: the work is almost certainly still in the browser's localStorage —\n"
            "   reopen the sheet, click 'copy JSON', and save through the sidecar:\n"
            "     python3 ~/.claude/skills/review-sheets/assets/serve_sheet.py \\\n"
            f"       --sheet {os.path.basename(path).replace('.decisions.json', '.html')} \\\n"
            f"       --decisions {os.path.basename(path)}\n"
            "   Clearing browsing data destroys it; nothing else does."))
    if doc.get("frozen") is not True and not allow_unfrozen:
        raise Refuse(RC_NOT_FROZEN, (
            f"🔴 REFUSING {os.path.basename(path)}: \"frozen\" is not set.\n"
            "   The normal path is: the owner finishes, the file is frozen (review-sheets §7 —\n"
            "   `\"frozen\": true` plus frozenOn/frozenMeaning, after which the sidecar returns\n"
            "   423 and the sheet goes read-only), and only THEN is it consumed. Applying an\n"
            "   unfrozen file races the owner's next click.\n"
            "   Pass --allow-unfrozen to consume a mid-review file deliberately."))
    return doc


def overrides_of(doc: dict) -> list[dict]:
    """Rows whose decision differs from the landed prefill. Order preserved."""
    out = []
    for rid, row in (doc.get("decisions") or {}).items():
        if not isinstance(row, dict):
            continue
        decision, prefill = row.get("decision"), row.get("prefill")
        if decision is None or decision == prefill:
            continue
        out.append({"id": rid, "decision": decision, "prefill": prefill,
                    "note": (row.get("note") or "").strip()})
    return out


def parse_id(rid: str) -> tuple[str, str, str]:
    """-> (prefix, sheet, tail). `sheet` may contain spaces and '+'."""
    prefix, _, rest = rid.partition(":")
    if prefix == "h":
        return "h", "", rest
    if prefix == "purge":
        return "purge", rest, ""
    if ":" not in rest:
        return prefix, rest, ""
    sheet, _, tail = rest.rpartition(":")
    return prefix, sheet, tail


# ─────────────────────────────────────────────────────────────────────────────
# note mining — the owner's free text is the only place a target or a value lives
# ─────────────────────────────────────────────────────────────────────────────

MOVE_PATTERNS = (
    re.compile(r"move\s*:\s*([A-Za-z_][\w]*)", re.I),
    re.compile(r"(?:->|→|=>)\s*([A-Za-z_][\w]*)"),
    re.compile(r"\b(?:to|into|home(?:s)?\s+(?:in|to))\s+([A-Za-z_][\w]*)", re.I),
)
COMM_RE = re.compile(r"\bcomm(?:onality)?\s*[:= ]\s*([0-9]*\.?[0-9]+)", re.I)


def mined_target(note: str) -> str | None:
    for pat in MOVE_PATTERNS:
        m = pat.search(note or "")
        if m:
            return m.group(1)
    return None


def mined_commonality(note: str, default: float) -> float:
    m = COMM_RE.search(note or "")
    return float(m.group(1)) if m else default


def named_in_note(note: str, candidates: list[str], labels: dict[str, str]) -> list[str]:
    """Which of `candidates` (defNames) the owner named — by defName or by label."""
    text = (note or "")
    hit = []
    for dn in candidates:
        if re.search(rf"(?<![\w]){re.escape(dn)}(?![\w])", text):
            hit.append(dn)
            continue
        lab = labels.get(dn)
        if lab and len(lab) > 3 and re.search(re.escape(lab), text, re.I):
            hit.append(dn)
    return hit


# ─────────────────────────────────────────────────────────────────────────────
# the plan
# ─────────────────────────────────────────────────────────────────────────────

class Change:
    def __init__(self, rid: str, what: str, fn):
        self.id, self.what, self.fn = rid, what, fn

    def apply(self):
        self.fn()


def _verdict(date: str, decision: str, note: str) -> str:
    tail = f" — {note}" if note else ""
    return f"owner verdict {date}: {decision}{tail}"


def build_plan(dec_doc: dict, rows: list[dict], by_sheet: dict, glob: dict,
               date: str) -> tuple[list[Change], list[str]]:
    changes: list[Change] = []
    errors: list[str] = []
    kind = "flora" if "flora" in str(dec_doc.get("sheet", "")) else "fauna"

    def sheet_entry(sheet: str, rid: str):
        entry = by_sheet.get(sheet)
        if entry is None:
            errors.append(f"{rid}: no roster carries sheet {sheet!r} "
                          f"(known: {', '.join(sorted(by_sheet)[:4])}, ...)")
        return entry

    def resolve_move_target(rid: str, note: str) -> tuple[str, dict] | None:
        target = mined_target(note)
        if not target:
            errors.append(
                f"{rid}: verdict 'move' with no target in the note. The note must name the "
                f"destination — 'move:<BiomeDefName>' or '-> <sheet>'. Note was: {note!r}")
            return None
        entry = by_sheet.get(target)
        if entry is None:
            for cand in by_sheet.values():
                if target in (cand["doc"].get("defNames") or []):
                    entry = cand
                    break
        if entry is None:
            errors.append(f"{rid}: move target {target!r} is neither a roster sheet nor a "
                          f"painted biome defName in any roster.")
            return None
        return target, entry

    def mark(entry: dict):
        entry["dirty"] = True

    def add_fauna(entry: dict, defname: str, commonality: float, law: str,
                  note: str, action: str = "import"):
        fauna = entry["doc"].setdefault("fauna", [])
        for row in fauna:
            if row.get("def") == defname:
                row["law"] = (row.get("law") or "") + f"  — {law}"
                if note:
                    row["owner_note"] = note
                mark(entry)
                return
        new = {"def": defname, "commonality": commonality, "action": action, "law": law}
        if note:
            new["owner_note"] = note
        fauna.append(new)
        mark(entry)

    def to_evictions(entry: dict, defname: str, disposition: str, reason: str,
                     note: str, carried: dict | None):
        evictions = entry["doc"].setdefault("evictions", [])
        for row in evictions:
            if row.get("def") == defname:
                row["disposition"] = disposition
                row["reason"] = reason
                if note:
                    row["owner_note"] = note
                mark(entry)
                return
        row = {"def": defname, "reason": reason, "disposition": disposition}
        if note:
            row["owner_note"] = note
        if carried:
            # carry the landed row's own record through, minus the fields that only
            # mean something while it is rostered
            for key, val in carried.items():
                if key not in {"def", "commonality", "action", "law", "band"}:
                    row.setdefault(key, val)
        evictions.append(row)
        mark(entry)

    def take_from(lst: list, defname: str) -> dict | None:
        for i, row in enumerate(lst):
            if row.get("def") == defname:
                return lst.pop(i)
        return None

    def find(lst: list, defname: str) -> dict | None:
        for row in lst:
            if row.get("def") == defname:
                return row
        return None

    for row in rows:
        rid, decision, note = row["id"], row["decision"], row["note"]
        prefix, sheet, tail = parse_id(rid)
        verdict = _verdict(date, decision, note)

        # ── h: the homeless in-joke rows, which live in _global.json ────────────────
        if prefix == "h":
            if not glob:
                errors.append(f"{rid}: _global.json not loaded")
                continue
            defname = tail

            def do_h(defname=defname, decision=decision, verdict=verdict):
                ruled = glob["doc"].setdefault("ruled", {})
                jokes = ruled.setdefault("in_jokes_kept_reskinned", {})
                jokes[defname] = f"{jokes.get(defname, '')}  — {verdict}".strip()
                if decision in {"evict", "purge", "drop"}:
                    reserve = glob["doc"].setdefault("reserve_for_events", [])
                    if defname not in reserve:
                        reserve.append(defname)
                        reserve.sort()
                glob["dirty"] = True

            changes.append(Change(rid, f"_global.json in_jokes[{defname}] ← {decision}", do_h))
            continue

        entry = sheet_entry(sheet, rid)
        if entry is None:
            continue
        doc = entry["doc"]

        # ── c: an unsettled confidence[] claim ─────────────────────────────────────
        if prefix == "c":
            conf = doc.get("confidence") or []
            try:
                idx = int(tail)
                target_row = conf[idx]
            except (ValueError, IndexError):
                errors.append(f"{rid}: confidence[{tail}] does not exist in {sheet!r} "
                              f"({len(conf)} entries) — the roster changed since the sheet "
                              f"was generated; regenerate the sheet before applying.")
                continue

            def do_c(target_row=target_row, decision=decision, note=note, entry=entry,
                     verdict=verdict):
                target_row["owner_verdict"] = decision
                if note:
                    target_row["owner_note"] = note
                if decision in CLOSING:
                    target_row["status"] = f"RULED — {verdict}"
                mark(entry)

            changes.append(Change(rid, f"{sheet}: confidence[{tail}] ← {decision}", do_c))
            continue

        # ── nd: the NEW-ART/DEF ledger ─────────────────────────────────────────────
        if prefix == "nd":
            news = doc.get("new_defs") or []
            try:
                idx = int(tail)
                target_row = news[idx]
            except (ValueError, IndexError):
                errors.append(f"{rid}: new_defs[{tail}] does not exist in {sheet!r} "
                              f"({len(news)} entries) — regenerate the sheet first.")
                continue
            status = LEDGER_STATUS.get(decision, decision)

            def do_nd(target_row=target_row, status=status, note=note, entry=entry,
                      verdict=verdict):
                target_row["status"] = status
                target_row["owner_verdict"] = verdict
                if note:
                    target_row["owner_note"] = note
                mark(entry)

            changes.append(Change(
                rid, f"{sheet}: new_defs[{tail}] "
                     f"({target_row.get('name', '?')[:40]}) status ← {status}", do_nd))
            continue

        # ── purge: the one-per-biome flora_purged summary row ──────────────────────
        if prefix == "purge":
            purged = doc.get("flora_purged") or []
            if decision in {"keep", "thin"}:
                labels = {p.get("def", ""): p.get("label", "") for p in purged}
                named = named_in_note(note, [p.get("def", "") for p in purged], labels)
                if not named:
                    errors.append(
                        f"{rid}: overruled to {decision!r} but the note names none of the "
                        f"{len(purged)} purged plants, so there is nothing to restore. The "
                        f"note must name the defNames to bring back. Note was: {note!r}")
                    continue

                def do_restore(entry=entry, named=named, verdict=verdict, note=note):
                    d = entry["doc"]
                    for defname in named:
                        gone = take_from(d.setdefault("flora_purged", []), defname)
                        law = f"{verdict} — restored"
                        if gone and gone.get("reason"):
                            law += f" (was purged: {gone['reason']})"
                        flora = d.setdefault("flora", [])
                        if not find(flora, defname):
                            flora.append({"def": defname,
                                          "commonality": mined_commonality(note, 0.5),
                                          "law": law, "owner_note": note})
                    mark(entry)

                changes.append(Change(
                    rid, f"{sheet}: RESTORE {len(named)} purged plant(s) "
                         f"({', '.join(named)}) to flora[]", do_restore))
            else:
                def do_purge_note(entry=entry, verdict=verdict, decision=decision):
                    entry["doc"].setdefault("owner_verdicts", []).append(
                        {"row": "flora_purged (whole-biome)", "verdict": verdict})
                    mark(entry)

                changes.append(Change(
                    rid, f"{sheet}: flora_purged summary annotated ← {decision}",
                    do_purge_note))
            continue

        defname = tail

        # ── p: a landed flora[] row ────────────────────────────────────────────────
        if prefix == "p":
            flora = doc.get("flora") or []
            target_row = find(flora, defname)
            if target_row is None:
                errors.append(f"{rid}: {defname} is not in {sheet!r} flora[] — the roster "
                              f"changed since the sheet was generated.")
                continue
            if decision in {"purge", "drop", "evict"}:
                def do_p_purge(entry=entry, defname=defname, verdict=verdict, note=note):
                    d = entry["doc"]
                    take_from(d.setdefault("flora", []), defname)
                    row = {"def": defname, "reason": verdict}
                    if note:
                        row["owner_note"] = note
                    d.setdefault("flora_purged", []).append(row)
                    mark(entry)

                changes.append(Change(rid, f"{sheet}: flora {defname} → flora_purged[]",
                                      do_p_purge))
            else:
                # thin / defer / keep — an annotation plus a flag for the commonality edit
                def do_p_note(entry=entry, target_row=target_row, decision=decision,
                              note=note, verdict=verdict, defname=defname):
                    target_row["owner_verdict"] = verdict
                    if note:
                        target_row["owner_note"] = note
                    if decision == "thin":
                        entry["doc"].setdefault("owner_pending_edits", []).append(
                            {"def": defname, "kind": "flora commonality",
                             "verdict": verdict})
                    mark(entry)

                changes.append(Change(
                    rid, f"{sheet}: flora {defname} annotated ← {decision}"
                         + (" (flagged for the commonality edit)" if decision == "thin" else ""),
                    do_p_note))
            continue

        # ── f: a landed fauna[] row ────────────────────────────────────────────────
        if prefix == "f":
            fauna = doc.get("fauna") or []
            target_row = find(fauna, defname)
            if target_row is None:
                errors.append(f"{rid}: {defname} is not in {sheet!r} fauna[] — the roster "
                              f"changed since the sheet was generated.")
                continue

            if decision == "evict":
                def do_evict(entry=entry, defname=defname, verdict=verdict, note=note):
                    carried = take_from(entry["doc"].setdefault("fauna", []), defname)
                    to_evictions(entry, defname, "homeless-reserve", verdict, note, carried)

                changes.append(Change(
                    rid, f"{sheet}: fauna {defname} → evictions[] (homeless-reserve)",
                    do_evict))

            elif decision == "move":
                resolved = resolve_move_target(rid, note)
                if resolved is None:
                    continue
                target, tentry = resolved

                def do_move(entry=entry, tentry=tentry, target=target, defname=defname,
                            verdict=verdict, note=note, sheet=sheet):
                    carried = take_from(entry["doc"].setdefault("fauna", []), defname)
                    to_evictions(entry, defname, f"move:{target}", verdict, note, carried)
                    add_fauna(tentry, defname,
                              mined_commonality(note, carried.get("commonality", 0.4)
                                                if carried else 0.4),
                              f"{verdict} — moved here from {sheet}", note)

                changes.append(Change(
                    rid, f"{sheet}: fauna {defname} → evictions[] (move:{target}) "
                         f"AND rostered into {tentry['doc'].get('sheet')}", do_move))

            elif decision == "adjust":
                def do_adjust(entry=entry, target_row=target_row, defname=defname,
                              verdict=verdict, note=note):
                    target_row["action"] = "adjust-keep"
                    target_row["owner_verdict"] = verdict
                    if note:
                        target_row["owner_note"] = note
                    entry["doc"].setdefault("owner_pending_edits", []).append(
                        {"def": defname, "kind": "stat/commonality", "verdict": verdict})
                    mark(entry)

                changes.append(Change(
                    rid, f"{sheet}: fauna {defname} annotated ← adjust "
                         f"(flagged for the stat/commonality edit)", do_adjust))

            else:  # keep / open — annotate; 'keep' also cancels a pending adjust
                def do_keep(entry=entry, target_row=target_row, decision=decision,
                            verdict=verdict, note=note):
                    if decision == "keep":
                        target_row["action"] = "keep"
                    target_row["owner_verdict"] = verdict
                    if note:
                        target_row["owner_note"] = note
                    mark(entry)

                changes.append(Change(
                    rid, f"{sheet}: fauna {defname} annotated ← {decision}", do_keep))
            continue

        # ── e: an evictions[] row the sheet flagged ────────────────────────────────
        if prefix == "e":
            evictions = doc.get("evictions") or []
            target_row = find(evictions, defname)
            if target_row is None:
                errors.append(f"{rid}: {defname} is not in {sheet!r} evictions[] — the "
                              f"roster changed since the sheet was generated.")
                continue

            if decision in {"keep", "adjust"}:
                def do_restore(entry=entry, defname=defname, verdict=verdict, note=note,
                               decision=decision):
                    gone = take_from(entry["doc"].setdefault("evictions", []), defname)
                    law = verdict + " — restored to the roster"
                    if gone and gone.get("reason"):
                        law += f" (was evicted: {gone['reason']})"
                    add_fauna(entry, defname, mined_commonality(note, 0.4), law, note,
                              action="adjust-keep" if decision == "adjust" else "keep")
                    if decision == "adjust":
                        entry["doc"].setdefault("owner_pending_edits", []).append(
                            {"def": defname, "kind": "stat/commonality", "verdict": verdict})

                changes.append(Change(
                    rid, f"{sheet}: RESTORE {defname} evictions[] → fauna[] ({decision})",
                    do_restore))

            elif decision == "move":
                resolved = resolve_move_target(rid, note)
                if resolved is None:
                    continue
                target, tentry = resolved

                def do_emove(entry=entry, tentry=tentry, target=target, defname=defname,
                             verdict=verdict, note=note, sheet=sheet):
                    to_evictions(entry, defname, f"move:{target}", verdict, note, None)
                    add_fauna(tentry, defname, mined_commonality(note, 0.4),
                              f"{verdict} — moved here from {sheet}", note)

                changes.append(Change(
                    rid, f"{sheet}: eviction {defname} → move:{target} AND rostered "
                         f"into {tentry['doc'].get('sheet')}", do_emove))

            else:  # evict / open / drop
                def do_e_note(entry=entry, defname=defname, verdict=verdict, note=note,
                              decision=decision):
                    to_evictions(entry, defname, "homeless-reserve", verdict, note, None)

                changes.append(Change(
                    rid, f"{sheet}: eviction {defname} ← {decision} (homeless-reserve)",
                    do_e_note))
            continue

        errors.append(f"{rid}: unknown row-id prefix {prefix!r} — this consumer knows "
                      f"f/e/p/purge/nd/c/h. Was the sheet generator changed?")

    return changes, errors


# ─────────────────────────────────────────────────────────────────────────────
# reporting
# ─────────────────────────────────────────────────────────────────────────────

def print_override_group(name: str, doc: dict, rows: list[dict]) -> None:
    """review-sheets §3: read the overrides as a GROUP, not row by row."""
    total = len(doc.get("decisions") or {})
    print(f"\n{'=' * 78}\n{name}  —  {len(rows)} override(s) of {total} row(s) "
          f"({(len(rows) / total * 100 if total else 0):.1f}%)\n{'=' * 78}")
    if not rows:
        print("  no overrides. Every row stands as landed.\n"
              "  ⚠️  zero overrides means EITHER the prefill was right OR disagreeing was "
              "too hard — the file cannot tell you which (review-sheets §3).")
        return
    by_decision: dict[str, list[dict]] = {}
    for row in rows:
        by_decision.setdefault(row["decision"], []).append(row)
    for decision in sorted(by_decision):
        group = by_decision[decision]
        print(f"\n  ── {decision.upper()}  ({len(group)}) "
              f"{'─' * max(0, 60 - len(decision))}")
        for row in group:
            prefix, sheet, tail = parse_id(row["id"])
            where = f"{sheet}:{tail}" if sheet else tail
            print(f"    [{prefix:>5}] {where}   (was {row['prefill']})")
            if row["note"]:
                print(f"            note: {row['note']}")
    notes = [r for r in rows if r["note"]]
    print(f"\n  {len(notes)} of {len(rows)} overrides carry a note. Read them together "
          f"before implementing any one of them —\n  scattered disagreements are usually "
          f"one rule the sheet did not know.")


REGEN = [
    ("python3 design/Jawa/fauna/rosters_to_cast.py",
     "rosters -> cast_assignment.csv"),
    ("python3 design/Jawa/fauna/gen_cast_patch.py",
     "cast_assignment.csv -> BiomeCast_Ashkarr.xml"),
    ("python3 design/Jawa/mods/biome_flora.py --write --doc",
     "rosters -> the flora patch + its doc"),
    ("python3 design/Jawa/worldbuilding/review/gen_fauna_assignment_sheet.py --sheet-only",
     "re-render the fauna sheet (SAFE: --sheet-only never touches the decisions file)"),
    ("python3 design/Jawa/worldbuilding/review/gen_flora_assignment_sheet.py --sheet-only",
     "re-render the flora sheet (same guard)"),
]


def print_regen(changed: list[str]) -> None:
    print(f"\n{'=' * 78}\nREGENERATION OWED — {len(changed)} roster file(s) changed. "
          f"NOT run by this tool.\n{'=' * 78}")
    for path in changed:
        print(f"  changed: {path}")
    print("\n  From the repo root, in this order:")
    for cmd, why in REGEN:
        print(f"    {cmd}\n        # {why}")
    print("\n  ⛔ Do NOT run the sheet generators without --sheet-only: they rewrite the\n"
          "     decisions file with the agent's prefill and eat the owner's verdicts.")


def run_validator(validator: str, rosters_dir: str) -> int:
    print(f"\n{'=' * 78}\nVALIDATOR: {validator} --cross\n{'=' * 78}")
    proc = subprocess.run([sys.executable, validator, "--cross"],
                          cwd=rosters_dir, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    red = [ln for ln in out.splitlines() if ln.startswith("🔴")]
    warn = [ln for ln in out.splitlines() if ln.startswith("⚠️")]
    for line in red + warn:
        print("  " + line)
    print(f"  -> exit {proc.returncode}; {len(red)} red, {len(warn)} warning(s)")
    if proc.returncode != 0 or red:
        print("\n🔴🔴 VALIDATOR WENT RED AFTER THE APPLY. The rosters ON DISK are now\n"
              "     inconsistent. Fix the findings above, or `git checkout --` the roster\n"
              "     files listed and re-run with corrected verdict notes. Do NOT regenerate\n"
              "     the cast or flora patches from a red roster set.")
        return RC_VALIDATOR
    return RC_OK


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def write_rosters(by_sheet: dict, glob: dict) -> list[str]:
    written = []
    for entry in list(by_sheet.values()) + ([glob] if glob else []):
        if not entry.get("dirty"):
            continue
        with open(entry["path"], "w", encoding="utf-8") as fh:
            json.dump(entry["doc"], fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        written.append(entry["path"])
    return written


def run(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Apply owner verdicts from an assignment review sheet to the rosters.")
    ap.add_argument("decisions", nargs="*", help="decisions JSON (default: both sheets)")
    ap.add_argument("--apply", action="store_true",
                    help="write the rosters (default: report only)")
    ap.add_argument("--allow-unfrozen", action="store_true",
                    help="consume a decisions file that has not been frozen")
    ap.add_argument("--rosters", default=ROSTERS, help="roster directory")
    ap.add_argument("--validator", default=None,
                    help="validator script (default: <rosters>/_validate.py)")
    ap.add_argument("--no-validate", action="store_true",
                    help="skip the post-apply validator (for a dry lane only)")
    ap.add_argument("--date", default=_dt.date.today().isoformat(),
                    help="the date stamped into every verdict line")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    paths = args.decisions or DEFAULT_DECISIONS
    validator = args.validator or os.path.join(args.rosters, "_validate.py")

    try:
        by_sheet, glob = load_rosters(args.rosters)
        all_changes: list[Change] = []
        all_errors: list[str] = []
        for path in paths:
            doc = load_decisions(path, args.allow_unfrozen)
            rows = overrides_of(doc)
            print_override_group(os.path.basename(path), doc, rows)
            changes, errors = build_plan(doc, rows, by_sheet, glob, args.date)
            all_changes += changes
            all_errors += errors
    except Refuse as exc:
        print(str(exc))
        return exc.code

    print(f"\n{'=' * 78}\nPLAN — {len(all_changes)} roster amendment(s)\n{'=' * 78}")
    for change in all_changes:
        print(f"  {change.what}")
    if not all_changes:
        print("  (nothing to do)")

    if all_errors:
        print(f"\n{'=' * 78}\n🔴 {len(all_errors)} VERDICT(S) COULD NOT BE RESOLVED — "
              f"NOTHING WAS WRITTEN\n{'=' * 78}")
        for err in all_errors:
            print(f"  {err}")
        return RC_UNRESOLVED

    if not args.apply:
        print("\n  report only. Nothing written. Re-run with --apply to amend the rosters.")
        return RC_OK

    for change in all_changes:
        change.apply()
    written = write_rosters(by_sheet, glob)
    print(f"\n  wrote {len(written)} roster file(s).")

    rc = RC_OK
    if not args.no_validate:
        rc = run_validator(validator, args.rosters)
    print_regen(written)
    return rc


# ─────────────────────────────────────────────────────────────────────────────
# selftest — a synthetic roster + decisions pair, proving the four contracts
# ─────────────────────────────────────────────────────────────────────────────

SELFTEST_ROSTER = {
    "sheet": "synth_one",
    "defNames": ["SynthBiome"],
    "unknown_top_key": {"kept": "carry me through untouched"},
    "law_sources": ["synth.md"],
    "fauna": [
        {"def": "SynthKeeper", "commonality": 0.5, "action": "keep", "law": "stays put",
         "unknown_row_key": 42},
        {"def": "SynthEvictee", "commonality": 0.3, "action": "keep", "law": "landed"},
        {"def": "SynthMover", "commonality": 0.6, "action": "keep", "law": "landed"},
        {"def": "SynthAdjustee", "commonality": 0.7, "action": "keep", "law": "landed"},
    ],
    "evictions": [
        {"def": "SynthReturner", "reason": "flagged for owner review",
         "disposition": "homeless-reserve"},
    ],
    "stat_adjustments": [],
    "flora": [{"def": "SynthPlant", "commonality": 0.4, "law": "landed"}],
    "flora_purged": [{"def": "SynthPurged", "reason": "Earth-nameable"}],
    "fish": {"ruling": "none", "list": []},
    "new_defs": [{"name": "synth signature plant", "kind": "plant",
                  "mechanic_load": "none", "from_sheet": "synth §1"}],
    "confidence": [{"claim": "SynthMover flies", "status": "UNMEASURED",
                    "why": "register flag broken"}],
}

SELFTEST_ROSTER_TWO = {
    "sheet": "synth two + deep",
    "defNames": ["SynthBiomeTwo"],
    "fauna": [], "evictions": [], "flora": [], "flora_purged": [],
    "fish": {"ruling": "none", "list": []}, "new_defs": [], "confidence": [],
}

SELFTEST_DECISIONS = {
    "sheet": "fauna_assignment_register",
    "posture": "blacklist",
    "unknown_top_key": "carried",
    "decisions": {
        "f:synth_one:SynthKeeper": {"decision": "keep", "prefill": "keep", "note": ""},
        "f:synth_one:SynthEvictee": {"decision": "evict", "prefill": "keep",
                                     "note": "does not belong"},
        "f:synth_one:SynthMover": {"decision": "move", "prefill": "keep",
                                   "note": "move:SynthBiomeTwo comm 0.25"},
        "f:synth_one:SynthAdjustee": {"decision": "adjust", "prefill": "keep",
                                      "note": "too fast, halve moveSpeed"},
        "e:synth_one:SynthReturner": {"decision": "keep", "prefill": "evict",
                                      "note": "I want this one, comm 0.2"},
        "nd:synth_one:0": {"decision": "defer", "prefill": "keep", "note": "later"},
        "c:synth_one:0": {"decision": "keep", "prefill": "open", "note": "it flies"},
    },
}

STUB_OK = ("import sys, pathlib\n"
           "pathlib.Path(__file__).with_name('VALIDATOR_RAN').write_text(' '.join(sys.argv))\n"
           "print('OK')\n")
STUB_RED = ("print('\\U0001f534 cross: synthetic failure')\nraise SystemExit(1)\n")


def _run_tool(argv, cwd=None):
    proc = subprocess.run([sys.executable, os.path.abspath(__file__)] + argv,
                          capture_output=True, text=True, cwd=cwd)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def selftest() -> int:
    failures = []

    def check(name, cond, detail=""):
        print(("  ✅ " if cond else "  ❌ ") + name + (f"  {detail}" if not cond else ""))
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        rosters = os.path.join(tmp, "rosters")
        os.makedirs(rosters)
        for doc in (SELFTEST_ROSTER, SELFTEST_ROSTER_TWO):
            name = doc["sheet"].replace(" ", "_").replace("+", "and") + ".json"
            with open(os.path.join(rosters, name), "w", encoding="utf-8") as fh:
                json.dump(doc, fh, indent=2)
        pristine = os.path.join(tmp, "pristine")
        shutil.copytree(rosters, pristine)

        stub_ok = os.path.join(tmp, "stub_validate.py")
        stub_red = os.path.join(tmp, "stub_red.py")
        open(stub_ok, "w").write(STUB_OK)
        open(stub_red, "w").write(STUB_RED)
        marker = os.path.join(tmp, "VALIDATOR_RAN")

        prefill = os.path.join(tmp, "prefill.decisions.json")
        with open(prefill, "w", encoding="utf-8") as fh:
            json.dump(SELFTEST_DECISIONS, fh, indent=1)

        signed = json.loads(json.dumps(SELFTEST_DECISIONS))
        signed.update({"savedBy": "review-sheet-sidecar", "writeCount": 12,
                       "savedAt": "2026-09-09T10:00:00+0000"})
        unfrozen = os.path.join(tmp, "unfrozen.decisions.json")
        with open(unfrozen, "w", encoding="utf-8") as fh:
            json.dump(signed, fh, indent=1)

        frozen_doc = dict(signed, frozen=True, frozenOn="2026-09-09")
        frozen = os.path.join(tmp, "frozen.decisions.json")
        with open(frozen, "w", encoding="utf-8") as fh:
            json.dump(frozen_doc, fh, indent=1)

        base = ["--rosters", rosters, "--validator", stub_ok, "--date", "2026-09-09"]

        print("\n1. the touchedBySheet guard — a PREFILL must never be consumed")
        rc, out = _run_tool([prefill, "--apply"] + base)
        check("refuses without the sidecar keys", rc == RC_NO_SIDECAR, f"rc={rc}")
        check("names the missing keys", all(k in out for k in SIDECAR_KEYS))
        check("hands back the localStorage recovery", "localStorage" in out)
        check("wrote nothing", _same_tree(rosters, pristine))

        print("\n2. the freeze guard")
        rc, out = _run_tool([unfrozen, "--apply"] + base)
        check("refuses an unfrozen decisions file", rc == RC_NOT_FROZEN, f"rc={rc}")
        rc, out = _run_tool([unfrozen, "--allow-unfrozen"] + base)
        check("--allow-unfrozen lets it through", rc == RC_OK, f"rc={rc}")

        print("\n3. report first, apply second")
        rc, out = _run_tool([frozen] + base)
        check("report mode exits 0", rc == RC_OK, f"rc={rc}")
        check("prints the overrides grouped by verdict", "── EVICT" in out and "── MOVE" in out)
        check("prints the plan", "PLAN — " in out)
        check("report mode writes NOTHING", _same_tree(rosters, pristine))
        check("report mode does not run the validator", not os.path.exists(marker))

        rc, out = _run_tool([frozen, "--apply"] + base)
        check("apply exits 0", rc == RC_OK, f"rc={rc}\n{out[-2000:]}")
        check("apply runs the validator with --cross", os.path.exists(marker)
              and "--cross" in open(marker).read())
        check("prints the regeneration commands owed",
              "rosters_to_cast.py" in out and "biome_flora.py --write --doc" in out)
        check("does not RUN them", "wrote cast_assignment" not in out)

        with open(os.path.join(rosters, "synth_one.json"), encoding="utf-8") as fh:
            after = json.load(fh)
        fauna = {r["def"]: r for r in after["fauna"]}
        evic = {r["def"]: r for r in after["evictions"]}
        with open(os.path.join(rosters, "synth_two_and_deep.json"), encoding="utf-8") as fh:
            after2 = json.load(fh)

        print("\n4. the verdicts landed")
        check("evict → evictions[] homeless-reserve",
              "SynthEvictee" not in fauna
              and evic.get("SynthEvictee", {}).get("disposition") == "homeless-reserve")
        check("evict reason is 'owner verdict <date>'",
              evic.get("SynthEvictee", {}).get("reason", "").startswith(
                  "owner verdict 2026-09-09"))
        check("move → evictions[] move:<target from the note>",
              evic.get("SynthMover", {}).get("disposition") == "move:SynthBiomeTwo")
        check("move also rosters the def in the TARGET (or _validate goes red)",
              any(r["def"] == "SynthMover" for r in after2["fauna"]))
        check("move carries the note's commonality",
              any(r["def"] == "SynthMover" and r["commonality"] == 0.25
                  for r in after2["fauna"]))
        check("adjust annotates + flags the stat edit",
              fauna["SynthAdjustee"].get("owner_note") == "too fast, halve moveSpeed"
              and any(e["def"] == "SynthAdjustee"
                      for e in after.get("owner_pending_edits", [])))
        check("keep on an eviction row restores it to fauna[]",
              "SynthReturner" in fauna and "SynthReturner" not in evic
              and "owner verdict" in fauna["SynthReturner"]["law"])
        check("NEW-ART ledger verdict rewrites new_defs status",
              after["new_defs"][0].get("status") == "defer")
        check("confidence[] verdict is recorded and closed",
              after["confidence"][0].get("owner_verdict") == "keep"
              and after["confidence"][0]["status"].startswith("RULED"))

        print("\n5. rows the owner did not override, and unknown keys")
        check("a non-overridden row is untouched",
              fauna["SynthKeeper"] == SELFTEST_ROSTER["fauna"][0])
        check("unknown TOP-LEVEL key carried through",
              after.get("unknown_top_key") == {"kept": "carry me through untouched"})
        check("unknown ROW-LEVEL key carried through",
              fauna["SynthKeeper"].get("unknown_row_key") == 42)
        check("untouched roster file not rewritten at all",
              json.load(open(os.path.join(rosters, "synth_two_and_deep.json"))) != {}
              and set(SELFTEST_ROSTER_TWO) <= set(after2))

        print("\n6. an unresolvable verdict refuses the WHOLE apply")
        bad = json.loads(json.dumps(frozen_doc))
        bad["decisions"] = {"f:synth_one:SynthKeeper":
                            {"decision": "move", "prefill": "keep", "note": "somewhere"}}
        bad_path = os.path.join(tmp, "bad.decisions.json")
        json.dump(bad, open(bad_path, "w"))
        shutil.rmtree(rosters)
        shutil.copytree(pristine, rosters)
        rc, out = _run_tool([bad_path, "--apply"] + base)
        check("move with no target in the note is refused", rc == RC_UNRESOLVED, f"rc={rc}")
        check("nothing written on an unresolved plan", _same_tree(rosters, pristine))

        print("\n7. a red validator is loud and non-zero")
        rc, out = _run_tool([frozen, "--apply", "--rosters", rosters,
                             "--validator", stub_red, "--date", "2026-09-09"])
        check("red validator → exit 4", rc == RC_VALIDATOR, f"rc={rc}")
        check("says so loudly", "VALIDATOR WENT RED" in out)

    print(f"\n{'PASS' if not failures else 'FAIL'} — "
          f"{len(failures)} failure(s){': ' + ', '.join(failures) if failures else ''}")
    return 1 if failures else 0


def _same_tree(a: str, b: str) -> bool:
    names = sorted(os.listdir(a))
    if names != sorted(os.listdir(b)):
        return False
    return all(open(os.path.join(a, n), "rb").read() == open(os.path.join(b, n), "rb").read()
               for n in names)


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))

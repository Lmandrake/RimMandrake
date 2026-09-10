#!/usr/bin/env python3
"""apply_assignment_verdicts.py — the CONSUMER side of the fauna/flora assignment sheets.

Rewritten for the 2026-09-09 rulings schema (commit 19e03876). The old applier
(row ids f:/e:/p:/purge:/nd:/c:/h:, verdicts keep/adjust/move/evict/open/...)
is DEAD — the sheets now emit q:/fauna:/flora:/homeless:/ledger: row ids and
in/move/out/later verdicts, plus two extra per-row lanes (sizeBin, art). This
reads gen_fauna_assignment_sheet.py / gen_flora_assignment_sheet.py's own
header text and the live sheets/decisions files as the schema authority —
never guessed.

    python3 apply_assignment_verdicts.py                 # report only, both sheets
    python3 apply_assignment_verdicts.py --apply          # write rosters + worklists
    python3 apply_assignment_verdicts.py fauna_assignment_register.decisions.json --apply
    python3 apply_assignment_verdicts.py --selftest       # delegates to the selftest file

🔴 THE GUARD THAT MATTERS (review-sheets skill §8). A pre-fill and a reviewed
file look byte-similar. Only the sidecar can stamp savedBy/writeCount — a
pre-fill generator can never emit them — so this REFUSES to touch a decisions
file lacking that stamp: an agent's own guesses must never be applied as the
owner's verdicts. `frozen` is NOT checked — freezing happens at review end,
and a frozen file is exactly as safe to apply as a live one; only an
UNSTAMPED file is refused.

ROW-ID SCHEME (see gen_fauna_assignment_sheet.py / gen_flora_assignment_sheet.py):
    q:<sheet>:<slug>          a question card               decision in {in,out,later}
    fauna:<sheet>:<defName>   an in-biome creature row       decision in {in,move,out,later}
                              + sizeBin (small|medium|large|titan), art (keep|improve|redo)
    flora:<sheet>:<defName>   an in-biome plant row          same shape as fauna: rows
    homeless:<defName>        a no-home-yet creature row     decision in {in,move,out,later}
                              "in" = carry out the row's GROUP recommendation (read from
                              the sheet's ITEMS block — decisions.json does not carry it);
                              "move" = a real biome named in the note; "out" = CUT FOR REAL
                              regardless of which of the 6 recommendation groups it sat in
    ledger:<sheet>:<slug>     a NEW-ART/NEW-DEF commission row (fauna sheet has none;
                              flora sheet's "New things to create" rows)  decision in
                              {in,out,later}: in = commission, out = drop for good

⚠️ <sheet> is the roster's `sheet` FIELD, not its filename (`the_grey_sea.json` carries
sheet "terminator_sea + the_grey_deep"). Resolve by loading every roster and indexing on
that field — never guess it from the filename.

WHAT THIS WRITES (only under --apply; report mode never touches disk):
    rosters/<file>.json                  in-biome Move/Out edits (per decisions file's biomes)
    rosters/_draft_<cave|sea|dungeon>_layer.json   the 3 strange-strata homeless groups,
                                                    "in" verdicts — leading "_" keeps
                                                    _validate.py's bare glob from eating them
    <sheet>.homeless_events_quest_pool.json        homeless "keep for events & quests" group
    <sheet>.homeless_livestock_trader_stock.json   homeless "livestock & trader stock" group
    <sheet>.cherry_pick_cut_list.json              every real "cut for real" disposition —
                                                    NEVER runs Cherry Picker itself
    <sheet>.size_rescale_worklist.json             defName/current bin/chosen bin/grow-shrink,
                                                    for FOUNDRY — this tool never edits a def
    <sheet>.art_queue.json                         art verdicts != keep, + ledger commissions

Nothing partial: each decisions file's whole plan is built in memory first: an
unparseable/missing Move target refuses THAT FILE's entire apply (report still
runs) and nothing from it is written. Out-of-scope top-level keys in a decisions
file are carried through untouched (this tool never rewrites the decisions file).

Exit codes: 0 ok · 2 no sidecar stamp (nothing applied) · 5 a Move target could
not be resolved (nothing from that file was written) · 6 the post-apply
rosters/_validate.py --cross run reported problems (the writes already landed)
"""
from __future__ import annotations

import argparse
import glob as _glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ROSTERS = os.path.join(ROOT, "design", "Jawa", "worldbuilding", "biomes", "rosters")
REVIEW = HERE

DEFAULT_DECISIONS = [
    os.path.join(REVIEW, "fauna_assignment_register.decisions.json"),
    os.path.join(REVIEW, "flora_assignment_register.decisions.json"),
]

STAMP_BY = "review-sheet-sidecar"   # assets/serve_sheet.py's STAMP_BY — the unforgeable mark
RC_OK, RC_NO_SIDECAR, RC_UNRESOLVED, RC_VALIDATOR = 0, 2, 5, 6

SIZE_ORDER = ["small", "medium", "large", "titan"]

# Verbatim from gen_fauna_assignment_sheet.py's HOMELESS_GROUPS — the label text IS the
# only place a homeless row's recommendation-group lives (decisions.json does not carry
# it). Kept as a literal table, not re-derived, so a generator wording change fails LOUD
# (KeyError on an unrecognised group) instead of silently mis-bucketing a verdict.
HOMELESS_GROUPS = {
    "No home yet → my call: the underground & cave layer (draft roster)": "cave",
    "No home yet → my call: the deep seas & underwater layer (draft roster)": "sea",
    "No home yet → my call: dungeon & vault guardians (draft palette)": "dungeon",
    "No home yet → my call: keep for events & quests only": "events",
    "No home yet → my call: livestock & trader stock only": "livestock",
    "No home yet → my call: cut for real": "cut",
}
DRAFT_ROSTER_NAME = {"cave": "_draft_cave_layer.json",
                      "sea": "_draft_sea_layer.json",
                      "dungeon": "_draft_dungeon_guardians.json"}


class Refuse(Exception):
    """A guard refused. Nothing from this decisions file is written."""


# ═══════════════════════════════════════════════════════════════ loading

def load_decisions(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if not isinstance(doc, dict) or not isinstance(doc.get("decisions"), dict):
        raise Refuse(f"{os.path.basename(path)}: not a decisions file (no 'decisions' object)")
    touched = doc.get("savedBy") == STAMP_BY and isinstance(doc.get("writeCount"), int) \
        and doc.get("writeCount", 0) >= 1
    if not touched:
        raise Refuse(
            f"🔴 REFUSING {os.path.basename(path)}: not stamped by the sidecar "
            f"(savedBy={doc.get('savedBy')!r}, writeCount={doc.get('writeCount')!r}). "
            "An untouched pre-fill is the agent's guesses, never the owner's review — "
            "open the sheet, let the owner save at least once, then run this again. "
            "(frozen is not checked here — a frozen file is fine to apply.)")
    return doc


def _find_script_json(html: str, script_id: str):
    """The template's own header text mentions `<script id="...">` inside an HTML
    comment before the real tag — take the LAST occurrence that parses as JSON."""
    idxs = [m.start() for m in re.finditer(rf'<script id="{script_id}"', html)]
    for i in reversed(idxs):
        start = html.find(">", i) + 1
        end = html.find("</script>", start)
        if start <= 0 or end < 0:
            continue
        try:
            return json.loads(html[start:end])
        except json.JSONDecodeError:
            continue
    return None


def load_items(html_path: str) -> dict:
    """id -> item dict from the sheet's ITEMS block. Best-effort: a missing/unparseable
    sheet degrades label quality and disables homeless-group classification, but never
    crashes the report (it can still print raw ids and every fauna:/flora: in-biome row,
    whose biome is already in the id)."""
    if not os.path.isfile(html_path):
        return {}
    try:
        html = open(html_path, encoding="utf-8").read()
    except OSError:
        return {}
    items = _find_script_json(html, "ITEMS")
    if not isinstance(items, list):
        return {}
    return {it["id"]: it for it in items if isinstance(it, dict) and "id" in it}


def load_roster_index() -> dict:
    """sheet-FIELD -> (path, doc). Never index by filename — the_grey_sea.json's sheet
    field is 'terminator_sea + the_grey_deep', not derivable from the path."""
    index = {}
    for path in sorted(_glob.glob(os.path.join(ROSTERS, "*.json"))):
        name = os.path.basename(path)
        if name.startswith("_"):
            continue
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        key = doc.get("sheet")
        if not key:
            continue
        index[key] = {"path": path, "doc": doc}
    return index


# ═══════════════════════════════════════════════════════════════ row-id parsing

def parse_row_id(item_id: str):
    """-> (kind, sheet_or_None, rest). Sheet keys hold spaces and '+' but never ':',
    so a bounded split is safe; homeless: rows carry no sheet segment at all."""
    kind, _, tail = item_id.partition(":")
    if kind == "homeless":
        return kind, None, tail
    sheet, _, rest = tail.partition(":")
    return kind, sheet, rest


# ═══════════════════════════════════════════════════════ Move target resolution

def _sheet_terms(sheet_key: str) -> list[str]:
    plain = sheet_key.replace("_", " ")
    terms = [plain]
    if plain.startswith("the "):
        terms.append(plain[4:])
    return terms


def resolve_move_target(note: str, own_sheet, roster_index: dict):
    """-> sheet_key, or None if the note names no single unambiguous destination.
    Tiered: prefer a full sheet-phrase match (handles 'the rot' safely) and only fall
    back to a bare single word when no phrase matched anywhere, to avoid 'desert'
    swallowing 'dune_sea + deep_desert'. Ambiguity is failure, not a guess."""
    text = (note or "").lower()
    tier1, tier2 = set(), set()
    for key in roster_index:
        if key == own_sheet:
            continue
        for term in _sheet_terms(key):
            if not term:
                continue
            pat = r"\b" + re.escape(term) + r"\b"
            if re.search(pat, text):
                (tier1 if " " in term or len(term) > 6 else tier2).add(key)
                break
    hit = tier1 or tier2
    return next(iter(hit)) if len(hit) == 1 else None


# ═══════════════════════════════════════════════════════════════ the plan

class Plan:
    def __init__(self, sheet_kind: str, source: str):
        self.sheet_kind = sheet_kind          # "fauna" | "flora"
        self.source = source                  # decisions file basename, for provenance
        self.overrides: list[dict] = []       # decision != prefill, ALL kinds
        self.q_rulings: list[dict] = []
        self.roster_writes: dict = {}         # sheet_key -> doc (mutated in place)
        self.draft_additions: dict = {}       # gkey(cave/sea/dungeon) -> [entries]
        self.cut_list: list[dict] = []
        self.events_pool: list[dict] = []
        self.livestock_pool: list[dict] = []
        self.size_worklist: list[dict] = []
        self.art_queue: list[dict] = []
        self.errors: list[str] = []
        self.noop = 0


def _label(items: dict, item_id: str, fallback: str) -> str:
    it = items.get(item_id)
    return (it.get("label") if it else None) or fallback


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _law_text(kind: str, verdict: str, source_sheet, target_sheet, note: str) -> str:
    bits = [f"owner review {_now_stamp()} ({verdict})"]
    if source_sheet and target_sheet:
        bits.append(f"{source_sheet} → {target_sheet}")
    if note:
        bits.append(note.strip())
    return "; ".join(bits)


def _remove_def(doc: dict, listkey: str, defname: str):
    doc[listkey] = [r for r in (doc.get(listkey) or []) if r.get("def") != defname]


def build_plan(doc: dict, sheet_kind: str, items: dict, roster_index: dict,
               source_name: str) -> Plan:
    plan = Plan(sheet_kind, source_name)
    decisions = doc["decisions"]

    for item_id, entry in decisions.items():
        decision = entry.get("decision")
        prefill = entry.get("prefill")
        note = (entry.get("note") or "").strip()
        kind, sheet, rest = parse_row_id(item_id)
        label = _label(items, item_id, rest or item_id)
        group = (items.get(item_id) or {}).get("group", "")

        if decision != prefill:
            plan.overrides.append({
                "id": item_id, "kind": kind, "group": group or sheet or "?",
                "label": label, "decision": decision, "prefill": prefill, "note": note,
            })

        # size / art lanes ride on top of ANY kind that carries them, independent
        # of the disposition below (dispositions decide WHERE it lives, not HOW big
        # or well-drawn — a rescale/redraw target only matters for a thing staying
        # in the game, so "out"/"later" rows are excluded here).
        keeps_playing = decision in ("in", "move")
        if keeps_playing and "sizeBin" in entry:
            cur, chosen = entry.get("sizeBinPrefill"), entry.get("sizeBin")
            if cur in SIZE_ORDER and chosen in SIZE_ORDER:
                delta = SIZE_ORDER.index(chosen) - SIZE_ORDER.index(cur)
                direction = "grow" if delta > 0 else "shrink" if delta < 0 else "same"
            else:
                direction = "unknown"
            plan.size_worklist.append({
                "defName": rest, "sheet": sheet or "homeless",
                "currentBin": cur, "chosenBin": chosen, "direction": direction,
            })
        if keeps_playing and entry.get("art") not in (None, "keep"):
            plan.art_queue.append({
                "defName": rest, "sheet": sheet or "homeless", "kind": "regrade",
                "verdict": entry.get("art"), "note": note,
            })

        if kind == "q":
            plan.q_rulings.append({"id": item_id, "label": label, "decision": decision,
                                    "note": note})
            continue

        if kind == "ledger":
            if decision == "in":
                plan.art_queue.append({
                    "id": item_id, "sheet": sheet, "label": label, "kind": "commission",
                    "verdict": "commission", "note": note,
                })
            # out/later: nothing exists yet to write anywhere; the report already
            # carries the ruling via overrides/q_rulings-style bookkeeping is not
            # needed since "in" (commission) is the sheet's own prefill for these.
            continue

        if kind in ("fauna", "flora"):
            listkey = kind  # "fauna" or "flora" list name matches the row kind
            defname = rest
            if decision == "in" or decision == "later":
                continue  # stands as recommended, or parked on purpose — no write
            src = roster_index.get(sheet)
            if src is None:
                plan.errors.append(f"{item_id}: source sheet {sheet!r} not found in rosters/")
                continue
            src_doc = src["doc"]
            src_entry = next((r for r in (src_doc.get(listkey) or [])
                              if r.get("def") == defname), None)
            if decision == "out":
                _remove_def(src_doc, listkey, defname)
                if kind == "fauna":
                    src_doc.setdefault("evictions", []).append({
                        "def": defname,
                        "reason": _law_text(kind, "out", sheet, None, note),
                        "disposition": "homeless-reserve",
                    })
                else:
                    src_doc.setdefault("flora_purged", []).append({
                        "def": defname, "reason": _law_text(kind, "out", sheet, None, note),
                    })
                plan.roster_writes[sheet] = src["path"]
            elif decision == "move":
                target = resolve_move_target(note, sheet, roster_index)
                if target is None:
                    plan.errors.append(
                        f"{item_id}: Move but the note does not name one unambiguous "
                        f"biome — note={note!r}")
                    continue
                _remove_def(src_doc, listkey, defname)
                tgt = roster_index[target]
                new_row = {"def": defname,
                           "commonality": (src_entry or {}).get("commonality", 0.5),
                           "law": _law_text(kind, "move", sheet, target, note)}
                if kind == "fauna":
                    new_row["action"] = "import"
                    if src_entry and src_entry.get("band"):
                        new_row["band"] = src_entry["band"]
                    src_doc.setdefault("evictions", []).append({
                        "def": defname,
                        "reason": _law_text(kind, "move", sheet, target, note),
                        "disposition": f"move:{tgt['doc'].get('defNames', [target])[0] if tgt['doc'].get('defNames') else target}",
                    })
                tgt["doc"].setdefault(listkey, []).append(new_row)
                plan.roster_writes[sheet] = src["path"]
                plan.roster_writes[target] = tgt["path"]
            else:
                plan.errors.append(f"{item_id}: unrecognised decision {decision!r}")
            continue

        if kind == "homeless":
            defname = rest
            if decision == "later":
                continue
            if decision == "out":
                plan.cut_list.append({"defName": defname, "note": note,
                                       "reason": "owner review: Out on a no-home row"})
                continue
            if decision == "move":
                target = resolve_move_target(note, None, roster_index)
                if target is None:
                    plan.errors.append(
                        f"{item_id}: Move but the note does not name one unambiguous "
                        f"biome — note={note!r}")
                    continue
                tgt = roster_index[target]
                tgt["doc"].setdefault("fauna", []).append({
                    "def": defname, "commonality": 0.5, "action": "import",
                    "law": _law_text(kind, "move", None, target, note),
                })
                plan.roster_writes[target] = tgt["path"]
                continue
            # decision == "in": carry out the row's own recommendation group
            gkey = HOMELESS_GROUPS.get(group)
            if gkey is None:
                plan.errors.append(
                    f"{item_id}: homeless row's group {group!r} does not match any "
                    "known HOMELESS_GROUPS label — sheet text may have changed; "
                    "refusing rather than guessing its destiny "
                    "(is the ITEMS block loadable? check the .html sibling exists)")
                continue
            if gkey == "cut":
                plan.cut_list.append({"defName": defname, "note": note,
                                       "reason": "owner review: stands as recommended (cut)"})
            elif gkey == "events":
                plan.events_pool.append({"defName": defname, "note": note})
            elif gkey == "livestock":
                plan.livestock_pool.append({"defName": defname, "note": note})
            else:  # cave / sea / dungeon draft rosters
                plan.draft_additions.setdefault(gkey, []).append({
                    "def": defname, "commonality": 0.5,
                    "law": _law_text(kind, "in", None, gkey, note),
                })
            continue

        plan.errors.append(f"{item_id}: unrecognised row-id kind {kind!r}")

    return plan


# ═══════════════════════════════════════════════════════════════ report + write

def print_overrides(plan: Plan):
    if not plan.overrides:
        print(f"  (no overrides — every row still reads as its own prefill)")
        return
    by_group: dict[str, list] = {}
    for o in plan.overrides:
        by_group.setdefault(o["group"], []).append(o)
    for group, rows in sorted(by_group.items()):
        print(f"  ── {group} ──")
        for o in rows:
            note = f"  — {o['note']}" if o["note"] else ""
            print(f"    [{o['kind']}] {o['label']}: {o['prefill']} → {o['decision']}{note}")


def print_report(plan: Plan):
    print(f"\n=== {plan.source} — overrides (decision != prefill), as groups ===")
    print_overrides(plan)
    if plan.q_rulings:
        print(f"\n=== {plan.source} — question-card rulings ===")
        for q in plan.q_rulings:
            note = f"  — {q['note']}" if q["note"] else ""
            print(f"  {q['label']}: {q['decision']}{note}")
    print(f"\n=== {plan.source} — write plan ===")
    print(f"  rosters touched: {len(plan.roster_writes)}")
    print(f"  draft-group additions: { {k: len(v) for k, v in plan.draft_additions.items()} }")
    print(f"  cut-for-real: {len(plan.cut_list)}")
    print(f"  events/quest pool: {len(plan.events_pool)}")
    print(f"  livestock/trader pool: {len(plan.livestock_pool)}")
    print(f"  size-rescale worklist rows: {len(plan.size_worklist)}")
    print(f"  art-queue rows: {len(plan.art_queue)}")
    if plan.errors:
        print(f"\n🔴 {len(plan.errors)} BLOCKING error(s) — nothing from {plan.source} "
              "will be written:")
        for e in plan.errors:
            print(f"    - {e}")


def apply_all(plan: Plan, roster_index: dict, sheet_stem: str):
    written = []
    for sheet_key, path in plan.roster_writes.items():
        doc = roster_index[sheet_key]["doc"]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        written.append(path)

    for gkey, rows in plan.draft_additions.items():
        path = os.path.join(ROSTERS, DRAFT_ROSTER_NAME[gkey])
        doc = {"sheet": f"_draft_{gkey}", "draft": True,
               "draftMeaning": "no biome/layer exists for this yet — a first-cut roster "
                                "from the homeless review, not a real biome file",
               "generatedFrom": os.path.basename(plan.source), "fauna": []}
        if os.path.isfile(path):
            doc = json.load(open(path, encoding="utf-8"))
        doc.setdefault("fauna", []).extend(rows)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        written.append(path)

    def _side(name, rows):
        if not rows:
            return
        path = os.path.join(REVIEW, f"{sheet_stem}.{name}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        written.append(path)

    _side("cherry_pick_cut_list", plan.cut_list)
    _side("homeless_events_quest_pool", plan.events_pool)
    _side("homeless_livestock_trader_stock", plan.livestock_pool)
    _side("size_rescale_worklist", plan.size_worklist)
    _side("art_queue", plan.art_queue)
    return written


def run_validate_cross():
    script = os.path.join(ROSTERS, "_validate.py")
    if not os.path.isfile(script):
        print(f"\n(no rosters/_validate.py at {script} — skipping the post-apply "
              "cross-check; this is expected in a selftest fixture, never in a real run)")
        return 0
    proc = subprocess.run([sys.executable, script, "--cross"],
                           cwd=ROSTERS, capture_output=True, text=True)
    print("\n=== rosters/_validate.py --cross ===")
    print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip())
    return proc.returncode


REGEN_COMMANDS = [
    "python3 design/Jawa/worldbuilding/biomes/rosters/_validate.py --cross",
    "python3 design/Jawa/worldbuilding/biomes/rosters/_consolidate.py   "
    "# recomputes _global.json's reserve_for_events from the edited per-biome rosters "
    "— never hand-edit _global.json",
    "python3 design/Jawa/worldbuilding/review/gen_fauna_assignment_sheet.py",
    "python3 design/Jawa/worldbuilding/review/gen_flora_assignment_sheet.py",
]


def print_regen_commands():
    print("\n=== regeneration commands to run next ===")
    for c in REGEN_COMMANDS:
        print(f"  {c}")


# ═══════════════════════════════════════════════════════════════ main

def sheet_kind_of(path: str) -> str:
    base = os.path.basename(path)
    if "flora" in base:
        return "flora"
    return "fauna"


def html_for(decisions_path: str) -> str:
    return decisions_path[:-len(".decisions.json")] + ".html" \
        if decisions_path.endswith(".decisions.json") else decisions_path + ".html"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("decisions", nargs="*", default=None,
                     help="decisions.json file(s); default: both fauna and flora sheets")
    ap.add_argument("--apply", action="store_true", help="write rosters + worklists")
    args = ap.parse_args(argv)

    paths = args.decisions or DEFAULT_DECISIONS
    overall_rc = RC_OK
    any_written = False

    for path in paths:
        if not os.path.isfile(path):
            print(f"(skip) {path}: no such file")
            continue
        try:
            doc = load_decisions(path)
        except Refuse as exc:
            print(str(exc))
            overall_rc = max(overall_rc, RC_NO_SIDECAR)
            continue

        sheet_stem = os.path.basename(path).replace(".decisions.json", "")
        kind = sheet_kind_of(path)
        items = load_items(html_for(path))
        roster_index = load_roster_index()
        plan = build_plan(doc, kind, items, roster_index, os.path.basename(path))
        print_report(plan)

        if plan.errors:
            overall_rc = max(overall_rc, RC_UNRESOLVED)
            continue

        if args.apply:
            written = apply_all(plan, roster_index, sheet_stem)
            any_written = True
            print(f"\n  wrote {len(written)} file(s):")
            for w in written:
                print(f"    {w}")

    if args.apply and any_written:
        rc = run_validate_cross()
        if rc:
            overall_rc = max(overall_rc, RC_VALIDATOR)
        print_regen_commands()

    return overall_rc


if __name__ == "__main__":
    sys.exit(main())

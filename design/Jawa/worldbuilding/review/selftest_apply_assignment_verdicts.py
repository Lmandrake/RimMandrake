#!/usr/bin/env python3
"""selftest_apply_assignment_verdicts.py — synthetic end-to-end proof for
apply_assignment_verdicts.py against the 2026-09-09 rulings schema.

Builds a tiny fixture sheet + decisions + roster set in a tmp dir (never touches
the real design/Jawa/worldbuilding/review or rosters/ files) and proves:
  1. an unstamped decisions file is refused
  2. a Move verdict whose note names no unambiguous biome refuses the WHOLE
     apply for that file — nothing partial is written
  3. a clean apply (Move + Out) round-trips onto the roster JSON correctly
  4. an out-of-scope key on a roster doc (something this tool does not know
     about) survives a write untouched

    python3 selftest_apply_assignment_verdicts.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_PATH = os.path.join(HERE, "apply_assignment_verdicts.py")

spec = importlib.util.spec_from_file_location("apply_assignment_verdicts", MODULE_PATH)
av = importlib.util.module_from_spec(spec)
spec.loader.exec_module(av)

FAILURES = []


def check(cond, label, detail=""):
    mark = "✅" if cond else "❌"
    print(f"{mark} {label}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(label)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)


def make_items_html(path, items):
    body = json.dumps(items)
    html = (
        '<html><body>\n'
        '<script id="CONFIG" type="application/json">{"sheetId": "fixture"}</script>\n'
        f'<script id="ITEMS" type="application/json">{body}</script>\n'
        '</body></html>\n'
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)


def make_roster(sheet, defnames, fauna_rows, extra_top=None):
    doc = {
        "sheet": sheet, "defNames": defnames, "tiles": 100,
        "authored": "2026-09-09", "law_sources": ["fixture"],
        "fauna": fauna_rows, "evictions": [], "flora": [], "flora_purged": [],
        "fish": {"ruling": "fixture — no fish", "list": []},
    }
    if extra_top:
        doc.update(extra_top)
    return doc


def stamped_decisions(rows_dict, saved_by="review-sheet-sidecar", write_count=3):
    return {
        "sheet": "fauna_assignment_register", "posture": "blacklist",
        "postureMeaning": "fixture", "criterion": "fixture",
        "generatedBy": "fixture", "generatedFrom": "fixture", "invented": [],
        "savedBy": saved_by, "writeCount": write_count, "savedAt": "2026-09-10T00:00:00Z",
        "decidedCount": len(rows_dict), "decisions": rows_dict,
    }


def run():
    tmp = tempfile.mkdtemp(prefix="applier_selftest_")
    try:
        rosters_dir = os.path.join(tmp, "rosters")
        review_dir = os.path.join(tmp, "review")
        os.makedirs(rosters_dir)
        os.makedirs(review_dir)

        # ── fixture rosters: two real biomes + a target biome for Move ──────
        write_json(os.path.join(rosters_dir, "biome_a.json"), make_roster(
            "biome_a", ["BiomeA"],
            [{"def": "Critterus", "commonality": 0.8, "action": "keep",
              "band": "small", "law": "fixture law A"},
             {"def": "Wanderus", "commonality": 0.5, "action": "keep",
              "law": "fixture law A2"}],
            extra_top={"unrelated_field": "should-survive-untouched"}))
        write_json(os.path.join(rosters_dir, "biome_b.json"), make_roster(
            "biome_b", ["BiomeB"], []))

        av.ROSTERS = rosters_dir
        av.REVIEW = review_dir

        # ══════════════════════════════════════════════ test 1: unstamped refusal
        unstamped_path = os.path.join(review_dir, "unstamped.decisions.json")
        write_json(unstamped_path, stamped_decisions(
            {"fauna:biome_a:Critterus": {"decision": "in", "prefill": "in", "note": ""}},
            saved_by=None, write_count=None))
        refused = False
        try:
            av.load_decisions(unstamped_path)
        except av.Refuse:
            refused = True
        check(refused, "unstamped decisions file is refused")

        # ══════════════════════════════════════ test 2: missing Move target refuses whole apply
        make_items_html(os.path.join(review_dir, "movebad.html"), [
            {"id": "fauna:biome_a:Critterus", "label": "Critterus", "group": "biome_a"},
            {"id": "fauna:biome_a:Wanderus", "label": "Wanderus", "group": "biome_a"},
        ])
        movebad_path = os.path.join(review_dir, "movebad.decisions.json")
        write_json(movebad_path, stamped_decisions({
            "fauna:biome_a:Critterus": {"decision": "in", "prefill": "in", "note": ""},
            "fauna:biome_a:Wanderus": {"decision": "move", "prefill": "in",
                                       "note": "no biome named here at all"},
        }))
        before_a = json.load(open(os.path.join(rosters_dir, "biome_a.json")))
        before_b = json.load(open(os.path.join(rosters_dir, "biome_b.json")))

        doc = av.load_decisions(movebad_path)
        items = av.load_items(av.html_for(movebad_path))
        roster_index = av.load_roster_index()
        plan = av.build_plan(doc, "fauna", items, roster_index, "movebad.decisions.json")
        check(bool(plan.errors), "unresolvable Move target is flagged as a blocking error")
        # main() must refuse to write anything for this file
        rc = av.main([movebad_path, "--apply"])
        check(rc != av.RC_OK, "main() returns a non-zero exit for the unresolved Move")
        after_a = json.load(open(os.path.join(rosters_dir, "biome_a.json")))
        after_b = json.load(open(os.path.join(rosters_dir, "biome_b.json")))
        check(after_a == before_a, "biome_a.json unchanged after the refused apply")
        check(after_b == before_b, "biome_b.json unchanged after the refused apply")

        # ══════════════════════════════════════════════ test 3: clean apply round-trips
        make_items_html(os.path.join(review_dir, "clean.html"), [
            {"id": "fauna:biome_a:Critterus", "label": "Critterus", "group": "biome_a"},
            {"id": "fauna:biome_a:Wanderus", "label": "Wanderus", "group": "biome_a"},
        ])
        clean_path = os.path.join(review_dir, "clean.decisions.json")
        write_json(clean_path, stamped_decisions({
            "fauna:biome_a:Critterus": {
                "decision": "move", "prefill": "in", "note": "belongs in biome b now",
                "sizeBin": "medium", "sizeBinPrefill": "small",
                "art": "improve", "artPrefill": "keep"},
            "fauna:biome_a:Wanderus": {"decision": "out", "prefill": "in",
                                       "note": "doesn't fit after all"},
        }))
        rc = av.main([clean_path, "--apply"])
        a_after = json.load(open(os.path.join(rosters_dir, "biome_a.json")))
        b_after = json.load(open(os.path.join(rosters_dir, "biome_b.json")))
        check(not any(r["def"] == "Critterus" for r in a_after["fauna"]),
              "Critterus removed from biome_a after Move")
        check(any(r["def"] == "Critterus" for r in b_after["fauna"]),
              "Critterus landed in biome_b after Move")
        check(not any(r["def"] == "Wanderus" for r in a_after["fauna"]),
              "Wanderus removed from biome_a after Out")
        check(any(e["def"] == "Wanderus" for e in a_after.get("evictions", [])),
              "Wanderus recorded in biome_a's evictions after Out")
        size_path = os.path.join(review_dir, "clean.size_rescale_worklist.json")
        check(os.path.isfile(size_path), "size-rescale worklist file was written")
        if os.path.isfile(size_path):
            rows = json.load(open(size_path))
            row = next((r for r in rows if r["defName"] == "Critterus"), None)
            check(row is not None and row["direction"] == "grow",
                  "Critterus's rescale row says grow (small -> medium)")
        art_path = os.path.join(review_dir, "clean.art_queue.json")
        check(os.path.isfile(art_path), "art-queue file was written")

        # ══════════════════════════════════════════ test 4: out-of-scope keys survive
        check(a_after.get("unrelated_field") == "should-survive-untouched",
              "an unrelated top-level key on the roster survives a write untouched")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    run()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        sys.exit(1)
    print("\nALL GREEN")
    sys.exit(0)

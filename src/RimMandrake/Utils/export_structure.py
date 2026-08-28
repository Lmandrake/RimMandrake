#!/usr/bin/env python3
"""
export_structure.py - a live map rect becomes a rimplace BuildPlan JSON.

    python.exe src/RimMandrake/Utils/export_structure.py --rect 83,59,86,133 \\
        --out world/_ship/exports/corrosion_halo.plan.json

THE CONCEPT (owner, 2026-08-28): one IR, two writers, one placer. Lua templates
compile INTO a BuildPlan; this exports a built structure OUT to the same
BuildPlan - so anything built or tweaked in-game inherits rimplace's whole
offline toolchain (render, lint, diff, contract check) and reinserts through the
same compiled jawa/* calls. Replaces the ShipLayoutDefV2 save->reinsert cycle as
the canonical path; gravship_layout.py remains the V2 ADAPTER for the Gravship
Exporter mod ecosystem (V2 carries no paint, so it is lossy - ours is not).

IDENTITY-GRADE, CAPTURE-FIRST (owner's ruling): every row records quality, paint,
hit points, faction, container CONTENTS, bills and storage settings via
jawa/export_things - even though today's placer replays only def/stuff/rot/paint/
terrain. Nothing recorded is ever lost; replay fidelity grows later, and the
plan's meta.identityUnreplayed lists exactly what was captured but not yet
replayable so nobody mistakes a rebuild for a restoration.

Reads: jawa/export_things (identity rows) - needs the 240-surface companion
DEPLOYED (down window; a companion registers at startup only) -
jawa/get_terrain_layers (top/foundation/colour), jawa/get_roof_batch.

⚠️ python.exe, never python3 - the bridge binds Windows loopback.
⚠️ Blueprints, frames, motes and filth are not exported; pawns only with --pawns
   (recorded for the record; the placer never spawns pawns from a plan).
"""
import argparse
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rimbridge_client import RimBridge, resolve_endpoint     # noqa: E402
from rimplace.core import BuildPlan                          # noqa: E402

ROW_BAND = 12        # get_terrain_layers rows per call, respecting its cell cap


def unwrap(r):
    if isinstance(r, dict) and r.get("content"):
        try:
            return json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r or {}


IDENTITY_KEYS = ("quality", "hitPoints", "maxHitPoints", "stackCount",
                 "faction", "plantToGrow", "contents", "bills", "storage")
SKIP_DEF_PREFIX = ("Blueprint_", "Frame_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rect", required=True, help="x,z,w,h on the live map")
    ap.add_argument("--out", required=True, help="path for the BuildPlan JSON")
    ap.add_argument("--pawns", action="store_true", help="record pawns too (never replayed)")
    ap.add_argument("--label", default=None)
    args = ap.parse_args()
    x0, z0, w, h = [int(v) for v in args.rect.split(",")]

    plan = BuildPlan({"template": "live-export", "rect": [x0, z0, w, h],
                      "label": args.label,
                      "identityUnreplayed": ["quality", "hitPoints", "contents",
                                             "bills", "storage", "faction"]})

    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token, timeout=900.0) as rb:
        # -- things, identity-grade ----------------------------------------
        t = unwrap(rb.call("jawa/export_things", {
            "rect": args.rect, "includePawns": bool(args.pawns),
            "limit": 100000}))
        if not t.get("success"):
            print("export_things REFUSED: %s" % t)
            return 2
        if t.get("truncated"):
            print("REFUSING to write a partial export: export_things truncated")
            return 2
        for row in t.get("things") or []:
            d = row.get("def") or ""
            if d.startswith(SKIP_DEF_PREFIX):
                continue
            extra = {k: row[k] for k in IDENTITY_KEYS if row.get(k) is not None}
            plan.add_thing(d, row["x"], row["z"], row.get("rot") or 0,
                           row.get("stuff"), role=None,
                           paint=row.get("paint"),
                           extra=extra or None)

        # -- terrain: top + foundation + floor colour, banded by rows ------
        for zb in range(z0, z0 + h, ROW_BAND):
            hh = min(ROW_BAND, z0 + h - zb)
            g = unwrap(rb.call("jawa/get_terrain_layers", {
                "rect": "%d,%d,%d,%d" % (x0, zb, w, hh), "limit": w * hh}))
            if not g.get("success"):
                print("get_terrain_layers REFUSED at band z=%d: %s" % (zb, g))
                return 2
            for c in g.get("cells") or []:
                cx, cz = c.get("x"), c.get("z")
                if c.get("top"):
                    plan.set_terrain(cx, cz, c["top"])
                if c.get("foundation"):
                    plan.set_foundation(cx, cz, c["foundation"])
                if c.get("color"):
                    plan.set_floor_color(cx, cz, c["color"])

        # -- roof ----------------------------------------------------------
        r = unwrap(rb.call("jawa/get_roof_batch", {"rect": args.rect,
                                                   "limit": w * h}))
        for c in (r.get("cells") or r.get("roofs") or []):
            if c.get("roof") or c.get("def"):
                plan.set_roof(c.get("x"), c.get("z"), c.get("roof") or c.get("def"))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(plan.to_json())
    n_id = sum(1 for th in plan.things if th.extra)
    print("exported %d things (%d carrying identity payload), %d floor cells, "
          "%d foundation, %d coloured, %d roofed -> %s"
          % (len(plan.things), n_id, len(plan.terrain), len(plan.foundation),
             len(plan.floor_color), len(plan.roof), args.out))
    print("reinsert:  rimplace's compile_calls(plan) — paint included; identity "
          "payload replays as the placer grows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

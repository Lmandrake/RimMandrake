"""rimplace - run a Lua structure template offline and see the house.

    render   run a template and DRAW it            (the debug loop)
    minrect  how big a canvas does it need?        (asked without building)
    lint     run it and report what is wrong
    calls    emit the exact jawa/* bridge calls
    verify   check every defName against the live def dump
    export   write the flat runtime plan (for GenStep_RimplacePlan)
    selftest prove the engine still works

Needs the lupa Lua runtime:
    python3 -m venv ~/.local/venvs/rimlua
    ~/.local/venvs/rimlua/bin/pip install lupa
    ~/.local/venvs/rimlua/bin/python -m rimplace render <template>
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from rimplace.core import Palette, Rect                       # noqa: E402
from rimplace.luaenv import (TemplateError, TemplateTooSmall,  # noqa: E402
                             declared_min_rect, run_template)
from rimplace.plan import (calls_summary, compile_calls,      # noqa: E402
                           compile_flat, lint, render)
from game_paths import DEF_DUMP                               # noqa: E402
import dump_projection                                        # noqa: E402

REPO = _HERE.parents[3]
TEMPLATES = REPO / "design" / "Jawa" / "templates"
# 🔴 `defs.sqlite` lives at the DefDump ROOT and outlives any one capture
# (DUMP_STORAGE_LAYOUT_RULING_1), so a raw `DUMP_ROOT / "defs.sqlite"` path
# finds the file even when it describes an OLDER capture than the one
# currently live - measured 2026-09-03: the db on disk right now describes
# 2026-09-02T19:36:08Z while the newest capture is 2026-09-04T02-23-44Z.
# `dump_projection.sqlite_path()` is the project's one fingerprint-checked
# resolver (see its `_sqlite_describes`) - it returns None on a stale or
# unusable db, and that must map to UNMEASURED here, never a silent pass
# against yesterday's defs.
DUMP_SQLITE = dump_projection.sqlite_path(str(DEF_DUMP))
DUMP_SQLITE = Path(DUMP_SQLITE) if DUMP_SQLITE else None


def _resolve_template(name: str) -> Path:
    p = Path(name)
    if p.exists():
        return p
    for cand in (TEMPLATES / name, TEMPLATES / f"{name}.lua"):
        if cand.exists():
            return cand
    raise SystemExit(f"template not found: {name} (looked in {TEMPLATES})")


def _params(a) -> dict:
    return {
        "faction": a.faction, "rooms": a.rooms, "occupants": a.occupants,
        "wealth": a.wealth, "techLevel": a.tech, "defended": a.defended,
        "condition": a.condition, "climate": a.climate,
        "temperature_c": a.temperature, "seed": a.seed,
    }


def _build(a):
    path = _resolve_template(a.template)
    pal_data = json.loads((_HERE / "palette.json").read_text(encoding="utf-8"))
    palette = Palette(pal_data, a.faction, a.tech, a.wealth)
    rect = Rect(*[int(v) for v in a.rect.split(",")])
    try:
        return path, run_template(path, rect, _params(a), palette, a.seed)
    except TemplateTooSmall as e:
        # A size refusal is its own exit code (3), so a caller batching templates
        # can tell "this needs a bigger canvas" from "this template is broken".
        raise SystemExit(f"CANVAS TOO SMALL: {e}\n"
                         f"  ask first:  rimplace minrect {path.stem}")
    except TemplateError as e:
        raise SystemExit(f"TEMPLATE ERROR: {e}")


# --------------------------------------------------------------------------- #
def _verified_defs(plan) -> set[str] | None:
    """Look every defName up in the live dump. Returns None if the dump is not
    readable (missing, corrupt, or stale against the current capture) - and
    the caller then reports UNMEASURED rather than passing."""
    if DUMP_SQLITE is None:
        return None
    want = plan.defnames()
    con = sqlite3.connect(f"file:{DUMP_SQLITE}?mode=ro", uri=True)
    try:
        # validate the query shape against a known answer first
        n = con.execute("SELECT COUNT(*) FROM defs WHERE def_name='Human'").fetchone()[0]
        if n == 0:
            return None          # query shape is wrong; report UNMEASURED, never pass
        qs = ",".join("?" * len(want))
        rows = con.execute(
            f"SELECT DISTINCT def_name FROM defs WHERE def_name IN ({qs})",
            tuple(want)).fetchall()
        return {r[0] for r in rows}
    except sqlite3.Error:
        return None
    finally:
        con.close()


def _paint_violations(plan):
    """-> (violations, unmeasured_reason). Every painted thing and every coloured
    floor must sit on a def the game will actually paint (def.building.paintable /
    TerrainDef.isPaintable) — jawa/paint_building refuses these live, but a
    generated template should fail OFFLINE, before it costs a game round.

    🔑 The flag ships in the dump only from the 2026-08-28 RimDefDump build on.
    A dump with no 'paintable' key at all is OLDER than the flag, and the honest
    answer is UNMEASURED, never a pass and never a spray of false violations."""
    painted = {t.defName for t in plan.things if t.paint}
    floored = {plan.terrain[c] for c in plan.floor_color if c in plan.terrain}
    if not painted and not floored:
        return [], None
    if DUMP_SQLITE is None:
        return [], "dump unreadable"
    con = sqlite3.connect(f"file:{DUMP_SQLITE}?mode=ro", uri=True)
    try:
        n = con.execute(
            "SELECT COUNT(*) FROM def_flags WHERE key='paintable'").fetchone()[0]
        if n == 0:
            return [], ("this capture predates the paintable flag "
                        "(RimDefDump 2026-08-28) — redeploy the dumper and reload")
        want = sorted(painted | floored)
        qs = ",".join("?" * len(want))
        ok = {r[0] for r in con.execute(
            "SELECT DISTINCT d.def_name FROM defs d "
            "JOIN def_flags f ON f.def_id = d.id "
            f"WHERE f.key='paintable' AND f.value='true' AND d.def_name IN ({qs})",
            tuple(want))}
        out = []
        for d in sorted(painted - ok):
            out.append(f"'{d}' is painted but the game will not paint it "
                       "(building.paintable is false or absent)")
        for d in sorted(floored - ok):
            out.append(f"floor '{d}' is coloured but TerrainDef.isPaintable is false")
        return out, None
    except sqlite3.Error:
        return [], "dump unreadable"
    finally:
        con.close()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rimplace", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["render", "minrect", "lint", "calls",
                                        "verify", "export", "selftest"])
    ap.add_argument("template", nargs="?", default="dwelling")
    ap.add_argument("--rect", default="0,0,16,12", help="x,z,w,h")
    ap.add_argument("--faction", default="Jawa_IndigenousTribes")
    ap.add_argument("--rooms", type=int, default=2)
    ap.add_argument("--occupants", type=int, default=2)
    ap.add_argument("--wealth", default="modest")
    ap.add_argument("--tech", default="Industrial")
    ap.add_argument("--defended", default="none")
    ap.add_argument("--condition", default="kept")
    ap.add_argument("--climate", default="auto")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--roof", action="store_true", help="show roof in render")
    ap.add_argument("--json", action="store_true", help="emit the BuildPlan")
    ap.add_argument("--out", default=None,
                    help="export: file path to write the flat plan to")
    a = ap.parse_args(argv)

    if a.command == "selftest":
        from rimplace.selftest import run_selftest
        return run_selftest()

    if a.command == "minrect":
        # ⭐ The only command that answers WITHOUT building. `--template all` sweeps
        # the library, which is what a re-export or a TileMutatorDef wiring pass
        # actually needs: one table of every footprint floor in the repo.
        names = ([p for p in sorted(TEMPLATES.glob("*.lua"))]
                 if a.template == "all" else [_resolve_template(a.template)])
        for p in names:
            try:
                need = declared_min_rect(p, _params(a))
            except TemplateError as e:
                print(f"  {p.stem:<28} ERROR  {e}")
                continue
            print(f"  {p.stem:<28} {'%dx%d' % need if need else 'none declared'}")
        if a.template == "all":
            print("\n  'none declared' means the template declares no floor — either it is "
                  "genuinely\n  size-agnostic, or nobody has written its `min_rect(params)` yet. "
                  "It is NOT a\n  promise that any rect works, and a declared floor is a "
                  "minimum, not a guarantee.")
        return 0

    path, plan = _build(a)

    if a.command == "render":
        print(render(plan, show_roof=a.roof))
        if a.json:
            print(plan.to_json())
        findings = lint(plan)
        errs = [f for f in findings if f.level == "ERROR"]
        if errs:
            print(f"\n  ⚠ {len(errs)} error(s) - run `lint` for detail")
        return 0

    if a.command == "lint":
        vd = _verified_defs(plan)
        findings = lint(plan, vd)
        if vd is None:
            print("  UNMEASURED: def dump not readable; defName checks SKIPPED")
        print(f"  {path.name}: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1 if any(f.level == "ERROR" for f in findings) else 0

    if a.command == "calls":
        calls = compile_calls(plan, faction=a.faction)
        print(calls_summary(calls))
        print()
        for c in calls:
            p = {k: v for k, v in c["params"].items() if k != "_dryRun"}
            s = json.dumps(p)
            print(f"  {c['tool']:<26} {s[:150]}{'…' if len(s) > 150 else ''}")
        return 0

    if a.command == "verify":
        vd = _verified_defs(plan)
        want = sorted(plan.defnames())
        if vd is None:
            print(f"  UNMEASURED - no fresh, readable defs.sqlite for capture\n    {DEF_DUMP}")
            print("  This is not a pass. Nothing was checked.")
            return 2
        missing = [d for d in want if d not in vd]
        print(f"  {len(want)} distinct defName(s) in the plan; "
              f"{len(want) - len(missing)} found, {len(missing)} MISSING")
        for d in missing:
            print(f"    MISSING  {d}")
        viols, unmeasured = _paint_violations(plan)
        if unmeasured:
            print(f"  PAINT: UNMEASURED — {unmeasured}. Not a pass.")
        for v in viols:
            print(f"    UNPAINTABLE  {v}")
        if viols:
            print(f"  {len(viols)} paint target(s) the game will refuse.")
        return 1 if (missing or viols) else (2 if unmeasured else 0)

    if a.command == "export":
        if not a.out:
            raise SystemExit("export needs --out <path>")
        flat = compile_flat(plan)
        out_path = Path(a.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(flat, encoding="utf-8")
        print(f"  wrote {out_path} ({len(flat.splitlines())} line(s))")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""naming_lint.py — the three-tier naming gate (design/NAMING_SCHEME_PLAN.md §6).

Warn-mode by default: reports violations, exits 0. --strict exits 1 on any
violation (the future hard gate; wiring into deploy is NAMING_SCHEME_EXECUTION_1's
job — this script deliberately touches nothing else).

Checks per mod folder (any dir with About/About.xml under src/):
  packageId   matches  mandrake.(rm|rsw|rut).<name>
  defNames    carry the mod's tier prefix (RM_/RSW_/RUT_) — a defName whose
              rename-map row says new==old is a sanctioned exception
  namespace   matches  <Tier>.<ModName>
  folder      parent dir is the tier dir (src/<Tier>/)
  leak        shipping XML/C# must not reference exempt tooling (JawaBench, "jawa/")

Tier per mod comes from infrastructure/state/naming_rename_map.csv (mod rows);
a mod absent from the map lints as UNASSIGNED (every check skipped except leak).
"""
import argparse, csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
MAP = ROOT / "infrastructure/state/naming_rename_map.csv"

TIER_PREFIX = {"RimMandrake": "RM_", "RimStarWars": "RSW_", "RimUtinni": "RUT_"}
TIER_PID = {"RimMandrake": "rm", "RimStarWars": "rsw", "RimUtinni": "rut"}
PID_RX = re.compile(r"^mandrake\.(rm|rsw|rut)\.[a-z0-9]+$")
LEAK_RX = re.compile(r'JawaBench|"jawa/')


def load_map():
    tiers, sanctioned = {}, set()
    if not MAP.exists():
        return tiers, sanctioned
    with MAP.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["kind"] == "mod":
                tiers[Path(row["old"]).name] = row["tier"]
                tiers[Path(row["new"]).name] = row["tier"]
            elif row["kind"] == "def" and row["old"] == row["new"]:
                sanctioned.add(row["old"])
    return tiers, sanctioned


def lint_mod(mod: Path, tier: str, sanctioned: set):
    v = []
    about = (mod / "About" / "About.xml").read_text(encoding="utf-8", errors="replace")
    pid = (re.search(r"<packageId>([^<]+)</packageId>", about) or [None, "MISSING"])[1]
    if tier == "UNASSIGNED":
        v.append(("mod", "not in rename map — tier UNASSIGNED"))
    elif tier == "SPLIT":
        v.append(("mod", "marked SPLIT — Phase 3 triage owed"))
    else:
        want = f"mandrake.{TIER_PID[tier]}."
        if not (PID_RX.match(pid) and pid.startswith(want)):
            v.append(("packageId", f"{pid} != {want}<name>"))
        if mod.parent.name != tier:
            v.append(("folder", f"src/{mod.parent.name}/ != src/{tier}/"))
        prefix = TIER_PREFIX[tier]
        bad = 0
        for x in mod.rglob("*.xml"):
            if x.name == "About.xml":
                continue
            for d in re.findall(r"<defName>([A-Za-z0-9_\-]+)</defName>",
                                x.read_text(encoding="utf-8", errors="replace")):
                if not d.startswith(prefix) and d not in sanctioned:
                    bad += 1
        if bad:
            v.append(("defName", f"{bad} defs lack {prefix}"))
        for c in mod.rglob("*.cs"):
            if "/obj/" in str(c):
                continue
            for ns in re.findall(r"^\s*namespace\s+([A-Za-z0-9_.]+)",
                                 c.read_text(encoding="utf-8", errors="replace"), re.M):
                # ruled 2026-08-31: namespaces nest under the RimMandrake root —
                # RimMandrake.<Mod> / RimMandrake.StarWars.<Mod> / RimMandrake.Utinni.<Mod>
                want = {"RimMandrake": "RimMandrake.",
                        "RimStarWars": "RimMandrake.StarWars.",
                        "RimUtinni": "RimMandrake.Utinni."}.get(tier, f"{tier}.")
                if not ns.startswith(want):
                    v.append(("namespace", f"{ns} != {want}{mod.name}"))
                    break
            break
    for x in list(mod.rglob("*.xml")) + [c for c in mod.rglob("*.cs") if "/obj/" not in str(c)]:
        if x.name == "About.xml":
            continue
        if LEAK_RX.search(x.read_text(encoding="utf-8", errors="replace")):
            v.append(("leak", f"references exempt tooling: {x.relative_to(mod)}"))
            break
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true", help="exit 1 on any violation")
    ap.add_argument("--quiet", action="store_true", help="summary only")
    args = ap.parse_args()

    tiers, sanctioned = load_map()
    mods = sorted(p.parent.parent for p in SRC.glob("*/*/About/About.xml"))
    total, dirty = 0, 0
    for mod in mods:
        v = lint_mod(mod, tiers.get(mod.name, "UNASSIGNED"), sanctioned)
        total += len(v)
        if v:
            dirty += 1
            if not args.quiet:
                print(f"{mod.relative_to(ROOT)}  [{tiers.get(mod.name, 'UNASSIGNED')}]")
                for kind, msg in v:
                    print(f"  {kind:10} {msg}")
    print(f"\nnaming_lint: {len(mods)} mods, {dirty} non-compliant, "
          f"{total} violations ({'STRICT' if args.strict else 'warn mode'})")
    sys.exit(1 if args.strict and total else 0)


if __name__ == "__main__":
    main()

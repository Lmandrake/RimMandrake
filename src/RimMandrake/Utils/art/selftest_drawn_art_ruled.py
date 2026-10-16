#!/usr/bin/env python3
"""selftest_drawn_art_ruled — every picture the game DRAWS for an approved creature must be a picture he ruled on.

Why (GIZKA_FROG, 2026-10-15): the owner approved the biped Gizka at least seven times (2026-09-17 x2, 10-04, 10-05,
10-06, greentide, 10-11) and the game still drew the forbidden frog. Every approval rewrote the PRIMARY body
graphic (Gizka_*), but the PawnKindDef also carried `alternateGraphics` -> GizkaW at alternateGraphicChance 0.8, so
80% of spawned gizkas drew GizkaW, whose east/north were still the frog. The art ledger's slot scan
(artledger.scan_def_slots / GRAPHIC_ROLE) has no role for `alternateGraphics/li`, so GizkaW had "(none in our defs)"
slots: no sheet ruling could bind to it, and no tool ever compared it with the approved art.

The check, for every PawnKindDef in src/ (parsed XML, never text-matched):
  * primary = lifeStages body/female graphic texPaths; alternates = alternateGraphics/li/texPath, drawn at
    alternateGraphicChance (engine default 0.5);
  * a creature is APPROVED when the owner has a keep/pick/approve ruling on its subject, or one of its primary
    pictures is owner-protected;
  * for an approved creature, every alternate PNG (resolved in the def's own mod Textures/) must be byte-identical to
    one of its primary pictures, or owner-protected / owner-ruled by sha. Anything else is a picture the game shows
    on most spawns that he never saw next to his approval.

Known debts are listed in drawn_art_ruled_baseline.json (a ratchet: a NEW violation fails, a fixed one must be removed
from the baseline). Limitation: alternateGraphics added by a Patch are not seen.

Usage: python3 selftest_drawn_art_ruled.py [--report] [--write-baseline]
"""
from __future__ import annotations

import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
BASELINE = HERE / "drawn_art_ruled_baseline.json"
FACINGS = ("south", "east", "north", "west")
APPROVE = {"keep", "pick", "approve", "A", "B", "C", "D", "E", "F", "G", "H"}


def mod_root(f: Path) -> Path | None:
    for p in f.parents:
        if p.name in ("Defs",):
            return p.parent
    return None


def pngs(mod: Path, tp: str) -> dict:
    out = {}
    for fc in FACINGS:
        p = mod / "Textures" / f"{tp}_{fc}.png"
        if p.is_file():
            out[fc] = p
    single = mod / "Textures" / f"{tp}.png"
    if not out and single.is_file():
        out["single"] = single
    return out


def scan_kinds(root: Path) -> list[dict]:
    kinds = []
    for f in sorted(root.rglob("*.xml")):
        if "/Defs/" not in f.as_posix():
            continue
        try:
            tree = ET.parse(f)
        except (ET.ParseError, OSError):
            continue
        for k in tree.getroot().iter("PawnKindDef"):
            dn = (k.findtext("defName") or "").strip()
            alts = [(li.findtext("texPath") or "").strip() for li in k.findall("alternateGraphics/li")]
            alts = [a for a in alts if a]
            if not dn or not alts:
                continue
            prim = []
            for tag in ("bodyGraphicData", "femaleGraphicData"):
                for g in k.findall(f"lifeStages/li/{tag}"):
                    t = (g.findtext("texPath") or "").strip()
                    if t and t not in prim:
                        prim.append(t)
            try:
                chance = float(k.findtext("alternateGraphicChance") or 0.5)
            except ValueError:
                chance = 0.5
            kinds.append({"def": dn, "race": (k.findtext("race") or "").strip(), "file": f, "mod": mod_root(f),
                          "primary": prim, "alternates": sorted(set(alts)), "chance": chance})
    return kinds


def owner_ruled(idx, sha: str) -> bool:
    return bool(idx.protected(sha)) or any(r.get("by") == "owner" and r.get("verdict") not in ("redo", "reject", "cut")
                                           for r in idx.rulings_by_sha.get(sha, []))


def approved(idx, L, kind: dict, prim_shas: set) -> bool:
    keys = {L.subject_key(kind["def"]), L.subject_key(kind["race"] or kind["def"])}
    for r in idx.subject_rulings(keys):
        if r.get("by") == "owner" and (r.get("verdict") in APPROVE or r.get("raw_verdict") in APPROVE):
            return True
    return any(idx.protected(s) for s in prim_shas)


def violations(kinds, idx, L, sha_of) -> list[dict]:
    out = []
    for k in kinds:
        if k["mod"] is None:
            continue
        prim_shas = {sha_of(p) for tp in k["primary"] for p in pngs(k["mod"], tp).values()}
        if not prim_shas or not approved(idx, L, k, prim_shas):
            continue
        for tp in k["alternates"]:
            if tp in k["primary"]:
                continue
            for fc, p in sorted(pngs(k["mod"], tp).items()):
                s = sha_of(p)
                if s in prim_shas or owner_ruled(idx, s):
                    continue
                out.append({"key": f"{k['def']}|{tp}|{fc}", "def": k["def"], "texPath": tp, "facing": fc,
                            "chance": k["chance"], "sha": s})
    return out


def fixture_check(L) -> list[str]:
    """The Gizka shape must be caught; the fixed shape must pass."""
    fails = []
    with tempfile.TemporaryDirectory() as td:
        mod = Path(td) / "M"
        (mod / "Defs").mkdir(parents=True)
        (mod / "Textures" / "X").mkdir(parents=True)
        (mod / "Defs" / "k.xml").write_text(
            "<Defs><PawnKindDef><defName>FX_Beast</defName><race>FX_Beast</race>"
            "<alternateGraphicChance>0.8</alternateGraphicChance><alternateGraphics><li><texPath>X/BeastW</texPath>"
            "</li></alternateGraphics><lifeStages><li><bodyGraphicData><texPath>X/Beast</texPath></bodyGraphicData>"
            "</li></lifeStages></PawnKindDef></Defs>")
        for fc in ("east", "north", "south"):
            (mod / "Textures" / "X" / f"Beast_{fc}.png").write_bytes(b"good-" + fc.encode())
            (mod / "Textures" / "X" / f"BeastW_{fc}.png").write_bytes(b"frog-" + fc.encode())

        class FakeIdx:
            rulings_by_sha = {}
            def protected(self, sha):
                return []
            def subject_rulings(self, keys):
                return [{"by": "owner", "verdict": "keep"}]

        sha_of = lambda p: L.sha256_file(p)
        kinds = scan_kinds(Path(td))
        v = violations(kinds, FakeIdx(), L, sha_of)
        if len(v) != 3:
            fails.append(f"fixture: frog alternate at 80% should give 3 violations, got {len(v)}")
        for fc in ("east", "north", "south"):
            (mod / "Textures" / "X" / f"BeastW_{fc}.png").write_bytes(b"good-" + fc.encode())
        v = violations(scan_kinds(Path(td)), FakeIdx(), L, sha_of)
        if v:
            fails.append(f"fixture: alternate identical to the approved primary should pass, got {len(v)}")
    return fails


def main(argv) -> int:
    import artledger as L
    fails = fixture_check(L)
    idx = L.Index()
    cache = {}
    sha_of = lambda p: cache.setdefault(p, L.sha256_file(p))
    v = violations(scan_kinds(L.src_root()), idx, L, sha_of)
    keys = {x["key"] for x in v}
    if "--write-baseline" in argv:
        BASELINE.write_text(json.dumps({"why": "known approved-creature alternates the owner never ruled on; "
                                        "a ratchet — remove a row once fixed", "keys": sorted(keys)}, indent=1) + "\n")
        print(f"baseline written: {len(keys)} row(s)")
        return 0
    base = set(json.loads(BASELINE.read_text())["keys"]) if BASELINE.is_file() else set()
    new, fixed = sorted(keys - base), sorted(base - keys)
    if "--report" in argv:
        for x in v:
            print(f"  {x['def']}: {int(x['chance'] * 100)}% of spawns draw {x['texPath']} {x['facing']} "
                  f"({x['sha'][:12]}) — never ruled, not the approved primary{'' if x['key'] in base else '  NEW'}")
    for k in new:
        fails.append(f"NEW unruled alternate on an approved creature: {k}")
    for k in fixed:
        fails.append(f"baseline row now passes — remove it from {BASELINE.name}: {k}")
    print(f"drawn_art_ruled: {len(v)} violation(s), {len(base)} baselined, {len(new)} new, {len(fixed)} stale")
    for f in fails:
        print("FAIL", f)
    if not fails:
        print("PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

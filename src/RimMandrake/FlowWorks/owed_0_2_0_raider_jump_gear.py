#!/usr/bin/env python3
"""owed_0_2_0_raider_jump_gear.py - FlowWorks 0.2.0 acceptance test: raiders are dressed from jump gear by capability.

RED by design until 0.2.0 builds it, so it is named outside run_selftests' `selftest*.py` discovery (a red test there
turns every full run red). The 0.2.0 build that makes it green renames it selftest_flowworks_raider_jump_gear.py.

Item RIMMANDRAKE_FIND_STAR_WARS_JUMP_PACK_ELSE_MAKE_ONE_BLACKSTAR_WEARS (next-version entry in
design/concepts/FlowWorks/version/next_version/README.md). Owner, 2026-11-24 about 11:15 PM PST (ledger note on
RIMMANDRAKE_RULE_RAIDER_JUMP_PACKS_THE_SHIP_LIST_CUTS): "The jump pack should NOT be cut for FlowWorks, it was a
RimStarWars decision/setting specific decision." FlowWorks is setting-free, so the dressing patch must not name one def.

The contract (RM_Patch_Raid_JumpPacks in Source/Superdeep/RM_RaiderTrench.cs, and a pure pick in RM_RaiderTrenchMath):
  A1  the patch names no ThingDef by a string literal (today: GetNamedSilentFail("Apparel_PackJump"), so with the
      vanilla pack cut by Cherry Picker and a Star Wars jetpack loaded, no raider is dressed: RED for that reason)
  A2  it builds its candidates from the loaded ThingDefs (DefDatabase<ThingDef>), apparel only, by a verb whose class is
      Verb_Jump or a subclass of it (a cut def is not in the DefDatabase, so it is never a candidate)
  A3  an empty candidate list dresses nobody and returns (a game with no jump gear at all)
  A4  each raider's pick comes from the pure rule RM_RaiderTrenchMath.PickJumpGear, and a candidate the raider cannot
      wear without dropping something is skipped for the next one (no shield belt is swapped out)
  B   (--dotnet) SelfTest cases RaiderTrench_jump_gear_* : at least 3 run and all pass. The cases owed: an index is always
      inside the list or -1; an empty list gives -1; the pick is deterministic per pawn id; over many ids every candidate
      is picked (a second jump apparel is used, not only the first).

Exit 0 PASS, 1 FAIL (a contract line is broken), 2 COULD NOT LOOK (a file or the SelfTest build cannot be read).
  --src PATH   check this RM_RaiderTrench.cs instead of the repo's (used to show the test can go green)
  --dotnet     also run the SelfTest cases (Windows dotnet through winbuild.py)
Seen RED on the base commit 7d3ad544ee (A1, A2, A3, A4 fail); GREEN on a planted capability patch (--src, --math);
RED again with the literal put back into that patch; COULD NOT LOOK (exit 2) on a missing file. 2026-11-24, offline only.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src/RimMandrake/FlowWorks/Source/Superdeep/RM_RaiderTrench.cs"
MATH = REPO / "src/RimMandrake/FlowWorks/Source/Superdeep/RM_RaiderTrenchMath.cs"


def patch_body(text: str):
    m = re.search(r"public static class RM_Patch_Raid_JumpPacks\b(.*?)(?=\n\t(?:///|\[)|\Z)", text, re.S)
    return m.group(1) if m else None


def contract(src_text: str, math_text: str):
    body = patch_body(src_text)
    if body is None:
        return None, ["the class RM_Patch_Raid_JumpPacks is not in the source"]
    bad = []
    lit = re.findall(r'GetNamed(?:SilentFail)?\s*\(\s*"([^"]+)"', body)
    if lit:
        bad.append("A1 the dressing patch names a def by literal: " + ", ".join(lit))
    if not re.search(r"DefDatabase<ThingDef>\.AllDefs", body):
        bad.append("A2 the candidates are not read from the loaded ThingDefs (DefDatabase<ThingDef>.AllDefs...)")
    elif not re.search(r"IsApparel", body) or not re.search(r"typeof\(Verb_Jump\)\.IsAssignableFrom|is Verb_Jump|IsSubclassOf\(typeof\(Verb_Jump\)\)", body):
        bad.append("A2 the candidates are not filtered by apparel and a Verb_Jump verb")
    if not re.search(r"\.Count\s*==\s*0\)?\s*\)?\s*\{?\s*return", body) and not re.search(r"\.Count\s*>\s*0", body):
        bad.append("A3 an empty candidate list is not met by a return")
    if "PickJumpGear" not in body or not re.search(r"public static int PickJumpGear\s*\(", math_text):
        bad.append("A4 the pick is not RM_RaiderTrenchMath.PickJumpGear (pure, offline-testable)")
    elif not re.search(r"CanWearWithoutDroppingAnything", body):
        bad.append("A4 a candidate the raider cannot wear without dropping something is not skipped")
    return body, bad


def dotnet() -> int:
    b = subprocess.run([sys.executable, str(REPO / "src/RimMandrake/Utils/winbuild.py"),
                        "src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj"],
                       capture_output=True, text=True, cwd=str(REPO))
    if b.returncode != 0:
        print("COULD NOT LOOK  B: the SelfTest did not build:\n" + b.stdout[-800:] + b.stderr[-400:])
        return 2
    exe = next((p for p in (Path.home() / ".dotnet/dotnet", Path("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe"),
                            Path("/mnt/c/Program Files/dotnet/dotnet.exe")) if p.exists()), None)
    d = Path("/mnt/d/ClaudeWork/rimmandrake/build/FlowWorks/src/RimMandrake/FlowWorks/Source/SelfTest")
    dll = d / "bin/Release/net8.0/RimMandrakeFlowWorks.SelfTest.dll"
    if exe is None or not dll.exists():
        print("COULD NOT LOOK  B: no dotnet or no built SelfTest dll")
        return 2
    r = subprocess.run([str(exe), str(dll.relative_to(d)), "--only", "RaiderTrench_jump_gear_*"],
                       cwd=str(d), capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith(("ok", "FAIL", "fail"))]
    print("\n".join(lines))
    ok = sum(1 for l in lines if l.startswith("ok"))
    if r.returncode != 0 or ok < 3:
        print(f"FAIL  B: {ok} RaiderTrench_jump_gear_* case(s) passed, 3 or more owed (rc={r.returncode})")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src", help="check this RM_RaiderTrench.cs instead of the repo's")
    ap.add_argument("--math", help="check this RM_RaiderTrenchMath.cs instead of the repo's")
    ap.add_argument("--dotnet", action="store_true", help="also run the SelfTest cases RaiderTrench_jump_gear_*")
    a = ap.parse_args()
    try:
        s = Path(a.src or SRC).read_text(encoding="utf-8")
        m = Path(a.math or MATH).read_text(encoding="utf-8")
    except OSError as e:
        print(f"COULD NOT LOOK  {e}")
        return 2
    _, bad = contract(s, m)
    for b in bad:
        print("FAIL  " + b)
    rc = 1 if bad else 0
    if a.dotnet:
        d = dotnet()
        rc = 1 if 1 in (rc, d) else d
    if rc == 0:
        print("PASS  raiders are dressed from loaded jump gear by capability, never one named def")
    return rc


if __name__ == "__main__":
    sys.exit(main())

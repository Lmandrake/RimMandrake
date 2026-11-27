#!/usr/bin/env python3
"""RIMMANDRAKE_FIX_STEEL_BRIDGE_UNSET_STYLE_TAKES_LAST_CHOSEN: a bridge built with no style chosen takes the default look.

Seen 2026-11-25 on the walk map (stations 52, 53, 70, 78 and 84 came out Futuristic): _Shared/StylePicker/StylePickerCore
remembered one pick per ThingDef for the whole process, so a pick on one button (a proof's, or the player's in an earlier
save) reached every later build of that def. The fix: StylePickMemory keys a pick to the button that made it and to the
game it was made in. The behaviour is the C# cases StylePick_* (SelfTest/StylePickMemoryChecks.cs, run by
src/RimMandrake/Utils/selftest_flowworks_stock.py, seen red on the planted parent behaviour 2026-11-26); this checks that
the core reads that memory, that every assembly compiles it, and the live script's verdict (northstar/unset_bridge_look_live.py).

CAN IT FAIL: each wire taken out of a copy of the source must go red (run at the end).
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RM = HERE.parent
FILES = {
    "core": RM / "_Shared" / "StylePicker" / "StylePickerCore.cs",
    "memory": RM / "_Shared" / "StylePicker" / "StylePickMemory.cs",
    "fw": HERE / "Source" / "RimMandrake_FlowWorks.csproj",
    "gss": RM / "GimmeSomeSlack" / "Source" / "RimMandrake_GimmeSomeSlack.csproj",
    "st": HERE / "Source" / "SelfTest" / "RimMandrakeFlowWorks.SelfTest.csproj",
    "program": HERE / "Source" / "SelfTest" / "Program.cs",
    "checks": HERE / "Source" / "SelfTest" / "StylePickMemoryChecks.cs",
    "proofs": HERE / "Source" / "Pits" / "Suspension" / "RM_SuspensionProofs.cs",
}
LINK = 'Include="..\\..\\_Shared\\StylePicker\\StylePickMemory.cs"'


def body(src: str, sig: str) -> str:
    i = src.find(sig)
    if i < 0:
        return ""
    j = src.find("{", i)
    depth = 0
    for k in range(j, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
    return ""


def checks(t: dict) -> list[tuple[str, bool]]:
    core, mem = t["core"], t["memory"]
    resolve = body(core, "public ThingStyleDef Resolve(Designator_Build des)")
    pick = body(core, "public void Pick(Designator_Build des, string look)")
    for_button = body(mem, "public string ForButton(object button, object game)")
    remember = body(mem, "public void Remember(object button, object def, string look, object game)")
    return [
        ("the memory is engine-free", bool(mem) and "using Verse" not in mem and "using RimWorld" not in mem),
        ("the core keeps no per-def pick table", "Dictionary<ThingDef, string> lastPicked" not in core
         and "private readonly StylePickMemory lastPicked = new StylePickMemory();" in core),
        ("Resolve reads this button's own pick in this game",
         "resolve(lastPicked.ForButton(des, Current.Game), DefaultLook" in resolve),
        ("Pick remembers the button and the game", "lastPicked.Remember(des, d, look, Current.Game);" in pick),
        ("a pick is read only by its own button", "byButton.TryGetValue(button" in for_button and "byDef" not in for_button),
        ("a pick is read only in its own game", "SameGame(e, game)" in for_button
         and "ReferenceEquals(e.Game.Target, game)" in mem and "new WeakReference(game)" in remember),
        ("FlowWorks and Gimme Some Slack compile the memory", LINK in t["fw"] and LINK in t["gss"]),
        ("the SelfTest compiles the memory and its checks", 'StylePickMemory.cs" Link=' in t["st"]
         and 'Include="StylePickMemoryChecks.cs"' in t["st"] and "StylePickMemoryChecks.Run(Case);" in t["program"]),
        ("the C# cases name the reported fault", "StylePick_unset_button_takes_default_not_last_pick" in t["checks"]
         and "StylePick_pick_before_load_does_not_reach_the_loaded_game" in t["checks"]),
        ("the live proof builds the second bridge from a new, unpicked button",
         "public static string ProofUnsetLook(string arg)" in t["proofs"]
         and "Machinery.PipeLook.Core.Pick(first, picked);" in t["proofs"]
         and "second.TryDesignate(CellRect.FromLimits(c3, c4)" in t["proofs"]),
        ("the live proof shows it can see a stored look: the first bridge reads its own pick",
         'Read(CellRect.FromLimits(c1, c2), picked, out int own, null)' in body(t["proofs"], "public static string ProofUnsetLook(string arg)")
         and '" own=" + own + "/" + ownParts' in t["proofs"]),
    ]


def live_verdicts() -> list[tuple[str, bool]]:
    spec = importlib.util.spec_from_file_location("unset_live", HERE / "northstar" / "unset_bridge_look_live.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    v = lambda s: m.verdict(s)[:2]  # noqa: E731
    return [
        ("live: ok=True with parts reads PASS",
         v("UNSETLOOK ok=True default=Scrapper picked=Industrial own=4/4 parts=4 looks=Scrapper reason=-") == ("PASS", "MOD")),
        ("live: the first bridge's pick on the second reads FAIL",
         v("UNSETLOOK ok=False default=Scrapper picked=Industrial own=4/4 parts=4 looks=Industrial reason=-") == ("FAIL", "MOD")),
        ("live: the first bridge not in its own pick reads FAIL, never a blind PASS",
         v("UNSETLOOK ok=True default=Scrapper picked=Industrial own=0/4 parts=4 looks=Scrapper reason=-") == ("FAIL", "MOD")),
        ("live: a line with no own= reading is a harness fault, not a pass",
         v("UNSETLOOK ok=True default=Scrapper picked=Industrial parts=4 looks=Scrapper reason=-") == ("UNMEASURED", "HARNESS")),
        ("live: no part built is UNMEASURED, not a pass",
         v("UNSETLOOK ok=False default=Scrapper picked=Industrial own=0/0 parts=0 looks= reason=-") == ("UNMEASURED", "SITE")),
        ("live: a refused build is UNMEASURED",
         v("UNSETLOOK ok=False default=Scrapper picked=Industrial own=0/0 parts=0 looks= reason=no_pit") == ("UNMEASURED", "SITE")),
        ("live: a refusal line is a harness fault", v("REFUSED: arg must be ...") == ("UNMEASURED", "HARNESS")),
        ("live: no answer is a harness fault", v(None) == ("UNMEASURED", "HARNESS")),
    ]


MUTANTS = [
    ("core", "resolve(lastPicked.ForButton(des, Current.Game), DefaultLook", "resolve(lastPicked.LastForDef(d, Current.Game), DefaultLook"),
    ("core", "lastPicked.Remember(des, d, look, Current.Game);", "lastPicked.Remember(d, d, look, Current.Game);"),
    ("memory", "return SameGame(e, game) ? e.Look : null;\n        }\n\n        /// <summary>State read", "return e.Look;\n        }\n\n        /// <summary>State read"),
    ("gss", LINK, 'Include="gone.cs"'),
    ("program", "StylePickMemoryChecks.Run(Case);", ""),
]


def main() -> int:
    t = {k: p.read_text(encoding="utf-8") if p.exists() else "" for k, p in FILES.items()}
    rows = checks(t) + live_verdicts()
    bad = [n for n, ok in rows if not ok]
    for n, ok in rows:
        print("%s  %s" % ("ok  " if ok else "FAIL", n))
    for key, a, b in MUTANTS:
        if a not in t[key]:
            print("FAIL  mutant anchor missing in %s: %r" % (key, a[:60]))
            bad.append("anchor " + key)
            continue
        m = dict(t)
        m[key] = t[key].replace(a, b, 1)
        if all(ok for _n, ok in checks(m)):
            print("FAIL  mutant not caught: %s %r" % (key, a[:60]))
            bad.append("mutant " + key)
    print("%s unset bridge look: %d checks, %d mutants" % ("PASS" if not bad else "FAIL", len(rows), len(MUTANTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

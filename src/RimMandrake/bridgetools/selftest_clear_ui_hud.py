#!/usr/bin/env python3
"""selftest_clear_ui_hud.py - clear_ui must hide the colonist bar, and must give the HUD back.

CELL_RECT_SHOT_FIX_COLONIST_BAR_PHOTOBOMBS: clear_ui closed dev windows and the selection,
yet tall rect shots still carried the colonist bar across their top.

1. ENGINE (the game's own IL, via ilprobe - no recall):
   - MapInterface.MapInterfaceOnGUI_BeforeMainTabs calls ScreenshotModeHandler.FiltersCurrentEvent
     and its branch jumps OVER the ColonistBar.ColonistBarOnGUI call: screenshot mode hides the bar.
   - ColonistBar.Visible reads no preference (so there is no other switch to flip).
   - UIRoot.UIRootOnGUI calls ScreenshotModesOnGUI with no branch skipping it: the lease's
     postfix runs every OnGUI event, so the lease always expires.
2. COMPANION SOURCE:
   - clear_ui takes hideHud defaulting to true and goes through JawaBenchHudLease.Take;
   - the lease patches ScreenshotModesOnGUI with a postfix that switches the flag off only
     when the lease owns it, and Take never claims a flag that was already on.
No game assembly on this machine = the engine half is UNMEASURED, said aloud, and the test fails.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ILPROBE = os.path.join(REPO, "src", "RimMandrake", "Utils", "ilprobe")
GAME_DLL = ("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/"
            "RimWorldWin64_Data/Managed/Assembly-CSharp.dll")
TOOLS = os.path.join(HERE, "JawaBench.BridgeTools")

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def il(type_name, method):
    out = subprocess.run([sys.executable, "il.py", type_name, method], cwd=ILPROBE,
                         capture_output=True, text=True, timeout=300).stdout
    rows = []
    for line in out.splitlines():
        m = re.match(r"\s+IL_([0-9a-f]{4}):\s+(\S+)\s*(.*)$", line)
        if m:
            rows.append((int(m.group(1), 16), m.group(2), m.group(3).strip()))
    return rows


def offset_of(rows, needle):
    hits = [off for off, _, arg in rows if needle in arg]
    return hits[0] if hits else None


# ---- 1. engine -----------------------------------------------------------------
if not os.path.exists(GAME_DLL):
    check("engine IL readable", False, "UNMEASURED: no " + GAME_DLL)
else:
    rows = il("MapInterface", "MapInterfaceOnGUI_BeforeMainTabs")
    check("ilprobe sees MapInterfaceOnGUI_BeforeMainTabs", len(rows) > 20, len(rows))
    f = offset_of(rows, "ScreenshotModeHandler::get_FiltersCurrentEvent")
    c = offset_of(rows, "ColonistBar::ColonistBarOnGUI")
    br = [r for r in rows if f is not None and c is not None and f < r[0] < c and r[1].startswith("brtrue")]
    target = int(br[0][2].replace("IL_", ""), 16) if br else None
    check("screenshot mode branches over ColonistBarOnGUI",
          bool(br) and target is not None and target > c, (f, c, br))

    vis = il("ColonistBar", "get_Visible")
    check("ilprobe sees ColonistBar.Visible", len(vis) > 3, len(vis))
    check("ColonistBar.Visible reads no preference",
          not any(("Prefs::" in a or "PlaySettings" in a) for _, _, a in vis), vis)

    root = il("UIRoot", "UIRootOnGUI")
    s = offset_of(root, "ScreenshotModeHandler::ScreenshotModesOnGUI")
    skips = [r for r in root if s is not None and r[0] < s and r[1].startswith("b")
             and r[2].startswith("IL_") and int(r[2][3:], 16) > s]
    check("UIRootOnGUI calls ScreenshotModesOnGUI unconditionally", s is not None and not skips, (s, skips))

# ---- 2. companion source ---------------------------------------------------------
terrain = open(os.path.join(TOOLS, "JawaBenchTerrainTools.cs"), encoding="utf-8").read()
start = terrain.find("public static async Task<object> ClearUi(")
body = terrain[start:terrain.find("ConfigureAwait(false);", start)]
check("ClearUi found", start > 0)
check("hideHud defaults to true", re.search(r"bool hideHud = true", body) is not None)
check("ClearUi takes the lease", "JawaBenchHudLease.Take(" in body)
# The call must run on the DEFAULT path: guarded by a plain `if (hideHud)` (no negation,
# no extra conjunct), its result is what hudHidden reports, it is the only Take, and
# nothing in the body overwrites hideHud before it.
code = re.sub(r"//[^\n]*", "", body)
guarded = re.search(r"if\s*\(\s*hideHud\s*\)\s*hudHidden\s*=\s*JawaBenchHudLease\.Take\(\s*leaseSeconds\s*,", code)
check("default clear_ui runs Take under a bare `if (hideHud)`", guarded is not None)
check("Take is called exactly once in ClearUi", code.count("JawaBenchHudLease.Take(") == 1,
      code.count("JawaBenchHudLease.Take("))
check("ClearUi never reassigns hideHud",
      re.search(r"(?<![=!<>])\bhideHud\s*=(?!=)", code.replace("bool hideHud = true", "")) is None)
check("hideHud tool parameter advertises DefaultValue = true",
      re.search(r'DefaultValue = true\)\]\s*bool hideHud = true', code) is not None)
check("ClearUi reports hudHidden", "hudHidden," in body)

lease = open(os.path.join(TOOLS, "JawaBenchHudLease.cs"), encoding="utf-8").read()
check("lease targets ScreenshotModeHandler.ScreenshotModesOnGUI",
      'TargetType = "Verse.ScreenshotModeHandler"' in lease
      and 'TargetMethod = "ScreenshotModesOnGUI"' in lease)
check("lease patches a postfix", "postfix: new HarmonyMethod" in lease)
post = lease[lease.find("private static void Postfix("):]
check("postfix only switches off a flag it owns",
      re.search(r"if \(!Owned \|\|", post) is not None and "__instance.Active = false" in post)
take = lease[lease.find("internal static bool Take("):lease.find("private static void Postfix(")]
check("Take claims ownership only when the flag was off",
      re.search(r"if \(!wasActive\)\s*\{\s*handler\.Active = true;\s*Owned = true;", take) is not None)

print("%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)

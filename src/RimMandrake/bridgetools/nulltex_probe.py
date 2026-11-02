#!/usr/bin/env python3
r"""nulltex_probe.py - prove who passes a null texture to GUI.DrawTexture
(WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR).

Player.log carries "null texture passed to GUI.DrawTexture" with no stack. The JawaBench tool
`jawa/nulltex_probe` (JawaBenchNullTextureProbe.cs) records the managed stack of every such call.

  --offline   no game needed. Decompiles the INSTALLED binaries with ilspycmd.exe and checks:
              O1 Unity's internal 12-arg GUI.DrawTexture holds the warning, under Repaint + image==null,
                 and the probe's TargetArgs name exactly that signature, with the parameter 'image';
              O2 the probe is wired: Install() called from JawaBenchInit, tool jawa/nulltex_probe declared;
              O3 the offline suspect still stands: RimThemes' UI_BackgroundMain_Patch draws
                 VideoPlayer.texture with no null check, and VBE's DrawBG reads texture.width first
                 (a null there throws, it cannot log this warning).
  --live A1   game up, bridge reachable: the probe is installed and has recorded >=1 null call with a
              managed caller. 0 calls is INCONCLUSIVE (exit 1): this session drew no null texture yet.
  --live A2   the most frequent caller is in aRandomKiwi.RimThemes (the offline prediction). Prints the
              real caller either way, so a refutation names its replacement.

FINDINGS SO FAR (offline, 2026-11-02; decompiled copies in D:\ClaudeWork\rimmandrake\scratch\nulltex):
- Vanilla UIRoot_Entry.DoMainMenu calls UIMenuBackgroundManager.background.BackgroundOnGUI() on EVERY
  Entry-state OnGUI, long events included, so a world load or quicktest started from the menu keeps
  drawing the menu background under the loading screen.
- RimThemes (aRandomKiwi.RimThemes, workshop 1668983184) prefixes UI_BackgroundMain.BackgroundOnGUI and,
  once its VideoPlayer is "playing", draws Utils.CurrentMainAnimatedBg.texture unguarded; LoaderGM does
  the same with its own loader VideoPlayer. VideoPlayer.texture is null until a frame is decoded.
- The active theme is ours: Config/Mod_1668983184_RimThemes.xml curTheme = "mandrake.rut.shell§Utinni
  Shell" (MenuShell), which ships animated UI_BackgroundMain.BGPlanet*.webm, enabling that video path.
- VBE (2775017012) also draws VideoPlayer textures, but DrawBG reads texture.width first: excluded.
- The load-to-load spread (19,519 vs 77) is UNEXPLAINED offline; the probe's byProgramState and
  duringLongEvent split says when the nulls land.

Exit 0 = the clause holds, 1 = it does not (or cannot be shown), 2 = usage/instrument error.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROBE_CS = ROOT / "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchNullTextureProbe.cs"
INIT_CS = ROOT / "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchInit.cs"

STEAM = Path("/mnt/c/Program Files (x86)/Steam/steamapps")
IMGUI = STEAM / "common/RimWorld/RimWorldWin64_Data/Managed/UnityEngine.IMGUIModule.dll"
RIMTHEMES = STEAM / "workshop/content/294100/1668983184/1.6/Assemblies/RimThemes.dll"
VBE = STEAM / "workshop/content/294100/2775017012/1.6/Assemblies/VBE.dll"
ILSPY = Path("/mnt/c/Users/Mandrake/.dotnet/tools/ilspycmd.exe")

WARNING = "null texture passed to GUI.DrawTexture"
SIG12 = ("Rect position, Texture image, ScaleMode scaleMode, bool alphaBlend, float imageAspect, "
         "Color leftColor, Color topColor, Color rightColor, Color bottomColor, Vector4 borderWidths, "
         "Vector4 borderRadiuses, bool drawSmoothCorners")
TYPES12 = ["Rect", "Texture", "ScaleMode", "bool", "float", "Color", "Color", "Color", "Color",
           "Vector4", "Vector4", "bool"]


def winpath(p: Path) -> str:
    return subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True, check=True).stdout.strip()


def decompile_type(dll: Path, type_name: str) -> str:
    if not dll.is_file():
        raise FileNotFoundError(dll)
    r = subprocess.run([str(ILSPY), "-t", type_name, winpath(dll)], capture_output=True, text=True,
                       timeout=300)
    if r.returncode != 0 or f"class {type_name.rsplit('.', 1)[-1]}" not in r.stdout:
        raise RuntimeError(f"ilspycmd could not decompile {type_name} from {dll}: {r.stderr.strip()[:300]}")
    return r.stdout


def method_body(src: str, header_re: str) -> str:
    """Text of the first method whose header matches, up to its balanced closing brace."""
    m = re.search(header_re, src)
    if not m:
        return ""
    i = src.index("{", m.end())
    depth = 0
    for j in range(i, len(src)):
        depth += {"{": 1, "}": -1}.get(src[j], 0)
        if depth == 0:
            return src[m.start():j + 1]
    return ""


def offline() -> int:
    fails = []

    def check(ok: bool, label: str, detail: str = "") -> None:
        print(("PASS " if ok else "FAIL ") + label + (f"  ({detail})" if detail else ""))
        if not ok:
            fails.append(label)

    gui = decompile_type(IMGUI, "UnityEngine.GUI")
    body = method_body(gui, r"internal static void DrawTexture\(" + re.escape(SIG12) + r"\)")
    check(bool(body), "O1a Unity has the internal 12-arg GUI.DrawTexture", SIG12[:60] + "...")
    check(WARNING in body and "image == null" in body and "EventType.Repaint" in body,
          "O1b it alone writes the warning, under Repaint and image == null")
    check(gui.count(WARNING) == 1, "O1c the warning text occurs once in UnityEngine.GUI",
          f"{gui.count(WARNING)} occurrence(s)")
    probe = PROBE_CS.read_text()
    m = re.search(r"TargetArgs\s*=\s*\{(.*?)\};", probe, re.S)
    got = re.findall(r"typeof\((\w+)\)", m.group(1)) if m else []
    check(got == TYPES12, "O1d the probe's TargetArgs are that signature", " ".join(got))
    check(re.search(r"static void Prefix\(Texture image\)", probe) is not None,
          "O1e the prefix binds Harmony parameter 'image'")
    check("JawaBenchNullTextureProbe.Install()" in INIT_CS.read_text(), "O2a Install() is called from JawaBenchInit")
    check('"jawa/nulltex_probe"' in probe, "O2b the tool jawa/nulltex_probe is declared")

    rt = decompile_type(RIMTHEMES, "aRandomKiwi.RimThemes.UI_BackgroundMain_Patch")
    unguarded = re.search(r"GUI\.DrawTexture\(\w+, Utils\.CurrentMainAnimatedBg\.texture,", rt)
    check(unguarded is not None and "CurrentMainAnimatedBg.texture != null" not in rt
          and "(Object)(object)Utils.CurrentMainAnimatedBg.texture" not in rt,
          "O3a RimThemes UI_BackgroundMain_Patch draws VideoPlayer.texture with no null check")
    vbe = decompile_type(VBE, "VBE.Utils")
    draw = method_body(vbe, r"public static void DrawBG\(Texture texture\)")
    rect = method_body(vbe, r"public static Rect GetBGRect\(Texture texture\)")
    check("GetBGRect(texture)" in draw and "texture.width" in rect,
          "O3b VBE.DrawBG dereferences texture.width first (a null throws, never this warning)")
    print("OFFLINE " + ("PASS" if not fails else f"FAIL: {len(fails)} check(s)"))
    return 0 if not fails else 1


def live(clause: str) -> int:
    sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
    import rimbridge_client as rb  # noqa: E402
    host, port, token = rb.resolve_endpoint()
    s = rb.RimBridge(host=host, port=port, token=token, timeout=45.0)
    s.connect()
    r = s.call("jawa/nulltex_probe", {"action": "get", "top": 5}) or {}
    if isinstance(r, dict) and r.get("content"):
        r = json.loads(r["content"][0]["text"])
    out = Path(os.environ.get("NULLTEX_OUT", tempfile.gettempdir())) / "nulltex_probe_live.json"
    out.write_text(json.dumps(r, indent=1))
    print(f"probe reading -> {out}")
    if not r.get("installed"):
        print(f"FAIL {clause}: probe NOT installed ({r.get('installError') or r.get('error') or r})")
        return 1
    n = int(r.get("nullCalls") or 0)
    callers = r.get("byCaller") or []
    for c in callers[:5]:
        print(f"  {c['count']:>7}  {c['caller']}")
    if n == 0 or not callers:
        print(f"INCONCLUSIVE {clause}: installed, armed={r.get('armed')}, 0 null calls since install "
              "- this session drew no null texture after the first jawa/ call (load a save or a quicktest "
              "from the main menu with RimThemes + MenuShell active, then re-read)")
        return 1
    top = callers[0]["caller"]
    if clause == "A1":
        ok = not top.startswith("<no managed caller")
        print(("PASS" if ok else "FAIL") + f" A1: {n} null call(s); top caller {top}")
        return 0 if ok else 1
    ok = top.startswith("aRandomKiwi.RimThemes.")
    print(("PASS" if ok else "FAIL") + f" A2: top caller {top} ({callers[0]['count']} of {n})"
          + ("" if ok else " - the RimThemes prediction is REFUTED; the line above names the real caller"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--offline", action="store_true")
    g.add_argument("--live", choices=["A1", "A2"])
    a = ap.parse_args()
    try:
        return offline() if a.offline else live(a.live)
    except (FileNotFoundError, RuntimeError, subprocess.SubprocessError, OSError) as e:
        print(f"INSTRUMENT ERROR: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())

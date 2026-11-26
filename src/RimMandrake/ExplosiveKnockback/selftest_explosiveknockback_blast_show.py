#!/usr/bin/env python3
"""T_BLAST_SHOW_OFFLINE: the offline check of Explosive Knockback 0.2.0's blast show
(design/specs/2026-11-24-knockback-blast-show/design.md; bars blast_show_* in design/concepts/ExplosiveKnockback/record.json).

Grown from proof/absorb_blast_show_check.py. Two halves:

1. STRUCTURE, per part of the show (read from the mod's own defs, C# and Textures, nothing run): our own flecks with our
   own art, the hook on Explosion.StartExplosion, one saved on/off per part (default on, saved, drawn, reset), the shake
   slider, the prefix writing nothing but the three visual fields (the show changes no damage, radius, cell or throw), the
   scar defs at the kernel's sizes with rain and time and cleaning, and no donor mod named.
2. THE KERNEL: Source/SelfTestShow compiles the shipped RM_KnockbackShowPlan.cs and reads a generated range of blasts with
   the bars' own checks (its range and what it leaves out are declared at the top of its Program.cs).

Every line prints PASS or FAIL with its worst value, its limit and its case count. A part that is not built yet fails by
name; the look of each part is the live scene sc_blast_show's and the art judge's, never this script's.
Exit 0 = every line passes; 1 = a line fails; 2 = UNMEASURED (no Windows dotnet on this machine: the kernel half could not
run, which is not a pass).

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_blast_show.py
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_str  # noqa: E402  (data root: rmpaths.py)
import fcntl
import glob
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

EK = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(EK, "Source")
STAGE = os.environ.get("WINBUILD_ROOT", rm_str("build")) + "/ExplosiveKnockbackShowSelfTest"
DOTNET = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]
SHIPPED = ("RM_KnockbackMath.cs", "RM_KnockbackShowPlan.cs")
# the donor mods the show replaces (design §1.1): nothing of theirs is named, copied or pointed at
DONORS = r"Keshash|ExtraExplosionEffects|Fleck_EEE|nephlite|advexplosions|Mote_AdvExplosion|blues\.forge|ForgedSplash"
# vanilla textures a part may use by design: the ripple is drawn by the game's own distortion shader on its own
# distortion textures (design §3.6, "Art: none (vanilla texture)")
VANILLA_OK = {"RM_KnockbackBlastRipple": ("Things/Mote/Black", "/Things/Mote/PsychicDistortionCurrents", "/Things/Mote/PsycastNoise")}

SCAR_WIDTHS = ("3", "5", "7", "10", "14", "20")     # RM_KnockbackShowPlan.ScarDrawSizes, read from the kernel below
SCAR_NAMES = ["RM_KnockbackBlast%s_%sWide" % (k, w) for k in ("Crater", "Scorch") for w in SCAR_WIDTHS]
# part -> (switch field, the defs it owns (kind, defName), the code it must hold (label, regex over the show's C#))
PARTS = {
    "fire_and_flash": ("showFireAndFlash",
                       [("FleckDef", "RM_KnockbackBlastFlash"), ("FleckDef", "RM_KnockbackBlastFireball"),
                        ("FleckDef", "RM_KnockbackBlastSpark"), ("FleckDef", "RM_KnockbackBlastDirt"),
                        ("FleckDef", "RM_KnockbackBlastStone")],
                       [("vanilla visuals handed over", r"doVisualEffects\s*=\s*false"),
                        ("the splash kept", r"FleckMaker\.WaterSplash\(")]),
    "screen_shake": ("showScreenShake", [],
                     [("our shake added", r"shaker\.DoShake\("), ("trauma rule", r"ShakeToAdd\("), ("vanilla shake zeroed", r"screenShakeFactor\s*=\s*0")]),
    "air_ripple": ("showAirRipple", [("FleckDef", "RM_KnockbackBlastRipple")], [("ripple drawn", r"RM_KnockbackBlastRipple")]),
    "crater_scar": ("showCraterScars",
                    [("ThingDef", n) for n in SCAR_NAMES],
                    [("vanilla mark dropped", r"preExplosionSpawnSingleThingDef\s*=\s*null"),
                     ("scar laid", r"FilthMaker\.TryMakeFilth\(")]),
    "smoke": ("showSmoke", [("FleckDef", "RM_KnockbackBlastSmoke")], [("smoke drawn", r"RM_KnockbackBlastSmoke")]),
    "soot_on_things": ("showSootOnThings", [], [("charred paint", r"RM_FE_Charred"), ("paint laid", r"ChangePaint\(")]),
    "soot_on_pawns": ("showSootOnPawns", [("HediffDef", "RM_KnockbackSoot")], [("soot hediff", r"RM_KnockbackSoot")]),
}
OUT = []


def line(ok, ident, what, worst, limit, cases):
    OUT.append(ok)
    print("%s %s: %s | worst %s | limit %s | cases %d" % ("PASS" if ok else "FAIL", ident, what, worst, limit, cases))


def read(p):
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def defs():
    """-> {(kind, defName): element} of every def in the mod's Defs/."""
    out = {}
    for p in sorted(glob.glob(os.path.join(EK, "Defs", "**", "*.xml"), recursive=True)):
        for el in ET.parse(p).getroot():
            n = el.findtext("defName")
            if n:
                out[(el.tag, n)] = el
    return out


def show_source():
    """The C# of the show: every .cs in Source/ that is not a proof file (proof code never ships in the release DLL)."""
    files = [p for p in sorted(glob.glob(os.path.join(SRC, "*.cs"))) if "Proof" not in os.path.basename(p)]
    return {os.path.basename(p): read(p) for p in files}


def tex_ok(name, el):
    """-> (ok, why): every texture the def draws (graphicData and each randomGraphics entry) is our own PNG under the mod's
    Textures/; the ripple alone may use the game's own distortion textures (design §3.6)."""
    paths = [x.text or "" for x in el.iter("texPath")]
    if name in VANILLA_OK:
        allowed = VANILLA_OK[name]
        used = paths + [x.text or "" for x in el.iter() if x.tag.startswith("_") and x.tag.endswith("Tex")]
        bad = [u for u in used if u not in allowed]
        return (not bad and bool(paths)), ("vanilla engine textures %s" % used) if not bad else "not the design's vanilla textures: %s" % bad
    if not paths:
        return False, "no texPath"
    owed = []
    for tex in paths:
        hits = glob.glob(os.path.join(EK, "Textures", tex + ".png")) + glob.glob(os.path.join(EK, "Textures", tex, "*.png")) \
            + glob.glob(os.path.join(EK, "Textures", tex + "_*.png"))
        if not hits:
            owed.append(tex)
    return not owed, ("art owed: no PNG under Textures/ for %s" % ", ".join(owed)) if owed else "%d texture(s) present" % len(paths)


def setting_ok(src, field, kind="bool", default="true"):
    """A setting is real when it is declared with its default, saved with that default, drawn and reset."""
    mod = src.get("RM_KnockbackMod.cs", "")
    window = mod.split("public void DoWindowContents", 1)[-1].split("public static void ResetFields", 1)[0]
    reset = mod.split("public static void Reset()", 1)[-1]
    lit = default if kind != "float" else default.rstrip("f") + "f"
    miss = []
    if not re.search(r"public static %s %s\s*=\s*%s\s*;" % (kind, field, re.escape(lit)), mod):
        miss.append("declared %s = %s" % (kind, lit))
    if not re.search(r'Scribe_Values\.Look\(ref %s, "%s", %s\)' % (field, field, re.escape(lit)), mod):
        miss.append("saved with its default")
    if not re.search(r"\b%s\b" % field, window):
        miss.append("drawn")
    if not re.search(r"RimMandrakeExplosiveKnockbackSettings\.%s\s*=\s*%s\s*;" % (field, re.escape(lit)), reset):
        miss.append("reset")
    return not miss, miss


def structure():
    D, src = defs(), show_source()
    code = "\n".join(src.values())
    for part, (switch, owned, needles) in PARTS.items():
        miss = []
        ok, why = setting_ok(src, switch)
        if not ok:
            miss.append("switch %s not %s" % (switch, ", ".join(why)))
        for kind, name in owned:
            el = D.get((kind, name))
            if el is None:
                miss.append("no %s %s" % (kind, name))
                continue
            if kind in ("FleckDef", "ThingDef"):
                tok, twhy = tex_ok(name, el)
                if not tok:
                    miss.append("%s: %s" % (name, twhy))
        for label, rx in needles:
            if not re.search(rx, code):
                miss.append("no code: %s" % label)
        line(not miss, "B_PART_" + part.upper(), "%s built: switch, defs, own art, code" % part,
             "; ".join(miss) if miss else "all present", "nothing missing", len(owned) + len(needles) + 1)

    ok, why = setting_ok(src, "showShakeStrength", "float", "1")
    mod = src.get("RM_KnockbackMod.cs", "")
    slider = re.search(r"showShakeStrength\s*=\s*[^;]*Slider\(\s*showShakeStrength\s*,\s*0f\s*,\s*2f\s*\)", mod)
    line(ok and bool(slider), "B_SHAKE_SLIDER", "a screen shake strength slider from none (0) to double (2), default 1",
         "; ".join(why) + ("" if slider else " no Slider(showShakeStrength, 0f, 2f)") or "present", "saved, drawn 0..2, reset", 1)
    ok, why = setting_ok(src, "showMarksLast", "int", "1")
    line(ok, "B_MARKS_LAST", "how long scars and soot last: a choice short (0) / normal (1) / long (2), default normal",
         "; ".join(why) or "present", "saved, drawn, reset", 1)

    hook = [n for n, t in src.items() if re.search(r'HarmonyPatch\(\s*typeof\(Explosion\)\s*,\s*(nameof\(Explosion\.StartExplosion\)|"StartExplosion")', t)]
    pre = post = False
    writes = []
    for n in hook:
        t = src[n]
        pre = pre or bool(re.search(r"static\s+void\s+Prefix\(", t))
        post = post or bool(re.search(r"static\s+void\s+Postfix\(", t))
        writes += re.findall(r"__instance\.(\w+)\s*(?:=|\+=|-=|\*=)(?!=)", t)
    line(bool(hook) and pre and post, "B_HOOK", "a prefix and a postfix on Explosion.StartExplosion, apart from the knockback hook",
         ", ".join(hook) or "none", "one file with both", len(src))
    allowed = {"doVisualEffects", "screenShakeFactor", "preExplosionSpawnSingleThingDef"}
    bad = sorted(set(writes) - allowed)
    line(bool(hook) and not bad, "B_VISUAL_ONLY", "the hook writes only the three visual fields of the explosion (no damage, radius, cell or throw)",
         ", ".join(bad) or "writes %s" % sorted(set(writes)), "subset of %s" % sorted(allowed), len(writes))

    plan = read(os.path.join(SRC, "RM_KnockbackShowPlan.cs")) if os.path.isfile(os.path.join(SRC, "RM_KnockbackShowPlan.cs")) else ""
    m = re.search(r"RippleGrowthPerSecond\s*=\s*([\d.]+)f", plan)
    rip = D.get(("FleckDef", "RM_KnockbackBlastRipple"))
    g = rip.findtext("growthRate") if rip is not None else None
    line(bool(m) and g is not None and abs(float(g) - float(m.group(1))) < 1e-6, "B_RIPPLE_RATE",
         "the ripple def's growthRate equals the kernel's RippleGrowthPerSecond (the ring's width is its life times that rate)",
         "def %s, kernel %s" % (g, m.group(1) if m else None), "equal", 1)

    widths = re.search(r"ScarDrawSizes\s*=\s*\{([^}]*)\}", plan)
    kw = tuple(x.strip().rstrip("f") for x in widths.group(1).split(",")) if widths else ()
    scars, sbad = 0, ([] if kw == SCAR_WIDTHS else ["kernel widths %s, defs named for %s" % (kw, SCAR_WIDTHS)])
    for name in SCAR_NAMES:
        el = D.get(("ThingDef", name))
        if el is None:
            continue
        scars += 1
        want = float(name.rsplit("_", 1)[1][:-len("Wide")])
        got = el.findtext("graphicData/drawSize")
        f = el.find("filth")
        rain = f is not None and (f.findtext("rainWashes") or "").strip().lower() == "true"
        days = f is not None and f.find("disappearsInDays") is not None
        clean = f is not None and f.findtext("cleaningWorkToReduceThickness") is not None
        if got is None or abs(float(got.strip("() ").split(",")[0]) - want) > 1e-6:
            sbad.append("%s drawSize %s, kernel %s" % (name, got, want))
        if not (rain and days and clean):
            sbad.append("%s rain %s days %s clean %s" % (name, rain, days, clean))
    line(scars == len(SCAR_NAMES) and not sbad, "B_SCAR_DEFS",
         "a scar def per kernel width and kind; rain washes them, time wears them, a colonist cleans them",
         "; ".join(sbad) or "%d defs" % scars, "%d defs, all true" % len(SCAR_NAMES), len(SCAR_NAMES))

    # the game logs "Config error in <def>: ends with a numerical digit, which is not allowed on ThingDefs" at every load
    # (ThingDef.ConfigErrors; RIMMANDRAKE_RENAME_KNOCKBACK_SCAR_DEFS_DIGIT_ENDING_CONFIG_ERROR)
    digit = sorted(n for (t, n) in D if t == "ThingDef" and n[-1:].isdigit())
    line(not digit, "B_NO_DIGIT_THINGDEF", "no ThingDef of the mod has a name that ends in a digit (a config error at every load)",
         ", ".join(digit) or "none", "none", sum(1 for (t, _n) in D if t == "ThingDef"))
    show = read(os.path.join(SRC, "RM_KnockbackShow.cs")) if os.path.isfile(os.path.join(SRC, "RM_KnockbackShow.cs")) else ""
    named = re.search(r"ScarDefName\(KbScarKind kind, int sizeClass\)\s*\{\s*return OldScarDefName\(kind, sizeClass\) \+ \"Wide\";", show)
    # the postfix sits on BackCompatibleDefName and maps only a ThingDef name (a wrong type guard would map nothing a save holds)
    old = re.search(r"BackCompatibleDefName\)\)\]\s*\[[^\]]*\]\s*public static class RM_Patch_ScarOldNames.*?"
                    r"defType != typeof\(ThingDef\).*?__result \+ \"Wide\"", show, re.S)
    line(bool(named) and bool(old), "B_SCAR_NAMES_LOAD",
         "the code lays the defs by their Wide names, and a save that holds a 0.2.0 name (no Wide) loads the renamed def",
         "ScarDefName %s, old-name postfix %s" % (bool(named), bool(old)), "both", 2)

    donors = []
    for p in glob.glob(os.path.join(EK, "**", "*"), recursive=True):
        if os.path.isfile(p) and p.endswith((".cs", ".xml")) and re.search(DONORS, read(p)):
            donors.append(os.path.relpath(p, EK))
    line(not donors, "B_NO_DONOR", "nothing in the mod names a donor explosion mod or its defs", ", ".join(donors) or "none", "none", 1)


def win(p):
    p = os.path.abspath(p)
    return "%s:\\%s" % (p[5].upper(), p[7:].replace("/", "\\"))


def kernel():
    """-> True when the kernel half ran (its lines are printed), False when it could not look."""
    dotnet = next((d for d in DOTNET if os.path.isfile(d)), None)
    if dotnet is None or not os.path.isdir(os.path.dirname(STAGE)):
        print("UNMEASURED K_SHOW: no Windows dotnet.exe or D: staging root on this machine; the kernel half did not run")
        return False
    if not all(os.path.isfile(os.path.join(SRC, f)) for f in SHIPPED):
        line(False, "K_SHOW", "the show kernel exists", "missing %s" % [f for f in SHIPPED if not os.path.isfile(os.path.join(SRC, f))], "both", 0)
        return True
    from winbuild import run_interop_captured  # WSL lost-launch retry
    with open(os.path.join("/tmp", "explosiveknockback_showselftest.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        for d in ("obj", "bin"):    # a retained output can look newer than a fresh source: build clean
            shutil.rmtree(os.path.join(STAGE, "SelfTestShow", d), ignore_errors=True)
        os.makedirs(os.path.join(STAGE, "SelfTestShow"), exist_ok=True)
        for f in SHIPPED:           # shutil.copy, never copy2: a fresh mtime makes dotnet rebuild
            shutil.copy(os.path.join(SRC, f), os.path.join(STAGE, f))
        for f in ("Program.cs", "RimMandrakeExplosiveKnockback.ShowSelfTest.csproj"):
            shutil.copy(os.path.join(SRC, "SelfTestShow", f), os.path.join(STAGE, "SelfTestShow", f))
        r = run_interop_captured([dotnet, "run", "--project", win(os.path.join(STAGE, "SelfTestShow",
                                  "RimMandrakeExplosiveKnockback.ShowSelfTest.csproj")), "-c", "Release"],
                                 capture_output=True, text=True, stdin=subprocess.DEVNULL)
    out = (r.stdout or "") + (r.stderr or "")
    rows = [l for l in out.splitlines() if l.startswith(("PASS ", "FAIL "))]
    for l in rows:
        print(l.replace("PASS ", "PASS K_", 1).replace("FAIL ", "FAIL K_", 1))
        OUT.append(l.startswith("PASS "))
    if r.returncode != 0 and not any(l.startswith("FAIL ") for l in rows):
        tail = "\n".join(out.strip().splitlines()[-15:])
        line(False, "K_SHOW_BUILD", "the show kernel builds and runs", "exit %d: %s" % (r.returncode, tail), "exit 0", 0)
    elif not rows:
        line(False, "K_SHOW_ROWS", "the show kernel printed its checks", "no PASS/FAIL row", ">= 1 row", 0)
    return True


def main():
    structure()
    looked = kernel()
    failed = OUT.count(False)
    if not looked:
        print("UNMEASURED blast show: %d structure line(s), %d failing; the kernel half could not run" % (len(OUT), failed))
        return 2 if failed == 0 else 1
    print("%s blast show: %d of %d line(s) failing" % ("PASS" if failed == 0 else "FAIL", failed, len(OUT)))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

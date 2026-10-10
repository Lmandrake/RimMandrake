#!/usr/bin/env python3
"""Offline lint of ExplosiveKnockback (mandrake.rm.explosiveknockback): defs/patches vs C# via lint_mod_defs.py, plus:

  ek-ext      every RM_KnockbackExtension li anywhere in src/ (this mod's patches, KineticArms' defs and patches): only the four fields
              the class has (force, maxThrowCells, impactFactor, immuneBodySizeOverride), force 0..10, maxThrowCells integer 0..30,
              impactFactor >= 0, immuneBodySizeOverride >= 0; a DamageDef xpath names a vanilla damage def we ship against or a def some
              mod defines. Sanity probe: the sweep sees this mod's six damage-def patches and KineticArms' extensions
  ek-flyer    RM_PawnFlyer_Knockback: PawnFlyerBase parent, thingClass PawnFlyer (FlowWorks' pit-landing postfix is on the base class),
              flight duration and speed positive, progress curve rises monotonically from (0,0) to (1,1), stun range lo <= hi
  ek-reset    Reset-to-defaults writes exactly the declared default of every setting, and every default sits inside its slider
  ek-kernel   RM_KnockbackMath.cs is Verse-free (the offline tests compile it alone); the Harmony id equals the About packageId

    python3 src/RimMandrake/Utils/lint_explosiveknockback_defs.py [--quiet] [--mod-dir D]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
EXT = "RimMandrake.ExplosiveKnockback.RM_KnockbackExtension"
FIELDS = {"force", "maxThrowCells", "impactFactor", "immuneBodySizeOverride"}
VANILLA_DAMAGE = {"Bomb", "Flame", "EMP", "Smoke", "Extinguish", "ToxGas", "Thump"}   # Core, Biotech (ToxGas) and Odyssey (Thump) damage defs this stack patches
S = "RimMandrakeExplosiveKnockbackSettings"


def main(argv):
    rc = lint_mod_defs.run("ExplosiveKnockback", argv)
    if rc == 2:
        return 2
    mod = os.path.join(REPO, "src", "RimMandrake", "ExplosiveKnockback")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    errs = []
    E = lambda c, m: errs.append("ERROR %s: %s" % (c, m))
    rd = lambda *p: open(os.path.join(mod, *p), encoding="utf-8-sig").read()

    # ek-ext
    defined = set()
    for p in glob.glob(os.path.join(REPO, "src", "*", "*", "Defs", "**", "*.xml"), recursive=True):
        defined |= set(re.findall(r"<defName>([^<]+)</defName>", re.sub(r"<!--.*?-->", "", open(p, encoding="utf-8-sig", errors="replace").read(), flags=re.S)))
    seen, in_mod, in_kinetic = 0, 0, 0
    real = os.path.join(REPO, "src", "RimMandrake", "ExplosiveKnockback") + os.sep
    files = [p for p in glob.glob(os.path.join(REPO, "src", "*", "*", "**", "*.xml"), recursive=True) if not p.startswith(real)]
    files += glob.glob(os.path.join(mod, "**", "*.xml"), recursive=True)      # this mod, or the planted copy of it
    for p in files:
        if os.sep + "Textures" + os.sep in p or os.sep + "About" + os.sep in p:
            continue
        txt = open(p, encoding="utf-8-sig", errors="replace").read()
        if EXT not in txt:
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        rel = os.path.relpath(p, os.path.join(REPO, "src")) if p.startswith(REPO) else "ExplosiveKnockback(copy)/" + os.path.relpath(p, mod)
        for op in root.iter("Operation"):
            for xp in op.iter("xpath"):
                m = re.search(r'DamageDef\[defName="([^"]+)"\]', xp.text or "")
                if m and m.group(1) not in VANILLA_DAMAGE and m.group(1) not in defined:
                    E("ek-ext", "%s patches DamageDef %s which no mod defines and is not a known vanilla damage def" % (rel, m.group(1)))
        for li in root.iter("li"):
            if li.get("Class") != EXT:
                continue
            seen += 1
            in_mod += p.startswith(mod + os.sep)
            in_kinetic += "KineticArms" in rel
            kids = {k.tag for k in li}
            if kids - FIELDS:
                E("ek-ext", "%s: unknown field(s) %s (the class has %s; an unknown field is dropped silently)" % (rel, sorted(kids - FIELDS), sorted(FIELDS)))
            try:
                force = float(li.findtext("force") or 1)
                cap = li.findtext("maxThrowCells")
                imp = float(li.findtext("impactFactor") or 1)
                imm = float(li.findtext("immuneBodySizeOverride") or 0)
                if not 0 <= force <= 10:
                    E("ek-ext", "%s: force %s outside 0..10" % (rel, force))
                if cap is not None and not (re.fullmatch(r"\d+", cap.strip()) and 0 <= int(cap) <= 30):
                    E("ek-ext", "%s: maxThrowCells %r is not an integer 0..30" % (rel, cap))
                if imp < 0:
                    E("ek-ext", "%s: impactFactor %s < 0" % (rel, imp))
                if imm < 0:
                    E("ek-ext", "%s: immuneBodySizeOverride %s < 0" % (rel, imm))
            except ValueError as e:
                E("ek-ext", "%s: a field is not a number (%s)" % (rel, e))
    if in_mod < 6 or in_kinetic < 1:
        E("ek-ext", "sweep saw %d extensions in this mod (want >= 6) and %d in KineticArms (want >= 1): the lint cannot see what it checks" % (in_mod, in_kinetic))

    # ek-flyer
    root = ET.parse(os.path.join(mod, "Defs", "ThingDefs", "RM_PawnFlyer_Knockback.xml")).getroot()
    d = next((x for x in root.iter("ThingDef") if x.findtext("defName") == "RM_PawnFlyer_Knockback"), None)
    if d is None:
        E("ek-flyer", "RM_PawnFlyer_Knockback is missing")
    else:
        if d.get("ParentName") != "PawnFlyerBase":
            E("ek-flyer", "parent is %r, not PawnFlyerBase" % d.get("ParentName"))
        if (d.findtext("thingClass") or "").strip() != "PawnFlyer":
            E("ek-flyer", "thingClass is %r; it must stay vanilla PawnFlyer so FlowWorks' pit-landing postfix on the base RespawnPawn catches it" % d.findtext("thingClass"))
        pf = d.find("pawnFlyer")
        if float(pf.findtext("flightDurationMin") or 0) <= 0 or float(pf.findtext("flightSpeed") or 0) <= 0:
            E("ek-flyer", "flightDurationMin / flightSpeed must be positive")
        pts = [tuple(float(v) for v in re.findall(r"-?[\d.]+", li.text)) for li in pf.findall("progressCurve/points/li")]
        if len(pts) < 2 or pts[0] != (0.0, 0.0) or pts[-1] != (1.0, 1.0) or any(b[0] <= a[0] or b[1] < a[1] for a, b in zip(pts, pts[1:])):
            E("ek-flyer", "progressCurve %s does not rise monotonically from (0,0) to (1,1)" % pts)
        lo, hi = (int(v) for v in (pf.findtext("stunDurationTicksRange") or "0~0").split("~"))
        if lo > hi:
            E("ek-flyer", "stun range %d~%d is inverted" % (lo, hi))

    # ek-reset
    modcs = rd("Source", "RM_KnockbackMod.cs")
    decl = dict(re.findall(r"public static (?:bool|float|int) (\w+) = ([^;]+);", modcs))
    reset = modcs[modcs.index("public static void Reset()"):]
    wrote = dict(re.findall(S + r"\.(\w+) = ([^;]+);", reset))
    for fld, val in decl.items():
        if fld not in wrote:
            E("ek-reset", "Reset() never writes %s" % fld)
        elif wrote[fld].strip() != val.strip():
            E("ek-reset", "Reset() writes %s = %s but it is declared %s" % (fld, wrote[fld], val))
    for m in re.finditer(r"(\w+) = (?:\(int\))?(?:Mathf\.Round\()?list\.Slider\(\1, ([\d.]+)f, ([\d.]+)f\)", modcs):
        fld, lo, hi = m.group(1), float(m.group(2)), float(m.group(3))
        v = decl.get(fld)
        if v is None or not lo <= float(v.rstrip("f")) <= hi:
            E("ek-reset", "%s default %s lies outside its slider %s..%s" % (fld, v, lo, hi))

    # ek-kernel
    for n, line in enumerate(rd("Source", "RM_KnockbackMath.cs").splitlines(), 1):
        if re.match(r"\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", line):
            E("ek-kernel", "RM_KnockbackMath.cs:%d `%s` (the offline tests compile this file alone)" % (n, line.strip()))
    about_path = os.path.join(mod, "About", "About.xml")
    if not os.path.exists(about_path):
        about_path = os.path.join(REPO, "src", "RimMandrake", "ExplosiveKnockback", "About", "About.xml")
    pkg = ET.parse(about_path).getroot().findtext("packageId")
    hid = re.search(r'new Harmony\("([^"]+)"\)', modcs)
    if not hid or hid.group(1) != pkg:
        E("ek-kernel", "Harmony id %r differs from the About packageId %r" % (hid.group(1) if hid else None, pkg))
    print("explosiveknockback data: %d RM_KnockbackExtension li checked (%d here, %d in KineticArms)" % (seen, in_mod, in_kinetic))
    for e in errs:
        print(e)
    return 1 if (errs or rc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

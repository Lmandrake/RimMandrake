"""Acceptance: Blisterfloat and Gorekite carry a whole-body flying flip-book like Skinflap and Sparkleech.
PASS 4/4 when each race def sets flyingAnimationFramePathPrefix and frames exist on disk for it. FAIL on base."""
import re, sys, pathlib
root = pathlib.Path(__file__).resolve().parents[3] / "src/RimMandrake/Contagion"
xml = (root / "Defs/ThingDefs_Races/RM_ContagionFauna.xml").read_text(encoding="utf-8")
ok = 0
for race in ("RM_Blisterfloat", "RM_Gorekite"):
    pre = None  # the prefix sits on the PawnKindDef, a later block with the same defName
    for m in re.finditer(r"<defName>%s</defName>((?:(?!<defName>).)*)" % race, xml, re.S):
        pre = pre or re.search(r"<flyingAnimationFramePathPrefix>([^<]+)<", m.group(1))
    print("prefix", race, "PASS" if pre else "FAIL"); ok += bool(pre)
    frames = list((root / "Textures").glob(pre.group(1) + "*.png")) if pre else []
    print("frames", race, "PASS" if frames else "FAIL"); ok += bool(frames)
print("%d/4" % ok); sys.exit(0 if ok == 4 else 1)

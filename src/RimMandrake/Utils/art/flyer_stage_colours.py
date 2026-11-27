#!/usr/bin/env python3
"""flyer_stage_colours.py - make a flyer fly at each life stage's own size: InheritColors true, one colour per stage.

RimWorld 1.6 (AnimationDefGenerator_Flying) sizes every stage's flight frames from the first stage when
flyingAnimationInheritColors is false, and caches them by bodyGraphicData colour when it is true. This edits each named
PawnKindDef in src/ in place (text edit, the file's layout kept): InheritColors true, and stage i's bodyGraphicData (and
femaleGraphicData) colour = the first stage's colour (white if unset) less i on the blue channel (white: all channels),
1/255 apart, not visible. It expects three life stages. Check after with flyer_size_census.py.

    python3 src/RimMandrake/Utils/art/flyer_stage_colours.py <PawnKindDef> ...
"""
import re
import sys
from pathlib import Path

TARGETS = sys.argv[1:]
NOTE = ("<!-- flyer_stage_colours.py: InheritColors true and one bodyGraphicData colour per life stage\n"
        "{ind}     (1/255 apart, not visible) are load-bearing: the engine (AnimationDefGenerator_Flying) sizes every stage's flight\n"
        "{ind}     frames from the first stage when InheritColors is false, and caches them by colour when it is true. Checked by\n"
        "{ind}     src/RimMandrake/Utils/art/flyer_size_census.py. -->\n")
root = Path(__file__).resolve().parents[3]
files = {}
for d in TARGETS:
    hits = [f for f in root.rglob("Defs/**/*.xml") if f"<defName>{d}</defName>" in f.read_text(encoding="utf-8") and "flyingAnimationFramePathPrefix" in f.read_text(encoding="utf-8")]
    assert len(hits) == 1, (d, hits)
    files.setdefault(hits[0], []).append(d)

def col(base, i):
    return "(" + ",".join(str(c) for c in base[:2]) + f",{base[2]-i})" if base else f"({255-i},{255-i},{255-i})"

def recolor_block(block, tag, c):
    """Set <color> inside the first <tag>...</tag> of block."""
    m = re.search(rf"(<{tag}>)(.*?)(</{tag}>)", block, re.S)
    assert m, tag
    inner = m.group(2)
    if "<color>" in inner:
        inner = re.sub(r"<color>[^<]*</color>", f"<color>{c}</color>", inner, count=1)
    else:
        dm = re.search(r"\n([ \t]*)<drawSize>[^<]*</drawSize>", inner)
        assert dm, (tag, inner)
        inner = inner[:dm.end()] + f"\n{dm.group(1)}<color>{c}</color>" + inner[dm.end():]
    return block[:m.start(2)] + inner + block[m.end(2):]

for f, defs in files.items():
    text = f.read_text(encoding="utf-8")
    for d in defs:
        pks = [m for m in re.finditer(r"<PawnKindDef\b.*?</PawnKindDef>", text, re.S) if f"<defName>{d}</defName>" in m.group(0)]
        assert len(pks) == 1, (d, len(pks))
        pk = pks[0].group(0)
        # InheritColors
        if "<flyingAnimationInheritColors>" in pk:
            pk = re.sub(r"<flyingAnimationInheritColors>\w+</flyingAnimationInheritColors>", "<flyingAnimationInheritColors>true</flyingAnimationInheritColors>", pk)
        else:
            mm = re.search(r"\n([ \t]*)<flyingAnimationDrawSizeIsMultiplier>true</flyingAnimationDrawSizeIsMultiplier>", pk)
            pk = pk[:mm.end()] + f"\n{mm.group(1)}<flyingAnimationInheritColors>true</flyingAnimationInheritColors>" + pk[mm.end():]
        im = re.search(r"\n([ \t]*)<flyingAnimationInheritColors>", pk)
        pk = pk[:im.start() + 1] + im.group(1) + NOTE.format(ind=im.group(1)) + pk[im.start() + 1:]
        # life stages
        ls = re.search(r"<lifeStages>(.*)</lifeStages>", pk, re.S)
        body = ls.group(1)
        lis = [m.span() for m in re.finditer(r"<li>.*?</li>(?=\s*(<li>|$))", body, re.S)]
        assert len(lis) == 3, (d, len(lis))
        base = None
        first = re.search(r"<bodyGraphicData>.*?<color>\s*\(([^)]*)\)\s*</color>", body[lis[0][0]:lis[0][1]], re.S)
        if first:
            base = [int(x.strip()) for x in first.group(1).split(",")][:3]
        out, pos = [], 0
        for i, (a, b) in enumerate(lis):
            li = body[a:b]
            c = col(base, i)
            li = recolor_block(li, "bodyGraphicData", c)
            if "<femaleGraphicData>" in li:
                li = recolor_block(li, "femaleGraphicData", c)
            out.append(body[pos:a] + li)
            pos = b
        body = "".join(out) + body[pos:]
        pk = pk[:ls.start(1)] + body + pk[ls.end(1):]
        text = text.replace(pks[0].group(0), pk)
        print("fixed", d, f.relative_to(root))
    f.write_text(text, encoding="utf-8")

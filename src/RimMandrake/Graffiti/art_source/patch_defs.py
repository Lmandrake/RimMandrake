"""Write each mark's wall-plane size, pigmenting and description into the defs from the art manifest. Idempotent."""
import glob, os, re
import manifest as MF

DEFS = os.path.join(MF.REPO, "src/RimMandrake/Graffiti/Defs")
SIZES = {}
PIG = set()
for m in MF.M.values():
    SIZES[m["folder"]] = (m["width"], m["height"])
    if m["pigmented"]:
        PIG.add(m["folder"])

DESC = {
    "RM_Graffiti_Glyph_Cannibal": "A gnawed bone in a ring of toothmarks, wet from the brush - a mark for those who feed on their own kind.",
    "RM_Graffiti_Glyph_MaleSupremacy": "A great horned head over a row of bowed little figures, daubed in rust.",
    "RM_Graffiti_Glyph_FemaleSupremacy": "A crowned woman's head over a row of bowed little figures, sprayed tall.",
    "RM_Graffiti_Glyph_Nudism": "A naked running figure in four strokes of charcoal, arms flung wide.",
    "RM_Graffiti_Glyph_Inhuman": "A head that is only a jagged burst with too many eyes.",
    "RM_Graffiti_Glyph_PainIsVirtue": "A wreath of thorns dragged in one go, a blot of red falling from it.",
    "RM_Graffiti_Glyph_Raider": "A boot stamped on a heap, smeared by the heel.",
    "RM_Graffiti_Glyph_Supremacist": "A sword thrust down into a heap of little heads.",
    "RM_Graffiti_Glyph_Loyalist": "A blunt three-spiked banner on a pole, hung and dripping.",
    "RM_Graffiti_Glyph_Individualist": "One big open eye, alone, a line slashed under it.",
    "RM_Graffiti_Glyph_Collectivist": "A mob of thumbprint heads pressed so close they make one blot.",
    "RM_Graffiti_Glyph_Guilty": "A head bowed to the ground in charcoal, lines of weeping dragged away from it.",
    "RM_Graffiti_Glyph_Darkness": "A wiped black blot with a pale ragged ring left around it.",
    "RM_Graffiti_Glyph_Blindsight": "An eye gouged out with two heavy strokes.",
    "RM_Graffiti_Glyph_Bloodfeeding": "Two long fangs and a wiped smear of red.",
    "RM_Graffiti_Glyph_Transhumanist": "Half a head, half a machine, hard-edged on one side and loose on the other.",
    "RM_Graffiti_Glyph_FleshPurity": "A heart wrapped in a wet scrawl.",
    "RM_Graffiti_Glyph_HumanPrimacy": "A big human handprint, pressed and dragged down the wall.",
    "RM_Graffiti_Glyph_NaturePrimacy": "A twisted knot of roots clawing downward.",
    "RM_Graffiti_Glyph_AnimalPersonhood": "A wolf's head in five thick strokes, with a person's eye.",
    "RM_Graffiti_Glyph_Rancher": "The wide horns and long face of a muskox, daubed fast.",
    "RM_Graffiti_Glyph_Tunneler": "A black hole rammed into a mound, pick marks fanning out.",
    "RM_Graffiti_Glyph_TreeConnection": "A gnarled trunk dragged with a filthy rag, branches like arms.",
    "RM_Graffiti_Glyph_HighLife": "One long curl of smoke rising into a blot.",
    "RM_Graffiti_Glyph_Proselytizer": "A screaming mouth with three lines of shout flying out of it.",
    "RM_Graffiti_Glyph_Ritualist": "Thumbed squat figures dancing around a blot of fire.",
    "RM_Graffiti_Glyph_Shipborn": "A blunt ship rising over the curve of a world.",
}

for path in glob.glob(DEFS + "/ThingDefs_Graffiti*.xml"):
    s = open(path, encoding="utf-8").read()

    def fix(match):
        d = match.group(0)
        name = re.search(r"<defName>(\w+)</defName>", d)
        tex = re.search(r"<texPath>Things/Filth/Art/(\w+)</texPath>", d)
        if not name or not tex:
            return d
        name = name.group(1)
        folder = tex.group(1)
        if folder not in SIZES:
            return d
        w, h = SIZES[folder]
        size = f"<drawSize>({w:g}, {h:g})</drawSize>"
        if "<drawSize>" in d:
            d = re.sub(r"<drawSize>.*?</drawSize>", size, d)
        else:
            d = re.sub(r"(\s*)<shaderType>", lambda m: f"{m.group(1)}{size}{m.group(1)}<shaderType>", d, count=1)
        if folder in PIG and "<pigmented>" not in d:
            d = re.sub(r"(\s*)<form>", lambda m: f"{m.group(1)}<pigmented>true</pigmented>{m.group(1)}<form>", d, count=1)
        if folder == "RM_Graffiti_Scratches" and "<wallThrough>" not in d:
            d = re.sub(r"(\s*)<form>", lambda m: f"{m.group(1)}<wallThrough>0</wallThrough>{m.group(1)}<form>", d, count=1)
        if name in DESC:
            d = re.sub(r"<description>.*?</description>", lambda m: f"<description>{DESC[name]}</description>", d, flags=re.S)
        return d

    s2 = re.sub(r"<ThingDef\b.*?</ThingDef>", fix, s, flags=re.S)
    if s2 != s:
        open(path, "w", encoding="utf-8", newline="").write(s2)
        print("patched", os.path.basename(path))

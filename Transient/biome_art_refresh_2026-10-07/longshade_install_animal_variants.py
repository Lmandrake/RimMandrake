"""Long Shade sheet — owner's ticked animal variants (card answer 2026-10-07 22:48 PDT: his picks REPLACE the donor
colour versions at all ages). Installs each full-set variant at swanimals/<Sp>/<Sp>V_<letter>_<facing>.png via the art
ledger and rewrites the PawnKindDef alternateGraphics to exactly those. East-only variants (Gorg L, FrilledGorg I/K)
are wired when their queued N/S art lands. Usage: python3 longshade_install_animal_variants.py"""
import json, re, sys
from pathlib import Path
R = Path("/home/mandrake/rm/bench")
sys.path.insert(0, str(R / "src/RimMandrake/Utils/art"))
import artledger as L
VIA = "Transient/biome_ffar/desert_sheet_2026-10-04.decisions.json"
SWB = "src/RimStarWars/SWBestiary"
SPEC = {  # row: (texture folder/stem, def file, PawnKindDef defName, variant letters)
    "RSW_Bantha": ("Bantha/Bantha", "RSW_Bantha.xml", "RSW_Bantha", "GHIJ"),
    "RSW_Gorg": ("Gorg/Gorg", "RSW_Gorg.xml", "RSW_Gorg", "GHKNO"),
    "RSW_FrilledGorg": ("FrilledGorg/FrilledGorg", "RSW_FrilledGorg.xml", "RSW_FrilledGorg", "GJM"),
    "RSW_LongtailGorg": ("LongtailGorg/LongtailGorg", "RSW_LongtailGorg.xml", "RSW_LongtailGorg", "GHIJKL"),
    "RSW_Varactyl": ("Varactyl/Varactyl", "RSW_Varactyl.xml", "RSW_Varactyl", "EF"),
    "RSW_WraidAlpha": ("WraidAlpha/WraidAlpha", "RSW_WraidAlpha.xml", "RSW_WraidAlpha", "D"),
}
snap = json.loads((R / "infrastructure/state/art/sheets/desert_sheet_2026-10-04.snapshot.json").read_text())["rows"]
idx = L.Index()
for row, (stem, deff, kind, letters) in SPEC.items():
    paths = []
    for c in letters:
        cols = snap[row]["columns"][c]
        assert set(cols) == {"east", "north", "south"}, (row, c)
        rid = next(e["id"] for e in idx.rulings if e.get("via") == VIA and (e.get("target") or {}).get("row") == row
                   and (e.get("target") or {}).get("column") == c and L.normalise_verdict(e.get("verdict")) == "keep")
        tp = f"swanimals/{stem}V_{c}"
        for f, sha in cols.items():
            print(row, c, f, L.install(SWB, f"{tp}_{f}.png", sha, ruling_id=rid).get("status"))
        paths.append(tp)
    p = R / SWB / "Defs/ThingDefs_Races" / deff
    s = p.read_text()
    i = s.index(f"<defName>{kind}</defName>", s.index("<PawnKindDef"))
    j = s.index("</PawnKindDef>", i)
    blk = s[i:j]
    lis = "".join(f"\n      <li>\n        <texPath>{t}</texPath>\n      </li>" for t in paths)
    chance = round(len(paths) / (len(paths) + 1), 3)
    new = (f"<alternateGraphicChance>{chance}</alternateGraphicChance>  <!-- owner 2026-10-07 card: his Long Shade sheet "
           f"variant picks replace the donor colour versions at all ages; base + {len(paths)} variants equally likely -->\n"
           f"    <alternateGraphics>{lis}\n    </alternateGraphics>")
    blk2, n = re.subn(r"<alternateGraphicChance>.*?</alternateGraphics>", new, blk, count=1, flags=re.S)
    if not n:
        blk2 = blk.replace("<lifeStages>", new + "\n    <lifeStages>", 1)
    p.write_text(s[:i] + blk2 + s[j:])
    print("wired", deff, chance)

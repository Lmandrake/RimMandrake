#!/usr/bin/env python3
"""texture_regen_jobs.py — artpipe job file for the gaps design/RimMandrake/biome_texture_regeneration_audit_2026-10-18.md
found with NO render of ours anywhere in the artpipe state (texture_regen_audit.py `render_dirs` empty, probe-checked).

    python3 src/RimMandrake/Utils/art/texture_regen_jobs.py --out design/RimMandrake/biome_texture_regen_jobs_2026-10-18.json --item <ID>

Then (state dir, not git):  python3 src/RimMandrake/Utils/artpipe/fill_queue.py --input <that file>
Prompts come from each def's own description (same house style as placeholder_jobs.py); no reference images, no facings
(all subjects are single-picture items, plants or buildings). Never runs image generation itself.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import placeholder_jobs as PJ  # noqa: E402

# (defName, kind, canvas, biome register key, priority, why)
SPECS = [
    ("RM_Vashuu", "item", 128, "RM_Greentide", 12, "catch item wears the mee's old picture (commit f3a7513c5)"),
    ("RM_UltrissPad", "plant", 256, "RM_Stillsand", 12, "draws the donor Ultracactus bytes"),
    ("RM_SekkulaathCream", "item", 128, "RM_FeverWood", 15, "geometric placeholder, allowlist OWED"),
    ("RM_Sekkulaath_Bloom", "building", 512, "RM_FeverWood", 15, "geometric placeholder, allowlist OWED"),
    ("RM_SekkulaathTank", "building", 512, "RM_FeverWood", 15, "geometric placeholder, allowlist OWED"),
    ("RM_ElderSealedRelic", "item", 128, "RM_GreySea", 15, "geometric placeholder"),
    ("RM_CargoFloat", "item", 256, "RM_GreySea", 15, "geometric placeholder"),
    ("RM_RawSalt", "item", 128, "RM_GreySea", 15, "geometric placeholder"),
    ("RM_GlowTank", "building", 512, "RM_TwilightSea", 15, "geometric placeholder; RM_ConstellationCageCube shares the texPath"),
    ("RM_WeakTarSolvent", "item", 128, "RM_TheSump", 15, "geometric placeholder"),
    ("RM_GaslightLamp", "building", 256, "RM_TheSump", 15, "geometric placeholder"),
    ("RM_TarVault", "building", 512, "RM_TheSump", 15, "geometric placeholder"),
    ("RM_SkerrelGall", "item", 128, "RM_Greentide", 25, "draws a donor plant texture"),
    ("RM_GloomcastHide", "item", 128, "RM_LongShade", 25, "draws donor swresource/Leather_Heavy"),
    ("RM_GloomcastMeat", "item", 128, "RM_LongShade", 25, "draws donor swresource/Meat_Saurian"),
    ("RM_GuzzkaEggFertilized", "item", 128, "RM_Stillsand", 25, "one shared donor egg texture for six egg defs"),
    ("RM_VauliskLureOrgan", "item", 128, "RM_TwilightSea", 25, "borrows the Eesh catch picture"),
    ("RM_HullSaltCrust", "item", 256, "RM_GreySea", 25, "draws the StandIn ChunkStone"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--item", required=True)
    a = ap.parse_args()
    defs = PJ.load_defs()
    jobs = []
    for dn, kind, px, bkey, prio, why in SPECS:
        e = defs[dn]
        tp = next(g.findtext("texPath") for g in e.iter("graphicData"))
        label = (e.findtext("label") or dn).strip()
        desc = PJ.clean(e.findtext("description"))
        noun = {"item": "item sprite", "plant": "plant sprite", "building": "building sprite, seen from above"}[kind]
        prompt = (f"RimWorld {noun}, painterly: the {label}. {desc} Our own original design, drawn fresh. "
                  f"One subject, centred.")
        jobs.append({"id": f"texregen_{dn}_v1", "rimflow_item_id": a.item, "target_def": dn, "target_texpath": tp,
                     "slot": tp, "prompt": prompt, "canvas_w": px, "canvas_h": px, "priority": prio,
                     "background": "transparent", "channel": "codex", "facings": [],
                     "biome_register": PJ.REGISTER.get(bkey, PJ.DEFAULT_REG), "style_notes": PJ.HOUSE,
                     "ask": "new", "why": why})
    Path(a.out).write_text(json.dumps(jobs, indent=1))
    print("jobs", len(jobs), "->", a.out)


if __name__ == "__main__":
    main()

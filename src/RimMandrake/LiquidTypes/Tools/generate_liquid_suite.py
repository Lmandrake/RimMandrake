#!/usr/bin/env python3
"""generate_liquid_suite.py — LIQUID_TYPES_SPIKES_1, Spike A (generator).

Proves the mechanism `design/RimMandrake/RM_liquid_types_mod.md` section 5
calls for: one liquid ROW in a small data table -> a cloned TerrainDef suite
whose tags/affordances are UNIONED from the frozen dump's POST-PATCH leaf
(the resolved WaterShallow/WaterDeep etc. as the live 584-mod stack actually
shipped it, not the bare vanilla Core XML) -> a modExtensions block carrying
RM_LiquidProperties -> a compat-patch stub for indexing into a foreign mod's
water terrain.

Spike sizing per section 8: "prove on ONE def, measure, report." This run
proves it on ONE liquid (acid) and writes the result to
../Defs/TerrainDefs/RM_AcidWater.xml. Adding a second row is a dict entry,
not new code — that generality is itself part of what the spike proves.

Source of the post-patch leaf: the FROZEN official dump, OFFICIAL-2026-08-29
(infrastructure/state/dumps/REGISTRY.jsonl), never a live capture — dumps
decay, the official one is the design target and only the owner re-freezes it.
"""

import json
import sys
from pathlib import Path

DUMP_PATH = (
    "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
    "RimWorld by Ludeon Studios/DefDump/captures/2026-08-29T13-30-02Z/defs/TerrainDef.json"
)

# The four leaves RUT_ScaldWater cloned by hand. A moving-water liquid would
# add WaterMovingShallow/WaterMovingChestDeep the same way; the acid pool
# spike only needs still water (Scarlands' "rainbow pools", per the roster).
LEAVES = ["WaterShallow", "WaterDeep"]

# --- the one liquid row this spike proves --------------------------------
# Mirrors §6's table row for "acid": native toxic+dangerous, extension
# carries pH + corrosion. Values [INVENTED unless the table cites a source],
# same flag discipline as the design doc.
LIQUID_ROWS = {
    "acid": {
        "defnamePrefix": "RM_Acid",
        "label_shallow": "acid pool",
        "label_deep": "acid pool, deep",
        "description": (
            "Water gone wrong — the color isn't life, it's reaction. Cloth "
            "and skin both lose a little of themselves to it with every "
            "second submerged."
        ),
        "texturePath_shallow": "Terrain/Surfaces/WaterShallowRamp",
        "texturePath_deep": "Terrain/Surfaces/WaterDeepRamp",
        "glowColor": None,
        "native_overrides": {
            # dangerous+toxic are native fields the engine already reads
            # (§1's table); burnDamage/burnIntervalTicks left at 0 (acid
            # is a corrosion mechanic, not a burn one — §4a's own split).
            "dangerous": True,
            "toxicBuildupFactor": 1,
        },
        "extension": {
            "Class": "RimMandrake.LiquidTypes.RM_LiquidProperties",
            "fields": {
                "viscosityClass": "water",
                "pH": 2,
                "damageOnContact": {"damageDef": "AcidBurn", "amount": 1},
                "damageOnImmersion": {"damageDef": "AcidBurn", "amount": 3},
                "corrodesApparel": True,
            },
        },
        # one compat-index target, per §5.2: our extension riding onto a
        # foreign mod's existing acid-flavoured water. Odyssey's own toxic
        # water is the nearest acid-adjacent donor already in the frozen
        # dump (§2); this is the match-validation entry the patch ships.
        "compat_targets": ["ToxicWaterShallow", "ToxicWaterDeep"],
    }
}


def load_leaf(defs_by_name, leaf_name):
    d = defs_by_name.get(leaf_name)
    if d is None:
        raise SystemExit(f"FATAL: {leaf_name} not found in frozen dump — dump may be stale/wrong path")
    return d["fields"]


def union_tags_affordances(leaf_fields, extra_tags):
    tags = list(dict.fromkeys((leaf_fields.get("tags") or []) + extra_tags))
    # Drop the vanilla salinity/ocean tags that don't apply to a still pool;
    # keep everything else the live stack patched onto vanilla water
    # (dbh_water, BMT_DeepWaterBridgeable, TST_TerrainForMeditationStone, ...).
    tags = [t for t in tags if t not in ("WaterFreshShallow", "WaterFreshShallowStill")]
    affordances = list(leaf_fields.get("affordances") or [])
    return tags, affordances


def build_terrain_xml(defname, label, description, texture_path, leaf_fields,
                       native_overrides, extension, render_precedence, extra_tags):
    tags, affordances = union_tags_affordances(leaf_fields, extra_tags)
    lines = []
    lines.append(f'  <TerrainDef ParentName="{"WaterDeepBase" if "Deep" in defname else "WaterShallowBase"}">')
    lines.append(f"    <defName>{defname}</defName>")
    lines.append(f"    <label>{label}</label>")
    lines.append(f"    <description>{description}</description>")
    lines.append(f"    <renderPrecedence>{render_precedence}</renderPrecedence>")
    lines.append(f"    <texturePath>{texture_path}</texturePath>")
    for k, v in native_overrides.items():
        xv = "true" if v is True else "false" if v is False else v
        lines.append(f"    <{k}>{xv}</{k}>")
    if affordances:
        lines.append("    <affordances>")
        for a in affordances:
            lines.append(f"      <li>{a}</li>")
        lines.append("    </affordances>")
    if tags:
        lines.append("    <tags>")
        for t in tags:
            lines.append(f"      <li>{t}</li>")
        lines.append("    </tags>")
    if extension:
        lines.append("    <modExtensions>")
        lines.append(f'      <li Class="{extension["Class"]}">')
        for fk, fv in extension["fields"].items():
            if isinstance(fv, dict):
                lines.append(f"        <{fk}>")
                for ik, iv in fv.items():
                    lines.append(f"          <{ik}>{iv}</{ik}>")
                lines.append(f"        </{fk}>")
            else:
                xv = "true" if fv is True else "false" if fv is False else fv
                lines.append(f"        <{fk}>{xv}</{fk}>")
        lines.append("      </li>")
        lines.append("    </modExtensions>")
    lines.append("  </TerrainDef>")
    return "\n".join(lines)


def generate(liquid_key, out_dir: Path):
    row = LIQUID_ROWS[liquid_key]
    with open(DUMP_PATH, encoding="utf-8") as f:
        dump = json.load(f)
    defs_by_name = {d["defName"]: d for d in dump["defs"]}

    shallow_leaf = load_leaf(defs_by_name, "WaterShallow")
    deep_leaf = load_leaf(defs_by_name, "WaterDeep")

    prefix = row["defnamePrefix"]
    shallow_xml = build_terrain_xml(
        f"{prefix}Shallow", row["label_shallow"], row["description"],
        row["texturePath_shallow"], shallow_leaf, row["native_overrides"],
        row["extension"], 394, extra_tags=["Water"],
    )
    deep_xml = build_terrain_xml(
        f"{prefix}Deep", row["label_deep"], row["description"],
        row["texturePath_deep"], deep_leaf, row["native_overrides"],
        row["extension"], 395, extra_tags=["Water"],
    )

    header = f"""<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  {prefix}Water.xml         GENERATED by generate_liquid_suite.py, Spike A
  ============================================================================
  Source leaf: frozen dump OFFICIAL-2026-08-29 (2026-08-29T13-30-02Z),
  defs/TerrainDef.json, WaterShallow/WaterDeep as the live 584-mod stack
  resolved them (POST-PATCH — tags/affordances union-carried from BMT, DBH,
  TST, as measured directly from that capture, not re-typed by hand).

  This regenerates from the LIQUID_ROWS table in
  src/RimMandrake/LiquidTypes/Tools/generate_liquid_suite.py; edit the table,
  never this file, once the generator is the standing tool rather than a
  spike. Regenerate only against a re-frozen official dump, never a live
  capture (dumps decay — CHARTER's instrument order).
  ============================================================================
-->
<Defs>

{shallow_xml}

{deep_xml}

</Defs>
"""
    out_path = out_dir / f"{prefix}Water.xml"
    out_path.write_text(header, encoding="utf-8")
    return out_path, shallow_leaf, deep_leaf


def build_compat_patch(liquid_key, out_dir: Path):
    row = LIQUID_ROWS[liquid_key]
    ext = row["extension"]
    targets = row["compat_targets"]
    ops = []
    for target in targets:
        field_xml = []
        for fk, fv in ext["fields"].items():
            if isinstance(fv, dict):
                continue  # keep the compat default simple; skip nested damage blocks
            xv = "true" if fv is True else "false" if fv is False else fv
            field_xml.append(f"            <{fk}>{xv}</{fk}>")
        ops.append(f"""
    <!-- match-validation: expects exactly 1 hit against /Defs/TerrainDef[defName="{target}"] -->
    <Operation Class="PatchOperationConditional">
      <xpath>/Defs/TerrainDef[defName="{target}"]</xpath>
      <match Class="PatchOperationAddModExtension">
        <xpath>/Defs/TerrainDef[defName="{target}"]</xpath>
        <value>
          <li Class="{ext['Class']}">
{chr(10).join(field_xml)}
          </li>
        </value>
      </match>
    </Operation>""")

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  RM_LiquidProperties_CompatIndex.xml     GENERATED by generate_liquid_suite.py
  ============================================================================
  Spike A's third deliverable: the "indexing into every other mod" patch
  index (design doc §5.2). Every Operation here is
  PatchOperationConditional-guarded on the target def actually existing, so a
  missing donor mod prints nothing (never a red error) — the doctrinal
  default for a patch that "matches nothing".

  🔴 NOT YET GATED on our own packageId via PatchOperationFindMod. Per the
  measured fact in modextension-missing-type-discards-def: a modExtensions
  <li Class="..."> whose type cannot be found in ANY loaded assembly does not
  degrade — it discards the WHOLE target def. Since this patch file ships
  INSIDE mandrake.rm.liquidtypes itself, our own assembly is guaranteed
  present whenever this patch runs at all, so that failure mode cannot occur
  here. It becomes live risk only if this compat block is ever copied into a
  DIFFERENT mod's patch folder (e.g. the RUT layer, §7) without a
  FindMod("mandrake.rm.liquidtypes") guard around it — flagged for whoever
  builds §7, not fixed here.
  ============================================================================
-->
<Patch>
{"".join(ops)}
</Patch>
"""
    out_path = out_dir / "RM_LiquidProperties_CompatIndex.xml"
    out_path.write_text(xml, encoding="utf-8")
    return out_path, targets


def main():
    root = Path(__file__).resolve().parent.parent
    terrain_dir = root / "Defs" / "TerrainDefs"
    patch_dir = root / "Defs" / "Patches"
    terrain_dir.mkdir(parents=True, exist_ok=True)
    patch_dir.mkdir(parents=True, exist_ok=True)

    out_path, shallow_leaf, deep_leaf = generate("acid", terrain_dir)
    print(f"WROTE {out_path}")
    print(f"  WaterShallow post-patch tags: {shallow_leaf.get('tags')}")
    print(f"  WaterShallow post-patch affordances: {shallow_leaf.get('affordances')}")
    print(f"  WaterDeep post-patch tags: {deep_leaf.get('tags')}")

    patch_path, targets = build_compat_patch("acid", patch_dir)
    print(f"WROTE {patch_path}")
    print(f"  match-validation targets (expect 1 hit each via validate_patch.py --defs): {targets}")


if __name__ == "__main__":
    sys.exit(main())

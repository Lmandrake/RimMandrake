#!/usr/bin/env python3
"""generate_liquid_suite.py — LIQUID_TYPES_MOD_1, full roster.

Started life as LIQUID_TYPES_SPIKES_1 Spike A (generator), proved on ONE row
(acid). This pass extends LIQUID_ROWS to cover the remaining rows of
design/RimMandrake/RM_liquid_types_mod.md §6 — the mechanism itself is
unchanged: one liquid ROW -> a cloned TerrainDef suite whose tags/affordances
are UNIONED from the frozen dump's POST-PATCH leaf (the resolved
WaterShallow/WaterDeep etc. as the live mod stack actually shipped it, not
bare vanilla Core XML) -> a modExtensions block carrying RM_LiquidProperties
-> entries in a shared compat-patch index for indexing into a foreign mod's
water terrain.

Rows deliberately NOT generated here, per §6 and the item's own scoping:
  - "normal water" — vanilla, no clone. It gets a COMPAT_ONLY_ROWS entry
    instead (§6: "pH 7 row via patch") — a baseline RM_LiquidProperties onto
    vanilla's own water family, not a new TerrainDef.
  - "slime" — RM_GelatinousSlime (src/RimMandrake/GelatinousSlime) already
    ships its OWN liquid terrain, RM_Slime_Liquid (a non-water ground
    terrain, ParentName-free, pathCost 25 — see SlimeTerrain.xml). §6's own
    row says as much: "that mod authors its OWN suite; this mod supplies the
    property grammar it fills in." Cloning a second RM_SlimeShallow/Deep off
    vanilla water here would duplicate/confuse that, so "slime" is also a
    COMPAT_ONLY_ROWS entry (patched onto RM_Slime_Liquid and, for the same
    "shape" donor §6 cites, Alpha Biomes' AB_LiquidSlime) rather than a
    cloned suite.
  - "mud grades (churnmud)" — §6: native Mud/Marsh + one RM_Churnmud. Hand-
    authored directly as ../Defs/TerrainDefs/RM_Churnmud.xml (ParentName
    "MarshBase", the Name= vanilla's own Marsh def carries in
    Data/Core/Defs/TerrainDefs/Terrain_Water.xml:163) — a single standalone
    terrain, not a shallow/deep pair, so it does not fit this generator's
    per-row shape and isn't worth bending it for one def.

RM_LiquidProperties (Source/RM_LiquidProperties.cs) ships exactly SEVEN
fields: viscosityClass, pH, damageOnContact, damageOnImmersion,
corrodesApparel, flammable, igniteTemp. §3's fuller field list (opacity,
surfaceFilm, freezesTo/boilsAwayTo) is DESIGN-ONLY — Spike B "trimmed to what
that spike actually exercises" and this pass does not add C#, so no row here
uses a field the class does not have. Where §6 cites film/opacity for a row,
that part of the row is not represented in the emitted extension (mechanism
absorbed in the doc's own §4c "films — v2 candidate, deferred").

Source of the post-patch leaf: the FROZEN official dump, OFFICIAL-2026-08-29
(infrastructure/state/dumps/REGISTRY.jsonl), never a live capture — dumps
decay, the official one is the design target and only the owner re-freezes it.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "RimMandrake" / "Utils"))
from game_paths import CAPTURES  # the seam owns the LocalLow root

# Pinned to the FROZEN capture on purpose (see docstring) — only the capture
# id is hardcoded, the LocalLow root comes from the seam.
DUMP_PATH = os.path.join(CAPTURES, "2026-08-29T13-30-02Z", "defs", "TerrainDef.json")

# Every row still only needs still water's two leaves. A moving-water liquid
# would add WaterMovingShallow/WaterMovingChestDeep the same way; per §6's
# own line ("a canal or pool liquid ships shallow+deep only; ocean/moving
# variants exist where a consumer does") none of this item's rows has an
# IN-SCOPE consumer that needs ocean/moving depth — those consumers (the
# Scald's own RUT_ScaldWater*, the Greentide salinity gradient, Twilight/Grey
# seas) belong to the RUT layer (§7) or a worldmap biome item, explicitly out
# of scope here. So: shallow+deep, uniformly, for every row below.
LEAVES = ["WaterShallow", "WaterDeep"]

RENDER_PRECEDENCE_SHALLOW = 394
RENDER_PRECEDENCE_DEEP = 395


def _merge(*dicts):
    out = {}
    for d in dicts:
        if d:
            out.update(d)
    return out


# --- the liquid rows -------------------------------------------------------
# Values [INVENTED unless the row's own comment cites a source], same flag
# discipline as the design doc and Spike A's own acid row.
LIQUID_ROWS = {
    "acid": {
        "defnamePrefix": "RM_Acid",
        "file_name": "RM_AcidWater.xml",
        "label_shallow": "acid pool",
        "label_deep": "acid pool, deep",
        "description": (
            "Water gone wrong — the color isn't life, it's reaction. Cloth "
            "and skin both lose a little of themselves to it with every "
            "second submerged."
        ),
        "native_overrides": {
            "dangerous": True,
            "toxicBuildupFactor": 1,
        },
        "extension": {
            "viscosityClass": "water",
            "pH": 2,
            "damageOnContact": {"damageDef": "AcidBurn", "amount": 1},
            "damageOnImmersion": {"damageDef": "AcidBurn", "amount": 3},
            "corrodesApparel": True,
        },
        "compat_targets": ["ToxicWaterShallow", "ToxicWaterDeep"],
    },

    # R-B4a's boiling-lift values, cited (not invented) — read directly from
    # src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_ScaldWater.xml, itself
    # sourced from design/Jawa/mods/REGROWTH_BOILING_LIFT_SPEC.md §R-B4a.
    # This RM_WaterBoiling* suite is the GENERIC (non-campaign) offering —
    # the Scald keeps its own already-shipped RUT_ScaldWater* untouched
    # (§7, out of scope). No extension: native burnDamage/burnIntervalTicks
    # already carries the whole "immersion hurts more than contact" story
    # via two different TerrainDefs (1/300 shallow vs 2/240 deep) — an
    # extension here would only document a neutral pH with no damage spec,
    # which is the same "empty but valid" case §3 names directly.
    "boiling": {
        "defnamePrefix": "RM_WaterBoiling",
        "file_name": "RM_WaterBoiling.xml",
        "label_shallow": "boiling water",
        "label_deep": "boiling water, deep",
        "description": (
            "Kept liquid by heat rather than depth. Steam stands off the "
            "surface even in still air, and nothing wades in without "
            "paying for it."
        ),
        "native_overrides_shallow": {
            "canFreeze": False,
            "burnDamage": 1,
            "burnIntervalTicks": 300,
            "glowColor": "(2,154,229)",
            "glowRadius": 2,
            "traversedThought": "HotSpring",
        },
        "native_overrides_deep": {
            "burnDamage": 2,
            "burnIntervalTicks": 240,
            "glowColor": "(2,154,229)",
            "glowRadius": 2,
            "traversedThought": "HotSpring",
        },
        "extension": None,
        "compat_targets": [],
    },

    # Spike D settled the mechanism: negative heatPerTick is inert (both
    # engine consumers guard on > 0f), so "frigid" ships as the corrosion
    # code path with a cold-shock DamageDef swap, not a native heat field.
    "frigid": {
        "defnamePrefix": "RM_WaterFrigid",
        "file_name": "RM_WaterFrigid.xml",
        "label_shallow": "frigid water",
        "label_deep": "frigid water, deep",
        "description": (
            "Water cold enough to steal warmth through boots and gloves "
            "alike. It does not so much freeze as it freezes you."
        ),
        "native_overrides_shallow": {"pathCost": 60},  # [INVENTED] slush, 2x WaterShallowBase's 30
        "native_overrides_deep": {"canFreeze": True},  # deep water does not freeze natively; frigid should
        "extension": {
            "viscosityClass": "thick",
            "pH": 7,
            "damageOnContact": {"damageDef": "Frostbite", "amount": 1},
            "damageOnImmersion": {"damageDef": "Frostbite", "amount": 3},
            "corrodesApparel": False,
        },
        "compat_targets": [],
    },

    # Two salinity grades, per §6's two defnamePrefixes. waterBodyType
    # Saltwater is the engine's whole salinity axis (§1) — pH/viscosity ride
    # the extension "up the ladder" per §6's own phrasing.
    "brackish": {
        "defnamePrefix": "RM_WaterBrackish",
        "file_name": "RM_WaterBrackish.xml",
        "label_shallow": "brackish water",
        "label_deep": "brackish water, deep",
        "description": (
            "Fresh water gone part of the way to the sea — drinkable in a "
            "pinch, unpleasant at length."
        ),
        "native_overrides": {"waterBodyType": "Saltwater"},
        "extension": {"viscosityClass": "water", "pH": 7.5, "corrodesApparel": False},  # [INVENTED]
        "compat_targets": [],
    },
    "brine": {
        "defnamePrefix": "RM_WaterBrine",
        "file_name": "RM_WaterBrine.xml",
        "label_shallow": "brine pool",
        "label_deep": "brine pool, deep",
        "description": (
            "Salt concentrated past drinking, dense enough to feel "
            "underfoot. Nothing that needs fresh water stays here long."
        ),
        "native_overrides": {"waterBodyType": "Saltwater"},
        "native_overrides_shallow": {"pathCost": 45},  # [INVENTED] denser than brackish
        "extension": {"viscosityClass": "thick", "pH": 8, "corrodesApparel": False},  # [INVENTED]
        "compat_targets": [],
    },

    "poison": {
        "defnamePrefix": "RM_WaterPoisoned",
        "file_name": "RM_WaterPoisoned.xml",
        "label_shallow": "poisoned water",
        "label_deep": "poisoned water, deep",
        "description": "Water carrying more than it should. Nothing in it is inert.",
        "native_overrides": {"toxicBuildupFactor": 2, "dangerous": True},  # [INVENTED, within cited 2-3]
        "extension": None,  # §6's own row: extension column is "—"
        "compat_targets": [],
    },

    # Spike C's two hard findings apply directly: extinguishesFire must be
    # FALSE (else any Fire standing on it self-destroys the same tick,
    # Fire.DoComplexCalcs's flammabilityMax<0.01f guard) and native
    # Flammability must stay near-zero (left unset — WaterShallowBase itself
    # carries no Flammability statBase, so the inherited default is the same
    # "no spontaneous vanilla spread" baseline RUT_ScaldWater/RM_AcidWater
    # already rely on) so LiquidIgnitionMapComponent's trigger-gated ignition
    # is the ONLY ignition route, never vanilla's own TrySpread.
    "propane": {
        "defnamePrefix": "RM_Propane",
        "file_name": "RM_Propane.xml",
        "label_shallow": "liquid propane",
        "label_deep": "liquid propane, deep",
        "description": (
            "Thin, cold, and utterly indifferent to fire until something "
            "else provides the spark. Do not smoke near it."
        ),
        "native_overrides": {"waterBodyType": "None", "canFreeze": False, "extinguishesFire": False},
        "native_overrides_shallow": {"pathCost": 20},  # [INVENTED] thin viscosity, flows easier than water
        "extension": {"viscosityClass": "thin", "pH": 7, "flammable": True, "igniteTemp": 40},  # [INVENTED igniteTemp]
        "compat_targets": [],
    },

    "tar": {
        "defnamePrefix": "RM_Tar",
        "file_name": "RM_Tar.xml",
        "label_shallow": "tar pit",
        "label_deep": "tar pit, deep",
        "description": "Black and patient. It does not drown you so much as keep you.",
        "native_overrides": {"canFreeze": False, "takeSplashes": False},
        "native_overrides_shallow": {"pathCost": 300},  # cited: "pathCost 300 Standable"
        "extension": {"viscosityClass": "heavy", "pH": 7},
        "compat_targets": [],
    },

    "ooze": {
        "defnamePrefix": "RM_Ooze",
        "file_name": "RM_Ooze.xml",
        "label_shallow": "ooze",
        "label_deep": "ooze, deep",
        "description": "Thicker than mud, thinner than slime — the wetland's own compromise.",
        "native_overrides_shallow": {"pathCost": 20},  # [INVENTED] between Mud's 14 and RM_Slime_Liquid's 25
        "native_overrides_deep": {"pathCost": 200, "passability": "Standable"},  # [INVENTED] thick, not impassable
        "extension": {"viscosityClass": "thick", "pH": 7},
        "compat_targets": [],
    },

    "mineralized": {
        "defnamePrefix": "RM_WaterMineral",
        "file_name": "RM_WaterMineral.xml",
        "label_shallow": "mineralized water",
        "label_deep": "mineralized water, deep",
        "description": (
            "Cloudy with dissolved stone, warm from wherever it surfaced. "
            "It leaves a rim on everything it touches."
        ),
        "native_overrides": {"waterBodyType": "Other"},
        "native_overrides_shallow": {"canFreeze": False},
        # pH 9-10 cited as "basic" but explicitly BELOW LiquidCorrosion's
        # pH>10 threshold — mineralized water is basic-leaning, not
        # corrosive, and 9.5 sits inside the cited range without crossing it.
        "extension": {"viscosityClass": "water", "pH": 9.5},
        "compat_targets": [],
    },

    # CARD-2 ruled: coolant is waterBodyType Other, its own bucket (not
    # invented — MECHANICS_CARDS_SITTING_1, cited in §9).
    "coolant": {
        "defnamePrefix": "RM_Coolant",
        "file_name": "RM_Coolant.xml",
        "label_shallow": "coolant canal",
        "label_deep": "coolant canal, deep",
        "description": (
            "Industrial runoff, engineered rather than natural — kept "
            "flowing, kept from freezing, kept out of the fish census."
        ),
        "native_overrides": {
            "waterBodyType": "Other",  # CARD-ruled, §9
            "toxicBuildupFactor": 1,
            "canFreeze": False,
            "glowColor": "(120,200,255)",  # [INVENTED] pale industrial cyan-white for "faint glow"
            "glowRadius": 1,
        },
        "extension": {"viscosityClass": "thin", "pH": 7},
        "compat_targets": [],
    },

    "reactionliquor": {
        "defnamePrefix": "RM_ReactionLiquor",
        "file_name": "RM_ReactionLiquor.xml",
        "label_shallow": "reaction-liquor pool",
        "label_deep": "reaction-liquor pool, deep",
        "description": (
            "Crystal clear and every color at once when the light catches "
            "it wrong. The color isn't life — it's reaction."
        ),
        "native_overrides": {"toxicBuildupFactor": 2, "dangerous": True, "heatPerTick": 0.02},  # [INVENTED]
        "extension": {
            "viscosityClass": "water",
            "pH": 1,  # [INVENTED] "pH extreme" — picked acidic, worse than plain acid's pH 2
            "damageOnContact": {"damageDef": "AcidBurn", "amount": 2},
            "damageOnImmersion": {"damageDef": "AcidBurn", "amount": 5},
            "corrodesApparel": True,
        },
        "compat_targets": [],
    },

    "fuelsap": {
        "defnamePrefix": "RM_FuelSap",
        "file_name": "RM_FuelSap.xml",
        "label_shallow": "fuel-sap liquor",
        "label_deep": "fuel-sap liquor, deep",
        "description": (
            "Distilled and thick, brewed rather than found. It burns the "
            "way the still that made it intended."
        ),
        "native_overrides": {"canFreeze": False, "extinguishesFire": False},  # same ignition prerequisite as propane
        "extension": {"viscosityClass": "thick", "pH": 7, "flammable": True},
        "compat_targets": [],
    },

    "ichor": {
        "defnamePrefix": "RM_Ichor",
        "file_name": "RM_Ichor.xml",
        "label_shallow": "ichor",
        "label_deep": "ichor, deep",
        "description": (
            "Thick and dark, more animal than mineral. Whatever bled this "
            "much is not in this pool anymore."
        ),
        "native_overrides": {},
        # §6: "film=scum, opacity 1" — neither field exists on the shipped
        # RM_LiquidProperties (see module docstring); only viscosity/pH ride.
        "extension": {"viscosityClass": "thick", "pH": 7},
        "compat_targets": [],
    },

    "ammonia": {
        "defnamePrefix": "RM_Ammonia",
        "file_name": "RM_Ammonia.xml",
        "label_shallow": "cryo-ammonia",
        "label_deep": "cryo-ammonia, deep",
        "description": (
            "A solvent that stays liquid well past where water would have "
            "frozen solid, and burns skin more than it drowns lungs."
        ),
        "native_overrides": {"canFreeze": False},
        "extension": {
            "viscosityClass": "water",
            # Real ammonia solution is basic (pH ~11); crosses the >10
            # corrosion threshold on its own, matching the cited "mild
            # corrosion (polar solvent)".
            "pH": 11,
            "damageOnContact": {"damageDef": "Frostbite", "amount": 1},
            "damageOnImmersion": {"damageDef": "Frostbite", "amount": 3},
            "corrodesApparel": True,
        },
        "compat_targets": [],
    },
}

# Rows built out of scope for a cloned suite — compat patch only. See
# module docstring for why "normal water" and "slime" land here.
COMPAT_ONLY_ROWS = {
    "normal_water_baseline": {
        "extension": {"viscosityClass": "water", "pH": 7},
        "compat_targets": [
            "WaterShallow", "WaterDeep",
            "WaterOceanShallow", "WaterOceanDeep",
            "WaterMovingShallow", "WaterMovingChestDeep",
            "Marsh",
        ],
    },
    "slime": {
        "extension": {"viscosityClass": "thick", "pH": 7},
        "compat_targets": ["RM_Slime_Liquid", "AB_LiquidSlime"],
    },
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
    # Uniform across every row, matching Spike A's proven acid precedent —
    # no per-liquid semantic filtering (e.g. stripping dbh_water off
    # propane/tar) is done here; that stays a known simplification, flagged
    # in the item's own notes, not a new decision made in this pass.
    tags = [t for t in tags if t not in ("WaterFreshShallow", "WaterFreshShallowStill")]
    affordances = list(leaf_fields.get("affordances") or [])
    return tags, affordances


def build_terrain_xml(defname, label, description, leaf_fields,
                       native_overrides, extension, render_precedence, extra_tags):
    tags, affordances = union_tags_affordances(leaf_fields, extra_tags)
    is_deep = "Deep" in defname
    texture_path = "Terrain/Surfaces/WaterDeepRamp" if is_deep else "Terrain/Surfaces/WaterShallowRamp"
    lines = []
    lines.append(f'  <TerrainDef ParentName="{"WaterDeepBase" if is_deep else "WaterShallowBase"}">')
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
        lines.append('      <li Class="RimMandrake.FlowWorks.LiquidTypes.RM_LiquidProperties">')
        for fk, fv in extension.items():
            if isinstance(fv, dict):
                lines.append(f"        <{fk}>")
                for ik, iv in fv.items():
                    lines.append(f"          <{ik}>{iv}</{ik}>")
                lines.append(f"        </{fk}>")
            else:
                xv = _enum_xv(fk, fv)
                lines.append(f"        <{fk}>{xv}</{fk}>")
        lines.append("      </li>")
        lines.append("    </modExtensions>")
    lines.append("  </TerrainDef>")
    return "\n".join(lines)


def generate(liquid_key, defs_by_name, out_dir: Path):
    row = LIQUID_ROWS[liquid_key]
    shallow_leaf = load_leaf(defs_by_name, "WaterShallow")
    deep_leaf = load_leaf(defs_by_name, "WaterDeep")

    common = row.get("native_overrides", {})
    shallow_overrides = _merge(common, row.get("native_overrides_shallow"))
    deep_overrides = _merge(common, row.get("native_overrides_deep"))

    prefix = row["defnamePrefix"]
    shallow_xml = build_terrain_xml(
        f"{prefix}Shallow", row["label_shallow"], row["description"],
        shallow_leaf, shallow_overrides, row["extension"],
        RENDER_PRECEDENCE_SHALLOW, extra_tags=["Water"],
    )
    deep_xml = build_terrain_xml(
        f"{prefix}Deep", row["label_deep"], row["description"],
        deep_leaf, deep_overrides, row["extension"],
        RENDER_PRECEDENCE_DEEP, extra_tags=["Water"],
    )

    header = f"""<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  {row['file_name']}         GENERATED by generate_liquid_suite.py
  ============================================================================
  Source leaf: frozen dump OFFICIAL-2026-08-29 (2026-08-29T13-30-02Z),
  defs/TerrainDef.json, WaterShallow/WaterDeep as the live mod stack resolved
  them (POST-PATCH — tags/affordances union-carried from BMT, DBH, TST, as
  measured directly from that capture, not re-typed by hand).

  This regenerates from the LIQUID_ROWS table in
  src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py; edit the table,
  never this file. Regenerate only against a re-frozen official dump, never a
  live capture (dumps decay — CHARTER's instrument order).
  ============================================================================
-->
<Defs>

{shallow_xml}

{deep_xml}

</Defs>
"""
    out_path = out_dir / row["file_name"]
    out_path.write_text(header, encoding="utf-8")
    return out_path, shallow_leaf, deep_leaf


def _compat_operations(extension, targets):
    ops = []
    for target in targets:
        field_xml = []
        for fk, fv in extension.items():
            if isinstance(fv, dict):
                continue  # keep the compat default simple; skip nested damage blocks
            xv = _enum_xv(fk, fv)
            field_xml.append(f"            <{fk}>{xv}</{fk}>")
        ops.append(f"""
    <!-- match-validation: expects exactly 1 hit against /Defs/TerrainDef[defName="{target}"] -->
    <Operation Class="PatchOperationConditional">
      <xpath>/Defs/TerrainDef[defName="{target}"]</xpath>
      <match Class="PatchOperationAddModExtension">
        <xpath>/Defs/TerrainDef[defName="{target}"]</xpath>
        <value>
          <li Class="RimMandrake.FlowWorks.LiquidTypes.RM_LiquidProperties">
{chr(10).join(field_xml)}
          </li>
        </value>
      </match>
    </Operation>""")
    return ops


def build_compat_patch(out_dir: Path):
    """One combined compat-patch index covering every row (and compat-only
    row) that names compat_targets. PatchOperationConditional-guarded on the
    target def actually existing, so a missing donor mod prints nothing
    (never a red error) — the doctrinal default for a patch that "matches
    nothing"."""
    all_ops = []
    all_targets = []
    for key, row in LIQUID_ROWS.items():
        targets = row.get("compat_targets") or []
        if not targets:
            continue
        all_ops.extend(_compat_operations(row["extension"], targets))
        all_targets.extend(targets)
    for key, row in COMPAT_ONLY_ROWS.items():
        targets = row["compat_targets"]
        all_ops.extend(_compat_operations(row["extension"], targets))
        all_targets.extend(targets)

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  RM_LiquidProperties_CompatIndex.xml     GENERATED by generate_liquid_suite.py
  ============================================================================
  The "indexing into every other mod" patch index (design doc §5.2). Every
  Operation here is PatchOperationConditional-guarded on the target def
  actually existing, so a missing donor mod prints nothing (never a red
  error) — the doctrinal default for a patch that "matches nothing".

  🔴 NOT gated on our own packageId via PatchOperationFindMod. Per the
  measured fact in modextension-missing-type-discards-def: a modExtensions
  <li Class="..."> whose type cannot be found in ANY loaded assembly does not
  degrade — it discards the WHOLE target def. Since this patch file ships
  INSIDE mandrake.rm.liquidtypes itself, our own assembly is guaranteed
  present whenever this patch runs at all, so that failure mode cannot occur
  here. It becomes live risk only if this compat block is ever copied into a
  DIFFERENT mod's patch folder (e.g. the RUT layer, §7) without a
  FindMod("mandrake.rm.liquidtypes") guard around it — flagged for whoever
  builds §7, not fixed here.

  Includes: acid (Spike A's proof, onto Odyssey ToxicWater*), a normal-water
  pH7 baseline onto vanilla's own water family + Marsh, and slime (onto
  RM_GelatinousSlime's own RM_Slime_Liquid and Alpha Biomes' AB_LiquidSlime)
  — see the module docstring for why those two are patch-only, no clone.
  ============================================================================
-->
<Patch>
{"".join(all_ops)}
</Patch>
"""
    out_path = out_dir / "RM_LiquidProperties_CompatIndex.xml"
    out_path.write_text(xml, encoding="utf-8")
    return out_path, all_targets


# --- v1 LiquidDef registry rows (LIQUID_REGISTRY_CORE_1, design §3) --------
# Each row is the top-level RimMandrake.FlowWorks.LiquidTypes.LiquidDef
# instance -- the registry BENCH filed this item to build, distinct from the
# LIQUID_ROWS terrain-suite table above (LIQUID_TYPES_MOD_1's older roster,
# which these rows ADOPT rather than regenerate — design §2: "no terrain is
# re-authored").
#
# Scope of THIS pass, and why it stops here: every hard reference below
# resolves under "minimal list + the mod" alone (this item's own verify) --
# vanilla Core defs (WaterShallow/Deep, WaterOceanShallow/Deep, Chemfuel,
# AcidBurn, Frostbite) and FlowWorks' own already-shipped terrain/FluidDefs
# (RM_AcidShallow/Deep, RM_TarShallow/Deep, RM_WaterBrine*, RM_Propane*,
# RM_WaterBoiling*, RM_WaterFrigid*, RM_WaterPoisoned*, RM_Fluid_Water,
# RM_Fluid_Tar). Nothing here references an optional third-party def
# (Odyssey toxic suites, Alpha Biomes slime, VGE astrofuel) -- those need a
# MayRequire-gated PATCH onto the row, not a hard field reference, and are
# left for the pass that builds that adoption.
#
# Explicitly DEFERRED, not forgotten:
#   - Slime RED/GREEN/WHITE/YELLOW: design §7 phase ④ ("slime streams"), its
#     own build slice after this one (②) -- and the only always-loaded slime
#     terrain in this mod is GelatinousSlime's RM_Slime_Liquid, a SEPARATE
#     mod not guaranteed present under "the mod" alone; the tinted
#     RM_Slime_<Colour> defs in ManyWaters/RM_ColoredWater.xml are
#     MayRequire="sarg.alphabiomes" and would red-error a minimal-list load.
#   - Blood: item-only bottled row (design §3), phase ⑤/⑥ -- no bottle
#     ThingDef exists yet (LIQUID_BOTTLE_LOOP_1 territory).
#   - Astrofuel: "adopts VGE" needs a soft MayRequire-gated adoption patch,
#     not a hard bottled.bottle reference -- VGE is absent from the minimal
#     list and a hard reference to VGE_Astrofuel* would fail the def-load
#     verify outright.
#   - trade/cuisineTags/conversions slots: left null across every row here.
#     No economy numbers or cuisine-tag vocabulary were asked for by this
#     item's own verify (row resolution), and inventing marketValue/cuisine
#     tags now risks being wrong ahead of the Bazaar (§9) and RSW cuisine
#     mod that actually consume them.
#
# worldTag convention (unruled before this pass -- WORLDMAP_LIQUID_TAGS_1
# hasn't authored the map side yet): a row's own defName IS its worldTag, so
# that later item can write the LiquidDef's defName straight onto a world
# tile and resolve it with DefDatabase<LiquidDef>.GetNamed(tag). Set on the
# three of the frozen world's four authored bodies this pass gives a full
# row to (boiling ocean, two brine seas, propane lake -- design §3's "every
# authored body gets at least a minimal row, or ruling 5 cannot hold").
LIQUID_DEF_ROWS = {
    "freshwater": {
        "defName": "RM_Liquid_FreshWater",
        "label": "fresh water",
        "description": "Water, unmodified — the baseline every other row is measured against.",
        "viscosityClass": "Water",
        "pH": 7,
        "terrainSuite": {"shallow": "WaterShallow", "deep": "WaterDeep"},
        "canalFluid": "RM_Fluid_Water",
        "thirstQuality": "Potable",
        # Fresh water is the DISTILLATE, not an input -- WRECKED_DISTILLATION_MODULE_1's
        # module OUTPUTS this row. It is still "water family", so it stays
        # true here too per the orchestrator's explicit six-row list; a
        # consumer that refuses same-liquid-in/out is that consumer's own
        # ConfigError to add, not this registry's.
        "distillable": True,
        # LIQUID_BOTTLE_LOOP_1: bottle defName derived from this row's own
        # defName (RM_Liquid_X -> RM_Bottle_X, see build_bottle_thingdefs's
        # own docstring for why that's computed, not retyped, everywhere
        # else in this table). unitsPerBottle=1 matches the only other
        # bottled row shipped so far (chemfuel: "one item IS one unit").
        # No revertsTo/rotsTo here -- fresh water is the thing everything
        # else reverts/distills TO, not a row with its own timer.
        "bottled": {"bottle": "RM_Bottle_FreshWater", "unitsPerBottle": 1,
                    "bucket": "RM_Bucket_FreshWater", "barrel": "RM_Barrel_FreshWater"},
    },
    "saltwater": {
        "defName": "RM_Liquid_SaltWater",
        "label": "salt water",
        "description": "The open sea — undrinkable raw, and the product most conversions start from.",
        "viscosityClass": "Water",
        "pH": 8,  # [INVENTED] real seawater runs ~8.1; mildly basic, below the pH>10 corrosion band
        "terrainSuite": {"shallow": "WaterOceanShallow", "deep": "WaterOceanDeep"},
        "thirstQuality": "Fouled",
        "distillable": True,
        "bottled": {"bottle": "RM_Bottle_SaltWater", "unitsPerBottle": 1,
                    "bucket": "RM_Bucket_SaltWater", "barrel": "RM_Barrel_SaltWater"},
    },
    "boiling": {
        "defName": "RM_Liquid_BoilingWater",
        "label": "boiling water",
        "description": "Kept liquid by heat rather than depth. Steam stands off the surface even in still air.",
        "viscosityClass": "Water",
        "pH": 7,
        "terrainSuite": {"shallow": "RM_WaterBoilingShallow", "deep": "RM_WaterBoilingDeep"},
        "worldTag": "RM_Liquid_BoilingWater",  # frozen world's boiling ocean, LIQUID_BIOMES_MAP_1
        "distillable": True,
        # revertsTo/revertTicks (bottled boiling -> fresh once it cools) is
        # the item's own named special behavior but is DEFERRED this pass,
        # same reasoning as icy below: LiquidBottledForm.ConfigErrors
        # requires revertTicks >= 1 the moment revertsTo is set, and nothing
        # in this build consumes it yet -- see LIQUID_BOTTLE_LOOP_1's
        # stopping note. Row data only, no invented timer duration.
        "bottled": {"bottle": "RM_Bottle_BoilingWater", "unitsPerBottle": 1,
                    "bucket": "RM_Bucket_BoilingWater", "barrel": "RM_Barrel_BoilingWater"},
    },
    "icy": {
        "defName": "RM_Liquid_IcyWater",
        "label": "icy water",
        "description": "Water cold enough to steal warmth through boots and gloves alike.",
        "viscosityClass": "Thick",
        "pH": 7,
        "damageOnContact": {"damageDef": "Frostbite", "amount": 1},
        "damageOnImmersion": {"damageDef": "Frostbite", "amount": 3},
        "corrodesApparel": False,
        "terrainSuite": {"shallow": "RM_WaterFrigidShallow", "deep": "RM_WaterFrigidDeep"},
        "distillable": True,
        # See "boiling" above -- revert-on-bottle deferred, no consumer yet.
        "bottled": {"bottle": "RM_Bottle_IcyWater", "unitsPerBottle": 1,
                    "bucket": "RM_Bucket_IcyWater", "barrel": "RM_Barrel_IcyWater"},
    },
    "toxic": {
        "defName": "RM_Liquid_ToxicWater",
        "label": "toxic water",
        "description": "Water carrying more than it should. Nothing in it is inert.",
        "viscosityClass": "Water",
        "pH": 7,
        "terrainSuite": {"shallow": "RM_WaterPoisonedShallow", "deep": "RM_WaterPoisonedDeep"},
        "thirstQuality": "Toxic",
        "distillable": True,
        "bottled": {"bottle": "RM_Bottle_ToxicWater", "unitsPerBottle": 1,
                    "bucket": "RM_Bucket_ToxicWater", "barrel": "RM_Barrel_ToxicWater"},
    },
    "acid": {
        "defName": "RM_Liquid_AcidWater",
        "label": "acid water",
        "description": "Water gone wrong — the color isn't life, it's reaction.",
        "viscosityClass": "Water",
        "pH": 2,
        "damageOnContact": {"damageDef": "AcidBurn", "amount": 1},
        "damageOnImmersion": {"damageDef": "AcidBurn", "amount": 3},
        "corrodesApparel": True,
        "terrainSuite": {"shallow": "RM_AcidShallow", "deep": "RM_AcidDeep"},
        "bottled": {"bottle": "RM_Bottle_AcidWater", "unitsPerBottle": 1,
                    "bucket": "RM_Bucket_AcidWater", "barrel": "RM_Barrel_AcidWater"},
    },
    "tar": {
        "defName": "RM_Liquid_Tar",
        "label": "tar",
        "description": "Black and patient. It does not drown you so much as keep you.",
        "viscosityClass": "Heavy",
        "pH": 7,
        "terrainSuite": {"shallow": "RM_TarShallow", "deep": "RM_TarDeep"},
        "canalFluid": "RM_Fluid_Tar",
        "bottled": {"bottle": "RM_Bottle_Tar", "unitsPerBottle": 1,
                    "bucket": "RM_Bucket_Tar", "barrel": "RM_Barrel_Tar"},
    },
    "brine": {
        "defName": "RM_Liquid_Brine",
        "label": "brine",
        "description": "Salt concentrated past drinking, dense enough to feel underfoot.",
        "viscosityClass": "Thick",
        "pH": 8,  # [INVENTED] matches the brine terrain's own extension value
        "corrodesApparel": False,
        "terrainSuite": {"shallow": "RM_WaterBrineShallow", "deep": "RM_WaterBrineDeep"},
        # No canalFluid: RM_Fluid_Brine does not exist yet -- FlowWorks_Fluids.xml
        # ships only water and tar this pass. Owed to whoever authors the
        # brine canal's own temporary fill terrains.
        "worldTag": "RM_Liquid_Brine",  # frozen world's two brine seas, LIQUID_BIOMES_MAP_1
        "thirstQuality": "Fouled",
        "distillable": True,
        "bottled": {"bottle": "RM_Bottle_Brine", "unitsPerBottle": 1,
                    "bucket": "RM_Bucket_Brine", "barrel": "RM_Barrel_Brine"},
    },
    "propane": {
        "defName": "RM_Liquid_Propane",
        "label": "liquid propane",
        "description": "Thin, cold, and utterly indifferent to fire until something else provides the spark.",
        "viscosityClass": "Thin",
        "pH": 7,
        "flammable": True,
        "igniteTemp": 40,  # [INVENTED] matches the propane terrain's own extension value
        "terrainSuite": {"shallow": "RM_PropaneShallow", "deep": "RM_PropaneDeep"},
        # No canalFluid: RM_Fluid_Propane does not exist yet, same gap as brine.
        "worldTag": "RM_Liquid_Propane",  # frozen world's propane lake under Umbra, LIQUID_BIOMES_MAP_1
        "bottled": {"bottle": "RM_Bottle_Propane", "unitsPerBottle": 1,
                    "bucket": "RM_Bucket_Propane", "barrel": "RM_Barrel_Propane"},
    },
    "chemfuel": {
        "defName": "RM_Liquid_Chemfuel",
        "label": "chemfuel",
        "description": "Refined fuel, adopted as-is — the vanilla item already is this liquid's bottled form.",
        "viscosityClass": "Water",  # [INVENTED] thin/pourable, no engine field measures it
        "pH": 7,
        "flammable": True,
        # Adopts the vanilla ThingDef directly (design §3: "adopts the vanilla
        # item") rather than authoring a new bottle -- one Chemfuel item IS
        # one unit of this liquid. No terrain/canal form in v1.
        "bottled": {"bottle": "Chemfuel", "unitsPerBottle": 1},
    },
}


def _xv(v):
    if v is True:
        return "true"
    if v is False:
        return "false"
    return v


# RimWorld parses an enum field with a CASE-SENSITIVE Enum.Parse
# (Verse.ParseHelper.FromString). A mis-cased value throws while the
# modExtensions <li> is being read, and DirectXmlToObjectNew then discards
# THE WHOLE TARGET DEF rather than degrading. That is how
# <viscosityClass>water</viscosityClass> deleted WaterShallow, WaterDeep,
# WaterMovingShallow, WaterMovingChestDeep, WaterOceanShallow,
# WaterOceanDeep, ToxicWaterShallow, ToxicWaterDeep and Marsh from the live
# game - every river, lake and coast then generated its channel and painted
# it with a null terrain, so no map had water at all
# (QUICKTEST_RIVER_WATER_MISSING_1, measured 2026-09-18).
# Normalise here, and refuse an unknown member rather than emitting XML that
# will silently eat a def.
_VISCOSITY_MEMBERS = ("Thin", "Water", "Thick", "Heavy")  # Source/LiquidTypes/RM_LiquidProperties.cs


def _enum_xv(field, value):
    """Case-correct a known enum field; raise on a value the enum lacks."""
    if field != "viscosityClass":
        return _xv(value)
    for member in _VISCOSITY_MEMBERS:
        if str(value).lower() == member.lower():
            return member
    raise ValueError(
        "viscosityClass %r is not a LiquidViscosityClass member %r - emitting it "
        "would make RimWorld discard the entire target def." % (value, _VISCOSITY_MEMBERS)
    )


def _damage_spec_xml(indent, tag, spec):
    if not spec:
        return []
    return [
        f"{indent}<{tag}>",
        f"{indent}  <damageDef>{spec['damageDef']}</damageDef>",
        f"{indent}  <amount>{spec['amount']}</amount>",
        f"{indent}</{tag}>",
    ]


def build_liquiddef_xml(row):
    lines = ["  <RimMandrake.FlowWorks.LiquidTypes.LiquidDef>"]
    lines.append(f"    <defName>{row['defName']}</defName>")
    lines.append(f"    <label>{row['label']}</label>")
    lines.append(f"    <description>{row['description']}</description>")
    if "viscosityClass" in row:
        lines.append(f"    <viscosityClass>{_enum_xv('viscosityClass', row['viscosityClass'])}</viscosityClass>")
    if "pH" in row:
        lines.append(f"    <pH>{row['pH']}</pH>")
    lines += _damage_spec_xml("    ", "damageOnContact", row.get("damageOnContact"))
    lines += _damage_spec_xml("    ", "damageOnImmersion", row.get("damageOnImmersion"))
    if "corrodesApparel" in row:
        lines.append(f"    <corrodesApparel>{_xv(row['corrodesApparel'])}</corrodesApparel>")
    if "flammable" in row:
        lines.append(f"    <flammable>{_xv(row['flammable'])}</flammable>")
    if "igniteTemp" in row:
        lines.append(f"    <igniteTemp>{row['igniteTemp']}</igniteTemp>")
    if row.get("distillable"):
        lines.append("    <distillable>true</distillable>")

    suite = row.get("terrainSuite")
    if suite:
        lines.append("    <terrainSuite>")
        for slot in ("shallow", "deep", "chestDeep"):
            if suite.get(slot):
                lines.append(f"      <{slot}>{suite[slot]}</{slot}>")
        lines.append("    </terrainSuite>")

    if row.get("canalFluid"):
        lines.append(f"    <canalFluid>{row['canalFluid']}</canalFluid>")

    bottled = row.get("bottled")
    if bottled:
        lines.append("    <bottled>")
        lines.append(f"      <bottle>{bottled['bottle']}</bottle>")
        lines.append(f"      <unitsPerBottle>{bottled.get('unitsPerBottle', 1)}</unitsPerBottle>")
        # LIQUID_BOTTLE_LOOP_1 third slice: bucket/barrel are optional
        # siblings, same "bottled" slot as bottle -- see LiquidBottledForm.
        if bottled.get("bucket"):
            lines.append(f"      <bucket>{bottled['bucket']}</bucket>")
            lines.append(f"      <unitsPerBucket>{bottled.get('unitsPerBucket', 5)}</unitsPerBucket>")
        if bottled.get("barrel"):
            lines.append(f"      <barrel>{bottled['barrel']}</barrel>")
            lines.append(f"      <unitsPerBarrel>{bottled.get('unitsPerBarrel', 25)}</unitsPerBarrel>")
        if bottled.get("revertsTo"):
            lines.append(f"      <revertsTo>{bottled['revertsTo']}</revertsTo>")
            lines.append(f"      <revertTicks>{bottled['revertTicks']}</revertTicks>")
        if bottled.get("rotsTo"):
            lines.append(f"      <rotsTo>{bottled['rotsTo']}</rotsTo>")
            lines.append(f"      <rotTicks>{bottled['rotTicks']}</rotTicks>")
        lines.append("    </bottled>")

    if row.get("worldTag"):
        lines.append(f"    <worldTag>{row['worldTag']}</worldTag>")

    if row.get("thirstQuality"):
        lines.append(f"    <thirstQuality>{row['thirstQuality']}</thirstQuality>")

    lines.append("  </RimMandrake.FlowWorks.LiquidTypes.LiquidDef>")
    return "\n".join(lines)


def build_liquiddef_registry(out_dir: Path):
    """Emits the v1 LiquidDef registry rows (LIQUID_REGISTRY_CORE_1, design
    §3) into one file. See LIQUID_DEF_ROWS' own module comment for exactly
    which rows this pass covers and why the rest are deferred."""
    blocks = [build_liquiddef_xml(row) for row in LIQUID_DEF_ROWS.values()]
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  RM_LiquidDefRegistry.xml         GENERATED by generate_liquid_suite.py
  ============================================================================
  The v1 LiquidDef registry (LIQUID_REGISTRY_CORE_1, design §3). Regenerates
  from LIQUID_DEF_ROWS in
  src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py; edit the table,
  never this file.

  Ten rows this pass: fresh/salt/boiling/icy/toxic/acid water, tar, brine,
  propane, chemfuel — every one resolving only against vanilla Core defs and
  FlowWorks' own already-shipped terrain/FluidDefs, so it loads clean under
  a minimal mod list with no third-party dependency. Slime (RED/GREEN/WHITE/
  YELLOW), blood and astrofuel are deliberately NOT here — see the table's
  own module comment for why each is deferred to a later build phase.
  ============================================================================
-->
<Defs>

{(chr(10) * 2).join(blocks)}

</Defs>
"""
    out_path = out_dir / "RM_LiquidDefRegistry.xml"
    out_path.write_text(xml, encoding="utf-8")
    return out_path


# --- LIQUID_BOTTLE_LOOP_1: the container-ThingDef emission this item's own
# scope needed and the generator did not yet have (see the item's unblock
# note -- this was never actually LIQUID_REGISTRY_CORE_1's gap, it was this
# item's own). One filled ThingDef per LIQUID_DEF_ROWS row per size slot
# (`bottle` always; `bucket`/`barrel` where the row's own dict names one) --
# a row that ADOPTS an existing vanilla/foreign item for a slot instead
# (chemfuel -> Chemfuel, bottle-only) is skipped for that slot -- no new
# ThingDef to author, same as the row's own comment says.
#
# RM_BottleEmpty/RM_BottleDirty/RM_BucketEmpty/RM_BucketDirty/
# RM_BarrelEmpty/RM_BarrelDirty and the shared RM_*ItemBase/
# RM_LiquidBottleItems category are HAND-AUTHORED (Defs/LiquidTypes/ThingDefs/
# RM_LiquidBottles_Base.xml) -- they are liquid-agnostic and never generated.
# This function's ONLY job is the filled state, per row per size.
_CONTAINER_SIZE_META = {
    # size key -> (bottled-dict key, ParentName, defName prefix, noun,
    #              nutrition-per-unit multiplier, gets-ingestible-block)
    "bottle": ("bottle", "RM_BottleItemBase", "RM_Bottle_", "bottle", 1, True),
    "bucket": ("bucket", "RM_BucketItemBase", "RM_Bucket_", "bucket", 5, True),
    # Barrels never get an <ingestible> block -- bulk TRADE good, not a
    # food item a pawn drinks from directly. See this module's own header
    # and RM_LiquidBottles_Base.xml's.
    "barrel": ("barrel", "RM_BarrelItemBase", "RM_Barrel_", "barrel", 25, False),
}


def build_bottle_thingdef_xml(container_defname, liquid_defname, liquid_label, description,
                               size="bottle", thirst_quality=None):
    _, parent, prefix, noun, nutrition_mult, gets_ingestible = _CONTAINER_SIZE_META[size]
    lines = [f'  <ThingDef ParentName="{parent}">']
    lines.append(f"    <defName>{container_defname}</defName>")
    lines.append(f"    <label>{('bottled' if size == 'bottle' else size + 'ed')} {liquid_label}</label>")
    lines.append(f"    <description>A {noun} holding {liquid_label}. {description}</description>")
    lines.append("    <modExtensions>")
    lines.append('      <li Class="RimMandrake.FlowWorks.LiquidTypes.RM_BottledLiquidExtension">')
    lines.append(f"        <liquid>{liquid_defname}</liquid>")
    if size != "bottle":
        lines.append(f"        <size>{size.capitalize()}</size>")
    lines.append("      </li>")
    lines.append("    </modExtensions>")
    # LIQUID_BOTTLE_LOOP_1: only a row the registry already marked drinkable
    # (thirstQuality set -- fresh/salt/toxic/brine water) becomes ingestible
    # at all, and only for the bottle/bucket size tiers. That is an existing,
    # non-invented signal: boiling water would scald, icy water gives
    # frostbite, and acid/tar/propane are hazards or fuel, never a drink --
    # none of those five rows carry thirstQuality, so none of them get this
    # block. IngestionOutcomeDoer_BottleResidue (Source/LiquidTypes/) reads
    # RM_BottledLiquidExtension generically and leaves a dirty/empty
    # same-sized container behind per the Mod Settings toggle; DBH
    # registration (LIQUID_THIRST_CHAIN_1) layers its own hydration/thirst
    # effect on the SAME ingestion without touching this block.
    if thirst_quality and gets_ingestible:
        lines.append("    <statBases>")
        lines.append(f"      <Nutrition>{0.05 * nutrition_mult}</Nutrition>")
        lines.append("    </statBases>")
        lines.append("    <ingestible>")
        lines.append("      <foodType>Fluid</foodType>")
        lines.append("      <preferability>DesperateOnlyForHumanlikes</preferability>")
        lines.append("      <outcomeDoers>")
        lines.append('        <li Class="RimMandrake.FlowWorks.LiquidTypes.IngestionOutcomeDoer_BottleResidue" />')
        lines.append("      </outcomeDoers>")
        lines.append("    </ingestible>")
    lines.append("  </ThingDef>")
    return "\n".join(lines)


def build_bottle_thingdefs(out_dir: Path):
    """Emits RM_Bottle_<X>/RM_Bucket_<X>/RM_Barrel_<X> for every
    LIQUID_DEF_ROWS row and every size slot its own `bottled` dict names
    under the matching RM_<Size>_ prefix -- i.e. every row/size this pass
    generates a container for, as opposed to a slot that ADOPTS an existing
    item (chemfuel's bottle -> Chemfuel) and needs none. See this function's
    own module comment."""
    blocks = []
    generated_for = []
    adopted = []
    for row in LIQUID_DEF_ROWS.values():
        bottled = row.get("bottled")
        if not bottled:
            continue
        for size, (dict_key, _parent, prefix, _noun, _mult, _ing) in _CONTAINER_SIZE_META.items():
            container_defname = bottled.get(dict_key)
            if not container_defname:
                continue
            if not container_defname.startswith(prefix):
                adopted.append((row["defName"], container_defname))
                continue
            blocks.append(build_bottle_thingdef_xml(
                container_defname, row["defName"], row["label"], row["description"],
                size=size, thirst_quality=row.get("thirstQuality"),
            ))
            generated_for.append(container_defname)

    adopted_note = (
        "  Adopted, not generated: " + ", ".join(f"{d} -> {b}" for d, b in adopted) + "."
        if adopted else "  Nothing adopted this pass."
    )
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  RM_LiquidBottles.xml         GENERATED by generate_liquid_suite.py
  ============================================================================
  LIQUID_BOTTLE_LOOP_1. One filled ThingDef per LIQUID_DEF_ROWS row per size
  slot (bottle/bucket/barrel) its own `bottled` dict names under the
  matching RM_<Size>_ prefix. Regenerates from that table in
  src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py; edit the table,
  never this file.

  RM_BottleEmpty/RM_BottleDirty/RM_BucketEmpty/RM_BucketDirty/
  RM_BarrelEmpty/RM_BarrelDirty and the RM_*ItemBase families are
  HAND-AUTHORED in the sibling RM_LiquidBottles_Base.xml, not here — they
  are liquid-agnostic and every generated container ParentName-inherits
  from the matching size's ItemBase.

{adopted_note}

  The fill/use/dirty/wash JobDriver/WorkGiver pair is built and GENERIC
  across all three sizes (Source/LiquidTypes/{{RM_LiquidBottleUtility,
  WorkGiver_FillBottle,JobDriver_FillBottle,WorkGiver_WashBottle,
  JobDriver_WashBottle,IngestionOutcomeDoer_BottleResidue}}.cs), reading
  RM_BottledLiquidExtension.size rather than branching per size in XML or
  C#. The dirty-stage Mod Settings toggle ships
  (RimMandrakeFlowWorksSettings.bottleDirtyStageEnabled, default ON). Only
  a row with `thirstQuality` set gets an `<ingestible>` block, and only on
  its bottle/bucket siblings — never barrel, the bulk TRADE good — see
  build_bottle_thingdef_xml's own comment.

  Still deliberately NOT built (LIQUID_BOTTLE_LOOP_1's own stopping note):
  filling from a TANK (the universal cargo tank design §6/§9 names, and the
  spec's own "barrels... plus fill/empty bills at a tank" — no tank building
  exists yet anywhere in FlowWorks or WreckedMachines, so all three sizes
  this pass fill from terrain only), and revertsTo/rotsTo row data
  (boiling/icy revert-on-bottle, blood-rot — LiquidBottledForm.ConfigErrors
  requires a real revertTicks/rotTicks the moment either is set, and nothing
  reads them yet).
  ============================================================================
-->
<Defs>

{(chr(10) * 2).join(blocks)}

</Defs>
"""
    out_path = out_dir / "RM_LiquidBottles.xml"
    out_path.write_text(xml, encoding="utf-8")
    return out_path, generated_for


def main():
    root = Path(__file__).resolve().parent.parent
    # Merged into FlowWorks 2026-09-16 (FLOWWORKS_BUILD_PROGRAM_1 Phase 1):
    # the LiquidTypes trees are subfolders of one mod now, and the compat
    # index lives under the mod's real Patches/ root — under Defs/ it was
    # never loaded as a patch at all (ModContentPack.LoadPatches scans
    # "Patches/" only) while the def loader choked on its <Patch> root.
    terrain_dir = root / "Defs" / "LiquidTypes" / "TerrainDefs"
    patch_dir = root / "Patches" / "LiquidTypes"
    liquiddef_dir = root / "Defs" / "LiquidTypes" / "LiquidDefs"
    thingdef_dir = root / "Defs" / "LiquidTypes" / "ThingDefs"
    terrain_dir.mkdir(parents=True, exist_ok=True)
    patch_dir.mkdir(parents=True, exist_ok=True)
    liquiddef_dir.mkdir(parents=True, exist_ok=True)
    thingdef_dir.mkdir(parents=True, exist_ok=True)

    with open(DUMP_PATH, encoding="utf-8") as f:
        dump = json.load(f)
    defs_by_name = {d["defName"]: d for d in dump["defs"]}

    for key in LIQUID_ROWS:
        out_path, shallow_leaf, deep_leaf = generate(key, defs_by_name, terrain_dir)
        print(f"WROTE {out_path}")

    patch_path, targets = build_compat_patch(patch_dir)
    print(f"WROTE {patch_path}")
    print(f"  match-validation targets (expect 1 hit each via validate_patch.py --defs): {targets}")

    liquiddef_path = build_liquiddef_registry(liquiddef_dir)
    print(f"WROTE {liquiddef_path}")

    bottle_path, generated_for = build_bottle_thingdefs(thingdef_dir)
    print(f"WROTE {bottle_path}")
    print(f"  bottle ThingDefs generated for: {generated_for}")


if __name__ == "__main__":
    sys.exit(main())

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
        lines.append('      <li Class="RimMandrake.LiquidTypes.RM_LiquidProperties">')
        for fk, fv in extension.items():
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
  src/RimMandrake/LiquidTypes/Tools/generate_liquid_suite.py; edit the table,
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
            xv = "true" if fv is True else "false" if fv is False else fv
            field_xml.append(f"            <{fk}>{xv}</{fk}>")
        ops.append(f"""
    <!-- match-validation: expects exactly 1 hit against /Defs/TerrainDef[defName="{target}"] -->
    <Operation Class="PatchOperationConditional">
      <xpath>/Defs/TerrainDef[defName="{target}"]</xpath>
      <match Class="PatchOperationAddModExtension">
        <xpath>/Defs/TerrainDef[defName="{target}"]</xpath>
        <value>
          <li Class="RimMandrake.LiquidTypes.RM_LiquidProperties">
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


def main():
    root = Path(__file__).resolve().parent.parent
    terrain_dir = root / "Defs" / "TerrainDefs"
    patch_dir = root / "Defs" / "Patches"
    terrain_dir.mkdir(parents=True, exist_ok=True)
    patch_dir.mkdir(parents=True, exist_ok=True)

    with open(DUMP_PATH, encoding="utf-8") as f:
        dump = json.load(f)
    defs_by_name = {d["defName"]: d for d in dump["defs"]}

    for key in LIQUID_ROWS:
        out_path, shallow_leaf, deep_leaf = generate(key, defs_by_name, terrain_dir)
        print(f"WROTE {out_path}")

    patch_path, targets = build_compat_patch(patch_dir)
    print(f"WROTE {patch_path}")
    print(f"  match-validation targets (expect 1 hit each via validate_patch.py --defs): {targets}")


if __name__ == "__main__":
    sys.exit(main())

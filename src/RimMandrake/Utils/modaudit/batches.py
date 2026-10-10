#!/usr/bin/env python3
"""modaudit/batches.py - partition the audit universe into self-contained assessor batches.

    python3 src/RimMandrake/Utils/modaudit/batches.py [--target 45]

Reads facts/mod_facts.jsonl; writes design/RimMandrake/mod_audit/batches/batch_NN.json and batches/INDEX.md.

The CATEGORY is a ROUTING label so one assessor sees related mods together (it can compare overlapping creature
packs, or frameworks against their dependants). It is not a verdict and an assessor may say a mod is misfiled.
Rules run in order (first match wins), over measured facts plus the mod's own name/description text:
  ours_rm / ours_rsw_rut   our own mods (by packageId tier)
  frameworks_libraries     Core/DLC; or code with < 10 defs that another universe mod depends on / names itself a
                           framework, library, API, core, loader
  star_wars_donors         Star Wars text in name/packageId/description
  vanilla_expanded         a Vanilla Expanded / Oskar Potocki mod
  biomes_world             BiomeDef/TerrainDef/WorldObjectDef/GenStep/MapGenerator/TileMutator/Landmark dominant
  creatures_animals        PawnKindDef + race-carrying ThingDefs dominant, and no FactionDef
  factions_pawns           FactionDef / XenotypeDef / GeneDef / BackstoryDef / IdeoPresetDef / PreceptDef present
  weapons_apparel          weapon/armor/apparel words, or many ThingDefs + SoundDefs with weapon words
  buildings_production     furniture/building/production/power/storage words or DesignationCategory/Recipe heavy
  code_tweaks_qol_ui       code-only behaviour mods nobody depends on (DLL, < 10 defs), or UI/QoL/performance words
  misc_content             everything else
A category over `target` mods is split into numbered chunks of near-equal size (keeping universe order inside);
a batch file lists, per mod, the facts an assessor needs without opening mod_facts.jsonl.
"""
import argparse
import json
import math
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

WORLD_TYPES = ("BiomeDef", "TerrainDef", "WorldObjectDef", "GenStepDef", "MapGeneratorDef", "TileMutatorDef",
               "LandmarkDef", "RiverDef", "RoadDef", "WeatherDef", "GameConditionDef", "PlanetLayerDef")
FACTION_TYPES = ("FactionDef", "XenotypeDef", "GeneDef", "BackstoryDef", "IdeoPresetDef", "PreceptDef", "MemeDef",
                 "RulePackDef", "CultureDef", "AlienRace.ThingDef_AlienRace")
SW_WORDS = re.compile(r"star ?wars|outer ?rim|jedi|\bsith\b|mandalor|kotor|\bclone wars\b|wookie|wookiee|tatooine|"
                      r"\bgalactic empire\b|\brebel alliance\b|lightsaber|\bdroid ?depot\b|\bswbestiary\b", re.I)
VE_WORDS = re.compile(r"^vanillaexpanded\.|^oskarpotocki\.|^vanilla(?:factions|furniture|weapons|apparel)expanded|"
                      r"\bvanilla [a-z ]*expanded\b", re.I)
WEAPON_WORDS = re.compile(r"weapon|armou?r|apparel|gun|rifle|blaster|sword|melee|clothing|helmet|outfit|ammo", re.I)
BUILD_WORDS = re.compile(r"furniture|building|production|power|storage|door|wall|floor|bench|crafting|kitchen|"
                         r"farm|bed|light|turret|structure|workbench|fridge|shelf", re.I)
FRAMEWORK_WORDS = re.compile(r"framework|librar|\blib\b|\bapi\b|harmony|hugslib|prepatcher|\bcore\b|loader|"
                             r"utilit|toolkit|\bshared\b", re.I)
UI_WORDS = re.compile(r"\bui\b|interface|quality of life|\bqol\b|performance|optimi[sz]|tab\b|menu|speed|"
                      r"tweak|fix|bug|camera|zoom|overlay|alert|notification|search|sort|mod manager|log", re.I)


def _n(d, *types):
    return sum(v for k, v in (d or {}).items() if k in types or any(k.endswith("." + t) for t in types))


def categorize(f):
    """Routing category for one facts row. Pure; selftested."""
    pid = f["packageId"].lower()
    if f["class"] == "OURS":
        return "ours_rm" if pid.startswith("mandrake.rm.") else "ours_rsw_rut"
    if f["class"] == "CORE_DLC":
        return "frameworks_libraries"
    text = " ".join([f.get("name") or "", pid, (f.get("description") or "")[:1500]])
    dt = f.get("defs_by_type") or {}
    total = f.get("def_total") or 0
    if (f.get("dll_count") or 0) > 0 and total < 10 and (f.get("texture_count") or 0) < 40 and \
            not SW_WORDS.search(text):
        # a library is something others build on: a dependant in the universe, or it says so in its name
        if f.get("dependants") or FRAMEWORK_WORDS.search((f.get("name") or "") + " " + pid):
            return "frameworks_libraries"
        return "code_tweaks_qol_ui"
    if total == 0 and (f.get("dll_count") or 0) == 0 and not SW_WORDS.search(text):
        return "misc_content"
    if SW_WORDS.search(f.get("name") or "") or SW_WORDS.search(pid) or SW_WORDS.search(text):
        return "star_wars_donors"
    if VE_WORDS.search(pid) or VE_WORDS.search(f.get("name") or ""):
        return "vanilla_expanded"
    world = _n(dt, *WORLD_TYPES)
    pk = _n(dt, "PawnKindDef")
    fac = _n(dt, *FACTION_TYPES)
    if world and world * 3 >= total:
        return "biomes_world"
    if _n(dt, "BiomeDef"):
        return "biomes_world"
    if pk and not _n(dt, "FactionDef") and pk * 4 >= total * 0.5 and fac == 0:
        return "creatures_animals"
    if fac:
        return "factions_pawns"
    if WEAPON_WORDS.search(f.get("name") or ""):
        return "weapons_apparel"
    if BUILD_WORDS.search(f.get("name") or ""):
        return "buildings_production"
    if UI_WORDS.search(f.get("name") or ""):
        return "code_tweaks_qol_ui"
    if pk:
        return "creatures_animals"
    if WEAPON_WORDS.search(text):
        return "weapons_apparel"
    if BUILD_WORDS.search(text):
        return "buildings_production"
    return "misc_content"


def split_balanced(groups, target=45):
    """{cat: [items]} -> {name: [items]}: a group over target*1.25 is cut into round(n/target) near-equal chunks
    named cat_1..cat_k. Pure; selftested."""
    out = OrderedDict()
    for cat, items in groups.items():
        if len(items) <= target * 1.25:
            out[cat] = list(items)
            continue
        k = max(1, int(round(len(items) / float(target))))   # chunk size nearest the target
        if k == 1:
            out[cat] = list(items)
            continue
        size = math.ceil(len(items) / float(k))
        for i in range(k):
            out["%s_%d" % (cat, i + 1)] = list(items[i * size:(i + 1) * size])
    return out


def merge_small(parts, floor=8):
    """Fold batches under `floor` mods into misc so no assessor gets a near-empty file."""
    out = OrderedDict()
    spill = []
    for k, v in parts.items():
        if len(v) < floor and not k.startswith("ours"):
            spill += [(k, x) for x in v]
        else:
            out[k] = v
    if spill:
        cands = [k for k in out if not k.startswith("ours")]
        if not cands:
            out["misc_content"] = []
            cands = ["misc_content"]
        dest = min(cands, key=lambda k: len(out[k]))      # the smallest non-ours batch absorbs the leftovers
        out[dest] = out[dest] + [x for _, x in spill]
    return out


BATCH_FIELDS = ("packageId", "name", "author", "class", "membership", "full_latest_position", "folder", "workshop_id",
                "steam_url", "about_url", "supports_1_6", "description", "dependencies", "dependants", "dependants_ours", "load_after", "load_before",
                "incompatible_with", "disk_mb", "disk_by_kind", "texture_count", "texture_decoded_mb_est",
                "dll_count", "dlls", "dll_flags", "ships_source", "def_total", "defs_by_type", "patch_ops_all",
                "patched_def_types", "patch_findmod_names", "patches_mods", "patches_ours_refs", "patched_by",
                "patched_by_ours_refs", "runtime_scope", "log_error_occurrences", "log_errors_distinct",
                "log_error_samples", "log_evidence_kinds", "log_chatter_lines", "static_ctors", "tps_cost",
                "memory_cost", "source_url", "source_kind", "source_confidence", "source_license", "source_last_push",
                "source_archived", "source_note", "in_vendor_sources_md", "mentioned_in_forbidden_mods_md",
                "prior_verdict_2026_08_30", "prior_note_2026_08_30", "src")


def main(argv=None):
    from universe import AUDIT_DIR, FACTS_DIR, ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=45)
    a = ap.parse_args(argv)
    facts = [json.loads(l) for l in open(os.path.join(FACTS_DIR, "mod_facts.jsonl"))]
    groups = OrderedDict()
    order = ["frameworks_libraries", "code_tweaks_qol_ui", "star_wars_donors", "vanilla_expanded", "biomes_world",
             "creatures_animals", "factions_pawns", "weapons_apparel", "buildings_production", "misc_content",
             "ours_rm", "ours_rsw_rut"]
    for c in order:
        groups[c] = []
    for f in facts:
        groups[categorize(f)].append(f)
    parts = merge_small(split_balanced(groups, a.target))
    bdir = os.path.join(AUDIT_DIR, "batches")
    os.makedirs(bdir, exist_ok=True)
    for old in os.listdir(bdir):
        if old.startswith("batch_") and old.endswith(".json"):
            os.remove(os.path.join(bdir, old))
    index = ["# Mod audit batches", "",
             "Generated by `python3 src/RimMandrake/Utils/modaudit/batches.py` from `facts/mod_facts.jsonl`. "
             "The category routes related mods to one assessor; it is not a verdict.", "",
             "| batch | category | mods | ours | third-party | core/DLC |", "|---|---|---|---|---|---|"]
    n = 0
    for name, items in parts.items():
        if not items:
            continue
        n += 1
        fn = "batch_%02d.json" % n
        body = {"batch": n, "category": name, "count": len(items),
                "instructions": "Assess every mod per design/RimMandrake/mod_audit/RUBRIC.md against "
                                "design/RimMandrake/mod_audit/SCENARIO_BRIEF.md; write assessments/batch_%02d.jsonl. "
                                "Whole-session context (TPS, memory, log probe): facts/session_context.json." % n,
                "mods": [{k: f.get(k) for k in BATCH_FIELDS} for f in items]}
        with open(os.path.join(bdir, fn), "w") as fh:
            json.dump(body, fh, indent=1, ensure_ascii=False)
        cl = [f["class"] for f in items]
        index.append("| `%s` | %s | %d | %d | %d | %d |" % (fn, name, len(items), cl.count("OURS"),
                                                            cl.count("THIRD_PARTY"), cl.count("CORE_DLC")))
    index.append("")
    index.append("Total: %d mods in %d batches." % (len(facts), n))
    open(os.path.join(bdir, "INDEX.md"), "w").write("\n".join(index) + "\n")
    print("batches: %d mods -> %d batches: %s" % (len(facts), n, ", ".join("%s=%d" % (k, len(v)) for k, v in parts.items() if v)))


if __name__ == "__main__":
    main()

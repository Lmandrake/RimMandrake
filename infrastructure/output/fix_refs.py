#!/usr/bin/env python3
"""fix_refs.py — the reference half of the option-B restructure.

`do_restructure.sh` moved the files; this repoints what pointed at them.
Two passes, both run from the repo root:

  1. TARGETED — code that builds a path out of *segments*
     (`os.path.join(ROOT, "custom_patches", ...)`) or derives the repo root by
     counting `..` upwards. A textual sweep cannot see either, and every one of
     them is load-bearing: `Utils/` went from one level below the root to three,
     so every `dirname(dirname(...))` in it now stops at `src/RimMandrake/`.

  2. SWEEP — plain repo-relative path literals in tracked `.md .py .sh .json`,
     which is plan §4 dep 5 (`refresh.py` x26, `deploy_custom_mods.py` x24,
     `whats_new.py` x18, `doc_budget.py` x10). Single pass over an alternation
     so a replacement is never re-matched; a lookbehind stops it firing inside a
     path that is already correct.

`infrastructure/output/` and `infrastructure/disposing/` are excluded: they hold
audits and quarantined docs that quote superseded paths on purpose, which is
also why `check_refs.py` skips scanning them.
"""
import os
import re
import subprocess

STAMP = "observed/2026-08-13_pre-restructure"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------- pass 1
# (path, old, new) -- exact, unique substrings.
TARGETED = [
    # --- repo-root derivation: Utils/ is now three levels down, not one -----
    ("src/RimMandrake/Utils/check_refs.py",
     "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
     "ROOT = os.path.dirname(os.path.dirname(os.path.dirname(\n"
     "    os.path.dirname(os.path.abspath(__file__)))))"),
    ("src/RimMandrake/Utils/check_refs.py",
     'SKIP_SCAN = ("disposing/", "output/", "mods/mod_sources/", ".git/")',
     'SKIP_SCAN = ("infrastructure/disposing/", "infrastructure/output/",\n'
     '             "vendor/mod_sources/", ".git/")'),
    ("src/RimMandrake/Utils/check_refs.py",
     'SKIP_FILES = {"output/REF_AUDIT.md", "REF_AUDIT.md"}',
     'SKIP_FILES = {"infrastructure/output/REF_AUDIT.md", "REF_AUDIT.md"}'),
    ("src/RimMandrake/Utils/deploy_custom_mods.py",
     "ROOT = os.path.dirname(HERE)",
     "ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))"),
    ("src/RimMandrake/Utils/refresh.py",
     "ROOT = os.path.dirname(HERE)",
     "ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))"),
    ("src/RimMandrake/Utils/modset_builder.py",
     'ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))',
     'ROOT = os.path.abspath(os.path.join(\n'
     '    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))'),
    ("src/RimMandrake/Utils/package_skill.py",
     "REPO = Path(__file__).resolve().parent.parent",
     "REPO = Path(__file__).resolve().parent.parent.parent.parent"),
    ("src/RimMandrake/Utils/patch_provenance.py",
     'ROOT = os.path.abspath(os.path.join(HERE, ".."))',
     'ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))'),
    ("src/RimMandrake/Utils/peers.py",
     'repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))',
     'repo = os.path.abspath(\n'
     '        os.path.join(os.path.dirname(__file__), "..", "..", ".."))'),
    ("src/RimMandrake/Utils/status.py",
     "ROOT = Path(__file__).resolve().parent.parent",
     "ROOT = Path(__file__).resolve().parent.parent.parent.parent"),
    ("src/RimMandrake/Utils/rimbench/shipbuild.py",
     "REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
     "REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(\n"
     "    os.path.dirname(os.path.abspath(__file__))))))"),

    # --- Utils/ data + tool paths ------------------------------------------
    ("src/RimMandrake/Utils/refresh.py",
     'INVENTORY = os.path.join(ROOT, "mods", "inventory")',
     'INVENTORY = os.path.join(ROOT, "observed", "2026-08-13_pre-restructure",\n'
     '                         "inventory")'),
    ("src/RimMandrake/Utils/refresh.py",
     'ARMOURY = os.path.join(ROOT, "custom_patches", "Jawa_Armoury")',
     'ARMOURY = os.path.join(ROOT, "src", "Jawa", "Jawa_Armoury")'),
    ("src/RimMandrake/Utils/refresh.py",
     'os.path.join("Utils", "animal_inventory.py")',
     'os.path.join("src", "RimMandrake", "Utils", "animal_inventory.py")'),
    ("src/RimMandrake/Utils/refresh.py",
     '"--out", os.path.join("mods", "inventory")',
     '"--out", os.path.join("observed", "2026-08-13_pre-restructure",\n'
     '                                    "inventory")'),
    ("src/RimMandrake/Utils/refresh.py",
     'os.path.join("Utils", "animal_contact_sheet.py")',
     'os.path.join("src", "RimMandrake", "Utils", "animal_contact_sheet.py")'),
    ("src/RimMandrake/Utils/modset_builder.py",
     'BACKUPS = os.path.join(ROOT, "runtime", "backups")',
     'BACKUPS = os.path.join(ROOT, "deployed", "config")'),
    ("src/RimMandrake/Utils/patch_provenance.py",
     'CUSTOM = os.path.join(ROOT, "custom_patches")',
     'CUSTOM = os.path.join(ROOT, "src")'),
    ("src/RimMandrake/Utils/patch_provenance.py",
     'LEDGER = os.path.join(ROOT, "mods", "inventory", "patch_ledger.json")',
     'LEDGER = os.path.join(ROOT, "observed", "2026-08-13_pre-restructure",\n'
     '                      "inventory", "patch_ledger.json")'),
    ("src/RimMandrake/Utils/animal_contact_sheet.py",
     '"mods", "inventory", "animals.csv"',
     '"observed", "2026-08-13_pre-restructure", "inventory", "animals.csv"'),
    ("src/RimMandrake/Utils/animal_live_diff.py",
     'os.path.join("mods", "inventory")',
     'os.path.join("observed", "2026-08-13_pre-restructure", "inventory")'),
    ("src/RimMandrake/Utils/Map_synth.py",
     'os.path.join(os.path.dirname(here), "player_maps")',
     'os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(here))),\n'
     '                       "src", "RimMandrake", "mapsynth")'),
    ("src/RimMandrake/Utils/build_jawavoice.py",
     '"custom_patches", "JawaVoice"',
     '"src", "Jawa", "JawaVoice"'),
    ("src/RimMandrake/Utils/status.py",
     'sys.path.insert(0, str(ROOT / "Utils"))',
     'sys.path.insert(0, str(ROOT / "src" / "RimMandrake" / "Utils"))'),
    ("src/RimMandrake/Utils/status.py",
     '(ROOT / "queue").glob("*.md")',
     '(ROOT / "infrastructure" / "state" / "queue").glob("*.md")'),
    ("src/RimMandrake/Utils/status.py",
     '(ROOT / "queue").is_dir()',
     '(ROOT / "infrastructure" / "state" / "queue").is_dir()'),
    ("src/RimMandrake/Utils/rimbench/shipbuild.py",
     'MAPS = os.path.join(REPO, "player_maps")',
     'MAPS = os.path.join(REPO, "src", "RimMandrake", "mapsynth")'),
    ("src/RimMandrake/Utils/rimbench/shipbuild.py",
     'OUT = os.path.join(REPO, "worldbuilding", "ship_build")',
     'OUT = os.path.join(REPO, "design", "Jawa", "worldbuilding", "ship_build")'),

    # --- Utils/jawavoice/ is now four levels down --------------------------
    ("src/RimMandrake/Utils/jawavoice/compose.py",
     'os.path.join(os.path.dirname(__file__), "..", "..")',
     'os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")'),
    ("src/RimMandrake/Utils/jawavoice/genideo.py",
     'os.path.join(os.path.dirname(__file__), "..", "..")',
     'os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")'),
    ("src/RimMandrake/Utils/jawavoice/genxml.py",
     'os.path.join(os.path.dirname(__file__), "..", "..")',
     'os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")'),

    # --- bridgetools/ kept its depth relative to Utils/, but not to the root
    ("src/RimMandrake/bridgetools/prove_capture_restore.py",
     '_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
     '_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(\n'
     '    os.path.dirname(os.path.abspath(__file__)))))'),
    ("src/RimMandrake/bridgetools/prove_capture_restore.py",
     'CAPTURE_FILE = os.path.join(_ROOT, "runtime", "last_capture.ops")',
     'CAPTURE_FILE = os.path.join(_ROOT, "observed", "last_capture.ops")'),
    ("src/RimMandrake/bridgetools/prove_new_tools.py",
     '_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
     '_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(\n'
     '    os.path.dirname(os.path.abspath(__file__)))))'),

    # --- custom_patches/*/Source/ is now src/<tier>/*/Source/, one deeper ---
    ("src/Jawa/Jawa_Armoury/Source/gen_armour_patch.py",
     'ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))',
     'ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))'),
    ("src/Jawa/Jawa_Armoury/Source/gen_armour_patch.py",
     'OUTDIR = os.path.join(ROOT, "custom_patches", "Jawa_Armoury", "Patches")',
     'OUTDIR = os.path.join(ROOT, "src", "Jawa", "Jawa_Armoury", "Patches")'),
    ("src/Jawa/Jawa_Armoury/Source/gen_armour_patch.py",
     'ANIMALS = os.path.join(ROOT, "mods", "inventory", "animals.csv")',
     'ANIMALS = os.path.join(ROOT, "observed", "2026-08-13_pre-restructure",\n'
     '                       "inventory", "animals.csv")'),
    ("src/Jawa/Jawa_Armoury/Source/gen_armoury_patch.py",
     'OUTDIR = os.path.join(_REPO_ROOT, "custom_patches", "Jawa_Armoury", "Patches")',
     'OUTDIR = os.path.join(_REPO_ROOT, "src", "Jawa", "Jawa_Armoury", "Patches")'),
    ("src/Jawa/Jawa_Armoury/Source/gen_torpedo_speed.py",
     'OUT = os.path.join(_REPO_ROOT, "custom_patches", "Jawa_Armoury", "Patches",',
     'OUT = os.path.join(_REPO_ROOT, "src", "Jawa", "Jawa_Armoury", "Patches",'),
    ("src/Jawa/Jawa_Armoury/Source/compare_ladder.py",
     'PATCHES = os.path.join(_REPO_ROOT, "custom_patches", "Jawa_Armoury",',
     'PATCHES = os.path.join(_REPO_ROOT, "src", "Jawa", "Jawa_Armoury",'),
    ("src/Jawa/Jawa_Doctrine/Source/gen_megafauna_yield.py",
     'ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))',
     'ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))'),
    ("src/Jawa/Jawa_Doctrine/Source/gen_megafauna_yield.py",
     'OUTDIR = os.path.join(ROOT, "custom_patches", "Jawa_Doctrine", "Patches")',
     'OUTDIR = os.path.join(ROOT, "src", "Jawa", "Jawa_Doctrine", "Patches")'),
]

# plan §4 dep 8 -- doc_budget.py's per-class patterns are rooted at the repo top
# and would silently stop matching, dropping files out of their budget class
# with no error. The glob'd ones (queue/, agents/) the sweep catches; these are
# the bare root filenames it deliberately leaves alone.
for _f, _d in (("AGENT_*_state.md", "infrastructure/state/"),
               ("agents_def.md", "infrastructure/"),
               ("DOC_BUDGET.md", "infrastructure/"),
               ("STRUCTURE.md", "infrastructure/"),
               ("V1_SCOPE.md", "infrastructure/state/"),
               ("OWNER_DECISIONS.md", "infrastructure/state/"),
               ("CLOSED.md", "infrastructure/state/"),
               ("NEXT_RELOAD.md", "infrastructure/state/")):
    TARGETED.append(("src/RimMandrake/Utils/doc_budget.py",
                     '("%s",' % _f, '("%s%s",' % (_d, _f)))

# whats_new.py's DOCTRINE list is git pathspecs, and status.py reads three of
# the state files by name.
for _f, _d in (("agents_def.md", "infrastructure/"),
               ("V1_SCOPE.md", "infrastructure/state/"),
               ("DOC_BUDGET.md", "infrastructure/"),
               ("CLOSED.md", "infrastructure/state/")):
    TARGETED.append(("src/RimMandrake/Utils/whats_new.py",
                     '    "%s",' % _f, '    "%s%s",' % (_d, _f)))
TARGETED.append(("src/RimMandrake/Utils/whats_new.py",
                 'for d in ("agents", "queue"):',
                 'for d in (os.path.join("infrastructure", "agents"),\n'
                 '              os.path.join("infrastructure", "state", "queue")):'))
for _f, _d in (("V1_SCOPE.md", "infrastructure/state/"),
               ("OWNER_DECISIONS.md", "infrastructure/state/"),
               ("NEXT_RELOAD.md", "infrastructure/state/")):
    TARGETED.append(("src/RimMandrake/Utils/status.py",
                     '"%s"' % _f, '"%s%s"' % (_d, _f)))

# `os.path.join(<root>, "Utils"[, "rimbench"])` -- same shape in eight files.
UTILS_JOIN = [
    ("src/RimMandrake/bridgetools/prove_capture_restore.py", '_ROOT'),
    ("src/RimMandrake/bridgetools/prove_new_tools.py", '_ROOT'),
    ("src/Jawa/Jawa_Armoury/Source/compare_ladder.py", '_REPO_ROOT'),
    ("src/Jawa/Jawa_Armoury/Source/gen_armoury_patch.py", '_REPO_ROOT'),
    ("src/Jawa/Jawa_Armoury/Source/gen_torpedo_speed.py", '_REPO_ROOT'),
    ("src/Jawa/Jawa_Armoury/Source/gen_armour_patch.py", 'ROOT'),
    ("src/Jawa/Jawa_Doctrine/Source/gen_megafauna_yield.py", 'ROOT'),
]

# `_REPO_ROOT = abspath(join(dirname(__file__), "..", "..", ".."))` -- the same
# three files that also carry the join(_REPO_ROOT, "Utils") above.
DEEPEN = [
    ("src/Jawa/Jawa_Armoury/Source/compare_ladder.py", 3),
    ("src/Jawa/Jawa_Armoury/Source/gen_armoury_patch.py", 3),
    ("src/Jawa/Jawa_Armoury/Source/gen_torpedo_speed.py", 3),
    # Utils/jawavoice/ -- two levels became four.
    ("src/RimMandrake/Utils/jawavoice/jawafit.py", 2),
]

# ⚠️ NOT deepened, deliberately: bridgetools/prove_set_terrain.py and
# time_formation.py resolve `<up-two>/Utils` and `<here>/../Utils`, and
# bridgetools/ and Utils/ stayed siblings under src/RimMandrake/. Both still
# land on the real Utils/ -- plan §4 dep 6, the reason Utils/ moved as one unit.

JAWAVOICE = ('"custom_patches", "JawaVoice"', '"src", "Jawa", "JawaVoice"')

# ---------------------------------------------------------------- pass 2
def _mods_md(name, dest):
    return ("mods/" + name, dest + "/" + name)


MAP = {}
MAP.update({
    # Utils / bridgetools -- plan §4 dep 5 and dep 6 (Utils moves as one unit)
    "Utils/": "src/RimMandrake/Utils/",
    "bridgetools/": "src/RimMandrake/bridgetools/",
    # custom_patches split across the two tiers
    "custom_patches/Jawa_Armoury": "src/Jawa/Jawa_Armoury",
    "custom_patches/Jawa_Doctrine": "src/Jawa/Jawa_Doctrine",
    "custom_patches/Jawa_Patches": "src/Jawa/Jawa_Patches",
    "custom_patches/JawaVoice": "src/Jawa/JawaVoice",
    "custom_patches/JawaIonWeapons": "src/Jawa/JawaIonWeapons",
    "custom_patches/DesertVehicleReskin": "src/Jawa/DesertVehicleReskin",
    "custom_patches/MissingArtFixes": "src/RimMandrake/MissingArtFixes",
    "custom_patches/WreckedMachines": "src/RimMandrake/WreckedMachines",
    "custom_patches/DEPLOY_HOLD.txt": "src/DEPLOY_HOLD.txt",
    "custom_patches/README.md": "src/Jawa/README.md",
    "custom_patches/": "src/",
    # mods/
    "mods/dev/RimDefDump": "src/RimMandrake/RimDefDump",
    "mods/inventory": STAMP + "/inventory",
    "mods/dumps": STAMP + "/dumps",
    "mods/live_mod_inventory.md": STAMP + "/live_mod_inventory.md",
    "mods/mod_sources": "vendor/mod_sources",
    "mods/inspiration": "research/RimMandrake/inspiration",
    "mods/sw_ingredients_inventory.md": "research/Jawa/sw_ingredients_inventory.md",
    # runtime/ -- ceases to exist
    "runtime/logs": STAMP + "/logs",
    "runtime/latency_": STAMP + "/latency_",
    "runtime/backups": "deployed/config",
    "runtime/art": "src/Jawa/art_bench",
    "runtime/last_capture.ops": "observed/last_capture.ops",
    # worldbuilding/
    "worldbuilding/Custom_World.md": "design/RimMandrake/Custom_World.md",
    "worldbuilding/faction_authoring_mechanism.md":
        "design/RimMandrake/faction_authoring_mechanism.md",
    "worldbuilding/balance_paradigm.md": "design/RimMandrake/balance_paradigm.md",
    "worldbuilding/Factory_lore.md": "vendor/wisdom/Factory_lore.md",
    "worldbuilding/star_wars_species_scale_reference_atlas.pdf":
        "research/Jawa/star_wars_species_scale_reference_atlas.pdf",
    "worldbuilding/": "design/Jawa/worldbuilding/",
    # player_maps/
    "player_maps/authored/coastal_mesa_rationale.md":
        "design/RimMandrake/coastal_mesa_rationale.md",
    "player_maps/authored": "src/RimMandrake/mapsynth/authored",
    "player_maps/README.md": "src/RimMandrake/mapsynth/README.md",
    # savegame / image_request
    "savegame/": STAMP + "/savegame/",
    "image_request/_review": "src/Jawa/art_bench/_review",
    "image_request/": "design/Jawa/art/",
    # infrastructure
    "agents/": "infrastructure/agents/",
    "queue/": "infrastructure/state/queue/",
    "output/": "infrastructure/output/",
    "disposing/": "infrastructure/disposing/",
    # already-landed stages 1-2 whose code refs were never swept
    "hand_authored_maps/": "research/RimMandrake/hand_authored_maps/",
    "samuel_streamer_study/": "research/RimMandrake/samuel_streamer_study/",
})
for _n in ("benign_log_errors.md", "cqf_quest_types_explainer.md",
           "def_override_clusters.md", "github_issue_swcp_bundle.md"):
    MAP.update([_mods_md(_n, "vendor/wisdom")])
for _n in ("agent_supersession_audit.md", "armoury_keeplist.md",
           "cherry_picker_killlist.md", "concept_defnames.md",
           "forbidden_mods.md", "outer_rim_cherrypick_list.md",
           "required_mods.md", "world_interest_and_mech_danger.md"):
    MAP.update([_mods_md(_n, "design/Jawa/mods")])
for _n in ("beautiful_tilemap.md", "llm_stack_assessment.md",
           "llm_voice_preauthoring.md", "map_authoring_decision.md",
           "music_protocol.md", "ollama.md", "rimbridge.md",
           "rimtalk_analysis.md"):
    MAP["runtime/" + _n] = "design/RimMandrake/" + _n
for _n in ("build_plan.md", "carbonite_trophy_mod.md",
           "divine_satiation_engine.md", "droid_ruling.md",
           "first_live_access.md", "parked_mod_concepts.md"):
    MAP["runtime/" + _n] = "design/Jawa/" + _n

# player_maps/: .py + README + authored/ went to mapsynth/, run outputs to runs/.
PLAYER_MAPS = re.compile(r"player_maps/([A-Za-z0-9_.\-]+)")

# Root files. Only rewritten when they carry an unambiguous absolute prefix --
# a bare `TODO.md` in prose is not a path claim and `check_refs.py` resolves it
# by basename anywhere in the tree, so rewriting it buys nothing and risks prose.
ROOTDOCS = {
    "STRUCTURE.md": "infrastructure/STRUCTURE.md",
    "agents_def.md": "infrastructure/agents_def.md",
    "DOC_BUDGET.md": "infrastructure/DOC_BUDGET.md",
    "REFRESH.md": "infrastructure/REFRESH.md",
    "TODO_v2.md": "infrastructure/state/TODO_v2.md",
    "TODO.md": "infrastructure/state/TODO.md",
    "NEXT_RELOAD.md": "infrastructure/state/NEXT_RELOAD.md",
    "OWNER_DECISIONS.md": "infrastructure/state/OWNER_DECISIONS.md",
    "CLOSED.md": "infrastructure/state/CLOSED.md",
    "V1_SCOPE.md": "infrastructure/state/V1_SCOPE.md",
    "AGENT_BRIDGE_state.md": "infrastructure/state/AGENT_BRIDGE_state.md",
    "AGENT_CREATE_state.md": "infrastructure/state/AGENT_CREATE_state.md",
    "AGENT_OPS_state.md": "infrastructure/state/AGENT_OPS_state.md",
    "AGENT_PROJECT_state.md": "infrastructure/state/AGENT_PROJECT_state.md",
    "context.md": "infrastructure/archive/context.md",
    "concept.md": "design/Jawa/concept.md",
    "rimworld_file_lore.md": "design/RimMandrake/rimworld_file_lore.md",
    "save_authoring_pipeline.md": "design/RimMandrake/save_authoring_pipeline.md",
}

_keys = sorted(MAP, key=len, reverse=True)
SWEEP = re.compile(r"(?<![A-Za-z0-9_.\-/])((?:\./)?)(" +
                   "|".join(re.escape(k) for k in _keys) + r")")
# `D:\Luke\dev\Rimworld\<x>` / `/mnt/d/.../Rimworld/<x>` -- separator-aware.
_absk = sorted(list(MAP) + list(ROOTDOCS), key=len, reverse=True)
ABS_F = re.compile(r"(Rimworld/)(" + "|".join(re.escape(k) for k in _absk) + r")")
ABS_B = re.compile(r"(Rimworld\\)(" +
                   "|".join(re.escape(k.replace("/", "\\")) for k in _absk) + r")")
BACK = {k.replace("/", "\\"): v.replace("/", "\\")
        for k, v in list(MAP.items()) + list(ROOTDOCS.items())}
ALL = dict(MAP)
ALL.update(ROOTDOCS)

RUN_EXT = (".png", ".json", ".npy", "_report.md", "_improvement.md")


def player_maps_sub(m):
    name = m.group(1)
    if name.endswith(".py") or name in ("README.md", "authored"):
        return "src/RimMandrake/mapsynth/" + name
    if name.endswith(RUN_EXT):
        return "src/RimMandrake/mapsynth/runs/" + name
    return "src/RimMandrake/mapsynth/" + name


def fix_text(s):
    s = SWEEP.sub(lambda m: m.group(1) + MAP[m.group(2)], s)
    s = PLAYER_MAPS.sub(player_maps_sub, s)
    s = ABS_F.sub(lambda m: m.group(1) + ALL[m.group(2)], s)
    s = ABS_B.sub(lambda m: m.group(1) + BACK[m.group(2)], s)
    return s


SKIP_DIRS = ("vendor/", "infrastructure/output/", "infrastructure/disposing/",
             "research/RimMandrake/hand_authored_maps/")
EXTS = (".md", ".py", ".sh", ".json")


def main():
    os.chdir(ROOT)
    changed = []
    for path, old, new in TARGETED:
        with open(path, encoding="utf-8") as fh:
            s = fh.read()
        if old not in s:
            print("MISS  %s :: %s" % (path, old[:60]))
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(s.replace(old, new))
        changed.append(path)
    for path, var in UTILS_JOIN:
        with open(path, encoding="utf-8") as fh:
            s = fh.read()
        n = s.replace('os.path.join(%s, "Utils"' % var,
                      'os.path.join(%s, "src", "RimMandrake", "Utils"' % var)
        if n != s:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(n)
            changed.append(path)
        else:
            print("MISS  %s :: join(%s, \"Utils\")" % (path, var))
    for path, n in DEEPEN:
        with open(path, encoding="utf-8") as fh:
            s = fh.read()
        old = 'os.path.join(os.path.dirname(__file__), ' + ', '.join(['".."'] * n) + ')'
        new = 'os.path.join(os.path.dirname(__file__), ' + \
              ', '.join(['".."'] * (n + 2)) + ')'
        if old not in s:
            print("MISS  %s :: %s" % (path, old))
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(s.replace(old, new))
        changed.append(path)
    for path in ("compose.py", "genideo.py", "genxml.py", "jawafit.py"):
        p = "src/RimMandrake/Utils/jawavoice/" + path
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        n = s.replace(*JAWAVOICE)
        if n == s:
            print("MISS  %s :: JawaVoice join" % p)
            continue
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(n)
        changed.append(p)
    print("targeted: %d files" % len(set(changed)))

    files = subprocess.run(["git", "ls-files"], capture_output=True,
                           text=True).stdout.split("\n")
    swept = 0
    for f in files:
        if not f or not f.endswith(EXTS) or f.startswith(SKIP_DIRS):
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                s = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        n = fix_text(s)
        if n != s:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(n)
            swept += 1
    print("swept: %d files" % swept)


if __name__ == "__main__":
    main()

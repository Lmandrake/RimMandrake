#!/usr/bin/env python3
"""l1_donor_off_round.py -- Phase 0 step L1: the donor-off live round (PREPARED, run in one bridge sitting).

Spec: design/RimMandrake/biome_sprint_kickoff_2026-10-15.md §0.5.4 (L1) and §0.5.5 item 5 (the "Live" gate).
Runbook: Transient/phase0_L1_runbook.md. Tier: modset_builder.py `donor_off_phase0` (neither art donor).

Two halves, two interpreters (live-debugging-proof-harness: WSL cannot reach the bridge):

  1. DERIVE (WSL python3, offline). Builds the subject list from the repo, never from memory:
       python3 src/RimMandrake/Utils/modcheck/l1_donor_off_round.py derive --out <manifest.json>
     species  = tracker twins (design/RimMandrake/donor_pack_port_tracker.md, status PORTED / DONE_ALREADY_OWNED)
              + P2 outcomes (Transient/phase0_p2_classification.md)
              + every race / plant ThingDef defined in a Def file the Phase 0 commits touched (PHASE0_COMMITS);
              each name must resolve to a race ThingDef in src with a PawnKindDef, or it is listed `unresolved`.
     biomes   = every RM_ BiomeDef (direct or patch-added roster row) that still carries a donor-guarded row or names a
              Phase 0 port, plus RUT_AridShrubland (the W4 handoff's list); frozen RUT_ twins only with --include-frozen.
     flyers   = subjects whose race carries MaxFlightTime > 0 (statBases or a patch) -- the flight rows.
     It also reports, per subject, the defining packageId (composed-biome folds resolved) against the tier closure, and
     texPaths with no PNG in src (art owed) -- both are OFFLINE gate rows the runbook reads before taking the bridge.

  2. RUN (python.exe from the repo root, bridge up on the donor_off_phase0 tier, a quicktest colony map loaded):
       python.exe src/RimMandrake/Utils/modcheck/l1_donor_off_round.py run --manifest <manifest.json> [--phase P,...]
           [--owner-present "<his words>"] [--save <name>] [--out <result.json>] | tr -d '\\r'
     Phases, in order: pre, log, spawn, plants, burst, oomb, haze, portal, mapgen, flight, save.
     `save` LOADS a save and so ends the quicktest map: it is last, and it runs only when named or with --phase all.

Rows follow the harness contract (skills/live-debugging-proof-harness): PASS = asked, answered, met the bar; FAIL =
asked, answered, missed; UNMEASURED = could not ask (tool refused, precondition never held, log dead, owner absent).
Every row carries PROVE / EXPECT / LIES in its plan (PLAN below). Classes: MOD / SITE / HARNESS / OWNER.

🔴 FLIGHT rows are OWNER-PRESENT-ONLY (CLAUDE.md, three times): skipped as UNMEASURED/OWNER unless --owner-present
quotes him, and even then they are a STATE READ of Pawn_FlightTracker (jawa/pawn_flight action=report), never a
visual check and never a forced take-off.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(UTILS, "..", "..", ".."))
SRC = os.path.join(REPO, "src")
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TIER = "donor_off_phase0"
DONORS = ("mlie.starwarsanimalcollection", "sarg.alphaanimals", "daria40k.alphaanimalspatchoutposts")
DLC = ("ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
       "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")
VEF = "oskarpotocki.vanillafactionsexpanded.core"
OURS_RE = re.compile(r"\b(RM|RSW|RUT)_")

# The Phase 0 commits named by the L1 brief (2026-10-15). Their touched Def files are a subject source.
PHASE0_COMMITS = ("ab6ba54f4 419d5e70b 98f7b4506 59c2718b0 447cae1f2 ba71a81be 3021d7031 f690b6984 85ae91677 "
                  "b4a5cf348 3fbec5530 aabcd7a 4da61378 15414fe38 1f59d0939 aaf59cd6e a8b30d24d 14405b1c4").split()
TRACKER = os.path.join(REPO, "design", "RimMandrake", "donor_pack_port_tracker.md")
P2_CLASSIFICATION = os.path.join(REPO, "Transient", "phase0_p2_classification.md")
P6_CENSUS = os.path.join(REPO, "Transient", "phase0_p6_save_census.md")
SARLACC_RENAMES = os.path.join(REPO, "Transient", "phase0_sarlacc_save_renames.md")
TRACKER_KEEP = ("PORTED", "DONE_ALREADY_OWNED")
# W4 handoff (FOUNDRY_HANDOFF_202610151923, DONOR_OFF_LOAD_PROVE_AFTER_BENCH): "generate AridShrubland, TheRot, Webwork".
# TheRot and Webwork are derived (RM_ rows); AridShrubland has only the frozen twin, named here with its source.
EXTRA_BIOMES = {"RUT_AridShrubland": "W4 handoff FOUNDRY_HANDOFF_202610151923 (RSW_Plant_Nysyllin_Wild row, W4a)"}

# Mechanism subjects. Every defName here is checked against the derived defs by `derive` (a missing one is a manifest
# error, never a guess carried into the live run).
BURSTS = [
    # id, kind, how it dies, the tell, the def's own deathAction (read back in derive)
    {"id": "BURST_BLOODYMESS_KILLED", "kind": "RM_BloodyMess", "death": "kill", "tell": "acid",
     "why": "b4a5cf348: bursts into acid when killed (owner card Q3 'Burst only when killed')"},
    {"id": "BURST_BLOODYMESS_GESTATION", "kind": "RM_BloodyMess", "death": "gestation", "tell": "no_acid_organs",
     "why": "b4a5cf348: no burst when it dies giving birth (AmoebaHostUtility.CompleteGestation -> KillGivingBirth)"},
    {"id": "BURST_BULLOO", "kind": "RM_Bulloo", "death": "kill", "tell": "sentinel",
     "why": "447cae1f2 / ab6ba54f4: the bulloo keeps vanilla DeathActionWorker_SmallExplosion (flame)"},
    {"id": "BURST_BLISTERED_BULLOO", "kind": "RM_InfectedAerofleet", "death": "kill", "tell": "acid",
     "why": "ab6ba54f4: the blistered bulloo's acid burst repointed to EnvironmentalHazards ScaledExplosion"},
    {"id": "BURST_SCORCHPOD", "kind": "RM_Scorchpod", "death": "kill", "tell": "acid",
     "why": "f690b6984: the scorchpod carries the red spore's acid burst (ScaledExplosion)"},
]
ACID_FILTH = "Filth_SpentAcid"
GESTATION_PRODUCTS = ("Kidney", "Liver", "Lung", "Heart", "RM_GrownLeg", "RM_GrownArm", "RM_PillarArmItem", "RM_LashItem",
                      "RM_EyeburstItem", "RM_CaudalSpringItem", "RM_BellowsItem")
SENTINEL = "WoodLog"
OOMB = {"growth": {"kind": "RM_LesserOomb", "into": "RM_Oomb", "feedings": 10, "cycles": 16},
        "split": {"kind": "RM_GreaterOomb", "into": "RM_LesserOomb", "feedings": 20, "cycles": 30, "offspring": 2}}
OOMB_FOOD = ("Filth_Dirt", "Plant_Grass")
HAZE = {"kind": "RM_OcularJelly", "biome": "RM_Contagion", "plant": "Plant_Grass",
        "results": ("RM_HalfmadeTree", "RM_Lashgrass", "RM_Bleedleaf"),
        "settings": "RimMandrake.Contagion.RM_ContagionSettings", "rate_field": "zhoolConversionRate",
        "enabled_field": "zhoolConversionEnabled", "rate": "5", "ticks": 2500, "count": 3}
SARLACC = {"portal": "RSW_DeadSarlaccHusk", "exit": "CaveExit", "generator": "RSW_SarlaccCavity", "size": (12, 9)}
TEX_MISS_RE = re.compile(r"(Failed to find any textures at|No textures found at|Could not load Texture2D|"
                         r"Could not find texture|Could not get texture)\s*:?\s*(\S+)?", re.I)
XREF_RE = re.compile(r"Could not resolve cross-reference", re.I)

PLAN = {
    "P01_TIER_TRUTH": ("jawa/running_mods details=false", "no donor packageId; all five DLC; len == manifest tier len",
                       "a label that is not the list (2026-10-10: a 'tier' run on 550 mods)"),
    "P02_TOOLS": ("rimbridge list_tools", "every tool this round calls is registered",
                  "a stale companion (L05, 2026-10-15) answers some calls and not others"),
    "P03_LOG_ALIVE": ("validation_core.log_revive", "the sentinel warning reads back", "Verse.Log cap: silent PASSes"),
    "P04_MAP": ("jawa/map_info + list_pawns faction=player", "a Playing map with >=1 free colonist",
                "rows that wait on a colonist void after a menu drop"),
    "L01_FIRST_EXCEPTION": ("Player.log of this load", "0 lines containing Exception",
                            "a stale log from the previous process (identity: [JawaBench] ready line)"),
    "L02_XREF_OURS": ("Player.log", "0 'Could not resolve cross-reference' lines naming RM_/RSW_/RUT_",
                      "cross-refs to absent mods' defs are expected on a 25-mod tier; only ours are graded"),
    "L03_TEX_PORTED": ("Player.log", "0 texture misses on a manifest subject's texPath",
                       "a pawn texture resolves at load, not at spawn: the spawn row alone cannot see it"),
    "L04_TEX_OURS": ("Player.log", "0 texture misses on any RM_/RSW_/RUT_ path (gate 0.5.5 #5)",
                     "art-owed items (no PNG yet) fail this honestly; read the split before blaming the port"),
    "SPAWN_*": ("jawa/spawn_pawn count=2 faction=none; 60 ticks; list_pawns; thing_graphic; tap",
                "2 alive, kindActual == kind, no badTex, no new log line naming the kind/race/texPath",
                "thing_graphic may not read a pawn graphic (then the log is the only texture evidence: said so)"),
    "PLANT_*": ("jawa/set_plants; list_things; thing_graphic", "the plant stands and badTex is false",
                "a plant with no PNG reads badTex only if the instrument can see the material"),
    "BURST_*": ("spawn hostile, kill_hostiles(pawnDef, destroyCorpses=false), 30 ticks, census the rect",
                "acid: Filth_SpentAcid delta > 0; sentinel: WoodLog HP < max or Fire; gestation: organs > 0, acid 0",
                "the burst's own Mod Setting off reads as a mod FAIL: the row reports the death and the tell separately"),
    "OOMB_GROWTH": ("tamed RM_LesserOomb; food need 0 then 500 ticks, repeated", "RM_Oomb appears, the lesser is gone",
                    "growth is VEF's feeding counter: no VEF, no growth (P01 reads VEF in the list)"),
    "OOMB_SPLIT": ("tamed RM_GreaterOomb; same cycle", ">=2 new tamed RM_LesserOomb, the greater is gone",
                   "fissionOnlyIfTamed: a wild subject never splits (spawned as player on purpose)"),
    "HAZE_ZHOOL": ("home tile -> RM_Contagion, grass site, 3 zhools, rate 5 (compressed, restored), 2500 ticks",
                   "converted ocular flora count > 0", "OurBiome() refuses a non-mandrake biome: the row reads the "
                   "map biome back first"),
    "PORTAL_ENTER": ("spawn RSW_DeadSarlaccHusk; ordered_job EnterPortal", "a new map with a CaveExit, colonist on it",
                     "the old route listed loaded maps from a wrong key and read 'no map' x4 (SEA_DIVE_LIVE_ERRORS_1)"),
    "PORTAL_EXIT": ("ordered_job EnterPortal on the CaveExit", "the colonist is back on the home map", ""),
    "MAPGEN_*": ("jawa/world_tile_map_generate(tile, biome) on a scratch tile, read, map_drop",
                 "map biome == B; wild animals > 0 or plants > 0 (gate 0.5.5 #5); no exception during mapgen",
                 "a tile climate outside the roster's comfort reads 0 animals: the row says the temperature used"),
    "ROSTER_*": ("jawa/biome_probe find=<ported rows of B>", "each unguarded port reads 'spawning'",
                 "rows still MayRequire'd on a donor (art owed) drop donor-off: expected, listed, not FAIL"),
    "FLIGHT_*": ("OWNER PRESENT ONLY: jawa/pawn_flight action=report kind=K", "canEverFly true, maxFlightTimeStat > 0",
                 "never visual; never forced; a report read is the whole bar"),
    "SAVE_LOAD": ("go_to_main_menu; rimworld/load_game <fixed save>", "Playing; 0 reference errors naming a donor def "
                  "or its RSW_ rename", "on a 25-mod tier the save's other mods are missing: only donor names graded"),
}


# ============================================================ offline: derive
def _parse(path):
    try:
        return ET.parse(path).getroot()
    except Exception:  # noqa: BLE001
        return None


def _def_xml_files(kind="Defs"):
    out = []
    for dp, dn, fn in os.walk(SRC):
        dn[:] = [d for d in dn if d not in ("Textures", "art_source", "Staged", "__pycache__", "Sounds")]
        if os.sep + kind not in dp + os.sep and not dp.endswith(os.sep + kind):
            continue
        out += [os.path.join(dp, f) for f in fn if f.endswith(".xml")]
    return sorted(out)


def _mod_folder(path):
    """src/<Tier>/<Mod>/... -> (tier, mod)."""
    rel = os.path.relpath(path, SRC).split(os.sep)
    return (rel[0], rel[1]) if len(rel) > 2 else (None, None)


def _package_ids():
    """{(tier, mod): packageId as the GAME sees it}: composed-biome folds resolved to the composed id."""
    try:
        import biomes_compose
        folded = biomes_compose.folded_ids(SRC)
    except Exception:  # noqa: BLE001
        folded = {}
    out = {}
    for tier in os.listdir(SRC):
        td = os.path.join(SRC, tier)
        if not os.path.isdir(td):
            continue
        for mod in os.listdir(td):
            about = os.path.join(td, mod, "About", "About.xml")
            if os.path.isfile(about):
                r = _parse(about)
                pid = ((r.findtext("packageId") if r is not None else "") or "").strip().lower()
                if pid:
                    out[(tier, mod)] = folded.get(pid, pid)
    return out


def _texpaths(el):
    return sorted({(t.text or "").strip() for t in el.iter("texPath") if (t.text or "").strip()})


def scan_defs():
    """races {defName: {...}}, kinds {defName: race}, kind_tex {kind: [texPath]}, plants {defName: {...}}, biomes."""
    races, kinds, kind_tex, plants, biomes = {}, {}, {}, {}, {}
    for p in _def_xml_files("Defs"):
        root = _parse(p)
        if root is None:
            continue
        for el in root:
            if not isinstance(el.tag, str):
                continue
            dn = (el.findtext("defName") or "").strip()
            if not dn:
                continue
            if el.tag == "ThingDef" and el.find("race") is not None:
                sb = el.find("statBases")
                mft = sb.findtext("MaxFlightTime") if sb is not None else None
                cmin = sb.findtext("ComfyTemperatureMin") if sb is not None else None
                cmax = sb.findtext("ComfyTemperatureMax") if sb is not None else None
                da = el.find("race/deathAction")
                races[dn] = {"file": os.path.relpath(p, REPO), "mod": _mod_folder(p),
                             "maxFlightTime": _f(mft), "comfy": [_f(cmin), _f(cmax)],
                             "deathAction": None if da is None else (da.get("Class") or "") + "|" + (da.findtext("workerClass") or ""),
                             "texPaths": _texpaths(el)}
            elif el.tag == "ThingDef" and el.find("plant") is not None:
                plants[dn] = {"file": os.path.relpath(p, REPO), "mod": _mod_folder(p), "texPaths": _texpaths(el)}
            elif el.tag == "PawnKindDef":
                kinds[dn] = (el.findtext("race") or "").strip()
                kind_tex[dn] = _texpaths(el)
            elif el.tag == "BiomeDef":
                b = biomes.setdefault(dn, {"file": os.path.relpath(p, REPO), "rows": []})
                b["file"] = os.path.relpath(p, REPO)
                for lst in ("wildAnimals", "wildPlants"):
                    node = el.find(lst)
                    if node is not None:
                        for ch in node:
                            if isinstance(ch.tag, str):
                                b["rows"].append({"name": ch.tag, "list": lst, "mayRequire": ch.get("MayRequire"),
                                                  "src": os.path.relpath(p, REPO)})
    return races, kinds, kind_tex, plants, biomes


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def scan_patches(biomes):
    """Patch-added roster rows (into `biomes`) and patch-set MaxFlightTime -> {defName}."""
    flyers = set()
    for p in _def_xml_files("Patches"):
        root = _parse(p)
        if root is None:
            continue
        for op in root.iter():
            if not isinstance(op.tag, str):
                continue
            xp, val = op.find("xpath"), op.find("value")
            if xp is None or val is None or not xp.text:
                continue
            names = re.findall(r'defName\s*=\s*["\']([^"\']+)', xp.text)
            blob = ET.tostring(val, encoding="unicode")
            if "MaxFlightTime" in blob and re.search(r"<MaxFlightTime>\s*[1-9]", blob):
                flyers.update(names)
            if "BiomeDef" in xp.text and names and ("wildAnimals" in xp.text or "wildPlants" in xp.text):
                lst = "wildAnimals" if "wildAnimals" in xp.text else "wildPlants"
                for ch in val:
                    if not isinstance(ch.tag, str):
                        continue
                    kids = list(ch) if ch.tag in ("wildAnimals", "wildPlants") else [ch]
                    for k in kids:
                        if isinstance(k.tag, str):
                            biomes.setdefault(names[0], {"file": None, "rows": []})["rows"].append(
                                {"name": k.tag, "list": lst, "mayRequire": k.get("MayRequire"),
                                 "src": os.path.relpath(p, REPO)})
    return flyers


def tracker_names(path=TRACKER):
    keep, skipped = [], []
    if not os.path.isfile(path):
        return keep, [{"name": None, "source": "tracker", "why": "tracker missing: %s" % path}]
    for ln in open(path, encoding="utf-8"):
        if not ln.startswith("| ") or ln.startswith("| species") or ln.startswith("|---"):
            continue
        cols = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cols) < 7:
            continue
        twin, status = cols[2], cols[6]
        m = re.match(r"^(R(?:SW|M)_\w+)$", twin)
        if not m:
            if re.match(r"^R(?:SW|M)_", twin):
                skipped.append({"name": twin, "source": "tracker", "why": "twin column '%s' (removed or annotated)" % twin})
            continue
        if status in TRACKER_KEEP:
            keep.append(m.group(1))
        else:
            skipped.append({"name": m.group(1), "source": "tracker", "why": "status %s" % status})
    return keep, skipped


def classification_names(path=P2_CLASSIFICATION):
    keep = []
    if not os.path.isfile(path):
        return keep
    for ln in open(path, encoding="utf-8"):
        cols = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cols) != 5 or not cols[0].isdigit():
            continue
        out = cols[4]
        if out.startswith("NOT ported") or out.startswith("P3"):
            continue
        keep += re.findall(r"\b(R(?:SW|M)_[A-Za-z0-9]+)\b", out)
    return keep


def commit_def_files(commits=PHASE0_COMMITS):
    """Def XML files the Phase 0 commits touched and that still exist (one git call)."""
    try:
        out = subprocess.run(["git", "-C", REPO, "show", "--name-only", "--format=@@%h"] + list(commits),
                             capture_output=True, text=True, timeout=120)
    except Exception as e:  # noqa: BLE001
        return [], "git failed: %s" % e
    if out.returncode != 0:
        return [], "git show exit %d: %s" % (out.returncode, out.stderr.strip()[:200])
    files = sorted({f.strip() for f in out.stdout.splitlines()
                    if f.strip().endswith(".xml") and "/Defs/" in f and os.path.isfile(os.path.join(REPO, f.strip()))})
    return files, None


def _defs_in(relpath, tag_test):
    root = _parse(os.path.join(REPO, relpath))
    names = []
    if root is not None:
        for el in root:
            if isinstance(el.tag, str) and tag_test(el):
                dn = (el.findtext("defName") or "").strip()
                if dn:
                    names.append(dn)
    return names


def png_index():
    idx = set()
    for tier in os.listdir(SRC):
        td = os.path.join(SRC, tier)
        if not os.path.isdir(td):
            continue
        for mod in os.listdir(td):
            tex = os.path.join(td, mod, "Textures")
            for dp, dn, fn in os.walk(tex):
                for f in fn:
                    if f.lower().endswith((".png", ".dds", ".psd", ".jpg")):
                        rel = os.path.relpath(os.path.join(dp, f), tex).replace(os.sep, "/")
                        idx.add(rel.rsplit(".", 1)[0])
    return idx


def tex_owed(texpath, idx):
    """True when no PNG of ours serves texPath (file, Graphic_Multi facings, or a Graphic_Random folder)."""
    t = texpath.replace("\\", "/")
    if t in idx:
        return False
    pref = t + "_", t + "/"
    return not any(p.startswith(pref) for p in idx)


def tier_closure():
    try:
        import modset_builder as M
        inst = M.scan()
        ordered, missing, refusals = M.resolve_tier(TIER, inst)
        return {"ordered": ordered, "missing": missing, "refusals": refusals}
    except Exception as e:  # noqa: BLE001
        return {"ordered": [], "missing": [], "refusals": [], "error": "%s: %s" % (type(e).__name__, e)}


def derive(include_frozen=False, closure=None, commit_files=None):
    races, kinds, kind_tex, plants, biomes = scan_defs()
    patch_flyers = scan_patches(biomes)
    pids = _package_ids()
    tracked, skipped = tracker_names()
    p2 = classification_names()
    if commit_files is None:
        commit_files, git_err = commit_def_files()
    else:
        git_err = None
    from_commits = []
    plant_subjects = []
    for f in commit_files:
        from_commits += _defs_in(f, lambda el: el.tag == "ThingDef" and el.find("race") is not None)
        plant_subjects += _defs_in(f, lambda el: el.tag == "ThingDef" and el.find("plant") is not None)
    sources = {}
    for src_name, names in (("tracker", tracked), ("p2_classification", p2), ("phase0_commit", from_commits)):
        for n in names:
            sources.setdefault(n, []).append(src_name)
    by_race = {}
    for k, r in kinds.items():
        by_race.setdefault(r, []).append(k)
    idx = png_index()
    species, unresolved = [], list(skipped)
    for name in sorted(sources):
        race = name if name in races else (kinds.get(name) if name in kinds else None)
        if race not in races:
            unresolved.append({"name": name, "source": sources[name], "why": "no race ThingDef of that name in src"})
            continue
        ks = sorted(by_race.get(race, []))
        if not ks:
            unresolved.append({"name": name, "source": sources[name], "why": "race has no PawnKindDef in src"})
            continue
        kind = name if name in ks else ks[0]
        rd = races[race]
        tex = sorted(set(rd["texPaths"]) | set(t for k in ks for t in kind_tex.get(k, [])))
        species.append({"race": race, "kind": kind, "kinds": ks, "source": sources[name], "file": rd["file"],
                        "packageId": pids.get(tuple(rd["mod"])) if rd["mod"][0] else None,
                        "texPaths": tex, "texOwed": [t for t in tex if OURS_RE.search(t) and tex_owed(t, idx)],
                        "flyer": bool((rd["maxFlightTime"] or 0) > 0 or race in patch_flyers),
                        "deathAction": rd["deathAction"], "comfy": rd["comfy"]})
    plant_rows = []
    for name in sorted(set(plant_subjects)):
        pd = plants.get(name)
        if not pd:
            continue
        plant_rows.append({"def": name, "file": pd["file"], "packageId": pids.get(tuple(pd["mod"])),
                           "texPaths": pd["texPaths"],
                           "texOwed": [t for t in pd["texPaths"] if tex_owed(t, idx)]})
    ported = {s["race"] for s in species} | {k for s in species for k in s["kinds"]} | {p["def"] for p in plant_rows}
    phase0 = set(from_commits) | set(p2) | set(plant_subjects)
    b_rows, frozen = [], []
    for b, info in sorted(biomes.items()):
        donor_rows = [r for r in info["rows"] if r["mayRequire"] and any(d in r["mayRequire"].lower() for d in DONORS)]
        port_rows = [r for r in info["rows"] if r["name"] in phase0]
        if not (donor_rows or port_rows) and b not in EXTRA_BIOMES:
            continue
        races_here = [races[r["name"]] for r in info["rows"] if r["name"] in races]
        mids = [(c[0] + c[1]) / 2.0 for c in (x["comfy"] for x in races_here) if c[0] is not None and c[1] is not None]
        entry = {"biome": b, "file": info["file"], "why": EXTRA_BIOMES.get(b) or
                 "%d donor-guarded row(s), %d Phase 0 port row(s)" % (len(donor_rows), len(port_rows)),
                 "donorGuarded": sorted({r["name"] for r in donor_rows}),
                 "portRows": sorted({r["name"] for r in port_rows if not (r["mayRequire"] and any(
                     d in r["mayRequire"].lower() for d in DONORS))}),
                 "tileTemperature": round(sorted(mids)[len(mids) // 2], 1) if mids else None}
        if b.startswith("RUT_") and b not in EXTRA_BIOMES:
            frozen.append(entry)
        else:
            b_rows.append(entry)
    if include_frozen:
        b_rows += frozen
    closure = tier_closure() if closure is None else closure
    in_tier = set(closure.get("ordered") or [])
    for s in species + plant_rows:
        s["inTier"] = (s.get("packageId") in in_tier) if in_tier else None
    problems = []
    if git_err:       # without the Phase 0 commits the subject list is silently shorter
        problems.append("Phase 0 commit def files unreadable: %s" % git_err)
    subj = {s["kind"] for s in species} | {s["race"] for s in species} | set(kinds)
    for b in BURSTS:
        if b["kind"] not in subj:
            problems.append("burst subject %s is not a derived PawnKindDef" % b["kind"])
    for k in (OOMB["growth"]["kind"], OOMB["growth"]["into"], OOMB["split"]["kind"], HAZE["kind"]):
        if k not in kinds:
            problems.append("mechanism subject %s has no PawnKindDef in src" % k)
    things = set()
    for p in _def_xml_files("Defs"):
        root = _parse(p)
        if root is not None:
            things.update((el.findtext("defName") or "").strip() for el in root if isinstance(el.tag, str))
    for d in (SARLACC["portal"], SARLACC["generator"]) + HAZE["results"]:
        if d not in things:
            problems.append("def %s not found in src" % d)
    return {
        "schema": 1, "derivedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "head": _git_head(), "tier": {"name": TIER, "closure": closure.get("ordered"), "missing": closure.get("missing"),
                                      "refusals": closure.get("refusals"), "error": closure.get("error")},
        "commitFiles": commit_files, "gitError": git_err,
        "species": species, "plants": plant_rows, "unresolved": unresolved,
        "biomes": b_rows, "frozenTwinBiomes": [f["biome"] for f in frozen],
        "flyers": [s["kind"] for s in species if s["flyer"]],
        "bursts": BURSTS, "oomb": OOMB, "haze": HAZE, "sarlacc": SARLACC,
        "save": find_fixed_save(), "problems": problems, "ported": sorted(ported),
        "donorNames": donor_rename_names(),
    }


def _git_head():
    try:
        return subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


def find_fixed_save(path=P6_CENSUS):
    """The P6 donor-free save name from its census file, or None (then --save is required for the save row)."""
    if not os.path.isfile(path):
        return None
    m = re.findall(r"([\w.\-]+_donorfree)\.rws", open(path, encoding="utf-8").read())
    return m[-1] if m else None


def donor_rename_names(path=SARLACC_RENAMES):
    """Old donor def names (and their RSW_ renames) from the Sarlacc rename table: the save row greps for these."""
    old, new = set(), set()
    if os.path.isfile(path):
        for ln in open(path, encoding="utf-8"):
            cols = [c.strip().strip("`") for c in ln.strip().strip("|").split("|")]
            if len(cols) == 3 and cols[0] and not cols[0].startswith(("def type", "---")):
                if re.match(r"^\w+$", cols[1]):
                    old.add(cols[1])
                if re.match(r"^RSW_\w+$", cols[2]) or cols[2].startswith("Blueprint_Install_RSW_"):
                    new.add(cols[2].split()[0])
    return {"old": sorted(old), "new": sorted(new)}


def offline_rows(man):
    """Rows the runbook reads BEFORE taking the bridge (tier refusals, subjects outside the tier, art owed)."""
    rows = []
    t = man["tier"]
    if t.get("error"):
        _row(rows, "O01_TIER_RESOLVES", "UNMEASURED", "HARNESS", "modset_builder could not resolve: %s" % t["error"])
    elif t.get("refusals") or t.get("missing"):
        _row(rows, "O01_TIER_RESOLVES", "FAIL", "SITE", {"refusals": t.get("refusals"), "missing": t.get("missing"),
             "hint": "a deployed About.xml still names a donor: deploy the mod whose src dropped it (SWBestiary)"})
    else:
        _row(rows, "O01_TIER_RESOLVES", "PASS", "SITE", "%d mods, no donor, all DLC" % len(t.get("closure") or []))
    outside = [s.get("kind") or s.get("def") for s in man["species"] + man["plants"] if s.get("inTier") is False]
    _row(rows, "O02_SUBJECTS_IN_TIER", "FAIL" if outside else ("PASS" if t.get("closure") else "UNMEASURED"),
         "HARNESS", {"outside": outside[:40], "count": len(outside)})
    owed = {s.get("kind") or s.get("def"): s["texOwed"] for s in man["species"] + man["plants"] if s.get("texOwed")}
    _row(rows, "O03_ART_PRESENT", "FAIL" if owed else "PASS", "MOD",
         {"subjectsWithOwedArt": len(owed), "examples": dict(list(owed.items())[:12]),
          "meaning": "texPath of ours with no PNG in src: the live L03/L04 rows will read these as texture misses"})
    _row(rows, "O04_MANIFEST_SANE", "FAIL" if man["problems"] or not man["species"] else "PASS", "HARNESS",
         {"problems": man["problems"], "species": len(man["species"]), "plants": len(man["plants"]),
          "biomes": len(man["biomes"]), "flyers": len(man["flyers"]), "unresolved": len(man["unresolved"])})
    return rows


# ================================================================ live: rows
def _row(rows, rid, status, cls, detail):
    rows.append({"id": rid, "status": status, "class": cls, "detail": detail})
    print("%-34s %-10s %s" % (rid, status, json.dumps(detail, default=str)[:160]), flush=True)


class Round(object):
    def __init__(self, B, man, args, V=None):
        self.B, self.man, self.args, self.rows = B, man, args, []
        self.V = V
        self.tap = None
        self.home = None
        self.colonist = None
        self.site_x = None

    # ------------------------------------------------------------- helpers
    def call(self, tool, **kw):
        try:
            r = self.B.call(tool, **kw)
        except Exception as e:  # noqa: BLE001
            return {"success": False, "transport": True, "error": "%s: %s" % (type(e).__name__, e)}
        return r if isinstance(r, dict) else {"success": False, "transport": True, "raw": r}

    def row(self, rid, status, cls, detail):
        _row(self.rows, rid, status, cls, detail)

    def ticks(self, n):
        """Game time through the harness (clockgate safe_advance). Returns None, or the GovernorStop text."""
        try:
            self.B.ticks(n)
            if self.tap:
                self.tap.poll()
            return None
        except Exception as e:  # noqa: BLE001 -- GovernorStop and transport faults alike: the row is UNMEASURED
            return "%s: %s" % (type(e).__name__, str(e)[:200])

    def log_mark(self):
        if self.tap is None:
            return None
        self.tap.poll()
        return self.tap.last

    def log_since(self, mark, needles):
        """New warn+/error journal lines since `mark` that mention any needle (case-sensitive substrings)."""
        if self.tap is None:
            return None
        hits = []
        for e in self.tap.since(mark):
            msg = str(e.get("Message", ""))
            if any(n and n in msg for n in needles):
                hits.append(msg[:200])
        return hits

    def pawns(self, rect=None, faction=None, corpses=False):
        kw = {"limit": 2000, "includeCorpses": corpses}
        if rect:
            kw["rect"] = "%d,%d,%d,%d" % tuple(rect)
        if faction:
            kw["faction"] = faction
        r = self.call("jawa/list_pawns", **kw)
        return None if r.get("success") is False else (r.get("pawns") or [])

    def things(self, defs, rect=None, limit=2000):
        kw = {"defName": ",".join(defs) if isinstance(defs, (list, tuple)) else defs, "limit": limit}
        if rect:
            kw["rect"] = "%d,%d,%d,%d" % tuple(rect)
        r = self.call("jawa/list_things", **kw)
        return None if r.get("success") is False else (r.get("things") or [])

    def site(self, w, h, rid):
        """A cleared rect east of the colonist, stepping east each call so sites stay disjoint."""
        mi = self.home or {}
        sx, sz = int(mi.get("sizeX") or 250), int(mi.get("sizeZ") or 250)
        if self.site_x is None:
            self.site_x = 10
        x, z = self.site_x, max(5, sz // 2 - h // 2 - 40)
        if x + w + 10 > sx:
            self.site_x, x = 10, 10
            z = min(sz - h - 5, sz // 2 + 40)
        self.site_x = x + w + 6
        rect = (x, z, w, h)
        if self.V is not None and not self.V.prepare_site(self.B, rect, self.rows, rid + "_SITE"):
            return None
        return rect

    def free_colonist(self):
        ps = self.pawns(faction="player") or []
        free = [p for p in ps if not p.get("dead") and not p.get("downed") and (p.get("def") or "Human") == "Human"
                and (p.get("kind") or "") not in {s["kind"] for s in self.man["species"]}]
        return free[0] if free else None

    # ------------------------------------------------------------ phases
    def phase_pre(self):
        rm = self.call("jawa/running_mods", details=False, assembly="")
        running = [str(x).lower() for x in (rm.get("packageIds") or rm.get("mods") or [])
                   if isinstance(x, str)] or [str(m.get("packageId", "")).lower() for m in (rm.get("mods") or [])
                                              if isinstance(m, dict)]
        if not running:
            self.row("P01_TIER_TRUTH", "UNMEASURED", "HARNESS", {"why": "running_mods unreadable", "raw": str(rm)[:200]})
        else:
            donors = [d for d in DONORS if d in running]
            dlc = [d for d in DLC if d not in running]
            want = len(self.man["tier"].get("closure") or [])
            ok = not donors and not dlc and VEF in running
            self.row("P01_TIER_TRUTH", "PASS" if ok else "FAIL", "HARNESS",
                     {"running": len(running), "tierLen": want, "donorsPresent": donors, "dlcMissing": dlc,
                      "vef": VEF in running, "lenMatches": len(running) == want})
        need = ["jawa/running_mods", "jawa/spawn_pawn", "jawa/list_pawns", "jawa/list_things", "jawa/thing_graphic",
                "jawa/kill_hostiles", "jawa/static_call", "jawa/pawn_need", "jawa/mod_settings_field",
                "jawa/world_tile_map_generate", "jawa/world_tile_set", "jawa/map_drop", "jawa/biome_probe",
                "jawa/ordered_job", "jawa/set_current_map", "jawa/pawn_flight", "jawa/set_plants", "jawa/spawn_batch",
                "jawa/destroy_bulk", "jawa/safe_advance"]
        lt = getattr(self.B, "list_tools", None) or getattr(getattr(self.B, "S", None), "list_tools", None)
        try:
            tools = lt() if lt else None
        except Exception:  # noqa: BLE001
            tools = None
        if tools is None:
            self.row("P02_TOOLS", "UNMEASURED", "HARNESS", "no tool listing on this bridge object")
        else:
            names = {t.get("name") if isinstance(t, dict) else str(t) for t in tools}
            miss = [n for n in need if n not in names]
            self.row("P02_TOOLS", "FAIL" if miss else "PASS", "HARNESS", {"missing": miss, "tools": len(names)})
        if self.V is not None:
            alive = self.V.log_revive(self.B)
            self.tap = self.V.tap_start(self.B)
            self.row("P03_LOG_ALIVE", "PASS" if alive.get("alive") else "UNMEASURED", "HARNESS", alive)
        self.home = self.call("jawa/map_info")
        self.colonist = self.free_colonist()
        ok = self.home.get("success") is not False and self.home.get("sizeX") and self.colonist
        self.row("P04_MAP", "PASS" if ok else "UNMEASURED", "SITE",
                 {"mapId": self.home.get("mapId"), "tile": self.home.get("tile"), "biome": self.home.get("mapBiome"),
                  "colonist": (self.colonist or {}).get("id")})
        self.call("jawa/set_game_speed", speed="Paused")
        return bool(ok)

    def phase_log(self):
        path = self.args.player_log or (self.V.PLAYER_LOG if self.V else None)
        if not path or not os.path.isfile(path):
            for rid in ("L01_FIRST_EXCEPTION", "L02_XREF_OURS", "L03_TEX_PORTED", "L04_TEX_OURS"):
                self.row(rid, "UNMEASURED", "HARNESS", "Player.log not readable at %s" % path)
            return
        log = open(path, encoding="utf-8", errors="replace").read()
        if "[JawaBench] ready" not in log and "Bridge token:" not in log:   # the JawaBench line is lazy (first call)
            for rid in ("L01_FIRST_EXCEPTION", "L02_XREF_OURS", "L03_TEX_PORTED", "L04_TEX_OURS"):
                self.row(rid, "UNMEASURED", "HARNESS", "no '[JawaBench] ready' / 'Bridge token:' line: this log may not be this load")
            return
        lines = log.splitlines()
        exc = [ln.strip()[:220] for ln in lines if "Exception" in ln]
        first = next((ln.strip()[:220] for ln in lines
                      if re.search(r"Exception|Could not find type named|Config error in", ln)), None)
        self.row("L01_FIRST_EXCEPTION", "FAIL" if exc else "PASS", "MOD",
                 {"exceptions": len(exc), "first": first, "firstException": exc[0] if exc else None,
                  "configErrors": sum(1 for ln in lines if ln.startswith("Config error in"))})
        xref = [ln.strip()[:220] for ln in lines if XREF_RE.search(ln) and OURS_RE.search(ln)]
        self.row("L02_XREF_OURS", "FAIL" if xref else "PASS", "MOD", {"count": len(xref), "examples": xref[:8]})
        tex_lines = [ln.strip() for ln in lines if TEX_MISS_RE.search(ln)]
        ported = sorted({t for s in self.man["species"] + self.man["plants"] for t in s.get("texPaths", [])})
        hit_ported = [ln[:220] for ln in tex_lines if any(t in ln for t in ported)]
        ours = [ln[:220] for ln in tex_lines if OURS_RE.search(ln) or re.search(r"\bsw[a-z]+/", ln)]
        self.row("L03_TEX_PORTED", "FAIL" if hit_ported else "PASS", "MOD",
                 {"count": len(hit_ported), "examples": hit_ported[:10]})
        self.row("L04_TEX_OURS", "FAIL" if ours else "PASS", "MOD",
                 {"count": len(ours), "ofWhichPorted": len(hit_ported), "examples": ours[:10]})

    def phase_spawn(self, batch=12):
        species = self.man["species"]
        if self.args.only_kinds:
            want = set(self.args.only_kinds.split(","))
            species = [s for s in species if s["kind"] in want or s["race"] in want]
        instrument = {"graphicReadable": 0, "graphicUnreadable": 0}
        # SANITY PROBE (2026-10-16 night): jawa/thing_graphic reads Pawn.Graphic, which is UI/Misc/BadTexture for EVERY pawn
        # until it has been drawn: a vanilla Muffalo read badTex=true and 144 of 144 spawn rows failed on it. A control
        # pawn decides whether badTex means anything on this map; if the control is bad, pawn badTex is not evidence.
        pawn_badtex_blind = True       # blind until a control pawn proves the instrument can see
        rect0 = self.site(6, 6, "SPAWN_CONTROL")
        if rect0 is not None:
            c = self.call("jawa/spawn_pawn", kindDef="Muffalo", x=rect0[0] + 2, z=rect0[1] + 2, faction="none", count=1)
            cids = [p.get("id") for p in (c.get("pawns") or []) if p.get("ok")]
            if cids:
                cg = self.call("jawa/thing_graphic", thing=",".join(cids))
                crows = [x for x in (cg.get("things") or []) if isinstance(x, dict)]
                if crows:
                    pawn_badtex_blind = any(x.get("badTex") for x in crows)
            self.call("jawa/destroy_bulk", filter="factionlessAnimals", dryRun=False)
        if pawn_badtex_blind:
            self.row("SPAWN_BADTEX_CONTROL", "UNMEASURED", "HARNESS",
                     {"note": "no control: a vanilla Muffalo read badTex=true (Pawn.Graphic not drawn yet) or could not be "
                              "spawned/read; pawn badTex is ignored, texture grading rests on the Player.log rows (L03/L04)"})
        for i in range(0, len(species), batch):
            chunk = species[i:i + batch]
            rect = self.site(4 * batch + 4, 10, "SPAWN_BATCH_%d" % (i // batch))
            if rect is None:
                for s in chunk:
                    self.row("SPAWN_" + s["kind"], "UNMEASURED", "SITE", "batch site would not clear")
                continue
            mark = self.log_mark()
            spawned = {}
            for j, s in enumerate(chunk):
                r = self.call("jawa/spawn_pawn", kindDef=s["kind"], x=rect[0] + 2 + 4 * j, z=rect[1] + 5,
                              faction="none", count=2)
                spawned[s["kind"]] = r
            stop = self.ticks(60)
            seen = self.pawns(rect=rect, corpses=True)
            for s in chunk:
                r = spawned[s["kind"]]
                rid = "SPAWN_" + s["kind"]
                if stop:
                    self.row(rid, "UNMEASURED", "HARNESS", {"governorStop": stop})
                    continue
                if r.get("success") is False and not r.get("pawns"):
                    # the game answered "no" (e.g. an unknown kindDef = the def did not load): a MOD verdict; a call
                    # that never reached the game is not one
                    self.row(rid, "UNMEASURED" if r.get("transport") else "FAIL", "HARNESS" if r.get("transport") else
                             "MOD", {"spawn": str(r.get("message") or r.get("error"))[:200]})
                    continue
                ids = [p.get("id") for p in (r.get("pawns") or []) if p.get("ok")]
                subst = [p.get("kindActual") for p in (r.get("pawns") or []) if p.get("kindSubstituted")]
                mine = [p for p in (seen or []) if p.get("id") in ids]
                alive = [p for p in mine if not p.get("dead")]
                g = self.call("jawa/thing_graphic", thing=",".join(ids)) if ids else {}
                grows = [x for x in (g.get("things") or []) if isinstance(x, dict)]
                bad = [] if pawn_badtex_blind else [x.get("id") for x in grows if x.get("badTex")]
                readable = [x for x in grows if x.get("resolvedPath") or x.get("textureName")]
                instrument["graphicReadable" if readable else "graphicUnreadable"] += 1
                needles = [s["kind"], s["race"]] + s.get("texPaths", [])
                logged = self.log_since(mark, needles)
                detail = {"spawned": len(ids), "alive": len(alive), "substituted": subst, "badTex": bad,
                          "graphic": "read" if readable else "unreadable (log is the texture evidence)",
                          "log": logged[:4] if logged else ([] if logged is not None else "UNMEASURED: no tap"),
                          "texOwed": s.get("texOwed")}
                if seen is None or logged is None:
                    self.row(rid, "UNMEASURED", "HARNESS", detail)
                elif len(ids) < 2 or len(alive) < 2 or subst or bad or logged:
                    self.row(rid, "FAIL", "MOD", detail)
                else:
                    self.row(rid, "PASS", "MOD", detail)
            self.call("jawa/destroy_bulk", filter="factionlessAnimals", dryRun=False)
        if instrument["graphicUnreadable"] and not instrument["graphicReadable"]:
            self.row("SPAWN_GRAPHIC_INSTRUMENT", "UNMEASURED", "HARNESS",
                     {"note": "jawa/thing_graphic read no pawn graphic: texture grading rested on Player.log (L03) "
                              "and the journal tap only", "counts": instrument})

    def phase_plants(self):
        for p in self.man["plants"]:
            rid = "PLANT_" + p["def"]
            rect = self.site(5, 5, rid)
            if rect is None:
                self.row(rid, "UNMEASURED", "SITE", "site would not clear")
                continue
            r = self.call("jawa/set_plants", ops="%s:%d,%d,1,1" % (p["def"], rect[0] + 2, rect[1] + 2), growth=1.0)
            got = self.things(p["def"], rect=rect)
            if r.get("success") is False or got is None:
                self.row(rid, "UNMEASURED" if got is None else "FAIL", "MOD", {"set_plants": str(r)[:200]})
                continue
            if not got:
                self.row(rid, "FAIL", "MOD", {"standing": 0, "set_plants": str(r.get("message"))[:160]})
                continue
            g = self.call("jawa/thing_graphic", thing=got[0].get("id"))
            gr = (g.get("things") or [{}])[0] if g.get("things") else {}
            if gr.get("badTex"):
                self.row(rid, "FAIL", "MOD", {"badTex": True, "texOwed": p.get("texOwed"), "path": gr.get("graphicPath")})
            elif not gr:
                self.row(rid, "UNMEASURED", "HARNESS", {"standing": len(got), "graphic": "unreadable"})
            else:
                self.row(rid, "PASS", "MOD", {"standing": len(got), "texture": gr.get("textureName")})

    def _census(self, rect):
        acid = self.things(ACID_FILTH, rect=rect)
        fire = self.things("Fire", rect=rect)
        sent = self.things(SENTINEL, rect=rect)
        organs = self.things(list(GESTATION_PRODUCTS), rect=rect)
        if acid is None or fire is None or sent is None or organs is None:
            return None
        hp = [(t.get("hitPoints"), t.get("maxHitPoints")) for t in sent]
        return {"acid": len(acid), "fire": len(fire), "sentinelHp": hp, "organs": len(organs)}

    def phase_burst(self):
        for b in self.man["bursts"]:
            rid = b["id"]
            rect = self.site(11, 11, rid)
            if rect is None:
                self.row(rid, "UNMEASURED", "SITE", "site would not clear")
                continue
            cx, cz = rect[0] + 5, rect[1] + 5
            self.call("jawa/spawn_batch", ops="%s:%d,%d,75" % (SENTINEL, cx + 1, cz))
            before = self._census(rect)
            faction = "hostile" if b["death"] == "kill" else "none"
            sp = self.call("jawa/spawn_pawn", kindDef=b["kind"], x=cx, z=cz, faction=faction, count=1)
            ids = [p.get("id") for p in (sp.get("pawns") or []) if p.get("ok")]
            if not ids or before is None:
                self.row(rid, "UNMEASURED", "HARNESS", {"spawn": str(sp.get("message") or sp.get("error"))[:200],
                                                        "census": before})
                continue
            if b["death"] == "kill":
                k = self.call("jawa/kill_hostiles", pawnDef=b["kind"], destroyCorpses=False)
            else:
                k = self.call("jawa/static_call", type="RimMandrake.Contagion.AmoebaHostUtility",
                              method="CompleteGestation", args="%s|0|L1 donor-off round|false" % ids[0])
            stop = self.ticks(30)
            after = self._census(rect)
            corpses = self.pawns(rect=rect, corpses=True) or []
            dead = [p for p in corpses if p.get("id") in ids and p.get("dead")]
            detail = {"death": b["death"], "deathCall": str(k.get("message") or k.get("result") or k.get("error"))[:160],
                      "dead": len(dead), "before": before, "after": after, "why": b["why"]}
            if stop or after is None:
                self.row(rid, "UNMEASURED", "HARNESS", dict(detail, governorStop=stop))
                continue
            if not dead:
                self.row(rid, "UNMEASURED", "HARNESS", dict(detail, meaning="the subject did not die: no verdict"))
                continue
            d_acid = after["acid"] - before["acid"]
            hurt = any(h and m and h < m for h, m in after["sentinelHp"]) or after["sentinelHp"] != before["sentinelHp"]
            if b["tell"] == "acid":
                ok = d_acid > 0
            elif b["tell"] == "sentinel":
                ok = hurt or after["fire"] > before["fire"]
            else:   # no_acid_organs
                ok = d_acid == 0 and after["organs"] > before["organs"] and not hurt
            self.row(rid, "PASS" if ok else "FAIL", "MOD", dict(detail, acidDelta=d_acid, sentinelHurt=hurt))
        self.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)

    def phase_oomb(self):
        for key, rid in (("growth", "OOMB_GROWTH"), ("split", "OOMB_SPLIT")):
            o = self.man["oomb"][key]
            rect = self.site(15, 15, rid)
            if rect is None:
                self.row(rid, "UNMEASURED", "SITE", "site would not clear")
                continue
            ops = ";".join("%s:%d,%d,1" % (OOMB_FOOD[0], x, z) for x in range(rect[0], rect[0] + 15, 2)
                           for z in range(rect[1], rect[1] + 15, 2))
            self.call("jawa/spawn_batch", ops=ops)
            self.call("jawa/set_plants", ops="%s:%d,%d,15,15" % ((OOMB_FOOD[1],) + tuple(rect[:2])), density=0.5,
                      clearFirst=False)
            before_into = {p.get("id") for p in (self.pawns(faction="player") or []) if p.get("kind") == o["into"]}
            sp = self.call("jawa/spawn_pawn", kindDef=o["kind"], x=rect[0] + 7, z=rect[1] + 7, faction="player",
                           count=1)
            ids = [p.get("id") for p in (sp.get("pawns") or []) if p.get("ok")]
            if not ids:
                self.row(rid, "UNMEASURED", "HARNESS", {"spawn": str(sp.get("message") or sp.get("error"))[:200]})
                continue
            done, cycles, stop, counter = False, 0, None, None
            for cycles in range(1, o["cycles"] + 1):
                self.call("jawa/pawn_need", pawn=ids[0], action="need", need="Food", level=0.0)
                stop = self.ticks(500)
                if stop:
                    break
                ps = self.pawns(faction="player") or []
                still = [p for p in ps if p.get("id") == ids[0] and not p.get("dead")]
                new = [p for p in ps if p.get("kind") == o["into"] and p.get("id") not in before_into]
                if not still and len(new) >= o.get("offspring", 1):
                    done = True
                    break
                if still:
                    cr = self.call("jawa/comp_read", thing=ids[0], comp="EatWeirdFood")
                    counter = {k: v for k, v in (cr.get("values") or {}).items() if "feed" in k.lower() or "count" in k.lower()}
            detail = {"subject": o["kind"], "into": o["into"], "cycles": cycles, "ticks": cycles * 500,
                      "feedingsNeeded": o["feedings"], "counter": counter,
                      "method": "compressed: food need set to 0 each 500-tick cycle (debug_process long-duration rule)"}
            if stop:
                self.row(rid, "UNMEASURED", "HARNESS", dict(detail, governorStop=stop))
            elif done:
                self.row(rid, "PASS", "MOD", detail)
            else:
                self.row(rid, "UNMEASURED", "SITE", dict(detail, meaning="the cycle did not complete inside the "
                         "budget; read `counter`: a rising count with no change is a MOD lead, a flat one is SITE"))
            self.call("jawa/destroy_bulk", filter="playerAnimals", dryRun=False)

    def phase_haze(self):
        h = self.man["haze"]
        rid = "HAZE_ZHOOL"
        tile = self.home.get("tile")
        was = self.home.get("mapBiome")
        if tile is None:
            self.row(rid, "UNMEASURED", "HARNESS", "map_info named no home tile: nothing to re-biome")
            return
        self.call("jawa/world_tile_set", tiles=str(tile), biome=h["biome"])
        self.call("jawa/world_commit")
        now = self.call("jawa/map_info").get("mapBiome")
        old_rate = self.call("jawa/mod_settings_field", typeName=h["settings"], action="get",
                             field=h["rate_field"]).get("value")
        enabled = self.call("jawa/mod_settings_field", typeName=h["settings"], action="get",
                            field=h["enabled_field"]).get("value")
        try:
            if now != h["biome"]:
                self.row(rid, "UNMEASURED", "SITE", {"mapBiome": now, "wanted": h["biome"]})
                return
            if old_rate is None or str(enabled).lower() != "true":
                self.row(rid, "UNMEASURED", "HARNESS", {"rate": old_rate, "enabled": enabled})
                return
            rect = self.site(21, 21, rid)
            if rect is None:
                self.row(rid, "UNMEASURED", "SITE", "site would not clear")
                return
            self.call("jawa/set_plants", ops="%s:%d,%d,21,21" % ((h["plant"],) + tuple(rect[:2])), growth=0.6)
            before = self.things(list(h["results"]))
            self.call("jawa/mod_settings_field", typeName=h["settings"], action="set", field=h["rate_field"],
                      value=h["rate"])
            sp = self.call("jawa/spawn_pawn", kindDef=h["kind"], x=rect[0] + 10, z=rect[1] + 10, faction="player",
                           count=h["count"])
            stop = self.ticks(h["ticks"])
            after = self.things(list(h["results"]))
            detail = {"spawned": sp.get("spawnedCount"), "before": None if before is None else len(before),
                      "after": None if after is None else len(after), "ticks": h["ticks"], "rate": h["rate"],
                      "method": "compressed: conversion rate %s (MaxRate), restored to %s" % (h["rate"], old_rate)}
            if stop or before is None or after is None or not sp.get("spawnedCount"):
                self.row(rid, "UNMEASURED", "HARNESS", dict(detail, governorStop=stop))
            else:
                self.row(rid, "PASS" if len(after) > len(before) else "FAIL", "MOD", detail)
        finally:
            if old_rate is not None:
                self.call("jawa/mod_settings_field", typeName=h["settings"], action="set", field=h["rate_field"],
                          value=str(old_rate))
            self.call("jawa/destroy_bulk", filter="playerAnimals", dryRun=False)
            if was:
                self.call("jawa/world_tile_set", tiles=str(tile), biome=was)
                self.call("jawa/world_commit")

    def loaded_maps(self):
        r = self.call("jawa/set_current_map", mapId=-987654)
        maps = (r.get("details") or {}).get("loadedMaps") or r.get("loadedMaps") or []
        return {m.get("mapId"): m for m in maps if isinstance(m, dict)} if maps else None

    def phase_portal(self):
        s = self.man["sarlacc"]
        col = self.free_colonist()
        home_id = self.home.get("mapId")
        rect = self.site(s["size"][0] + 4, s["size"][1] + 4, "PORTAL_ENTER")
        if rect is None:
            self.row("PORTAL_ENTER", "UNMEASURED", "SITE", "site would not clear")
            self.row("PORTAL_EXIT", "UNMEASURED", "SITE", "no pocket map to exit")
            return
        if not col:
            self.row("PORTAL_ENTER", "UNMEASURED", "SITE", "no free colonist")
            return
        self.call("jawa/spawn_batch", ops="%s:%d,%d" % (s["portal"], rect[0] + 2 + s["size"][0] // 2,
                                                         rect[1] + 2 + s["size"][1] // 2))
        husk = self.things(s["portal"])
        before = self.loaded_maps()
        if not husk or before is None:
            self.row("PORTAL_ENTER", "UNMEASURED", "HARNESS", {"husk": husk, "maps": before})
            return
        oj = self.call("jawa/ordered_job", pawnId=col.get("id"), jobDef="EnterPortal", targetAId=husk[0].get("id"))
        new, stop = {}, None
        for _ in range(20):
            stop = self.ticks(250)
            if stop:
                break
            now = self.loaded_maps() or {}
            new = {k: v for k, v in now.items() if k not in before}
            if new:
                break
        refused = oj.get("success") is False         # the order never reached a pawn: not a verdict on the portal
        if stop or not new:
            self.row("PORTAL_ENTER", "UNMEASURED" if (stop or refused) else "FAIL", "HARNESS" if (stop or refused) else "MOD",
                     {"orderedJob": str(oj.get("message") or oj.get("error"))[:160], "governorStop": stop,
                      "newMaps": 0})
            self.row("PORTAL_EXIT", "UNMEASURED", "HARNESS", "no pocket map to exit")
            return
        mid, m = next(iter(new.items()))
        self.call("jawa/set_current_map", mapId=mid)
        info = self.call("jawa/map_info")
        exits = self.things(s["exit"]) or []
        here = [p for p in (self.pawns(faction="player") or []) if p.get("id") == col.get("id")]
        ok = bool(exits) and bool(here)
        self.row("PORTAL_ENTER", "PASS" if ok else "FAIL", "MOD",
                 {"pocketMap": mid, "map": m, "biome": info.get("mapBiome"), "size": [info.get("sizeX"), info.get("sizeZ")],
                  "exits": len(exits), "colonistArrived": bool(here)})
        if not exits:
            self.row("PORTAL_EXIT", "UNMEASURED", "MOD", "no CaveExit on the pocket map")
            self.call("jawa/set_current_map", mapId=home_id)
            return
        self.call("jawa/ordered_job", pawnId=col.get("id"), jobDef="EnterPortal", targetAId=exits[0].get("id"))
        back = False
        for _ in range(20):
            stop = self.ticks(250)
            if stop:
                break
            self.call("jawa/set_current_map", mapId=home_id)
            back = any(p.get("id") == col.get("id") for p in (self.pawns(faction="player") or []))
            if back:
                break
            self.call("jawa/set_current_map", mapId=mid)
        self.call("jawa/set_current_map", mapId=home_id)
        self.row("PORTAL_EXIT", "UNMEASURED" if stop else ("PASS" if back else "FAIL"),
                 "HARNESS" if stop else "MOD", {"back": back, "governorStop": stop})

    def scratch_tiles(self, n):
        home = int(self.home.get("tile") or 0)
        cands = [home + d for d in range(40, 40 * (6 * n + 6), 37)]
        r = self.call("jawa/tile_settleable", tiles=",".join(str(c) for c in cands))
        rows = r.get("tiles") or r.get("rows") or r.get("results") or []
        ok = [int(x.get("tile")) for x in rows if isinstance(x, dict) and x.get("tile") is not None and
              (x.get("settleable") or x.get("valid") or x.get("ok"))]
        return ok[:n] if ok else None

    def phase_mapgen(self):
        biomes = self.man["biomes"]
        if self.args.only_biomes:
            want = set(self.args.only_biomes.split(","))
            biomes = [b for b in biomes if b["biome"] in want]
        if not biomes:
            self.row("MAPGEN_NONE", "UNMEASURED", "HARNESS", "no biome selected (manifest empty or --only-biomes matched none)")
            return
        probe = self.call("jawa/biome_probe", biomes=",".join(b["biome"] for b in biomes),
                          find=",".join(sorted({n for b in biomes for n in b["portRows"]})) or None,
                          animals=True, plants=False, limit=80)
        per = {}
        for x in probe.get("biomes") or []:
            if isinstance(x, dict):
                per[x.get("defName") or x.get("biome")] = x
        for b in biomes:
            rid = "ROSTER_" + b["biome"]
            pb = per.get(b["biome"])
            if pb is None:
                self.row(rid, "UNMEASURED", "HARNESS", {"why": "biome_probe returned no row", "raw": str(probe)[:160]})
                continue
            fr = {f.get("name") or f.get("defName"): f.get("state") for f in (pb.get("findResults") or [])
                  if isinstance(f, dict)}
            off = {n: fr.get(n) for n in b["portRows"] if fr.get(n) != "spawning"}
            self.row(rid, "FAIL" if off else "PASS", "MOD",
                     {"ports": len(b["portRows"]), "notSpawning": off,
                      "donorGuardedDropExpected": b["donorGuarded"][:12]})
        tiles = self.scratch_tiles(len(biomes))
        if not tiles:
            for b in biomes:
                self.row("MAPGEN_" + b["biome"], "UNMEASURED", "HARNESS", "no settleable scratch tile found")
            return
        home_id = self.home.get("mapId")
        for b in biomes[len(tiles):]:          # zip() would drop these without a trace
            self.row("MAPGEN_" + b["biome"], "UNMEASURED", "HARNESS", "only %d settleable scratch tile(s) found" % len(tiles))
        for b, tile in zip(biomes, tiles):
            rid = "MAPGEN_" + b["biome"]
            orig = self.call("jawa/world_tile_get", tiles=str(tile)).get("tiles") or [{}]
            kw = {"tiles": str(tile), "biome": b["biome"]}
            if b.get("tileTemperature") is not None:
                kw["temperature"] = b["tileTemperature"]
            self.call("jawa/world_tile_set", **kw)
            self.call("jawa/world_commit")
            mark = self.log_mark()
            before = self.loaded_maps() or {}
            g = self.call("jawa/world_tile_map_generate", tile=tile, biome=b["biome"], sizeX=150, sizeZ=150)
            new = {k: v for k, v in (self.loaded_maps() or {}).items() if k not in before}
            if g.get("success") is False or not new:
                self.row(rid, "FAIL" if g.get("success") is False else "UNMEASURED", "MOD",
                         {"generate": str(g.get("message") or g.get("error"))[:200], "newMaps": len(new)})
                continue
            mid, m = next(iter(new.items()))
            self.call("jawa/set_current_map", mapId=mid)
            info = self.call("jawa/map_info")
            ps = self.pawns() or []
            wild = [p for p in ps if not p.get("faction") and not p.get("dead")]
            plants = self.call("jawa/list_things", group="Plant", limit=1).get("countMatched")
            errs = self.log_since(mark, ["Exception", "Error", "NullReference"]) if mark is not None else None
            exc = [e for e in (errs or []) if "Exception" in e]
            kinds = {}
            for p in wild:
                kinds[p.get("kind")] = kinds.get(p.get("kind"), 0) + 1
            detail = {"tile": tile, "mapBiome": info.get("mapBiome"), "temperature": kw.get("temperature"),
                      "wildAnimals": len(wild), "kinds": dict(sorted(kinds.items(), key=lambda kv: -kv[1])[:10]),
                      "plants": plants, "exceptions": exc[:3], "errors": len(errs or [])}
            if info.get("mapBiome") != b["biome"] or plants is None:
                self.row(rid, "UNMEASURED", "HARNESS", detail)
            elif exc or (not wild and not plants):
                self.row(rid, "FAIL", "MOD", detail)
            elif errs is None:
                self.row(rid, "UNMEASURED", "HARNESS", dict(detail, note="no journal tap: mapgen exceptions were not observable"))
            else:
                self.row(rid, "PASS", "MOD", detail)
            self.call("jawa/set_current_map", mapId=home_id)
            idx = g.get("mapIndex", m.get("index"))
            if idx is not None:
                self.call("jawa/map_drop", mapIndex=idx, notifyPlayer=False)
            if orig and orig[0].get("biome"):
                self.call("jawa/world_tile_set", tiles=str(tile), biome=orig[0]["biome"])
                self.call("jawa/world_commit")

    def phase_flight(self):
        flyers = self.man["flyers"]
        if not flyers:
            self.row("FLIGHT_NONE", "UNMEASURED", "HARNESS", "manifest names no flyer")
            return
        if not self.args.owner_present:
            for k in flyers:
                self.row("FLIGHT_" + k, "UNMEASURED", "OWNER",
                         "OWNER-PRESENT-ONLY: skipped (rerun with --phase flight --owner-present \"<his words>\")")
            return
        rect = self.site(4 * max(1, len(flyers)) + 4, 8, "FLIGHT")
        if rect is None:
            for k in flyers:
                self.row("FLIGHT_" + k, "UNMEASURED", "SITE", "site would not clear")
            return
        for j, k in enumerate(flyers):
            self.call("jawa/spawn_pawn", kindDef=k, x=rect[0] + 2 + 4 * j, z=rect[1] + 4, faction="player", count=1)
            r = self.call("jawa/pawn_flight", action="report", kind=k, maxPawns=5, maintainTicks=0, unpause=False)
            rows = [p for p in (r.get("pawns") or []) if isinstance(p, dict)]
            if not rows:
                self.row("FLIGHT_" + k, "UNMEASURED", "HARNESS", {"raw": str(r)[:200]})
                continue
            ok = all(p.get("canEverFly") and (p.get("maxFlightTimeStat") or 0) > 0 for p in rows)
            self.row("FLIGHT_" + k, "PASS" if ok else "FAIL", "MOD",
                     {"ownerSaid": self.args.owner_present, "pawns": [{x: p.get(x) for x in
                      ("canEverFly", "maxFlightTimeStat", "flightState")} for p in rows]})
        self.call("jawa/destroy_bulk", filter="playerAnimals", dryRun=False)

    def phase_save(self):
        name = self.args.save or self.man.get("save")
        if not name:
            self.row("SAVE_LOAD", "UNMEASURED", "HARNESS", "no fixed save: P6 has not written "
                     "Transient/phase0_p6_save_census.md naming a *_donorfree.rws; pass --save")
            return
        names = self.man.get("donorNames") or {}
        needles = list(names.get("old", [])) + list(names.get("new", []))
        self.call("rimworld/go_to_main_menu")
        mark = self.log_mark()
        self.call("rimworld/load_game", saveName=name)
        ok, waited = (self.V._wait_playing(self.B, budget_s=1200) if self.V else (False, "no harness"))
        logged = self.log_since(mark, ["Could not load reference", "Could not resolve cross-reference",
                                       "Could not find class"])
        refs = list(logged or [])
        donor_refs = [e for e in refs if any(re.search(r"\b%s\b" % re.escape(n), e) for n in needles)]
        mm = self.call("jawa/savegame_mod_match")
        detail = {"save": name, "playing": ok, "waited": waited, "referenceErrors": len(refs),
                  "donorReferenceErrors": donor_refs[:10], "modMatch": str(mm.get("loadedModsSummary"))[:200]}
        if ok and logged is None:
            self.row("SAVE_LOAD", "UNMEASURED", "HARNESS", dict(detail, note="no journal tap: reference errors were not observable"))
        elif not ok:
            self.row("SAVE_LOAD", "UNMEASURED", "HARNESS", dict(detail, hint="a mod-mismatch dialog is the usual "
                     "block on a short tier: read rimworld/get_ui_state"))
        else:
            self.row("SAVE_LOAD", "FAIL" if donor_refs else "PASS", "MOD", detail)


PHASES = ("pre", "log", "spawn", "plants", "burst", "oomb", "haze", "portal", "mapgen", "flight", "save")


def summarize(rows):
    out = {}
    for r in rows:
        out[r["status"]] = out.get(r["status"], 0) + 1
    return out


def run(args, B=None, V=None):
    man = json.load(open(args.manifest, encoding="utf-8"))
    if V is None:
        import validation_core as V  # noqa: N812
    if B is None:
        B = V.Bridge()
    rd = Round(B, man, args, V)
    unknown = [p for p in args.phase.split(",") if args.phase != "all" and p not in PHASES]
    if unknown:
        raise SystemExit("unknown phase(s) %s; known: %s" % (",".join(unknown), ",".join(PHASES)))
    want = PHASES if args.phase == "all" else tuple(p for p in PHASES if p in args.phase.split(","))
    if "pre" not in want:
        want = ("pre",) + want
    aborted = False
    for ph in want:
        if ph == "save" and args.phase != "all" and "save" not in args.phase.split(","):
            continue
        if ph == "pre":
            if not rd.phase_pre() and not args.force:
                print("preflight failed: stopping (pass --force to run the rest anyway)")
                aborted = True
                break
            continue
        getattr(rd, "phase_" + ph)()
    res = {"mode": "live" if args.phase == "all" else "partial", "tier": TIER, "manifestHead": man.get("head"),
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "phases": list(want),
           "ownerPresent": args.owner_present, "aborted": aborted, "rows": rd.rows, "summary": summarize(rd.rows),
           "tapLost": getattr(rd.tap, "lost", None), "plan": PLAN}
    out = args.out or os.path.join(REPO, "Transient", "phase0_L1_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
    print("\nRESULT %s  %s  tapLost=%s" % (out, json.dumps(res["summary"]), res["tapLost"]))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("derive", help="offline: build the subject manifest (WSL python3)")
    d.add_argument("--out", required=True)
    d.add_argument("--include-frozen", action="store_true", help="also mapgen the frozen RUT_ twins with donor rows")
    r = sub.add_parser("run", help="live: drive the bridge (python.exe)")
    r.add_argument("--manifest", required=True)
    r.add_argument("--phase", default="all", help="all, or a comma list of %s" % ",".join(PHASES))
    r.add_argument("--owner-present", metavar="HIS_WORDS", help="enables the FLIGHT rows (state read only)")
    r.add_argument("--save", help="the fixed save's name (no .rws); default: from the P6 census file")
    r.add_argument("--player-log", help="Player.log path (default: validation_core.PLAYER_LOG)")
    r.add_argument("--only-kinds", help="spawn phase: comma list of kinds/races")
    r.add_argument("--only-biomes", help="mapgen phase: comma list of BiomeDefs")
    r.add_argument("--force", action="store_true", help="continue after a failed preflight")
    r.add_argument("--out")
    a = ap.parse_args(argv)
    if a.cmd == "derive":
        man = derive(include_frozen=a.include_frozen)
        man["offlineRows"] = []
        print("offline gate rows:")
        man["offlineRows"] = offline_rows(man)
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(man, fh, indent=1)
        print("\nmanifest %s: %d species, %d plants, %d biomes (%d frozen twins skipped), %d flyers, %d unresolved, "
              "save=%s" % (a.out, len(man["species"]), len(man["plants"]), len(man["biomes"]),
                           len(man["frozenTwinBiomes"]), len(man["flyers"]), len(man["unresolved"]), man["save"]))
        return 0 if not any(r["status"] == "FAIL" for r in man["offlineRows"] if r["id"] in ("O01_TIER_RESOLVES",
                                                                                               "O04_MANIFEST_SANE")) else 1
    res = run(a)
    return 0 if not res["summary"].get("FAIL") and not res["aborted"] else 1


if __name__ == "__main__":
    sys.exit(main())

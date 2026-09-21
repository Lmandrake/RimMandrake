"""Build a minimal, dependency-complete ModsConfig for a named test tier.

WHY THIS EXISTS. Bisecting a 568-mod stack by hand is how loads get wasted. A
cold load is ~23-30 minutes; a 5-mod load is seconds. Proving RimBridge against
the full stack means every failure has 568 suspects, and "debug actions do not
work" could be the bridge, a Harmony conflict, or any of four hundred mods that
patch the dev menu. Prove it on bare Core first, then add exactly what the next
test needs and nothing else.

THE HARD PART is not choosing mods, it is dependency closure. Asking for
"KotOR weapons" without Vanilla Expanded Framework or Humanoid Alien Races
produces a load that fails in a way that looks like the thing you were testing.
This walks <modDependencies> transitively so a tier is always complete.

ORDERING. RimWorld cares about load order, and About.xml declares it through
<loadAfter>, <loadBefore> and <forceLoadAfter>/<forceLoadBefore>. This does a
topological sort over those edges, with Core and Harmony pinned to the front and
our own mods pinned to the back, which is the invariant the whole armoury rests
on: our patches must have the final word.

SAFETY. This NEVER writes ModsConfig.xml while RimWorld is running -- the game
holds its list in memory and rewrites the file on exit, so an edit made during a
session is silently discarded. It refuses, loudly, if Player.log is newer than a
few minutes. Always back up first; --apply does that automatically.

    python src/RimMandrake/Utils/modset_builder.py --list
    python src/RimMandrake/Utils/modset_builder.py --tier bridge          # plan only
    python src/RimMandrake/Utils/modset_builder.py --tier bridge --apply  # writes ModsConfig
    python src/RimMandrake/Utils/modset_builder.py --restore              # back to the full set
"""
import argparse
import collections
import io
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

# 🔴 A TIER'S `why` TEXT CARRIES EMOJI, AND WINDOWS PYTHON DEFAULTS TO cp1252.
# Printing the `shrublandfauna` tier's 🔑 raised UnicodeEncodeError and aborted
# --apply BEFORE ModsConfig was written, so the swap silently did not happen and
# the next launch ran the previous list (FOUNDRY, 2026-09-21). PYTHONIOENCODING
# does not survive the WSL->python.exe hop, so the fix has to live in the script.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
# Per-platform, not hardcoded to C:\ — see src/RimMandrake/Utils/game_paths.py. These were
# Windows literals until 2026-08-13 and so were unusable under WSL.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import LOCALLOW, WORKSHOP, LOCAL_MODS, GAME_DATA  # noqa: E402

LOWDIR = LOCALLOW
GAME = os.path.dirname(LOCAL_MODS)      # ...\common\RimWorld
DATA = GAME_DATA
CONFIG = os.path.join(LOWDIR, "Config", "ModsConfig.xml")
PLAYERLOG = os.path.join(LOWDIR, "Player.log")
BACKUPS = os.path.join(ROOT, "deployed", "config")
# 🔴 Was a dated one-off snapshot (ModsConfig.full-568.2026-08-11.xml, 568 mods)
# that drifted stale as the owner's real list grew -- measured 2026-09-06: it
# silently dropped 30 mods (568 vs the then-live 598) on a --restore after a
# --tier swap. ModsConfig.FULL.LATEST.xml is the doctrinally frozen, kept-current
# full list (CLAUDE.md / rimworld-load-round skill) -- restore to THAT, always.
FULL_BACKUP = os.path.join(ROOT, "infrastructure", "state", "modlists",
                            "ModsConfig.FULL.LATEST.xml")

CORE = "ludeon.rimworld"
HARMONY = "brrainz.harmony"
BRIDGE = "brrainz.rimbridgeserver"

# Ours always loads last; this is the invariant the armoury patches depend on.
OURS_PREFIX = "mandrake."

# --------------------------------------------------------------------- tiers
# Each tier lists only what it WANTS. Dependencies are resolved automatically,
# so these stay readable and honest about intent.
#
# 🔴 dlc is ALWAYS True now — owner ruling 2026-09-19, verbatim: "ALL TEST MOD
# LISTS should include ALL THE EXPANSIONS; we're not trying to ablate
# expansions out of our list at this time." Trigger: a FireHawk flight test
# ran and looked broken, and the first question was whether Odyssey had even
# been loaded (it had — this specific test used the full live list, not a
# tier — but the standing tiers below still excluded DLC on principle, which
# is exactly the gap this rule closes). A tier's "why" can still narrow the
# MOD count for isolation; it no longer narrows the DLC set.
TIERS = {
    "bridge": {
        "why": "Prove RimBridge connects and debug actions fire, with nothing "
               "else that could explain a failure.",
        "want": [BRIDGE],
        "dlc": True,
    },
    "slime": {
        "why": "Prove the Gelatinous Slime gene machine (SLIME_GENE_ARCHIVE_BUILD_1): "
               "the campaign's RUT_SlimeGeneArchive (priority 100) must win over "
               "GelatinousSlime's own universal RM_Archive_Default (priority 0), so "
               "Dialog_GeneArchive offers the frozen A-list, not the 17 vanilla "
               "placeholders. Needs Biotech for GeneDef at all.",
        "want": [BRIDGE, "mandrake.rm.gelatinousslime", "mandrake.rut.patches"],
        "dlc": True,
    },
    "pits": {
        "why": "Prove the pit framework inside FlowWorks (dig stages, mass-sum "
               "cover trigger, struggle escape) with nothing else on the map "
               "that could spring a trap or explain a failure.",
        "want": [BRIDGE, "mandrake.rm.flowworks"],
        "dlc": True,
    },
    "visibility": {
        "why": "Prove mandrake.rm.visibility's threat-point Prefix and "
               "tile-memory round trip (COLONY_VISIBILITY_BUILD_1) with "
               "nothing else on the list that could explain a failure. "
               "Needs Odyssey for GravshipUtility/Building_GravEngine.",
        "want": [BRIDGE, "mandrake.rm.visibility"],
        "dlc": True,
    },
    "graffiti": {
        "why": "Prove mandrake.rm.graffiti + mandrake.rm.sacredgraffiti load "
               "clean and the absorbed vandal spree mechanic runs, with "
               "Mlie.GraffitiMod already retired and nothing else on the "
               "list that could explain a failure.",
        "want": [BRIDGE, "mandrake.rm.graffiti", "mandrake.rm.sacredgraffiti"],
        "dlc": True,
    },
    "bench": {
        "why": "RimBridge + our mods + the smallest content set that can answer "
               "the open balance questions: saber vs vibro vs armour, ion vs "
               "droids, and megafauna butcher yields.",
        "want": [
            BRIDGE,
            # --- ours
            "mandrake.rsw.armoury", "mandrake.rut.doctrine",
            "mandrake.jawa.patches", "mandrake.rsw.ionweapons",
            "mandrake.rm.rimdefdump",
            # --- weapons and armour matrix (L3 / L14)
            "lee.theforce.lightsaber",      # lightsabers, Heat damage
            "guy762.mm.kotorcore",          # durasteel + matrix armour
            "guy762.kotorweapons",          # vibro-weapons, the AP contrast
            # --- ion versus droids (the flesh-type flip)
            "neronix17.asimov",             # Asimov_Automaton flesh type
            "neronix17.outerrim.droiddepot",  # the actual droid RACES to shoot
            # --- butcher yields (bodySize^2 meat and bone)
            "sihv.rombonesport",            # BoneAmount stat
        ],
        "dlc": True,
    },
    "xenotypes": {
        "why": "LOOK at our Star Wars species. Stages the naked-races grid for "
               "XENOTYPE_CANON_CORRECTION_1's ruled sequence (skin colour -> grid "
               "-> head shapes -> grid). Needs the xenotype mod plus whatever its "
               "About.xml pulls in transitively -- Biotech for genes at all, and "
               "the gene/head frameworks the defs actually reference. 🔑 Head types "
               "carry TabulaRasa.DefModExt_HeadTypeStuff under MayRequire, so "
               "neronix17.toolbox is named explicitly: a MayRequire that does not "
               "resolve drops the extension SILENTLY and every head reads as "
               "misconfigured rather than absent.",
        "want": [
            BRIDGE,
            "mandrake.rsw.starwarsraces",
            "neronix17.toolbox",
        ],
        "dlc": True,
    },
    "beastmechanics": {
        "why": "Live-verify PORTED_BEAST_MECHANICS_REBUILD_1's three rebuilt donor "
               "mechanics (steel-eating ferroclaw, two chemfuel ejectors) on "
               "RSW_Ferroclaw / RSW_Voltmaw / RSW_Cindermite, AND "
               "DRUM_LURE_PREDATOR_BUILD_1's vibration-lure ambush + egg-trap clutch "
               "on RSW_Drazzik / RSW_DrazzikEggFertilized -- both items live in "
               "mandrake.rsw.swbestiary and share this same dependency closure. "
               "🔑 All of these carry comps from RimMandrakeBeastMechanicsRSW.dll or "
               "RimMandrake.CreatureBehaviors, and a missing comp TYPE discards the "
               "whole def silently -- so criterion 1 (no 'Could not find type named') "
               "is the first thing this tier exists to answer. "
               "sarg.alphaanimals is a REQUIRED dependency, not a convenience: "
               "removing it breaks ScenPart_StartingAnimal because some SWBestiary "
               "defs inherit an Alpha-Animals parent (MEASURED, ruled out as a "
               "workaround by BRIDGE_PAWN_SPAWN_CRASHES_VEF_1).",
        "want": [
            BRIDGE,
            "mandrake.rsw.swbestiary",
            "sarg.alphaanimals",
            "mlie.starwarsanimalcollection",
            # 🔴 BOTH of these are REQUIRED by SWBestiary and INVISIBLE to
            # dependency closure. MEASURED live 2026-09-20 on this tier:
            #  - mandrake.rm.creaturebehaviors supplies five RM_CompProperties_*
            #    classes. It is listed only under <loadAfter>, which is an
            #    ORDERING hint, not a dependency -- so closure (which walks
            #    <modDependencies>) skips it, the comp types fail to resolve, and
            #    a missing comp type DISCARDS THE WHOLE DEF silently. That ate
            #    RSW_Drazzik, RSW_WraidAlpha and the BiomesTeamPort races.
            #  - OskarPotocki.VFE.Insectoid2 is not declared anywhere at all, yet
            #    owns the ONLY copy of Things/Pawn/Animal/Fuelmite/* -- the texPath
            #    RSW_Cindermite (zhakka) binds to. Without it the creature spawns
            #    fine and renders as a magenta X.
            "mandrake.rm.creaturebehaviors",
            "oskarpotocki.vfe.insectoid2",
            # 🔑 ADDED 2026-09-20 for DRUM_LURE_PREDATOR_BUILD_1: RSW_DrazzikEgg-
            # Fertilized's trap comp is MayRequire="mandrake.rm.proximityhatch" and
            # is also only in SWBestiary's <loadAfter>, not <modDependencies> --
            # same invisible-to-closure shape as the two above. Without it the def
            # still loads (MayRequire degrades gracefully) but falls back to
            # CompHatcher's vanilla timer, so the actual trap mechanic (hatch on
            # approach) is unprovable without this mod present.
            "mandrake.rm.proximityhatch",
        ],
        "dlc": True,
    },
    "warlab": {
        "why": "Prove ANCIENT_WAR_LAB_1's KCSG dungeon (RUT_WarLab_Complex) "
               "spawns, guardians/fauna present, connectivity holds -- "
               "mandrake.rut.injections is NOT in the owner's live FULL list "
               "yet, so this is the smallest closure that loads it.",
        "want": [BRIDGE, "mandrake.rut.injections", "sarg.alphaanimals"],
        "dlc": True,
    },
    "oracle": {
        "why": "Prove ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1's live 'Test Ohm "
               "letter' debug action fires a real claude -p subprocess call "
               "-- start_debug_game_ready is unreliable on the owner's full "
               "590-mod stack (WorldGenStep errors, quicktest-crashes-full-"
               "modlist-use-cheap-mechanism-list), so prove it here instead.",
        "want": [BRIDGE, "mandrake.rm.oracle"],
        "dlc": True,
    },
    "fish": {
        "why": "Prove FISH_BESTIARY_BUILD_1's live fishing wiring (Scald, "
               "Wasteland brine mining, Cracked Lands, Weeping Stones, "
               "Greentide) with Odyssey's water/fishing mechanics present "
               "and nothing else on the map that could explain a failure.",
        "want": [BRIDGE, "mandrake.rut.patches", "mandrake.rsw.swbestiary"],
        "dlc": True,
    },
    "desertplants": {
        "why": "Live-verify the desert shade plants and the SWBestiary body-part "
               "repoint in one load: DESERT_LEACHMOSS_LIVE_VERIFY_1 (RM_Leachmoss "
               "spawn competition on RUT_Desert), VENOMVINE_LIVE_VERIFY_1 "
               "(CompContactVenom / MapComponent_ContactVenom), and "
               "SWBESTIARY_BODYPART_LIVE_VERIFY_1 (zero 'BodyPartRecord with null "
               "def' / RSW_ body-part cross-reference lines). All three subjects "
               "meet in RUT_Desert's wildPlants, which names RM_Leachmoss and "
               "RM_Venomvine (mandrake.rm.environmentalhazards), RSW_Ultracactus "
               "and four more SWBestiary plants, and RUT_Vorrel "
               "(mandrake.rut.ashkarrflora) -- a MayRequire that does not resolve "
               "drops the entry SILENTLY, so every one of those mods must be "
               "present or the biome reads as misconfigured rather than absent. "
               "mandrake.rm.proximityhatch is named explicitly because SWBestiary "
               "carries it only under <loadAfter>, which closure does not walk.",
        "want": [
            BRIDGE,
            "mandrake.rm.environmentalhazards",
            "mandrake.rut.patches",
            "mandrake.rut.ashkarrflora",
            "mandrake.rsw.swbestiary",
            "mandrake.rm.proximityhatch",
        ],
        "dlc": True,
    },
    "diving": {
        "why": "Prove SCALD_DIVING_MOD_1's dive-site float menu, job "
               "completion, terrain burn ticks and Mod Settings load clean "
               "against the actual RUT_ScaldWater* terrain it patches, with "
               "nothing else on the map that could explain a failure.",
        "want": [BRIDGE, "mandrake.rut.patches", "mandrake.rm.divinginteraction"],
        "dlc": True,
    },
    "shrublandfauna": {
        "why": "The union of `beastmechanics` and `desertplants`: one load that can "
               "answer SHRUBLAND_GIANT_ENRAGE_1 (RSW_ShrublandGiant + "
               "RM_CompParentalEnrage), SCRAPNEST_BIRD_LIVE_VERIFY_1 "
               "(RSW_ScrapNestBird's JobGiver_HoardScrap, in "
               "RimMandrakeBeastMechanicsRSW.dll), FILTH_ON_NATURAL_TERRAIN_NOOP_1 "
               "(RSW_ShadeWhale's RM_CompDungSeeder / RM_FilterFeedExtension and the "
               "new RSW_Filth_WhaleDung) and VENOMVINE_PATHCOST_AND_FLYER_1 "
               "(RM_Venomvine, mandrake.rm.environmentalhazards). "
               "🔑 mandrake.rm.creaturebehaviors, sarg.alphaanimals, "
               "mlie.starwarsanimalcollection, oskarpotocki.vfe.insectoid2 and "
               "mandrake.rm.proximityhatch are named EXPLICITLY for the reasons "
               "spelled out on the `beastmechanics` tier -- SWBestiary carries them "
               "under <loadAfter> or not at all, closure walks only "
               "<modDependencies>, and a missing comp TYPE discards the whole def "
               "silently. Dropping any of them makes a working mechanic read as a "
               "clean negative.",
        "want": [
            BRIDGE,
            "mandrake.rsw.swbestiary",
            "mandrake.rm.creaturebehaviors",
            "mandrake.rm.environmentalhazards",
            "mandrake.rm.proximityhatch",
            "mandrake.rut.patches",
            "mandrake.rut.ashkarrflora",
            "sarg.alphaanimals",
            "mlie.starwarsanimalcollection",
            "oskarpotocki.vfe.insectoid2",
        ],
        "dlc": True,
    },
}


def read_about(path):
    try:
        r = ET.parse(path).getroot()
    except Exception as e:
        print("  ! could not parse %s (%s: %s) -- this mod will read as "
              "NOT INSTALLED" % (path, type(e).__name__, e), file=sys.stderr)
        return None
    pid = (r.findtext("packageId") or "").strip()
    if not pid:
        return None

    def lst(tag):
        node = r.find(tag)
        out = []
        if node is not None:
            for li in node.findall("li"):
                # modDependencies entries are objects with a packageId child;
                # loadAfter entries are bare strings. Handle both shapes.
                v = (li.findtext("packageId") or li.text or "").strip()
                if v:
                    out.append(v.lower())
        return out

    return {
        "packageId": pid.lower(),
        "name": (r.findtext("name") or pid).strip(),
        "deps": lst("modDependencies"),
        "after": lst("loadAfter") + lst("forceLoadAfter"),
        "before": lst("loadBefore") + lst("forceLoadBefore"),
    }


def scan():
    """packageId -> record, across DLC, workshop and local mods."""
    found = {}
    for base in (DATA, WORKSHOP, LOCAL_MODS):
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base)):
            about = os.path.join(base, d, "About", "About.xml")
            if not os.path.isfile(about):
                continue
            rec = read_about(about)
            if rec and rec["packageId"] not in found:
                rec["dir"] = os.path.join(base, d)
                found[rec["packageId"]] = rec
    return found


def close_over(want, installed):
    """Transitive dependency closure. Reports anything not installed."""
    seen, missing, queue = set(), [], list(want)
    while queue:
        pid = queue.pop(0).lower()
        if pid in seen:
            continue
        rec = installed.get(pid)
        if rec is None:
            missing.append(pid)
            continue
        seen.add(pid)
        queue.extend(rec["deps"])
    return seen, missing


def order(pids, installed):
    """Topological sort over loadAfter/loadBefore, Core first, ours last."""
    pids = set(pids)
    edges = collections.defaultdict(set)      # node -> must come after these
    for pid in pids:
        rec = installed[pid]
        for a in rec["deps"] + rec["after"]:
            if a in pids:
                edges[pid].add(a)
        for b in rec["before"]:
            if b in pids:
                edges[b].add(pid)

    def rank(pid):
        if pid == CORE:
            return 0
        if pid.startswith("ludeon.rimworld."):
            return 1                            # official DLC
        if pid == HARMONY:
            return 2
        if pid.startswith(OURS_PREFIX):
            return 9                            # ours last, always
        return 5

    out, placed = [], set()
    pool = sorted(pids, key=lambda p: (rank(p), p))
    guard = 0
    while pool and guard < 10000:
        guard += 1
        for pid in list(pool):
            if edges[pid] <= placed:
                out.append(pid)
                placed.add(pid)
                pool.remove(pid)
                break
        else:
            # A cycle, or an edge we cannot satisfy. Take the lowest-rank
            # remaining item and move on rather than looping forever -- but
            # say so: this is exactly the case where a mod can end up loading
            # before something it needed to follow.
            pid = pool.pop(0)
            unmet = sorted(edges[pid] - placed)
            print("  ! order: forcing %s into place with unmet ordering "
                  "constraint(s) on %s (cycle or unsatisfiable loadAfter/"
                  "loadBefore)" % (pid, unmet), file=sys.stderr)
            out.append(pid)
            placed.add(pid)
    return out


def game_running():
    """Is RimWorld actually up?

    Ask the OS, not the clock. This used to infer "live" from Player.log having
    been touched in the last 3 minutes, which is a proxy for the thing we
    actually care about and gets it wrong in the direction that wastes the
    owner's time: for three minutes after a clean exit it refuses to do work
    that is perfectly safe. A closed game is closed, immediately.

    The mtime check survives only as a fallback for when the process list is
    unavailable, and it stays deliberately conservative there: if we cannot ask,
    assume live and refuse.
    """
    try:
        out = subprocess.run(
            ["tasklist.exe", "/FI", "IMAGENAME eq RimWorldWin64.exe", "/NH"],
            capture_output=True, text=True, timeout=15)
        if out.returncode == 0:
            return "RimWorldWin64" in out.stdout
    except (OSError, subprocess.SubprocessError) as e:
        print("  ! could not ask the OS (%s: %s) -- falling back to the "
              "Player.log mtime heuristic" % (type(e).__name__, e), file=sys.stderr)

    # Could not ask the OS. Fall back to the old heuristic.
    if not os.path.isfile(PLAYERLOG):
        return False
    return (time.time() - os.path.getmtime(PLAYERLOG)) < 180


def full_mod_count():
    """Current size of the full mod list, for the tier-savings line.

    Never a baked-in baseline -- the owner's full list keeps growing (measured
    2026-09-06: a dated snapshot read 568 while the live list was already 598),
    so a literal number here goes stale the same way and just lies quietly.
    """
    try:
        return len(ET.parse(FULL_BACKUP).getroot().find("activeMods").findall("li"))
    except Exception:
        return None


def write_config(pids, version_from):
    tree = ET.parse(version_from)
    root = tree.getroot()
    active = root.find("activeMods")
    for li in list(active):
        active.remove(li)
    for pid in pids:
        ET.SubElement(active, "li").text = pid
    # Preserve the file's own newline convention; a text-mode round trip once
    # rewrote every ending and made the whole file read as changed.
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    with open(CONFIG, "wb") as fh:
        fh.write(buf.getvalue().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tier", choices=sorted(TIERS))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--restore", action="store_true")
    a = ap.parse_args()

    installed = scan()
    print("installed mods discovered: %d" % len(installed))

    if a.list:
        for name, t in sorted(TIERS.items()):
            pids, missing = close_over(t["want"], installed)
            print("\n  %-8s %d wanted -> %d with dependencies%s"
                  % (name, len(t["want"]), len(pids),
                     "  MISSING %s" % missing if missing else ""))
            print("           %s" % t["why"])
        return 0

    if a.restore:
        if game_running():
            print("REFUSING: RimWorld looks live. Exit first.")
            return 1
        # 🔴 CONFIG is NOT "the live list" at this point in normal usage -- by
        # the time anyone calls --restore, CONFIG already holds whatever tiny
        # --tier ... --apply just wrote, so comparing the restore target
        # against CONFIG compares it against the test tier it is about to
        # replace, which can never usefully warn of anything. The actual
        # pre-swap state lives in the newest ModsConfig.before-tier-*.xml this
        # session wrote; compare against THAT instead. Measured 2026-09-06:
        # comparing against CONFIG let a 568-vs-598 mod loss through silently.
        try:
            before_files = sorted(
                (p for p in os.listdir(BACKUPS) if p.startswith("ModsConfig.before-tier-")),
                key=lambda p: os.path.getmtime(os.path.join(BACKUPS, p)))
            if before_files:
                pre_swap = os.path.join(BACKUPS, before_files[-1])
                pre_swap_n = len(ET.parse(pre_swap).getroot().find("activeMods").findall("li"))
                backup_n = len(ET.parse(FULL_BACKUP).getroot().find("activeMods").findall("li"))
                if backup_n != pre_swap_n:
                    print("  ! restoring %s (%d mods); the pre-swap snapshot %s has %d -- "
                          "these disagree, check which one is actually current."
                          % (os.path.relpath(FULL_BACKUP, ROOT), backup_n,
                             os.path.relpath(pre_swap, ROOT), pre_swap_n))
        except Exception:
            pass
        shutil.copy2(FULL_BACKUP, CONFIG)
        print("restored the full mod list from %s" % os.path.relpath(FULL_BACKUP, ROOT))
        return 0

    if not a.tier:
        ap.error("give --tier, --list or --restore")

    t = TIERS[a.tier]
    want = list(t["want"])
    if t["dlc"]:
        want += [p for p in installed if p.startswith("ludeon.rimworld")]
    else:
        want += [CORE]
    want += [HARMONY]

    pids, missing = close_over(want, installed)
    ordered = order(pids, installed)

    print("\ntier '%s': %s\n" % (a.tier, t["why"]))
    for i, pid in enumerate(ordered, 1):
        print("  %3d  %-44s %s" % (i, pid, installed[pid]["name"][:40]))
    if missing:
        print("\n  ! NOT INSTALLED (tier is incomplete): %s" % missing)
        return 1
    full_n = full_mod_count()
    print("\n  %d mods%s." % (len(ordered),
                              ", down from %d" % full_n if full_n else ""))

    if not a.apply:
        print("  plan only. Re-run with --apply to write ModsConfig.xml.")
        return 0
    if game_running():
        print("\n  REFUSING TO WRITE: RimWorld looks live (Player.log touched "
              "in the last 3 minutes).\n  The game rewrites ModsConfig on exit, "
              "so this edit would be silently lost.\n  Exit the game, then re-run.")
        return 1

    os.makedirs(BACKUPS, exist_ok=True)
    stamp = os.path.join(BACKUPS, "ModsConfig.before-tier-%s.xml" % a.tier)
    shutil.copy2(CONFIG, stamp)
    write_config(ordered, CONFIG)
    print("\n  backed up  -> %s" % os.path.relpath(stamp, ROOT))
    print("  wrote      -> ModsConfig.xml (%d active)" % len(ordered))
    print("  restore with: python src/RimMandrake/Utils/modset_builder.py --restore")
    return 0


if __name__ == "__main__":
    sys.exit(main())

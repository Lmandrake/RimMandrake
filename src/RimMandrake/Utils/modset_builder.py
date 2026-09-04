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
FULL_BACKUP = os.path.join(BACKUPS, "ModsConfig.full-568.2026-08-11.xml")

CORE = "ludeon.rimworld"
HARMONY = "brrainz.harmony"
BRIDGE = "brrainz.rimbridgeserver"

# Ours always loads last; this is the invariant the armoury patches depend on.
OURS_PREFIX = "mandrake."

# --------------------------------------------------------------------- tiers
# Each tier lists only what it WANTS. Dependencies are resolved automatically,
# so these stay readable and honest about intent.
TIERS = {
    "bridge": {
        "why": "Prove RimBridge connects and debug actions fire, with nothing "
               "else that could explain a failure.",
        "want": [BRIDGE],
        "dlc": False,
    },
    "pits": {
        "why": "Prove the RimMandrake Pits framework (dig stages, mass-sum "
               "cover trigger, struggle escape) with nothing else on the map "
               "that could spring a trap or explain a failure.",
        "want": [BRIDGE, "mandrake.rm.pits"],
        "dlc": False,
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
        # FULL_BACKUP is a hardcoded snapshot, not re-derived from the live
        # list. It silently drifts out of date as mods are added -- restoring
        # it can UNDO mods the live ModsConfig currently has that this
        # snapshot predates. Compare counts and say so; this does not decide
        # which count is "right", only stops the loss from being invisible.
        try:
            live_n = len(ET.parse(CONFIG).getroot().find("activeMods").findall("li"))
            backup_n = len(ET.parse(FULL_BACKUP).getroot().find("activeMods").findall("li"))
            if backup_n < live_n:
                print("  ! %s has %d mods; the live list currently has %d -- "
                      "restoring will DROP %d mod(s) versus what is live now."
                      % (os.path.relpath(FULL_BACKUP, ROOT), backup_n, live_n,
                         live_n - backup_n))
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
    print("\n  %d mods, down from 568." % len(ordered))

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

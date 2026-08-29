#!/usr/bin/env python3
"""
sync_mod_state.py -- bring every file that RECORDS mod state into agreement with
the build and mod list that are actually installed right now.

WHY THIS EXISTS
---------------
Three separate files each keep their own copy of "which mods, which build", and
nothing keeps them in step:

  1. Config/ModsConfig.xml      <version>      the build the list was written for
  2. Config/LastPlayedVersion.txt              the build the game last ran as
  3. Saves/*.rws  <meta>                       gameVersion + the FULL mod list
                                               (modIds / modSteamIds / modNames)

When (3) disagrees with the live list, RimWorld raises the mod-mismatch dialog at
load -- the long "these mods were added / removed" wall. It is noise to the human
whenever the divergence is one WE caused deliberately (a deploy, a descope, a
mod-list edit), and it is worse than noise to tooling: every validator that joins
a save against the live set reports a difference that is expected and already
understood, which trains people to skim past real ones.

This tool makes them agree. It does NOT change what is installed -- it updates the
RECORDS to match reality.

⚠️ WHAT THIS IS NOT
-------------------
Not a migration tool. It rewrites a save's idea of which mods it was made with, so
the save then loads QUIETLY against the current set. If a mod that supplied defs
the save actually references has been removed, silencing the dialog does NOT make
the save whole -- you get `Could not load reference to <def>` from Scribe instead,
and no mod-list edit fixes that (see skills/rimworld-savegame). Silence the dialog
when you already know why the lists differ; never to make an unexplained one go
away.

SAFETY
------
· Dry-run by DEFAULT. `--apply` writes. There is no `--plan` flag; running it bare
  IS the plan. (Same convention as deploy_custom_mods.py, and the same reason.)
· Refuses to run while RimWorld is up. The game holds these files and rewrites
  Config on exit paths, so an edit made now is either lost or fighting the game.
· Backs up every file before touching it, next to the original.
· Saves are spliced at the BYTE level: only the bytes between <meta> and </meta>
  are rebuilt, everything else is copied through untouched. A .rws is up to ~50 MB
  and holds base64 map grids; reparsing and re-serialising the whole document
  would rewrite regions this tool has no business touching.

USAGE
  python3 sync_mod_state.py                     # plan, all targets, all saves
  python3 sync_mod_state.py --apply             # write
  python3 sync_mod_state.py --saves none        # config files only
  python3 sync_mod_state.py --saves "New Arrivals1"   # one save (repeatable)
  python3 sync_mod_state.py --apply --quiet     # for the pre-load offer
"""

import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape, unescape as xml_unescape

# ------------------------------------------------------------------ locations

LOCALLOW = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
            "RimWorld by Ludeon Studios")
GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld"
WORKSHOP = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"

MODSCONFIG = os.path.join(LOCALLOW, "Config/ModsConfig.xml")
LASTPLAYED = os.path.join(LOCALLOW, "Config/LastPlayedVersion.txt")
SAVES = os.path.join(LOCALLOW, "Saves")
VERSION_TXT = os.path.join(GAME, "Version.txt")

# The three roots a mod can live under. Core and the DLCs are NOT under Mods/ --
# omitting Data/ manufactures six false "missing" hits (ludeon.rimworld and the
# five expansions). See skills/rimworld-start-prep section 4.
MOD_ROOTS = [WORKSHOP, os.path.join(GAME, "Mods"), os.path.join(GAME, "Data")]

BACKUP_SUFFIX = ".bak-sync_mod_state"


# ------------------------------------------------------------------ utilities

def die(msg):
    sys.exit("sync_mod_state: %s" % msg)


def game_is_running():
    """True if RimWorld holds the files. Unknown -> treated as NOT running, but
    say so, because a wrong 'it is down' is the expensive direction."""
    try:
        out = subprocess.run(["tasklist.exe"], capture_output=True, text=True,
                             timeout=30).stdout
    except Exception:
        return None
    return "RimWorldWin64.exe" in out


def _rev(v):
    """The rev number out of `1.6.4871 rev591`, or -1 if it carries none."""
    m = re.search(r"rev(\d+)\s*$", v or "")
    return int(m.group(1)) if m else -1


def read_version():
    """The build to stamp everywhere — taken from what the RUNNING GAME reports,
    not from the install file.

    🔴 THESE TWO DISAGREE ON THIS MACHINE AND THE INSTALL FILE IS THE WRONG ONE.
    Measured 2026-08-15, and the split is entirely by WHO WROTE THE FILE:

        written by the running game   DefDump/manifest.json   1.6.4871 rev591
                                      every Saves/*.rws       1.6.4871 rev591
        static / launcher-written     Version.txt             1.6.4871 rev590
                                      ModsConfig <version>    1.6.4871 rev590

    `Version.txt` ships with the install and does not track the rev the engine
    reports at runtime. Stamping it into the saves would REPLACE a correct rev591
    with a stale rev590 -- manufacturing the very mismatch this tool exists to
    remove, in six files at once, and looking like a successful sync while doing
    it. So: prefer the runtime source, fall back to the install file only when no
    runtime source exists, and never silently pick the lower one."""
    runtime = None
    # The producer migrated flat DefDump/manifest.json into
    # DefDump/captures/<id>/manifest.json on 2026-08-22; check both, newest wins.
    candidates = [os.path.join(LOCALLOW, "DefDump/manifest.json")]
    capdir = os.path.join(LOCALLOW, "DefDump/captures")
    if os.path.isdir(capdir):
        candidates += [os.path.join(capdir, d, "manifest.json")
                       for d in os.listdir(capdir)]
    candidates = [p for p in candidates if os.path.exists(p)]
    for manifest in sorted(candidates, key=os.path.getmtime, reverse=True):
        try:
            import json
            runtime = (json.load(io.open(manifest, encoding="utf-8-sig"))
                       .get("gameVersion") or "").strip() or None
        except Exception:
            runtime = None
        if runtime:
            break

    install = None
    if os.path.exists(VERSION_TXT):
        install = io.open(VERSION_TXT, encoding="utf-8-sig").read().strip()

    if not runtime and not install:
        die("no build stamp anywhere: neither %s nor a DefDump manifest exists."
            % VERSION_TXT)
    if not runtime:
        return install, ("install file only (no DefDump manifest); if the game "
                         "reports a higher rev at runtime this will be stale")
    if not install or runtime == install:
        return runtime, None
    if _rev(runtime) >= _rev(install):
        return runtime, ("Version.txt says %s but the running game reports %s. "
                         "Using the RUNTIME value -- the install file does not "
                         "track the rev." % (install, runtime))
    # Install newer than anything the game has yet written: a patch landed and
    # the game has not run since. That is the one case the install file wins.
    return install, ("Version.txt (%s) is NEWER than the last runtime stamp "
                     "(%s) -- the game has not run since a patch. Using the "
                     "install value." % (install, runtime))


def short_version(v):
    """`1.6.4871 rev590` -> `1.6.4871`.

    LastPlayedVersion.txt holds the SHORT form -- measured, not assumed. Writing
    the rev into it would not match what the game writes there itself."""
    return re.sub(r"\s*rev\d+\s*$", "", v).strip()


def rev_of(v):
    """The trailing revN as an int, or None. Only used to catch the one case
    where Version.txt is the WRONG side of a disagreement -- see main()."""
    m = re.search(r"rev(\d+)\s*$", v or "")
    return int(m.group(1)) if m else None


def active_mods():
    """The live ordered activeMods list, verbatim (original case preserved --
    a save's modIds are case-sensitive strings, not normalised ids)."""
    if not os.path.exists(MODSCONFIG):
        die("no ModsConfig.xml at %s" % MODSCONFIG)
    root = ET.parse(MODSCONFIG).getroot()
    node = root.find("activeMods")
    if node is None:
        die("ModsConfig.xml has no <activeMods>")
    return [(li.text or "").strip() for li in node if (li.text or "").strip()]


def index_installed():
    """packageId(lower) -> (displayName, steamId).

    🔴 <packageId> is NOT unique inside an About.xml -- a regex takes the FIRST
    match, which in most modern mods is a DEPENDENCY's id inside
    <modDependencies>. Take the direct child of <ModMetaData> only. Getting this
    wrong reports dozens of installed mods as missing."""
    out = {}
    for root in MOD_ROOTS:
        if not os.path.isdir(root):
            continue
        for entry in sorted(os.listdir(root)):
            ax = os.path.join(root, entry, "About", "About.xml")
            if not os.path.exists(ax):
                continue
            try:
                meta = ET.parse(ax).getroot()
            except ET.ParseError:
                continue
            pid = meta.find("packageId")          # direct child only
            if pid is None or not (pid.text or "").strip():
                continue
            name = (meta.findtext("name") or entry).strip()
            # 🔴 modSteamIds is About.xml's <steamAppId>, NOT the Workshop folder
            # name. Measured against every .rws on this disk: RimWorld writes "0"
            # for a Workshop mod that does not declare one -- only the five DLC
            # and the two mods that ship a <steamAppId> carry a number, 7 rows of
            # 576. Using the folder id instead put a wrong value in 553 of them.
            sid = (meta.findtext("steamAppId") or "").strip() or "0"
            out[pid.text.strip().lower()] = (name, sid)
    return out


def backup(path):
    dst = path + BACKUP_SUFFIX
    shutil.copy2(path, dst)
    return dst


# ------------------------------------------------- target 1: ModsConfig.xml

def plan_modsconfig(version):
    """Only <version> is ours to touch here. activeMods is the SOURCE of truth
    this whole tool syncs everything else against -- rewriting it would be the
    tool eating its own input."""
    raw = io.open(MODSCONFIG, encoding="utf-8-sig").read()
    m = re.search(r"<version>(.*?)</version>", raw, re.S)
    cur = m.group(1).strip() if m else None
    if cur == version:
        return None
    return ("ModsConfig.xml", "<version>", cur, version)


def write_modsconfig(version):
    data = io.open(MODSCONFIG, "rb").read()
    text = data.decode("utf-8-sig")
    bom = data.startswith(b"\xef\xbb\xbf")
    new = re.sub(r"<version>.*?</version>",
                 "<version>%s</version>" % version, text, count=1, flags=re.S)
    out = new.encode("utf-8")
    io.open(MODSCONFIG, "wb").write((b"\xef\xbb\xbf" + out) if bom else out)


# ------------------------------------------- target 2: LastPlayedVersion.txt

def plan_lastplayed(version):
    short = short_version(version)
    cur = (io.open(LASTPLAYED, encoding="utf-8-sig").read().strip()
           if os.path.exists(LASTPLAYED) else None)
    if cur == short:
        return None
    return ("LastPlayedVersion.txt", "(whole file)", cur, short)


def write_lastplayed(version):
    io.open(LASTPLAYED, "w", encoding="utf-8").write(short_version(version))


# ------------------------------------------------------- target 3: the saves

LIST_TAGS = ("modIds", "modSteamIds", "modNames")


def _indent_of(block, tag):
    """Reuse the file's own indentation. RimWorld writes tabs; a rebuilt block
    with different whitespace still loads, but it makes every future diff of the
    save noisy for no reason."""
    m = re.search(r"([ \t]*)<%s>" % tag, block)
    outer = m.group(1) if m else "\t\t"
    m2 = re.search(r"<%s>\s*\n([ \t]*)<li>" % tag, block)
    inner = m2.group(1) if m2 else outer + "\t"
    return outer, inner


def _replace_list(block, tag, values):
    outer, inner = _indent_of(block, tag)
    # RimWorld writes CRLF. Emitting bare LF into the middle of a CRLF file
    # still parses, but it makes the save's own diff noisy and is a gratuitous
    # difference from what the game would have written.
    nl = "\r\n" if "\r\n" in block else "\n"
    # 🔴 Mod names really do contain `&` -- four of them in this colony's list.
    # Writing one through raw makes the whole save malformed XML, and Scribe
    # rejects the file outright rather than degrading. Escape on the way in;
    # plan_save unescapes on the way out so the two sides compare like for like.
    body = "".join("%s<li>%s</li>%s" % (inner, xml_escape(v), nl) for v in values)
    new = "%s<%s>%s%s%s</%s>" % (outer, tag, nl, body, outer, tag)
    pat = re.compile(r"[ \t]*<%s>.*?</%s>" % (tag, tag), re.S)
    if not pat.search(block):
        return block, False
    return pat.sub(lambda _: new, block, count=1), True


def plan_save(path, version, ids, names, steamids):
    """Read ONLY the head of the file -- meta lives at the top and a save can be
    50 MB. Returns (changes, meta_bounds) or None when already in agreement."""
    with io.open(path, "rb") as fh:
        head = fh.read(4 * 1024 * 1024)
    if head.startswith(b"\xef\xbb\xbf"):
        head = head[3:]
    # 🔴 Find the bounds in BYTES and decode only the meta slice. Decoding the
    # whole 4 MB head first throws UnicodeDecodeError whenever the cut lands
    # mid-character in the body -- a perfectly good save then gets reported
    # "unreadable" and silently skipped, which is the one failure mode nobody
    # would go looking for.
    i, j = head.find(b"<meta>"), head.find(b"</meta>")
    if i < 0 or j < 0:
        return ("no <meta> block in the first 4 MB", None)
    try:
        block = head[i:j + len(b"</meta>")].decode("utf-8")
    except UnicodeDecodeError:
        return ("meta block is not valid UTF-8", None)

    changes = []
    cur_ver = re.search(r"<gameVersion>(.*?)</gameVersion>", block, re.S)
    cur_ver = xml_unescape(cur_ver.group(1).strip()) if cur_ver else None
    if cur_ver != version:
        changes.append(("gameVersion", cur_ver, version))
    for tag, want in zip(LIST_TAGS, (ids, steamids, names)):
        span = re.search(r"<%s>.*?</%s>" % (tag, tag), block, re.S)
        # The file's text is escaped; `want` is not. Compare unescaped, or a
        # single `&amp;` in a mod name reports a diff that --apply can never
        # settle and the tool never becomes idempotent.
        have = [xml_unescape(v) for v in
                re.findall(r"<li>(.*?)</li>", span.group(0) if span else "", re.S)]
        if have != want:
            changes.append((tag, "%d entries" % len(have), "%d entries" % len(want)))
    return (changes, (i, j)) if changes else None


def write_save(path, version, ids, names, steamids):
    """Byte-level splice of the meta block only. Everything outside <meta> is
    copied through unchanged -- including the base64 map grids, which must never
    pass through an XML round-trip."""
    data = io.open(path, "rb").read()
    bom = data.startswith(b"\xef\xbb\xbf")
    body = data[3:] if bom else data
    start = body.find(b"<meta>")
    end = body.find(b"</meta>")
    if start < 0 or end < 0:
        return False, "no <meta>"
    end += len(b"</meta>")
    block = body[start:end].decode("utf-8")

    block = re.sub(r"<gameVersion>.*?</gameVersion>",
                   lambda _: "<gameVersion>%s</gameVersion>" % xml_escape(version),
                   block, count=1, flags=re.S)
    for tag, values in zip(LIST_TAGS, (ids, steamids, names)):
        block, ok = _replace_list(block, tag, values)
        if not ok:
            return False, "missing <%s>" % tag

    out = body[:start] + block.encode("utf-8") + body[end:]
    io.open(path, "wb").write((b"\xef\xbb\xbf" + out) if bom else out)
    return True, None


def list_saves(selector):
    if not os.path.isdir(SAVES):
        return []
    allsaves = sorted(f for f in os.listdir(SAVES) if f.endswith(".rws"))
    if selector == ["none"]:
        return []
    if not selector or selector == ["all"]:
        return [os.path.join(SAVES, f) for f in allsaves]
    picked = []
    for want in selector:
        want = want[:-4] if want.endswith(".rws") else want
        hit = [f for f in allsaves if f[:-4] == want]
        if not hit:
            die("no save named %r in %s" % (want, SAVES))
        picked.append(os.path.join(SAVES, hit[0]))
    return picked


# ------------------------------------------------------------------ reporting

def main():
    ap = argparse.ArgumentParser(
        description="Sync every record of mod state to the installed build "
                    "and live mod list. Dry-run unless --apply.")
    ap.add_argument("--apply", action="store_true",
                    help="write the changes (default is plan only)")
    ap.add_argument("--saves", nargs="*", default=["all"], metavar="NAME",
                    help="'all' (default), 'none', or save names without .rws")
    ap.add_argument("--quiet", action="store_true",
                    help="one summary line instead of the table")
    ap.add_argument("--force-running", action="store_true",
                    help="proceed even though RimWorld appears to be up. Almost "
                         "always wrong -- the game rewrites these files.")
    a = ap.parse_args()

    running = game_is_running()
    if running and not a.force_running:
        die("RimWorld is RUNNING. These files are held by the game and a write "
            "now is lost or fought over. Close it, then re-run. "
            "(--force-running overrides, and you should not need it.)")
    # 🔴 --quiet must NEVER hide this. It is the guard admitting it could not
    # check, and the pre-load offer runs `--apply --quiet` -- exactly the path
    # where an unverified "the game is down" gets acted on.
    if running is None and (a.apply or not a.quiet):
        print("⚠️  could not read the process list, so the game-is-down check did "
              "NOT run. Confirm RimWorld is closed before trusting this.")

    version, version_note = read_version()
    if version_note:
        print("⚠️  %s" % version_note)
    ids = active_mods()
    installed = index_installed()
    names, steamids, unknown = [], [], []
    for pid in ids:
        name, sid = installed.get(pid.lower(), (None, None))
        if name is None:
            unknown.append(pid)
            name, sid = pid, "0"       # listed but not installed -- keep the row
        names.append(name)
        steamids.append(sid)

    if unknown:
        print("⚠️  %d active mod(s) are LISTED BUT NOT INSTALLED. They are kept in "
              "the records under their packageId so nothing silently shrinks, but "
              "this is a real mod-list problem, not a records problem:"
              % len(unknown))
        for p in unknown[:10]:
            print("      %s" % p)
        if len(unknown) > 10:
            print("      ... and %d more" % (len(unknown) - 10))

    plans, targets = [], []
    for planner, writer in ((plan_modsconfig, write_modsconfig),
                            (plan_lastplayed, write_lastplayed)):
        p = planner(version)
        if p:
            plans.append(p)
            targets.append((writer, None))

    save_plans = []
    for path in list_saves(a.saves):
        res = plan_save(path, version, ids, names, steamids)
        if res is None:
            continue
        changes, _ = res
        if isinstance(changes, str):
            print("⚠️  skipping %s: %s" % (os.path.basename(path), changes))
            continue
        save_plans.append((path, changes))

    # 🔴 Version.txt is not always the honest side. Measured here: every save on
    # disk records rev591 while Version.txt still reads rev590, because the file
    # is written at install time and the rev the game reports at runtime can move
    # past it. Syncing then DOWNGRADES a correct gameVersion to a stale one and
    # manufactures the very mismatch this tool exists to remove. Say so; the human
    # decides, because the tool cannot tell a stale Version.txt from stale saves.
    downgrades = sorted({cur for _, ch in save_plans for tag, cur, want in ch
                         if tag == "gameVersion" and rev_of(cur) is not None
                         and rev_of(version) is not None and rev_of(cur) > rev_of(version)})
    if downgrades:
        msg = ("would write %s over a HIGHER rev already recorded in the saves "
               "(%s). That REPLACES a correct stamp with a stale one and "
               "manufactures the mismatch this tool exists to remove.\n"
               "`read_version` already prefers the runtime stamp over "
               "Version.txt, so reaching here means the inputs genuinely "
               "disagree -- a human has to say which side is stale. Nothing was "
               "written." % (version, ", ".join(downgrades)))
        if a.apply:
            die("REFUSING: " + msg)
        print("⚠️  %s\n" % msg)

    total = len(plans) + len(save_plans)
    if not total:
        print("Everything already agrees with %s and the %d active mods. "
              "Nothing to do." % (version, len(ids)))
        return 0

    if not a.quiet:
        print("build : %s   (LastPlayedVersion form: %s)"
              % (version, short_version(version)))
        print("mods  : %d active" % len(ids))
        print("mode  : %s\n" % ("APPLY" if a.apply else "plan only (use --apply to write)"))
        for name, field, cur, want in plans:
            print("  %-24s %-12s %r -> %r" % (name, field, cur, want))
        for path, changes in save_plans:
            print("  %s" % os.path.basename(path))
            for tag, cur, want in changes:
                print("      %-14s %s -> %s" % (tag, cur, want))

    if not a.apply:
        print("\n%d file(s) would change. Re-run with --apply to write." % total)
        return 0

    written = 0
    for (writer, _), plan in zip(targets, plans):
        path = MODSCONFIG if plan[0].startswith("ModsConfig") else LASTPLAYED
        backup(path)
        writer(version)
        written += 1
    for path, _ in save_plans:
        backup(path)
        ok, err = write_save(path, version, ids, names, steamids)
        if not ok:
            print("  FAILED %s: %s" % (os.path.basename(path), err))
            continue
        written += 1

    # Verify by re-planning: a clean re-plan is the proof, not our own say-so.
    leftover = []
    if plan_modsconfig(version):
        leftover.append("ModsConfig.xml")
    if plan_lastplayed(version):
        leftover.append("LastPlayedVersion.txt")
    for path, _ in save_plans:
        if plan_save(path, version, ids, names, steamids) is not None:
            leftover.append(os.path.basename(path))

    print("\nwrote %d file(s); backups alongside as *%s" % (written, BACKUP_SUFFIX))
    if leftover:
        print("❌ STILL OUT OF SYNC after writing: %s" % ", ".join(leftover))
        return 1
    print("✅ verified: every record now reads %s with %d mods." % (version, len(ids)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

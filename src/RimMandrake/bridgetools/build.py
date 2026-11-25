#!/usr/bin/env python3
"""
build.py - build and deploy the JawaBench RimBridge companion assembly.

WHAT A COMPANION IS
===================
Not a mod. RimWorld's mod loader never sees it. RimBridgeServer loads it late,
out of the GAME-ROOT `BridgeTools` folder, and registers its [Tool] methods onto
the live bridge. So it does not go through src/RimMandrake/Utils/deploy_custom_mods.py, and it
does not appear in ModsConfig.xml.

    repo:  src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll
    game:  <RimWorld>/BridgeTools/JawaBench/JawaBench.BridgeTools.dll

WRITING IS NOT DEPLOYING
========================
Same trap as the mods, same shape: building the DLL and the game being able to
see it are two different claims. Default is plan-only; `--apply` deploys.

THE ONE THING THAT MUST NOT HAPPEN
==================================
The companion must NOT ship RimBridgeServer.Sdk.dll, Assembly-CSharp.dll or any
UnityEngine DLL. RimBridgeServer resolves those to the copies the running game
already loaded; a second copy in the bundle folder means two versions of the
same type in one process, and a TerrainDef built from "our" Assembly-CSharp is
not a TerrainDef the game will accept. The csproj sets Private=false and
CopyLocalLockFileAssemblies=false to prevent it; this script FAILS THE BUILD if
it happens anyway, because the csproj is the thing most likely to be edited
later by someone who does not know this.

REQUIRES A RESTART
==================
Companions are discovered when RimBridgeServer starts. Deploying to a running
game changes nothing until RimWorld is restarted.

THE GM TOOLS ARE IN BY DEFAULT
==============================
The tools inside `#if JAWA_GM_TOOLS` (jawa/fire_incident, jawa/send_letter and
about 48 more) let the world act on the colony. Every game we run is a test game,
so the build includes them; `--no-gm` leaves them out. The plan says which in
capitals either way, because "which tools did I just ship" must never be a thing
you infer from a byte count.

USAGE
  python src/RimMandrake/bridgetools/build.py                 # build + verify, plan the deploy
  python src/RimMandrake/bridgetools/build.py --apply         # build + verify + deploy
  python src/RimMandrake/bridgetools/build.py --apply --clean
  (--apply refuses uncommitted companion sources unless --allow-dirty: deploy from a `git archive HEAD` export)
"""

import argparse
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tool_metadata
import companion_identity  # noqa: E402 - the source hash embedded in the DLL (STEVE_COMPANION_FIX_DLL_STALE_NO_PRIORITIES)

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBench.BridgeTools.csproj")
ARTIFACT_DIR = os.path.join(HERE, "artifacts", "BridgeTools", "JawaBench")
DLL_NAME = "JawaBench.BridgeTools.dll"

DOTNET = os.path.join(os.path.expanduser("~"), ".dotnet", "dotnet.exe")

# Two routes. Under Windows python (repo on D:) everything is a `C:\...` path and dotnet.exe
# builds in place. Under WSL python3 from an ext4 clone (git_workflow_plan_2026-10-01.md §2.3),
# dotnet.exe cannot build a `\\wsl.localhost` path, so the project is staged on D: by
# src/RimMandrake/Utils/winbuild.py and the artifacts copied back; game paths become /mnt/c.
# WSL python3 on a /mnt/d tree is still refused: use python.exe there, as before.
WSL = sys.platform.startswith("linux") and os.path.isdir("/mnt/c")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
STAGED = WSL and not os.path.realpath(REPO_ROOT).startswith("/mnt/")
if STAGED:
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "RimMandrake", "Utils"))
    import winbuild  # noqa: E402

GAME_ROOT = ("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld" if STAGED
             else r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld")
BRIDGETOOLS_ROOT = os.path.join(GAME_ROOT, "BridgeTools")
DEPLOY_DIR = os.path.join(BRIDGETOOLS_ROOT, "JawaBench")
GAME = "a"      # the game the deploy is for: a is Steam's install above; b has its own (aim)


def _game_name():
    """-> the name people read for GAME on this machine: ArchBig, ArchSmall (rimflow/game_names.py, the one map)."""
    rf = os.path.join(REPO_ROOT, "src", "RimMandrake", "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import game_names
    return game_names.show(GAME)


def _gi():
    utils = os.path.join(REPO_ROOT, "src", "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import game_instance
    return game_instance


def aim(name=None):
    """Point the deploy at game `name` (None: RM_GAME_INSTANCE, else a). Game a keeps Steam's install; a named game
    deploys into its own install's BridgeTools (game_instance.game_dir), never the folder game a has loaded
    (RIMMANDRAKE_SPLIT_SECOND_GAME_MODS_FOLDER_SHARED_WITH_FIRST: both games used to load one BridgeTools folder)."""
    global GAME, GAME_ROOT, BRIDGETOOLS_ROOT, DEPLOY_DIR
    gi = _gi()
    GAME = gi.check_name(name or gi.current())
    if GAME != "a":
        GAME_ROOT = gi._native(gi.game_dir(GAME))
        BRIDGETOOLS_ROOT = os.path.join(GAME_ROOT, "BridgeTools")
        DEPLOY_DIR = os.path.join(BRIDGETOOLS_ROOT, "JawaBench")
    return DEPLOY_DIR

# Anything in this list appearing in the output folder is a build error, not a
# warning: each one is a duplicate of a type the host has already loaded.
FORBIDDEN = ("rimbridgeserver.sdk.dll", "assembly-csharp.dll",
             "rimbridgeserver.dll", "rimbridgeserver.contracts.dll",
             "rimbridgeserver.core.dll", "newtonsoft.json.dll",
             "lib.gab.dll", "gabp.runtime.dll")


def sh(cmd, **kw):
    print("+ " + " ".join(cmd if isinstance(cmd, list) else [cmd]))
    return subprocess.run(cmd, **kw)


# The two tools that let the world act on the player rather than on a named
# target. Checked BY NAME in the built DLL, so "the gate worked" is verified
# rather than assumed -- a #if that silently fails to fire is exactly the kind
# of thing that would ship a raid tool believing it had not.
GM_TOOLS = ("jawa/fire_incident", "jawa/send_letter")


def src_hash_prop():
    """-p:JawaSrcHash=<hash of the companion sources on disk>: the csproj embeds it as
    [assembly: AssemblyMetadata("JawaBenchSrcHash", ...)] so a lane can tell, from the DLL alone, which companion
    sources it was compiled from (companion_identity.py; the testq worker refuses a DLL whose hash is not the job's)."""
    h = companion_identity.srchash_worktree(REPO_ROOT)
    if not h:
        sys.exit("cannot hash the companion sources under %s" % companion_identity.SRC_REL)
    return "-p:JawaSrcHash=%s" % h


def verify_src_hash(dll):
    """The built DLL carries the source hash of what is on disk now (a stale incremental output would not)."""
    with open(dll, "rb") as f:
        got = companion_identity.embedded(f.read())
    want = companion_identity.srchash_worktree(REPO_ROOT)
    if got != want:
        sys.exit("\nFAIL: %s embeds source hash %s, the sources on disk hash %s (stale output or a csproj without "
                 "the JawaBenchSrcHash AssemblyMetadata item)" % (dll, got, want))
    print("source hash embedded: %s (companion_identity.py checks it on every lane)" % got[:16])


def build_staged(clean, gm):
    """ext4 clone: stage on D:, build with dotnet.exe there, copy the bundle back."""
    rel_art = os.path.relpath(ARTIFACT_DIR, REPO_ROOT)
    if clean:
        # x.B4: each wipe under the lock its writer holds (the stage is shared by every clone; the clone's copy is
        # written by this clone's copy-back), so a --clean never deletes under a build that is running
        stage_art = os.path.join(winbuild.stage_dir("JawaBench"), rel_art)
        with winbuild.stage_lock("JawaBench"):
            if os.path.isdir(stage_art):
                shutil.rmtree(stage_art)
        with winbuild.clone_outputs_lock():
            if os.path.isdir(ARTIFACT_DIR):
                shutil.rmtree(ARTIFACT_DIR)
    extra = ["--no-incremental", "-p:JawaGmTools=%s" % ("true" if gm else "false"), src_hash_prop()]
    extra_dirs, late = [], []
    # SteveDesktop's install is not the csproj's default (C:\Program Files (x86)\Steam): testcentre_env.sh sets RM_STEAMAPPS.
    sa = os.environ.get("RM_STEAMAPPS")
    if sa and os.path.isfile(os.path.join(sa, "common", "RimWorld", "RimWorldWin64_Data", "Managed", "Assembly-CSharp.dll")):
        extra.append("-p:RimWorldDir=%s" % winbuild.win(os.path.join(sa, "common", "RimWorld")))
        # its Workshop folder, or the copy in Mods/<id> (sync_test_mods.py copies, it does not subscribe)
        for prop, rel, dll in (("RimBridgeSdkDir", "3727949765/1.6/Assemblies", "RimBridgeServer.Sdk.dll"),
                               ("HarmonyDir", "2009463077/1.6/Assemblies", "0Harmony.dll")):
            ws, copy = os.path.join(sa, "workshop", "content", "294100", rel), os.path.join(sa, "common", "RimWorld", "Mods", rel)
            for d in (ws, copy):
                if os.path.isfile(os.path.join(d, dll)):
                    extra.append("-p:%s=%s" % (prop, winbuild.win(d)))
                    break
        # our own mods: the game's copy, else the DLL committed in the repo (a compile reference only, Private=false)
        mods = os.path.join(sa, "common", "RimWorld", "Mods")
        for env, prop, folder, dll in (("ORACLE_MOD_DIR", "OracleModDir", "Oracle/Assemblies", "RimMandrakeOracle.dll"),
                                       ("RIMDEFDUMP_MOD_DIR", "RimDefDumpModDir", "RimDefDump/1.6/Assemblies", "RimDefDump.dll"),
                                       ("DROIDWORKS_MOD_DIR", "DroidworksModDir", "Droidworks/Assemblies", None),
                                       ("INHABITED_MOD_DIR", "InhabitedModDir", "Inhabited/Assemblies", None),
                                       ("GSS_MOD_DIR", "GssModDir", "GimmeSomeSlack/Assemblies", None),
                                       ("FLOWWORKS_MOD_DIR", "FlowWorksModDir", "FlowWorks/Assemblies", None)):
            if os.environ.get(env):
                continue
            here = os.path.join(mods, folder)
            repo = os.path.join(REPO_ROOT, "src", "RimMandrake", folder)
            if os.path.isdir(here) and (dll is None or os.path.isfile(os.path.join(here, dll))):
                extra.append("-p:%s=%s" % (prop, winbuild.win(here)))
            elif dll and os.path.isfile(os.path.join(repo, dll)):
                extra.append("-p:%s=%s" % (prop, winbuild.win(repo)))
    for env, prop in (("ORACLE_MOD_DIR", "OracleModDir"), ("INHABITED_MOD_DIR", "InhabitedModDir"), ("GSS_MOD_DIR", "GssModDir"),
                      ("FLOWWORKS_MOD_DIR", "FlowWorksModDir")):
        v = os.environ.get(env)
        if not v:
            continue
        if os.path.realpath(v).startswith(os.path.realpath(REPO_ROOT) + os.sep):
            extra_dirs.append(v)                 # a repo dir: stage it and point at the staged copy
            late.append((prop, v))
        else:
            extra.append("-p:%s=%s" % (prop, v if ":" in v else winbuild.win(v)))
    if late:                                     # staged paths are known only after a dry stage
        _, rec = winbuild.stage_build(PROJECT, "Release", (), extra_dirs, dry_run=True, stage_name="JawaBench")   # the SAME stage as the build below
        extra += ["-p:%s=%s" % (p, winbuild.staged_win(rec, v)) for p, v in late]
    rc, rec = winbuild.stage_build(PROJECT, "Release", extra, extra_dirs,
                                   copy_back_dirs=[rel_art], stage_name="JawaBench")
    if rc:
        sys.exit("BUILD FAILED")
    return os.path.join(ARTIFACT_DIR, DLL_NAME)


def build(clean, gm):
    if STAGED:
        return build_staged(clean, gm)
    if WSL:
        sys.exit(
            "On the /mnt/d tree run this under Windows Python, not WSL python3 (from an ext4\n"
            "clone, WSL python3 works — it stages the build through winbuild.py):\n"
            "    cd /mnt/d/Luke/dev/RimMandrake && python.exe src/RimMandrake/bridgetools/build.py\n"
            "dotnet.exe cannot accept a /mnt/... project path, and every deploy\n"
            "path in this script is Windows-native.")
    if not os.path.exists(DOTNET):
        sys.exit("dotnet not found at %s (it is not on PATH by design)" % DOTNET)
    if clean and os.path.isdir(ARTIFACT_DIR):
        shutil.rmtree(ARTIFACT_DIR)

    # --no-incremental on purpose: JawaGmTools flips DefineConstants, and an
    # incremental build keys off timestamps, not properties. Skipping it would
    # let a --gm run hand back the previous --no-gm DLL (or the reverse).
    # The whole build is under a second, so there is nothing to save here.
    cmd = [DOTNET, "build", PROJECT, "-c", "Release", "--nologo",
           "--no-incremental", "-p:JawaGmTools=%s" % ("true" if gm else "false"), src_hash_prop()]
    # The Oracle reference defaults to the DEPLOYED game copy, which lags the repo
    # whenever the shutdown deploy is still owed (it broke this build 2026-09-09,
    # missing OracleSettings.claudeCliPath). ORACLE_MOD_DIR overrides it.
    if os.environ.get("ORACLE_MOD_DIR"):
        cmd.append("-p:OracleModDir=%s" % os.environ["ORACLE_MOD_DIR"])
    # Same trap, same fix, for Inhabited (SETTLEMENT_VISIT_LOOP_1): the deployed
    # Mods\Inhabited\Assemblies\Inhabited.dll lags the repo whenever a companion
    # tool adds a new call into RimMandrake.Inhabited and the game is up (so the
    # mod DLL cannot be redeployed this session). INHABITED_MOD_DIR overrides it
    # to point at the repo's own build output (src/RimMandrake/Inhabited/Assemblies)
    # instead, which building Inhabited.csproj writes to WITHOUT touching the
    # live game's Mods folder.
    if os.environ.get("INHABITED_MOD_DIR"):
        cmd.append("-p:InhabitedModDir=%s" % os.environ["INHABITED_MOD_DIR"])
    # GSS and FlowWorks (the hose moved there at the hose port): same trap, same override
    for env, prop in (("GSS_MOD_DIR", "GssModDir"), ("FLOWWORKS_MOD_DIR", "FlowWorksModDir")):
        if os.environ.get(env):
            cmd.append("-p:%s=%s" % (prop, os.environ[env]))
    r = sh(cmd, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit("BUILD FAILED")
    return os.path.join(ARTIFACT_DIR, DLL_NAME)


def verify_bundle(dll):
    """The bundle must contain exactly one DLL: ours."""
    if not os.path.exists(dll):
        sys.exit("build reported success but %s does not exist" % dll)

    stray = []
    for name in sorted(os.listdir(ARTIFACT_DIR)):
        low = name.lower()
        if low in FORBIDDEN:
            stray.append(name)
        elif low.endswith(".dll") and name != DLL_NAME:
            stray.append(name)

    print("\nbundle contents (%s):" % ARTIFACT_DIR)
    for name in sorted(os.listdir(ARTIFACT_DIR)):
        size = os.path.getsize(os.path.join(ARTIFACT_DIR, name))
        flag = "  <-- MUST NOT SHIP" if name in stray else ""
        print("  %-40s %8d B%s" % (name, size, flag))

    if stray:
        sys.exit("\nFAIL: the companion bundle contains assemblies the host "
                 "already provides: %s\nFix the csproj (Private=false, "
                 "CopyLocalLockFileAssemblies=false) rather than deleting them "
                 "by hand." % ", ".join(stray))
    print("\nOK: bundle ships only %s" % DLL_NAME)


def verify_shared_closures(dll):
    """No field of the shared [Tool] class or its <>c may name an optional mod's type: one such
    field kills every static-lambda tool on a list without that mod (closure_scan.py says why)."""
    import closure_scan
    print("")
    if closure_scan.main(["closure_scan", dll]) != 0:
        sys.exit("\nFAIL: refusing to deploy - see closure_scan above.")


def verify_gm_gate(dll, gm):
    """Read the tool names back out of the compiled DLL.

    A [Tool] name is a custom-attribute constructor argument, so it lives in
    the metadata BLOB heap as a length-prefixed UTF-8 SerString (ECMA-335
    II.23.3) -- not as a free string a byte/regex scan can stumble on, and
    not in the #US heap either, which is where ordinary string literals
    (including a DESCRIPTION that merely MENTIONS a tool name in prose) live.
    `tool_metadata.tool_names_from_dll` reads the CustomAttribute table's
    Value column directly and slices each name using the blob's own length
    prefix, so a description that says "unlike jawa/fire_incident, this..."
    can never be mistaken for the attribute application itself: only a real
    [Tool(...)] declaration's first constructor argument is ever considered.

    Until 2026-09-07 this compared exact length-prefixed byte patterns against
    the raw file (calibrated 2026-08-28, itself a fix for an earlier bare
    substring search). That worked but duplicated the same blob-heap
    assumptions `tool_metadata.py` now encodes once, in one place, backed by
    real metadata-table parsing rather than a second calibrated pattern guess.
    """
    present = [t for t in GM_TOOLS if t in tool_metadata.tool_names_from_dll(dll)]

    if gm:
        # ASCII only: the Windows console is cp1252 here and an em dash prints
        # as a replacement char, which makes the one warning that matters most
        # look like a corrupted line.
        print("\n*** GM TOOLS INCLUDED - this build can act on the player. ***")
        for t in GM_TOOLS:
            print("  %-24s %s" % (t, "in DLL" if t in present else "MISSING"))
        missing = [t for t in GM_TOOLS if t not in present]
        if missing:
            sys.exit("\nFAIL: the GM tools are on but %s is not in the built DLL. "
                     "The JAWA_GM_TOOLS constant did not reach the compiler."
                     % ", ".join(missing))
    else:
        print("\nGM tools EXCLUDED (--no-gm).")
        if present:
            sys.exit("\nFAIL: the GM pair is compiled OUT but %s is still in the "
                     "built DLL. Do not deploy this. Check that the #if "
                     "JAWA_GM_TOOLS region still encloses both tools."
                     % ", ".join(present))
        print("  verified absent from the DLL: %s" % ", ".join(GM_TOOLS))


def tool_surface(blob):
    """Every jawa/* tool name declared in a compiled DLL, as an EXACT set.

    BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1, 2026-09-06: this used to decode the
    whole DLL as UTF-16LE and as UTF-8 and regex for a run of `[a-z_]`
    characters, on the theory that a tool name might show up in either the
    UTF-8 blob heap (attribute arguments) or the UTF-16 #US heap (ordinary
    string literals). That theory was right about WHERE names live but wrong
    about HOW to read them: a coincidental re-encoding of blob-heap bytes as
    UTF-16LE can stop looking like a letter partway through a real name, and
    the regex happily reports the truncated fragment as if it were a whole
    tool -- which is exactly what shipped a fictitious lost tool,
    `jawa/pawn_`, that was really a prefix-truncated read of a real,
    still-present name. The same looseness also matched a name merely
    MENTIONED in another tool's Description prose (`jawa/revoke`, subtracted
    by hand in prove_stat_and_room.py's PHANTOMS set because this function
    could not tell the difference).

    `tool_metadata.tool_names_from_dll` fixes both: it walks the actual
    CustomAttribute table and slices each name using the metadata blob's own
    length prefix, so the result is the exact set of `[Tool(...)]`
    declarations compiled into this DLL -- no truncation, no prose
    false-positives, nothing to subtract by hand afterward.

    THE BLIND SPOT THIS STILL HAS, found by turning this check's own lesson
    back on itself
    ------------------------------------------------------------------------
    The test for whether a comparison is a gate or a proxy: CONSTRUCT THE CASE
    WHERE THE THING CHANGES AND YOUR FIELD DOES NOT. If you cannot build one you
    have a gate; if you can, you have a proxy wearing the artifact's clothes.

    This one is easy to build. Tool NAMES are the field, and capability is the
    thing. A tool that keeps its name while losing a parameter, tightening a
    guard, dropping a code path or becoming an outright no-op changes capability
    and moves no name at all. The surfaces compare equal and the deploy sails
    through -- exactly the shape this function was written to catch, one level
    down.

    So state what it is: this catches a tool DISAPPEARING, not a tool getting
    WORSE. It is a gate for the case that actually bit us (a forgotten --gm
    silently dropping two tools) and a proxy for capability in general.

    What covers the rest is src/RimMandrake/bridgetools/prove_new_tools.py, which asks the
    RUNNING game and exercises behaviour rather than names. The two are
    deliberately different questions and neither substitutes for the other:
    this one runs offline before a deploy and answers "did anything vanish?";
    that one needs a live map and answers "does it still work?".
    """
    return tool_metadata.tool_names_from_dll(blob)


def build_stamp(blob):
    """The git commit this DLL was built from, or None.

    The SDK embeds HEAD into AssemblyInformationalVersion as
    '<version>+<40-hex-sha>'. Stored UTF-16 in the metadata, so search both.
    """
    import re
    for enc in ("utf-16-le", "utf-8"):
        try:
            text = blob.decode(enc, "ignore")
        except Exception:
            continue
        m = re.search(r"\d+\.\d+\.\d+\+([0-9a-f]{40})", text)
        if m:
            return m.group(1)
    return None


def game_running():
    """-> True/False from the process list, or None when it cannot be read (then the copy's own refusal decides). The
    deploy's own game (a game nobody can attribute counts): each game maps only its own install's BridgeTools, so game
    b up never refuses game a's deploy (RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_FOUR)."""
    try:
        return _gi().running(GAME)
    except Exception as e:  # noqa: BLE001 - an unreadable list is UNMEASURED, said aloud, never "no game"
        print("  game process check UNMEASURED (%s: %s); the replace itself still refuses a mapped DLL"
              % (type(e).__name__, e))
        return None


def bridge_holder():
    """-> the seat holding game a's driver lock (model.game_a_lock_record), or None when free or unreadable (said aloud,
    UNMEASURED). A named game's bridge is its own driver lock: another live driver on it holds it; game a's lock is not b's."""
    if GAME != "a":
        try:
            held = _gi().live_holder(GAME)
            return ("another live driver of %s (%s)" % (_game_name(), held)) if held else None
        except Exception as e:  # noqa: BLE001
            print("  bridge hold check UNMEASURED (%s: %s)" % (type(e).__name__, e))
            return None
    try:
        sys.path.insert(0, os.path.join(REPO_ROOT, "src", "RimMandrake", "rimflow"))
        import model
        d = model.game_a_lock_record()       # game a's driver lock, the one record (game_lock.py)
        if d and d.get("holder") != "OWNER" and _held_by_my_take(model, d):
            return None
        return d.get("holder") if d else None
    except Exception as e:  # noqa: BLE001
        print("  bridge hold check UNMEASURED (%s: %s)" % (type(e).__name__, e))
        return None


def _held_by_my_take(model, d):
    """Game a's live holder is this build's own take: it inherited the take (RM_HOST_GUARD_GEN, host_guard._reentrant)
    or the holder is this process or an ancestor (game_lock.in_my_tree). The in-game visit's repair holds the lock and
    runs this build as its child; seat names cannot tell that take from another run's, since every detached run is
    BENCH (RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_EIGHT). His OWNER hold is never ours."""
    import game_lock
    import host_guard
    try:
        return bool(host_guard._reentrant(model.game_a_lock_path()) is not None
                    or game_lock.in_my_tree(d.get("identity")))
    except Exception as e:  # noqa: BLE001  could not look: the hold stands
        print("  own-take check UNMEASURED (%s: %s); the hold stands" % (type(e).__name__, e))
        return False


def _my_seat():
    return (os.environ.get("RIMFLOW_SEAT") or os.environ.get("AGENT_SEAT") or "").strip().upper() or None


DESPITE_HOLD = None     # main --despite-hold: deploy into a game held by `pipe off game:<g>`, on purpose


def plan_deploy(dll, apply_it, allow_removal=False, ignore_hold=False):
    print("deploy target: %s, %s" % (_game_name(), DEPLOY_DIR))
    target = os.path.join(DEPLOY_DIR, DLL_NAME)
    exists = os.path.exists(target)
    ours = open(dll, "rb").read()
    theirs = open(target, "rb").read() if exists else b""
    same = exists and ours == theirs

    # WHY THIS IS NOT A PLAIN BYTE COMPARE
    # ====================================
    # The build embeds the git HEAD SHA (see build_stamp), and the PE timestamp
    # and MVID are hashes over the content -- so committing ANYTHING, in any
    # file, by any of the four agents sharing this tree, changes these bytes with
    # no source change whatsoever. Measured 2026-08-12: 96 of 125,440 bytes.
    #
    # A checker that cries "differs" after every commit trains you to ignore it,
    # and this repo has already been there: the last session's notes say
    # "build.py reporting 'differs' is expected, not drift". That sentence is how
    # a real drift gets waved through. So split the two cases apart and let only
    # the second one be alarming.
    ours_at, theirs_at = build_stamp(ours), build_stamp(theirs) if exists else None

    print("\ndeploy plan")
    print("  from : %s" % dll)
    print("  to   : %s" % target)
    # x.B9: anything else in the deploy dir loads beside the companion; say so rather than never looking
    try:
        others = sorted(n for n in os.listdir(DEPLOY_DIR) if n != DLL_NAME)
    except OSError:
        others = []
    if others:
        print("  also in the deploy dir (not touched by this deploy): %s" % ", ".join(others))
    if not exists:
        print("  state: not deployed yet")
    elif same:
        print("  state: identical, nothing to do")
    elif ours_at and theirs_at and ours_at != theirs_at:
        print("  state: differs -- built from a DIFFERENT COMMIT (expected after "
              "any commit)")
        print("         game copy : %s" % theirs_at[:12])
        print("         this build: %s" % ours_at[:12])
        print("         The build is deterministic per commit, so this alone "
              "does NOT mean")
        print("         the tool code changed. Deploy to make them agree.")
    elif ours_at and theirs_at and ours_at == theirs_at:
        print("  state: *** DRIFT *** same commit (%s), DIFFERENT BYTES."
              % ours_at[:12])
        print("         One commit builds different bytes when the sources are dirty, --gm differs, or a")
        print("         reference-dir variable changed; otherwise someone hand-edited the deployed DLL or it")
        print("         is from another checkout. Investigate before overwriting -- --apply replaces it.")
    else:
        print("  state: differs, would overwrite (no build stamp to compare)")

    # WHY THE STAMP IS NOT ENOUGH ON ITS OWN
    # ======================================
    # Everything above compares PROVENANCE (which commit) and never CAPABILITY
    # (which tools). Those come apart in the case this repo actually hit on
    # 2026-08-12: build.py then defaulted to GM tools OFF, so a bare `build.py --apply`
    # against a game copy built with --gm printed the wholly routine "differs --
    # built from a DIFFERENT COMMIT ... Deploy to make them agree" and would have
    # SILENTLY REMOVED jawa/fire_incident and jawa/send_letter. The plan invited
    # the deploy; nothing in it mentioned that two tools were about to vanish.
    #
    # That is the worst failure shape there is -- no error, no log line, and the
    # symptom arrives 25 minutes into a cold load as a tool that is merely absent.
    # A missing tool does not announce itself the way a wrong number does.
    #
    # So compare the tool surfaces too, and let only a REDUCTION be alarming:
    # gaining tools is the normal case for a companion under development.
    # tool_surface() is an EXACT metadata read (tool_metadata.py) as of
    # BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1 -- every name in it is a complete,
    # length-prefix-sliced [Tool(...)] declaration, never a scan artifact. So
    # a straight set difference is safe: unlike the old byte-scan, this
    # cannot manufacture a truncated "jawa/pawn_"-style phantom for a rename
    # to report as a loss (proven live: renaming a real tool's string to
    # "<name>_SUFFIX" reports exactly "<name>" removed and nothing else, even
    # though "<name>" is now a strict prefix of the still-present renamed
    # tool -- a prefix-based filter here would wrongly swallow that real
    # loss, which is why there isn't one).
    removed = sorted((tool_surface(theirs) if exists else set()) - tool_surface(ours))
    if removed:
        print("\n*** THIS DEPLOY WOULD REMOVE TOOLS ***")
        for t in removed:
            print("  LOSES  %s" % t)
        print("  The game copy has these and this build does not. If you did not")
        print("  intend to reduce the companion, check for --no-gm, or for a checkout")
        print("  older than the game copy.")
        print("  Deliberate? Re-run with --allow-tool-removal.")

    if not apply_it:
        print("\nplan only. Re-run with --apply to deploy.")
        return same

    if removed and not allow_removal:
        sys.exit("\nREFUSING TO DEPLOY: it would remove %s.\n"
                 "  Re-run without --no-gm, from a current checkout, or with\n"
                 "  --allow-tool-removal if the reduction is intended."
                 % ", ".join(removed))

    if not os.path.isdir(GAME_ROOT):
        sys.exit("game root not found: %s" % GAME_ROOT)
    if same:
        print("\nalready deployed: identical bytes, nothing copied.")
        return True
    # RIMMANDRAKE_MAKE_COMPANION_DEPLOY_ATOMIC_HELD (x.B1): the game and the bridge hold are checked BEFORE any write
    held = _gi().hold_refusal(GAME, DESPITE_HOLD) if apply_it else None
    if held:
        sys.exit("\nREFUSING TO DEPLOY into %s's %s: %s" % (_game_name(), DEPLOY_DIR, held))
    if game_running():
        sys.exit("\nCANNOT DEPLOY WHILE RIMWORLD IS RUNNING (the process list shows it). Nothing was written.")
    holder = bridge_holder()
    if holder and holder != _my_seat() and not ignore_hold:
        sys.exit("\nREFUSING TO DEPLOY: the bridge is held by %s (this seat: %s). Swapping the companion under a\n"
                 "  held session changes its tools at its next restart. Take the bridge first, or pass\n"
                 "  --ignore-bridge-hold on purpose." % (holder, _my_seat() or "unset"))
    os.makedirs(DEPLOY_DIR, exist_ok=True)
    # x.B2/x.B3: write the bytes already read and checked (never a re-read of the path) to a temp file beside the
    # target, then one atomic replace; any failure leaves the old DLL untouched and removes the temp file.
    tmp = os.path.join(DEPLOY_DIR, ".%s.deploying.%d" % (DLL_NAME, os.getpid()))
    try:
        with open(tmp, "wb") as f:
            f.write(ours)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
    except OSError as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        # WinError 1224 = "a file with a user-mapped section open". RimWorld has
        # the companion memory-mapped for as long as it runs, so the deploy is
        # not merely ineffective while the game is up -- it is IMPOSSIBLE. Worth
        # saying plainly: the raw traceback reads like a permissions bug and
        # sends you looking at the wrong thing entirely.
        if getattr(e, "winerror", None) == 1224 or "user-mapped section" in str(e):
            sys.exit(
                "\nCANNOT DEPLOY WHILE RIMWORLD IS RUNNING.\n"
                "  The game holds %s memory-mapped, so Windows refuses the "
                "overwrite (WinError 1224).\n"
                "  The build is fine and the artifact is up to date -- only the "
                "copy failed.\n"
                "  Close RimWorld, re-run with --apply, then start the game: "
                "companions are\n"
                "  discovered at RimBridgeServer startup, so they need that "
                "restart anyway." % DLL_NAME)
        sys.exit("\nDEPLOY FAILED, the old DLL is untouched: %s: %s" % (type(e).__name__, e))
    import hashlib
    with open(target, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    want = hashlib.sha256(ours).hexdigest()
    if got != want:
        sys.exit("\nDEPLOY READBACK MISMATCH: %s reads sha256 %s, the verified build is %s. Not deployed."
                 % (target, got[:16], want[:16]))
    print("  readback sha256 %s matches the verified build" % got[:16])
    print("\ndeployed. RimBridgeServer only discovers companions at startup, so "
          "this does nothing until RimWorld restarts.")
    return True


def regenerate_canonical_saves():
    """The compiled-in list of canonical world saves is what CANONICAL_SAVE.md says now, for every game this builds for
    (design/specs/2026-11-23-canonical-save-guard/boundary.md). A document it cannot read stops the build: an old list
    could lack a save."""
    utils = os.path.join(REPO_ROOT, "src", "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import canonical_saves as cs
    try:
        wrote = cs.write(REPO_ROOT)
    except cs.Unreadable as e:
        sys.exit("CANONICAL SAVES UNREADABLE: %s" % e)
    print("canonical saves: %s" % ("list written again from %s; commit %s" % (cs.DOC, cs.GENERATED) if wrote else "list is current"))


def source_dirty():
    """-> the `git status --porcelain` lines for the companion's sources (its project folder plus any repo-local
    *_MOD_DIR it stages), [] when they are clean, or None when this tree is not a git checkout (a `git archive`
    export of one commit, which is clean by construction). A shared seat clone carries peers' uncommitted edits, and
    the build compiles whatever is on disk (BENCH 2026-10-15: never build the companion from the dirty tree)."""
    root = os.path.realpath(REPO_ROOT)
    dirs = [os.path.relpath(os.path.realpath(os.path.dirname(PROJECT)), root)]
    for env in ("ORACLE_MOD_DIR", "INHABITED_MOD_DIR", "GSS_MOD_DIR", "FLOWWORKS_MOD_DIR"):
        v = os.environ.get(env)
        if v and os.path.realpath(v).startswith(root + os.sep):
            dirs.append(os.path.relpath(os.path.realpath(v), root))
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    except OSError as e:
        return ["?? git could not run (%s): refusing rather than guessing clean" % e]
    if r.returncode != 0:
        if "not a git repository" in (r.stderr or ""):
            return None                          # an export: no .git anywhere above it
        return ["?? git rev-parse failed: %s" % (r.stderr or "").strip()[:200]]
    top = os.path.realpath(r.stdout.strip())
    if top != root:
        # x.B6: a tree inside some other checkout is an export only when that checkout tracks none of the companion
        # sources; when it does track them, its status is the truth about them
        dirs = [os.path.relpath(os.path.join(root, d), top) for d in dirs]
        r = subprocess.run(["git", "-C", top, "ls-files", "--"] + dirs, capture_output=True, text=True)
        if r.returncode != 0:
            return ["?? git ls-files failed in %s: %s" % (top, (r.stderr or "").strip()[:200])]
        if not r.stdout.strip():
            return None                          # an export unpacked inside some other checkout
        root = top
    r = subprocess.run(["git", "-C", root, "status", "--porcelain", "--untracked-files=normal", "--"] + dirs,
                       capture_output=True, text=True)
    if r.returncode != 0:
        return ["?? git status failed: %s" % (r.stderr or "").strip()[:200]]   # fail closed
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


EXPORT_HINT = ("build from a clean export of committed HEAD instead:\n"
               "    git -C <clone> archive --format=tar HEAD | tar -x -C <empty dir>\n"
               "    python3 <empty dir>/src/RimMandrake/bridgetools/build.py --apply")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="actually deploy to the game")
    ap.add_argument("--clean", action="store_true", help="wipe the artifact folder first")
    ap.add_argument("--gm", action=argparse.BooleanOptionalAction, default=True,
                    help="the tools that let the world act on the colony; on by default, --no-gm leaves them out")
    ap.add_argument("--allow-tool-removal", action="store_true",
                    help="permit a deploy that removes tools the game copy "
                         "already has. Refused by default, because the usual "
                         "cause is an old checkout or --no-gm rather than an "
                         "intent to reduce the companion.")
    ap.add_argument("--ignore-bridge-hold", action="store_true",
                    help="deploy although another seat (or the OWNER) holds the bridge. Refused by default.")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="permit --apply from a checkout whose companion sources have uncommitted changes. "
                         "Refused by default: in a shared seat clone those are usually a peer's edits.")
    ap.add_argument("--instance", metavar="GAME", default=None,
                    help="the game to deploy to: a (Steam's install) or a named game's own install. Default: "
                         "RM_GAME_INSTANCE, else a")
    ap.add_argument("--despite-hold", dest="despite_hold", metavar="WHY", default=None,
                    help="--apply into a game held by `pipe off game:<g>`, on purpose: why")
    args = ap.parse_args(argv)
    global DESPITE_HOLD
    DESPITE_HOLD = args.despite_hold
    aim(args.instance)

    regenerate_canonical_saves()
    dirty = source_dirty()
    if dirty:
        print("*** companion sources are DIRTY in %s:\n  %s" % (REPO_ROOT, "\n  ".join(dirty)))
        if args.apply and not args.allow_dirty:
            sys.exit("\nREFUSING TO DEPLOY a build of uncommitted sources; " + EXPORT_HINT +
                     "\n(or --allow-dirty if every listed change is yours and intended)")
    elif dirty is None:
        print("source: not a git checkout (an export of one commit): treated as clean")

    dll = build(args.clean, args.gm)
    verify_bundle(dll)
    verify_src_hash(dll)
    verify_gm_gate(dll, args.gm)
    verify_shared_closures(dll)
    plan_deploy(dll, args.apply, args.allow_tool_removal, args.ignore_bridge_hold)
    return 0


if __name__ == "__main__":
    sys.exit(main())

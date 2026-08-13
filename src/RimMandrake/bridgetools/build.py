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

THE GM PAIR IS OPT-IN
=====================
jawa/fire_incident and jawa/send_letter are compiled OUT by default. Every other
tool changes only what the caller named; fire_incident can drop a raid on the
colony the owner is playing. `--gm` includes them, and the plan says so in
capitals either way, because "which tools did I just ship" must never be a thing
you infer from a byte count.

USAGE
  python src/RimMandrake/bridgetools/build.py                 # build + verify, plan the deploy
  python src/RimMandrake/bridgetools/build.py --apply         # build + verify + deploy
  python src/RimMandrake/bridgetools/build.py --gm --apply    # ...including the GM pair
  python src/RimMandrake/bridgetools/build.py --apply --clean
"""

import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBench.BridgeTools.csproj")
ARTIFACT_DIR = os.path.join(HERE, "artifacts", "BridgeTools", "JawaBench")
DLL_NAME = "JawaBench.BridgeTools.dll"

DOTNET = os.path.join(os.path.expanduser("~"), ".dotnet", "dotnet.exe")

# This script is Windows-native throughout: DOTNET, GAME_ROOT and DEPLOY_DIR are
# all `C:\...` paths, and dotnet.exe cannot take a `/mnt/d/...` project path even
# though WSL can launch the .exe itself. Under WSL, `~` is /home/<user>, so the
# first symptom is a misleading "dotnet not found" pointing at a Linux path.
# Fail early and say the actual fix instead.
WSL = sys.platform.startswith("linux") and os.path.isdir("/mnt/c")

GAME_ROOT = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld"
BRIDGETOOLS_ROOT = os.path.join(GAME_ROOT, "BridgeTools")
DEPLOY_DIR = os.path.join(BRIDGETOOLS_ROOT, "JawaBench")

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


def build(clean, gm):
    if WSL:
        sys.exit(
            "Run this under Windows Python, not WSL python3:\n"
            "    cd /mnt/d/Luke/dev/Rimworld && python.exe src/RimMandrake/bridgetools/build.py\n"
            "dotnet.exe cannot accept a /mnt/... project path, and every deploy\n"
            "path in this script is Windows-native.")
    if not os.path.exists(DOTNET):
        sys.exit("dotnet not found at %s (it is not on PATH by design)" % DOTNET)
    if clean and os.path.isdir(ARTIFACT_DIR):
        shutil.rmtree(ARTIFACT_DIR)

    # --no-incremental on purpose: JawaGmTools flips DefineConstants, and an
    # incremental build keys off timestamps, not properties. Skipping it would
    # let a --gm run hand back the previous non-GM DLL (or worse, the reverse).
    # The whole build is under a second, so there is nothing to save here.
    r = sh([DOTNET, "build", PROJECT, "-c", "Release", "--nologo",
            "--no-incremental", "-p:JawaGmTools=%s" % ("true" if gm else "false")],
           capture_output=True, text=True)
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


def verify_gm_gate(dll, gm):
    """Read the tool names back out of the compiled DLL.

    Searching the raw bytes needs no IL reader and cannot be fooled by what the
    source LOOKS like it should have produced -- which is the point: the claim
    under test is 'the #if fired', and the source is the thing that claim is
    about, so the source cannot also be the evidence.

    ENCODING, measured 2026-08-12 rather than assumed: a tool name is a [Tool]
    CUSTOM ATTRIBUTE argument, so it is stored in the metadata BLOB heap as
    length-prefixed UTF-8 -- NOT as UTF-16 in the #US heap, which is where
    ordinary string literals live. A UTF-16-only search reports a clean 0/14 on
    a DLL that in fact contains all fourteen. Both encodings are checked below
    because being wrong in the safe direction here means refusing to deploy;
    being wrong in the other direction means shipping a raid tool believing it
    was gated.
    """
    blob = open(dll, "rb").read()
    present = [t for t in GM_TOOLS
               if t.encode("utf-16-le") in blob or t.encode("utf-8") in blob]

    if gm:
        # ASCII only: the Windows console is cp1252 here and an em dash prints
        # as a replacement char, which makes the one warning that matters most
        # look like a corrupted line.
        print("\n*** GM TOOLS INCLUDED - this build can act on the player. ***")
        for t in GM_TOOLS:
            print("  %-24s %s" % (t, "in DLL" if t in present else "MISSING"))
        missing = [t for t in GM_TOOLS if t not in present]
        if missing:
            sys.exit("\nFAIL: --gm was passed but %s is not in the built DLL. "
                     "The JAWA_GM_TOOLS constant did not reach the compiler."
                     % ", ".join(missing))
    else:
        print("\nGM tools EXCLUDED (default). Pass --gm to include "
              "jawa/fire_incident and jawa/send_letter.")
        if present:
            sys.exit("\nFAIL: the GM pair is compiled OUT but %s is still in the "
                     "built DLL. Do not deploy this. Check that the #if "
                     "JAWA_GM_TOOLS region still encloses both tools."
                     % ", ".join(present))
        print("  verified absent from the DLL: %s" % ", ".join(GM_TOOLS))


def tool_surface(blob):
    """Every jawa/* tool name found in a compiled DLL, as a set.

    Same byte-scanning trick as verify_gm_gate, and the same reason for it: the
    question is what the ARTIFACT contains, so the source cannot be the evidence.
    Both encodings, because tool names live in the UTF-8 blob heap as custom
    attribute arguments while ordinary literals are UTF-16 in #US.

    KNOWN IMPRECISION, stated because it decides how the result may be used:
    this also matches a tool name MENTIONED in another tool's description
    string ("...call jawa/refresh_rect once."). So the set is an upper bound on
    the registered tools, not an exact census -- get that from the live game via
    prove_new_tools.py, which asks the running server.

    The imprecision is harmless for the one comparison below, which is the
    direction that matters: a name present in the deployed copy and absent from
    the new build is a real capability reduction either way, because a prose
    mention only disappears when the text mentioning it does.

    THE BLIND SPOT, found by turning this check's own lesson back on itself
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
    import re
    names = set()
    for enc in ("utf-16-le", "utf-8"):
        names |= set(re.findall(r"jawa/[a-z_]{3,40}", blob.decode(enc, "ignore")))
    return names


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


def plan_deploy(dll, apply_it, allow_removal=False):
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
        print("         The build is deterministic, so this should be "
              "impossible. Someone")
        print("         hand-edited the deployed DLL, or it is from another "
              "checkout. Investigate")
        print("         before overwriting -- --apply will destroy whatever "
              "is there.")
    else:
        print("  state: differs, would overwrite (no build stamp to compare)")

    # WHY THE STAMP IS NOT ENOUGH ON ITS OWN
    # ======================================
    # Everything above compares PROVENANCE (which commit) and never CAPABILITY
    # (which tools). Those come apart in the case this repo actually hit on
    # 2026-08-12: build.py defaults to GM tools OFF, so a bare `build.py --apply`
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
    removed = sorted(tool_surface(theirs) - tool_surface(ours)) if exists else []
    if removed:
        print("\n*** THIS DEPLOY WOULD REMOVE TOOLS ***")
        for t in removed:
            print("  LOSES  %s" % t)
        print("  The game copy has these and this build does not. If you did not")
        print("  intend to reduce the companion, you are probably missing a build")
        print("  flag -- --gm is OFF by default and drops the GM pair.")
        print("  Deliberate? Re-run with --allow-tool-removal.")

    if not apply_it:
        print("\nplan only. Re-run with --apply to deploy.")
        return same

    if removed and not allow_removal:
        sys.exit("\nREFUSING TO DEPLOY: it would remove %s.\n"
                 "  Re-run with --gm if you meant to keep the GM pair, or with\n"
                 "  --allow-tool-removal if the reduction is intended."
                 % ", ".join(removed))

    if not os.path.isdir(GAME_ROOT):
        sys.exit("game root not found: %s" % GAME_ROOT)
    os.makedirs(DEPLOY_DIR, exist_ok=True)
    try:
        shutil.copy2(dll, target)
    except OSError as e:
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
        raise
    print("\ndeployed. RimBridgeServer only discovers companions at startup, so "
          "this does nothing until RimWorld restarts.")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="actually deploy to the game")
    ap.add_argument("--clean", action="store_true", help="wipe the artifact folder first")
    ap.add_argument("--gm", action="store_true",
                    help="include jawa/fire_incident and jawa/send_letter, which "
                         "let the world act on the player. Off by default; needs "
                         "the owner's ruling.")
    ap.add_argument("--allow-tool-removal", action="store_true",
                    help="permit a deploy that removes tools the game copy "
                         "already has. Refused by default, because the usual "
                         "cause is a forgotten --gm rather than an intent to "
                         "reduce the companion.")
    args = ap.parse_args(argv)

    dll = build(args.clean, args.gm)
    verify_bundle(dll)
    verify_gm_gate(dll, args.gm)
    plan_deploy(dll, args.apply, args.allow_tool_removal)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""The 0.1.0 reading of sc_fire_catches_and_runs, taken by the same instrument: the mod/Pyrelands/v0.1.0 DLL with
FireCatchesProbe (FireEcologyHook.cs, the block between its begin and end markers: read-only, it changes no burn) built in.

    python3 src/RimMandrake/Pyrelands/fire_catches_take010.py build [--out DIR]
        exports the tag's Pyrelands source (and the shared source its csproj links) to DIR (default
        /mnt/d/ClaudeWork/rimmandrake/fire_catches/tag010, a Windows drive), puts the probe block before the tag
        FireEcologyHook.cs's namespace close, builds it in place with this clone's winbuild.py (exported beside it), prints
        the DLL's path. DIR must be fresh or an earlier export of the same tag.
Then, live (Stage 6), with the game shut: deploy the current build (Pyrelands ships composed: deploy_custom_mods.py
--compose biomes --apply), then in the game's Mods\\RimMandrake.Biomes\\Biomes\\Pyrelands replace Defs, Patches and
Languages with the tag's (git archive mod/Pyrelands/v0.1.0 of those three folders; the current Defs name classes the tag
DLL lacks, e.g. RM_Plant_WithersUnderRoof, ember grass's thingClass: live 2026-11-27) and put that DLL (and its .srchash)
over Assemblies\\FireEcologyHook.dll. Load, and run the chain with PYRE_FCR_TAKE_010=1 (fire_catches_live.py); it writes
fire_catches_010_reading.json beside the chain and judges nothing. Redeploy the current build afterwards.
"""
import argparse
import io
import os
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TAG = "mod/Pyrelands/v0.1.0"
HOOK = "src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs"
CSPROJ = "src/RimMandrake/Pyrelands/Source/FireEcologyHook.csproj"
EXPORT = ("src/RimMandrake/Pyrelands/Source", "src/RimMandrake/Pyrelands/Assemblies", "src/RimMandrake/_Shared",
          "src/Directory.Build.targets")
BEGIN = "// FireCatchesProbe begin"
END = "// FireCatchesProbe end"
OUT = "/mnt/d/ClaudeWork/rimmandrake/fire_catches/tag010"


def probe_block(src):
    """Pure. The current FireEcologyHook.cs -> the probe block, its marker lines included; None if either marker is gone."""
    i, j = src.find(BEGIN), src.find(END)
    if i < 0 or j < i:
        return None
    i = src.rfind("\n", 0, i) + 1
    return src[i:j + len(END)] + "\n"


def inject(tag_src, block):
    """Pure. The tag's FireEcologyHook.cs and the probe block -> the source with the block before the namespace's closing
    brace (the file's last '}'); None when the tag source already names the probe or has no closing brace."""
    if "class FireCatchesProbe" in tag_src or not block:
        return None
    j = tag_src.rstrip().rfind("}")
    if j < 0:
        return None
    return tag_src[:j] + block + tag_src[j:]


def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), check=True, stdout=subprocess.PIPE).stdout


def build(out):
    # the tag's mod source; this clone's build plumbing: winbuild.py, run from out, builds out in place (its ROOT is a /mnt
    # path), and Directory.Build.props finds 0Harmony.dll where this machine has it (the tag's path is gone)
    for ref, paths in ((TAG, EXPORT), ("HEAD", ("src/RimMandrake/Utils", "src/RimMandrake/contracts",
                                                "src/Directory.Build.props"))):
        data = git("archive", "--format=tar", ref, "--", *paths)
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            tf.extractall(out)
    with open(os.path.join(ROOT, HOOK), encoding="utf-8") as f:
        block = probe_block(f.read())
    path = os.path.join(out, HOOK)
    with open(path, encoding="utf-8") as f:
        merged = inject(f.read(), block)
    if merged is None:
        sys.exit("probe block not found in %s, or the tag already has it" % HOOK)
    with open(path, "w", encoding="utf-8") as f:
        f.write(merged)
    r = subprocess.run([sys.executable, os.path.join(out, "src", "RimMandrake", "Utils", "winbuild.py"),
                        os.path.join(out, CSPROJ)])
    dll = os.path.join(out, "src", "RimMandrake", "Pyrelands", "Assemblies", "FireEcologyHook.dll")
    print("TAG010_DLL %s rc=%d" % (dll, r.returncode))
    return r.returncode


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["build"])
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    return build(a.out)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

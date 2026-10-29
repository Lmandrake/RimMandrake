#!/usr/bin/env python3
r"""Copy the third-party mods of the MINIMAL test list, and the JawaBench companion, to SteveDesktop.

STEVEDESKTOP_MODS_INSTALL_BRIDGE_AND_MINIMAL (2026-10-25). SteveDesktop's Steam login has none
of our Workshop subscriptions, and subscribing needs the Steam client's UI, which is not
scriptable from here. So every non-Ludeon, non-`mandrake.*` mod on
`infrastructure/state/modlists/ModsConfig.MINIMAL.xml` is copied from Archmagi's Workshop
folder into SteveDesktop's `RimWorld\Mods\<workshop id>` as a local mod (RimWorld loads by packageId;
the folder name does not matter). Our own mods are not copied here: the runner clone deploys
them with deploy_custom_mods.py, exactly as on Archmagi.

The companion is THIS clone's build (src/RimMandrake/bridgetools/artifacts/, from build.py --gm), never
Archmagi's game copy: it must be FRESH - its embedded source hash equal to the companion sources at HEAD
(bridgetools/companion_identity.py) - or nothing is sent. It goes to the worker's inbox
`$STEVE_TESTQ_HOME/companion/` (default /mnt/d/RimTest/testq), not the game folder: the game holds the DLL
mapped while it runs, so the worker's deploy phase installs it with the game down at the next job
(STEVE_COMPANION_FIX_DLL_STALE_NO_PRIORITIES, 2026-10-29: this script used to copy Archmagi's game copy and
call it "same" on file count + byte total; a PE file is 512-byte aligned, so a rebuild from other source
routinely has the same size, and SteveDesktop ran droid_dig on a companion missing manualPrioritiesOn).
The companion is compared by sha256.

    python3 infrastructure/stevedesktop/sync_test_mods.py            # plan: what would go where
    python3 infrastructure/stevedesktop/sync_test_mods.py --apply    # stream each folder over ssh

Runs on Archmagi WSL. Target: `$STEVE_WSL` (default mandrake@stevedesktop-wsl) and
`$STEVE_GAME_WSL` (default /mnt/d/SteamLibrary/steamapps/common/RimWorld). A folder already
present with the same file count and byte total is skipped. A target that cannot be read (ssh down)
is UNMEASURED and a source folder absent here is MISSING; both exit 1, never 'same' or 'copy'.
"""
import argparse
import os
import re
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "bridgetools"))
import companion_identity as CI  # noqa: E402
import game_paths as gp  # noqa: E402
from rimworld_loadset import parse_mods_config  # noqa: E402

MINIMAL = os.path.join(REPO, "infrastructure", "state", "modlists", "ModsConfig.MINIMAL.xml")
TARGET = os.environ.get("STEVE_WSL", "mandrake@stevedesktop-wsl")
GAME = os.environ.get("STEVE_GAME_WSL", "/mnt/d/SteamLibrary/steamapps/common/RimWorld")
INBOX = os.environ.get("STEVE_TESTQ_HOME", "/mnt/d/RimTest/testq") + "/companion"
ARTIFACT = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "artifacts", "BridgeTools", "JawaBench")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "-o", "LogLevel=ERROR", TARGET]
_SKIP = re.compile(r"<(modDependencies\w*|loadAfter\w*|loadBefore\w*|incompatibleWith\w*)>.*?</\1>", re.S)


def own_package_id(about):
    """The mod's OWN packageId: the first one outside dependency/load-order blocks
    (About.xml often names Harmony in modDependencies before its own id)."""
    with open(about, encoding="utf-8", errors="replace") as f:
        m = re.search(r"<packageId>\s*([^<\s]+)", _SKIP.sub("", f.read()))
    return m.group(1).lower() if m else None


def wanted(path=None):
    """Third-party ids of <activeMods> only (parsed, not grepped: a commented-out <li> or another list must not count)."""
    ids, _ = parse_mods_config(path or MINIMAL)
    out = []
    for i in ids:
        if i.startswith(("ludeon.", "mandrake.")) or i in out:
            continue
        out.append(i)
    return out


def locate(ids):
    found = {}
    for d in sorted(os.listdir(gp.WORKSHOP)):
        about = os.path.join(gp.WORKSHOP, d, "About", "About.xml")
        if os.path.isfile(about):
            pid = own_package_id(about)
            if pid in ids and pid not in found:
                found[pid] = os.path.join(gp.WORKSHOP, d)
    return found


def tally(path):
    n = b = 0
    for root, _, files in os.walk(path):
        for f in files:
            n += 1
            b += os.path.getsize(os.path.join(root, f))
    return n, b


def remote_tally(path):
    """(files, bytes) on the target; (0, 0) for an absent folder; None when the target could not be read
    (ssh failed or printed no tally) - unread is not empty."""
    cmd = "cd %s 2>/dev/null && find . -type f -printf '%%s\\n' | awk '{n++; b+=$1} END {print n+0, b+0}' || echo 0 0" % shlex.quote(path)
    try:
        r = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None
    f = r.stdout.split()
    if r.returncode or len(f) != 2 or not all(x.isdigit() for x in f):
        return None
    return int(f[0]), int(f[1])


def remote_sha(path):
    """sha256 of the file on the target; "" when it is absent; None when the target could not be read."""
    q = shlex.quote(path)
    cmd = "if [ -f %s ]; then sha256sum %s | cut -d' ' -f1; else echo absent; fi" % (q, q)
    try:
        r = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    out = r.stdout.strip()
    if r.returncode or not (out == "absent" or re.fullmatch(r"[0-9a-f]{64}", out)):
        return None
    return "" if out == "absent" else out


def push_file(src, dest_dir):
    """Stream one file into `dest_dir` on the target under its own name (a .part, then an atomic mv)."""
    d, f = shlex.quote(dest_dir), shlex.quote(dest_dir + "/" + os.path.basename(src))
    with open(src, "rb") as fh:
        r = subprocess.run(SSH + ["set -e; mkdir -p %s; cat > %s.part; mv %s.part %s" % (d, f, f, f)], stdin=fh,
                           capture_output=True, timeout=600)
    if r.returncode:
        raise RuntimeError("push %s failed: ssh=%s %s" % (src, r.returncode, r.stderr.decode(errors="replace").strip()))


def companion(apply):
    """Stage this clone's companion build in the worker's inbox -> 0 ok / 1 refused, unread or mismatched."""
    v = CI.verdict(os.path.join(ARTIFACT, CI.DLL_NAME), REPO, "HEAD")
    if v["state"] != "FRESH":
        print("%s JawaBench companion: %s - not sent; build it here first: python3 src/RimMandrake/bridgetools/"
              "build.py --gm" % (v["state"], CI.describe(v)))
        return 1
    dest = INBOX + "/" + CI.DLL_NAME
    remote = remote_sha(dest)
    if remote is None:
        print("UNMEASURED JawaBench companion: could not read %s on %s (ssh failed)" % (dest, TARGET))
        return 1
    state = "same" if remote == v["dll_sha256"] else "copy"
    print("%-4s %-42s sha256 %s (source hash %s) -> %s" % (state, "JawaBench companion", v["dll_sha256"][:12],
                                                          v["embedded"][:12], dest))
    if state == "copy" and apply:
        push_file(v["dll"], INBOX)
        after = remote_sha(dest)
        print("     %s (target sha256 %s; the next testq job installs it with the game down)" % (
            "ok" if after == v["dll_sha256"] else "MISMATCH", "unreadable" if after is None else after[:12] or "absent"))
        return 0 if after == v["dll_sha256"] else 1
    return 0


def push(src, dest_parent, name):
    """tar `src` as `name` into `dest_parent` on the target, replacing what is there."""
    if not re.match(r"^[\w.-]+$", name):
        raise ValueError("unsafe folder name %r" % name)
    p, part = shlex.quote(dest_parent), name + ".part"
    rcmd = (f"set -e; mkdir -p {p}; cd {p}; rm -rf {part}; mkdir {part}; tar -xf - -C {part}; "
            f"rm -rf {name}; mv {part}/{name} {name}; rmdir {part}")
    tar = subprocess.Popen(["tar", "-cf", "-", "-C", os.path.dirname(src), "--transform",
                            "s,^%s,%s," % (re.escape(os.path.basename(src)), name), os.path.basename(src)],
                           stdout=subprocess.PIPE)
    r = subprocess.run(SSH + [rcmd], stdin=tar.stdout, capture_output=True, text=True, timeout=1800)
    tar.stdout.close()
    tar.wait()
    if tar.returncode or r.returncode:
        raise RuntimeError("push %s failed: tar=%s ssh=%s %s" % (src, tar.returncode, r.returncode, r.stderr.strip()))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="copy (default: plan only)")
    a = ap.parse_args()
    ids = wanted()
    found = locate(ids)
    missing = [i for i in ids if i not in found]
    jobs = [(found[i], GAME + "/Mods", os.path.basename(found[i]), i) for i in ids if i in found]
    bad = companion(a.apply)
    for src, parent, name, label in jobs:
        if not os.path.isdir(src):          # an absent source tallies (0, 0) and would read 'same' as an absent target
            print("MISSING %s: source folder %s does not exist here" % (label, src))
            bad += 1
            continue
        local = tally(src)
        remote = remote_tally(parent + "/" + name)
        if remote is None:
            print("UNMEASURED %s: could not read %s/%s on %s (ssh failed)" % (label, parent, name, TARGET))
            bad += 1
            continue
        state = "same" if local == remote else "copy"
        print("%-4s %-42s %5d files %8.1f MB -> %s/%s" % (state, label, local[0], local[1] / 1e6, parent, name))
        if state == "copy" and a.apply:
            push(src, parent, name)
            after = remote_tally(parent + "/" + name)
            ok = after == local
            bad += not ok
            print("     %s (target now %s)" % ("ok" if ok else "MISMATCH",
                                             "unreadable" if after is None else "%d files, %d bytes" % after))
    for i in missing:
        print("MISSING %s: not in Archmagi's Workshop folder %s" % (i, gp.WORKSHOP))
    if not a.apply:
        print("\nplan only; --apply copies")
    return 1 if (missing or bad) else 0


if __name__ == "__main__":
    sys.exit(main())

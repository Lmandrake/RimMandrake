#!/usr/bin/env python3
r"""Copy the third-party mods of the MINIMAL test list, and the JawaBench companion, to SteveDesktop.

STEVEDESKTOP_MODS_INSTALL_BRIDGE_AND_MINIMAL (2026-10-25). SteveDesktop's Steam login has none
of our Workshop subscriptions, and subscribing needs the Steam client's UI, which is not
scriptable from here. So every non-Ludeon, non-`mandrake.*` mod on
`infrastructure/state/modlists/ModsConfig.MINIMAL.xml` is copied from Archmagi's Workshop
folder into SteveDesktop's `RimWorld\Mods\<workshop id>` as a local mod (RimWorld loads by packageId;
the folder name does not matter). Our own mods are not copied here: the runner clone deploys
them with deploy_custom_mods.py, exactly as on Archmagi.

The companion goes to `RimWorld\BridgeTools\JawaBench\` (RimBridgeServer discovers it there at
start; it cannot be replaced while the game runs, so stop the game first).

    python3 infrastructure/stevedesktop/sync_test_mods.py            # plan: what would go where
    python3 infrastructure/stevedesktop/sync_test_mods.py --apply    # stream each folder over ssh

Runs on Archmagi WSL. Target: `$STEVE_WSL` (default mandrake@stevedesktop-wsl) and
`$STEVE_GAME_WSL` (default /mnt/d/SteamLibrary/steamapps/common/RimWorld). A folder already
present with the same file count and byte total is skipped.
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
import game_paths as gp  # noqa: E402

MINIMAL = os.path.join(REPO, "infrastructure", "state", "modlists", "ModsConfig.MINIMAL.xml")
TARGET = os.environ.get("STEVE_WSL", "mandrake@stevedesktop-wsl")
GAME = os.environ.get("STEVE_GAME_WSL", "/mnt/d/SteamLibrary/steamapps/common/RimWorld")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "-o", "LogLevel=ERROR", TARGET]
_SKIP = re.compile(r"<(modDependencies\w*|loadAfter\w*|loadBefore\w*|incompatibleWith\w*)>.*?</\1>", re.S)


def own_package_id(about):
    """The mod's OWN packageId: the first one outside dependency/load-order blocks
    (About.xml often names Harmony in modDependencies before its own id)."""
    with open(about, encoding="utf-8", errors="replace") as f:
        m = re.search(r"<packageId>\s*([^<\s]+)", _SKIP.sub("", f.read()))
    return m.group(1).lower() if m else None


def wanted():
    with open(MINIMAL, encoding="utf-8") as f:
        ids = re.findall(r"<li>\s*([^<\s]+)\s*</li>", f.read())
    out = []
    for i in ids:
        i = i.lower()
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
    cmd = "cd %s 2>/dev/null && find . -type f -printf '%%s\\n' | awk '{n++; b+=$1} END {print n+0, b+0}' || echo 0 0" % shlex.quote(path)
    r = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=300)
    n, b = (r.stdout.split() + ["0", "0"])[:2]
    return int(n), int(b)


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
    jawa = os.path.join(gp.GAME_DIR, "BridgeTools", "JawaBench")
    jobs.append((jawa, GAME + "/BridgeTools", "JawaBench", "JawaBench companion"))
    bad = 0
    for src, parent, name, label in jobs:
        local = tally(src)
        remote = remote_tally(parent + "/" + name)
        state = "same" if local == remote else "copy"
        print("%-4s %-42s %5d files %8.1f MB -> %s/%s" % (state, label, local[0], local[1] / 1e6, parent, name))
        if state == "copy" and a.apply:
            push(src, parent, name)
            after = remote_tally(parent + "/" + name)
            ok = after == local
            bad += not ok
            print("     %s (target now %d files, %d bytes)" % ("ok" if ok else "MISMATCH", after[0], after[1]))
    for i in missing:
        print("MISSING %s: not in Archmagi's Workshop folder %s" % (i, gp.WORKSHOP))
    if not a.apply:
        print("\nplan only; --apply copies")
    return 1 if (missing or bad) else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Outcome check of EXTRA_LOOKS_WIRE_AS_THEY_TRICKLE_IN: is every rendered commissioned look (xart_* job in the art
queue's done/) of a mod that is not held in the game, its facings installed under src/ and its texPath in a def?

    python3 src/RimMandrake/Utils/artpipe/xart_wired.py        exit 0 every look is in, 1 one is not (or none rendered),
                                                               2 the queue could not be read here or on Archmagi

The queue lives on Archmagi (state_dir.py). Where this machine has none, the same reading runs on Archmagi over ssh, in
its seat clone (this file sent on stdin); it is never answered from an empty folder. Held mods: src/RimMandrake/rimflow/mod_owner_hold.json.
"""
from __future__ import annotations

import collections
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4] if HERE.name == "xart_wired.py" else Path.cwd()     # run from stdin on Archmagi: cwd is its clone
ARCHMAGI = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "mandrake@archmagi-wsl",
            "cd ~/rm/bench && python3 - --here"]                            # this file on stdin: no copy there is assumed


def reading(queue: Path, repo: Path = REPO) -> tuple[int, list[str]]:
    """-> (rendered unheld looks, those not installed and wired), from the queue's done/ and the repo at `repo`."""
    held = {h["mod"] for h in json.loads((repo / "src/RimMandrake/rimflow/mod_owner_hold.json").read_text())["holds"]}
    looks = collections.defaultdict(list)
    for p in (queue / "done").glob("xart_*.json"):
        if p.name.endswith(".manifest.json"):
            continue
        j = json.loads(p.read_text())
        if j["install_to"].split("/")[2] not in held:
            looks[j["target_texpath"]].append(j["install_to"])

    def wired(t):
        # hang guard: a grep of src/ takes about a second; 120 s is far above a real run, never a speed bar
        return subprocess.run(["grep", "-rqF", "<texPath>%s</texPath>" % t, str(repo / "src"), "--include=*.xml"],
                              timeout=120).returncode == 0
    bad = sorted(t for t, fs in looks.items() if not all((repo / f).is_file() for f in fs) or not wired(t))
    return len(looks), bad


def main(argv) -> int:
    sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/artpipe"))
    import state_dir
    try:
        q = state_dir.require()
    except BaseException as e:  # noqa: BLE001 — absent here: read it where it lives
        if "--here" in argv:
            print("UNMEASURED: %s" % e)
            return 2
        try:
            # hang guard: the remote reading takes about 20 s; 300 s is far above a real run, never a speed bar
            r = subprocess.run(ARCHMAGI, input=Path(__file__).read_text(), capture_output=True, text=True, timeout=300)
        except Exception as e2:  # noqa: BLE001
            print("UNMEASURED: no queue here (%s) and Archmagi could not be read (%s)" % (e, e2))
            return 2
        print("read on Archmagi: " + (r.stdout.strip() or r.stderr.strip()[-300:]))
        return r.returncode if r.returncode in (0, 1) else 2
    n, bad = reading(q)
    print("rendered unheld looks %d, not installed and wired %d %s" % (n, len(bad), bad[:3]))
    return 1 if bad or not n else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

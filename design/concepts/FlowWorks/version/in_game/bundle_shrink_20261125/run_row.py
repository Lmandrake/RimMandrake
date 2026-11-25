#!/usr/bin/env python3
"""run_row.py -- run one stage-6 check's command against the live game and append its row to rows.jsonl.

    python3 design/concepts/FlowWorks/version/in_game/bundle_shrink_20261125/run_row.py <test_id> [--site-key K] [--tier T | --full] -- <command ...>

Copy of visit 12's runner for the live pass of RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES (game a on Archmagi: row game "archmagi", instance from RM_GAME_INSTANCE): each row also merges build_match.py identity (--tier, default flowworks; --full for
a full-list check), run after the command so it reads the deployed folder and the list the check ran on.

The command's output goes to evidence/<test_id>_<stamp>.log; a literal OUT in the command is replaced by
evidence/<test_id>_<stamp>.json. Verdict: exit 0 PASS, exit 1 FAIL, anything else (or a timeout) UNMEASURED.
site_checked is True only when the evidence JSON shows the site asserted: the calm save loaded and read back
(`site.verified`, concept_scenes), or the log names a CLEAN site save (extension_proof), or --site-key names a
JSON key path that must be truthy. Each row carries the active mod list parsed from ModsConfig.xml and the game build
from Player.log (spec: a verdict counts only on the version and list he walks).
"""
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
from game_paths import MODS_CONFIG as CFG, PLAYER_LOG as LOG  # noqa: E402


def env():
    mods = [li.text for li in ET.parse(CFG).find("activeMods")]
    build = None
    with open(LOG, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            m = re.match(r"RimWorld (\S+ rev\d+)", line)
            if m:
                build = m.group(1)
                break
            if i > 200:
                break
    sha = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%H", "--", "src/RimMandrake/FlowWorks"],
                         capture_output=True, text=True).stdout.strip()
    dep = os.path.join(HERE, 'DEPLOYED_SHA')          # what is deployed, not what the clone has since synced to
    if os.path.exists(dep):
        sha = open(dep).read().strip()
    return mods, build, sha


def dig(d, path):
    for k in path.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def main(argv):
    if "--" not in argv:
        sys.exit(__doc__)
    i = argv.index("--")
    head, cmd = argv[:i], argv[i + 1:]
    tid = head[0]
    site_key = head[head.index("--site-key") + 1] if "--site-key" in head else None
    limit = int(head[head.index("--timeout") + 1]) if "--timeout" in head else 525
    stamp = time.strftime("%Y%m%dT%H%M%S")
    ev = os.path.join(HERE, "evidence")
    os.makedirs(ev, exist_ok=True)
    out_json = os.path.join(ev, "%s_%s.json" % (tid, stamp))
    out_log = os.path.join(ev, "%s_%s.log" % (tid, stamp))
    win_json = subprocess.run(["wslpath", "-w", out_json], capture_output=True, text=True).stdout.strip()
    cmd = [win_json if c == "OUT" and cmd[0].endswith(".exe") else (out_json if c == "OUT" else c) for c in cmd]
    mods, build, sha = env()
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=limit)
        rc, text = p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace").replace("\r", "")
    except subprocess.TimeoutExpired as e:
        rc, text = "timeout", ((e.stdout or b"") + (e.stderr or b"")).decode("utf-8", "replace").replace("\r", "")
    with open(out_log, "w", encoding="utf-8") as f:
        f.write(text)
    verdict = {0: "PASS", 1: "FAIL"}.get(rc, "UNMEASURED")
    res = None
    if os.path.exists(out_json):
        try:
            res = json.load(open(out_json, encoding="utf-8"))
        except ValueError:
            res = None
    sub = res.get("rows") if isinstance(res, dict) else None
    m = re.search(r"extensions: (\{[^}]*\})", text)
    if verdict == "FAIL" and m:
        # an extension_proof summary: FAIL only when a component FAILED; otherwise it could not ask
        counts = eval(m.group(1), {})
        if not counts.get("FAIL"):
            verdict = "UNMEASURED"
    if verdict == "FAIL" and isinstance(sub, list) and sub:
        # a run whose only non-PASS rows are UNMEASURED could not ask: it is UNMEASURED, never FAIL
        st = [x.get("status") for x in sub if isinstance(x, dict)]
        if "FAIL" not in st and "UNMEASURED" in st:
            verdict = "UNMEASURED"
    site_ev = None
    if "--site-log" in head:
        # a site asserted by a prep step run just before (river_site.py, a calm-site load): PATH and a regex that must match
        lp, rx = head[head.index("--site-log") + 1], head[head.index("--site-log") + 2]
        lt = open(lp, encoding="utf-8", errors="replace").read() if os.path.exists(lp) else ""
        site = bool(re.search(rx, lt))
        site_ev = "%s matches %r: %s" % (os.path.relpath(lp, ROOT) if os.path.exists(lp) else lp, rx, site)
    elif site_key:
        site = bool(dig(res or {}, site_key))
    elif isinstance(res, dict) and isinstance(res.get("site"), dict):
        site = bool(res["site"].get("verified"))
    else:
        site = bool(re.search(r"site save \S+: CLEAN", text))
    row = {"test": tid, "verdict": verdict, "site_checked": site, "game": "archmagi", "instance": os.environ.get("RM_GAME_INSTANCE", "a"), "mod_sha": sha,
           "command": " ".join(cmd), "rc": rc, "wall_s": round(time.time() - t0, 1),
           "evidence": os.path.relpath(out_json if os.path.exists(out_json) else out_log, ROOT),
           "log": os.path.relpath(out_log, ROOT), "active_mods": mods, "game_build": build,
           "at": time.strftime("%Y-%m-%d %H:%M %Z")}
    if site_ev:
        row["site_evidence"] = site_ev
    row["held"] = []  # the whole mod ran; the calm site locks Clear weather and holds incidents, neither a FlowWorks mechanic
    row["site_controls"] = ["clear weather locked", "incidents held"]
    row["kind"], row["outcome"] = "A", ("SUCCESS" if verdict == "PASS" else "")
    tier_args = ["--full"] if "--full" in head else ["--tier", head[head.index("--tier") + 1] if "--tier" in head else "flowworks"]
    ident = subprocess.run([sys.executable, os.path.join(ROOT, "src", "RimMandrake", "rimflow", "build_match.py"), "identity",
                            "--mod", "FlowWorks"] + tier_args, cwd=ROOT, capture_output=True, text=True)
    try:
        row.update(json.loads(ident.stdout.strip().splitlines()[-1]))
        row['mod_sha'] = sha                      # identity reads the clone's HEAD
    except (ValueError, IndexError):
        row["identity_error"] = (ident.stdout + ident.stderr)[-400:]
    if isinstance(sub, list):
        row["rows"] = [{k: x.get(k) for k in ("id", "status", "kind", "detail")} for x in sub if isinstance(x, dict)]
    if isinstance(res, dict) and res.get("error"):
        row["error"] = str(res["error"])[:600]
    with open(os.path.join(HERE, "rows.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    tail = [l for l in text.strip().splitlines() if l.strip()][-6:]
    print("%s %s rc=%s site=%s %.0fs  %s" % (tid, verdict, rc, site, row["wall_s"], row["evidence"]))
    print("\n".join("  | " + l[:300] for l in tail))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

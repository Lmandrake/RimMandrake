#!/usr/bin/env python3
"""Bookkeeping for the Claude Whittle loops (loop.sh): status page files, the shared claims table, and the shortlist a
round picks its one ticket from. Owner order 2026-11-11: two live FlowWorks loops (one per game) and offline loops on
Archmagi, one ticket at a time, never two loops on one item.

    wc.py status <WORKER> [--state S] [--item ID|-] [--round N] [--note TEXT] [--lane L --game G --unit U --machine M]
    wc.py log <WORKER> TEXT              one loop.log line, "YYYY-MM-DD HH:MM <text>" in local time (the contract)
    wc.py shortlist <WORKER> <fwlive|offline> [--n 12]
    wc.py claim <WORKER> <ID>            exit 3 when another loop holds it
    wc.py unclaim <WORKER> <ID>
    wc.py mine <WORKER>                  the ids the worker holds in the claims table, one per line
    wc.py lane-open <fwlive|offline>     count of open items the lane could take
    wc.py nonpass <ID>                   trailing run of non-pass results on the item
    wc.py tokens <claude json log>...    total tokens the logs report (input+output+cache), or 0

Files live in /mnt/d/ClaudeWork/rimmandrake/whittle_claude (WC_HOME overrides): <WORKER>/worker.json, loop.log,
claims.json (under claims.lock), workers.json (the roster). On SteveDesktop WC_REMOTE=mandrake@archmagi-wsl: status, log,
claim and unclaim run on Archmagi's copy (REMOTE_WC) over ssh and the shortlist reads Archmagi's claims table, so every
loop on both machines shares one claims table and the WHITTLE_NOW page sees every worker. Every stamp carries a date and an offset: a time-only
stamp is what broke ARTISAN_NOW's dates."""
import argparse
import datetime as dt
import fcntl
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

HOME = Path(os.environ.get("WC_HOME", "/mnt/d/ClaudeWork/rimmandrake/whittle_claude"))
REMOTE = os.environ.get("WC_REMOTE")          # user@host whose HOME holds the shared files
REMOTE_WC = "/mnt/d/ClaudeWork/rimmandrake/whittle_claude/tools/wc.py"
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "LogLevel=ERROR"]
REPO = Path(__file__).resolve().parents[2]
LIVE_NEEDS = ("bridge", "game-up")
NEVER_NEEDS = ("owner",)


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def wdir(worker):
    d = HOME / worker
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_json(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


class Locked:
    def __enter__(self):
        HOME.mkdir(parents=True, exist_ok=True)
        self.fh = open(HOME / "claims.lock", "w")
        fcntl.flock(self.fh, fcntl.LOCK_EX)
        return self

    def __exit__(self, *a):
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()


def status(a):
    p = wdir(a.worker) / "worker.json"
    w = read_json(p, {})
    w.setdefault("worker", a.worker)
    for k in ("unit", "machine", "lane", "game"):
        if getattr(a, k):
            w[k] = getattr(a, k)
    if a.item is not None:
        item = None if a.item in ("", "-") else a.item
        if item != w.get("item"):
            w["item_started_at"] = now() if item else None
        w["item"] = item
    if a.round is not None:
        w["round"] = a.round
    if a.state:
        w["state"] = a.state
    if a.note is not None:
        w["note"] = a.note.splitlines()[0][:300] if a.note else ""
    for k in ("unit", "machine", "lane", "game", "item", "item_started_at", "round", "state", "note"):
        w.setdefault(k, None)
    w["updated_at"] = now()
    write_json(p, w)
    with Locked():
        r = read_json(HOME / "workers.json", {"workers": []})
        names = [x["worker"] for x in r["workers"]]
        if a.worker not in names:
            r["workers"].append({"worker": a.worker, "dir": str(HOME / a.worker), "lane": w["lane"],
                                 "machine": w["machine"], "game": w["game"], "unit": w["unit"]})
        r["updated_at"] = now()
        write_json(HOME / "workers.json", r)


def log(a):
    with open(wdir(a.worker) / "loop.log", "a", encoding="utf-8") as fh:
        fh.write("%s %s\n" % (dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"), " ".join(a.text)))


def world():
    sys.path.insert(0, str(REPO / "src/RimMandrake/rimflow"))
    import cli
    return cli.load()[1]


def lane_patterns():
    d = json.loads((REPO / "infrastructure/state/flowworks_lane.json").read_text(encoding="utf-8"))
    return [re.compile(p) for p in d["id_patterns"]]


def nonpass_of(v):
    n = 0
    for r in reversed(v.runs or []):
        if str(getattr(r, "result", "")).lower() == "pass":
            break
        n += 1
    return n


def shared_claims():
    if not REMOTE:
        return read_json(HOME / "claims.json", {})
    r = subprocess.run(SSH + [REMOTE, "cat %s" % shlex.quote(str(HOME / "claims.json"))], capture_output=True, text=True,
                       timeout=60)
    if r.returncode != 0:
        raise SystemExit("cannot read the shared claims table on %s: %s" % (REMOTE, r.stderr.strip()[:200]))
    try:
        return json.loads(r.stdout or "{}")
    except ValueError:
        return {}


def candidates(worker, lane):
    w, pats = world(), lane_patterns()
    claims = shared_claims()
    out = []
    for v in w.items.values():
        if not v.open or v.needs in NEVER_NEEDS:
            continue
        held = claims.get(v.id)
        if held and held.get("worker") != worker:
            continue
        if v.owner not in ("BENCH", worker):
            continue
        fw = any(p.search(v.id) for p in pats)
        live = v.needs in LIVE_NEEDS
        if lane == "fwlive":
            if not fw:
                continue
            # the blockage: built or validated work that only lacks its live proof comes first, then other live
            # items, then FlowWorks offline work
            rank = (0 if live and v.state in ("built", "validated") else 1 if live else 2)
        else:
            if live:
                continue
            # FlowWorks offline items belong to the live loops first; an offline loop takes them last
            rank = (0 if v.state == "ready" else 1) + (2 if fw else 0)
        if v.blocked:
            rank += 4
        out.append((rank, -(len(v.criteria or [])), v))
    out.sort(key=lambda t: (t[0], len(t[2].runs or []), t[2].id))
    return out


def shortlist(a):
    rows = candidates(a.worker, a.lane)
    for rank, _, v in rows[:a.n]:
        print("%s | state=%s needs=%s owner=%s runs=%d nonpass_tail=%d blocked=%s | %s" % (
            v.id, v.state, v.needs, v.owner, len(v.runs or []), nonpass_of(v), bool(v.blocked),
            (v.title or "")[:140]))
    print("# %d candidates in lane %s for %s at %s" % (len(rows), a.lane, a.worker, now()))


def lane_open(a):
    print(len(candidates("-", a.lane)))


def claim(a):
    with Locked():
        c = read_json(HOME / "claims.json", {})
        held = c.get(a.id)
        if held and held.get("worker") != a.worker:
            print("REFUSED: %s is claimed by %s since %s" % (a.id, held["worker"], held.get("at")))
            return 3
        mine = [k for k, x in c.items() if x.get("worker") == a.worker and k != a.id]
        if mine:
            print("REFUSED: %s already holds %s; one ticket at a time (unclaim it first)" % (a.worker, ", ".join(mine)))
            return 3
        c[a.id] = {"worker": a.worker, "at": now()}
        write_json(HOME / "claims.json", c)
    print("CLAIMED %s for %s" % (a.id, a.worker))
    return 0


def unclaim(a):
    with Locked():
        c = read_json(HOME / "claims.json", {})
        if c.get(a.id, {}).get("worker") == a.worker:
            del c[a.id]
            write_json(HOME / "claims.json", c)
            print("UNCLAIMED %s" % a.id)
        else:
            print("not held by %s: %s" % (a.worker, a.id))
    return 0


def mine(a):
    for k, x in read_json(HOME / "claims.json", {}).items():
        if x.get("worker") == a.worker:
            print(k)


def nonpass(a):
    v = world().items.get(a.id)
    print(nonpass_of(v) if v else "unknown item")


def tokens(a):
    total = 0
    for p in a.logs:
        for line in Path(p).read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                d = json.loads(line)
            except ValueError:
                continue
            u = d.get("usage") if isinstance(d, dict) and d.get("type") == "result" else None
            if u:
                total += sum(int(u.get(k) or 0) for k in ("input_tokens", "output_tokens",
                             "cache_creation_input_tokens", "cache_read_input_tokens"))
    print(total)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("worker")
    for k in ("state", "item", "note", "lane", "game", "unit", "machine"):
        s.add_argument("--" + k)
    s.add_argument("--round", type=int)
    s = sub.add_parser("log")
    s.add_argument("worker")
    s.add_argument("text", nargs="+")
    s = sub.add_parser("shortlist")
    s.add_argument("worker")
    s.add_argument("lane", choices=("fwlive", "offline"))
    s.add_argument("--n", type=int, default=12)
    s = sub.add_parser("lane-open")
    s.add_argument("lane", choices=("fwlive", "offline"))
    for name in ("claim", "unclaim"):
        s = sub.add_parser(name)
        s.add_argument("worker")
        s.add_argument("id")
    s = sub.add_parser("mine")
    s.add_argument("worker")
    s = sub.add_parser("nonpass")
    s.add_argument("id")
    s = sub.add_parser("tokens")
    s.add_argument("logs", nargs="+")
    a = ap.parse_args(argv)
    if REMOTE and a.cmd in ("status", "log", "claim", "unclaim", "mine"):
        args = sys.argv[1:] if argv is None else argv
        r = subprocess.run(SSH + [REMOTE, "python3 %s %s" % (REMOTE_WC, shlex.join(args))], timeout=120)
        return r.returncode
    fn = {"status": status, "log": log, "shortlist": shortlist, "lane-open": lane_open, "claim": claim,
          "unclaim": unclaim, "mine": mine, "nonpass": nonpass, "tokens": tokens}[a.cmd]
    return fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())

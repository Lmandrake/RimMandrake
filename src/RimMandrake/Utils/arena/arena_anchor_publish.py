#!/usr/bin/env python3
"""arena_anchor_publish.py - publish every arena arm's signed event-log head to the git ledger, every few minutes
and again at close-out, so a dead runner or a lost clone cannot leave the trial UNMEASURED
(ARENA_ANCHOR_FIX_PUBLISH_BEFORE_ANALYSIS; the reader side is ARENA_ANALYSIS_WIRE_LEDGER_ANCHORS_TRUST).

    python3 src/RimMandrake/Utils/arena/arena_anchor_publish.py                 one tick (the timer runs this)
    python3 src/RimMandrake/Utils/arena/arena_anchor_publish.py --final         close-out: publish, then exit 3 unless
                                                                                every replay arm is anchored to its tip
    python3 src/RimMandrake/Utils/arena/arena_anchor_publish.py --dry-run       plan only, writes nothing
    python3 src/RimMandrake/Utils/arena/arena_anchor_publish.py --ledger EVENTS.jsonl   throwaway ledger (no git)
    python3 src/RimMandrake/Utils/arena/arena_anchor_publish.py --install [--interval-min 10]   clone + timer

WHY A SEPARATE PUBLISHER. arena_analysis / arena_spend trust an arm only when a SIGNED `ARENA_ANCHOR` ledger note
covers its whole accepted log; before this file nothing published one (`arena_eventlog anchor-note` only PRINTS
the command). It does not live in the runner on purpose: the runner can die or be restarted at any time, and a
publisher inside it dies with it.

WHAT ONE TICK DOES (plan()). For every arm to cover (the [trial] replay_arms of arm.toml, else arena.py's
TRIAL_DEFAULTS, plus every other log in the events dir) it verifies the log with the harness token (read only) and
publishes the arm's head `arm:n:head:lsig` (arena_eventlog.make_anchor) only when ALL hold:
  - no published, local or witness anchor contradicts the log (arena_eventlog.check_anchors: a truncated or
    rewritten log is REFUSED, never re-anchored at its shorter tip);
  - the witness (journald) is readable and its newest anchor for the arm is the log's accepted count (a log
    mid-write, or one whose tail was cut, waits for the next tick);
  - n grew past the newest anchor already in the ledger (IDEMPOTENT: nothing grew, no note, no commit).
The `@roster` token rides along whenever anything is published or the roster grew.

WHERE IT PUBLISHES (the sound route). The note is written by `rimflow note --seat FOUNDRY` and pushed with
./publish from a DEDICATED clone (default /home/mandrake/rm/anchor, sparse: infrastructure/state + rimflow +
Utils), never from a seat clone: there the FOUNDRY shard holds only this publisher's lines, so a path commit of it
sweeps nobody's hunks, and no seat clone's HEAD moves under a live agent. The shards are `merge=union`
(.gitattributes), so the seats' own FOUNDRY lines merge without conflict. Once pushed to origin the note is in a
store no arm can write (arm processes run in arm_sandbox's bwrap, /home is a tmpfs: no clone, no ssh key) and no
dead runner or lost clone can take back. Seat clones see it when they next pull: the close-out either pulls first
or passes `--ledger <anchor clone>/infrastructure/state/ledger/events.jsonl` to arena_analysis / arena_spend.

The analysis side (arena_analysis.verified_logs, used by both CLIs) reports in log_trust.anchor_lag every arm whose
log has records newer than its last ledger anchor, and names this script's --final.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_eventlog as L  # noqa: E402
import arena_tasks as A  # noqa: E402

REPO = HERE.parent.parent.parent.parent
DEFAULT_CLONE = Path("/home/mandrake/rm/anchor")
ORIGIN_URL = "git@github.com:Lmandrake/RimMandrake.git"
DEFAULT_ITEM = "ARENA_ANCHOR_FIX_PUBLISH_BEFORE_ANALYSIS"
SEAT = "FOUNDRY"
SHARD_REL = "infrastructure/state/ledger/events/%s.jsonl" % SEAT
LEDGER_REL = "infrastructure/state/ledger/events.jsonl"
SPARSE = ("infrastructure/state", "src/RimMandrake/rimflow", "src/RimMandrake/Utils")
UNIT = "rm-arena-anchor"
TEMPLATES = REPO / "infrastructure" / "arena" / "systemd"
LOG_DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/foundry_arena/anchor_publish/publisher.log"
WHY = "arena harness anchor: signed event-log heads published so a deleted or forged event is caught at report time"


class PublishError(Exception):
    pass


# ---------------------------------------------------------------- which arms

def replay_arms() -> list[str]:
    """[trial] replay_arms of arm.toml; arena.py's TRIAL_DEFAULTS when arm.toml is unreadable."""
    import arena as AR
    try:
        arms = AR.load_config()["trial"].get("replay_arms")
    except Exception:       # noqa: BLE001  unreadable arm.toml: fall back to the code defaults, never skip arms
        arms = None
    return list(arms or AR.TRIAL_DEFAULTS["replay_arms"])


def arms_to_cover(p: dict, required: list[str] | None = None) -> tuple[list[str], list[str]]:
    """-> (required, cover): required = the replay arms (--final insists on them), cover = required + every other
    arm log in the events dir (a lane arm, critic_calib) so no signed log goes unanchored."""
    req = list(required if required is not None else replay_arms())
    logs = sorted(f.stem for f in Path(p["events"]).glob("*.jsonl") if f.stem != "harness")
    return req, sorted(set(req) | set(logs))


# ---------------------------------------------------------------- plan (pure given its inputs)

def _usable(lst):
    return [a for a in lst or () if not (a.get("error") or L.anchor_error(a))]


def plan(p: dict, token: str, external: dict | None, cover: list[str], wit: dict | None = None,
         local: dict | None = None) -> dict:
    """-> {"arms": {arm: {"n", "published", "witness", "action", "why"}}, "anchors": [anchor to publish],
    "roster": roster anchor or None}. action: publish | current | skip | refused | nolog."""
    ext = L.verify_ledger_anchors(external or {}, token)
    wit = wit if wit is not None else L.witness_read(p, token)
    local = local if local is not None else L.read_anchors(p, token)["by_arm"]
    out, anchors = {}, []
    for arm in cover:
        f = L.arm_file(p, arm)
        pub = _usable(ext.get(arm))
        pub_n = max((a["n"] for a in pub), default=0)
        row = {"published": pub_n}
        if not f.exists():
            out[arm] = dict(row, n=0, action="nolog", why="no event log yet")
            continue
        v = L.verify(p, arm, token)
        acc = v["accepted"]
        wan = _usable(wit.get("anchors", {}).get(arm))
        wn = max((a["n"] for a in wan), default=0)
        row.update(n=len(acc), witness=wn, rejected=len(v["rejected"]), undecodable=v.get("undecodable", 0))
        viol = L.check_anchors(acc, pub + wan + _usable(local.get(arm)))
        if viol:
            out[arm] = dict(row, action="refused", why="; ".join(viol)[:300])
        elif wit.get("status") != "ok":
            out[arm] = dict(row, action="skip", why="witness %s: an unwitnessed head is not published"
                            % wit.get("status"))
        elif wn != len(acc):
            out[arm] = dict(row, action="skip", why="log n=%d but witness n=%d (mid-write, or a cut tail): next tick"
                            % (len(acc), wn))
        elif not acc:
            out[arm] = dict(row, action="skip", why="no accepted (signed) record to anchor")
        elif len(acc) == pub_n:
            out[arm] = dict(row, action="current", why="ledger already anchors n=%d" % pub_n)
        else:
            anchors.append(L.make_anchor(arm, acc, token))
            out[arm] = dict(row, action="publish", why="n %d -> %d" % (pub_n, len(acc)))
    ra = L.roster_anchor(p, token)
    pub_r = max((a["n"] for a in _usable(ext.get("@roster"))), default=-1)
    roster = ra if (anchors or ra["n"] > pub_r) and ra["n"] > 0 else None
    return {"arms": out, "anchors": anchors, "roster": roster}


def note_text(pl: dict) -> str | None:
    heads = list(pl["anchors"]) + ([pl["roster"]] if pl.get("roster") else [])
    return L.anchor_note_text(heads) if heads else None


def final_problems(pl: dict, required: list[str]) -> list[str]:
    """Close-out check after publishing: every required arm with a log is anchored to its tip in the ledger."""
    bad = []
    for arm in required:
        r = pl["arms"].get(arm)
        if r is None:
            bad.append("%s: not covered by the publisher" % arm)
        elif r["action"] == "nolog":
            bad.append("%s: no event log (UNMEASURED)" % arm)
        elif r["action"] != "current":
            bad.append("%s: %s (%s)" % (arm, r["action"], r["why"]))
    return bad


# ---------------------------------------------------------------- routes

def _run(argv, cwd=None, env=None, timeout=240):
    r = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def read_external(ledger: Path):
    import arena_analysis as AA
    return AA.ledger_external(str(ledger))


def note_throwaway(ledger: Path, text: str, item: str) -> dict:
    """--ledger: rimflow note into a throwaway ledger (RIMFLOW_LEDGER/RIMFLOW_ITEMS), no git."""
    env = dict(os.environ, RIMFLOW_LEDGER=str(ledger), RIMFLOW_ITEMS=str(Path(ledger).parent / "items"))
    rc, out = _run([sys.executable, str(REPO / "src/RimMandrake/rimflow/cli.py"), "note", item, "--seat", SEAT,
                    "--why", WHY, "--text", text], cwd=str(REPO), env=env)
    if rc:
        raise PublishError("rimflow note (throwaway) exit %d: %s" % (rc, out.strip()[-300:]))
    return {"route": "throwaway ledger", "ledger": str(ledger)}


def _git(clone, *args, check=True, timeout=240):
    rc, out = _run(["git", "-C", str(clone), *args], timeout=timeout)
    if check and rc:
        raise PublishError("git %s: %s" % (" ".join(args[:3]), out.strip()[-300:]))
    return rc, out


def _clone_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith(("RIMFLOW_", "GIT_"))}
    return env


def _publish(clone: Path, msg: str) -> str:
    rc, out = _run([sys.executable, str(clone / "src/RimMandrake/Utils/publish.py"), "-m", msg, SHARD_REL],
                   cwd=str(clone), env=_clone_env(), timeout=300)
    m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", out)
    if rc or not m:
        raise PublishError("./publish exit %d: %s" % (rc, out.strip()[-400:]))
    return m.group(1)


def sync_clone(clone: Path) -> dict:
    """Land anything a previous tick left (an uncommitted note, an unpushed commit), then fast-forward to
    origin/main, so the plan reads every anchor already published."""
    if not (clone / ".git").exists():
        raise PublishError("no anchor clone at %s: run --install" % clone)
    left = {}
    _, st = _git(clone, "status", "--porcelain", "--", SHARD_REL)
    _git(clone, "fetch", "-q", "origin")
    _, ahead = _git(clone, "rev-list", "--count", "origin/main..HEAD")
    if st.strip() or int(ahead.strip() or 0):
        left["relanded"] = _publish(clone, "ledger: ARENA_ANCHOR note (re-land of an earlier tick)")
    _git(clone, "merge", "--ff-only", "-q", "origin/main")
    return left


def note_clone(clone: Path, text: str, item: str) -> dict:
    rc, out = _run([sys.executable, str(clone / "src/RimMandrake/rimflow/cli.py"), "note", item, "--seat", SEAT,
                    "--why", WHY, "--text", text], cwd=str(clone), env=_clone_env())
    if rc:
        raise PublishError("rimflow note (anchor clone) exit %d: %s" % (rc, out.strip()[-300:]))
    sha = _publish(clone, "ledger: ARENA_ANCHOR note (%s)" % ", ".join(
        t.split(":", 2)[0] + ":" + t.split(":", 2)[1] for t in text.split()[1:]))
    return {"route": "anchor clone", "clone": str(clone), "published": sha}


# ---------------------------------------------------------------- one tick

def tick(p: dict, *, ledger: Path | None, clone: Path, item: str, dry: bool, required=None) -> dict:
    token = L._read_token(p)              # read only; never rotated, copied or written
    res = {"ts": L.now_ts()}
    if ledger is None:
        if not dry:
            res.update(sync_clone(clone))
        led = clone / LEDGER_REL
    else:
        led = Path(ledger)
    ext, trust = read_external(led)
    res["ledger"] = dict(trust, path=str(led))
    if ext is None:
        raise PublishError("ledger %s unreadable (%s): refusing to publish blind" % (led, trust.get("status")))
    req, cover = arms_to_cover(p, required)
    pl = plan(p, token, ext, cover)
    res.update(required=req, arms=pl["arms"])
    text = note_text(pl)
    if not text:
        res["note"] = None
    elif dry:
        res["note"] = "DRY-RUN: " + text
    else:
        res["note"] = (note_throwaway(led, text, item) if ledger is not None else note_clone(clone, text, item))
        res["note"]["anchors"] = ["%s:%d" % (a["arm"], a["n"]) for a in pl["anchors"]]
        ext2, _ = read_external(led)
        pl = plan(p, token, ext2, cover)
        res["arms_after"] = pl["arms"]
    res["final_problems"] = final_problems(pl, req)
    return res


def _lock(p: dict, wait_s: float):
    lp = L.token_path(p).parent / "anchor_publish.lock"
    fh = open(lp, "a+")
    end = time.time() + wait_s
    while True:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fh
        except OSError:
            if time.time() >= end:
                fh.close()
                return None
            time.sleep(2)


# ---------------------------------------------------------------- install (clone + units)

def render(name: str, **kw) -> str:
    text = (TEMPLATES / (name + ".tmpl")).read_text(encoding="utf-8")
    for k, v in kw.items():
        text = text.replace("@%s@" % k, str(v))
    left = re.findall(r"@[A-Z_]+@", text)
    if left:
        raise PublishError("%s: unfilled placeholder(s) %s" % (name, left))
    return text


def units(clone: Path, interval_min: int, log: str) -> dict:
    # The service runs the ANCHOR CLONE's copy (pinned to origin/main, fast-forwarded each tick), never a seat
    # clone's working tree, so an uncommitted edit in a seat cannot change what the timer runs.
    import arena as AR
    script = clone / HERE.relative_to(REPO) / "arena_anchor_publish.py"
    return {UNIT + ".service": render(UNIT + ".service", WORKDIR=clone, SCRIPT=script,
                                      CLONE=clone, LOG=log, ARM_TOML=AR.arm_toml_path()),
            UNIT + ".timer": render(UNIT + ".timer", INTERVAL_MIN=interval_min)}


def make_clone(clone: Path) -> list[str]:
    """A hardlinked local clone of this repo, origin = GitHub, sparse, on main at origin/main. Never on /mnt."""
    if (clone / ".git").exists():
        return ["clone exists: %s" % clone]
    if os.path.realpath(str(clone.parent)).startswith("/mnt/"):
        raise PublishError("anchor clone must be on ext4, not %s" % clone)
    steps = []
    for args in (["clone", "-q", "--no-checkout", str(REPO), str(clone)],):
        rc, out = _run(["git", *args], timeout=540)
        if rc:
            raise PublishError("git clone: %s" % out[-300:])
        steps.append("git " + " ".join(args))
    for args in (["remote", "set-url", "origin", ORIGIN_URL], ["fetch", "-q", "origin"],
                 ["sparse-checkout", "set", "--cone", *SPARSE], ["checkout", "-q", "-B", "main", "origin/main"],
                 ["branch", "-q", "--set-upstream-to=origin/main", "main"]):
        _git(clone, *args, timeout=540)
        steps.append("git " + " ".join(args))
    return steps


def install(clone: Path, interval_min: int, log: str, dry: bool) -> dict:
    u = units(clone, interval_min, log)
    d = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "systemd" / "user"
    res = {"units": {k: str(d / k) for k in u}, "clone": str(clone)}
    if dry:
        return dict(res, dry_run=True, text=u)
    res["clone_steps"] = make_clone(clone)
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    d.mkdir(parents=True, exist_ok=True)
    for k, v in u.items():
        (d / k).write_text(v, encoding="utf-8")
    for args in (["daemon-reload"], ["enable", "--now", UNIT + ".timer"]):
        rc, out = _run(["systemctl", "--user", *args], timeout=60)
        if rc:
            raise PublishError("systemctl --user %s: %s" % (" ".join(args), out.strip()[-200:]))
    return res


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--final", action="store_true", help="close-out: wait for the lock, publish, exit 3 unless every "
                    "replay arm is anchored to its tip")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ledger", help="throwaway rimflow events.jsonl (no git; its items/ beside it)")
    ap.add_argument("--clone", default=str(DEFAULT_CLONE), help="dedicated anchor clone (default %(default)s)")
    ap.add_argument("--item", default=DEFAULT_ITEM)
    ap.add_argument("--arms", help="comma list overriding the required replay arms (tests)")
    ap.add_argument("--install", action="store_true", help="make the anchor clone, install + start the timer")
    ap.add_argument("--interval-min", type=int, default=10)
    ap.add_argument("--log", default=LOG_DEFAULT)
    a = ap.parse_args(argv)
    if a.install:
        try:
            print(json.dumps(install(Path(a.clone), a.interval_min, a.log, a.dry_run), indent=1, default=str))
            return 0
        except PublishError as e:
            print("arena_anchor_publish: INSTALL REFUSED: %s" % e, file=sys.stderr)
            return 2
    p = A.paths()
    fh = _lock(p, 300 if a.final else 0)
    if fh is None:
        print(json.dumps({"ts": L.now_ts(), "skipped": "another publisher holds the lock"}))
        return 3 if a.final else 0
    try:
        res = tick(p, ledger=Path(a.ledger) if a.ledger else None, clone=Path(a.clone), item=a.item,
                   dry=a.dry_run, required=a.arms.split(",") if a.arms else None)
    except (PublishError, L.Rejected, OSError, subprocess.SubprocessError) as e:
        print(json.dumps({"ts": L.now_ts(), "ERROR": "%s: %s" % (type(e).__name__, e)}))
        return 2
    finally:
        fh.close()
    if a.final:
        res["close_out"] = ("analyse with --ledger %s (or pull this clone first)" % res["ledger"]["path"])
    print(json.dumps(res, sort_keys=True, default=str))
    return 3 if (a.final and res["final_problems"]) else 0


if __name__ == "__main__":
    sys.exit(main())

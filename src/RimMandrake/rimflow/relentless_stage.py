#!/usr/bin/env python3
"""Relentless's game staging as a Python function, not an LLM session (STAGING_REWIRE_PYTHON_NOT_AN_LLM; owner
2026-11-06: "Python script to setup the game, done... file and expedite."). Every step stage_prompt() asked an LLM to do
was already a script; the LLM's own turns were the 9-20 minute holds (design/RimMandrake/fast_testing_2026-11-05/
scored.md, "Deterministic staging daemon").

The supervisor (relentless_game, phase "stage") writes a plan beside the run's output and launches this file as the
staging unit's body, in the same unit shape as a worker, so alive/stop/settle and the bridge hold are unchanged:

    deploy plan (stop on a hand-edited game copy: another seat's file) -> game down -> apply (the stale DLL copy rides
    the shutdown window, and the JawaBench companion when the plan owes it: bridgetools/build.py --gm --apply) -> modlist_swap.py (restore FULL.LATEST for a final; --enable <mods>, its About.xml dependency
    closure) -> a live-toggle side's list check -> launch through Steam -> wait for `Bridge token:` bounded by
    load_policy -> the proofs' live-menu commands, at the main menu before any game -> lane-fix producers ->
    `relentless.py game-ready` (or `snag --class game_stage` on a known stop)

An unhandled exception, and only that, execs the old LLM staging worker (the plan's `fallback` argv, the stage prompt).

    relentless_stage.py run --plan <run>.stage.json
    relentless_stage.py holds [--journal <store>/journal.jsonl] [--since ISO] [--json]   staging hold census
"""
import argparse
import calendar
import json
import os
import re
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
DEPLOY = os.path.join(UTILS, "deploy_custom_mods.py")
SWAP = os.path.join(UTILS, "modlist_swap.py")
GAME_EXE = "RimWorldWin64.exe"
STOP_GRACE_S = 90           # live_session.stop_game's graceful wait, then /F
LAUNCH_SETTLE_S = 20        # live_session.launch_and_wait: Steam's own hand-off before the log is read
MARGIN_S = 120              # left of stage_max_s for game-ready and the remedies' own bound
REMEDY_MAX_S = 480
MENU_MAX_S = 300            # one live-menu command (STAGING_MENU_FIX_ALWAYS_PARKS_ON_MAPS), inside REMEDY_TOTAL_S
REMEDY_TOTAL_S = 420        # all producers together, inside the supervisor's stage_idle_s (600) after the game is UP
START_GRACE_S = 180         # a cold Steam (closed, updating) may not have the game process yet: no "died" before this
# a deploy plan's `-` line that is not a repo delete: a file present only in the game copy, hand-edited there, maybe by
# another seat; --apply never deletes it without --prune, but its owner's work is in that folder (rimworld-deploy §3)
HAND_EDIT = re.compile(r"^\s+-\s+(\S.*?)\s+\(in game, not in repo; kept")
REFUSAL = re.compile(r"REFUSING|DEF GUARD")
PLAN_END = re.compile(r"^(Drift found|Everything in sync|Gate:|Nothing to do|Deployed \d+ file|NOTHING WAS WRITTEN)", re.M)


class Stop(Exception):
    """A known reason the staging cannot finish: told as a game_stage snag, never handed to an LLM."""


# ---------------------------------------------------------------- the world it acts on (faked in the selftest)

class Ops(object):
    def __init__(self, plan):
        self.plan = plan
        self.cwd = plan.get("clone") or REPO

    def now(self):
        return time.time()

    def sleep(self, s):
        time.sleep(s)

    def sh(self, argv, timeout=480):
        try:
            p = subprocess.run(argv, cwd=self.cwd, capture_output=True, text=True, timeout=timeout,
                               encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return 124, "timed out after %d s: %s" % (timeout, " ".join(argv)[:200])
        return p.returncode, (p.stdout or "") + (p.stderr or "")

    def running(self):
        rc, out = self.sh(["tasklist.exe", "/FI", "IMAGENAME eq %s" % GAME_EXE], timeout=60)
        if rc != 0:
            raise RuntimeError("tasklist.exe exit %d: %s" % (rc, out[-200:]))     # blind: unhandled, never "down"
        return GAME_EXE.lower() in out.lower()

    def kill(self, force=False):
        return self.sh(["taskkill.exe"] + (["/F"] if force else []) + ["/IM", GAME_EXE], timeout=60)

    def stamp(self, state):
        return self.sh(["./game", "--idle-ok", "--why", "relentless staging %s (python stager)" % self.plan["item"],
                        state], timeout=120)

    def cursor(self):
        if UTILS not in sys.path:
            sys.path.insert(0, UTILS)
        import logwait
        from game_paths import PLAYER_LOG
        return logwait.LogCursor(PLAYER_LOG)

    def launch(self):
        # through Steam, never the bare .exe (rimworld-load-round §10: the bare exe corrupts assembly loading)
        return self.sh(["powershell.exe", "-NoProfile", "-Command", "Start-Process 'steam://rungameid/294100'"], timeout=60)

    def load_bound(self):
        if UTILS not in sys.path:
            sys.path.insert(0, UTILS)
        import load_policy
        return int(load_policy.profile_for(load_policy.active_count_from_modsconfig())["process_to_bridge_deadline_s"])

    def live_mods(self):
        """The active mod ids of the live ModsConfig.xml (the next load), lower-cased, or None when unreadable."""
        if UTILS not in sys.path:
            sys.path.insert(0, UTILS)
        import modlist_swap
        got = modlist_swap.mods(modlist_swap.LIVE)
        return None if got is None else [m.lower() for m in got]

    def companion_covers(self, shas):
        """None when build.py here would deploy a companion holding every built sha in `shas`, else why not: the
        working tree's companion sources must be HEAD's (a clean build: its stamp names HEAD honestly), HEAD must be
        on origin/main (the gate reads the stamp in the books clone) and hold each sha (companion_identity cover)."""
        d = os.path.join(self.cwd, "src", "RimMandrake", "bridgetools")
        if d not in sys.path:
            sys.path.insert(0, d)
        import companion_identity as CI
        head = subprocess.run(["git", "-C", self.cwd, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=60)
        head = head.stdout.strip() if head.returncode == 0 else None
        if not head:
            return "cannot read this clone's HEAD"
        wt, at = CI.srchash_worktree(self.cwd), CI.srchash_at(self.cwd, head)
        if not wt or wt != at:
            return ("this clone's companion sources (hash %s) are not its HEAD %s's (%s): uncommitted companion work"
                    % ((wt or "unreadable")[:12], head[:12], (at or "unreadable")[:12]))
        self.sh(["git", "-C", self.cwd, "fetch", "-q", "origin", "main"], timeout=120)  # a lead alone never ./syncs
        if not CI.descends(self.cwd, head, "origin/main"):
            return "HEAD %s is not on origin/main: the DLL's stamp would name a commit the gate cannot read" % head[:12]
        lacks = [s for s in shas if not CI.descends(self.cwd, s, head)]
        if lacks:
            return "HEAD %s does not hold build %s" % (head[:12], ", ".join(s[:12] for s in lacks))
        return None

    def companion_build(self):
        """build.py --gm --apply from this clone: builds, verifies and writes BridgeTools/JawaBench (the game is down)."""
        return self.sh([sys.executable, os.path.join(self.cwd, "src", "RimMandrake", "bridgetools", "build.py"), "--gm",
                        "--apply"], timeout=480)

    def report(self, verb, text, klass=None):
        argv = [sys.executable, os.path.join(self.cwd, "src", "RimMandrake", "rimflow", "relentless.py"), verb,
                "--item", self.plan["item"], "--gen", str(self.plan["gen"])]
        argv += (["--class", klass] if klass else []) + [text[:1800]]
        return self.sh(argv, timeout=120)


# ---------------------------------------------------------------- the steps

def plan_hazards(out):
    """A deploy plan's output -> why --apply must not run, or None. A plan cut short (no closing line) is a hazard too:
    the walk can stop mid-list and read as clean (rimworld-deploy §2)."""
    hand = [m.group(1) for m in map(HAND_EDIT.match, out.splitlines()) if m]
    if hand:
        return "the game copy holds %d file(s) not in the repo (another seat's or a hand edit; --pull rescues): %s" % (
            len(hand), ", ".join(hand[:6]))
    bad = [ln.strip() for ln in out.splitlines() if REFUSAL.search(ln)]
    if bad:
        return "the deploy plan refuses: %s" % " | ".join(bad[:3])[:400]
    if not PLAN_END.search(out):
        return "the deploy plan did not finish (no closing line): %s" % out.strip()[-300:]
    return None


def _ok(rc, out, what):
    if rc != 0:
        raise Stop("%s exit %d: %s" % (what, rc, out.strip()[-400:]))
    return out


def game_down(ops, log):
    if not ops.running():
        log.append("game was down")
        return
    ops.stamp("going-down")
    ops.kill()
    t0 = ops.now()
    while ops.running() and ops.now() - t0 < STOP_GRACE_S:
        ops.sleep(2)
    if ops.running():
        ops.kill(force=True)
        t1 = ops.now()
        while ops.running() and ops.now() - t1 < 30:
            ops.sleep(2)
        if ops.running():
            raise Stop("the game would not exit (taskkill, then /F, %d s)" % (STOP_GRACE_S + 30))
        log.append("game stopped (forced after %d s)" % STOP_GRACE_S)
    else:
        log.append("game stopped")
    ops.sleep(5)            # the exit's own writes (Player.log, ModsConfig) settle before the list is written
    ops.stamp("down")


def run(plan, ops):
    """-> ("ready"|"snag", text). Raises only on what no step handles (the caller's LLM fallback)."""
    t0, log = ops.now(), []
    deadline = t0 + int(plan.get("max_s") or 3600) - MARGIN_S
    groups = [g for g in plan.get("deploy") or [] if g]
    try:
        if plan.get("riders"):      # each rider's build must be in this tree (stage_prompt's ./sync)
            _ok(*ops.sh(["./sync"], timeout=300), what="./sync for the riders' builds")
        for args in groups:         # 1. the plan, read before anything is written
            rc, out = ops.sh([sys.executable, DEPLOY] + args.split(), timeout=480)
            why = plan_hazards(out)
            if why:
                raise Stop("deploy %s: %s" % (args, why))
            if rc not in (0, 1):
                raise Stop("deploy plan %s exit %d: %s" % (args, rc, out.strip()[-300:]))
        want = plan.get("companion")   # the built shas whose companion BridgeTools/JawaBench lacks, or None
        if isinstance(want, str):   # a plan written before COMPANION_DEPLOY_LIVE_ROUND_FORGETS: a source hash, no sha
            raise Stop("the plan's companion is a source hash (%s), not the built shas: a plan from older code; "
                       "restage" % want[:12])
        if want:                    # LIVEROUND_COMPANION_DEPLOY_OLD_DLL_BLAMED: checked before anything is written
            why = ops.companion_covers(want)    # after ./sync: one build must hold every rider's (..._ROUND_FORGETS)
            if why:
                raise Stop("build.py here would not deploy a companion holding %s: %s"
                           % (", ".join(w[:12] for w in want), why))
        game_down(ops, log)         # 2. down: a DLL cannot be written while the game runs
        for args in groups:         # 3. apply in the shutdown window: the stale DLLs go with the rest
            _ok(*ops.sh([sys.executable, DEPLOY] + args.split() + ["--apply"], timeout=480), what="deploy --apply " + args)
        if want:                    # the companion too: no mod deploy writes BridgeTools/JawaBench
            _ok(*ops.companion_build(), what="bridgetools/build.py --gm --apply")
        log.append("deployed %s%s" % ("; ".join(groups) or "nothing",
                                      "; companion JawaBench holding %s" % ", ".join(w[:12] for w in want)
                                      if want else ""))
        if plan.get("full"):        # 4. the list: the owner's whole one for a final, then the mods on top
            _ok(*ops.sh([sys.executable, SWAP, "--restore", "--apply"], timeout=180), what="modlist_swap --restore")
        else:                       # the smallest list that proves it: the minimal one (all five DLC), the mods on top
            _ok(*ops.sh([sys.executable, SWAP, "--minimal", "--apply"], timeout=180), what="modlist_swap --minimal")
        if plan.get("enable"):
            _ok(*ops.sh([sys.executable, SWAP, "--enable"] + list(plan["enable"]) + ["--apply"], timeout=180),
                what="modlist_swap --enable")
        log.append("list: %s%s" % ("FULL.LATEST" if plan.get("full") else "MINIMAL",
                                   " + %s and their dependencies" % ", ".join(plan["enable"]) if plan.get("enable") else ""))
        tog = plan.get("toggle")
        if tog or plan.get("without"):   # a with/without pair: the list this load reads must be the side it claims
            have = ops.live_mods()
            if have is None:
                raise Stop("the live ModsConfig.xml is unreadable, so the %s side of %s cannot be checked"
                           % ((tog or {}).get("side", "without"), (tog or {}).get("mod", plan.get("without"))))
            # ModsConfig holds packageIds: a folder name (no dot) is not checkable here, and says so in the log
            held = [m for m in plan.get("without") or [] if "." in m and m.lower() in have]
            if held:
                raise Stop("the list holds %s, which this staging must load without (live-toggle side without)"
                           % ", ".join(held))
            if tog and tog.get("side") == "with" and "." in tog["mod"] and tog["mod"].lower() not in have:
                raise Stop("the list lacks %s after --enable: the with side of its live-toggle cannot load" % tog["mod"])
            log.append("toggle: %s %s" % (tog["side"], tog["mod"]) if tog else "without %s" % ", ".join(plan["without"]))
        ops.stamp("loading")        # 5. up, through Steam, waited on the bridge token written after the launch
        cur = ops.cursor()
        _ok(*ops.launch(), what="Steam launch")
        ops.sleep(LAUNCH_SETTLE_S)
        budget = max(60, min(ops.load_bound(), int(deadline - ops.now())) - LAUNCH_SETTLE_S)
        gone, seen, t_launch = [], [], ops.now()

        def abort():
            try:
                if ops.running():
                    seen.append(1)
                    return None
            except RuntimeError:    # one blind tasklist mid-load is no death: the token or the bound decides
                return None
            if not seen and ops.now() - t_launch < START_GRACE_S:
                return None         # not started yet is not dead
            gone.append(1)
            return "game process gone"
        got = cur.wait("Bridge token:", budget, abort=abort)
        took = int(ops.now() - t0)
        if not got.get("ok"):
            if gone:
                raise Stop("the game died during the load (%s); %s" % (got.get("why"), "; ".join(log)))
            # still loading at the bound this run can spend: the supervisor waits the load out itself (_load_gate)
            if plan.get("menu_cmds"):   # its proofs would read a launch the main-menu step never sampled
                raise Stop("still loading after %d s, so the main-menu step never ran (%s)"
                           % (took, " ; ".join(c[:80] for c in plan["menu_cmds"])))
            return "ready", "STILL LOADING after %d s (no Bridge token yet: %s); %s" % (took, got.get("why"), "; ".join(log))
        ops.stamp("up")
        log.append("bridge up %d s after the staging began" % took)
        t_rem = ops.now()       # menu step and producers share one budget inside the supervisor's stage_idle_s
        for cmd in (plan.get("menu_cmds") or []):       # 6a. at the main menu, before anything starts a game
            left = int(REMEDY_TOTAL_S - (ops.now() - t_rem))
            if left < 30:
                log.append("menu `%s` NOT RUN: the %d s budget after the load is spent" % (cmd[:120], REMEDY_TOTAL_S))
                continue
            rc, out = ops.sh(["bash", "-c", cmd], timeout=min(MENU_MAX_S, left))
            log.append("menu `%s` exit %d: %s" % (cmd[:120], rc, " / ".join(out.strip().splitlines()[-3:])[:300]))
        for cmd in (plan.get("remedy_cmds") or []):     # 6. the lane fix's producers, once, with the game up
            left = int(REMEDY_TOTAL_S - (ops.now() - t_rem))
            if left < 30:
                log.append("remedy `%s` NOT RUN: the producers' %d s budget is spent" % (cmd[:120], REMEDY_TOTAL_S))
                continue
            rc, out = ops.sh(["bash", "-c", cmd], timeout=min(REMEDY_MAX_S, left))
            log.append("remedy `%s` exit %d: %s" % (cmd[:120], rc, " / ".join(out.strip().splitlines()[-3:])[:300]))
        return "ready", "python stager: " + "; ".join(log)
    except Stop as e:
        return "snag", "python stager stopped: %s (done so far: %s)" % (e, "; ".join(log) or "nothing")


def main_run(path, ops=None, execv=os.execvp):
    with open(path, encoding="utf-8") as f:
        plan = json.load(f)
    ops = ops or Ops(plan)
    try:
        verdict, text = run(plan, ops)
    except Exception:           # noqa: BLE001  the one road to an LLM: what no step handles
        tb = traceback.format_exc()
        print("relentless_stage: unhandled, handing to the LLM stager:\n%s" % tb, file=sys.stderr, flush=True)
        fb = plan.get("fallback")
        try:
            if fb:
                execv(fb[0], fb)
            why = "no LLM fallback in the plan"
        except OSError as e:
            why = "the LLM fallback would not start: %s" % e
        ops.report("snag", "python stager crashed and %s: %s" % (why, tb.strip().splitlines()[-1][:600]), "game_stage")
        return 1
    rc, out = ops.report("game-ready" if verdict == "ready" else "snag", text,
                         None if verdict == "ready" else "game_stage")
    print("relentless_stage: %s: %s\n%s" % (verdict, text, out.strip()[-300:]), flush=True)
    return 0 if rc == 0 else 3


# ---------------------------------------------------------------- the measure: how long a staging holds the bridge

def _epoch(at):
    try:
        return calendar.timegm(time.strptime(str(at)[:19], "%Y-%m-%dT%H:%M:%S"))
    except (ValueError, TypeError):
        return None


def holds(lines, since=None):
    """Journal tick lines -> [{"item", "start", "end", "s"}]: each `game_stage` act paired with the item's next
    `game_staged`. A staging with no end yet is not a row (it is still holding)."""
    open_, out = {}, []
    for ln in lines:
        try:
            d = json.loads(ln)
        except ValueError:
            continue
        if not isinstance(d, dict) or d.get("do") != "tick":
            continue
        at = _epoch(d.get("at"))
        if at is None or (since is not None and at < since):
            continue
        for a in d.get("acts") or []:
            if not isinstance(a, dict):
                continue
            if a.get("do") == "game_stage":
                open_[a.get("item")] = at
            elif a.get("do") == "game_staged" and a.get("item") in open_:
                s0 = open_.pop(a["item"])
                out.append({"item": a["item"], "start": s0, "end": at, "s": at - s0})
    return out


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def holds_report(rows, since=None):
    s = [r["s"] for r in rows]
    if not s:
        return "staging holds: 0 complete stagings in the window%s (UNMEASURED, not zero)" % (
            " since " + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since)) if since else "")
    return "staging holds: n=%d median=%.0fs (%.1f min) min=%ds max=%ds" % (len(s), median(s), median(s) / 60.0,
                                                                           min(s), max(s))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run", help="the staging unit's body")
    p.add_argument("--plan", required=True)
    p = sub.add_parser("holds", help="median staging hold over the store journal")
    p.add_argument("--journal", default=os.path.join(os.environ.get("RELENTLESS_ROOT")       # relentless.Store: <root>/store
                                                     or os.path.expanduser("~/rm/relentless"), "store", "journal.jsonl"))
    p.add_argument("--since", help="ISO time, e.g. the landing of the python stager")
    p.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return main_run(a.plan)
    since = _epoch(a.since) if a.since else None
    with open(a.journal, encoding="utf-8", errors="replace") as f:
        rows = holds(f, since)
    print(json.dumps(rows) if a.json else holds_report(rows, since))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""detached_helper.py — long helper work that runs OUTSIDE the window (CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).

An in-process helper (the Agent tool) dies with its window, so a window past its context limit cannot restart while
one runs. A detached run lives in its own transient systemd unit and survives the window's restart:

  python3 src/RimMandrake/rimflow/detached_helper.py launch --seat BENCH --item ITEM_ID --brief-file F \
      [--model opus|sonnet] [--max-s 3600] [--budget-usd 15]
  python3 src/RimMandrake/rimflow/detached_helper.py status [--all]
  python3 src/RimMandrake/rimflow/detached_helper.py finish --unit U     (the unit's ExecStopPost; never by hand)

launch: the item must be on the ledger. It takes a pool clone <pool>/clones/<ITEM>.det through scratch_clone.py
(reused, synced, when it exists), then starts role_launch's path: systemd-run --user + claude_bounded.sh -p, the
model passed, wall time bounded twice (the unit's RuntimeMaxSec and claude_bounded's scope), spend bounded by
claude --max-budget-usd. The brief gets a footer: work in the clone, land with ./publish, put state, evidence and one
imperative NEXT on the item as a rimflow note and publish the shard.
finish: runs when the unit stops for any reason (done, failed, killed at its bound). It writes the outcome as a note
on the item, publishes the seat's shard from the clone, and appends one line to the Conductor log. Once per run.
Records: <RM_DISPATCHER_STATE>/detached/<unit>.json. Use it for anything expected to run over ~20 min; the Agent
tool stays for short work (CONDUCTOR.md "Checkpoint, so a drain never freezes him").
"""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import run_tmp  # noqa: E402  (its own TMPDIR: TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP)

DEFAULT_MAX_S = 3600
CAP_MAX_S = 4 * 3600
GRACE_S = 120          # finish + publish time on top of the run's own bound
DEFAULT_BUDGET_USD = 15.0
MODELS = ("opus", "sonnet", "haiku")
SEATS = ("BENCH", "FOUNDRY", "STEVE", "RUNNER")
REAL_LOG = "/mnt/d/ClaudeWork/rimmandrake/conductor/log.md"

FOOTER = """

---
You are a DETACHED helper: you run in your own systemd unit, outside any window, in the clone {clone} (your cwd).
Ledger item: {item}. Seat: {seat}. Wall-time bound: {max_s} s; spend bound ${budget}.
- Work only in that clone. Land code with `./publish -m "subject" <explicit paths>` (never git add -A, never --force).
- Before you stop, and at least every 20 minutes: write your state, evidence paths and one imperative NEXT as
  `python3 src/RimMandrake/rimflow/cli.py note {item} --text "..." --seat {seat} --why "detached run"`, then publish the
  shard: `./publish -m "ledger: {item} note" infrastructure/state/ledger/events/{seat}.jsonl`.
- Nobody reads your stdout until you end; the note is what the Conductor sees. End with a 5-line summary.
"""


def state_dir():
    import doorbell
    return doorbell.state_dir()


def runs_dir(root=None):
    d = os.path.join(root or state_dir(), "detached")
    os.makedirs(d, exist_ok=True)
    return d


def record_path(unit, root=None):
    return os.path.join(runs_dir(root), unit + ".json")


def read_record(unit, root=None):
    try:
        with open(record_path(unit, root), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write_record(rec, root=None):
    p = record_path(rec["unit"], root)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.replace(tmp, p)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def unit_name(seat, item, now):
    slug = re.sub(r"[^a-z0-9]+", "-", item.lower()).strip("-")[:40].strip("-")
    return "rm-detached-%s-%s-%d" % (seat.lower(), slug, int(now))


def pool_root():
    return os.environ.get("RM_DETACHED_POOL") or os.path.expanduser("~/rm/relentless")


def take_clone(item, runner=subprocess.run):
    """-> (clone path, log line). A pool clone named <ITEM>.det: made by scratch_clone.py, or reused and synced."""
    name = item + ".det"
    dest = os.path.join(pool_root(), "clones", name)
    if os.path.isdir(os.path.join(dest, ".git")):
        r = runner(["./sync"], cwd=dest, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        return dest, "reused %s (sync exit %d: %s)" % (dest, r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-160:])
    env = dict(os.environ, RM_SCRATCH_ROOT=pool_root(), RM_SEAT="clones")
    r = runner(["python3", os.path.join(REPO, "src", "RimMandrake", "Utils", "scratch_clone.py"), "clone",
                "detached run for " + item, "--name", name, "--checkout", "--fetch"],
               env=env, capture_output=True, text=True, timeout=540, stdin=subprocess.DEVNULL)
    if r.returncode or not os.path.isdir(os.path.join(dest, ".git")):
        raise RuntimeError("scratch_clone failed (exit %d): %s" % (r.returncode, ((r.stdout or "") + (r.stderr or ""))[-300:]))
    return dest, "made " + dest


def claude_bin():
    import shutil
    return os.environ.get("RM_DISPATCHER_CLAUDE") or shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")


def launch_argv(rec, msg, claude):
    """role_launch.launch_argv's shape, plus ExecStopPost=finish so the outcome is recorded even on a kill."""
    clone, unit, seat = rec["clone"], rec["unit"], rec["seat"]
    bounded = os.path.join(clone, "src", "RimMandrake", "Utils", "claude_bounded.sh")
    bound = int(rec["max_s"]) + GRACE_S
    path = os.path.dirname(claude) + ":" + os.environ.get("PATH", "/usr/bin:/bin")
    finish = "/usr/bin/python3 %s finish --unit %s" % (shlex.quote(os.path.abspath(__file__)), unit)
    wrapup = "-+/usr/bin/python3 %s unit --unit %s --seat %s --clone %s" % (
        shlex.quote(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wrapup.py")), shlex.quote(unit),
        shlex.quote(seat), shlex.quote(clone))
    cmd = [bounded, "-p", msg, "--model", rec["model"], "--name", "DETACHED %s %s" % (seat, rec["item"]),
           "--max-budget-usd", "%g" % rec["budget_usd"], "--output-format", "json", "--dangerously-skip-permissions"]
    return ["systemd-run", "--user", "--quiet", "--collect", "--unit", unit,
            "-p", "StandardOutput=file:" + rec["out"], "-p", "StandardError=file:" + rec["err"],
            "-p", "ExecStopPost=" + finish,
            "-p", "ExecStopPost=" + wrapup,     # the census of what it left (wrapup.py), after finish recorded it
            "--working-directory", clone,
            "--setenv", "AGENT_SEAT=" + seat, "--setenv", "RIMFLOW_SEAT=" + seat,
            *(sum((["--setenv", "%s=%s" % kv] for kv in run_tmp.env(rec["tmp"]).items()), []) if rec.get("tmp") else []),
            "--setenv", "CLAUDE_SCOPE_UNIT=claude-seat-%s-%s" % (seat, unit),
            "--setenv", "RM_ROLE_UNIT=" + unit, "--setenv", "RM_DETACHED_UNIT=" + unit,
            "--setenv", "RM_DISPATCHER_STATE=" + rec["state"],
            "--setenv", "CLAUDE_SCOPE_RUNTIME_MAX=%d" % bound,
            "-p", "RuntimeMaxSec=%d" % bound, "-p", "TimeoutStopSec=30",
            "--setenv", "PATH=" + path, "--"] + cmd


def launch(seat, item, brief, model, max_s, budget, now=None, runner=subprocess.run, known=None, clone=None):
    """-> (exit code, text). Refuses an unknown item, a bad model or seat, an empty brief."""
    now = now or time.time()
    if seat not in SEATS:
        return 2, "refused: seat %r is not one of %s" % (seat, ", ".join(SEATS))
    if model not in MODELS:
        return 2, "refused: model %r is not one of %s" % (model, ", ".join(MODELS))
    if not (brief or "").strip():
        return 2, "refused: empty brief"
    max_s = int(max_s)
    if not 60 <= max_s <= CAP_MAX_S:
        return 2, "refused: --max-s %d outside 60..%d" % (max_s, CAP_MAX_S)
    if known is None:
        import helper_checkpoint as HC
        known = HC.known_items()
    if not known:
        return 2, "refused: the ledger read 0 items (blind instrument), cannot check %s" % item
    if item not in known:
        return 2, "refused: %s is not a ledger item; file it first (rimflow namecheck, then file)" % item
    if clone:
        how = "given " + clone
    else:
        try:
            clone, how = take_clone(item, runner=runner)
        except Exception as e:  # noqa: BLE001
            return 1, "clone failed: %s" % e
    unit = unit_name(seat, item, now)
    root = state_dir()
    d = runs_dir(root)
    rec = {"unit": unit, "seat": seat, "item": item, "clone": clone, "model": model, "max_s": max_s,
           "budget_usd": float(budget), "at": now, "state": root, "out": os.path.join(d, unit + ".out.json"),
           "err": os.path.join(d, unit + ".err"), "status": "launching", "clone_how": how}
    msg = brief.rstrip() + FOOTER.format(clone=clone, item=item, seat=seat, max_s=max_s, budget="%g" % budget)
    if runner is subprocess.run:        # its own TMPDIR, deleted by run_tmp.sweep when the unit is gone
        rec["tmp"] = run_tmp.prepare(unit)
    write_record(rec, root)
    r = runner(launch_argv(rec, msg, claude_bin()), capture_output=True, text=True, timeout=60,
               stdin=subprocess.DEVNULL)
    if r.returncode:
        rec["status"] = "launch_failed"
        rec["why"] = ((r.stdout or "") + (r.stderr or "")).strip()[-300:]
        write_record(rec, root)
        return 1, "LAUNCH FAILED %s: %s" % (unit, rec["why"])
    rec["status"] = "running"
    write_record(rec, root)
    return 0, ("DETACHED %s\n  item %s, model %s, bound %d s, $%g\n  clone %s (%s)\n  record %s\n"
               "  it ends with a note on %s and a line in the Conductor log; `detached_helper.py status` lists runs"
               % (unit, item, model, max_s, budget, clone, how, record_path(unit, root), item))


def conductor_log_path():
    p = os.environ.get("RM_CONDUCTOR_LOG")
    if p:
        return p
    try:
        import dispatcher
        return dispatcher.no_handoff_rule(dispatcher.load_schedule()).get("conductor_log") or REAL_LOG
    except Exception:  # noqa: BLE001
        return REAL_LOG


def conductor_line(text, now, path=None):
    """One line in the Conductor log. Same guard as dispatcher.conductor_log: a test process never writes the real log."""
    import doorbell
    path = path or conductor_log_path()
    if (os.path.abspath(path) == os.path.abspath(REAL_LOG)
            and os.environ.get("RM_DISPATCHER_STATE", doorbell.DEFAULT_STATE) != doorbell.DEFAULT_STATE):
        raise RuntimeError("refusing to write the REAL conductor log from a test process: " + path)
    import conductor_log_guard
    conductor_log_guard.refuse_if_test(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n%s — DETACHED RUN ENDED: %s\n" % (iso(now), text))
    return path


def outcome(rec, env):
    """-> (short status, tokens or None, result tail). Reads claude's JSON and systemd's ExecStopPost variables."""
    import role_launch as RL
    res = RL.read_result({"out": rec["out"], "err": rec["err"]})
    svc = env.get("SERVICE_RESULT") or "unknown"
    code = env.get("EXIT_CODE") or "-"
    status = env.get("EXIT_STATUS") or "-"
    tokens = RL.run_tokens(res) if isinstance(res, dict) else None
    if isinstance(res, dict):
        tail = str(res.get("result") or res.get("subtype") or "")
        if len(tail) > 400:   # the end of the reply, cut at a word
            tail = "..." + tail[-400:].split(" ", 1)[-1]
        if res.get("is_error"):
            svc = svc + "/claude-error"
    else:
        try:
            with open(rec["err"], encoding="utf-8", errors="replace") as f:
                tail = "no result JSON; stderr tail: " + f.read()[-300:]
        except OSError:
            tail = "no result JSON, no stderr"
    return "%s (%s %s)" % (svc, code, status), tokens, " ".join(tail.split())


def finish(unit, now=None, env=None, runner=subprocess.run, log_path=None):
    """The unit's ExecStopPost. -> (exit code, text). Once per run: a second call changes nothing."""
    now = now or time.time()
    env = os.environ if env is None else env
    rec = read_record(unit)
    if not rec:
        return 2, "no record for %s" % unit
    if rec.get("status") == "finished":
        return 0, "already finished %s" % unit
    st, tokens, tail = outcome(rec, env)
    took = int(now - rec["at"])
    text = ("DETACHED run %s ended %s after %d s, %s tokens (model %s). Result: %s. Output %s; clone %s."
            % (unit, st, took, "UNMEASURED" if tokens is None else tokens, rec["model"], (tail if len(tail) <= 300 else "..." + tail[-300:].split(" ", 1)[-1]) or "-",
               rec["out"], rec["clone"]))
    clone, seat, item = rec["clone"], rec["seat"], rec["item"]
    cli = os.path.join(clone, "src", "RimMandrake", "rimflow", "cli.py")
    steps = []
    r = runner(["python3", cli, "note", item, "--text", text, "--seat", seat, "--why", "detached run ended"],
               cwd=clone, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    steps.append("note exit %d" % r.returncode)
    r = runner(["./publish", "-m", "ledger: detached run on %s ended" % item,
                "infrastructure/state/ledger/events/%s.jsonl" % seat],
               cwd=clone, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    pub = ((r.stdout or "") + (r.stderr or "")).strip()
    m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", pub)
    steps.append("publish " + (m.group(1)[:10] if m else "exit %d: %s" % (r.returncode, pub[-120:])))
    try:
        path = conductor_line("%s on %s (%s seat): %s, %d s, %s tokens. %s. READ: rimflow show %s."
                              % (unit, item, seat, st, took, "UNMEASURED" if tokens is None else tokens,
                                 (tail if len(tail) <= 200 else "..." + tail[-200:].split(" ", 1)[-1]) or "-", item), now, log_path)
        steps.append("conductor log " + path)
    except Exception as e:  # noqa: BLE001
        steps.append("conductor log FAILED: %s" % e)
    rec.update(status="finished", ended=now, result=st, tokens=tokens, steps=steps)
    write_record(rec)
    return 0, "FINISHED %s: %s" % (unit, "; ".join(steps))


def status(show_all=False, runner=subprocess.run):
    import role_launch as RL
    lines = []
    d = runs_dir()
    for n in sorted(os.listdir(d)):
        if not n.endswith(".json") or n.endswith(".out.json"):
            continue
        rec = read_record(n[:-5])
        if not rec or (rec.get("status") == "finished" and not show_all):
            continue
        live = RL.unit_state(rec["unit"], runner=runner) if rec.get("status") != "finished" else "-"
        lines.append("%s  %s  %s  item %s  %s  started %s" % (rec["unit"], rec.get("status"), live, rec["item"],
                                                               rec["model"], iso(rec["at"])))
    return "\n".join(lines) or "no detached runs" + ("" if show_all else " running (--all lists finished ones)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("launch")
    a.add_argument("--seat", required=True)
    a.add_argument("--item", required=True)
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--brief")
    g.add_argument("--brief-file")
    a.add_argument("--model", default="sonnet")
    a.add_argument("--max-s", type=int, default=DEFAULT_MAX_S)
    a.add_argument("--budget-usd", type=float, default=DEFAULT_BUDGET_USD)
    a.add_argument("--clone", help="an existing clone to run in (default: a pool clone <ITEM>.det)")
    f = sub.add_parser("finish")
    f.add_argument("--unit", required=True)
    s = sub.add_parser("status")
    s.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "launch":
        brief = args.brief
        if args.brief_file:
            with open(args.brief_file, encoding="utf-8") as fh:
                brief = fh.read()
        rc, text = launch(args.seat.upper(), args.item, brief, args.model, args.max_s, args.budget_usd,
                          clone=args.clone)
    elif args.cmd == "finish":
        rc, text = finish(args.unit)
    else:
        rc, text = 0, status(args.all)
    print(text)
    return rc


if __name__ == "__main__":
    sys.exit(main())

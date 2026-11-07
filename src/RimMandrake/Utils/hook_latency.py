#!/usr/bin/env python3
"""What do the PreToolUse hooks cost, and would one dispatcher per tool save enough to matter?

Item HOOKS_MERGE_ONE_DISPATCHER_PER_TOOL (redesign_final.md G19): merge hook entries only if a latency
measurement shows material cost; a replay corpus must show the same refusals and allowed operations.

    hook_latency.py                   measure here and now, print the table and the verdict
    hook_latency.py --gate            measure, replay the corpus, check settings agree with the verdict; exit 0/1
    hook_latency.py --replay          only the before/after replay
    hook_latency.py --transcripts     re-read real transcripts into hook_latency_transcripts.json
    hook_latency.py --harvest         re-sample real refused/allowed calls into hook_latency_corpus.json

"Before" runs each registered command string through `sh -c`, in parallel as Claude Code does.
"After" is an UNINSTALLED prototype: one process that runs every matching hook in turn, in-process, from cached
bytecode. It exists so the saving is measured rather than argued; settings.json never points at it.
"""
import argparse
import contextlib
import glob
import io
import json
import os
import random
import re
import resource
import runpy
import statistics
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SETTINGS = os.path.join(REPO, ".claude", "settings.json")
CORPUS = os.path.join(HERE, "hook_latency_corpus.json")
TRANSCRIPTS = os.path.join(HERE, "hook_latency_transcripts.json")
DECISION = os.path.join(REPO, "design", "RimMandrake", "hook_dispatcher_decision_2026-11-06.md")
FAILURE_HEADING = "## Dispatcher failure behaviour"

# What "material" means, fixed before the verdict is read. Any one of them makes the cost material.
MATERIAL_ABS_MS = 500        # a saving per typical Bash call a person or a log would notice
MATERIAL_STEP_SHARE = 0.05   # the saving as a share of a typical agent step (one tool call to the next)
MATERIAL_CPU_SHARE = 0.05    # the CPU saved across a day's calls as a share of the machine

SCRIPT = re.compile(r"/\.claude/hooks/([A-Za-z0-9_]+)\.py")
MUTED = re.compile(r"\|\|\s*(true|:)\s*$")
DISPATCHER = re.compile(r"(?i)dispatch")
PAYLOADS = {
    "bash_common": ("Bash", {"command": "ls -la src"}),
    "bash_commit": ("Bash", {"command": "git commit -m x"}),
    "bash_push": ("Bash", {"command": "git push origin HEAD"}),
    "edit": ("Edit", {"file_path": "src/x.py", "old_string": "a", "new_string": "b"}),
    "agent": ("Agent", {"description": "d", "prompt": "p", "subagent_type": "rm-fixer", "model": "sonnet"}),
}
SECRET = re.compile(r"(?i)token|secret|passw|api[_-]?key|authorization|bearer|ssh-")


def registrations(settings=SETTINGS, event="PreToolUse"):
    """[(matcher, command)] for one event, from the live settings file."""
    with open(settings) as f:
        groups = json.load(f).get("hooks", {}).get(event, [])
    return [(g.get("matcher") or "*", h["command"]) for g in groups for h in g.get("hooks", [])
            if h.get("type", "command") == "command"]


def commands_for(tool, settings=SETTINGS):
    """Every registered command that fires for this tool. Claude Code dedupes identical commands; so do we."""
    out = []
    for matcher, cmd in registrations(settings):
        if (matcher == "*" or re.fullmatch(matcher, tool)) and cmd not in out:
            out.append(cmd)
    return out


def payload(tool, tool_input, cwd=REPO):
    return {"session_id": "hook-latency", "transcript_path": "", "cwd": cwd, "permission_mode": "default",
            "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}


def child_env(repo=REPO):
    # RM_SPAWN_RESERVE_S=0: an allowed Agent call makes block_agent_over_slots reserve a real helper slot for 90 s, and
    # a replay is not a spawn. Without this a measurement run would steal live slots from a working seat.
    return dict(os.environ, CLAUDE_PROJECT_DIR=repo, RM_SPAWN_RESERVE_S="0")


def outcome(rc, out, err):
    """Claude Code's reading of one hook run: exit 2 or a JSON deny/block refuses; returns (refused, reason)."""
    if rc == 2:
        return True, err.strip()
    try:
        d = json.loads(out)
    except Exception:
        return False, ""
    if not isinstance(d, dict):
        return False, ""
    hso = d.get("hookSpecificOutput") or {}
    if hso.get("permissionDecision") == "deny":
        return True, hso.get("permissionDecisionReason", "")
    if d.get("decision") == "block" or d.get("continue") is False:
        return True, d.get("reason", "")
    return False, ""


def phase_parallel(cmds, pay, repo=REPO):
    """The registered commands, together, the way Claude Code runs them. Returns wall, cpu (s), per-hook outcomes."""
    env, data = child_env(repo), json.dumps(pay)
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.perf_counter()
    procs = [subprocess.Popen(["sh", "-c", c], cwd=repo, env=env, text=True, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) for c in cmds]
    # Feed all before reading any: a hook that ignores stdin must not hold the others back.
    for p in procs:
        try:
            p.stdin.write(data)
            p.stdin.close()
        except BrokenPipeError:
            pass
    results = {}
    for c, p in zip(cmds, procs):
        out, err = p.stdout.read(), p.stderr.read()
        results[c] = outcome(p.wait(), out, err)
    wall = time.perf_counter() - t0
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
    return wall, cpu, results


def run_prototype_inner(data, cmds):
    """One process, every hook in turn. Prints {command: [refused, reason]} on the real stdout."""
    real_argv, results, clean_path = sys.argv, {}, list(sys.path)
    for c in cmds:
        m = SCRIPT.search(c)
        if not m:
            continue
        hooks_dir = os.path.join(os.environ["CLAUDE_PROJECT_DIR"], ".claude", "hooks")
        # Restored per hook: block_blind_scan puts a skill folder on D: first in sys.path, which would charge every
        # later hook's imports for a slow mount and understate what a careful dispatcher saves.
        sys.path[:] = [hooks_dir] + clean_path
        out, err, rc = io.StringIO(), io.StringIO(), 0
        sys.argv = [os.path.join(hooks_dir, m.group(1) + ".py")]
        sys.stdin = io.StringIO(data)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                runpy.run_module(m.group(1), run_name="__main__", alter_sys=False)
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
            except BaseException:  # a raising hook fails open, as a registered one does
                rc = 1
        if MUTED.search(c) and rc:  # `2>/dev/null || true`: the exit code and stderr never reach Claude Code
            rc, err = 0, io.StringIO()
        results[c] = outcome(rc, out.getvalue(), err.getvalue())
    sys.argv = real_argv
    sys.__stdout__.write(json.dumps(results))


def phase_prototype(cmds, pay, repo=REPO):
    """The uninstalled dispatcher: a fresh process per call, as a registered hook would be."""
    env, data = child_env(repo), json.dumps(pay)
    with tempfile.NamedTemporaryFile("w", suffix=".json") as f:
        json.dump(cmds, f)
        f.flush()
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = time.perf_counter()
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--prototype-run", f.name], cwd=repo, env=env,
                           text=True, input=data, capture_output=True)
        wall = time.perf_counter() - t0
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
    if p.returncode:
        raise RuntimeError("prototype died rc=%s: %s" % (p.returncode, p.stderr[-400:]))
    return wall, cpu, {k: tuple(v) for k, v in json.loads(p.stdout).items()}


def measure(rounds=15, settings=SETTINGS, repo=REPO):
    """Median wall and CPU per payload class, before and after, modes interleaved so load drift hits both."""
    table = {}
    for name, (tool, tool_input) in PAYLOADS.items():
        cmds = commands_for(tool, settings)
        pay = payload(tool, tool_input, repo)
        n = rounds if name in ("bash_common", "edit", "agent") else max(3, rounds // 5)
        phase_prototype(cmds, pay, repo)  # warm the bytecode cache: credit the dispatcher its best case
        rows = {"before": [], "after": []}
        for _ in range(n):
            rows["before"].append(phase_parallel(cmds, pay, repo)[:2])
            rows["after"].append(phase_prototype(cmds, pay, repo)[:2])
        table[name] = {"hooks": len(cmds), "rounds": n}
        for side, vals in rows.items():
            table[name][side + "_wall_ms"] = statistics.median(v[0] for v in vals) * 1000
            table[name][side + "_cpu_ms"] = statistics.median(v[1] for v in vals) * 1000
    return table


def verdict(table, facts):
    """Pure arithmetic: the table plus the real call volume and step length give MATERIAL or NOT_MATERIAL."""
    heavy = facts["heavy_share"]
    heavy_saving = statistics.mean(table[k]["before_wall_ms"] - table[k]["after_wall_ms"]
                                   for k in ("bash_commit", "bash_push"))
    common = table["bash_common"]
    common_saving = common["before_wall_ms"] - common["after_wall_ms"]
    typical = (1 - heavy) * common_saving + heavy * heavy_saving
    step_share = typical / (facts["median_step_s"] * 1000)
    cpu_saving_ms = max(0.0, common["before_cpu_ms"] - common["after_cpu_ms"])
    cpu_share = cpu_saving_ms / 1000 * facts["bash_calls_per_day"] / (facts["cores"] * 86400)
    reasons = []
    if typical >= MATERIAL_ABS_MS:
        reasons.append("saving %.0f ms >= %d ms" % (typical, MATERIAL_ABS_MS))
    if step_share >= MATERIAL_STEP_SHARE:
        reasons.append("step share %.3f >= %.3f" % (step_share, MATERIAL_STEP_SHARE))
    if cpu_share >= MATERIAL_CPU_SHARE:
        reasons.append("cpu share %.3f >= %.3f" % (cpu_share, MATERIAL_CPU_SHARE))
    return {"verdict": "MATERIAL" if reasons else "NOT_MATERIAL", "reasons": reasons,
            "common_saving_ms": common_saving, "heavy_saving_ms": heavy_saving, "typical_saving_ms": typical,
            "step_share": step_share, "cpu_share": cpu_share}


def print_table(table):
    print("%-12s %5s %6s | %10s %10s | %9s %9s" % ("payload", "hooks", "rounds", "before ms", "after ms",
                                                    "b.cpu ms", "a.cpu ms"))
    for k, r in table.items():
        print("%-12s %5d %6d | %10.0f %10.0f | %9.0f %9.0f" % (
            k, r["hooks"], r["rounds"], r["before_wall_ms"], r["after_wall_ms"], r["before_cpu_ms"], r["after_cpu_ms"]))


def comparable(result):
    """Refused or not, and the reason with its clock readings and running counts blanked: hooks quote live state."""
    if result is None:
        return None
    return bool(result[0]), re.sub(r"\d+(\.\d+)?", "#", result[1] or "")


def replay(corpus=CORPUS, settings=SETTINGS, repo=REPO):
    """Every corpus call through the registered commands and through the prototype. Returns the comparison."""
    with open(corpus) as f:
        entries = json.load(f)["entries"]
    diffs, refused, refusing, allowed = [], 0, set(), 0
    for i, e in enumerate(entries):
        cmds = commands_for(e["tool"], settings)
        pay = payload(e["tool"], e["input"], repo)
        for _attempt in range(3):  # a hook quoting live state (running helpers) moved between the two runs: ask again
            before = phase_parallel(cmds, pay, repo)[2]
            after = phase_prototype(cmds, pay, repo)[2]
            differs = [c for c in cmds if SCRIPT.search(c) and comparable(before.get(c)) != comparable(after.get(c))]
            if not differs:
                break
        for c in cmds:
            if c in differs:
                diffs.append({"entry": i, "tool": e["tool"], "hook": SCRIPT.search(c).group(1),
                              "before": before.get(c), "after": after.get(c), "input": str(e["input"])[:160]})
        deny = [SCRIPT.search(c).group(1) for c, v in before.items() if v[0] and SCRIPT.search(c)]
        if deny:
            refused += 1
            refusing.update(deny)
        else:
            allowed += 1
    return {"entries": len(entries), "refused": refused, "allowed": allowed, "refusing_hooks": sorted(refusing),
            "diffs": diffs}


def transcript_files(days):
    cut = time.time() - days * 86400
    for d in glob.glob(os.path.expanduser("~/.claude/projects/-home-mandrake-rm-*")):
        for p, _, fs in os.walk(d):
            for f in fs:
                q = os.path.join(p, f)
                if f.endswith(".jsonl") and os.path.getmtime(q) >= cut:
                    yield q


def parse_ts(s):
    import datetime as dt
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def quantiles(v):
    v = sorted(v)
    return {"p%d" % int(p * 100): round(v[int(p * (len(v) - 1))] * 1000) for p in (.01, .05, .1, .25, .5, .75, .9)} if v else {}


def read_transcripts(days=3.0):
    """Real call volume, the gap between a tool call and its result, and agent step length from session transcripts."""
    calls, gaps, steps, cancels, files, heavy = {}, {}, [], {}, 0, 0
    for q in transcript_files(days):
        files += 1
        pend, last = {}, None
        for line in open(q, errors="replace"):
            if '"timestamp"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            a = d.get("attachment") or {}
            if a.get("hookEvent") == "PreToolUse" and a.get("type") == "hook_cancelled":
                key = (a.get("command") or "").rsplit("/", 1)[-1][:60]
                cancels[key] = cancels.get(key, 0) + 1
            if d.get("type") == "assistant":
                t = parse_ts(d["timestamp"])
                for b in (d.get("message") or {}).get("content") or []:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        pend[b["id"]] = (b["name"], t)
                        calls[b["name"]] = calls.get(b["name"], 0) + 1
                        if b["name"] == "Bash" and re.search(r"git (commit|push)|\./publish", str((b.get("input") or {}).get("command"))):
                            heavy += 1
                        if last is not None and 0 <= t - last < 600:
                            steps.append(t - last)
                        last = t
            elif d.get("type") == "user":
                c = (d.get("message") or {}).get("content")
                for b in c if isinstance(c, list) else []:
                    if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in pend:
                        n, t0 = pend.pop(b["tool_use_id"])
                        g = parse_ts(d["timestamp"]) - t0
                        if 0 <= g < 3600:
                            gaps.setdefault(n, []).append(g)
    bash = calls.get("Bash", 0)
    return {"measured_utc": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "days": days, "files": files,
            "bash_calls_per_day": round(bash / days), "heavy_share": round(heavy / max(bash, 1), 4),
            "median_step_s": round(statistics.median(steps), 2) if steps else None,
            "cores": os.cpu_count(), "tool_calls": calls, "gap_ms": {k: quantiles(v) for k, v in gaps.items()},
            "hook_cancelled": cancels}


def harvest(days=3.0, per_class=6, allowed_n=60, seed=20261106):
    """A committed corpus from real calls: refusals by kind (hook text prefix), plus a sample of allowed ones."""
    rnd = random.Random(seed)
    refused, allowed = {}, []

    def keep(i):
        s = json.dumps(i)
        return len(s) <= 1500 and not SECRET.search(s)
    for q in transcript_files(days):
        pend = {}
        for line in open(q, errors="replace"):
            if "tool_use" not in line and "tool_result" not in line:
                continue
            try:
                c = (json.loads(line).get("message") or {}).get("content")
            except Exception:
                continue
            for b in c if isinstance(c, list) else []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    pend[b["id"]] = (b["name"], b.get("input") or {})
                elif b.get("type") == "tool_result" and b.get("tool_use_id") in pend:
                    n, i = pend.pop(b["tool_use_id"])
                    if not keep(i):
                        continue
                    t = b.get("content")
                    t = t if isinstance(t, str) else " ".join(x.get("text", "") for x in t or [] if isinstance(x, dict))
                    if b.get("is_error") and re.match(r"PreToolUse:\w+ hook error", t):
                        refused.setdefault(t[:70], []).append({"tool": n, "input": i, "saw": t[:70]})
                    elif not b.get("is_error") and n in ("Bash", "Edit", "Write", "Agent", "SendMessage"):
                        allowed.append({"tool": n, "input": i})
    entries = []
    for k in sorted(refused):
        rnd.shuffle(refused[k])
        entries += refused[k][:per_class]
    rnd.shuffle(allowed)
    entries += allowed[:allowed_n]
    return {"note": "real calls sampled from session transcripts by hook_latency.py --harvest; replayed, never executed",
            "measured_utc": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "entries": entries}


def gate(rounds=15, settings=SETTINGS, corpus=CORPUS, facts_path=TRANSCRIPTS, decision=DECISION, repo=REPO):
    """Exit 0 only when the measurement, the replay, the settings file and the decision record all agree."""
    fails = []
    with open(facts_path) as f:
        facts = json.load(f)
    if not (facts.get("bash_calls_per_day", 0) > 0 and (facts.get("median_step_s") or 0) > 0):
        fails.append("transcript facts cannot see any calls: %s" % facts_path)
    table = measure(rounds, settings, repo)
    print_table(table)
    v = verdict(table, facts)
    print("verdict %s %s" % (v["verdict"], json.dumps({k: round(x, 4) for k, x in v.items() if isinstance(x, float)})))
    # The instrument must see the hooks at all: a phase faster than one interpreter start measured nothing.
    if table["bash_common"]["before_wall_ms"] < 5:
        fails.append("instrument blind: the Bash hook phase read %.1f ms" % table["bash_common"]["before_wall_ms"])
    merged = [c for _, c in registrations(settings) if DISPATCHER.search(c)]
    if v["verdict"] == "NOT_MATERIAL" and merged:
        fails.append("a dispatcher is registered but the cost is not material: %s" % merged[:2])
    if v["verdict"] == "MATERIAL" and not merged:
        fails.append("the cost is material (%s) and no dispatcher is built: this item is owed the merge" % v["reasons"])
    r = replay(corpus, settings, repo)
    print("replay entries=%d refused=%d allowed=%d hooks_refusing=%d diffs=%d" % (
        r["entries"], r["refused"], r["allowed"], len(r["refusing_hooks"]), len(r["diffs"])))
    print("refusing: " + " ".join(r["refusing_hooks"]))
    for d in r["diffs"][:10]:
        print("DIFF", json.dumps(d)[:400])
    if r["diffs"]:
        fails.append("%d replay differences before/after" % len(r["diffs"]))
    if r["refused"] < 5 or r["allowed"] < 20 or len(r["refusing_hooks"]) < 3:
        fails.append("the corpus cannot see both ways: %d refused by %d hooks, %d allowed" % (
            r["refused"], len(r["refusing_hooks"]), r["allowed"]))
    text = open(decision).read() if os.path.exists(decision) else ""
    if FAILURE_HEADING not in text:
        fails.append("%s lacks %r" % (decision, FAILURE_HEADING))
    for f_ in fails:
        print("GATE FAIL: " + f_)
    print("GATE " + ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--transcripts", action="store_true")
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--rounds", type=int, default=15)
    ap.add_argument("--days", type=float, default=3.0)
    ap.add_argument("--prototype-run")
    a = ap.parse_args()
    if a.prototype_run:
        with open(a.prototype_run) as f:
            cmds = json.load(f)
        run_prototype_inner(sys.stdin.read(), cmds)
        return 0
    if a.transcripts:
        with open(TRANSCRIPTS, "w") as f:
            json.dump(read_transcripts(a.days), f, indent=1, sort_keys=True)
        print(TRANSCRIPTS)
        return 0
    if a.harvest:
        c = harvest(a.days)
        with open(CORPUS, "w") as f:
            json.dump(c, f, indent=0)
        print("%s entries=%d" % (CORPUS, len(c["entries"])))
        return 0
    if a.gate:
        return gate(a.rounds)
    if a.replay:
        r = replay()
        print(json.dumps(r, indent=1)[:3000])
        return 1 if r["diffs"] else 0
    with open(TRANSCRIPTS) as f:
        facts = json.load(f)
    t = measure(a.rounds)
    print_table(t)
    print(json.dumps(verdict(t, facts), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

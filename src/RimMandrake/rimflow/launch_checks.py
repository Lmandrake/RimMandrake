#!/usr/bin/env python3
"""Launch checks: an item's declared `## launch-checks` block, run before a paid run starts (guard GATE_FIRST,
design/specs/2026-11-15-cheap-guards-at-every-door.md §3.2; RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES).

    ## launch-checks
    must-pass: <command>      exit 0 or the launch is refused with the command's own output
    must-fail: <command>      exit non-zero or the launch is refused: "already passes: close or re-scope"

Only that block is read; prose never refuses. A check that cannot run (exit 126/127, a timeout, an OSError, an unknown
line) is "did not run": never a refusal, the launch goes ahead (standing_rulings.md, A refusal carries its path to pass).
"""
import re
import subprocess
import time

HEAD = "## launch-checks"
KINDS = ("must-pass", "must-fail")
CANNOT_RUN = (126, 127)
TAIL_LINES = 20


def parse(text):
    """-> [{"kind", "cmd", "line"}] for each non-blank line of the `## launch-checks` section; [] when there is none."""
    out, inside = [], False
    for raw in (text or "").splitlines():
        s = raw.strip()
        if s.startswith("## "):
            inside = s.lower() == HEAD
            continue
        if not inside or not s or s.startswith("<!--"):
            continue
        m = re.match(r"^(must-pass|must-fail)\s*:\s*(.+)$", s)
        out.append({"kind": m.group(1), "cmd": m.group(2).strip(), "line": s} if m else
                   {"kind": "unknown", "cmd": "", "line": s})
    return out


def _tail(r):
    text = ((getattr(r, "stdout", "") or "") + (getattr(r, "stderr", "") or "")).strip()
    return "\n".join(text.splitlines()[-TAIL_LINES:]) or "(no output)"


def _refusal(c, rc, evidence):
    if c["kind"] == "must-pass":
        return {"check": c["line"], "kind": c["kind"], "evidence": "exit %d: %s" % (rc, evidence),
                "would_pass": "`%s` exits 0 in the run's clone" % c["cmd"],
                "smallest_fix": "do what the command's output asks first (it is the gate the run would hit), or re-scope "
                                "the item; the Conductor's bypass is --skip-launch-checks \"<why>\""}
    return {"check": c["line"], "kind": c["kind"], "evidence": "exit 0 (already passes): %s" % evidence,
            "would_pass": "`%s` exits non-zero on the run's clone (the red the item exists to fix)" % c["cmd"],
            "smallest_fix": "already passes: close the item with the sha that made it green, or re-scope it to what is "
                            "still red"}


def run(checks, cwd, timeout_s=120, runner=subprocess.run):
    """-> {"ok", "refusals", "did_not_run", "ms"}: each check run in cwd (the run's clone), capped at timeout_s."""
    t0 = time.time()
    refusals, dnr = [], []
    for c in checks:
        if c.get("kind") not in KINDS:
            dnr.append("%s: not a must-pass or must-fail line" % c.get("line"))
            continue
        try:
            r = runner(c["cmd"], shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            dnr.append("%s: timed out after %d s" % (c["line"], timeout_s))
            continue
        except OSError as e:
            dnr.append("%s: %s" % (c["line"], e))
            continue
        rc = r.returncode
        if rc in CANNOT_RUN:
            dnr.append("%s: exit %d (command not runnable): %s" % (c["line"], rc, _tail(r)))
        elif (c["kind"] == "must-pass") != (rc == 0):
            refusals.append(_refusal(c, rc, _tail(r)))
    return {"ok": not refusals, "refusals": refusals, "did_not_run": dnr, "ms": int((time.time() - t0) * 1000)}


def block_for(kind, mod=None, to=None, cmd=None):
    """-> the `## launch-checks` block a filer writes into an item: "advance" (mod, to) or "fix_red" (cmd)."""
    if kind == "advance":
        return "%s\nmust-pass: python3 src/RimMandrake/rimflow/maturation.py gate %s --to %s\n" % (HEAD, mod, to)
    if kind == "fix_red":
        return "%s\nmust-fail: %s\n" % (HEAD, cmd)
    raise ValueError("block_for: unknown kind %r" % (kind,))

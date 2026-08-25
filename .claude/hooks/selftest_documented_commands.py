#!/usr/bin/env python3
"""selftest_documented_commands.py — run the commands the docs tell people to run.

    python3 .claude/hooks/selftest_documented_commands.py
    python3 .claude/hooks/selftest_documented_commands.py --list

WHY THIS EXISTS
===============
🔴 Three separate failures on 2026-08-21, all the same shape: a doc told a seat to run a
command, and the command did not work.

  * `render.py`      — the documented form wrote a PREVIEW and published nothing, so
                       every seat's queue view sat frozen for 2h17m while four seats
                       filed 24 items into it. Fixed by adding `--overwrite-queues`.
  * `w9_run.py --dry` — the flag never existed. Argparse refused it, at the main menu,
                       with the owner waiting.
  * `cli.py game`    — POLICY's FIRST start-of-turn command, taking a required
                       positional. Bare, it exits non-zero. Every seat's turn had been
                       opening on a failing command.

Each was written by someone who never ran the line they wrote. This test runs them.

⛔ WHAT IT CANNOT CATCH, stated so nobody trusts it further than it goes
=======================================================================
It proves the command **parses and exits zero**, not that it DOES what the prose claims.
Bare `render.py` would still pass here — it is a valid invocation; it just does not
publish. So this catches the cheap two-thirds (dead flags, missing positionals, moved
paths) and never the subtle third. A green run is not a promise the docs are true.

⚠️ SIDE EFFECTS ARE THE RISK, and the rule is conservative: a command is run ONLY with
`--help`, or not at all. Nothing here may write the ledger, deploy a mod, touch the game
or take a bridge. When in doubt the line is SKIPPED and reported as skipped — a silent
skip would let this file rot into a green light over untested commands.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DOCS = ["CLAUDE.md", "GLOBAL_CLAUDE.md",
        "infrastructure/agents/POLICY.md",
        "infrastructure/agents/REP.md", "infrastructure/agents/BUILD.md",
        "infrastructure/agents/CHECK.md", "infrastructure/agents/DECIDE.md"]

# A documented invocation: `python3 <path.py> …`, or a `./script` at the repo root.
CMD_RE = re.compile(
    r"^\s*(?:python3?|py)\s+(?P<py>[\w./-]+\.py)(?P<args>[^\n]*)$"
    # ⚠️ `[\w.-]*` stopped at the first `/`, so `./src/.../show.sh <path>` parsed as the
    # command `src` with `/RimMandrake/...` as its arguments — and the test then tried to
    # execute the repo's `src` DIRECTORY. Slashes belong in the path.
    r"|^\s*\./(?P<sh>[\w][\w./-]*)(?P<shargs>[^\n]*)$", re.M)

# ⛔ Never executed, even with --help: these reach outside the repo or cost real time.
NEVER_RUN = ("broadcast.py",        # writes the peer socket — owner's tool
             "deploy_custom_mods.py",
             "modlist_swap.py",
             "status_server.py",    # binds a port and blocks
             "first_light.py",      # drives the live bridge
             "w9_run.py",           # drives the live bridge
             "refresh.py",          # long, and writes derived artefacts
             "board_loop.sh")       # no arg parsing: `--help` runs the publish loop
                                    # and re-execs itself. Measured 2026-08-24: it hit
                                    # the 60 s timeout and reported as a doc failure.


def commands():
    out = []
    for rel in DOCS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            body = fh.read()
        for m in CMD_RE.finditer(body):
            if m.group("py"):
                target, kind = m.group("py"), "py"
            else:
                target, kind = m.group("sh"), "sh"
            out.append((rel, kind, target, (m.group("args") or
                                            m.group("shargs") or "").strip()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    rows, fails, skips, ran = commands(), [], 0, 0
    for rel, kind, target, args in rows:
        path = os.path.join(ROOT, target)
        label = "%s  %s %s" % (rel, target, args)[:110]

        if a.list:
            print("  " + label)
            continue

        # 1. the file must exist. This alone catches a moved or renamed script.
        if not os.path.exists(path):
            fails.append((label, "no such file: %s" % target))
            continue
        if kind == "sh" and not os.access(path, os.X_OK):
            fails.append((label, "documented as ./%s but not executable" % target))
            continue
        if os.path.basename(target) in NEVER_RUN:
            skips += 1
            continue

        # 2. it must accept --help and exit 0. That is what proves argparse is wired
        #    and every documented flag at least reaches a parser.
        cmd = ([sys.executable, path, "--help"] if kind == "py"
               else [path, "--help"])
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               cwd=ROOT, timeout=60)
        except Exception as e:                                  # noqa: BLE001
            fails.append((label, "%s: %s" % (type(e).__name__, e)))
            continue
        ran += 1
        if r.returncode != 0:
            fails.append((label, "--help exited %d: %s"
                          % (r.returncode,
                             (r.stderr or r.stdout or "").strip()[:160])))
            continue

        # 3. every long flag the docs use must appear in that --help text.
        #    ⭐ This is the check that would have caught `w9_run.py --dry`.
        helptext = (r.stdout or "") + (r.stderr or "")

        # 🔴 CALIBRATION, 2026-08-24. This check used to compare a SUBCOMMAND's flags
        # against the PARENT's --help and report three false failures — `--owner-said`,
        # `--for`, `--kind` all exist on `rimflow` verbs and are used daily. A detector
        # that cries wolf three times in four is worse than no detector: it gets
        # ignored, then removed. An argparse subparser lists its flags only under
        # `<prog> <verb> --help`, so fetch that too.
        first = (args.strip().split() or [""])[0]
        if re.match(r"^[a-z][a-z-]*$", first):
            try:
                sub = subprocess.run(cmd[:-1] + [first, "--help"], capture_output=True,
                                     text=True, cwd=ROOT, timeout=60)
                helptext += (sub.stdout or "") + (sub.stderr or "")
            except Exception:                                   # noqa: BLE001
                pass                                            # parent help still applies
        elif first.startswith("<"):
            # The verb itself is a placeholder (`cli.py <verb> … --owner-said`), so
            # there is no subcommand help to fetch. Report it, never fail it —
            # UNMEASURED is an honest answer and a false FAIL is not.
            skips += 1
            continue

        for flag in re.findall(r"(?<!\w)--[a-z][a-z0-9-]+", args):
            if flag not in helptext:
                fails.append((label, "documents %s, which --help does not list" % flag))

    if a.list:
        print("\n%d documented command line(s)" % len(rows))
        return 0

    for label, why in fails:
        print("FAIL  %s\n        %s" % (label, why))
    print("\n%d checked, %d ran --help, %d skipped as side-effecting, %d failure(s)"
          % (len(rows), ran, skips, len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Class guard: `.claude/settings.json` still wires every hook a running promise names.

DRAFT (CLAUDE_STEVEDESKTOP_OFFLINE4, 2026-11-11): written while the WSL root went read-only; untested.
Destination: .claude/hooks/selftest_promised_hooks_wired.py in a clone.

A running promise `hook=<name>` (a `live` line on a ledger item, or a line of
src/RimMandrake/rimflow/live_baseline.txt) says the hook stays wired. The deadman
(deadman_check.py) rechecks those promises and reopens an item when one dies,
hours after the damage. The Pyrelands landing 8fb9f7f2b6 (2026-11-08) replaced
this file with a branch's copy holding one PreToolUse entry: every safety hook
went silent until 943a7a66da restored it. This test fails on any such settings
file, so the landing that carries one fails a selftest first.

The wiring check is the deadman's own (`live_line._hook`), run on the clone's
settings file alone. A hook retired on purpose is listed in
rimflow/live_retired.txt and is not owed.

    python3 .claude/hooks/selftest_promised_hooks_wired.py                 the working tree's settings
    python3 .claude/hooks/selftest_promised_hooks_wired.py --rev <sha>     the settings committed at <sha>
    python3 .claude/hooks/selftest_promised_hooks_wired.py --settings <f>  any settings file
"""
import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SETTINGS = os.path.join(REPO, ".claude", "settings.json")
sys.path[:0] = [os.path.join(REPO, "src", "RimMandrake", "rimflow"), os.path.join(REPO, "src", "RimMandrake", "Utils")]

import live_line          # noqa: E402
import deadman_check      # noqa: E402

PROBE = "block_blanket_git_stage.py"


def promised_hooks(items=None):
    retired = deadman_check.load_retired()
    out = {}

    def add(line, who):
        if deadman_check.subject(line) in retired:
            return
        p = live_line.parse(line)
        if p["kind"] == "hook":
            out.setdefault(p["hook"], []).append(who)

    for line in deadman_check.load_baseline():
        add(line, "live_baseline.txt")
    if items is None:
        import model
        items = model.replay(model.read()).items
    for iid, it in sorted(items.items()):
        line = getattr(it, "live", None)
        if line and not line.startswith("once:") and it.state not in deadman_check.RETIRED:
            add(line, iid)
    return out


def unwired(settings_path, hooks):
    return {h: why for h in sorted(hooks) for why in [live_line._hook(h, settings_path)] if why}


def staged(text, tmp):
    d = os.path.join(tmp, ".claude")
    os.makedirs(d, exist_ok=True)
    if not os.path.exists(os.path.join(d, "hooks")):
        os.symlink(HERE, os.path.join(d, "hooks"))
    path = os.path.join(d, "settings.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def without(settings, name):
    got = copy.deepcopy(settings)
    for groups in (got.get("hooks") or {}).values():
        for g in groups:
            g["hooks"] = [h for h in g.get("hooks", []) if name not in h.get("command", "")]
    return got


def probe(tmp):
    with open(SETTINGS, encoding="utf-8") as f:
        main = json.load(f)
    if live_line._hook(PROBE, SETTINGS):
        return None
    got = unwired(staged(json.dumps(without(main, PROBE)), os.path.join(tmp, "probe1")), [PROBE, "bench_mode.py"])
    if set(got) != {PROBE}:
        return "removing %s's registration should unwire it alone; the check said %s" % (PROBE, got or "nothing")
    if not unwired(staged("{not json", os.path.join(tmp, "probe2")), [PROBE]):
        return "an unparseable settings file read as wiring %s" % PROBE
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--rev")
    g.add_argument("--settings")
    a = ap.parse_args(argv)
    hooks = promised_hooks()
    if not hooks:
        print("FAIL: no running promise names a hook; the instrument cannot see")
        return 1
    with tempfile.TemporaryDirectory(prefix="promised_hooks_") as tmp:
        why = probe(tmp)
        if why:
            print("FAIL: sanity probe: %s" % why)
            return 1
        if a.rev:
            r = subprocess.run(["git", "show", "%s:.claude/settings.json" % a.rev], cwd=REPO, capture_output=True,
                               text=True, timeout=60)
            if r.returncode:
                print("FAIL: cannot read .claude/settings.json at %s: %s" % (a.rev, r.stderr.strip()))
                return 1
            path, label = staged(r.stdout, os.path.join(tmp, "rev")), "%s:.claude/settings.json" % a.rev
        elif a.settings:
            with open(a.settings, encoding="utf-8") as f:
                path, label = staged(f.read(), os.path.join(tmp, "file")), a.settings
        else:
            path, label = SETTINGS, os.path.relpath(SETTINGS, REPO)
        bad = unwired(path, hooks)
    if bad:
        print("FAIL: %s unwires %d of %d promised hooks:" % (label, len(bad), len(hooks)))
        for h, why in bad.items():
            print("  %-34s promised by %s" % (h, ", ".join(hooks[h])))
            print("  %-34s %s" % ("", why.replace(path, label)))
        return 1
    print("ok: %s wires all %d promised hooks (sanity probe saw an unwired %s)" % (label, len(hooks), PROBE))
    return 0


if __name__ == "__main__":
    sys.exit(main())

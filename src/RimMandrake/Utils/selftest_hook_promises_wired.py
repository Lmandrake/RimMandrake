#!/usr/bin/env python3
"""Class guard (CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE): every hook a `hook=` promise names is wired in the repo's
.claude/settings.json.

The instance: 8fb9f7f2b6 (Pyrelands lands on main, 2026-11-08 11:52 PST) squashed the branch's settings.json over
main's and left one hook (game_gate.py) of ~40. Every PreToolUse/PostToolUse safety hook went dark until 943a7a66da
restored the file at 19:38 PST; the deadman reopened every item that had closed on a hook promise
(CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE on hook=block_agent_over_slots.py, CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK on
hook=conductor_goodbye.py). This test reads the promises the way the deadman does (deadman_check: the ledger and
live_baseline.txt, minus live_retired.txt and dropped items) and checks each with the deadman's own wiring check
(live_line._hook), so a settings file that drops a promised hook goes red here, naming the hook and who promised it.

Wider than the sweep on purpose: the sweep rechecks only settled items, this checks every hook promise on a ledger item
that is not dropped or superseded (one reopened for rework still means its hook to be wired); a hook must also sit in
a hook command, not just anywhere in the `hooks` text; and a hook line that ever entered live_baseline.txt must still be
there or be retired, so a landing that rolls the baseline back with the settings cannot take its promises with it.
A broken settings file is a red row, never a crash (`rimflow guard` reads a crash as nothing shown).

The fixtures prove it can see, on a synthetic settings file and project root of their own (so a clobbered repo file
cannot blind them): the full set is green, one hook taken out is reported by name, and so on.

    python3 src/RimMandrake/Utils/selftest_hook_promises_wired.py
    python3 src/RimMandrake/Utils/selftest_hook_promises_wired.py --settings <copy of 8fb9f7f2b6:.claude/settings.json>
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SETTINGS = ROOT / ".claude" / "settings.json"
BASELINE_REL = "src/RimMandrake/rimflow/live_baseline.txt"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_hook_promises_wired_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
import deadman_check as DM  # noqa: E402
import live_line  # noqa: E402

FAILS = []
BASELINE = "live_baseline.txt"
TARGET = "block_agent_over_slots.py"      # this item's own promise
FIX = ("fix   wire each back in .claude/settings.json (a landing that replaced the file: restore it from the commit "
       "before), or retire a hook removed on purpose with a hook=<file> line in src/RimMandrake/rimflow/live_retired.txt")


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def promised(items, baseline, retired):
    """-> {hook file: {name as promised: [who promised it]}}, from the baseline and every item not dropped or
    superseded. `hook=conductor_goodbye.py` and `hook=.claude/hooks/conductor_goodbye.py` are one hook, each spelling
    checked as written (the deadman checks the literal). A hook promise that does not parse is kept under its raw line.
    A baseline line whose fixed item (LIVE_RESTORE_<X>) was dropped holds no promise, as in deadman_check.promises."""
    out = {}

    def add(line, who):
        sub = DM.subject(line)
        if not sub.startswith("hook=") or sub in retired:
            return
        try:
            name = live_line.parse(line)["hook"]
        except (ValueError, KeyError):
            name = "<unparsed: %s>" % line
        out.setdefault(os.path.basename(name), {}).setdefault(name, []).append(who)
    for line in baseline:
        it = items.get(DM.item_id(line))
        if not (it is not None and it.state in DM.RETIRED):
            add(line, BASELINE)
    for iid, it in sorted(items.items()):
        line = getattr(it, "live", None)
        if isinstance(line, str) and line and not line.startswith("once:") and it.state not in DM.RETIRED:
            add(DM.moved(line), iid)
    return out


def sources(spellings):
    return [w for ws in spellings.values() for w in ws]


def who(spellings):
    s = sources(spellings)
    return ", ".join(s[:4]) + (" and %d more" % (len(s) - 4) if len(s) > 4 else "")


def commands(cfg):
    """-> ([hook command strings], [shape problems]) for a settings dict, walked the way Claude Code reads it:
    hooks.<Event>[] groups, each with a hooks[] list of {command}. A part of another shape is a problem, not a crash."""
    hooks = cfg.get("hooks")
    if hooks is None:
        return [], []
    if not isinstance(hooks, dict):
        return [], ["`hooks` is a %s, not an object of events" % type(hooks).__name__]
    cmds, probs = [], []
    for ev, groups in hooks.items():
        if not isinstance(groups, list):
            probs.append("hooks.%s is a %s, not a list of groups" % (ev, type(groups).__name__))
            continue
        for i, g in enumerate(groups):
            if not isinstance(g, dict) or not isinstance(g.get("hooks"), list):
                probs.append("hooks.%s[%d] has no hooks list" % (ev, i))
                continue
            for j, h in enumerate(g["hooks"]):
                if isinstance(h, dict) and isinstance(h.get("command"), str):
                    cmds.append(h["command"])
                elif not isinstance(h, dict) or h.get("type", "command") == "command":   # a prompt hook has no command
                    probs.append("hooks.%s[%d].hooks[%d] has no command" % (ev, i, j))
    return cmds, probs


def unwired(promises, settings, root=ROOT):
    """-> ({hook file: why it is not wired}, [shape problems]) for the settings file at `settings`, hook files resolved
    under `root`. Never raises: an unreadable or odd-shaped file fails every promise it cannot honour."""
    try:
        cfg = json.loads(Path(settings).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {h: "settings unreadable (%s)" % e for h in promises}, ["%s does not read as JSON (%s)" % (settings, e)]
    if not isinstance(cfg, dict):
        why = "settings top level is a %s, not an object" % type(cfg).__name__
        return {h: why for h in promises}, [why]
    cmds, probs = commands(cfg)
    bad = {}
    for hook, spellings in sorted(promises.items()):
        for name in sorted(spellings):
            if name.startswith("<unparsed"):
                why = "the promise does not parse"
            else:
                try:
                    why = live_line._hook(name, str(settings), root=str(root))
                except Exception as e:  # noqa: BLE001   the deadman's check died on this file: that is a red, not a crash
                    why = "the deadman's wiring check raised %s: %s" % (type(e).__name__, e)
                rx = re.compile(r"(?<![\w.-])%s(?![\w.-])" % re.escape(name))
                if not why and not any(rx.search(c) for c in cmds):
                    why = "named in %s but in no hook command (hooks.<Event>[].hooks[].command)" % settings
            if why:
                bad[hook] = why.replace("hook %s is " % name, "")
                break
    return bad, probs


def baseline_history():
    """-> (every hook= subject ever added to live_baseline.txt, or None when git cannot say, and why). A shallow clone
    holds part of the history, so it cannot say."""
    try:
        sh = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=ROOT, capture_output=True, text=True,
                            timeout=60, stdin=subprocess.DEVNULL)
        if sh.returncode or sh.stdout.strip() != "false":
            return None, "a shallow clone (or no git) holds only part of the history: %s" % (sh.stdout or sh.stderr).strip()
        r = subprocess.run(["git", "log", "--follow", "--format=", "-p", "--", BASELINE_REL], cwd=ROOT,
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    if r.returncode:
        return None, (r.stderr or "").strip()[-200:]
    return {DM.subject(l[1:].split("#", 1)[0]) for l in r.stdout.splitlines() if l.startswith("+hook=")}, ""


def plain(promises):
    """The promises as the fixtures use them: an absolute or ~ spelling becomes its bare file name, so a fixture file is
    never written outside the fixtures' own root."""
    out = {h: {(h if n.startswith(("/", "~")) else n): w for n, w in sp.items() if not n.startswith("<unparsed")}
           for h, sp in promises.items()}
    return {h: sp for h, sp in out.items() if sp}


def fixture_path(name):
    return name if "/" in name else os.path.join(".claude", "hooks", name)


def fake_project(promises):
    """A project root of the fixtures' own, holding a file for every promised hook."""
    root = TMP / "project"
    for spellings in promises.values():
        for name in spellings:
            p = root / fixture_path(name)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch()
    return root


def fake_settings(promises, tag, drop=(), rename=None, extra=None):
    """A settings file in the repo's own command style wiring every promised hook but `drop`; `rename` = (hook, new
    name) wires a lookalike in its place."""
    cmds = []
    for hook, spellings in sorted(promises.items()):
        if hook in drop:
            continue
        for name in sorted(spellings):
            path = fixture_path(name)
            if rename and hook == rename[0]:
                path = path.replace(hook, rename[1])
            cmds.append({"type": "command", "command": 'python3 "${CLAUDE_PROJECT_DIR:-.}/%s" 2>/dev/null || true' % path})
    cfg = {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": cmds}]}}
    cfg.update(extra or {})
    p = TMP / ("settings_%s.json" % tag)
    p.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return p


def sanity(promises, items, baseline_names, ever):
    """The guard can see: it read the ledger and the baseline, and on fixtures of its own a missing hook is named."""
    ledger = {n for n, sp in promises.items() if any(s != BASELINE for s in sources(sp))}
    check(len(items) > 0, "the ledger reads (%d items)" % len(items))
    check(bool(ledger), "the ledger yields hook promises (%d hooks, e.g. %s)" % (len(ledger), ", ".join(sorted(ledger)[:3])))
    check(bool(baseline_names), "live_baseline.txt yields hook promises (%d)" % len(baseline_names))
    check(bool(ever), "live_baseline.txt's git history yields hook lines (%d)" % len(ever or ()))
    check(TARGET in promises, "%s (this item's own promise) is among the promises read" % TARGET)
    promises = plain(promises)
    promises.setdefault(TARGET, {TARGET: ["fixture"]})
    root = fake_project(promises)

    def run(path, proms=promises, at=root):
        return unwired(proms, path, root=at)[0]
    check(run(fake_settings(promises, "full")) == {}, "fixture: every promised hook wired reads green (%d hooks)" % len(promises))
    p = fake_settings(promises, "with_prompt_hook")
    cfg = json.loads(p.read_text(encoding="utf-8"))
    cfg["hooks"]["Stop"] = [{"hooks": [{"type": "prompt", "prompt": "check the work"}]}]
    p.write_text(json.dumps(cfg), encoding="utf-8")
    check(unwired(promises, p, root=root) == ({}, []), "fixture: a prompt hook (no command) beside the full set is no problem")
    got = run(fake_settings(promises, "minus_one", drop={TARGET}))
    check(set(got) == {TARGET}, "fixture: settings without %s report exactly that hook (got %s)" % (TARGET, sorted(got)))
    got = run(fake_settings(promises, "lookalike", rename=(TARGET, "x_" + TARGET)))
    check(set(got) == {TARGET}, "fixture: a lookalike x_%s does not count as wiring it (whole-name match)" % TARGET)
    only_ledger = sorted(ledger - baseline_names)
    if only_ledger:
        name = only_ledger[0]
        got = run(fake_settings(promises, "minus_ledger_only", drop={name}))
        check(set(got) == {name}, "fixture: a hook promised only on the ledger (%s, by %s) is reported when dropped"
              % (name, who(promises[name])))
    else:
        print("note  every ledger hook promise is also in the baseline: the ledger-only row has nothing to drop")
    got = run(fake_settings(promises, "disabled", extra={"disableAllHooks": True}))
    check(len(got) == len(promises), "fixture: disableAllHooks reports every promised hook (%d of %d)" % (len(got), len(promises)))
    p = fake_settings(promises, "matcher_only", drop={TARGET})
    cfg = json.loads(p.read_text(encoding="utf-8"))
    cfg["hooks"]["PreToolUse"].append({"matcher": TARGET, "hooks": []})
    p.write_text(json.dumps(cfg), encoding="utf-8")
    got = run(p)
    check(set(got) == {TARGET}, "fixture: %s named only in a matcher, in no command, is reported (got %s)" % (TARGET, sorted(got)))
    target_file = root / fixture_path(sorted(promises[TARGET])[0])
    target_file.unlink()
    got = run(fake_settings(promises, "file_gone"))
    target_file.touch()
    check("absent" in got.get(TARGET, ""), "fixture: a wired hook whose file is gone is reported (%s)" % got.get(TARGET))
    for tag, body in (("top_level_list", "[]"), ("hooks_string", '{"hooks": "%s"}' % TARGET),
                      ("group_dict", '{"hooks": {"PreToolUse": {"hooks": [{"command": "%s"}]}}}' % TARGET), ("not_json", "{")):
        p = TMP / ("settings_%s.json" % tag)
        p.write_text(body, encoding="utf-8")
        got, probs = unwired(promises, p, root=root)
        check(TARGET in got and probs, "fixture: a %s settings file fails %s with a shape problem, no crash (%s)"
              % (tag.replace("_", " "), TARGET, (probs or ["none"])[0]))
    ex = {"OLD": type("It", (), {"state": "dropped", "live": "hook=%s" % TARGET})()}
    check(TARGET not in promised(ex, [], set()) and TARGET not in promised({}, ["hook=" + TARGET], {"hook=" + TARGET})
          and "bench_mode.py" not in promised({"LIVE_RESTORE_BENCH_MODE": ex["OLD"]}, ["hook=bench_mode.py"], set()),
          "fixture: a dropped item, a retired subject and a dropped LIVE_RESTORE_ item promise nothing")


def main(settings=None):
    settings = Path(settings) if settings else SETTINGS
    items = DM.read_items()
    baseline = DM.load_baseline()
    retired = DM.load_retired()
    promises = promised(items, baseline, retired)
    baseline_names = {n for n, sp in promises.items() if BASELINE in sources(sp)}
    print("settings: %s" % settings)
    print("promises: %d hooks (%d from %s, %d from the ledger; live_retired.txt retires %d subjects)"
          % (len(promises), len(baseline_names), BASELINE,
             len({n for n, sp in promises.items() if any(x != BASELINE for x in sources(sp))}), len(retired)))
    bad, probs = unwired(promises, settings)
    for prob in probs:
        check(False, "settings shape: %s" % prob)
    for name, why in sorted(bad.items()):
        check(False, "hook %s (promised by %s): %s" % (name, who(promises[name]), why))
    check(not bad, "every promised hook is wired in %s (%d of %d)" % (settings, len(promises) - len(bad), len(promises)))
    if bad:
        print(FIX)
    ever, err = baseline_history()
    if ever is None:
        check(False, "git log of %s reads (%s)" % (BASELINE_REL, err))
    else:
        dropped = {s for s in ever if s and getattr(items.get(DM.item_id(s)), "state", None) in DM.RETIRED}
        gone = sorted(ever - {DM.subject(l) for l in baseline} - set(retired) - dropped)
        check(not gone, "every hook line ever in %s is still there or retired in live_retired.txt (gone: %s)"
              % (BASELINE, ", ".join(gone) or "none"))
    print("-- the instrument (fixtures of its own, whatever the settings above) --")
    sanity(promises, items, baseline_names, ever)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and (len(a) != 2 or a[0] != "--settings"):
        print("usage: selftest_hook_promises_wired.py [--settings <settings.json>]")
        shutil.rmtree(TMP, ignore_errors=True)
        sys.exit(2)
    try:
        main(a[1] if a else None)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("FAIL %d" % len(FAILS) if FAILS else "ALL OK")
    sys.exit(1 if FAILS else 0)

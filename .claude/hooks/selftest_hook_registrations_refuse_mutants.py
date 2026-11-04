#!/usr/bin/env python3
"""Selftest: selftest_hook_registrations_refuse goes RED when a refusal is muted.

A green pass from that test means something only if it would turn red on the
defect it guards (item HOOKS_VERIFY_TRUE_SUFFIX_MAY_MUTE_REFUSALS). Each mutant
here builds a scratch repo (the real tree symlinked, `.claude/` copied), breaks
one thing, points the selftest's module at it, and asserts the named tier fails:

  M0 unmutated copy                                   -> all tiers green
  M1 block_blanket_git_stage.py refuses by exit 2     -> tier 2 (static) AND
     behind its '2>/dev/null || true' registration       tier 3 (deny not blocked)
  M2 every '|| true' suffix stripped from settings    -> tier 1 sanity (MUTE blind)
  M3 block_blanket_git_stage.py's registration gone   -> tier 3 (not registered)
  M4 block_blanket_git_stage.py allows everything     -> tier 3 (deny not blocked)

    python3 .claude/hooks/selftest_hook_registrations_refuse_mutants.py
"""
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TARGET = "block_blanket_git_stage.py"


def load():
    spec = importlib.util.spec_from_file_location(
        "hookreg_under_test", os.path.join(HERE, "selftest_hook_registrations_refuse.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scratch():
    tmp = tempfile.mkdtemp(prefix="hookreg_mutant_")
    for name in os.listdir(REPO):
        if name in (".claude", ".git"):
            continue
        os.symlink(os.path.join(REPO, name), os.path.join(tmp, name))
    os.makedirs(os.path.join(tmp, ".claude"))
    shutil.copy(os.path.join(REPO, ".claude", "settings.json"), os.path.join(tmp, ".claude"))
    shutil.copytree(HERE, os.path.join(tmp, ".claude", "hooks"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    return tmp


def run_tiers(tmp):
    """-> {tier: [fail messages]} for the selftest pointed at scratch repo `tmp`."""
    mod = load()
    mod.REPO = tmp
    mod.HERE = os.path.join(tmp, ".claude", "hooks")
    mod.SETTINGS = os.path.join(tmp, ".claude", "settings.json")
    regs = mod.registrations()
    got = {}
    for tier in ("tier1_stubs", "tier2_static", "tier3_real"):
        del mod.fails[:]
        getattr(mod, tier)(regs)
        got[tier] = list(mod.fails)
    return got


def edit_settings(tmp, fn):
    p = os.path.join(tmp, ".claude", "settings.json")
    with open(p) as f:
        data = json.load(f)
    data = fn(data)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def write_hook(tmp, src):
    with open(os.path.join(tmp, ".claude", "hooks", TARGET), "w") as f:
        f.write(src)


EXIT2 = ("import json, sys\nd = json.load(sys.stdin)\n"
         "if 'git add -A' in (d.get('tool_input') or {}).get('command', ''):\n"
         "    sys.stderr.write('refused')\n    sys.exit(2)\nsys.exit(0)\n")
ALLOW_ALL = "import sys\nsys.stdin.read()\nsys.exit(0)\n"


def strip_mute(data):
    for groups in data.get("hooks", {}).values():
        for g in groups:
            for h in g.get("hooks", []):
                if "command" in h:
                    h["command"] = re.sub(r"\s*\|\|\s*true\s*$", "", h["command"])
    return data


def drop_target(data):
    for groups in data.get("hooks", {}).values():
        for g in groups:
            g["hooks"] = [h for h in g.get("hooks", []) if TARGET not in h.get("command", "")]
    return data


MUTANTS = [
    # name, mutate(tmp), tiers that must be red, (tier, substring a fail must carry)
    ("M0", lambda t: None, (), None),
    ("M1", lambda t: write_hook(t, EXIT2), ("tier2_static", "tier3_real"),
     ("tier3_real", "%s: deny case NOT blocked" % TARGET)),
    ("M2", lambda t: edit_settings(t, strip_mute), ("tier1_stubs",),
     ("tier1_stubs", "MUTE pattern is blind")),
    ("M3", lambda t: edit_settings(t, drop_target), ("tier3_real",),
     ("tier3_real", "%s is not registered" % TARGET)),
    ("M4", lambda t: write_hook(t, ALLOW_ALL), ("tier3_real",),
     ("tier3_real", "%s: deny case NOT blocked" % TARGET)),
]


def main():
    bad = []
    for name, mutate, red, must in MUTANTS:
        tmp = scratch()
        try:
            mutate(tmp)
            got = run_tiers(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        for tier, fails in sorted(got.items()):
            if tier in red and not fails:
                bad.append("%s: %s stayed GREEN on the mutant" % (name, tier))
            if tier not in red and fails:
                bad.append("%s: %s went red off-target: %s" % (name, tier, fails[:2]))
        if must and not any(must[1] in f for f in got[must[0]]):
            bad.append("%s: %s fails lack %r: %s" % (name, must[0], must[1], got[must[0]][:2]))
        print("%s red=%s" % (name, ",".join(t for t, f in sorted(got.items()) if f) or "none"))
    if bad:
        for b in bad:
            print("FAIL", b)
        return 1
    print("PASS selftest_hook_registrations_refuse_mutants: %d mutants, each caught by its tier"
          % len(MUTANTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())

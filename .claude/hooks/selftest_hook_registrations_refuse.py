#!/usr/bin/env python3
"""Selftest: every hook REGISTRATION in .claude/settings.json can still refuse.

Many registrations end in `2>/dev/null || true`. That suffix turns an exit-2
refusal into exit 0 (and throws its stderr reason away), so only a hook that
refuses with a JSON decision on STDOUT still blocks. Testing the script alone
cannot see this; this test runs the registered COMMAND STRING through `sh -c`,
the way Claude Code runs it (item HOOKS_VERIFY_TRUE_SUFFIX_MAY_MUTE_REFUSALS).

Three tiers:
  1. sanity probe — for each muted registration, a stub that refuses by exit 2
     must come back exit 0 through the registered command (proves this test can
     SEE muting), and a stub that refuses by JSON must still come back denied.
     The same stubs give the crash case: a hook that raises fails OPEN (never
     blocks), muted or not.
  2. static guard — no muted registration's script may refuse by exit 2
     (`sys.exit(2)`, `exit(2)`, `os._exit(2)`, or `return 2` from `main`).
  3. real scripts — the registered commands of hooks with a stateless trigger,
     run against the real repo: allow payload allowed, deny payload denied.

    python3 .claude/hooks/selftest_hook_registrations_refuse.py
"""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SETTINGS = os.path.join(REPO, ".claude", "settings.json")

# Exit-code muters: anything after which a non-zero exit becomes 0.
MUTE = re.compile(r"\|\|\s*(true|:|exit(\s+0)?)\s*$|;\s*(true|:|exit\s+0)\s*$")
SCRIPT = re.compile(r"/\.claude/hooks/([A-Za-z0-9_]+\.py)")
# Events where a hook's refusal means something (exit 2 or a JSON decision).
BLOCKING = {"PreToolUse", "PermissionRequest", "UserPromptSubmit", "Stop",
            "SubagentStop", "WorktreeCreate", "PreCompact", "PostToolUse"}

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


def registrations():
    with open(SETTINGS) as f:
        hooks = json.load(f).get("hooks", {})
    out = []
    for event, groups in hooks.items():
        for g in groups:
            for h in g.get("hooks", []):
                cmd = h.get("command", "")
                m = SCRIPT.search(cmd)
                out.append((event, g.get("matcher", ""), cmd, m.group(1) if m else None))
    return out


def run(cmd, payload, project):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=project)
    for k in ("MEASURE_ALLOW_SCAN", "RM_ALLOW_UNBOUNDED_AGENT"):
        env.pop(k, None)
    p = subprocess.run(["sh", "-c", cmd], input=json.dumps(payload), cwd=project,
                       capture_output=True, text=True, env=env, timeout=120)
    return p.returncode, p.stdout


def blocked(rc, out):
    """Claude Code's reading: exit 2 blocks; exit 0 with a JSON deny/block blocks."""
    if rc == 2:
        return True
    if rc != 0:
        return False
    for line in [out.strip()] + out.strip().splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        hso = d.get("hookSpecificOutput") or {}
        dec = hso.get("decision") if isinstance(hso.get("decision"), dict) else {}
        if (hso.get("permissionDecision") == "deny" or d.get("decision") == "block"
                or dec.get("behavior") == "deny" or d.get("continue") is False):
            return True
    return False


def payload_for(event, tool="Bash", tool_input=None):
    p = {"hook_event_name": event, "cwd": REPO, "session_id": "selftest"}
    if event in ("PreToolUse", "PermissionRequest", "PostToolUse"):
        p.update(tool_name=tool, tool_input=tool_input or {"command": "echo hi"})
    return p


STUB_EXIT2 = "import sys\nsys.stderr.write('refused')\nsys.exit(2)\n"
STUB_JSON = ("import json\nprint(json.dumps({'decision': 'block', 'reason': 'r', "
             "'hookSpecificOutput': {'hookEventName': 'PreToolUse', "
             "'permissionDecision': 'deny', 'permissionDecisionReason': 'r'}}))\n")
STUB_CRASH = "raise RuntimeError('hook crashed')\n"


def tier1_stubs(regs):
    tmp = tempfile.mkdtemp(prefix="hookreg_selftest_")
    try:
        hooks = os.path.join(tmp, ".claude", "hooks")
        os.makedirs(hooks)
        muted_seen = 0
        for event, _matcher, cmd, script in regs:
            if not script or event not in BLOCKING:
                continue
            path = os.path.join(hooks, script)
            muted = bool(MUTE.search(cmd))
            muted_seen += muted
            for stub, kind in ((STUB_EXIT2, "exit2"), (STUB_JSON, "json"), (STUB_CRASH, "crash")):
                with open(path, "w") as f:
                    f.write(stub)
                rc, out = run(cmd, payload_for(event), tmp)
                b = blocked(rc, out)
                tag = "%s %s" % (event, script)
                if kind == "exit2":
                    check(b != muted, "%s: exit-2 refusal muted=%s but blocked=%s (rc=%s) — "
                          "the MUTE pattern misreads this command: %r" % (tag, muted, b, rc, cmd))
                elif kind == "json":
                    check(b, "%s: a JSON refusal does not survive the registered command %r" % (tag, cmd))
                else:
                    check(not b, "%s: a crashing hook BLOCKS (rc=%s) — it must fail open" % (tag, rc))
        check(muted_seen > 0, "sanity: no muted registration found — the MUTE pattern is blind")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def exits_two(src):
    """Line numbers where the script refuses by exit code 2."""
    tree = ast.parse(src)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and node.args:
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            a = node.args[0]
            if name in ("exit", "_exit") and isinstance(a, ast.Constant) and a.value == 2:
                hits.append(node.lineno)
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for sub in ast.walk(node):
                if (isinstance(sub, ast.Return) and isinstance(sub.value, ast.Constant)
                        and sub.value.value == 2):
                    hits.append(sub.lineno)
    return hits


def tier2_static(regs):
    # the instrument must see an exit-2 refusal, or a clean pass means nothing
    check(exits_two("import sys\nsys.exit(2)\n") == [2], "sanity: sys.exit(2) not seen")
    check(exits_two("def main():\n    return 2\n") == [2], "sanity: main return 2 not seen")
    check(exits_two("# exit(2) in a comment\nx = 'exit(2)'\n") == [], "sanity: text read as exit")
    for event, _matcher, cmd, script in regs:
        if not script or event not in BLOCKING or not MUTE.search(cmd):
            continue
        path = os.path.join(HERE, script)
        check(os.path.exists(path), "%s registered but %s is missing" % (event, path))
        if not os.path.exists(path):
            continue
        with open(path) as f:
            lines = exits_two(f.read())
        check(not lines, "%s %s refuses by exit 2 at line(s) %s, but its registration %r "
              "mutes exit codes — refuse with a JSON decision on stdout instead"
              % (event, script, lines, cmd))


AGENT_OK = {"description": "bug fixes", "prompt": "x", "model": "sonnet",
            "subagent_type": "rm-fixer"}
# (script, tool, allow input, deny input) — stateless triggers only
REAL = [
    ("block_blanket_git_stage.py", "Bash", {"command": "echo hi"}, {"command": "git add -A"}),
    ("block_blind_scan.py", "Bash", {"command": "echo hi"},
     {"command": "grep -c Desert '/x/Saves/Ash.rws'"}),
    ("block_forged_validation.py", "Bash", {"command": "echo hi"},
     {"command": "echo '{}' > infrastructure/state/modcheck_status.json"}),
    ("block_agent_without_model.py", "Agent", AGENT_OK, dict(AGENT_OK, model="haiku")),
    ("block_agent_coded_name.py", "Agent", AGENT_OK, dict(AGENT_OK, description="C6")),
    ("block_unbounded_agent.py", "Agent", AGENT_OK, dict(AGENT_OK, subagent_type="general-purpose")),
]


def tier3_real(regs):
    by_script = {}
    for event, matcher, cmd, script in regs:
        if event == "PreToolUse" and script:
            by_script.setdefault(script, []).append((matcher, cmd))
    for script, tool, ok_in, bad_in in REAL:
        cmds = [c for m, c in by_script.get(script, []) if re.fullmatch(m or ".*", tool)]
        check(cmds, "%s is not registered for PreToolUse %s" % (script, tool))
        for cmd in cmds:
            rc, out = run(cmd, payload_for("PreToolUse", tool, ok_in), REPO)
            check(rc == 0 and not blocked(rc, out), "%s: allow case blocked (rc=%s) %s" % (script, rc, out[:200]))
            rc, out = run(cmd, payload_for("PreToolUse", tool, bad_in), REPO)
            check(blocked(rc, out), "%s: deny case NOT blocked through %r (rc=%s)" % (script, cmd, rc))


def main():
    regs = registrations()
    check(len(regs) > 5, "sanity: only %d registrations read from %s" % (len(regs), SETTINGS))
    tier1_stubs(regs)
    tier2_static(regs)
    tier3_real(regs)
    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    print("PASS selftest_hook_registrations_refuse: %d registrations, muted refusals none"
          % len(regs))
    return 0


if __name__ == "__main__":
    sys.exit(main())

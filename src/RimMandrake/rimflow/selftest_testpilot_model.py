#!/usr/bin/env python3
"""Selftest: the Test Pilot runs on Fable 5.2 (owner 2026-11-16 10:13 PM: "Test Pilot should also run as Fable 5.2 when it's
called. For obvious reasons. And it should get that same inspirational prompting we worked out, just with a live game flare").

The tier is the `model:` line of .claude/agents/rm-testpilot.md. `--model` beats that line, so a launcher must pass the
pilot's own model (run_store.pilot_model), and the bare CLI alias "fable" resolves to Fable 5.1, so the tier becomes an id
through the environment first, then detached_helper.MODEL_IDS. A builder keeps run_rules.json's model.

    python3 src/RimMandrake/rimflow/selftest_testpilot_model.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import detached_helper                                  # noqa: E402
import run_store                                        # noqa: E402
from rimflow import testpilot_route as TR               # noqa: E402

PASS, FAIL = [], []
AGENT = os.path.join(ROOT, ".claude", "agents", "rm-testpilot.md")
POLICY = os.path.join(ROOT, "infrastructure", "agents", "Agent_Policy.md")


def _agent():
    with open(AGENT, encoding="utf-8") as f:
        return f.read()


def t_agent_file_is_fable():
    head = _agent().split("\n---", 1)[0]
    assert "\nmodel: fable\n" in head + "\n", "rm-testpilot.md frontmatter must say `model: fable`"
    assert detached_helper.MODEL_IDS.get("fable") == "claude-fable-5-2", "the fable tier no longer maps to Fable 5.2"


def t_pilot_model_reads_the_tier_and_maps_it():
    got = run_store.pilot_model(ROOT, "rm-testpilot", "opus", env={})
    assert got == "claude-fable-5-2", "pilot_model gave %r, not Fable 5.2" % got


def t_environment_names_the_id_first():
    env = {"ANTHROPIC_DEFAULT_FABLE_MODEL": "fable-from-env[1m]"}
    got = run_store.pilot_model(ROOT, "rm-testpilot", "opus", env=env)
    assert got == "fable-from-env", "the environment's id (less [1m]) must win, got %r" % got


def t_no_agent_file_or_line_keeps_the_default():
    d = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(d, ".claude", "agents"))
        with open(os.path.join(d, ".claude", "agents", "x_nomodel.md"), "w") as f:
            f.write("---\nname: x_nomodel\ndescription: none\n---\nbody model: fable\n")
        assert run_store.pilot_model(d, "x_nomodel", "opus", env={}) == "opus", "a body line is not the frontmatter"
        assert run_store.pilot_model(d, "x_absent_agent", "opus", env={}) == "opus", "no file anywhere: the default"
    finally:
        shutil.rmtree(d)


def t_pilot_brief_names_fable_and_holds_before_surprise():
    v = {"id": "X_ITEM", "kind": "streak", "why": "3 non-pass runs in a row"}
    for host in TR.HOSTS:
        b = TR.brief(v, host)
        assert 'model "fable"' in b.splitlines()[0], "%s: the spawn line must name the fable tier" % host
        assert b.index(TR.HOLDS) < b.index(TR.POSITIVE_STEPS) < b.index(TR.SURPRISE), "%s: holds lead the brief" % host
        for want in ("Hunt parameter regimes and regions, not examples.", "You may not end with open cases.",
                     "game_instance.py status", "FIRST exception", "Never judge a mechanic on a site that switches it off"):
            assert want in b, "%s brief lacks %r" % (host, want)


def t_agent_file_holds_the_same_steps():
    a = _agent()
    assert a.index("## How a sitting holds") < a.index(TR.SURPRISE), "the holds section leads the agent file"
    assert TR.POSITIVE_STEPS in a.replace("\n", " ") or TR.POSITIVE_STEPS in a, "the positive steps, verbatim"
    for want in ("Hunt parameter regimes and regions, not examples.", "You may not end with open cases.",
                 "With the live game:", "game_instance.py status"):
        assert want in a, "rm-testpilot.md lacks %r" % want


def t_policy_records_the_exception_once():
    with open(POLICY, encoding="utf-8") as f:
        p = f.read()
    assert "Test Pilot should also run as Fable 5.2 when it's called." in p, "Agent_Policy.md must quote the order"
    assert "| `rm-testpilot` |" in p and "fable (the exception in the Fable row)" in p, "the helper table row"


def t_tick_pilot_model_passes_the_launch_gate():
    """RIMMANDRAKE_PASS_PILOT_ALIAS_TO_THE_LAUNCH_GATE (2026-11-21 12:43 AM PST): the tick's Test Pilot sitting on
    FlowWorks was refused at detached_helper's H4 gate, "model 'claude-fable-5-2' is not one of fable, opus, sonnet",
    and the mod paused. The tick must hand the helper the alias, and the helper must launch it as Fable 5.2."""
    import maturation_autonomy as AUT
    for env in ({}, {"ANTHROPIC_DEFAULT_FABLE_MODEL": "claude-fable-5-2"}):
        was = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("ANTHROPIC_DEFAULT_")}
        os.environ.update(env)
        try:
            got = AUT.pilot_run_model(ROOT, "opus")
        finally:
            for k in env:
                os.environ.pop(k, None)
            os.environ.update(was)
        assert got in detached_helper.MODELS, "the tick hands the helper %r, which its H4 gate refuses (env %s)" % (
            got, sorted(env))
        assert detached_helper.MODEL_IDS.get(got, got) == "claude-fable-5-2", "the helper launches %r, not Fable 5.2" % (
            detached_helper.MODEL_IDS.get(got, got))


CASES = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]

if __name__ == "__main__":
    for fn in CASES:
        try:
            fn(); PASS.append(fn.__name__); print("ok    " + fn.__name__)
        except (AssertionError, ValueError) as e:
            FAIL.append(fn.__name__); print("FAIL  %s\n        %s" % (fn.__name__, e))
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)

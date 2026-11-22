#!/usr/bin/env python3
"""selftest_run_spend_and_model_alias.py: the promises of design/specs/2026-11-22-run-spend-and-model-alias/boundary.md.

One home in role_launch for what a run spent and in which unit (stored_unit, tokens_v2, run_spend) and for which model
an alias means (MODEL_VARS, resolve_model, TIERS, tier, launch_model). Fixtures only: every test sets the model
variables itself and points role_launch.SETTINGS at a temp file, so the machine's environment decides nothing.
    python3 src/RimMandrake/rimflow/selftest_run_spend_and_model_alias.py
"""
import contextlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "..")]
import role_launch as RL  # noqa: E402
import maturation as M  # noqa: E402
import mod_model as MM  # noqa: E402

FAILS = []
FABLE = "ANTHROPIC_DEFAULT_FABLE_MODEL"


def check(ok, what, got=None):
    if not ok:
        FAILS.append(what)
        print("FAIL %s%s" % (what, "" if got is None else " (got %r)" % (got,)))


@contextlib.contextmanager
def models(env=None, settings=None):
    """The model variables are exactly `env` (os.environ) and `settings` (SETTINGS' env block), then put back."""
    saved = {k: os.environ.pop(k) for k in list(RL.MODEL_VARS.values()) if k in os.environ}
    old_settings = RL.SETTINGS
    d = tempfile.mkdtemp(prefix="rsma_")
    RL.SETTINGS = os.path.join(d, "settings.json")
    with open(RL.SETTINGS, "w") as f:
        json.dump({"env": settings or {}}, f)
    os.environ.update(env or {})
    try:
        yield
    finally:
        for k in RL.MODEL_VARS.values():
            os.environ.pop(k, None)
        os.environ.update(saved)
        RL.SETTINGS = old_settings


def raised(f, *a):
    try:
        f(*a)
    except RL.UnknownModel as e:
        return str(e)
    return None


def t_one_unit_reader():
    cases = [({"token_unit": "weighted_v2"}, "weighted_v2"), ({"token_unit": "weighted_v1"}, "weighted_v1"),
             ({"token_unit": "unstated"}, "unstated"), ({}, "weighted_v1"), ({"token_unit": " "}, "weighted_v1"),
             ({"token_unit": None, "at": "2026-11-20T10:00:00-08:00"}, "weighted_v1"), (None, "weighted_v1")]
    for rec, want in cases:
        check(RL.stored_unit(rec) == want, "stored_unit(%r) is %s" % (rec, want), RL.stored_unit(rec))
        if isinstance(rec, dict):
            check(M.row_unit(rec) == want, "maturation.row_unit(%r) reads stored_unit: %s" % (rec, want), M.row_unit(rec))
    for gone in ("V2_SWITCH", "_unit_by_time", "V1_UNIT"):
        check(not hasattr(M, gone), "no reader decides a unit by time: maturation.%s is gone" % gone)


def t_one_weigher():
    fable_v1 = {"tokens": 1000, "model": "claude-fable-5-2", "at": "2026-11-15T10:00:00Z", "budget": 5}
    check(RL.tokens_v2(dict(fable_v1)) == (2000, "v1_bound"), "an unstamped Fable figure converts to its v2 bound",
          RL.tokens_v2(dict(fable_v1)))
    check(RL.run_spend(dict(fable_v1)) == 2000, "run_spend is the tokens_v2 figure", RL.run_spend(dict(fable_v1)))
    v2 = {"tokens": 1234, "token_unit": "weighted_v2"}
    check(RL.tokens_v2(v2) == (1234, "v2") and RL.run_spend(dict(v2, budget=9)) == 1234,
          "a weighted_v2 figure is taken as it is, with no model needed")
    mu = {"claude-opus-5-5": {"inputTokens": 1000, "cacheCreationInputTokens": 0, "cacheReadInputTokens": 0,
                              "outputTokens": 0}}
    check(RL.tokens_v2({"tokens": 7, "token_unit": "weighted_v1", "model_usage": mu}) == (1000, "v1_usage"),
          "a weighted_v1 record with its usage is recomputed from it")
    check(RL.tokens_v2({"tokens": 9, "token_unit": "unstated"}) == (None, "unit unstated"),
          "a unit it cannot convert reads None and names the unit")


def t_unmeasured_counts_its_budget_never_zero():
    check(RL.run_spend({"tokens": None, "budget": 450}) == 450, "no figure counts its budget")
    unk = {"tokens": 10, "token_unit": "weighted_v1", "model": "claude-nonesuch-9-9", "budget": 777}
    check(RL.run_spend(dict(unk)) == 777, "a model it cannot price counts its budget, never the bare figure or 0",
          RL.run_spend(dict(unk)))
    msg = raised(RL.tokens_v2, dict(unk))
    check(msg is not None and "claude-nonesuch-9-9" in msg, "tokens_v2 raises UnknownModel naming the model", msg)
    check(RL.run_spend({"tokens": 9, "token_unit": "unstated", "budget": 33}) == 33, "an unconvertible unit counts its budget")
    with models():
        check(RL.run_spend({"tokens": 50, "model": "opus", "budget": 60}) == 60,
              "an alias whose variable is unset is UNMEASURED: its budget")


def t_a_run_row_takes_its_run_unit():
    import maturation_now as MN
    now = 1795400000.0
    base = {"unit": "u1", "item": "I", "model": "opus", "at": now - 900, "ended": now - 100, "status": "finished",
            "result": "success (exited 0)", "tokens": 500, "out": "/nonexistent"}
    stub = (lambda rec: ("UNMEASURED", None, "UNMEASURED"))
    v_new = MN.run_view(dict(base, token_unit="weighted_v2"), now, spend=stub)
    v_old = MN.run_view(dict(base), now, spend=stub)
    check(v_new.get("token_unit") == "weighted_v2", "the run view carries its record's token_unit", v_new.get("token_unit"))
    check(M._spend_row(v_new, ["blind_challenge"])["token_unit"] == "weighted_v2", "a run row takes its run's unit")
    check(M._spend_row(v_old, ["blind_challenge"])["token_unit"] == "weighted_v1",
          "a run record with no unit gives weighted_v1, whatever its end time")
    check(M._spend_row(v_new, ["blind_challenge"]).get("model") == "opus", "a run row names its run's model")


def t_every_committed_row_is_stamped():
    files = subprocess.run(["git", "-C", ROOT, "ls-files", "*version/run_spend.jsonl", "*version/stage_record.json"],
                           capture_output=True, text=True).stdout.split()
    check(files, "the census sees committed spend files", files)
    bad, n = [], 0
    for f in files:
        p = os.path.join(ROOT, f)
        rows = ([json.loads(x) for x in open(p) if x.strip()] if f.endswith(".jsonl")
                else json.load(open(p)).get("spend") or [])
        for x in rows:
            n += 1
            if not (isinstance(x.get("token_unit"), str) and x["token_unit"].strip()):
                bad.append(f)
    check(n > 0 and not bad, "every committed spend row carries a token_unit (%d rows)" % n, sorted(set(bad))[:5])


def t_one_alias_table():
    check(set(RL.MODEL_VARS) == {"fable", "opus", "sonnet", "haiku"}, "MODEL_VARS names the four aliases",
          sorted(RL.MODEL_VARS))
    check(RL.MODEL_VARS["fable"] == FABLE, "fable's variable is %s" % FABLE)
    with models({FABLE: "claude-fable-5-2"}):
        a, b = RL.resolve_model("fable"), MM.pin_id("fable")
        check(a == b == "claude-fable-5-2", "resolve_model('fable') and pin_id('fable') read the same variable", (a, b))
    with models({FABLE: "us.anthropic.claude-fable-5-2-v1:0[1m]"}):
        check(RL.resolve_model("fable") == MM.pin_id("fable") == "claude-fable-5-2",
              "a provider-prefixed id prices as its key")
    with models(settings={FABLE: "claude-fable-5-1"}):
        check(RL.resolve_model("fable") == "claude-fable-5-1", "the settings file's env names the id when the env does not")


def t_an_unset_variable_raises_by_name():
    with models():
        for f in (RL.resolve_model, RL.launch_model, MM.pin_id):
            msg = raised(f, "fable")
            check(msg is not None and FABLE in msg, "%s('fable') raises naming %s" % (f.__name__, FABLE), msg)


def t_the_cli_resolves_opus_and_sonnet():
    with models():
        check(RL.launch_model("opus") == "opus" and RL.launch_model("Sonnet") == "sonnet",
              "with no variable the CLI's own opus/sonnet alias is passed")
        check(RL.launch_model("claude-opus-5-5") == "opus", "a full id launches as its tier")
    with models({"ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-5-5", FABLE: "claude-fable-5-2"}):
        check(RL.launch_model("opus") == "claude-opus-5-5", "with the variable set its id is passed")
        for m in ("fable", "Fable", "claude-fable-5-2"):
            check(RL.launch_model(m) == "claude-fable-5-2", "%r launches as the variable's id, never the bare alias" % m,
                  RL.launch_model(m))
    with models(settings={FABLE: "claude-fable-5-2"}):
        check(RL.launch_model("fable") == "claude-fable-5-2", "the settings file names the id when the env does not")


def t_a_full_id_is_repaired_to_its_tier():
    for given, want in (("claude-fable-5-2", "fable"), ("claude-opus-5-5", "opus"), ("claude-sonnet-5-5", "sonnet"),
                        ("Opus", "opus"), ("us.anthropic.claude-opus-5-5-v1:0", "opus"), ("FABLE", "fable")):
        check(RL.tier(given) == want, "tier(%r) is %s" % (given, want), RL.tier(given))
    for given in ("haiku", "claude-haiku-5-5", "gpt-5", "fable-opus", "", None):
        check(RL.tier(given) not in RL.TIERS, "tier(%r) is no tier, so the H4 gate refuses it" % (given,), RL.tier(given))
    import detached_helper as DH
    for gone in ("MODELS", "MODEL_IDS", "model_tier"):
        check(not hasattr(DH, gone), "detached_helper holds no alias table of its own: %s is gone" % gone)


def t_haiku_is_never_a_tier():
    check("haiku" not in RL.TIERS and RL.TIERS == ("fable", "opus", "sonnet"), "TIERS is the ladder", RL.TIERS)
    with models({"ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-5-5"}):
        check(raised(MM.pin_id, "haiku") is not None, "haiku cannot pin a mod")
        check(RL.launch_model("haiku") == "haiku", "launch_model leaves a non-tier for the gate to refuse")
    check(RL.resolve_model("claude-haiku-5-5") == "claude-haiku-5-5", "a Haiku id is still priced for a record")


def t_the_pilot_reads_its_tier_once():
    import run_store as RS
    import maturation_autonomy as AUT
    d = tempfile.mkdtemp(prefix="rsma_pilot_")
    os.makedirs(os.path.join(d, ".claude", "agents"))
    for name, line in (("rm-testpilot", "model: fable"), ("x_full", "model: claude-fable-5-2"), ("x_none", "name: x")):
        with open(os.path.join(d, ".claude", "agents", name + ".md"), "w") as f:
            f.write("---\nname: %s\n%s\n---\nbody\nmodel: opus\n" % (name, line))
    check(RS.pilot_tier(d, "rm-testpilot", "opus") == "fable", "pilot_tier reads the agent file's model: line")
    check(RS.pilot_tier(d, "x_none", "opus") == "opus", "a body line is not the frontmatter: the default")
    check(RS.pilot_tier(d, "x_absent_agent_zz", "sonnet") == "sonnet", "no agent file anywhere: the default")
    check(AUT.pilot_run_model(d, "opus") == "fable", "the tick hands the helper the tier its H4 gate takes")
    import shutil
    shutil.copy(os.path.join(d, ".claude", "agents", "x_full.md"), os.path.join(d, ".claude", "agents", "rm-testpilot.md"))
    check(AUT.pilot_run_model(d, "opus") == "fable", "a full id on the line is handed over as its tier")
    check(not hasattr(RS, "pilot_model"), "run_store holds no id table of its own: pilot_model is gone")


def t_the_profile_installer_reads_the_environment():
    import install_wt_seat_profiles as W
    check(W.SEATS["BENCH"][1] == "fable", "the BENCH profile holds its tier, never a typed id", W.SEATS["BENCH"][1])
    with models({FABLE: "claude-fable-9-9"}):
        check(W.seat_model("BENCH") == "claude-fable-9-9", "BENCH's --model is read from the environment",
              W.seat_model("BENCH"))
    with models():
        msg = raised(W.seat_model, "BENCH")
        check(msg is not None and FABLE in msg, "with the variable unset the installer raises naming it", msg)
    src = open(W.__file__, encoding="utf-8").read()
    check('"claude-fable-' not in src, "no full Fable id is typed in the installer")


def main():
    tests = (t_one_unit_reader, t_one_weigher, t_unmeasured_counts_its_budget_never_zero, t_a_run_row_takes_its_run_unit,
             t_every_committed_row_is_stamped, t_one_alias_table, t_an_unset_variable_raises_by_name,
             t_the_cli_resolves_opus_and_sonnet, t_a_full_id_is_repaired_to_its_tier, t_haiku_is_never_a_tier,
             t_the_pilot_reads_its_tier_once, t_the_profile_installer_reads_the_environment)
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a crash is a FAIL with its cause, never a silent pass
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_run_spend_and_model_alias: %s" % ("all PASS (%d tests)" % len(tests) if not FAILS
                                                      else "%d FAIL" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

"""selftest_tick_names.py — every name the tick builds is valid; no filing is refused for its name.

    python3 src/RimMandrake/rimflow/selftest_tick_names.py

Page: design/specs/2026-11-20-tick-names-never-refused/boundary.md (each promise is a t_<name> below).
Item RIMMANDRAKE_FIX_TICK_NAMER_RUN_THREE_NAME_TOO_LONG: on 2026-11-20 at about 11 PM PST the tick named GimmeSomeSlack's
third road-back steward RIMMANDRAKE_ROUTE_GIMMESOMESLACK_VISIT_ONE_FAILURES_BACK_RUN_THREE (66 chars), rimflow spawn
refused it three times, and the fault loop paused the mod.
Exit 0 when every check passes; 1 otherwise (each failure named).
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CLI = os.path.join(HERE, "cli.py")

import model                        # noqa: E402
import maturation as M              # noqa: E402
import maturation_autonomy as AUT   # noqa: E402
import maturation_dispatch as MD    # noqa: E402
import run_void as RV               # noqa: E402

FAILS = []
_SLOTS = model.project_slots()
model.project_slots = lambda: _SLOTS     # one registry read: each call stats a file on the slow D: drive
LONG_MOD = "TheVeryLongestConceivableModNameForTests"       # 40 chars, past every real concept name
assert len(LONG_MOD) == 40
KINDS = ("exit_not_met", "exit_met", "ready", "hand_step", "chain", "exam_retake", "designer_locked", "stage",
         "builder_stalled", "cycle_unfinished", "some_new_kind")
NUMBERED = ("exit_not_met", "exit_met", "cycle_unfinished")
STAGED = ("ready", "hand_step", "stage")
TESTS = ("sc_walk", "sc_first_visit_slack_line_sags_under_a_pawn_and_springs_back", "x")


def check(ok, line):
    print("%s  %s" % ("PASS" if ok else "FAIL", line))
    if not ok:
        FAILS.append(line)


def mods():
    root = os.path.join(REPO, "design", "concepts")
    real = sorted(d for d in os.listdir(root) if not d.startswith((".", "_")) and os.path.isdir(os.path.join(root, d)))
    return real + [LONG_MOD]


def nword(n):
    return MD.word(n).replace("_", "")


def namers(mod):
    """-> [(key, number word or None, fn(known) -> name)] for every input the tick's namers take for `mod`."""
    out = []
    for n in range(0, 26):
        out.append((("build", mod, n), nword(n), lambda k, n=n: MD.item_id(mod, n, k)))
        out.append((("ingame", mod, n), nword(n), lambda k, n=n: MD.ingame_item_id(mod, n, k)))
        out.append((("blind", mod, n), nword(n), lambda k, n=n: MD.blind_item_id(mod, n, k)))
    for kind in KINDS:
        for stage in (M.WORDS if kind not in NUMBERED else ("in_game", "blind_challenge")):
            for n in (range(0, 26) if kind in NUMBERED else (1,)):
                row = {"mod": mod, "stage": stage, "steward_kind": kind, "visit": n, "cycle": n}
                if kind == "cycle_unfinished":      # names its cycle number at every stage
                    key = ("steward", kind, mod, n)
                elif kind in NUMBERED:
                    key = ("steward", kind, mod, stage == "in_game", n)
                elif kind in STAGED:
                    key = ("steward", kind, mod, stage)
                else:
                    key = ("steward", kind, mod)
                out.append((key, nword(n) if kind in NUMBERED else None,
                            lambda k, row=row: AUT.item_name(row, k)))
    return out


def problems(name):
    if not name:
        return ["no name"]
    p = list(model.mint_problems(name, set(), strict=False))
    w = name.split("_")
    if w[0] != "RIMMANDRAKE":
        p.append("slot 1 is not RIMMANDRAKE")
    if len(w) < model.NAME_MIN_WORDS:
        p.append("%d words" % len(w))
    return p


def t_every_tick_name_is_valid():
    bad, seen = [], 0
    for mod in mods():
        cands = namers(mod) + [(("cert", mod, t, kd), None, lambda k, t=t, kd=kd: MD.cert_item_id(mod, t, k, kd))
                               for t in TESTS for kd in ("red", "red_seen")]
        for key, _, fn in cands:
            known = set()
            for run in range(1, 21):
                name = fn(known)
                seen += 1
                p = problems(name) + (["already known"] if name in known else [])
                if key[0] == "ingame" and name and not model.RUNNER_INGAME_NAME.match(name):
                    p.append("fails RUNNER_INGAME_NAME")
                if p:
                    bad.append("%s run %d: %s (%s)" % (key, run, name, "; ".join(p)))
                    break
                known.add(name)
    check(not bad and seen > 10000, "every-tick-name-is-valid: %d names over %d mods, runs 1 to 20, %d bad%s" % (
        seen, len(mods()), len(bad), (": " + " | ".join(bad[:4])) if bad else ""))


def t_distinct_work_gets_distinct_names():
    by_name, clash, lost = {}, [], []
    for mod in mods():
        for key, num, fn in namers(mod):
            name = fn(set())
            if name in by_name and by_name[name] != key:
                clash.append("%s and %s -> %s" % (by_name[name], key, name))
            by_name.setdefault(name, key)
            if num and name and num not in name.split("_"):
                lost.append("%s -> %s (no %s)" % (key, name, num))
    check(not clash and not lost, "distinct-work-gets-distinct-names: %d names, %d clashes, %d lost their number%s" % (
        len(by_name), len(clash), len(lost), (": " + " | ".join((clash + lost)[:4])) if clash or lost else ""))


def t_the_run_three_name_fits():
    row = {"mod": "GimmeSomeSlack", "stage": "in_game", "visit": 1, "steward_kind": "exit_not_met"}
    base = "RIMMANDRAKE_ROUTE_GIMMESOMESLACK_VISIT_ONE_FAILURES_BACK"
    name = AUT.item_name(row, {base, base + "_RUN_TWO"})
    w = (name or "").split("_")
    check(not problems(name) and "GIMMESOMESLACK" in w and "VISIT_ONE" in (name or "") and name.endswith("_RUN_THREE"),
          "the-run-three-name-fits: GimmeSomeSlack visit 1, base and RUN_TWO taken -> %s (%s)" % (
              name, "; ".join(problems(name)) or "valid"))


# ---- the doors: rimflow file / spawn / namecheck, as real subprocesses on a throwaway ledger ------------------------

TMP = os.path.join(REPO, ".rimflow_selftest_tick_names", "run-%d" % os.getpid())
TOO_LONG = "RIMMANDRAKE_FILE_A_NAME_FAR_TOO_LONG_FOR_THE_GRAMMAR_CAP_OF_SIXTY_FOUR_CHARS"


def env():
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID") and not k.startswith("GIT_")}
    e.update(RIMFLOW_LEDGER=os.path.join(TMP, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(TMP, "items"),
             RIMFLOW_PROBE="no-reading", RIMFLOW_SCHEDULE=os.path.join(TMP, "no_schedule.json"),
             RIMFLOW_DRIVER_LOCK="", RM_HOST="archmagi", 
             RIMFLOW_BRIDGE_LOCK=os.path.join(TMP, "bridge.lock"), RIMFLOW_SEAT="BUILD")
    return e


def run(*args):
    p = subprocess.run([sys.executable, CLI] + list(args), capture_output=True, text=True, env=env(), cwd=REPO,
                       timeout=120)
    return p.returncode, p.stdout, p.stderr


def ledger_text():
    out = []
    for dp, _, fs in os.walk(TMP):
        for f in fs:
            if f.endswith(".jsonl"):
                with open(os.path.join(dp, f), encoding="utf-8") as fh:
                    out.append(fh.read())
    return "\n".join(out)


def fresh():
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(os.path.join(TMP, "items"), exist_ok=True)


def t_a_bad_name_files_with_a_warning():
    fresh()
    rc1, out1, err1 = run("file", TOO_LONG, "--for", "BUILD", "--title", "t")
    rc0, _, err0 = run("file", "RIMMANDRAKE_SEED_NAME_CAUSE_FIXTURE", "--for", "BUILD", "--title", "t")
    spawned = TOO_LONG + "_SPAWNED"
    rc2, out2, err2 = run("spawn", "--from", "RIMMANDRAKE_SEED_NAME_CAUSE_FIXTURE", "--for", "BUILD", "--name", spawned,
                          "--title", "t")
    led = ledger_text()
    check(rc1 == 0 and rc2 == 0 and rc0 == 0 and "NAME NOTE:" in out1 and "too long" in out1 and "NAME NOTE:" in out2
          and TOO_LONG in led and spawned in led and led.count('"name_note"') >= 2,
          "a-bad-name-files-with-a-warning: file exit %d, spawn exit %d, NAME NOTE in both %s, name_note on %d events%s"
          % (rc1, rc2, "NAME NOTE:" in out1 and "NAME NOTE:" in out2, led.count('"name_note"'),
             "" if rc1 == 0 and rc2 == 0 else " (stderr: %s | %s)" % (err1.strip()[-200:], err2.strip()[-200:])))


def t_only_identity_refuses():
    fresh()
    run("file", "RIMMANDRAKE_SEED_NAME_TWICE_FIXTURE", "--for", "BUILD", "--title", "t")
    rc1, _, e1 = run("file", "RIMMANDRAKE_SEED_NAME_TWICE_FIXTURE", "--for", "BUILD", "--title", "t")
    rc2, _, e2 = run("file", "rimmandrake_lower_case_name_fixture", "--for", "BUILD", "--title", "t")
    rc3, _, e3 = run("spawn", "--from", "RIMMANDRAKE_SEED_NAME_TWICE_FIXTURE", "--for", "BUILD",
                     "--name", "RIMMANDRAKE_SEED_NAME_TWICE_FIXTURE", "--title", "t")
    check(rc1 != 0 and "already exists" in e1 and rc2 != 0 and "UPPER_SNAKE" in e2 and rc3 != 0
          and "already exists" in e3,
          "only-identity-refuses: a second file of one id exit %d, a lower-case id exit %d, a spawn onto an existing id "
          "exit %d" % (rc1, rc2, rc3))


def t_namecheck_stays_advisory():
    fresh()
    rc, out, _ = run("namecheck", TOO_LONG)
    check(rc == 1 and "REFUSED:" in out, "namecheck-stays-advisory: namecheck of a too-long name exit %d, REFUSED %s"
          % (rc, "REFUSED:" in out))


def t_a_name_refusal_is_no_fault():
    name = "RIMMANDRAKE_ROUTE_FAKEFLOW_VISIT_ONE_FAILURES_BACK_RUN_THREE_AND_MORE"
    refusal = ("spawn refused: rimflow: %s is not a new-style item name:\n  - 69 chars; too long, the cap is 64" % name)
    cfg = {"launch_tries": 3, "_code": "c1", "seat": "BENCH"}
    st = {"mods": {"FakeFlow": {}}}
    s = st["mods"]["FakeFlow"]
    rows, now = [], 1795300000
    for i in range(3):
        x = (s.get("steward") or {}).get("k1")
        row = {"mod": "FakeFlow", "aut": "steward", "steward_key": "k1", "steward_kind": "exit_not_met",
               "stage": "in_game", "visit": 1, "cap": 10, **({"retry_of": x} if x else {})}
        AUT.execute("/nonexistent", cfg, st, [row], ["FakeFlow"], now + i * 60,
                    {"known": lambda: set(), "file": lambda *a, **k: (False, refusal),
                     "launch_brief": lambda *a, **k: (1, "never called", None)})
        RV.sync_system(st, lambda u: None, keep_failed=lambda b, x: MD.still_retried(cfg, b, x, "FakeFlow"),
                       now=now + i * 60 + 1)
        rows.append(row)
    x = (s.get("steward") or {}).get("k1") or {}
    # the in-game path files through launch_counted
    ok, item, unit, text, entry = MD.launch_counted(
        cfg, {}, {"cap": 1}, now, "ingame_auto", {"visit": 1}, lambda: name, lambda it: (False, refusal),
        lambda it: (0, "", None), lambda it: (1, "never", None))
    check(RV.faults(s) == 0 and rows[-1].get("decision") == "launch_wait" and int(x.get("tries") or 0) <= 1
          and entry.get("wait") and MD.retriable(cfg, entry, mod="FakeFlow"),
          "a-name-refusal-is-no-fault: three steward filings refused for the tick's own name: faults %d, decision %s, "
          "tries %s; the in-game entry a wait %s" % (RV.faults(s), rows[-1].get("decision"), x.get("tries"),
                                                     bool(entry.get("wait"))))


def main():
    tests = (t_every_tick_name_is_valid, t_distinct_work_gets_distinct_names, t_the_run_three_name_fits,
             t_a_bad_name_files_with_a_warning, t_only_identity_refuses, t_namecheck_stays_advisory,
             t_a_name_refusal_is_no_fault)
    try:
        for t in tests:
            try:
                t()
            except Exception as e:      # a crash is a failure of that check, named
                check(False, "%s crashed: %s: %s" % (t.__name__[2:], type(e).__name__, e))
    finally:
        shutil.rmtree(os.path.dirname(TMP), ignore_errors=True)
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

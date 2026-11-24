#!/usr/bin/env python3
"""The one home of the numbers that every time budget in pipeline machinery is held to (time_budget_lint.py checks them).

A time budget is a number that ends, skips, defers or fails work because time passed. It detects an out-of-control or
stuck program, and nothing else (owner, 2026-11-24: "Aren't time budgets for detecting out-of-control or stuck
programs?"). A class names its danger and its longest real run once. A call that belongs to a class says so beside its
number, or takes the number from here:

    subprocess.run(argv, timeout=1800)      # budget: class=call
    subprocess.run(argv, timeout=time_budget.CALL_S)

Page: design/specs/2026-11-24-time-budgets/boundary.md (LIMITS).
"""
FACTOR = 10     # a budget is at least this many times the longest real run of the work that it guards. The one constant.

CLASSES = {
    "call": {
        "s": 1800, "longest_s": 4,
        "danger": "a hung local command (git, systemctl, one small tool) holds its caller with no end",
        "evidence": "a robocopy on its default retries held a seat 4 h (2026-11-02)",
        "record": "225 git calls of 9 kinds sampled at load 20 to 52 (2026-11-24): a path log 3.8 s, a fetch 3.7 s, the rest under 1 s"},
    "publish": {
        "s": 21600, "longest_s": 584,
        "danger": "a hung ./publish or land.sh holds its caller with no end",
        "evidence": "none of a hang; callers of 120 to 900 s could cut a live publish inside its checks",
        "record": "the longest door-check wall of 636 publishes (agent transcripts, 14 days to 2026-11-24); each check "
                  "then had a deadline of 180 s, so a publish on a loaded machine can now take longer"},
    "deploy": {
        "s": 10800, "longest_s": 998,
        "danger": "a hung deploy holds its caller and the game copy with no end",
        "evidence": "a hung robocopy held a seat 4 h (2026-11-02)",
        "record": "the whole Dispatch tick that ran a biomes deploy (user journal, 14 days to 2026-11-24): an upper bound"},
    "launch": {
        "s": 10800, "longest_s": 896,
        "danger": "a hung launch (its clone, its sync, its checks) holds the tick with no end",
        "evidence": "none measured; a launch that a deadline cut leaves a half-made clone (selftest_take_clone_half_made.py)",
        "record": "the longest whole rm-list-dispatch run (user journal, 14 days to 2026-11-24): an upper bound"},
    "rimflow": {
        "s": 300, "longest_s": 28.3,
        "danger": "a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end",
        "evidence": "none measured of a hang; 10 to 28 s for one note at load 20 to 45 (2026-11-24)",
        "record": "the longest of 489 note steps of the Dispatcher's tick (tick_steps.jsonl, 2026-11-16 to 2026-11-24); one "
                  "step wrote 1 note; a note writes its event and lands nothing, and a replay reads the same ledger"},
    "judge": {
        "s": 5400, "longest_s": 462,
        "danger": "a judge (LLM) call that never returns holds its caller with no end",
        "evidence": "none measured",
        "record": "the longest COVERAGE JUDGE session (2 sessions; 119 calibration cases took 166 s at most and 100 art cases "
                  "134 s: agent transcripts, first to last line, 14 days to 2026-11-24)"},
}
CALL_S = CLASSES["call"]["s"]
PUBLISH_S = CLASSES["publish"]["s"]
DEPLOY_S = CLASSES["deploy"]["s"]
LAUNCH_S = CLASSES["launch"]["s"]
RIMFLOW_S = CLASSES["rimflow"]["s"]
JUDGE_S = CLASSES["judge"]["s"]

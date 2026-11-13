#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_EXTEND_PREFLIGHT_CORE_KINDS_IDS_SHAS_FULL_REASON (spec:
design/specs/2026-11-12-ticket-preflight-before-any-token.md, section 7 ticket 2). Written by the filing seat; the
builder does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/preflight_core_accept.py       # exit 0 and "PASS 37/37" when built

THE CONTRACT: ticket 1's `ticket_preflight.run_text` (see preflight_spine_accept.py), extended with
    kind="task", needs="offline"   the item's ledger fields (E12 reads them)
    items=None    {id: {"state": "open"|"closed"|"dropped"|"superseded", "successor": id|None}} or a callable
                  (None: the ledger replay)
    repo=None     the git checkout sha checks run in (None: this repo); "landed" = an ancestor of its HEAD
  New `## refs` keys: race:, pawnkind:, biome:, item:, sha:, full-why:, new-def:, none:. A line ending `(auto)` is a
  tool's guess: its observations carry "origin": "auto" (declared lines "declared").
  Checks: E11 strict parse (unknown key names the nearest valid key; two tiers and a def both def: and new-def: name
  both line numbers), B6 kinds, B10 item ids (a superseded id names its successor), B11 shas, C4 Full Mod reason
  (asked by `tier: full` or a GREEN-FULL criterion; the five reasons of spec 2.1; `explicit:` must name a real id),
  E12 declared block present for build, fix and live tickets (spec section 2, E12).
  `rimflow preflight --sweep --json` runs every open ticket once inside the 30 s hard stop, one timing line each, and
  reports `task_with_verify` (open `task` tickets with a `## verify` command: the gap E12 cannot see).
"""
import glob
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
sys.path.insert(0, RIMFLOW)
CLI = os.path.join(RIMFLOW, "cli.py")
TOTAL = 37
RESULTS = []


def check(ok, what):
    RESULTS.append((bool(ok), what))
    print(("ok    " if ok else "FAIL  ") + what)


PATHS = ["src/A/real.py"]
DEFS = {"capture": "T", "mods": ["pkg.a", "pkg.b"],
        "defs": [["ThingDef", "RM_OnList", 1, "pkg.a"], ["PawnKindDef", "RM_Kind", 3, "pkg.a"],
                 ["BiomeDef", "RM_Biome", 4, "pkg.a"]]}
SRC = {}
TIERS = {"small": ["pkg.a"], "wide": ["pkg.a", "pkg.b"], "full": ["pkg.a", "pkg.b"]}
ITEMS = {"OPEN_ONE": {"state": "open", "successor": None},
         "GONE_ONE": {"state": "superseded", "successor": "NEW_ONE"},
         "NEW_ONE": {"state": "open", "successor": None}}


def refs(*lines, criteria=""):
    body = "## spec\nA ticket.\n\n## refs\n" + "\n".join(lines) + "\n"
    return body + ("\n## criteria\n" + criteria + "\n" if criteria else "")


def obs(rep, cid, ref=None):
    return [c for c in rep["checks"] if c["id"] == cid and (ref is None or c.get("ref") == ref)]


def status(rep, cid, ref=None):
    return {c["status"] for c in obs(rep, cid, ref)}


def text_of(cs):
    return " ".join((c.get("evidence") or "") + " " + (c.get("fix") or "") for c in cs)


def git(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True, check=True, timeout=60).stdout.strip()


def main():
    try:
        import ticket_preflight as TP
    except Exception as e:
        print("FAIL  import ticket_preflight: %s: %s" % (type(e).__name__, e))
        print("PASS 0/%d" % TOTAL)
        return 1
    tmp = tempfile.mkdtemp(prefix="preflight_core_")
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        git(repo, "config", k, v)
    open(os.path.join(repo, "a"), "w").write("a")
    git(repo, "add", "a")
    git(repo, "commit", "-qm", "A")
    sha_a = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-qb", "side")
    open(os.path.join(repo, "b"), "w").write("b")
    git(repo, "add", "b")
    git(repo, "commit", "-qm", "B")
    sha_b = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "main")

    def run(text, proof_text="", **kw):
        for k, v in (("paths", PATHS), ("defs", DEFS), ("src", SRC), ("tiers", TIERS), ("items", ITEMS),
                     ("repo", repo), ("runs_path", os.path.join(tmp, "runs.jsonl"))):
            kw.setdefault(k, v)
        return TP.run_text(text, proof_text, **kw)

    cases = []

    def case(fn):
        cases.append(fn)
        return fn

    @case
    def strict_parse():
        r = run(refs("dfe: RM_OnList"))
        e = obs(r, "E11")
        check(e and e[0]["status"] == "FAIL" and "def" in text_of(e), "E11 an unknown key FAILs naming the nearest key")
        r = run(refs("file: src/A/real.py", "def ThingDef/RM_OnList"))
        check(status(r, "E11") == {"FAIL"} and "2" in text_of(obs(r, "E11")), "E11 a line with no key FAILs naming its line")
        r = run(refs("tier: small", "file: src/A/real.py", "tier: wide"))
        t = text_of(obs(r, "E11"))
        check(status(r, "E11") == {"FAIL"} and "1" in t and "3" in t, "E11 two tiers FAIL naming both lines")
        r = run(refs("def: RM_OnList", "new-def: ThingDef/RM_OnList"))
        check(status(r, "E11") == {"FAIL"}, "E11 one def both existing and to-be-made FAILs")
        r = run(refs("file: src/A/real.py", "def: RM_OnList", "tier: small", "item: OPEN_ONE"))
        check("FAIL" not in status(r, "E11"), "E11 a clean block does not FAIL")
        r = run(refs("file: src/A/missing.py (auto)", "file: src/A/real.py"))
        o = {c.get("ref"): c.get("origin") for c in obs(r, "B1")}
        check(o.get("src/A/missing.py") == "auto" and o.get("src/A/real.py") == "declared",
              "an (auto) line is origin auto, a plain line origin declared")

    @case
    def kinds():
        for line, ref, want, what in (("race: RM_Kind", "RM_Kind", {"FAIL"}, "race: on a PawnKindDef FAILs"),
                                      ("pawnkind: RM_Kind", "RM_Kind", {"PASS"}, "pawnkind: on a PawnKindDef PASSes"),
                                      ("biome: RM_OnList", "RM_OnList", {"FAIL"}, "biome: on a ThingDef FAILs"),
                                      ("race: RM_OnList", "RM_OnList", None, "race: on a ThingDef with no race data is not FAIL"),
                                      ("biome: RM_Biome", "RM_Biome", {"PASS"}, "biome: on a BiomeDef PASSes")):
            got = status(run(refs(line)), "B6", ref)
            check(got == want if want else (got and "FAIL" not in got), "B6 " + what)

    @case
    def item_ids():
        r = run(refs("item: OPEN_ONE", "item: GONE_ONE", "item: NO_SUCH_ITEM"))
        check(status(r, "B10", "OPEN_ONE") == {"PASS"}, "B10 an open item PASSes")
        g = obs(r, "B10", "GONE_ONE")
        check(g and g[0]["status"] == "FAIL" and "NEW_ONE" in text_of(g), "B10 a superseded item FAILs naming its successor")
        check(status(r, "B10", "NO_SUCH_ITEM") == {"FAIL"}, "B10 an unknown item FAILs")

    @case
    def shas():
        r = run(refs("sha: " + sha_a, "sha: " + sha_a[:10], "sha: " + sha_b, "sha: deadbeef12"))
        check(status(r, "B11", sha_a) == {"PASS"}, "B11 a landed full sha PASSes")
        check(status(r, "B11", sha_a[:10]) == {"PASS"}, "B11 a landed short sha PASSes")
        b = obs(r, "B11", sha_b)
        check(b and b[0]["status"] == "FAIL" and ("ancestor" in text_of(b).lower() or "landed" in text_of(b).lower()),
              "B11 a commit that never landed FAILs saying so")
        d = obs(r, "B11", "deadbeef12")
        check(d and d[0]["status"] == "FAIL" and "resolve" in text_of(d).lower(), "B11 an unknown sha FAILs: does not resolve")

    @case
    def full_reason():
        r = run(refs("tier: full", "def: RM_OnList"))
        c = obs(r, "C4")
        check(c and c[0]["status"] == "FAIL" and ("live-mods:" in text_of(c) or "tier:" in text_of(c)),
              "C4 Full with no reason FAILs and prints a candidate list")
        r = run(refs("tier: full", "full-why: performance: tick cost only shows at 300 mods"))
        check(status(r, "C4") == {"PASS"}, "C4 an allowed reason PASSes")
        r = run(refs("tier: full", "full-why: because I said so"))
        check(status(r, "C4") == {"FAIL"}, "C4 a reason outside the five FAILs")
        r = run(refs("tier: full", "full-why: explicit: NO_SUCH_EVENT"))
        check(status(r, "C4") == {"FAIL"}, "C4 explicit: naming no real id FAILs")
        r = run(refs("tier: full", "full-why: explicit: OPEN_ONE"))
        check(status(r, "C4") == {"PASS"}, "C4 explicit: naming a real id PASSes")
        r = run(refs("def: RM_OnList", criteria="- A1 (GREEN-FULL): the whole list loads clean"))
        check(status(r, "C4") == {"FAIL"}, "C4 a GREEN-FULL criterion with no reason FAILs")
        r = run(refs("tier: small", "def: RM_OnList"))
        check("FAIL" not in status(r, "C4"), "C4 a small tier owes no reason")

    @case
    def declared_block():
        r = run("## spec\nBuild the thing.\n", kind="build")
        e = obs(r, "E12")
        check(e and e[0]["status"] == "FAIL" and e[0].get("fix"), "E12 a build ticket with no refs FAILs with a block to paste")
        r = run(refs("file: src/A/real.py (auto)"), kind="fix")
        check(status(r, "E12") == {"FAIL"}, "E12 a fix ticket with only (auto) lines FAILs")
        r = run("## spec\nLook at it live.\n", kind="task", needs="bridge")
        check(status(r, "E12") == {"FAIL"}, "E12 a needs: bridge ticket with no refs FAILs")
        r = run("## spec\nA chore.\n", proof_text="live-proof A1: python3 x.py\n", kind="task")
        check(status(r, "E12") == {"FAIL"}, "E12 a ticket with a live-proof file and no refs FAILs")
        r = run("## spec\nA chore.\n", kind="task", needs="offline")
        check("FAIL" not in status(r, "E12"), "E12 an offline task with no proof file is not FAILed")
        r = run(refs("none: a pure rename inside one function, names nothing"), kind="bug")
        check(status(r, "E12") == {"PASS"}, "E12 a none: <why> line PASSes")
        r = run(refs("file: src/A/real.py"), kind="build")
        check(status(r, "E12") == {"PASS"}, "E12 one confirmed line PASSes")
        r = run(refs("none:"), kind="build")
        check(status(r, "E12") == {"FAIL"} or status(r, "E11") == {"FAIL"}, "E12/E11 a none: with no reason is not a pass")

    @case
    def sweep():
        runs = os.path.join(tmp, "sweep_runs.jsonl")
        env = dict(os.environ, RIMFLOW_PREFLIGHT_RUNS=runs)
        t = time.monotonic()
        p = subprocess.run([sys.executable, CLI, "preflight", "--sweep", "--json"], cwd=REPO, env=env,
                           capture_output=True, text=True, timeout=120)
        wall = time.monotonic() - t
        try:
            rep = json.loads(p.stdout)
        except ValueError:
            rep = {}
        live = len(glob.glob(os.path.join(REPO, "infrastructure", "state", "items", "*.md")))
        lines = open(runs).read().splitlines() if os.path.exists(runs) else []
        check(p.returncode == 0 and wall < 30.0, "the sweep exits 0 inside the 30 s hard stop (%.1f s)" % wall)
        check(live and len(lines) >= live, "the sweep writes a timing line per open ticket (%d lines, %d prose files)"
              % (len(lines), live))
        check(isinstance(rep.get("task_with_verify"), int), "the sweep reports task_with_verify")

    @case
    def spine_still_green():
        p = subprocess.run([sys.executable, os.path.join(HERE, "preflight_spine_accept.py")], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        check(p.returncode == 0, "ticket 1's acceptance test still passes")

    for fn in cases:
        try:
            fn()
        except Exception as e:
            check(False, "%s crashed: %s: %s" % (fn.__name__, type(e).__name__, e))
    passed = sum(1 for ok, _ in RESULTS if ok)
    print("PASS %d/%d" % (passed, TOTAL))
    return 0 if passed == TOTAL and len(RESULTS) == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())

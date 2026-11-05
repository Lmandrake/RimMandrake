#!/usr/bin/env python3
"""LIVEPROOFS_WRAPPERS_EXCISE_OUT_OF_DIR: the item asked to move PLANET_ATMOSPHERE_CLOUD_COST_1_live.py/_selftest.py out of
infrastructure/state/live_proofs/ because t_proofs_file was red on them. 612416958f (NIGHTLY_REDS) instead made a proof's
own .py/.json legal there; this test proves the supersession holds, and that each part goes red when it breaks:

  1. 612416958f is an ancestor of HEAD (the ruling that legalised the wrappers is on this tree);
  2. t_proofs_file, run over a mirror of the real live_proofs, is green on the mirror and RED on each mutant:
     a stray non-proof extension, an orphan wrapper whose stem names no ledger item, an unparseable .txt line;
  3. every live-proof line of PLANET_ATMOSPHERE_CLOUD_COST_1.txt runs a wrapper that exists in live_proofs/, and the
     wrapper's own _selftest.py passes (the wrapper is a proof's working script, not a stray);
  4. no lesson or skill still tells an agent that live_proofs may hold only .txt/.criteria (the stale remedy is deleted);
  5. the item's ledger carries a note naming 612416958f as the supersession.
"""
import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import selftest_relentless_live_round as S   # noqa: E402

ITEM = "LIVEPROOFS_WRAPPERS_EXCISE_OUT_OF_DIR"
RULING = "612416958f"
PROOF = "PLANET_ATMOSPHERE_CLOUD_COST_1"
PROOFS = os.path.join(ROOT, "infrastructure", "state", "live_proofs")
FAILS = []


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def run_proofs_file(books_root):
    """t_proofs_file over books_root/infrastructure/state/live_proofs -> the names of its failed checks."""
    old_here, old_fails = S.HERE, S.FAILS[:]
    S.HERE = os.path.join(books_root, "src", "RimMandrake", "rimflow")
    del S.FAILS[:]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            S.t_proofs_file()
        return [f for f in S.FAILS if f.startswith("proofs: every real")]
    finally:
        S.HERE = old_here
        S.FAILS[:] = old_fails


def mirror(d):
    """A books tree: a copy of live_proofs (mutable) and links to the real items and ledger (read-only)."""
    st = os.path.join(d, "infrastructure", "state")
    os.makedirs(os.path.join(d, "src", "RimMandrake", "rimflow"))
    os.makedirs(st)
    shutil.copytree(PROOFS, os.path.join(st, "live_proofs"))
    for sub in ("items", "ledger"):
        os.symlink(os.path.join(ROOT, "infrastructure", "state", sub), os.path.join(st, sub))
    return os.path.join(st, "live_proofs")


def t_ruling_on_head():
    p = subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", RULING, "HEAD"], capture_output=True)
    check("ruling %s is an ancestor of HEAD" % RULING, p.returncode == 0, p.stderr.decode()[:120])


def t_rule_bites():
    mutants = {
        "stray extension": ("%s_notes.md" % PROOF, "live-proof A1: echo x\n"),
        "orphan wrapper": ("NO_SUCH_ITEM_EVER_FILED_live.py", "print(1)\n"),
        "unparseable proof line": ("%s.txt" % PROOF, "this is not a proof line\n"),
    }
    with tempfile.TemporaryDirectory() as d:
        lp = mirror(d)
        check("t_proofs_file green on the mirror of the real live_proofs (wrappers in place)",
              run_proofs_file(d) == [], str(run_proofs_file(d)))
    for what, (name, body) in mutants.items():
        with tempfile.TemporaryDirectory() as d:
            lp = mirror(d)
            with open(os.path.join(lp, name), "a", encoding="utf-8") as f:
                f.write(body)
            check("t_proofs_file RED on mutant: %s" % what, run_proofs_file(d) != [])


def t_wrappers_are_the_proofs_own():
    with open(os.path.join(PROOFS, PROOF + ".txt"), encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f if l.startswith("live-proof ")]
    named = set()
    for l in lines:
        named.update(re.findall(r"infrastructure/state/live_proofs/(\S+\.py)", l))
    check("%s.txt has live-proof lines and each runs a wrapper in live_proofs/" % PROOF,
          len(lines) >= 3 and len(named) == 1 and all(PROOF in l and ".py" in l for l in lines), str(lines[:3]))
    check("every named wrapper exists in live_proofs/", named and all(os.path.isfile(os.path.join(PROOFS, n)) for n in named),
          str(named))
    st = os.path.join(PROOFS, PROOF + "_selftest.py")
    ok = os.path.isfile(st) and any("import %s" % n[:-3] in open(st, encoding="utf-8").read() for n in named)
    check("the _selftest.py tests the named wrapper", ok)
    p = subprocess.run([sys.executable, "-B", st], capture_output=True, timeout=300, cwd=ROOT,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1")) if ok else None
    check("the wrapper's _selftest.py passes", p is not None and p.returncode == 0,
          (p.stdout + p.stderr).decode()[-200:] if p else "absent")


def t_stale_remedy_deleted():
    pat = re.compile(r"live_proofs\S*/?.{0,80}(may only hold|requires every live_proofs file be)[^.\n]{0,40}\.txt", re.I)
    hits = []
    for top in ("infrastructure/state/lessons", "skills"):
        for dp, _, fs in os.walk(os.path.join(ROOT, top)):
            for fn in fs:
                if fn.endswith(".md"):
                    with open(os.path.join(dp, fn), encoding="utf-8", errors="replace") as f:
                        if pat.search(f.read()):
                            hits.append(os.path.relpath(os.path.join(dp, fn), ROOT))
    probe = "live_proofs/ may only hold <ID>.txt and <ID>.criteria"
    check("the stale-remedy pattern can see (sanity probe)", bool(pat.search(probe)))
    check("no lesson or skill still says live_proofs may hold only .txt/.criteria", not hits, str(hits[:3]))


def t_supersession_noted():
    ev = os.path.join(ROOT, "infrastructure", "state", "ledger", "events")
    found = False
    for shard in os.listdir(ev):
        with open(os.path.join(ev, shard), encoding="utf-8") as f:
            for line in f:
                if ITEM in line and '"note"' in line and RULING in line and "SUPERSEDED" in line:
                    found = True
    check("the item's ledger carries a note naming %s as the supersession" % RULING, found)


def main():
    for t in (t_ruling_on_head, t_rule_bites, t_wrappers_are_the_proofs_own, t_stale_remedy_deleted, t_supersession_noted):
        t()
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

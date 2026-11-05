"""Mutants for prove_revert_decision.py: each must exit 1 (control exits 0). Works on a scratch copy, never the clone."""
import glob, os, re, shutil, subprocess, sys
CLONE, S = sys.argv[1], "/mnt/d/ClaudeWork/rimmandrake/scratch/clonepool_mut"
P = "infrastructure/state/evidence/clone_pool_revert_2026-11-05/prove_revert_decision.py"
LED = "infrastructure/state/" + "ledger/events"

def setup(rev):
    shutil.rmtree(S, ignore_errors=True); os.makedirs(S)
    a = subprocess.run(["git", "archive", rev, "CLAUDE.md", "src/RimMandrake/Utils/scratch_clone.py", LED], cwd=CLONE, capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", S], input=a, check=True)
    os.makedirs(os.path.dirname(os.path.join(S, P)), exist_ok=True); shutil.copy(os.path.join(CLONE, P), os.path.join(S, P))

def edit(rel, fn):
    for f in glob.glob(os.path.join(S, rel)):
        t = open(f, encoding="utf-8").read(); open(f, "w", encoding="utf-8").write(fn(t))

def drop_lines(pred):
    return lambda t: "".join(l for l in t.splitlines(True) if not pred(l))

def run(name, expect):
    r = subprocess.run([sys.executable, os.path.join(S, P)], capture_output=True, text=True)
    bad = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    ok = (r.returncode == 0) == (expect == 0)
    print("%s %-45s exit=%d %s" % ("OK " if ok else "BAD", name, r.returncode, "; ".join(b[:70] for b in bad)))

setup("2c5c2cbf"); run("M0 control at 2c5c2cbf", 0)
setup("2c5c2cbf^"); run("M1 ledger of 2c5c2cbf^ (no why-not)", 1)
setup("2c5c2cbf"); edit(LED + "/*.jsonl", lambda t: "\n".join(l.replace("RELENTLESS_CAPACITY_WIDEN_EIGHT_ON_SIXTEEN", "XX") if "REVERT NOT CARRIED OUT" in l else l for l in t.split("\n"))); run("M2 why-not loses card citation", 1)
setup("2c5c2cbf"); edit(LED + "/*.jsonl", lambda t: "\n".join(l.replace("POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG", "XX") if "REVERT NOT CARRIED OUT" in l else l for l in t.split("\n"))); run("M2b why-not loses salvage citation", 1)
setup("2c5c2cbf"); edit(LED + "/*.jsonl", drop_lines(lambda l: '"id":"POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG"' in l and '"event":"close"' in l)); run("M3 salvage close removed", 1)
setup("2c5c2cbf"); edit(LED + "/*.jsonl", drop_lines(lambda l: '"id":"RELENTLESS_CAPACITY_WIDEN_EIGHT_ON_SIXTEEN"' in l and '"event":"close"' in l)); run("M4 card ruling close removed", 1)
setup("2c5c2cbf"); edit(LED + "/*.jsonl", lambda t: "\n".join(l.replace("16 clones / 70 GB", "10 clones / 40 GB") if "RELENTLESS_CAPACITY_WIDEN_EIGHT_ON_SIXTEEN" in l else l for l in t.split("\n"))); run("M4b card says 10/40", 1)
setup("2c5c2cbf"); edit("src/RimMandrake/Utils/scratch_clone.py", lambda t: re.sub(r"^POOL_MAX_CLONES = 16", "POOL_MAX_CLONES = 10", t, flags=re.M)); run("M5 clone cap back to 10", 1)
setup("2c5c2cbf"); edit("src/RimMandrake/Utils/scratch_clone.py", lambda t: re.sub(r"^POOL_MAX_BYTES = 70 ", "POOL_MAX_BYTES = 40 ", t, flags=re.M)); run("M5b GB cap back to 40", 1)
setup("2c5c2cbf"); edit("CLAUDE.md", lambda t: t.replace("Revert if a clone strands work or the pool passes 70 GB", "x")); run("M6 revert clause gone from CLAUDE.md", 1)
setup("2c5c2cbf"); [os.remove(f) for f in glob.glob(os.path.join(S, LED, "*"))]; run("M7 empty ledger (sanity probe)", 1)
shutil.rmtree(S, ignore_errors=True)

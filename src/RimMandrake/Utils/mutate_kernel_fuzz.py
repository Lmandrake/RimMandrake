#!/usr/bin/env python3
"""Mutation harness for the Approach B kernel fuzzers: plants one bug at a time in a production kernel, runs the mod's
fuzz wrapper (>= 4 s sleep first: staged builds can reuse a stale copy), expects a FAIL, restores the file byte-identical.

    python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py <wrapper.py> <mutations.json> [--only N]
mutations.json: [{"name": "...", "file": "<repo-relative>", "old": "<exact text>", "new": "<text>"}, ...]
Exit 1 if any mutation is not caught or a file fails to restore.
"""
import json, os, subprocess, sys, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(argv):
    wrapper, muts = argv[0], json.load(open(argv[1]))
    only = int(argv[argv.index("--only") + 1]) if "--only" in argv else None
    bad = 0
    for i, m in enumerate(muts):
        if only is not None and i != only:
            continue
        path = os.path.join(REPO, m["file"])
        raw = open(path, "rb").read()
        text = raw.decode("utf-8")
        if text.count(m["old"]) != 1:
            print(f"[{i}] {m['name']}: SKIP (old text matches {text.count(m['old'])} times)"); bad += 1; continue
        before = hashlib.sha256(raw).hexdigest()
        try:
            open(path, "wb").write(text.replace(m["old"], m["new"]).encode("utf-8"))
            time.sleep(4)
            os.utime(path)
            r = subprocess.run([sys.executable, os.path.join(HERE, wrapper)], capture_output=True, text=True, cwd=REPO)
            out = r.stdout + r.stderr
            fails = [l for l in out.splitlines() if l.startswith("FAIL") or "FAILURES" in l or "build FAILED" in l or "BUILD FAILED" in l]
            if "BUILD FAILED" in out or "build FAILED" in out:
                print(f"[{i}] {m['name']}: BUILD BROKEN (mutation invalid)"); bad += 1
            elif r.returncode != 0 and fails:
                first = next((l for l in fails if l.startswith("FAIL")), fails[0])
                print(f"[{i}] {m['name']}: CAUGHT  {first[:170]}")
            else:
                print(f"[{i}] {m['name']}: NOT CAUGHT"); bad += 1
        finally:
            open(path, "wb").write(raw)
            if sha(path) != before:
                print(f"[{i}] RESTORE FAILED for {m['file']}"); bad += 1
    print("mutations:", "ALL CAUGHT" if bad == 0 else f"{bad} PROBLEM(S)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

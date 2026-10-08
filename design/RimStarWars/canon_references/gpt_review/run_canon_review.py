#!/usr/bin/env python3
"""Send the Star Wars fauna/flora canon entries to GPT for review (CANON_FAUNA_FLORA_GPT_REVIEW_1).
TEXT ONLY: each entry's description.md (existing description + web citations); no image is ever sent.
Entries = every INDEX.md row with category 'creature' (119; plants such as chak_root are filed under it).
Batches of BATCH entries, serial, one gpt_consult per batch, output gpt_review/batch_NN.md.
usage: run_canon_review.py [batch numbers...]"""
import os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(LIB, "..", "..", ".."))
BATCH = 10

slugs = [m.group(1) for m in re.finditer(r"^\| \[([^\]]+)\]\([^)]*\) \| creature \|", open(os.path.join(LIB, "INDEX.md")).read(), re.M)]
batches = [slugs[i:i + BATCH] for i in range(0, len(slugs), BATCH)]
want = [int(a) for a in sys.argv[1:]] or list(range(1, len(batches) + 1))
prompt = open(os.path.join(HERE, "PROMPT.md")).read()
for n in want:
    out = os.path.join(HERE, f"batch_{n:02d}.md")
    if os.path.exists(out) and os.path.getsize(out) > 2000:
        print(n, "exists, skip", flush=True); continue
    bundle = os.path.join("/tmp", f"canon_batch_{n:02d}.txt")
    with open(bundle, "w") as b:
        for s in batches[n - 1]:
            b.write(f"\n\n===== ENTRY: {s} =====\n" + open(os.path.join(LIB, s, "description.md"), errors="ignore").read())
    pf = os.path.join("/tmp", f"canon_prompt_{n:02d}.md")
    open(pf, "w").write(prompt + "\n\nEntries in this batch: " + ", ".join(batches[n - 1]) + "\n")
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(ROOT, "src/RimMandrake/Utils/gpt_consult.py"), "--prompt-file", pf,
                        "-f", bundle, "--out", out, "--effort", "high", "--timeout", "2400"], capture_output=True, text=True)
    print(n, "rc", r.returncode, f"{time.time()-t0:.0f}s", os.path.getsize(out) if os.path.exists(out) else 0, flush=True)
    if r.returncode: print(r.stderr[-300:], flush=True)
print(f"{len(slugs)} entries in {len(batches)} batches", flush=True)

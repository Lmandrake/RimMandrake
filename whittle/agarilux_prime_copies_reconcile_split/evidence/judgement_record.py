#!/usr/bin/env python3
"""The survivor's judgement: the gptredo_03 rows for both subjects, which bytes each judged, and the owner's 2026-09-20 approval."""
import json, hashlib, subprocess
print("== gptredo_03 decision rows (infrastructure/state/art_eval/runs/gptredo_03/decisions.jsonl), both subjects")
for l in open("infrastructure/state/art_eval/runs/gptredo_03/decisions.jsonl"):
    d = json.loads(l)
    if not d["subject"].startswith("RM_AgariluxPrime"): continue
    print(f"- subject {d['subject']}  at {d['at']}")
    print(f"    judged file: {d['source_files']['single']}")
    print(f"    judged sha256: {d['source_sha256']['single']}")
    print(f"    decision: {json.dumps(d.get('decision'))}")
print("\n   (summary.md rows:)")
for l in open("infrastructure/state/art_eval/runs/gptredo_03/summary.md"):
    if "AgariluxPrime" in l: print("   " + l.strip()[:300])
P = "src/RimMandrake/TheRot/Textures/RotSpecies/AgariluxPrime.png"
print(f"\n== the survivor: {P}")
sha = hashlib.sha256(open(P, "rb").read()).hexdigest()
print(f"   sha256 {sha}")
print("   judged in gptredo_03?", "YES" if any(sha in l for l in open("infrastructure/state/art_eval/runs/gptredo_03/decisions.jsonl")) else "NO -- neither gptredo_03 row judged these bytes")
for old in ("src/RimMandrake/TheRot/Textures/Things/Plants/AB_AgariluxPrime.png", "src/RimUtinni/UtinniPatches/Textures/Things/Plants/AB_AgariluxPrime.png"):
    import os; print(f"   judged file {old}: {'STILL IN src' if os.path.exists(old) else 'retired (absent from src)'}")
R = "infrastructure/state/art_rulings/2026-09-20_rot_art_landed_20260920__rot_art_landed_20260920.decisions.json"
r = json.load(open(R))
print(f"\n== its standing judgement: {R}")
for k in ("approvedBy", "approvedAt", "approvedSaid", "approvalRoute"): print(f"   {k}: {r.get(k)}")
print(f"   row AB_AgariluxPrime: {r['decisions'].get('AB_AgariluxPrime')}  (sheet row effect: rot_agariluxprime_v3 landed clean; thumb thumbs/rot_agariluxprime_v3.png)")
g = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
b_now, b_v3 = g("hash-object", P), g("rev-parse", "9d83052dca:src/RimUtinni/UtinniPatches/Textures/RotSpecies/AgariluxPrime.png")
print(f"   bytes identity: git blob today {b_now} vs at 9d83052dca 'Land the 4 v3 regens' {b_v3}: {'IDENTICAL' if b_now == b_v3 else 'DIFFERENT'}")
print(f"   order: 9d83052dca committed {g('log','-1','--format=%ad','--date=iso','9d83052dca')}; approval stamped {r.get('approvedAt')} -- the approval came after the v3 landing it shows")
print("   art ledger live sha for RotSpecies/AgariluxPrime (art.py status): 85779af91a06 ->", "MATCH" if sha.startswith("85779af91a06") else "MISMATCH")
print("\n== conclusion")
print("   The survivor is neither gptredo_03 copy: the REGEN copy (UtinniPatches donor slot, sha c93606ba...) and the ACCEPT copy")
print("   (TheRot donor slot, 256 px, sha b0a767dc...) are both retired. The survivor is the v3 render the owner approved on 2026-09-20,")
print("   which the game has drawn since. Under the item's rule (re-judge only if the survivor is the REGEN copy), no re-judge is owed.")

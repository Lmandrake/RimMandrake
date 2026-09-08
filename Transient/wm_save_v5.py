import sys, os, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

SAVES = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"
NAME = "WORLDMAP_V10_cathedral_landmarks_2026-09-07"


def stat_all():
    return {f: os.path.getsize(os.path.join(SAVES, f))
            for f in os.listdir(SAVES) if f.endswith(".rws")}


before = stat_all()
print("BEFORE: %d .rws files" % len(before))

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/save_game", {"saveName": NAME})
    print("save_game claims ->", json.dumps({k: v for k, v in r.items() if k != "operation"})[:300])

time.sleep(3)
after = stat_all()

new = sorted(set(after) - set(before))
gone = sorted(set(before) - set(after))
resized = {f: (before[f], after[f]) for f in set(before) & set(after) if before[f] != after[f]}

print("\n== THE GUARD (never trust the path it returns) ==")
print("  NEW files:      %s" % (new or "NONE  <-- FAILURE, nothing was written"))
print("  DELETED files:  %s" % (gone or "none"))
print("  RESIZED files:  %s" % (resized or "none  <-- good, no existing slot overwritten"))
if new:
    for f in new:
        print("  %s  %d bytes" % (f, after[f]))
ok = bool(new) and not gone and not resized
print("\nVERDICT: %s" % ("SAVE OK" if ok else "SAVE SUSPECT - investigate before trusting it"))

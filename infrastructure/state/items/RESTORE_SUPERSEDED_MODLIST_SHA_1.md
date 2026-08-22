## spec
🔴 **One line only the owner should write.** `FROZEN_FINGERPRINT_OVERWRITTEN_1` is closed
in code (`3c092bd`): entries are now sealed, `freeze()` refuses to append past an edited
one, and superseding records the prior fingerprint instead of dropping it. **What is not
done is the historical repair**, because editing a frozen record is the owner's act and
doing it unasked would be the same class of act the item was filed about.

`9078a15` rewrote `OFFICIAL-2026-08-21`'s `modlist_sha` from `e0f11692cf69e516` to
`5ef6eec3daf6c325` in place, `capturedUtc` untouched, on a claim that the old value was
unreproducible. **It reproduces** — sha256 over the sorted, lowercased
`manifest.json mods[].packageId` set, first 16 hex, recomputed and recorded in `c330690`.

⚠️ **The 08:20 capture it described has since been replaced by the 22:44 one, so neither
value can be recomputed from disk any more.** The registry line is the only witness left,
and it currently reads as though only one number ever existed.

**The repair is to ADD a field, never to change one.** Appending
`"supersededModlistSha": "e0f11692cf69e516"` to that entry restores the fact that the
algorithm changed rather than the capture. ⛔ Do **not** also add a `seal` to that line —
sealing an already-edited entry launders the edit, which is exactly what
`registry_tamper()`'s refusal message warns against. The three existing entries stay
unsealed and read as UNMEASURED, which is the honest state.

**The command:**

```
! python3 - <<'PY'
import json
p = "/mnt/d/Luke/dev/Rimworld/infrastructure/state/dumps/REGISTRY.jsonl"
out = []
for line in open(p, encoding="utf-8"):
    if not line.strip():
        continue
    e = json.loads(line)
    if e.get("id") == "OFFICIAL-2026-08-21" and "supersededModlistSha" not in e:
        e["supersededModlistSha"] = "e0f11692cf69e516"
        e["supersededModlistShaNote"] = ("recorded 2026-08-21; 9078a15 replaced this "
                                         "value in place on a false unreproducible "
                                         "claim. The algorithm changed, not the capture.")
    out.append(json.dumps(e))
open(p, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("restored")
PY
```

## verify
`OFFICIAL-2026-08-21` carries both `modlist_sha 5ef6eec3daf6c325` and
`supersededModlistSha e0f11692cf69e516`; it carries no `seal`; the other two entries are
byte-unchanged; `python3 src/RimMandrake/Utils/selftest_frozen_dumps.py` still passes 30/30.

## criteria
A reader who recomputes the old way and gets `e0f11692cf69e516` can see from the entry
alone that the number is accounted for, and does not conclude the capture changed.

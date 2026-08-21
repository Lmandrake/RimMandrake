<!-- status: live -->
# Deployed patches, validated offline before the 2026-08-21 load — BUILD

**Command** (the raw 1.9 MB output is derived and deliberately not committed —
re-run this to reproduce it):

```
python3 skills/rimworld-modding/scripts/validate_patch.py \
  "<Mods>/Jawa_Patches/Patches" "<Mods>/JawaFactionSlate/Patches" \
  "<Mods>/Jawa_Doctrine/Patches" "<Mods>/Jawa_Armoury/Patches" \
  --defs "<Data>" --defs "<workshop/294100>" --defs "<Mods>"
```

Run against the **deployed game copies**, not the repo, on the 578-mod list with
the game down.

## Result

```
OK TOTAL - 52 file(s), 0 error(s), 1869 warning(s)
```

🔴 **Zero errors. No deployed patch is broken.**

⚠️ **A partial read of this file said "0 errors" when it was 6% written.** The run
takes ~10 minutes over 1,282 installed mods, and the output is buffered, so file
size stops growing long before the process ends. **Check `pgrep -f validate_patch`,
not the byte count** — the earlier reading was over 315 of 7,455 checks and the
final `OK TOTAL` line is the only verdict that counts.

## The 1,869 warnings, classified — none is a defect

| n | class | verdict |
|---|---|---|
| 1690 | *inner xpath differs from the conditional test* | advisory. The `<nomatch>` branch adds at a different path than the guard tests, which is the normal shape for "add it if the mod is here, add it elsewhere if not" |
| 172 | *0 nodes on disk, but `<node>` appears in a PatchOperation in `<other mods>`* | **expected and unfixable offline.** The target is created by another mod's patch at load time, and an on-disk scan cannot see post-patch state. This is what a `--live` check against a fresh dump answers — and this load produces that dump |
| 5 | *xpath matches N nodes in ONE mod folder and applies to ALL* | deliberate broad patches |
| 2 | *not wrapped in `PatchOperationConditional` or `PatchOperationFindMod`* | see below |

## The two unguarded operations — checked individually, both benign

| file | operation | target it actually matched |
|---|---|---|
| `Jawa_Patches/Patches/ForceGremlin_NoHair.xml` | `PatchOperationAdd` | **1 match** in *RimMandrake - Star Wars Races* → `RimMandrakeXenotypes.xml` |
| `Jawa_Patches/Patches/JawaWorld_Name.xml` | `PatchOperationReplace` | **1 match** in **Core** → `RulePacks_Namer_World.xml` |

🔑 **The generic warning does not apply to these two instances.** An unguarded patch
is dangerous when its target mod may be absent; here one target is **our own mod**
(absent only if nothing of ours works at all) and the other is **Core** (never
absent). Each matches exactly one node today.

⚠️ **The residual risk is the warning's second clause, not its first** — *"or fixes
its def upstream."* A RimWorld update that reshapes `RulePacks_Namer_World.xml`
would turn `JawaWorld_Name.xml` into a red error on every launch. That is a
game-version risk, not a mod-list one, so it cannot fire on this load. ⇒ **No action
before launch.**

## What this does NOT prove
- ⛔ Nothing about **post-patch** state: the 172 above are exactly the gap.
- ⛔ Nothing about **load order** — a patch can be valid and still run too early.
  Order was checked separately: all five of our dependency pairs are correct.
- ⛔ Nothing about whether a patch is **right**, only that it will match something.

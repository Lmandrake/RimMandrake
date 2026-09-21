# CREATURE_REGISTER_GEN_CORPSE_MISMATCH_1 — the register generator refuses on its own self-check

## what is wrong

`src/RimMandrake/Utils/gen_creature_register.py --stage data` refuses to write
`design/Jawa/worldbuilding/review/creature_register_rows.json`:

```
CORPSE CROSS-CHECK FAILED: 1242 vs 1265
```

Hit 2026-09-20 while working `ROSTER_VALIDATOR_STALE_REFS_1`. That item needed
11 newly-authored fauna added to the register but could not run the generator
to do it — it fell back to hand-adding 11 minimal stub rows (defName/label/mod/
packageId/kindOf/bodySize/pawnKind only, each value pulled from the live def
dump) instead of the generator's full analysis (biomes/stats/art fields). The
stub rows are flagged in their own `source` field so they're findable later.
Not chased further there — out of that item's scope.

## why it matters

The register can't be safely regenerated until this refusal is understood — any
future item that needs a full register refresh (not just a few rows) will hit
the same wall. A cross-check refusing is the generator behaving correctly
(better than silently writing a wrong file), but nobody has yet looked at what
the two numbers (1242, 1265) count or why they diverge.

## the work

1. Read `gen_creature_register.py`'s corpse cross-check to find what it counts on
   each side of 1242 vs 1265 (looks like two different corpse/creature tallies
   being compared for consistency).
2. Determine whether the divergence is real data drift (something added/removed
   without updating both sides) or a stale assumption in the check itself.
3. Fix whichever is wrong, then run `--stage data` clean and confirm the 11 stub
   rows added in `ac8b64d1c` get properly replaced with full generator output.

## verify

`gen_creature_register.py --stage data` completes without the cross-check
refusing, and the 11 stub rows carry real biome/stat/art fields afterward.

## criteria

The register generator is trustworthy to run again without hand-patched
fallback rows.

## spec
Explain the ~10% bare-pawn rate documented in
`infrastructure/state/facts/roll_arm_harvest_2026-08-28.md` for 23 of 49 kinds, given
both prior theories (pacifist backstory, weaponMoney floor) are ruled out. Read
`PawnWeaponGenerator.TryGenerateWeaponFor` from decompiled 1.6 source rather than guess.

## mechanism, read from `RimWorld/PawnWeaponGenerator.cs` (1.6)
The full per-candidate eligibility predicate (every one of these AND'd together, not
just price and tags):

    !(w.Price > randomInRange)                                              -- ruled out (fact #3, huge margin)
    && kindDef.weaponTags.Any(tag => w.thing.weaponTags.Contains(tag))      -- tag overlap
    && (kindDef.weaponStuffOverride == null || w.stuff == override)         -- stuff override
    && (!w.thing.IsRangedWeapon || !pawn.WorkTagIsDisabled(WorkTags.Shooting))  -- ⭐ NEW
    && (w.stuff == null || w.stuff.stuffProps.allowedInStuffGeneration)     -- stuff filter
    && (generateAllowChance >= 1f || Rand.ChanceSeeded(generateAllowChance, pawn.thingIDNumber ^ w.thing.shortHash ^ 0x1B3B648))  -- ⭐ NEW

🔴 **Correction to the filer's own hypothesis:** there is no `techLevel` filter anywhere
in this method. That candidate can be dropped; it does not exist at this stage of
generation (2026-08-28 03:12).

Two mechanisms survive, neither previously named as a candidate, both able to produce a
per-pawn (not per-kind) probabilistic bare result with **no shared trait or backstory**
— exactly what fact #2 measured:

1. **`WorkTagIsDisabled(WorkTags.Shooting)`** — a DIFFERENT worktag than the `Violent`
   check already ruled out. Any pawn incapable of Shooting (many unrelated
   traits/backstories can cause this independently) is excluded from every RANGED
   weapon. If a kind's entire within-budget, tag-matching pool happens to be ranged-only,
   that pawn generates bare. Explains "25 distinct backstory pairs, no repeated trait" —
   the CAUSE is the same mechanism, not the same source.
2. **`generateAllowChance`** (`ThingDef`, default 1f) gated by `Rand.ChanceSeeded(...,
   pawn.thingIDNumber ^ weapon.shortHash ^ 0x1B3B648)` — a per-pawn, per-weapon coin
   flip. If a kind's eligible pool is narrow (1-2 tag/budget matches) and one of them
   carries `generateAllowChance < 1`, that fraction of pawns empties the whole pool.

Both are consistent with ~10% and with "no shared trait." Distinguishing which kind
fails which way (or both) needs the **eligible pool itself** per kind — cross-referencing
`weaponTags` against every weapon def's `IsRangedWeapon` and `generateAllowChance` across
the full 582-mod set. No tool computes that; `jawa/pawnkind_audit` only reports
`cheapestEligible`, a single static price point, not the pool's ranged/melee mix or any
def's `generateAllowChance`. Not built here — this item's ask was the mechanism read,
not a new audit tool.

## decision
**Diagnosed, not yet fixable with certainty.** Recommend DECIDE accept this as the named
mechanism (real engine behaviour reacting to our own faction weaponTags authoring, not a
bug in our patches) and treat full per-kind attribution as its own scoped follow-up:
`PAWN_WEAPON_POOL_JOIN_TOOL_1` (build the weaponTags×roster join, needs offline). The
likely mitigation either way is the same shape — give every kind's weaponTags at least
one non-ranged (melee) fallback so a Shooting-incapable pawn, or an unlucky
generateAllowChance roll on the only ranged option, still has something to equip — but
which tags to add is a canon/faction-identity call, not mine to make for 23 kinds
unilaterally; that is a `needs: owner` item once the join tool names which kinds are
actually ranged-only.

## verify
Source read against `RimWorld/PawnWeaponGenerator.cs` 1.6 (mcp__rimsage), not guessed.
Predicate transcribed verbatim above; the missing techLevel filter is a negative result,
also verified by reading the whole method rather than assuming.

## criteria
- [x] Mechanism named from decompiled source, not guessed.
- [x] Both prior theories' status unchanged (pacifist/floor stay ruled out; nothing here
      contradicts either closed item).
- [x] Decision recorded: diagnosed-but-not-fully-attributed, with the concrete follow-up
      that would finish attribution, rather than a guessed fix applied blind.

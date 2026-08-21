# OUTLANDER_GROUPMAKER_PATCH_1 — the owner approved the abstract patch

## spec

🔴 **OWNER, 2026-08-21: "Approved abstract patch."** This reverses the ⛔ recorded at
`src/Jawa/Jawa_Patches/Defs/FactionDefs/HomesteadDefenseLeague.xml:36` —
*"pawnGroupMakers, factionNameMaker and the raid curves are untouched"* — and closes the
decision that `sixteen-roster-kinds-have-nowhere-to-be-used-8f21c4` was waiting on.

**The problem, stated once:** `pawnGroupMakers` for the Homestead Defense League lives on
the **abstract parent `OutlanderFactionBase`**, not on `OutlanderCivil`. So an xpath at
`FactionDef[defName="OutlanderCivil"]/pawnGroupMakers` **matches nothing — and a patch
that matches nothing logs nothing.** Five authored, valid pawn kinds are referenced by
nobody:

`Jawa_Homestead_Grunt` · `_Heavy` · `_Specialist` · `_Leader` · `Jawa_Homestead_DesertRanger`

**What is approved:** patch the abstract base, **additively**. One `<li>` at a low weight
per group maker that should field these kinds. ⛔ Leave vanilla's existing options and
weights alone — do not rebalance, do not remove, do not reweight what is already there.

⚠️ **Patching the abstract base reaches EVERY Outlander faction, not just the League, and
that is the accepted cost of the approval — but it is not licence to be careless.** The
League holds 13 of 72 settlements; a weight high enough to change how ordinary Outlander
raids compose is a bug even though the patch itself is approved. Low weight, additive,
and measure what the composition looks like before and after.

🔑 **The dune ranger is the one that must actually appear.** It is dressed explicitly
(`Apparel_Duster` + `Apparel_Headwrap`, both vanilla Core) because *looking* like the
desert is its whole brief — its four siblings leave apparel to `apparelMoney` and take the
roll. If the wiring works and the ranger still never spawns, the weight is wrong, not the
def.

## verify

- `validate_patch.py <path> --defs …` resolves the xpath against `OutlanderFactionBase`
  and reports a non-zero match count. ⛔ Zero matches is the exact silent failure this item
  exists to end — assert the count, never read "no errors" as success.
- The five kinds appear in a generated Outlander group on a quicktest, or in
  `pawnkind_audit` output over the live stack.
- `Jawa_Homestead_DesertRanger` specifically spawns wearing the duster and headwrap.
- Ordinary Outlander raid composition is compared before and after; the shift is small and
  is written down as a number, not asserted.

## criteria

Five authored kinds are reachable by the game, the ranger looks like the desert, and no
other Outlander faction visibly changed.

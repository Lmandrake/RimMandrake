## spec
🔴 **OWNER RULING 2026-08-20** (`OWNER_DECISIONS.md`, end of file): the
Galactic Empire's vessel is **vanilla `Empire`**. Owner, same day: **the Outer
Rim mod is NOT leaving the list** — it keeps shipping its own pawn kinds, gear
and droid factions.
✅ **The patch itself is already correct.** `Patches/GalacticEmpire.xml`
targets `/Defs/FactionDef[defName="Empire"]` at every xpath. Nothing to change
there.
❌ **`About/About.xml` still describes the old vessel**, in two places:
the `GalacticEmpire.xml` bullet in `<description>` says it "reskins
OuterRim_GalacticEmpire", and the `<loadAfter>` comment on
`Neronix17.OuterRim.GalacticEmpire` still credits that file. ⚠️ The `loadAfter`
ENTRY stays — other patches in this mod do touch Outer Rim defs; only its
trailing comment is wrong.
⚠️ The bullet also carries a fixedName trap written against the OLD def
("the shipped def sets BOTH to Galactic Empire"). Re-read it against vanilla
`Empire` before rewriting — the trap may or may not still apply, and this is
shipped user-facing text, so correct it rather than deleting it.
✅ **`JawaFactionSlate/Patches/OnlyOurFactions.xml` is CORRECT AS IS** — REP's
first draft of this item was wrong about it. Its six `OuterRim_GalacticEmpire`
xpaths are worldgen SUPPRESSION (`startingCountAtWorldCreation` 0), not a
reskin, and with the mod staying they are exactly what we want. It is a
generated file ("Do not hand-edit"); leave it alone.

## verify
`About.xml` names vanilla `Empire` as the Galactic Empire's vessel, and no prose in
`src/Jawa/Jawa_Patches/` claims we patch `OuterRim_GalacticEmpire`.

## criteria
the shipped mod description matches what the mod actually patches.
⚠️ **Also, low priority, and it needs YOUR hands not REP's:**
`bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs` had one
`SetFactionRelation` parameter DESCRIPTION re-pointed to `Empire` (it told
users to aim at the dead def). No behaviour change — but it is in a compiled
assembly, so **the repo and the deployed DLL now differ by that string until
the next rebuild.** Fold it into whatever rebuild comes next; do not spend a
game-down window on it alone.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20. `About/About.xml` rewritten and deployed.
⚠️ **TWO OF THE ITEM'S THREE CLAIMS WERE ALREADY STALE WHEN I GOT HERE, and the
real defect was bigger than the one described.**
✅ Already correct, no change needed: the bullet already said *vanilla `Empire`*,
not `OuterRim_GalacticEmpire`; and the `<loadAfter>` comment on
`Neronix17.OuterRim.GalacticEmpire` reads `OuterRim_Imp* pawn kinds
GalacticEmpire.xml`, which is **true** — the file still re-points those pawn
kinds. Nothing to fix in either.
🔴 **What WAS wrong, and the item did not know:** the bullet claimed the patch is
*"label-level only"* and that *"everything mechanical is deliberately untouched —
no goodwill, no settlement counts, no pawnGroupMakers, no memes"*. Read against
the file: it sets `permanentEnemy true`, drops `settlementGenerationWeight` 1 →
0.45, REMOVES `requiredMemes` and `structureMemeWeights`, and replaces two
`pawnGroupMakers` option lists. **Every clause of that sentence was false.**
🔴 **And the fixedName trap was written against the DEAD def, exactly as the item
warned.** It said *"the shipped def sets BOTH to Galactic Empire"*. Read off
`Data/Royalty/Defs/FactionDefs/Faction_Empire.xml`: vanilla `Empire` ships
`label` **"shattered empire"** and **NO `fixedName` at all** — which is why our
op is a `PatchOperationAdd` and not a Replace. ⚠️ **Do not read this off the def
dump; the dump is post-patch and shows our own values back.** The trap still
applies and is now stated correctly.
⛔ There is no colour op in the file. The old text described one at length.
verify: `About.xml` well-formed; the only `OuterRim_GalacticEmpire` string left
under `src/Jawa/Jawa_Patches/` is the patch header saying it USED to reskin that
def and no longer does. `deploy --apply` -> `VERIFIED in sync`.
⏳ **The `JawaBenchTerrainTools.cs` half is NOT done** — it needs a bridgetools
rebuild, the item says not to spend a window on it alone, and another seat has
been in that assembly tonight. Left for whoever rebuilds next.

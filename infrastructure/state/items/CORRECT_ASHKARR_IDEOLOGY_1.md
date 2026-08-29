# CORRECT_ASHKARR_IDEOLOGY_1 — ASHKARR_IDEOLOGY_MODE_CALL_1's "world creation only" claim is wrong

Filed 2026-08-29, FOUNDRY. The owner pushed back on my relay of `ASHKARR_IDEOLOGY_MODE_CALL_1`'s
framing: *"I really don't get this. You can set faction religions in-game, and then that's what
it is. We can't specify the faction religions in a live game?"* He was right to push back — I
relayed CHECK's 2026-08-26 claim without re-verifying it, and it does not hold up.

## Spec

`ASHKARR_IDEOLOGY_MODE_CALL_1` claims: *"the setting is chosen at world creation only — it
cannot be retrofitted onto an existing world by any def, patch or bridge call."* **This is
wrong.** Source-verified, not guessed:

**The live route.** `RimWorld/FactionIdeosTracker.cs`'s `ChooseOrGenerateIdeo(IdeoGenerationParms
parms)` is the ORDINARY public instance method the game itself calls to assign a faction's ideo
— nothing about it is world-creation-only, and nothing stops it being called again on an
already-existing `Faction` on a running save. When `parms.fixedIdeo` is true — exactly what all
twelve of our FactionDefs already declare — it takes priority over every classic-mode branch:
```csharp
Ideo ideo2 = IdeoGenerator.MakeFixedIdeo(parms);   // reads parms.deities/name/description/styles
ideo2.primaryFactionColor = faction.Color;
primaryIdeo = ideo2;
Find.IdeoManager.Add(ideo2);
```

**Why classic mode does not block this.** Two DIFFERENT flags, easy to conflate — CHECK's
original read conflated them:
- `IdeoManager.classicMode` (`RimWorld/IdeoManager.cs:22`) — a plain mutable **per-save** `bool`.
  Not locked after world creation: the game's own `Page_ChooseIdeoPreset.cs:87,556` sets it
  directly at runtime (`Find.IdeoManager.classicMode = false;`).
- `Ideo.classicMode` (`RimWorld/Ideo.cs:33`) — a **per-Ideo** `bool`. `IdeoGenerator.MakeFixedIdeo`
  / `GenerateIdeo` never set it true, so an Ideo made this way is a FULL ideoligion regardless of
  the save's global flag.

This also answers the leader-title concern directly: `IdeoFoundation.GenerateLeaderTitle`
(`RimWorld/IdeoFoundation.cs:697`) checks `ideo.classicMode` — the PER-IDEO flag, `false` on a
freshly `MakeFixedIdeo`'d ideo. Leader titles generate normally, no special-casing needed.

**What building this means.** A bridge tool (or debug action) that, per faction: builds an
`IdeoGenerationParms` from that FactionDef's existing `ideoName` / `ideoDescription` /
`deityPresets` / `requiredPreceptsOnly` fields (the struct takes these as explicit constructor
params, not auto-read off the FactionDef — mirror wherever `FactionGenerator.cs` does this at
normal worldgen) with `fixedIdeo: true`, then calls `faction.ideos.ChooseOrGenerateIdeo(parms)`.
No world recreation, no lossy mutator/landmark replay, none of `ASHKARR_IDEOLOGY_MODE_CALL_1`'s
option-1 cost.

## Verify

⚠️ **Not yet proven live — this is a source-verified route, not a tested one.** No bridge tool
calls `ChooseOrGenerateIdeo` today. Owner confirms this is landed when:
1. A scratch/quicktest run assigns a fixed ideo to a test faction on an ALREADY-classic-mode
   save, and `jawa/get_defs`-equivalent (or a new `faction_ideo_get` read) shows the faction's
   `primaryIdeo` carrying the authored `ideoName`, deities, and a generated (non-"leader") leader
   title.
2. Then, and only with the owner's go-ahead, the same call runs against the twelve Ash'karr
   factions on the real world.

## Criteria
- [x] Owner reads this and rules: pursue the live route, still prefer world recreation for some
      other reason, or park entirely. — RULED 2026-08-29T18:25:12Z: no world recreation, patch
      the live world's faction ideoligions via `ChooseOrGenerateIdeo`, build and run now.
- [ ] If pursued: a bridge tool built and proven on scratch before touching Ash'karr.
- [x] The 95 existing believers' pawns (currently on vanilla `Astropolitan`): owner ruled
      new pawns only — `Faction.primaryIdeo` changes going forward via `ChooseOrGenerateIdeo`;
      no `Pawn_IdeoTracker` reassignment pass on the existing 95.

## Watch out
`ASHKARR_IDEOLOGY_MODE_CALL_1`'s cost-of-recreation analysis (the file-import table, the
mutator/landmark non-restorability) stays correct information about option 1 and is NOT
superseded — kept there as the fallback if the live route below fails to pan out for some reason
not yet found. Only its "must recreate, cannot retrofit" CONCLUSION is wrong.

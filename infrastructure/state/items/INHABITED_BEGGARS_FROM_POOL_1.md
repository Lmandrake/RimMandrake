## spec
§4.1 consumer 2. ⚠️ **Two corrections to the design doc before you start:**
🔴 (a) The doc's `GiveQuest_Beggars` DOES NOT EXIST. The real class is
   `RimWorld.QuestGen.QuestNode_Root_Beggars`, and the pawns are made at `:103`,
   `quest2.GeneratePawn(new PawnGenerationRequest(beggar, faction2, ...))`.
   That is the Harmony target.
🔴 (b) `faction2` is a **hidden generated faction** built at `:73` from
   `FactionDefOf.Beggars` — beggars do NOT belong to an existing faction. So a
   Hutt refinery survivor cannot simply be handed over; the patch must draw from
   the pool AND move the pawn into the generated beggar faction, keeping name,
   traits, backstory, relations and memories. `Pawn.SetFaction` does this.
⚠️ (c) `:44` is `ModLister.CheckIdeology("Beggars")` — **the whole quest is
   Ideology-gated.** If Ideology is off in the shipped list this item is inert
   and that is not a bug; confirm against `ModsConfig.xml` before debugging.

## verify
`dotnet build` clean; the transpiler/postfix reports a patch target found — ⚠️ a
Harmony patch that matches nothing throws at startup, unlike an XML one, so this
one is loud. Good.

## criteria
burn out a cast, wait for a beggar event, and at least one beggar is a pawn from
the pool by name.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

built 2026-08-20, `8fd8fbd`. `src/Jawa/Inhabited/Source/Patch_BeggarsFromPool.cs`.
All three of the item's corrections were taken: the target is
`QuestGen_Pawns.GeneratePawn(Quest, PawnGenerationRequest, bool)`, the drawn pawn
is moved into the quest's hidden generated faction with `SetFaction`, and the
Ideology gate is noted at the class.
⭐ **The verify is stronger than the item asked for: the target is proven by the
COMPILER, not by Harmony at startup.** Binding the method group to a
`Func<Quest, PawnGenerationRequest, bool, Pawn>` makes C# check the signature
against the real `Assembly-CSharp.dll`, so a target that has moved fails the
BUILD in half a second instead of costing a 25-minute cold load to discover. The
same proof is on the `Game.DeinitAndRemoveMap` patch.
verify output: `Build succeeded. 0 Warning(s) 0 Error(s)` with both proofs in.
⚠️ The draw is `DrawAny`, not the faction-scoped `Draw` — beggars belong to a
hidden temporary faction, so a faction-scoped draw would always return nobody.
That is new API on `DisplacedPool`, added for this.
Live half filed to CHECK inside `INHABITED_POOL_ROUND_TRIP_1`.

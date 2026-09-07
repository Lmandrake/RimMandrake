# The edible-genepack loop — reverse-engineered, verified, ready to implement natively

Filed as `EDIBLE_GENEPACK_NATIVE_1`, owed by [the Slime's gene machine](the_slime.md) §7.
Source: `GenepacksInjection.dll` (TommasoBelluzzo.GenepacksInjection, workshop 3784789591,
packageId `TommasoBelluzzo.GenepacksInjection`) — **INACTIVE, not in ModsConfig.xml**, on
disk only at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3784789591\v1.6\Assemblies\GenepacksInjection.dll`.
Read with `ilprobe` (`src/RimMandrake/Utils/ilprobe/`), pointed at that DLL instead of its
hardcoded `Assembly-CSharp.dll` default via a source-patched exec (the tool itself was not
modified — it is shared infra for the game assembly specifically). Every claim below is
cited as `Type::Method` + IL offset; the vanilla members it calls into
(`Pawn_GeneTracker.AddGene`, `HediffDefOf.XenogerminationComa`) were independently
re-verified against the real `Assembly-CSharp.dll` with the unmodified tool, not just
trusted from the donor's own reference.

This supersedes `genepack_mods_plunder.md`'s open gap ("coma behavior UNMEASURED, not
decompiled") for this one mod.

## The core primitive: `StateUtilities.ApplyGenepack(GeneSetHolderBase source, Pawn recipient)`

```
IL_0000  guard: if source == null or recipient == null, return
IL_0007  foreach gene in source.GeneSet.GenesListForReading:
IL_0022      if recipient.genes.HasGene(gene): continue
IL_0030      recipient.genes.AddGene(gene, xenogene: !GenepacksInjectionMod.Settings.UseEndogenes)
IL_0063  recipient.health.AddHediff(HediffDefOf.XenogerminationComa, null, default(BodyPartRecord))
```

That is the ENTIRE mechanic. No custom hediff, no custom hidden state, no extraction
building, no gene bank. `XenogerminationComa` is vanilla Biotech
(`RimWorld.HediffDefOf.XenogerminationComa`, confirmed present in `Assembly-CSharp.dll`'s
`HediffDefOf` field list). `Pawn_GeneTracker.AddGene(GeneDef, bool xenogene)` is vanilla
too (confirmed: two `AddGene` overloads exist on `RimWorld.Pawn_GeneTracker` in the real
assembly). **A native reimplementation needs zero new hediffs and zero new gene-storage
code — it only needs to call these two vanilla APIs in this order, on a `GeneSetHolderBase`
(any `Genepack`, or any other GeneSet-holding Thing) and a target `Pawn`.**

The eligibility gate, `CheckUtilities.CanApplyGenepack(source, recipient)` (`AcceptanceReport`):
- false ("GPI_InvalidInjection") if `source`, `recipient`, or `recipient.genes` is null.
- false ("GPI_AllGenesAlreadyPresent") if every gene in `source.GeneSet.GenesListForReading`
  is already on `recipient.genes` (`HasGene` true for all).
- else true.

## Two consumption routes, same primitive underneath

**1. Self-use** (vanilla `CompUsable`/`UseItem` job — no custom JobDriver):
- XML side (not decompiled, read from the donor's own patch, `1.6/Patches/GenepackInjection.xml`):
  vanilla `Genepack` ThingDef gains `CompProperties_Usable` (useJob `UseItem`, 150 ticks) +
  `CompPropertiesGpi` (marker) + vanilla `CompProperties_UseEffectDestroySelf` (auto-destroys
  the item after use — a SEPARATE vanilla comp, not this mod's code).
- `CompUseEffectGpi.CanBeUsedBy(Pawn p)`: `p.IsColonistPlayerControlled` AND
  `CheckUtilities.CanApplyGenepack(parent as Genepack, p).Accepted`.
- `CompUseEffectGpi.DoEffect(Pawn p)`: `StateUtilities.ApplyGenepack(parent as Genepack, p)`.
  That's it — one call.

**2. Administer to a prisoner or slave** (custom `JobDef`
`GenepacksInjection_InjectGenepack`, driver `JobDriverGpi`):
- `CheckUtilities.IsValidActor(Pawn)`: non-null, spawned, alive, humanlike, has genes,
  `IsColonistPlayerControlled`.
- `CheckUtilities.IsValidRecipient(Pawn)`: non-null, spawned, alive, humanlike, has genes,
  not in an aggro mental state, AND (`IsPrisonerOfColony` && not prison-breaking) OR
  (`IsSlaveOfColony` && not rebelling). **The forced-injection job is prisoner/slave ONLY —
  self-injection only ever goes through route 1.**
- `TryMakePreToilReservations`: reserve the recipient (`maxPawns=1`), then reserve the
  genepack (`stackCount=1`).
- Toils, in order:
  1. `CreateToilExtraction` — if the genepack is null/destroyed, fail (`EndJobWith(4)`,
     `JobCondition.Incompletable`). If it currently sits in a `CompGenepackContainer`
     (a rack/holder), verify it's still actually contained, then
     `ThingOwner.TryTransferToContainer` it into the actor's `carryTracker`. (If the
     genepack has no container — already loose — this toil is effectively a no-op.)
  2. Goto the recipient carrying the genepack.
  3. `CreateToilInjection` = `Toils_General.WaitWith(recipientIndex, 150, useProgressBar:
     true, maintainPosture, maintainSleep, JobCondition.Incompletable, faceTargetIndex)` —
     **150 ticks (2.5s) with a visible progress bar**, matching route 1's own use-duration.
     - End condition (checked while waiting): `CheckUtilities.IsValidRecipient(recipient)`
       still true, else fail.
     - Finish action (runs once, on successful completion): re-check `CurJob` still active;
       re-resolve the genepack as `actor.carryTracker.CarriedThing as Genepack`; re-check
       `IsValidRecipient(recipient)` and `CheckUtilities.CanApplyGenepack(genepack,
       recipient).Accepted`; if both hold, `StateUtilities.ApplyGenepack(genepack,
       recipient)` **then `genepack.Destroy()`** — destruction is explicit here, unlike
       route 1 where a separate vanilla comp handles it.
- Float menu entry (`FloatMenuOptionProviderGpi`, drafted+undrafted, no multiselect):
  right-click a valid prisoner/slave → `OpenGenepackSelection` lists every reachable,
  reservable genepack on the map (`StateUtilities.GetAvailableGenepacks`, which walks both
  loose genepacks via `ListerThings` and genepacks inside any colonist-owned
  `CompGenepackContainer` building) → picking one calls `TryStartInjection`, which starts
  the job above.

## What a native reimplementation needs — and what it does not

**Needs**: one static method matching `ApplyGenepack`'s three lines (merge missing genes as
xeno/endo per a settings toggle or a fixed campaign choice, then apply
`HediffDefOf.XenogerminationComa`) plus the `CanApplyGenepack` gate. That is genuinely
donor-independent — it is two vanilla API calls wrapped in a null/duplicate check, nothing
`GenepacksInjection.dll`-specific about it. **This mechanism is fully verified and requires
no further contact with the donor DLL to implement.**

**Does not need copied**: `JobDriverGpi`'s exact toil shape, the float-menu provider, or the
prisoner/slave-only gate — those exist to serve GenepacksInjection's own UX (drag a
genepack to a captive), which is NOT the Slime's gene machine's UX (owner's design, §7 of
`the_slime.md`: pick a target gene → the machine computes where the current carrying that
gene passes on the map → the pawn stands there in the open → activates → coma → emerges
with the target gene *plus a hidden random rider* → must then take the Rot injection).
That flow needs its OWN job/building logic built around the same core primitive — a
different targeting and framing entirely, not a copy of GenepacksInjection's job.

## Why the C# has not been written yet

The gene machine's actual content — the curated target-gene list (SW-race gifts, etc.) and
the hidden odd-rider list — is still `the_slime.md`'s FIRST Owed item, unauthored, and
needs an owner sitting. Writing a mod (About.xml, csproj, defs) around content that does not
exist yet is exactly the premature scaffolding this repo's conventions warn against
(`CLAUDE.md`: "Don't design for hypothetical future requirements"). **This document is the
complete, verified spec** — when the gene lists are authored, whoever builds the machine
mod writes `ApplyGenepack`/`CanApplyGenepack` directly from the two code blocks above, with
zero need to re-open `GenepacksInjection.dll`.

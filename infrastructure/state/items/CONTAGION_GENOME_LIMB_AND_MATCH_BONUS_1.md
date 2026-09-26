# CONTAGION_GENOME_LIMB_AND_MATCH_BONUS_1 — grown limbs and an install-match bonus

Follow-on from `CONTAGION_GENOME_ORGAN_GROWING_1` (closed, v1 shipped in `mandrake.rm.contagion`).
That item built the full loop — extract a genome sample from a colonist
(`RM_ExtractGenomeSample`), carry it to a live `AA_RedGoo` and inject it
(`RM_InjectGenomeSample`), the amoeba gestates 4 days (`RM_AmoebaGestation`) and dies
producing 2-4 ordinary vanilla organs (kidney/liver/lung/heart) carrying the source
colonist's identity via `CompGenomeMatched` (patched onto those four vanilla ThingDefs).

Two pieces of the owner's ruling were deliberately left out of v1, not silently downgraded:

## spec

1. **Limbs.** The owner's own words were "a plethora of organs **and limbs**." Vanilla RimWorld
   has no natural-limb-transplant item or recipe at all (checked via RimSage against the
   decompiled 1.6 source this session — only bionic/prosthetic/archotech limb *replacements*
   exist, installed via their own recipes onto a missing-part hediff; there is no "install
   natural leg/arm" precedent the way `InstallNaturalKidney`/`Liver`/`Lung`/`Heart` exist for
   organs). Shipping a natural grown limb needs: a new BodyPartDef-targeted install recipe (or
   several, per limb type), a new installable ThingDef family, and a decision on what a
   "natural" leg/arm even restores versus a bionic (better than a peg leg, presumably worse
   than a bionic, matching Biosculpter's own natural-regrowth tier) — real new mechanism, not a
   ten-minute add. Scope this as its own recipe family when picked up.
2. **Install-match bonus.** `CompGenomeMatched` already carries the source colonist's identity
   end to end (sample -> gestation -> organ), so "matched to that individual" is real, not
   generic — v1's organs show "Grown from <Name>'s genome" in their inspect string. What v1 does
   NOT do is give any MECHANICAL difference between installing a matched organ into its own
   source colonist versus into someone else — every organ installs through vanilla's own
   `InstallNatural<Organ>` recipes unchanged, since that's what keeps them real, sellable,
   installable items (see `CompGenomeMatched.cs`'s header for why a new ThingDef family would
   break that). A real bonus (e.g. a mood thought or reduced something on a same-colonist
   install, nothing on a mismatch) needs a Harmony postfix or a dedicated install recipe
   checking `CompGenomeMatched.sourcePawnID == recipient.thingIDNumber` at
   `Recipe_InstallNaturalBodyPart`-equivalent completion — UNMEASURED whether that class name is
   exactly right; read it first, don't guess from this note.

## verify

Grown limbs: at least one limb type installable through a fitting new recipe, matched-identity
carried the same way organs already do it. Install-match bonus: a measurable in-game difference
(mood thought, message, stat) when a matched organ goes back into its own source colonist versus
a stranger, with a mismatch case producing no bonus (and, per the owner's body-horror caution on
this biome, no premise that mismatched tissue punishes the recipient either — check the Contagion
sheet's own limits before inventing a penalty).

## criteria

A grown limb exists as a real installable item, and installing a matched organ or limb into its
own source colonist visibly differs from installing it into anyone else.

## Watch out

- Do not invent a natural-limb mechanism from reasoning — read `InstallNaturalKidney`'s sibling
  recipes and vanilla's body-part-restoration path (`CompBiosculpterPod_HealingCycle`,
  `MedicalRecipesUtility`) first; this session found no natural-limb-item precedent at all, only
  bionic/prosthetic/archotech replacement lines — confirm that's still true before designing
  around it.
- The consumable-host ruling and the "no green squares" / "no finished natives beyond the ruled
  table" hard bans on the_contagion.md all still apply unchanged; this item only extends what the
  existing host (`AA_RedGoo`) produces, it does not touch the roster or placement.

## what shipped (FOUNDRY, 2026-09-26)

**RimSage precedent, confirmed against the decompiled 1.6 source (Core/Biotech/Royalty/
Ideology/Anomaly/Odyssey), reversing this item's own "no natural-limb precedent" watch-out:**
vanilla's `Recipe_InstallNaturalBodyPart` (used today by `InstallNaturalKidney/Liver/Lung/Heart`)
is NOT organ-specific — its `ApplyOnPawn` calls `MedicalRecipesUtility.RestorePartAndSpawnAllPreviousParts`,
generic to any `BodyPartRecord`. No vanilla DLC ships a natural leg/arm *item* (only
`SimpleProstheticLeg/Arm`, `BionicLeg/Arm`, `ArchotechLeg/Arm` — all artificial), but the
*mechanism* needed no invention: a new ThingDef family + RecipeDefs targeting `Leg`/`Arm`
through the same vanilla worker class does exactly what an organ install already does, restoring
the limb itself rather than fitting a device — the "natural regrowth tier" the spec asked for,
matching what Biotech's own Biosculpter Regeneration cycle does for its own small-part list
(restore, not replace).

**Built:**
- `RM_GrownLeg`/`RM_GrownArm` ThingDefs (`Defs/ThingDefs/RM_GrownLimbs.xml`), parented off
  vanilla's own `BodyPartNaturalBase` like Kidney/Liver/Lung/Heart, carrying `CompGenomeMatched`
  directly (no patch needed — these are new defs of our own).
- `RM_InstallGrownLeg`/`RM_InstallGrownArm` RecipeDefs (`Defs/RecipeDefs/RM_InstallGrownLimbs.xml`),
  parented off vanilla's `SurgeryInstallBodyPartNaturalBase`, `appliedOnFixedBodyParts` Leg/Arm.
- `AmoebaHostUtility.CompleteGestation`'s batch pool now includes both grown limbs alongside the
  four organs — a single mixed "organs and/or limbs" batch, per the owner's own "a plethora of
  organs and limbs" wording.
- **Install-match bonus**: `Recipe_InstallGrownBodyPart` (subclass of vanilla
  `Recipe_InstallNaturalBodyPart`) reads `CompGenomeMatched` off the ingredient before calling
  `base.ApplyOnPawn` (safe even though `Toils_Recipe.ConsumeIngredients` already `Destroy()`s the
  ingredient first — `Destroy()` doesn't clear comp field data), confirms the surgery actually
  succeeded (`!hediffSet.PartIsMissing(part)`), and on a same-colonist match grants a
  `Thought_Memory` (`RM_GenomeMatchedInstall`, +8 mood / 10 days) plus a message. A mismatch, or
  an organ/limb with no genome data at all, is a complete no-op — no bonus, no penalty, per the
  owner's body-horror caution. `Patches/OrganInstallGenomeMatch.xml` routes the four vanilla
  `InstallNatural<Organ>` RecipeDefs through this same subclass, so the bonus covers organs too
  (the item's own spec point 2), with zero behavioural change to any ordinary organ transplant.
- Gated by the existing `genomeOrganGrowingEnabled` Mod Settings toggle at the source (grown
  limbs/organs only exist if the loop that makes them is on) — no new toggle needed.

**Deferred:** a dedicated icon for the grown-limb items (placeholder: `BodyPartNaturalBase`'s own
inherited `HealthItem` texture, the same one vanilla's own organ ThingDefs ship with). No queued
or existing "grown limb" art found in `infrastructure/artpipe/done/`, `_artsrc/` or
`registry.jsonl`. Not filed as a follow-on item — fair v1 scope per the parent item's own
precedent (the genome sample item also reused a placeholder texture and was not treated as owed
work).

**Verified:** `validate_patch.py --defs --live` against the live DefDump (628 active mods,
68,680 defNames) — 0 errors; the new `OrganInstallGenomeMatch.xml` patch's `nomatch` branch
confirmed 1 live match each against `InstallNaturalHeart/Lung/Kidney/Liver` in Core's own
`Hediffs_BodyParts_Natural.xml`. `dotnet.exe build -c Release` — 0 warnings, 0 errors.
No live in-game surgery test performed (would need a bridge session; the mechanism was verified
against the decompiled source instead, per the item's own "no live-proven claim" constraint on
its parent).

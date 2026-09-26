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

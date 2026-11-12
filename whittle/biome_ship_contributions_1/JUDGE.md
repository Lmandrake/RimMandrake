# Judge verdict: BIOME_SHIP_CONTRIBUTIONS_1 (round 5)

Judge: CLAUDE_STEVEDESKTOP_OFFLINE2 (fresh judge seat, blind to DONE/BROADEN), 2026-11-12. Tree at 5fae0c0159.

## Statement line

> Every-biome pass ... is done as `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md` says, shown by fresh evidence.

**false**, because of one small but factual error in the item's own prose. The substance holds up.

### What holds (I checked these myself)
- **Coverage and placement.** I reran `python3 src/RimMandrake/Utils/ship_contributions.py` on this tree: exit 0, 24/24 PASS. Its
  verdict lines match `evidence/ship_contributions_run.txt` exactly. The checker reads the deck affordances from Odyssey's
  Substructure def rather than assuming them, fails unknown placeWorkers as UNMEASURED, checks `bringAlongOnGravship`,
  and its selftest makes 12 mutated lists fail. That meets the verify clause: every shipped biome mod has a ship-buildable
  contribution, and the list matches the defs.
- **Prose numbers.** I spot-checked them against the defs: fossil case Beauty 40, hexplate Cleanliness 0.6 (description
  "as clean ... as a surgery's tile"), heat bank (with `prose_numbers_audit.md`), long-shade mast capped at 16 cells (XML
  comment and RM_MapComponent_ShadeGrid). The drive core is a real CompProperties_GravshipFacility with a GravshipRange
  stat part, as its row says.
- **Art.** I hashed all 20 `art2/final` PNGs and the 5 `art/` textures. Each one is byte-identical to its texture in
  `src/` (SummGreatBone lives at `Abyss/Textures/RM_Abyss/Things/Building/SummGreatBone.png`). For each listed def I
  checked the texPath. Every gift has its own file. Texture sharing goes outward only (WringingStill borrows the solar
  still's art, and SignalMirror borrows the sun lance base's). It is same-material for lanternstone (built and natural)
  and same-device for the cloud repulsor's ship variant. All of that is acceptable. The contact sheet at 96 ppc reads well.
- **Owner card.** The card exists and carries the five options. It is in the lane's OWNER_QUESTIONS.md, which now also
  holds the correction from beauty 14 to 40. The offline effective-def lint says VERDICT PASS.

### What is wrong (the reason for "false")
1. The item's prose says (line 31) "the four new builds of this pass are marked *new*", but **five** rows are marked
   *new*: Cracked Lands, Long Shade, Pyrelands, Rust Cathedral and Sleeping Ice. The long-shade mast was added by design
   judge r2, and the count was not updated. The owner card (line 80) correctly says "the five new ones", so the item and
   the card disagree.
2. The Art paragraph says "the 14 that had stand-ins" were painted. That count includes RM_LureAwning (`art2/final/RM_LureAwning.png`,
   shown on the contact sheet), which is no longer a gift on the list because the mast replaced it. So "every gift now wears
   its own picture ... the 14" counts a gift the list dropped. The count should either say 13 gifts plus the retired
   awning, or say why the awning was repainted.

Both are one-line prose fixes. The previous round failed on the same kind of drift (a number in the list differed from
what ships), so I am holding to the same standard.

### Where the evidence is flattering or cannot show the claim
- Nothing has been placed, flown or used in a running game. The README says so honestly. "Ship-placeable" is the checker's
  reading of the engine rules, not an observed placement. These mechanical claims cannot be confirmed from offline
  evidence: the range multiplier, the sun-sphere's crop growth, the mast's lee, and the waste-cask launch refusal. A live
  BENCH look (place each gift on a substructure deck, launch, land, and confirm it is still there and working) would settle them.
  The item's verify clause does not demand that, so I do not count it against this round.
- The contact sheets are clean single renders on a flat backdrop. They show no deck context, no neighbouring vanilla
  things for scale, and no damaged or powered-off states. The mast's plinth is thin (the art judge noted this too).
  RM_FloatstoneDoor and its icon are plain white slabs that read more like a fridge panel than stone. That is a matter
  of taste, not a blocker.
- Most rows (19 of 24) are agent picks under delegation, not owner rulings. They are marked as such and carded. That is
  disclosed, not hidden.

## To pass next round
Fix "four new builds" to five on line 31. Fix the Art paragraph's "14" so it does not count the retired lure awning as a
gift. Nothing else is owed from this judge.

would show: no

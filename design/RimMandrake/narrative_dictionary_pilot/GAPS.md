# GAPS — what the narrative dictionary could not express (batch 1)

Input to `EVENT_TRACE_PROPS_LIBRARY_1`. Source: the eight vignettes in `vignettes.md` and the
45-row prop table `objects.jsonl`, built by `build.py`. Machine list: `gap_rows.json`.
Every defName named here was checked against the live def dump (628 mods, captured
2026-09-26T01:08:12Z) on 2026-10-03.

## 1. Unfilled ingredients: one line each (claim · register · what would fill it)

| # | vignette | claim it starves | register | what would fill it | trace needed |
|---|---|---|---|---|---|
| G1 | B3 fight at the door | someone fought their way in | marking | **Blaster-bolt scars on WALLS**: an impact pit with a scorch halo, in 2-3 variants, at chest height either side of a door. Vanilla `Filth_BlastMark` is a 3x3 *floor* explosion, and nothing marks a wall. | HIGH |
| G2 | B3 fight at the door | the door was forced | state | **A breached door state**: blown, buckled, or off its track. `AncientBlastDoor` and `Door` have no damaged state to place. | HIGH |
| G3 | B4 wrecked on purpose | smashed by people, not decayed | wear | **Impact/blunt-strike marks on equipment**: dents, cracked screens, a dropped tool beside them. `AncientDestroyedConsole`'s own description says "smashed *or* looted", so the cause is ambiguous. | HIGH |
| G4 | A3 daily path | they come and go every day | wear | **A worn-path floor**: a scuffed track, a polished lane, or a run of footprints. The validator **refused the whole vignette**, because `RM_Filth_Tar` is one dark blob that does not read as "tracked". | HIGH |
| G5 | B2 nobody for years | the desert is coming in | wear | **A drift edge**: sand banked against wall feet and fanned in under a door. `Filth_Sand` is uniform per cell **and shares its texture (`Things/Filth/Grainy`) with `Filth_Dirt`**, so it reads as "dirty", not as "desert getting in". | HIGH |
| G6 | A1 sorted salvage | nothing is wasted, everything is mended | state | **A repaired state on furniture**: a patch, a weld bead, a lashed binding. Nothing in the 628-mod set encodes "mended". | HIGH |

## 2. Structural gaps the table exposed (not tied to one vignette)

- **S1. Direction is missing.** Every trace is a 1x1 cell with no heading. Claims that
  carry a vector ("crawled away", "tracked in", "fled toward the exit") have to be faked
  with a chain of cells. `Filth_BloodSmear`'s texPath is `Things/Filth/CrawlSmear`, so a
  drag trail exists, but only in blood and only as a chain. ⇒ Build directional sprites
  (drag, skid, scrape, footprints) whose rotation carries the vector in one cell.
- **S2. Age is missing everywhere except blood.** `Filth_Blood`/`Filth_DriedBlood` is the
  only fresh-vs-old pair. A scorch, a scrape or a spill cannot say *when* it happened, yet
  "rich but abandoned" depends entirely on *long ago*. ⇒ Build every new trace in a fresh
  variant and an aged variant.
- **S3. The wall is a register only we supply.** Vanilla/DLC have no wall-mounted trace.
  Every wall mark in the table comes from `RimMandrake: Graffiti Framework`
  (`RM_Graffiti_*`). ⇒ Wall traces (G1, scorch, smoke-staining above a fire, rust runs)
  are the cheapest new register: the framework already places them on walls.
- **S4. "Tended" has no high-traceability object.** Stewardship ⊥ abundance (spec §4c) is
  only half expressible. *Neglect* has `AncientPlantPot` (dead soil, HIGH). *Care* has
  only a living `PlantPot` and a fuelled `RUT_GaslightLamp`, both MED. Otherwise it is
  shown by **absence** of dirt, which is LOW and is exactly what got A3 refused. ⇒ G6 and
  "signs of upkeep" (sweep marks, fresh paint over old, a patched wall) are the
  positive-evidence half of the vocabulary. They are not violence, but they are "signs of
  something happening".
- **S5. Cause misattribution (Gaver's *false* signal, spec §4d).** We looked at the sprite
  of `RM_Graffiti_Scratches`. It reads as **animal claws**, not as a tool or a blade. That
  is right for a beast lair and wrong for the "cut, not unbuckled" register.
  `RSW_CrackedCeramicShards` renders with the reused `Things/Item/Resource/StoneBlocks`
  texture, which is the owner's own anti-example (*"stone blocks… no traceability"*).
  ⇒ Each needs a variant whose look encodes the intended cause.
- **S6. States the engine will not place.** These are all needed by vignettes and none is
  placeable: lit vs unlit `TorchLamp` (already noted in `structure_procedural_spec.md`), an
  open `AncientSafe`, a breached door (G2), a tipped `Stool`. A trace prop is often the
  cheapest stand-in: a soot ring for a dead torch, scattered contents beside a closed
  safe.
- **S7. The vision pass covered 7 of 45 rows.** Vanilla and DLC sprites live in
  `resources.assets` and were not extracted, so legibility is UNMEASURED for 38 rows. Their
  traceability grades rest on the label and description (DEF_TEXT), not on pixels.
  ⇒ Before the library commissions art, run the vision pass on the vanilla traces it would
  sit beside (`reading-rimworld-graphics`), or it may duplicate one that already reads.

## 3. Correction: event traces are scarce, but they are not absent

Spec §6a counted **this repo's** XML and found no blaster scars, scorch marks, scrapes,
drag trails or impact spall. Across the **live 628-mod set**, a usable base already
exists, and the library should extend it rather than rebuild it:

| exists (verified defName) | what it encodes | limit |
|---|---|---|
| `Filth_BlastMark` (Core, 3x3) | explosion | floor only, no age, not a bolt |
| `Filth_BloodSmear` (Core, tex `CrawlSmear`) | wounded body moving | blood only, direction only by chaining |
| `Filth_DriedBlood` (Ideology) | old violence | the only aged trace |
| `Filth_Ash` · `Filth_MachineBits` · `Filth_RubbleBuilding` · `Filth_ScatteredDocuments` (Core) | burned / machine broke / structure broke / papers left | cause is generic ("what burned?") |
| `SlagRubble` · `Filth_LooseGround` · `Filth_OilSmear` (Core) | slag scattered / dug ground / leak | not looked at |
| `Filth_Floordrawing` (Biotech) | a child was here | HIGH; our best "who lived here" cue |
| `RM_Graffiti_Stencil_Crown` · `_Paste_Wanted` · `_Scratches` · `_TallyMarks` · `_WarningGlyph` (ours) | anti-authority, a hunt, claws, counting, crude warning | wall register; WarningGlyph does not say *what* danger |
| `RM_Filth_Tar` (ours, FlowWorks) | tar | does not read as tracked (G4) |

## 4. Suggested scope for `EVENT_TRACE_PROPS_LIBRARY_1`, ranked by claims unblocked

1. **Wall blaster scars**, fresh and aged (G1, S2, S3). They unblock the whole
   "fight happened here" family and are the owner's first-named item.
2. **Directional floor traces**: drag/skid/scrape, plus footprints in sand/tar/blood
   (S1, G4). They unblock every vector claim and the refused A3.
3. **Drift and accumulation edges**: sand banked at walls and under a door, a dust gradient
   (G5). These show time passing, which is the abandonment half.
4. **Impact/strike marks on equipment and a breached-door overlay** (G2, G3). These
   separate deliberate violence from decay.
5. **Signs of upkeep**: patches, welds, sweep marks, fresh paint over old (G6, S4). This is
   the positive evidence of care that spec §4c needs, so a poor clan reads as competent,
   not squalid.
6. **Age variants** of existing vanilla traces where a mod-side retexture can supply them
   (S2), e.g. an aged blast mark.

Not in scope here: the density ceiling per claim (spec §8). As the plan said, it waits for a
measured over-crowded case.

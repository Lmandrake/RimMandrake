# CONTAGION_RULED_CONTENT_1 — build the grotesque cast: 35 RM_ defs, full donor replacement

Ruled at `CONTAGION_BEDAZZLE_SITTING_1` (2026-09-27; owner-typed rulings + cards
on its ledger). **The authority is the cast bible:**
`design/Jawa/worldbuilding/biomes/contagion_grotesque_cast_2026-09-27.md` — per-
def hooks, stats sketches, wiring notes. The sheet amendment (2026-09-27 block in
`the_contagion.md`) admits the new natives. Art: 80 jobs queued
(`contagion_grotesque_cast.csv`); renders come back as a BENCH review sheet —
wire art as it is ruled kept.

## Scope

1. **Full RM_ port of the donor cast** — new ThingDef/PawnKindDef pairs under the
   grotesque names (Bloody Mess, Gawpsack, Blisterfloat, Scorchpod, Bloodlurk,
   Meltgut, Sparkleech + grub, Scaldhide, Doublemaw, Gnashling, Ikee, the
   Shambles, Peeper, Eyestinger, Fleshsop), NOT patches: the donor defs leave the
   roster, ours replace them at the ruled commonalities.
2. **New species**: Skinflap, Gorekite, Danglemaw, Crispling, Sloshbelly; flora
   Meatvine, Toothmoss, Wombpod (Wombpod wires into the BUILT amoeba-gestation
   loop as the harvestable host source).
3. **Flora ports**: Eyebark, Lashgrass, Bleedleaf, Gorestalk, Rattlegrope,
   Sapblister, Bloody Fist, Halfmade Tree + Blighted variant.
4. **Flyers** (Blisterfloat, Sparkleech, Skinflap, Gorekite — Gawpsack is ruled a
   GROUNDED floater): MaxFlightTime/FlightCooldown + race flight fields, Locust
   shape. Never block on animation frames.
5. Roster rewiring on `RM_Contagion`: shorthand element form, `RUT_Sytheclaw`
   dropped (never admitted; Pyrelands is its home), donor rows removed in the
   same change our rows land.

## Watch out

- `<li>` in wildAnimals/wildPlants silently discards — shorthand element form only.
- animalDensity/plantDensity must stay explicitly set on RM_Contagion.
- The Unfinished's spawner C# is live — do not rebuild; the new species must not
  duplicate its mechanism.
- Ban sweep before close: nothing edible (ban 4), nothing upgrading a visitor
  (ban 6), natives UV-shy or armored (ban 2).

## verify
- Donor defNames absent from RM_Contagion's roster; every ruled name present at
  the ruled commonality (measured, not assumed).
- A quicktest map spawns the new cast; flyers fly (state read, never an
  unattended screenshot hunt); Wombpod harvest yields a usable gestation host.

## Offline re-measure 2026-10-11 (FOUNDRY): offline scope built; the Shambles "gap" was a move
- **The 2026-10-07 reconcile's "missing: RM_Shambles" is wrong.** The def ships at
  `src/RimMandrake/TheRot/Defs/Fauna/RM_Shambles.xml`, rostered in `RM_TheRot_Biome.xml` at 0.5. It moved
  there on the owner's 2026-10-05 note (*"this belongs in the Rot, not here."*). The header comment in
  `RM_ContagionFauna.xml` now says so.
- **MEASURED from `RM_Contagion.xml`, parsed as XML elements, with 0 `<li>`:** animalDensity 3.0, plantDensity
  0.35. 23 fauna rows and 13 flora rows. All 9 ruled flora ports are present. 13 of 14 ruled fauna ports are
  present under their own names. Ikee ships as `RM_ContagionIkee` (`CONTAGION_IKEE_NAME_COLLISION_1`). Sanity
  probe: `RM_Shambles` resolves among 8,121 defNames in `src/`.
- **The verify bar "donor defNames absent" now conflicts with a LATER owner decision.** `AA_OcularJelly` and
  `AA_InfectedAerofleet` (`MayRequire sarg.alphaanimals`, 0.5 each) came back into the Contagion roster at
  `5011933af` (2026-10-09). That followed his Cauldron-sheet notes (*"This creature should be moved to the
  Contagion."*). The cast bible names these same two donors as the sources for `RM_Gawpsack` and
  `RM_Blisterfloat`, so each donor and its port now share one roster. ⛔ This pass did not remove them, because
  a rule must not overturn his placement. Whether the donor and its port should both stay is his call.
  NEXT: put it on the Contagion's next sheet as one row.
- Still owed (live): L1 defs resolve on minimal; L2 quicktest spawn, flyer STATE read, Wombpod harvest → gestation.

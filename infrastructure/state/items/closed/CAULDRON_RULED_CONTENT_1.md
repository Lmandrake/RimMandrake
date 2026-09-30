# CAULDRON_RULED_CONTENT_1 — Build the Cauldron ruled cast

From `CAULDRON_BEDAZZLE_SITTING_1` (volley closed 2026-09-28, all rulings on that
item's ledger notes). Analysis source — read it first:
`design/Jawa/worldbuilding/biomes/cauldron_bedazzle_review_2026-09-28.md`
(what's-there census, art table, collision sweeps). Cast bible follows from the
commission agent as `cauldron_bedazzle_cast_2026-09-28.md`.

The biome is `src/RimMandrake/PoisonForest/` today; `CAULDRON_FULL_RENAME_1` renames
everything — coordinate: content built here lands under the NEW names if the rename
has run, old names + rename-sweep otherwise. Say which in the closing note.

## spec

1. **Wire all 7 owner-ruled imports** (owner, turn 4: "Wire and keep."): Lylek,
   Plasmorph, LuciferBug, Radyak, RipperHound, Skalder, Silooth — into the biome's
   rosters (Utinni patch layer where donor/canon, per Q11/Q11a). Two rows contradict
   the frozen sheet's bans; the owner's ruling OVERRIDES the bans — amend the sheet
   lines, do not "fix" the wiring back out.
2. **Four new natives**, names collision-swept clean at the review pass (probe:
   korrum 63 files):
   - `RM_Vexxiss` — the GIANT. Solid, NO explosion anywhere on it (owner: "Too many
     exploding giant beasts"). Behaviors in `CAULDRON_MECHANICS_BUILD_1`; the def,
     body, stats, shear operation live here. **Shear yields `RM_Vexxith` (name
     pending one collision sweep): a rare material immune to powerful acids and
     temperature** (owner-typed ruling) — a stuff/material def, only obtainable by
     shearing a LIVING vexxiss; a kill wastes the lode.
   - `RM_Zisska` — plated mineral-rasping crust-grazer, the RM tier's own herbivore.
     Butchers to toxic prized meat + trace metal.
   - `RM_Eskith` — feather-footed ground-drummer; goes silent ahead of vent bloom
     (couples to the falter tell in MECHANICS).
   - `RM_Xithess` — filter-frond signature flora; harvests as vent-chemistry stock.
3. **Diverge the 7 donor AB_ flora into owned RM_ defs wearing the already-validated
   replacement art** sitting unwired in `infrastructure/artpipe/done/` (see the
   review doc's art table) — do NOT queue new art for these. Fix RM_TwistingThornwood's
   leftover donor description while in there.
4. **Metal-infused old growth**: both owned trees (and the diverged old-growth flora
   where the cast bible says so) get growth-scaled metal second-yield AND steep
   growth-scaled harvest work (owner: "The metallic infused trees should be slow to
   harvest") — greatbole second-yield precedent.
5. Toxic prized meat defs stay as-is.

## criteria

- 7 imports wired and visible in the merged roster read (parse `<wildAnimals>` by
  node NAME, never `<li>` count); frozen-sheet ban lines amended with the ruling.
- 4 natives + material def built, collision-proven, with Mod Settings coverage per
  the every-mod-ships-superb-settings law.
- AB_ flora divergence: 7 owned defs, validated art wired by texPath, donor rows
  retired from the RM tier (Q11a: RM tier stands alone rich).

# FORGE_RULED_CONTENT_1 — Build the Forge ruled cast and materials

From `FORGE_BEDAZZLE_SITTING_1` (volley closed 2026-09-29; every ruling is an
owner-typed ledger note on that item). Analysis:
`design/Jawa/worldbuilding/biomes/forge_bedazzle_review_2026-09-28.md`. Cast
bible follows from the commission agent as `forge_bedazzle_cast_2026-09-29.md`.
Mod: `src/RimMandrake/TheForge/`.

## spec

1. **Wire in all waiting** (owner, turn 2: "Wire in all waiting."): Tibidee and
   AA_ColossalAerofleet into the rosters; the fleet flier's finished artpipe art
   into the RM mod; `RUT_Plant_FlashFlora` thingClass onto the owned flora; the
   review doc's full found-unwired list, including the three DEPLOY_HOLD art
   debts it names.
2. **Four admitted natives** (turn 4: "1) admit."), collision-swept + name-checker
   passed at the review pass:
   - `RM_Dhokkur` — GIANT. Obsidian-backed rain-drinker; dormant through still
     heat (reads as terrain), unfurls to walk and drink only during boiling
     rain; neutral, immensely tough, slow; butchers to heat-shielding hide.
     Dormancy behavior lives in `FORGE_CYCLE_MECHANICS_1`.
   - `RM_Julmox` — plate-footed ground herd; sealed between bursts, grazes the
     flash-window moss film; tamable, the standalone tier's pastoral spine.
   - `RM_Jossur` — sky apex column-rider; REAL 1.6 flight (`MaxFlightTime`
     stat, Locust shape; never block on animation frames per the flyer law).
   - `RM_Dhuvvox` — flash-swarm: sealed ash nodules erupting by the hundred for
     the two-hour window; despawn/reseal on window end.
3. **Floatstone** (turn 7, owner verbatim): "Ultra-light pumice made of what
   looks like spun glass whirled into tangles. Super strong and light building
   material, not flammable, quite valuable, and the walls it makes look like
   swirled stone spun sugar made into blocks. Very beautiful." A stuff-capable
   material (strong, very light, flammability 0, high market value) whose
   walls/blocks read as swirled spun sugar; harvested from floatstone-garden
   growths during the freeze phase (spawn cycle in `FORGE_CYCLE_MECHANICS_1`).
4. **Struck — do not build**: vent machines beyond vanilla geothermal (turn 6:
   "lets just keep vent-based power as an option (already present in game)");
   the ship heat-exchanger (B), the fireweed scald-gear economy (D), the
   two-faiths mapgen content (F). ⚠️ `RM_ArmorRating_Scald` therefore remains
   granted-by-nothing ON PURPOSE — known state, not a defect to fix.

## criteria

- Merged rosters show the wired rows (parse `<wildAnimals>` by node NAME);
  four natives + floatstone built, Mod Settings coverage per the settings law;
  fleet flier renders from the RM mod's own textures.

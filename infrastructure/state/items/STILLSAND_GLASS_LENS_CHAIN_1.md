# STILLSAND_GLASS_LENS_CHAIN_1 — sand to glass to lens: stills, ovens, the sun lance and fulgurites

From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.4 and §4 #5, #11,
#12, with the turn-4 rulings in `stillsand_bedazzle_cast_2026-09-30.md` §0. Owner, typed, volley
turn 2: *"the very fine sand of this region is extremely high quality and can be smelted into a fine
glass fit for lenses. The lenses can be made into high performance solar stills and ovens."*

Checked before filing (2026-09-30): no glass stuff, solar still, solar oven or sun furnace exists in
the stack; the raw optics that do exist are `RM_Biosilica` (no use yet), `RSW_GlassPearl` (moving to
`RM_GlassPearl`), glasscrust grit and `RSW_KraytPearl`. Fulgurites already exist (below).

## spec

1. **Drift shovelling yields glass sand, at full yield (ruled by card 2026-09-30; REVERSES the
   dunes engine's "dig vanishes").** Clearing drift through vanilla's `Area_SnowOrSandClear` /
   `WorkGiver_ClearSnowOrSand` on a dunes-engine map drops `RM_GlassSand` in proportion to the sand
   depth removed, with no loss factor. Every drift is stock. `design/MOVING_DUNES_DESIGN.md` is
   corrected in the same commission. Mind the engine's mass cap: removed sand leaves the field.
2. **The sieve, rethought.** With drift as the bulk source, the sand sieve no longer makes sand
   from terrain. It becomes the **grader**: `RM_GlassSand` in, a fraction of **`RM_LensSand`**
   (the region's ultra-fine grain, the only input that makes lens-grade glass) out, the rest back
   as plain glass sand. Each batch also has small chances of grit finds: biosilica fragments,
   glasscrust grit, a glass-pearl seed. Plain glass sand makes plain sun glass (glazing, still
   tops); lens sand makes lens glass. The sieve is a staked screen built on sand, no power.
   ⚠️ This is BENCH's rethink, made because the ruling removed the sieve's old job; the owner may
   prefer another role (see the cast bible §7).
3. **The sun furnace (bootstrap).** A mirror-and-lens dish built with `RM_Biosilica` + steel; no
   fuel, no power. It melts glass sand into **`RM_SunGlass`** (one stuff, one stat line, one market
   value, waiting on `DESIGN_MATERIALS_REVIEW_1`) and lens sand into lens-grade glass. Output scales
   with the tile's sun elevation; the gale stops it.
4. **The lens bench** grinds lens glass into **`RM_PrecisionLens`**. Premium: a glass pearl gives a
   **pearl lens**, a krayt pearl a **krayt lens** (the apex; RSW patch recipe).
5. **The solar still.** A glazed, black-bottomed lens condenser distilling water from brine (cave
   seeps), wet organics (fresh kills, eggs, duumma sacs) and, as the **wringing still** (lore IN),
   **the dead**: a corpse gives water; outsiders take a mood penalty; Sun-Debt believers call it
   *drawing* (Utinni thoughts). Output into FlowWorks' water liquid or DBH water, whichever is live.
   Rate scales with sun elevation; a pearl lens doubles it. Every litre counts on the Debt
   (`STILLSAND_RETURN_RITUAL_1`). Distinct from the moisture vaporator (air; the Leaning Scrub owns
   moisture farming).
6. **The solar oven.** A glazed box on a mirror skirt that cooks with no fuel and no power, in full
   sun only (stops in shade and in the gale). A skirt of muurrok **crest-plate** (`RM_CrestPlate`,
   `STILLSAND_EVENT_CREATURES_1`) makes it high-performance: faster, and able to bake sun glass.
7. **The sun lance (slate IN).** A heliostat mirror-array turret that focuses the fixed sun on one
   target. It heats, never ignites; useless in the gale or in shade; strength scales with
   elevation. Kept distinct from the Long Shade's heliograph (that one talks, this one burns). It
   can share `RM_Verb_MirrorBeam` with the muurrok.
8. **The geophone.** A biosilica resonator staked in the sand that turns rumbles within its radius
   into coarse direction-and-size markers (reads the swim kit's submerged query). It cannot tell a
   drazzik's lie from a real drum.
9. **Sun goggles** get a sun-glass recipe here (the goggles themselves are
   `STILLSAND_SUN_FROM_LATITUDE_1` §7).
10. **Fulgurites (slate IN). Already built: do not rebuild.** `RM_FE_Fulgurite`
    (`src/RimMandrake/Pyrelands/Defs/ThingDefs_Fulgurite/Fulgurite.xml`) spawns from
    `Patch_LightningStrike_Fulgurite` in `FireEcologyHook.cs` on `RM_FE_Ground_Sand` and vanilla
    `Sand`. Owed here: (a) add `SoftSand` and `RM_DeepSand` to the sand family; (b) the hook is
    gated on `RM_PyrelandsSettings.pyrelandsEnabled`, so move or duplicate the gate so Stillsand
    fulgurites do not need the Pyrelands on; (c) give `RM_Stillsand` a rare **dry thunderstorm**
    (lightning, no rain: dune_sea §6 bans rain); (d) fulgurite melts at the sun furnace into sun
    glass; (e) **new art from real photographs**, owner, typed: *"the full rights should be looked
    up so you get realistic images of full rights, not some crazy simple tube or other fantasy
    image, actual lightning, striking actual sand"* ("full rights" is voice-typing for fulgurites).
    The new job (`RM_FE_Fulgurite_real`, cast bible §6) replaces `RM_FE_Fulgurite.png` for every
    biome once the owner accepts it. Reference photos and their licences:
    `design/Jawa/worldbuilding/biomes/references/fulgurite/`.
11. **The ship lens array** is the Stillsand's row for `BIOME_SHIP_CONTRIBUTIONS_1`: add the row there
    (a lens-array ship part fed by precision lenses); the build rides that item.
12. **Mod Settings:** toggle drift yield, each building, the sun lance and Stillsand fulgurites;
    sliders for drift yield per depth, sieve fraction and still rate.

## criteria

- On a Stillsand quicktest, clearing a drift drops glass sand; the sieve turns glass sand into lens
  sand; the furnace, bench and still each complete one cycle in full sun and stop in the gale.
- The oven cooks a meal with no fuel and no power in sun, and not in shade.
- A lightning strike on `RM_DeepSand` can leave a fulgurite with the Pyrelands toggle off.
- The sun lance damages a target and starts no fire.

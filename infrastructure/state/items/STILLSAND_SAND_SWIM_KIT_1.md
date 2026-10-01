# STILLSAND_SAND_SWIM_KIT_1 — things swim under the sand: the kit, the Listening, sand fishing, the thumper

From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.0, §2.1 and §4
#1, #9, #15, with the turn-4 rulings in the cast bible `stillsand_bedazzle_cast_2026-09-30.md` §0.
Owner, volley turn 2, typed: *"The listening should focus on wind and sand Noises and then ominous
rumbling as things swim through the sand or bury their way to the surface. The sand swimmer mod is.
Major player here."* This item is the base the event creatures, the gale and droid play stand on.

Checked before filing: nothing in `src/` makes a pawn swim under sand. `RM_DeepSand` (FlowWorks) is
terrain, `CompSarlaccSwimmer` is a water-budget and rooting comp, and the swimmers all walk the
surface on stock AI today.

## spec

1. **The sand-swim kit (RM tier, CreatureBehaviors kit).** `RM_SandSwimExtension` on a race
   (swim terrains: `Sand`, `SoftSand`, `RM_DeepSand`, and drift depth ≥ 0.3 from the dunes engine;
   a rumble `SoundDef`; surface and dive rules) and `RM_CompSandSwim`. On swim terrain and not in
   melee, the pawn is **submerged**: a hediff using vanilla `HediffComp_Invisibility` (Anomaly), wake
   flecks, a rumble sustainer scaled by body size, and `RM_Filth_SandWake` trough filth. It
   **surfaces** (breach dust burst, breach sound, a one-cell stagger) when it strikes, crosses
   non-swim ground (rock, floors, so hard ground is a moat), or is hit.
2. **No vanishing.** A take lays the shipped `RM_Filth_DisturbedSand` funnel at the wake's end plus
   a letter naming the victim; a drag lays `RM_Filth_DragMark`. Every loss of an animal or pawn
   leaves a readable sign (owner, Long Shade turn 4).
3. **Consumers, one XML extension each:** `RM_Vekka`, `RM_Qorrax`, `RM_Drazzik`, the fill-out's
   `RM_Duumma` (RM); `RSW_SandStalker`, `RSW_SarlaccSwimmer`, `RSW_KraytDragon`,
   `RSW_GreaterKraytDragon` (RSW patches). 🔴 The krayts and the war wyrm **stay wild** (owner, by
   card, 2026-09-30): the kit gives the wild krayt its wake and rumble; it does not remove it from
   the roster.
4. **Droids are invisible to the food web (slate IN).** The kit's strike-target filter skips any
   pawn with no water in it: mechanoids and droids (by race flag, not by a defName list). A droid
   crew can fish, haul and cross ground nothing alive can.
5. **The thumper (slate IN), with moisture.** Owner, typed: *"Also thumper needs moisture not just
   thump."* `RM_Thumper` is a staked drum that draws swimmer wakes toward it, and it draws **only
   while the sand around it is wet**: it holds a water charge (FlowWorks water liquid or DBH water,
   whichever is live), wets a small radius when it beats, and falls silent to swimmers when the
   charge runs dry. Vibration plus moisture is the lure; either alone is not. It is also the Long
   Hunger's owed v2 summon: `RUT_Groundcaller` (Utinni) becomes a thumper variant by patch, not a
   second mechanism.
6. **Sand fishing wired into `RM_Stillsand`.** Add `fishTypes` to the biome pointing at the catch
   family (`RM_DuneCrawler`, `RM_GlassPearl` after `STILLSAND_BEDAZZLE_CONTENT_1`'s tier move;
   `RSW_SandStalker` and `RSW_RareSandCatches` by Utinni patch). A fishing session on deep sand
   has a small chance to draw a stalker wake toward the fisher.
7. **The sound bed (the Listening).** On the shipped `RM_MapComponent_ProximitySoundscape` /
   `RM_ProximitySoundscapeExtension`: the hiss and saltation scale with wind speed; the
   **singing dunes** are a one-shot fired from the dunes engine's transport batch (one or two per
   batch near the camera, a small hook in `MapComponent_DuneField`); the rumble and breach come
   from the kit. **Singing dunes warn (slate IN):** a boom fires only off a moving slip face, so a
   dune singing near the colony is a dune marching on it; add a one-line message the first time a
   singing slip face is within N cells of a player building. Audio follows the placeholder-grain
   convention; LEVIATHANS' sandworm sounds may be a prototyping stand-in only, never a dependency.
8. **The piinnok hook.** The piinnok's "lenses sink when a big wake passes" belongs to
   `WATCHER_CREATURES_MOD_1` (its `warnOnLargeBurrower` geophone flag). This item exposes a cheap
   query, "submerged swimmers above body size X within radius R of cell C", for that kit to call.
   Do not build a second sink behaviour here.
9. **Mod Settings:** a toggle each for the swim, droid immunity, the thumper, fishing, the sound bed
   and the singing-dune warning; the rumble volume as a slider.

## criteria

- On a Stillsand quicktest, a vekka on deep sand cannot be targeted, leaves wake filth and a rumble,
  and surfaces on rock or when struck. A state read (not a screenshot hunt) proves submerged/surfaced.
- A swimmer kill always leaves a funnel or drag mark plus a letter; the test checks for both.
- A swimmer never strikes a mechanoid that stands in its path.
- A dry thumper draws no wake; a charged one draws one within its radius.
- Fishing on `RM_Stillsand` deep sand yields a catch.

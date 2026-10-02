# RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1 — the Rust Cathedral's giant: the borehulk, a colossal peaceful mining droid with a worn-out drill

Caused by `RUSTCATHEDRAL_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.rustcathedral` (an invented,
non-IP machine: Q11a, `design/RimMandrake/biome_mod_architecture.md` §7). Design:
`design/Jawa/worldbuilding/biomes/rustcathedral_bedazzle_review_2026-10-02.md` §8;
`design/Jawa/worldbuilding/biomes/rustcathedral_mining_droid_hooks_2026-10-02.md` (hook 2, the Worn Bit,
was chosen).

Ruling, owner, typed 2026-10-02: *"A massive mining droid, more like a digging tank with drill and scoop,
having escaped the abandoned mines to this place. Not very intelligent but ridiculously armored and
strong. Fortunately it is also peaceful. Needs a plot hook (feel free to share some ideas)"*. This
**replaces** the review's platewalker and loop-mother (neither is built). The plot hook is
`RUSTCATHEDRAL_WORN_BIT_ARC_1`; this item builds the body, its idle life and its three drill states, and
nothing of the arc.

**Name:** *the borehulk* (`RM_Borehulk`), in the biome's own accent of plain descriptive compounds (living
bolt, deck plate, dead smartsteel). Collision-checked 2026-10-02: a python sweep of `src/`, `design/`,
`infrastructure/`, `skills/` returns 0 files; Wookieepedia full-text search 0 hits (probes `wyyyschokk` 5,
`mynock` 5); `artpipe_state.py find borehulk` 0 (probe `korrum` hits). The pitch's placeholder *the Delver*
was rejected: 3 repo files (`kyber_trade_plot_spec.md`, `Alien_Bestiary.md`) and 4 Wookieepedia hits.

## spec

1. **The body.** `ThingDef RM_Borehulk` on `BaseMechanoidWalker` (the precedent is `RM_CathedralRoach`, a
   wild, factionless mechanoid with its own think tree), `PawnKindDef RM_Borehulk`. A digging tank: low,
   tracked, a broad armoured hull, a forward drill boom and a bucket scoop, a tiny sensor head. Body size
   about 6 (drawn huge on an ordinary footprint, drawSize about 5; no multi-cell pawn). **Ridiculously
   armoured and strong:** armour sharp and blunt far above any vanilla mechanoid of its size, health scale
   very high, heat armour high (it lives in the eternal noon). **Dim:** animal-class intelligence; no
   trainables until owned (the arc grants them). **Peaceful:** `manhunterOnDamageChance 0`, no hostile think
   branch, never attacks, never retaliates; damaged, it stops, sounds a long grinding horn and backs slowly
   away from the attacker. Its melee is harmless in the wild (it never chooses to use it).
2. **Where it lives.** Not in `wildAnimals` (it must never respawn by the wild spawner). `GenStepDef
   RM_BorehulkPlacement`, self-gated to `RM_RustCathedral` like the wall GenSteps, places **at most one** on
   map generation with a chance (Mod Settings, default 0.6), on plain deck plate, never inside a sacred
   wall ring. A map that rolls none has none, ever.
3. **Its idle life.** A custom think tree `RM_ThinkTree_Borehulk`: slow wandering along open plate, long
   idles, **freezes on low hum bands** exactly as the bolts do (`RM_ThinkNode_ConditionalAttitudeBand`), and
   stops for the line-cycle (`RM_Job_LineCycleStill`, built by `RUSTCATHEDRAL_BASE_FINISH_BUILD_1`). It
   never enters a cell of a sacred wall tier and never mines one.
4. **The worn drill (the hook's premise, readable).** A comp `RM_CompBorehulkDrill` with three saved states:
   - **Worn** (the spawn state): its drill head is worn to a stub. Every so often it lowers the drill and
     scrapes the plate uselessly: a grinding moan (`SoundDef RM_BorehulkGrind`), sparks, no cell mined. The
     inspect line says what is seen, never why: *"Its drill head is worn to a stub."*
   - **Unbitted** (the drill head removed by the arc): the boom ends in a bare chuck; it no longer grinds.
   - **Restored** (the refurbished head fitted by the arc): it can mine (the arc gives it someone to mine for,
     or not).
   The state picks the body graphic (three art sets; the swap mechanism is the builder's, measured: a
   custom body render node keyed on the comp state is the expected shape). Art: `RM_Borehulk` (Worn) is in
   `infrastructure/artpipe/art_lists/rustcathedral_turn1_2026-10-02.csv`; the Unbitted and Restored sets
   are **owed as edits of the delivered Worn sprite** (`editing-images`, `reference=` the approved Worn art),
   so the three read as one machine. Queue them once Worn is approved; until then all three states draw Worn.
5. **Killing it** is possible and very hard. Its wreck butchers into a large salvage yield (steel, plasteel,
   components) and the drill head; on Cathedral ground the violence raises the hum's irritation as any
   fight does (no new sacrilege class; it is not one of the Cathedral's sacred things).
6. **Mod Settings** (`MOD_OPTIONS_RETROFIT_1` law): on/off (map generation, labelled), spawn chance, grind
   frequency.

Depends on: `RUSTCATHEDRAL_FREE_NAMES_TIDY_1`. Soft: `RUSTCATHEDRAL_BASE_FINISH_BUILD_1` (the line-cycle
stop; without it the borehulk only freezes on low bands). Blocks: `RUSTCATHEDRAL_WORN_BIT_ARC_1`.

## criteria

Deterministic state reads through `jawa/get_defs` and debug `[Tool]`s, recorded as cases in
`RUST_CATHEDRAL_FIRST_SCRIPT_1`'s `validation.py`:
- Free tier: `ThingDef/RM_Borehulk`, `PawnKindDef/RM_Borehulk`, `ThinkTreeDef/RM_ThinkTree_Borehulk`,
  `GenStepDef/RM_BorehulkPlacement`, `SoundDef/RM_BorehulkGrind` resolve (`foundCount` = 5).
- `RM_Borehulk` is in no BiomeDef's merged `wildAnimals` (XML-element parse of every BiomeDef plus patches).
- Generation with the chance forced to 1: exactly one `RM_Borehulk` on a Rust Cathedral map, standing on a
  non-sacred cell; forced to 0: none; on any other biome's map: none.
- A spawned borehulk's comp state reads `Worn`; its faction is null; its body size ≥ 5; its
  `ArmorRating_Sharp` and `ArmorRating_Blunt` stat values each exceed every vanilla mechanoid race's (read
  from the def dump).
- Damage it with a spawned hostile pawn for 2,500 ticks: it never starts a melee or attack job (job log),
  and its mental state stays null.
- Force the hum band to the lowest freeze band: its current job is a wait/freeze job; restore the band: it
  moves again within 2,500 ticks.
- After 30,000 simulated ticks in Worn state: the count of mined cells attributable to it is 0 and it has
  played `RM_BorehulkGrind` at least once (comp counter).
- Setting the comp state to each of the three values swaps the body graphic path (read the resolved
  graphic's texPath per state; the three differ once the edit art exists).
- Each Mod Settings toggle off removes exactly its effect.

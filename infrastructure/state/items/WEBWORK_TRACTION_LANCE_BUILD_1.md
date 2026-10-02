# WEBWORK_TRACTION_LANCE_BUILD_1 — the thrixweave traction lance: the capstan's sibling, learnable at the Webwork or the Sump

Caused by `WEBWORK_SCORING_SITTING_1` (turn 1). Free tier. Design:
`design/Jawa/worldbuilding/biomes/webwork_bedazzle_review_2026-10-02.md` §5 idea 1 ("The Mouth's
Answer"), §8. Ruling: **new marks: the traction lance only** (decision taken by question card 2026-10-02
07:17 PDT). Owner, typed: *"That traction lance was just suggested in another biome too. So now there are
two places to get it from I guess. Lasso relative."* Falling sheets and roots in the ship were not chosen.

The "other biome" is the Sump's Blackline Capstan, `SUMP_CAPSTAN_TURRET_BUILD_1`, which the owner ordered
modelled on Melee Animation's lasso pull (job `AM_GrapplePawn`, driver
`AM.Grappling.JobDriver_GrapplePawn`, stats `AM_GrappleRadius` / `AM_GrappleCooldown` /
`AM_GrappleSpeed`; `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §5). The lassos
themselves leave the game (`LASSO_CHERRYPICKER_REMOVAL_1`); the pull stays, on buildings.

## spec

🔴 **One pull, two buildings. Never a second implementation.**

1. **The shared pull.** Whatever `SUMP_CAPSTAN_TURRET_BUILD_1` builds as its pull (a building verb that
   starts the lasso's grapple with the building as anchor, or a forced move along a cell line with the
   lasso's numbers; that item's step 3 decides after reading `JobDriver_GrapplePawn`) is factored so a
   second building can use it: one comp/verb (suggested `RM_CompTetherPull` + its properties: range,
   reel speed, cooldown, mass/body-size caps, snap chance, building-fill cap) in shared free-tier code
   both buildings load (`mandrake.rm.creaturebehaviors`, or the unified `RimMandrake.Biomes` assembly
   once `BIOME_MOD_UNIFICATION_1` lands). Whichever of the two items lands first builds it; the other
   only adds a def. If the capstan has already shipped with its pull inline, this item lifts it into the
   shared comp and repoints the capstan, behaviour unchanged.
2. **The lance, `RM_TractionLance`.** A manned emplacement (the capstan is the fixed turret; the lance is
   the crewed one, so the two read differently in play) that fires a tether and reels one visible pawn
   toward it: a downed colonist out of danger, a raider out of cover, **an ollathrix out into the sun**.
   Walls stop the pull (the shared comp's building-fill cap at full). Big targets cost more: power draw
   and tether wear scale with the target's body size.
3. **Lasso relative: the tether is stuffable by fabric**, mirroring the lasso's three tiers
   (cloth / devilstrand / hyperweave). The tether's stuff sets reach, reel strength and snap chance:
   cloth weak and snappy, devilstrand middling, **thrixweave** (the free tier's renamed hyperweave,
   `WEBWORK_BASE_PORT_BUILD_1`) best. BENCH's reading of "lasso relative"; numbers are FOUNDRY's first
   values, tuned in live play. A snapped tether is consumed and must be re-rigged (a small fabric cost).
4. **Two places to learn it (the owner's words).** One hidden research project
   (`RM_Research_TractionLance`) unlocks the lance, granted by either discovery:
   - **Webwork:** brace and cut out an intact gutter junction (`RM_Webwork_Gutter`, from
     `WEBWORK_BASE_PORT_BUILD_1`) without breaking it, then study the specimen (`RM_GutterJunction`,
     `CompStudiable`-style). Cutting it trips the web alarm (`RM_MapComponent_SenseWeb` registers the
     cut like a touch), so the owners come.
   - **Sump:** studying the capstan's preserved draw-joints (`SUMP_CAPSTAN_TURRET_BUILD_1` step 4) also
     grants it, as a second letter line: "the same pull, on a tether".
   Learned once, buildable anywhere. Guard any cross-mod grant with `PatchOperationFindMod` or a def
   existence test, never `MayRequire` on an `<Operation>` (inert in 1.6).
5. **Readable signs:** the visible tether line (fabric-coloured), the ratchet sound, a snapped-line mote
   and message naming the cause (mass, wall, wear).
6. **Mod Settings:** on/off; range; reel speed; cooldown; friendly pull; snap chance; per-stuff
   multipliers.

Depends on: `SUMP_CAPSTAN_TURRET_BUILD_1` (the pull: build once, see step 1), `WEBWORK_BASE_PORT_BUILD_1`
(thrixweave; the `RM_` gutter). Coordinate with `LASSO_CHERRYPICKER_REMOVAL_1` (the lasso defs go; the
grapple job and driver must stay loadable if reused). Art:
`infrastructure/artpipe/art_lists/webwork_turn1_2026-10-02.csv` (`RM_TractionLance_*`,
`RM_GutterJunction`).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded in the owning mod's functional script:
- One pull implementation: the capstan's and the lance's defs both name the same comp/verb class; a
  source search for a second pull implementation (a second forced-move or grapple-start site) returns 0
  hits beyond the shared class, with a sanity probe that finds the shared class.
- Quicktest: a manned `RM_TractionLance` with a thrixweave tether pulls a spawned raider N cells toward
  it (position delta read before/after); an unmanned one does nothing; a raider behind a wall is not
  pulled and the snap/blocked reason reads "wall".
- A downed colonist is pulled in with friendly pull on, and is not with it off.
- An `RM_Ollathrix` pulled from a canopy cell onto a clearing cell ends on a cell with `ShadeAt` below the
  scald threshold (the sun use works).
- Stuff: with identical targets, cloth reads a higher snap chance and shorter range than thrixweave; an
  over-mass target snaps a cloth tether (tether state `snapped`, message logged).
- Research: completing the gutter-junction study sets `RM_Research_TractionLance` finished; on a fresh
  game, completing the Sump draw-joint study sets it finished too; either way `RM_TractionLance` is
  buildable. Cutting the junction registers a touch event in `RM_MapComponent_SenseWeb`.
- Each Mod Settings toggle off removes exactly its effect.

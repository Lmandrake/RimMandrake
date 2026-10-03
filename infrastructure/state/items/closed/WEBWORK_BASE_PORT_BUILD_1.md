# WEBWORK_BASE_PORT_BUILD_1 — the free tier gets its web, its creeping front and its silk (thrixweave)

Caused by `WEBWORK_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.webwork` (folds into
`RimMandrake.Biomes` under `BIOME_MOD_UNIFICATION_1`; build where the Webwork lives on the day you start).
Design: `design/Jawa/worldbuilding/biomes/webwork_bedazzle_review_2026-10-02.md` §1 finding 1, §4 row 0,
§8. Ruling: **build first: fix the base** (decision taken by question card 2026-10-02 07:17 PDT). Already
ruled before the sitting: sitting ruling 1 (*mechanisms move to the free tier*), ruling 4 (the free-tier
silk is **thrixweave**), Q11a/Q12 (`design/RimMandrake/biome_mod_architecture.md` §7: the free mod must
look the same as the campaign one, rich enough to stand alone).

Sibling: `WEBWORK_HEAT_SHADE_BUILD_1` (heat kind and the sun-scald re-key), same ruling.

## spec

1. **Port the three web structures to `RM_`.** `RUT_Webwork_Anchor`, `RUT_Webwork_Web`,
   `RUT_Webwork_Gutter` (`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_WebworkStructures.xml`) become
   `RM_Webwork_Anchor` / `RM_Webwork_Web` / `RM_Webwork_Gutter` in the free mod, carrying the
   `WEBWORK_WEB_STRUCTURES_1` art (texPaths moved with them; the art binds by texPath) and the
   slick/locked adhesion (`RM_CompProperties_AdhesiveSlick`), the web-sense node comp
   (`RM_CompSenseWebNode`) and the quarrok's chew target (`RM_ChewableExtension`). The `RUT_` defs are
   deleted, not kept as aliases; every `RUT_` reference (twin biome, quests, ShokkweaveEconomy harvest
   nodes, scatter) is repointed in the same change. 🔴 The live campaign save may hold placed
   `RUT_Webwork_*` Things: check the save before deleting (memory: donor retirement is a mod check AND a
   save check); if any are placed, the remedy is a world-remake carry note, not a kept alias.
2. **Wire the creeping front on the free biome.** Add `RM_FrontCreepExtension` to `RM_Webwork`
   (`src/RimMandrake/Webwork/Defs/BiomeDefs/RM_Webwork_Biome.xml`) with the twin's values, pointed at the
   `RM_` structures. Delete the stale gate comment (l.26-28, "left off until `WEBWORK_WEB_STRUCTURES_1`
   ports the structures"): that item closed without porting them, and this item is the port.
3. **Thrixweave in the free tier.** The free mod renames vanilla Hyperweave to **thrixweave** (label,
   description in Webwork voice: ollathrix silk), strips it from traders (the sole-source rule from
   `SHOKKWEAVE_SOLE_SOURCE_1`, moved down a tier), and owns the harvest routes: harvest nodes on the web
   structures and the creep-web, the ollathrix butcher yield, and the scatter. Move the mechanism, not a
   copy: the campaign's `src/RimUtinni/ShokkweaveEconomy/` then **patches thrixweave to Shokkweave** (label
   and lore only) and drops its own copies of the strip and the routes. Never patch Hyperweave directly in
   the campaign layer after this. Fix `RM_Webwork_DamageDefs.xml` l.26's comment ("creates no thrixweave")
   to say what is now true.
4. **Mod Settings** (`MOD_OPTIONS_RETROFIT_1` law): on/off for the creeping front, its advance rate; on/off
   for the trader strip (the rename always applies). Defaults = shipped behaviour.

🔴 Search before building: the rename mechanism the campaign uses today (`ShokkweaveEconomy`) is the
template; read it first and move it, do not write a second one.

Depends on: nothing open. Blocks: `WEBWORK_TRACTION_LANCE_BUILD_1` (the tether stuff),
`WEBWORK_DEAD_GIANT_BUILD_1` (thrixweave from the wrappings). `WEBWORK_FIRST_SCRIPT_1` must be written
against this item's state, not today's.

## criteria

Deterministic state reads (def dump, `jawa/get_defs` reading `success`/`foundCount`, or debug `[Tool]`s),
recorded as cases in the Webwork mod's functional script (`WEBWORK_FIRST_SCRIPT_1`'s `validation.py`):
- On the free tier list (Webwork without any `mandrake.rut.*` mod): `ThingDef/RM_Webwork_Anchor`, `_Web`,
  `_Gutter` all resolve; `ThingDef/RUT_Webwork_Anchor` etc. resolve in neither tier; a repo search for
  `RUT_Webwork_Anchor|RUT_Webwork_Web|RUT_Webwork_Gutter` returns 0 hits with a sanity probe
  (`RM_Webwork_NestWall`) returning hits.
- `BiomeDef/RM_Webwork` carries `RM_FrontCreepExtension`; on a generated free-tier Webwork map,
  `RM_MapComponent_FrontCreep` reports a non-zero front cell count, and after N simulated days the count
  has grown.
- Free tier: `ThingDef/Hyperweave` label reads `thrixweave`; no trader stock generator yields it (read
  each `TraderKindDef`'s resolved stock); butchering a spawned `RM_Ollathrix` yields thrixweave; a web
  harvest node yields thrixweave.
- Campaign tier: the same def's label reads `Shokkweave`, and the strip/route patches exist exactly once
  (counted across both mods; no duplicate trader-strip operation).
- A sense-web probe: a pawn stepping onto a spawned `RM_Webwork_Web` registers a touch in
  `RM_MapComponent_SenseWeb`; a spawned `RM_Quarrok` with `RM_JobGiver_ChewAnchors` targets an
  `RM_Webwork_Anchor`.
- Each Mod Settings toggle off removes exactly its effect (one case per toggle).

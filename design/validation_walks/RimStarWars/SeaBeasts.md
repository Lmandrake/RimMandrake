# SeaBeasts — validation walk
subject: src/RimStarWars/SWBestiary  (packageId mandrake.rsw.swbestiary)
feature: sea-beasts-roster
absorbed: SeaBeasts (dying id rsw.seabeasts) folded into SWBestiary at Defs/SeaBeasts + Source/art/SeaBeasts + Textures/Pawn/Animal/SeaBeasts in Sprint wave A (commit 247cd6d40) — no longer ships alone.
deps: Ludeon.RimWorld.Odyssey (hard modDependency — Crab and Pinniped BodyDefs are Odyssey-only)
list: minimal+Ludeon.RimWorld.Odyssey
status-hint: 18 Naboo/Star Wars sea creatures across six roles (opee silt-ambushers, colo harpooners, sando leviathans, scalefish shoal grazers, a scavenger swarm, colossal filter-feeder neutrals) — zero C#, no swimmer pathgrid, plain seafloor-map animals per the ruled aquatic-movement decision. Dev/bridge-spawn only: none have wildBiomes yet (RM_SeafloorBiome does not exist), so they never wild-spawn today.

## must be true
- All 18 ThingDef/PawnKindDef pairs resolve: RSW_OpeeSeaKiller, RSW_CrimsonOpee, RSW_ShaleGorger (opee family, ThingDefs_Races/SeaBeasts_Opee.xml); RSW_ColoClawFish, RSW_AbyssalColo, RSW_ThornbackColo (colo, SeaBeasts_Colo.xml); RSW_SandoAquaMonster, RSW_ElderSando, RSW_StormSando (sando, SeaBeasts_Sando.xml); RSW_Mee, RSW_Faa, RSW_Laa (scalefish, SeaBeasts_Scalefish.xml); RSW_Yobshrimp, RSW_SiltLamprey, RSW_RustNipper (swarm, SeaBeasts_Swarm.xml); RSW_Reefback, RSW_Starmaw, RSW_Lanternwhale (colossi, SeaBeasts_Colossi.xml).
- Every one carries the five vanilla water fields (waterSeeker=true, waterCellCost=1, canFishForFood where predator, moveSpeedFactorByTerrainTag Water=2.0, a swimmingGraphicData block matching its bodyGraphicData) so it can swim shallow water on ANY map today — this is the whole point of the "plain seafloor-map animal" ruling.
- The three colossi (RSW_Reefback, RSW_Starmaw, RSW_Lanternwhale) are foodType=None, predator=false, canBePredatorPrey=false, disableMating=true, canArriveManhunter=false neutrals — they strain plankton the game does not model and carry no food need, same mechanism as the scalefish's None-foodType members.
- None of the 18 declares wildBiomes — confirms the About.xml claim that they are dev/bridge-spawn only pending RM_SeafloorBiome.
- Every lifeStage's bodyGraphicData and swimmingGraphicData point at the same texPath (Graphic_Multi fails silently on a missing facing — no magenta, no render — so a texPath drift here is invisible without a direct check).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.swbestiary" and no XML error naming any of SeaBeasts_Opee.xml / SeaBeasts_Colo.xml / SeaBeasts_Sando.xml / SeaBeasts_Scalefish.xml / SeaBeasts_Swarm.xml / SeaBeasts_Colossi.xml   # load-time; requires Odyssey active or Crab/Pinniped body ParentNames will not resolve
2. [D] def read-back: ThingDef RSW_OpeeSeaKiller exists; race/body=Crab, race/waterSeeker=true, race/waterCellCost=1, race/canFishForFood=true, race/foodType=CarnivoreAnimal, statBases/MarketValue=400
3. [D] def read-back: PawnKindDef RSW_OpeeSeaKiller exists; race=RSW_OpeeSeaKiller, moveSpeedFactorByTerrainTag[Water]=2.0, lifeStages[0]/bodyGraphicData/texPath=lifeStages[0]/swimmingGraphicData/texPath=Things/Pawn/Animal/SeaBeasts/OpeeSeaKiller/OpeeSeaKiller
4. [D] def read-back: ThingDef RSW_Reefback exists; race/body=Pinniped, race/foodType=None, race/predator=false, race/canBePredatorPrey=false, race/disableMating=true, statBases/MarketValue=8000; PawnKindDef RSW_Reefback/canArriveManhunter=false
5. [D] def read-back: repeat the (ThingDef exists, race/body correct, race/waterSeeker=true, matching PawnKindDef exists) triple for the remaining 16 defNames listed under "must be true" — cheap and mechanical, catches a copy-paste defName or texPath slip across the 6-file set
6. [D] confirm absence: none of the 18 ThingDefs' <race> block contains a <wildBiomes> element (grep the 6 XML files directly — a wildBiomes appearing on any of them contradicts the About.xml "dev/bridge-spawn only" claim and would need re-checking against RM_SeafloorBiome's existence)
7. [B] jawa/spawn_pawn {kindDef: "RSW_OpeeSeaKiller", faction: "none"} on a dev quicktest map (with water present) → returns success, one opee sea killer spawned
8. [B] jawa/spawn_pawn {kindDef: "RSW_Reefback", faction: "none"} → returns success, one reefback spawned (spot-checks a colossus at baseBodySize 32 generates without erroring on its own scale)
9. [B] jawa/list_pawns {} after steps 7-8 → 2 pawns present, races RSW_OpeeSeaKiller/RSW_Reefback, and jawa/pawn_get {pawn: <reefback id>} reports needs excluding Food (confirms foodType=None actually suppressed the food need at runtime, not just in the def)
X. [S] (human pass) the 4-facing sprite sets for all 18 creatures (Graphic_Multi's silent-fail-on-missing-facing means a broken set never magenta's — only a look catches it) and whether the colo/sando/opee/scalefish silhouettes read as their named Star Wars creature at map scale

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**In the water**
- [ ] `seabeast_drawn_while_swimming` — a sea beast entering shallow water stays
      drawn as the same creature (its `swimmingGraphicData`), never vanishing.
- [ ] `seabeast_reads_aquatic` — each of the 18 reads at play zoom as a sea
      creature (fin, tentacle, shell or maw), not a land animal standing in water.
      (guess)

**Six roles, visibly different**
- [ ] `seabeast_families_distinct` — an opee (`RSW_OpeeSeaKiller`), a colo
      (`RSW_ColoClawFish`) and a sando (`RSW_SandoAquaMonster`) side by side are
      unmistakably three different kinds of animal, not recolours.
- [ ] `seabeast_colossi_read_colossal` — `RSW_Reefback`, `RSW_Starmaw` and
      `RSW_Lanternwhale` read as enormous beside a colonist, the biggest things on
      the map.
- [ ] `seabeast_four_facings_hold` — each creature reads correctly from all four
      facings (every species ships separate north/east/south/west art).

### cannot show

- [ ] `seabeast_never_invisible_in_water` — a sea beast that disappears on a water
      cell (the silent `Graphic_Multi` facing failure the walk warns of).
- [ ] `seabeast_colossus_never_hostile_posture` — a colossus drawn charging or
      fighting; they are neutral plankton-strainers. (guess)

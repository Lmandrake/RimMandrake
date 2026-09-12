# FEVER_WOOD_MECHANICS_1 — C# mechanics kit spec (engine mapping)

Drafted 2026-09-11 against the FROZEN lore sheet
`design/Jawa/worldbuilding/biomes/the_fever_wood.md` (§4, §5, §6, §7, §7b, §8,
Owed) and the item's filing title (2026-09-07: "the Tenant as map-spanning
aquifer entity — pool-strike logic, evidence events, never-resolved rule; marsh
building-refusal terrain; pool-state intelligence; mirror-break events"). The
sheet's Owed section is the ruling scope; the filing title's four systems all
map into it below. **"The Tenant"** is the deep thing's internal working name
(from the sheet's first round; still live in `water_taxonomy.csv` row
`fever_pool`) — per hard ban §6.1 it never appears in player-facing text, so it
is used here for defNames and class names only. This spec maps the sheet's
mechanics onto the engine — it invents no lore. Anything marked **INVENTED** is
a tuning parameter this spec had to pick a starting value for; anything marked
❓ is an engine claim not verified against source and must be checked before
build.

**Source verification basis**: claims marked *(verified)* were read from the
RimSage source index this session (`mcp__rimsage__search_source` /
`read_csharp_symbol`). Same caveat as `greentide_kit_spec.md`: the index reads
as a 1.5-era decompile, so every "vanilla has no X" claim is "no X **in the
indexed source**" and carries an implicit ❓ against the live 1.6 assembly.
The sarlacc engine measurements (`sarlacc_spec.md`, 2026-08-31, rimsage-sourced)
are relied on where cited, not re-verified.

**Naming**: generic mechanisms are `RM_` (`RimMandrake.*`); Fever Wood content
defs exposing them are `RUT_` (`RimMandrake.Utinni.*`), per
`design/NAMING_SCHEME_PLAN.md`. One C# implementation per mechanic, tuned
per-biome by XML.

**Standing anchors reused from the Greentide kit** (verified there, not
re-argued here): `BiomeDef.biomeMapConditions` for standing conditions;
`GameCondition` virtuals; `RM_GenStep_RootCauseways` as the lane-painting
GenStep shape; `RM_MapComponent_LivingRegrowth` + mineable-heartwood pattern
(Greatbole class, M12 there) as the living-tree structure machinery — the
sheet's cross-flow ledger names that class as this biome's skeleton.

Scoreboard: **9 mechanics** · **3 sibling-kit reuses** (causeway GenStep shape,
LivingRegrowth/Greatbole class, growth-engine suppression grid) · **7 new RM_/
RUT_ classes** (1 L, 4 M, 2 S) · 3 owner cards open.

---

## F1. The Tenant — one aquifer, one entity, never seen (§4, §6.1)

**Player experience.** Nothing. That is the mechanic. The pools are still, the
big animals that drink at them are sometimes simply gone, and the game never
names, shows, or resolves what did it. The biome's dread is an absence
maintained by code.

**Engine route.** `RUT_MapComponent_TheTenant : MapComponent` — the Tenant is
**data, not a Thing**: it never spawns in ambient play, so hard ban §6.1 is
enforced by architecture, not discipline. On map init it registers every cell
of pool terrain (terrains carrying `RM_LurkingWaterExtension`, a
DefModExtension) as one shared body — map-spanning: every pool is one aquifer,
one creature. State per pool: **agitation** (recent disturbance) and **last
strike tick**; Scribe-saved.

**Pool-strike logic**: on interval, any pawn standing on or adjacent to
registered water (**INVENTED**: adjacency 1 cell, interval 250 ticks) accrues
exposure; a strike roll (MTB-based, **INVENTED**: MTB ~2.5 exposure-hours,
scaled up by body size — big drinkers die first, per §4 "the terribly lost")
subtracts the pawn: despawned (wild animals — no corpse, no filth), with a
single splash fleck + one heavy sound and a pool-agitation mark. Colonist/tamed
exposure behavior is **card 2** (subtract vs down-and-drag). Natives carrying
`RM_TenantTruceExtension` on their kind def are exempt (nothing native drinks
at the pools — §5; the exemption exists so roster spawns idling near water
don't get eaten by accident).

**Never-resolved rule, enforced**: no ambient IncidentDef references any
Tenant ThingDef; the strike spawns flecks and sounds only; all player-facing
strings say what was seen, never what did it ("The water closed over it.").
Linter check: no def with `RUT_Tenant` in its defName is reachable from any
IncidentDef/ThinkTree outside the plot-emergence gate (F4).

**Effort**: **M** (component + strike roll + save state). **v1: ships** — the
biome's thesis; F2/F3 read its state.

## F2. Pool evidence + mirror-break events (§4, §8, §9)

**Player experience.** The proof arrives as theatre: a caravan animal vanishes
at the water's edge; a ripple crosses a mirror that nothing touched and the
crown goes quiet; a pool your map called safe has "moved". Evidence, never an
answer.

**Engine route.** Consumers of F1's state, all cheap:

- **The terribly lost** (ambient subtraction): a low-weight ambient
  IncidentDef spawns a large wild herbivore pathing to a pool edge; F1 takes
  it from there. Zero new AI — a spawn + a forced goto job. The player who
  watches sees §4's tragedy happen; the player who doesn't finds nothing.
- **Mirror-break** (`RUT_MirrorBreakEvent`): rare event on a random registered
  pool — ripple flecks + a dread sound + **the silence beat**: reuse the
  Greentide's `RM_MapComponent_SilenceCue` (owner-ruled INTO v1 there, card 3
  of that sitting) to duck ambient sound for the window; §9's "everything
  above goes silent to watch" is the same mechanic pointed at water. Sets the
  pool's agitation high for days (**INVENTED**: 3 days), which F1 reads as a
  raised strike rate and F3 reports as "moved lately".
- **Letters**: only when a player-owned pawn is subtracted; wild losses are
  silent finds (a dropped pack saddle at the pool edge — item spawn,
  **INVENTED** flavor).

**Effort**: **S** (two IncidentDefs + fleck/sound content; silence cue is
sibling reuse). **v1: ships.**

## F3. Pool-state intelligence — the mirror list (§8 "the mirrors")

**Player experience.** Every settlement's maps mark which pools moved lately;
Sporefall sells the list. Buy it and your map view flags the agitated pools
for a while — the biome's weather report, priced in silver.

**Engine route.** `RUT_MirrorList` ThingDef (item, tradeable — stocked at
Sporefall/Wildsteam traders via trader-kind XML) + small
`RM_CompUseEffect_RevealHazards : CompUseEffect` ❓ *(CompUseEffect subclass
route assumed from vanilla artifact items; verify the exact base-class seam
before build)*: on use, reads F1's per-pool agitation and applies a timed
map-overlay flag (**INVENTED**: 15 days validity) — flagged pools draw a
warning ring while the intel is fresh (overlay drawn by F1's component;
`MapComponent` draw hooks ❓ verify `MapComponentUpdate`/overlay-drawer seam).
Stale intel is the mechanic: the list is a snapshot, agitation moves on.

**Effort**: **S/M** (use-effect + overlay draw). **v1: ships in minimal form**
(flag rings + trade stock; no GUI beyond the overlay).

## F4. The deep thing built in full — emergence capability, plot-reserved (§4, §6.1, Owed)

**Player experience** (in ordinary play): none — see F1. The build exists so
that, once, at a plotted moment, it CAN come up through the mud.

**Engine route.** Defs + art + the emergence machinery, gated OFF:

- **Body plan per the sarlacc family register** (`sarlacc_spec.md`, engine
  measurements 2026-08-31): tentacles must be PAWNS (no non-pawn animator);
  a central emerged mass as building/pawn with tentacle pawns around it;
  emergence via the `GroundSpawner` family — `BuildingGroundSpawner` exists
  *(verified, `Source/RimWorld/BuildingGroundSpawner.cs` — it even re-terrains
  for affordance on spawn, line 35)*. Defs: `RUT_TenantEmergedMass`,
  `RUT_TenantTentacle` (PawnKindDef), `RUT_TenantEmergenceSpawner`
  (GroundSpawner). Labels are evasive descriptors, never a name (§6.1) — the
  plot names it if the plot wants to.
- **Art**: commissioned under the standing art pipeline against
  `sarlacc_spec.md`'s family register (aquatic palette per §9: black water,
  oil-sheen). Rides the art queue, listed here so the item's "built in full"
  is complete.
- **The gate**: the emergence spawner def is referenced by NOTHING in this
  kit. The emergence *event* files with the plot when its moment is chosen
  (sheet's Owed, verbatim). This kit's deliverable is that the event, when
  filed, is one IncidentDef of XML.

**Effort**: **L** (creature defs + tentacle-pawn wiring + art), but all of it
off the critical path of the playable biome. **v1: defs + art ship dormant;
zero runtime presence.**

## F5. Ground building-refusal + stilts (§6.4, §7b, donor inventory)

**Player experience.** The marsh refuses heavy structures — walls sink, the
ground says no. Building means the trees, the boughways, or stilts. The donor
biome already says this; we keep it and sell the answer UP.

**Engine route.** Almost pure XML — the engine enforces
`BuildableDef.terrainAffordanceNeeded` against `TerrainDef.affordances`
everywhere already *(verified: `Source/Verse/BuildableDef.cs:52`;
`GenConstruct.cs:494+` blocks placement; `SectionLayer_BridgeProps`/
`BaseGenUtility` show the bridge-on-unbuildable pattern)*:

1. **Refusal**: audit the donor's ground terrains; every marsh/mud terrain
   carries Light at most, never Heavy (donor kept this; verify per-def at
   build — a patch per terrain that leaks Heavy).
2. **Stilts**: `RUT_StiltPlatform` TerrainDef — buildable foundation in the
   `TerrainDefOf.Bridge` mold (affordance granted: Heavy; costly wood,
   **INVENTED**: cost ≥ 2× bridge), so heavy building on the ground level is
   possible, expensive, and deliberate. No new C#.
3. **Pool water**: registered pool terrains grant NO buildable affordance at
   all — you do not bridge the mirrors (§5; also keeps F1's registry stable).
   This is the one place refusal is absolute — **the linter-checkable half of
   §6.4**.

**Effort**: **S** (XML + audit). **v1: ships.**

## F6. The boughway network — elevated lanes, slow variation (§1, §8, Owed)

**Player experience.** Living wood-roads span the map well above the pools:
fast, safe, toll-able lanes radiating between the great trunks. They seem
fixed and are not — between visits, a byway has drifted.

**Engine route.** Reuse the Greentide kit's **`RM_GenStep_RootCauseways`**
shape (M9 there) with a Fever Wood profile: anchors are the giant trunks
(F7's tree footprints), lanes are `RUT_Boughway` TerrainDef — low pathCost,
raised sprite, **affordance Medium** (boughway building per §7b: platforms
yes, bunkers no; **INVENTED** affordance tier — heavy goes on F5's stilts or
in F7's bore-caves), painted OVER whatever ground/pool lies beneath ❓
*(elevated-over-water terrain is a drawn fiction, same as vanilla bridges —
verify the donor's water terrains accept a Bridgeable-style replacement or
route lanes around pools at gen time; decide at build)*. The ground causeway
beneath (§7 "the free, wet, watched alternative") is the same GenStep's second
pass: a parallel low lane at water's edge, cheap to walk, inside F1's strike
adjacency — the price IS the mechanic, zero extra code.

**Slow variation** — "the byways slowly vary" (§5): the sheet's Owed names the
encroachment engine (`EXPLOSIVE_PLANT_GROWTH_1`). Same posture as the
Greentide's "roads slowly move between visits": needs persistent map mutation
over absences — **park the moving lanes on that engine's v2 list; v1 ships
static lanes** and the lore's "seemingly fixed" carries the theme. (The
Greentide spec already parked its identical clause there; this kit adds the
Fever Wood as second customer, strengthening the v2 case, not the v1 scope.)

**Effort**: **M** (GenStep profile + two-pass lanes). **v1: ships static.**

## F7. Bore-caves and the trunks — living rooms, sibling class (§4, §7, §8)

**Player experience.** The giant trunks are multi-tile towers; the borers'
galleries inside them are ready-made rooms. Claim one and the tree slowly
takes it back unless you seal it — the Greentide player already knows this
contract.

**Engine route.** **Pure reuse of the Greatbole class** (Greentide kit M12):
`RUT_FeverTrunk` heartwood defs on the mineable-edifice pattern +
`RM_MapComponent_LivingRegrowth` registration + the toxin-sealant contract,
retuned by XML (**INVENTED**: slower regrowth than the Greentide — this biome
is the still one). Wild bore-caves = M12's wild-bole capability (pre-carved,
part-sealed, occupant from the roster pass). Trunk placement is F6's GenStep
anchor pass. **No new C#**; the cross-flow ledger ordered exactly this reuse.

**Effort**: **S** (XML profile on the sibling's L machinery — hard dependency:
`GREENTIDE_MECHANICS_1` M12 lands first). **v1: ships after M12.**

## F8. Thornbugs — nectar for safety, fear dries the yield (§4, §6.6, §7)

**Player experience.** Thorn-shaped nectar-beasts clamped to the bark yield
sweet nectar while they feel safe; a frightened herd dries up for days. The
dairy is the alarm system — every raid costs nectar before it costs blood.

**Engine route.** Vanilla gathering machinery is the right base:
`CompHasGatherableBodyResource` *(verified,
`Source/RimWorld/CompHasGatherableBodyResource.cs` — fullness ramps in
`CompTick` gated on `Active` (faction != null), `Gathered()` pays out ×
fullness and resets)*. New subclass **`RM_CompGatherableCalmGated`**:

- Adds a **calm meter** (0–1, Scribe-saved). Fullness gain is multiplied by
  calm; a frightened herd's calm crashes to 0 and recovers over days
  (**INVENTED**: full recovery 4 days).
- **Fear sources** (map-scoped scan on interval): hostile pawns within radius
  (**INVENTED**: 40 cells — scope is **card 3**), damage to the thornbug or
  its clamped tree, gunfire nearby ❓ *(a cheap "recent combat" signal —
  verify what vanilla exposes, e.g. dangerWatcher, before inventing one)*.
- 🔴 **Ban §6.6 enforced in code, not content**: `Gathered()` override yields
  ZERO below a calm floor (**INVENTED**: 0.3) — no def, event, or mod math
  can milk a frightened herd, because the comp refuses. The gather job still
  completes (wasted trip — the player learns the contract).
- The **alarm system** is free: a `Fullness`/calm inspect-string plus a map
  alert when herd calm crashes ("The herd has gone dry.") — earlier than any
  raid letter if the fear radius sees the raid first.

Content: `RUT_Thornbug` PawnKindDef (roster pass owns stats/art),
`RUT_ThornbugNectar` ThingDef (nutrition + trade good; the liquor still input,
§8). Semi-domesticated: ships tameable, wildness mid-band.

**Effort**: **M**. **v1: ships** — the biome's economy and a hard ban ride it.

## F9. The two-front war — Ants and Feralisks (§4, §6.2, §6.3)

**Player experience.** Raids come from opposite directions: Feralisks from the
Webwork margin, the Ants from theirs. They despise each other — when both
arrive, open the gates between them and stand back. Ant raids haul thornbugs
away ALIVE; every loss is a trackable raid-back quest.

**Engine route.**

- **Two hidden plumbing FactionDefs** (`RUT_AntSwarm`, `RUT_FeraliskBrood`;
  hidden, no settlements, no comms, no goodwill): raids, lords, and mutual
  hostility all require a Faction object, and `FactionDef.permanentEnemy` +
  `permanentEnemyToEveryoneExcept` *(verified, `Source/RimWorld/FactionDef.cs:
  186–190`; enforced in `Faction.cs` and
  `GoodwillSituationWorker_PermanentEnemy`)* give "hostile to everyone,
  hate each other" as pure XML. This is the vanilla insectoid pattern —
  a hidden system faction is (this spec's reading) plumbing, not "faction
  allegiance" in §6.2's lore sense; **card 1** puts that reading to the owner.
- **Opposite directions**: each biome raid IncidentDef pins its arrival edge
  per faction (**INVENTED**: fixed compass halves per map, chosen at map init
  and persisted — "this month's raid direction" readable by watch-perches).
  ❓ verify the arrival-mode seam for forcing an edge (PawnsArrivalModeWorker)
  before build.
- **Target preference / mutual war**: permanentEnemy hostility makes them
  fight on contact for free; "prefer each other over you" is a lord-level
  nudge — ❓ verify whether duty/threat-selection exposes a faction weighting;
  if not, v1 ships contact-hostility only (the sheet's promise is that they
  CAN be left to fight, which contact hostility already delivers when the
  player opens the path).
- **Ant theft-hauling**: a steal-the-herd lord: `StealAIUtility` and
  `JobDriver_Kidnap : JobDriver_TakeAndExitMap` *(both verified;
  `LordToil_KidnapCover` shows the lord-toil shape)* — kidnap requires the
  takee downed or asleep *(verified, its `FailOn`)*, so the ant job downs the
  thornbug non-lethally first (an unclamp stun, **INVENTED**) then rides a
  kidnap-shaped `RUT_HaulPawnAndExit` job. Theft, not slaughter (§4).
- **Raid-back quest**: on ants exiting with living thornbugs, fire a
  QuestScriptDef (site with ant defenders + the stolen thornbugs recoverable
  alive; standard site-quest scaffolding, spec rides the quests skill at
  build). Every loss recoverable — §4 verbatim.

**Effort**: **M/L** (two lords + a job + a quest script; hostility is XML).
**v1: ships raids + mutual hostility + theft; the raid-back quest may trail by
one build** (loss letters must say the column can be tracked only once the
quest exists — do not promise before it ships).

---

## Reuse notes (counted, not scope)

- **Seep-oils, black water**: defs belong to `LIQUID_TYPES_MOD_1` (cross-flow
  ledger). This kit reserves nothing but the pool terrain's
  `RM_LurkingWaterExtension` hook; oil-gathering as a work type rides that
  item, at the water's edge, inside F1's adjacency — priced automatically.
- **No native chase predators** (§6.3): enforced by the roster pass (no
  pursuit AI on natives), not by this kit; noted so nobody builds one here.
- **No rain / no flowing water** (§6.5): BiomeDef weather table XML (donor
  audit at build) — no C#.

## New-C# roster

| Class | For | Effort |
|---|---|---|
| `RUT_MapComponent_TheTenant` (+ `RM_LurkingWaterExtension`, `RM_TenantTruceExtension`) | F1 | M |
| evidence/mirror-break IncidentWorkers (thin) | F2 | S |
| `RM_CompUseEffect_RevealHazards` + overlay draw | F3 | S/M |
| `RUT_TenantEmergedMass` + tentacle-pawn wiring (dormant) | F4 | L |
| — (XML only) | F5 | S |
| `RM_GenStep_RootCauseways` Fever Wood profile (sibling class) | F6 | M |
| — (XML profile on Greentide M12) | F7 | S |
| `RM_CompGatherableCalmGated` | F8 | M |
| ant/feralisk lords + `RUT_HaulPawnAndExit` + raid-back quest | F9 | M/L |

RM_ classes live in the ruled kit home (`src/RimMandrake/EnvironmentalHazards/`
or sibling per FOUNDRY's split); RUT_ content in the Fever Wood content mod.
Whether the Fever Wood follows the Greentide's standalone-mod ruling
(`GREENTIDE_STANDALONE_MOD_1`) is FOUNDRY's packaging call, not this spec's.

## Build order

1. **F1 Tenant component + F5 refusal XML** — the biome's floor: still water
   that eats, ground that refuses. Testable on a quicktest map immediately.
2. **F2 evidence events** (needs F1's state) + F3 mirror list.
3. **F6 boughways** (GenStep profile; sibling class must exist —
   `GREENTIDE_MECHANICS_1` M9), then **F7 bore-caves** (after M12).
4. **F8 thornbugs** — independent of 1–3; economy playable.
5. **F9 two-front war** — after F8 (the ants need something to steal); raids
   first, raid-back quest trailing.
6. **F4 deep-thing build** — any time; dormant by design; art rides the queue.

Cross-item dependencies: `GREENTIDE_MECHANICS_1` (F6 GenStep class, F7
Greatbole class, F2 silence cue), `EXPLOSIVE_PLANT_GROWTH_1` v2 (moving lanes
— deferred there), `LIQUID_TYPES_MOD_1` (oils), roster pass (thornbug/raider/
native kinds), `sarlacc_spec.md` (F4 family register), the plot (F4's
emergence event — files there, never here).

## Owner cards (open — this spec post-dates the closed
`KIT_SPECS_CARD_SITTING_1`; BENCH routes these three to the next card sitting)

1. **CARD — RULED 2026-09-12: hidden plumbing factions are FINE (A, spec as
   written).** Two hidden FactionDefs, vanilla-insectoid pattern, never
   player-facing; §6.2's "no faction allegiance" is a lore rule. The §4 war,
   its lords and the theft quest all stand.
2. **CARD — What the Tenant does to YOUR pawns.** Wild animals at the pools
   are subtracted outright (no corpse). For colonists/tamed: **A:** same —
   gone, one splash (maximum dread, savescum bait). **B:** dragged under —
   downed + drowning clock in the shallows, adjacent pawns can pull them out
   (a rescue window, one story per victim). Trade: A is the lore verbatim;
   B is survivable horror and shows more of the mechanic.
3. **CARD — How far does fear travel.** Thornbug calm crashes on threats
   within a radius (draft: 40 cells). **A:** radius as drafted — a far-side
   raid doesn't dry a sheltered herd. **B:** any raid on the map dries every
   herd ("every raid costs nectar", sheet verbatim, harsher). Trade: A rewards
   herd placement; B makes the sentence literally true everywhere.

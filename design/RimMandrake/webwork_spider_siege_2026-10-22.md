# The Webwork siege: the ollathrix come to you and spin (design spec, 2026-10-22)

Item: `WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE`. Written by FOUNDRY, offline. **Nothing is built;
the build waits for the owner's OK** (large autonomous build). Numbers marked PROVISIONAL are
first guesses under the 2026-10-03 provisional-numbers ruling.

**The order (owner, 2026-10-22, verbatim):** *"Make a webwork event into neighboring biomes where
spiders come in and start spinning webs as a map attack. Their version of a raid. Siege"*

**Rulings it must keep (same day, `design/RimMandrake/webworks_open_questions_2026-10-22.md`):**
- *"Webs don't creep they are made by spiders"* (the front creep was deleted, Q2). Every web in
  this event is spun by a living ollathrix doing a job you can watch and interrupt. No placement
  script lays silk on its own.
- The Webwork itself is quiet unless you walk in, judged mostly by soundscape; a ship landing in
  it always draws a response (Q7). This siege is the other direction: the Webwork coming OUT.
- No living giant; one biome per animal; the ollathrix is one race, one kind. The siege adds
  **no new creature and no siege caste**: it is ordinary `RM_Ollathrix` (combatPower 160).
- Hard bans (`design/Jawa/worldbuilding/biomes/the_webwork.md` §6): never tamed or negotiated (a
  siege has no parley, no tribute, no truce text); web comes from the mouth, never an abdomen.

## 0. Search first: what already exists

Searched `src/` (all tiers), `infrastructure/state/items/` (live and closed) and `design/` for
siege, web raid, spider raid, incursion, swarm. **No Webwork siege, raid or incursion exists.**
Machinery the siege reuses rather than rebuilds:

| need | existing piece |
|---|---|
| sticky ground web | `RM_Webwork_Strand` (local web) + `RM_CompAdhesiveSlick` → hediff `RM_Webwork_Slick` (sticky / slicked / locked) |
| shade-blotting silk sheet | `RM_Webwork_Web` (sheet web: *"thick enough to blot out the canopy above it"*) |
| anchor between two fixed points | `RM_Webwork_Anchor` (web anchor line) |
| ranged bind | `RM_Gun_LoomSpit` via `CompTurretGun`, hediff `RM_LoomBound` |
| "would this spider burn here?" | `RM_Hediff_SunScald.ExposedAt(map, cell)` — the one sun predicate |
| shade field | `RM_MapComponent_ShadeGrid`; a pitched shade piece asking for prompt recompute: `RM_CompShadeGear` |
| moving through shade | `RM_JobGiver_SeekShade`, `RM_ShadePatchGraph`, `RM_ShadeHop` |
| the web feels you | `RM_CompSenseWebNode` / `RM_MapComponent_SenseWeb` |
| cutting web yields silk | `RM_CompHarvestYield` (thrixweave = hyperweave) |
| beetles that chew anchors | `RM_JobGiver_ChewAnchors` (`RM_ChewAnchorsConsumerExtension`) |
| incident recipe and traps | skill `rimworld-custom-incidents` |

## 1. The one hard fact: they cannot cross sun

Canon (`the_webwork.md` §4, §5, §7b): *"helpless in direct sunlight"*, *"the owners physically
cannot cross open sunlit ground"*, *"Nothing they do overcomes the dry heat of the desert."* On
Ash'karr's tidally locked day side there is **no night**; only weather (overcast, rain, webfall)
and shade turn the sun off. Most maps next to the Webwork are desert (the Wildsteam seats ring its
Scald side). A siege that waits for darkness would never come on the day side.

**The answer this spec proposes: the spiders bring their own shade.** The siege is a **shade
road**: the ollathrix spin overhead silk canopy from the map edge toward the colony, one span at a
time, and stand only under what they have already spun. That is the "siege": a visible, slow,
spider-built approach line, exactly as a sapper's trench is in a human siege. It is honest to
sun-scald (they never step into sun by choice; every cell they stand on passes `ExposedAt`
= false), and it hands the player the canon defence: *"Only fire provides the kind of protection
and offense needed to drive them back."* Burn the road and the spiders on it are in the sun.

Where shade already exists (a canopy neighbour such as the Greentide, overcast or webfall weather,
night on an ordinary planet), they use it and spin less road; the road planner reads the same
predicate, so it needs no per-biome rule. This follows the One Direct Sun ruling: no
biome-specific sun, only geometry and the shade model.

🔴 **Dependency, stated plainly:** the shade grid the scald reads today is being reworked by the
Direct Sun unification and the tree shade model (`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`,
`tree_shade_model_2026-10-19.md`). The siege reads only `ExposedAt` and asks the grid to count
its canopy as overhead shade, so it follows whatever model ships. But the canopy's shade must be
re-registered with whichever model wins; that is one adapter, named in §9.

## 2. Trigger

- **Where:** a player home map on the surface layer whose world tile is a **neighbour** of a
  Webwork tile (`Find.WorldGrid` neighbours; `RM_Webwork` or `RUT_Webwork` until the end paint
  retires the twin, Q5). Never on a Webwork map itself (there, the native ambush and the
  ship-landing response are the threat). A biome on zero tiles today is expected; the siege simply
  cannot fire until the paint, and that is not a defect.
- **Vehicle:** `IncidentDef` (category `ThreatBig`, `targetTags` Map_PlayerHome,
  `layerWhitelist` surface) + `IncidentWorker_RM_WebworkSiege`. Adjacency cannot be said in XML.
  `CanFireNowSub` is cached per def per tick, so it answers the target-independent question
  ("does any player home map border the Webwork, is the setting on"); `TryExecuteWorker` re-checks
  its own target and returns **false, stamping nothing**, if that map does not qualify.
- **Weight and pacing (PROVISIONAL):** `baseChance` 1.2, `earliestDay` 20, `minRefireDays` 20,
  `minThreatPoints` 300. Shares a refire tag with nothing; it competes with ordinary raids by
  category weight.
- **Who comes:** `parms.points / 160`, clamped 2..8 ollathrix (PROVISIONAL). Spawned **awake**
  (the race's `CompCanBeDormant startsDormant` would otherwise leave a siege asleep at the edge).
- **Faction:** a lord needs a faction. Use vanilla `Faction.OfInsects` (hidden, permanently
  hostile, present in every save). ⚠️ A NEW hidden faction would have to exist when the world
  freezes (*"A faction ... absent when it freezes is absent from every player's game forever"*);
  whether 1.6 injects a missing hidden faction into an existing save is UNMEASURED, so do not
  depend on it. Letters name the ollathrix, never "insects".
- **Entry:** the map edge facing the Webwork tile, at the most shaded edge cell; if no edge cell
  within 20 cells of that side is shaded, the road starts at the edge itself (first span spun
  while the spiders shelter under a held-over sheet, §4). If even that fails, `TryExecute`
  returns false.

## 3. Phases (one `LordJob_RM_WebworkSiege`, toils in order)

1. **Arrive** (≤ 1 h). Letter, threat-big, *"The web has come out of the Webwork. N ollathrix
   are spinning a road of silk toward the colony."* Spiders gather under shade at the entry.
   Soundscape: the Webwork's web-thrum plays on the map while the siege lives (vanilla sound
   until sound work starts, 2026-10-03 ruling).
2. **Spin** (most of the siege). Each spider takes `RM_JobDriver_SpinSiegeWeb`: walk under the
   road's last span, face the next cell, work `spinTicks` (PROVISIONAL 600 = 10 s game time, with
   a progress bar and work sound), then the silk appears. The road is planned by a pure kernel
   (`RM_SiegeRoadPlanner`) over the shade grid: cheapest path from entry to the colony's
   perimeter, where a cell already in shade costs nothing to cross and an open cell costs one
   span. It prefers trees and walls as anchors. Around the road they lay snares (§4). Cap: 400
   spun cells per siege (PROVISIONAL).
3. **Press.** When the road's head is within 12 cells (PROVISIONAL) of a colony building, or
   wraps an outer wall, the lord switches to assault, **under the canopy only**: wrap doors,
   spit-bind pawns, cocoon the downed, target droids and mechanoids first (canon: *"They HATE
   droids"*). They keep spinning over the base itself, using its walls as anchors, so the roof of
   silk is how they get in.
4. **Break.** Any of: half the spiders dead; the siege has run `maxSiegeDays` (PROVISIONAL 3);
   the road behind them is cut so no shaded path leads back to the edge. Survivors with a shaded
   path walk home along the road and leave the map. Survivors without one are stranded: they hold
   the deepest shade left, and when that goes, they scald. Canon infighting: on a break, each
   stranded spider has a PROVISIONAL 30% chance to turn on the nearest other ollathrix (a scoped
   aggression mental state already exists: `RM_MentalState_ScopedAggression`).
5. **Aftermath.** What they spun stays where they spun it (spiders made it, so it is real) until
   cut or burned. Q5 asks whether it dries and falls on a desert map.

Readable-sign rule (*"no animal or pawn ever vanishes without a readable sign"*): a spider that
scalds shows the sun-scald hediff and a mote; one that leaves walks off along the road; a letter
reports the break (*"The siege has broken. K ollathrix went back into the jungle; J are dead."*).

## 4. What the spiders physically build, and how a colony beats it

| spun thing | what it does | how you defeat it |
|---|---|---|
| **silk canopy** (new `RM_Webwork_SiegeCanopy`, an overhead sheet; passable; draws over pawns) | overhead shade: `ExposedAt` reads false beneath it, so spiders can stand there; blocks the sky like a roof for shade only (not a roof for temperature or the roof grid) | **fire** (very flammable, PROVISIONAL `Flammability` 1.6); cut it (a deconstruct-like job, yields silk per Q2); shoot the spinner mid-job (the span is lost) |
| **snare web** (reuse `RM_Webwork_Strand` + `RM_CompAdhesiveSlick`) | ground web around the road; stepping in it applies `RM_Webwork_Slick` (sticky → locked) | burn it, cut it, walk around it; the slick hediff already wears off by its own stages |
| **anchor line** (reuse `RM_Webwork_Anchor`) | lets a canopy span cross a gap of open ground between two anchors (trees, walls, rock) | cut it and the spans hanging from it fall (canopy loses support) |
| **wrapped door** (state on the door, `RM_CompSilkWrap` or a map-level set) | the door will not open for anyone until cut; spiders can still break it | a pawn cuts it (one job, 4 s PROVISIONAL); fire |
| **wrapped wall** | becomes an anchor for canopy over your base | cut; or don't build walls under tree cover |
| **cocoon** (new `RM_Webwork_SiegeCocoon`, a casket holding a downed pawn) | a bound or downed pawn is wrapped where they fell; Q3 says what happens next | cut them out (rescue job); kill the spiders guarding it |
| **ranged bind** (existing loom spit, `RM_LoomBound`) | already in the race | doctors; already built |

**Counterplay summary for the player:** fire is the main answer, as canon says. Light is the
moat: a cleared, burned margin forces them to spin every cell of it, slowly, in the open, where
they can be shot. Anchor-beetles (`RM_JobGiver_ChewAnchors`) chew anchors if any are about.
Overcast weather is the danger window: the road gets cheap when the sky goes grey.

## 5. Sun-scald, honestly

- They never choose a cell where `ExposedAt` is true. The road planner, every job target and the
  lord's assault cells all filter through it. Path cost for open cells is set to impassable for
  siege pawns (a lit-ground aversion, already in canon §7b).
- A spider forced into sun (canopy burned over it, pulled by the traction lance) takes the
  existing scald build-up; nothing new.
- Day side: no night; only shade and weather. Ordinary planet: night counts as shade through the
  same predicate, so a siege there runs mostly at night with no extra rule.
- Desert dry heat: canon says they cannot overcome it. The siege does not pretend they do. The
  road is their only lifeline, it is cut by fire, and (Q5, recommended) silk dries and falls on a
  desert map within days. Q1 asks whether desert neighbours are eligible at all.

## 6. Mod Settings (Webwork's settings window, section "The siege")

| setting | default | note |
|---|---|---|
| The ollathrix lay siege to neighbouring maps | on | master switch; off = `CanFireNowSub` false, nothing else changes. Label: *affects maps next to the Webwork* |
| Siege strength | 100% | multiplies spider count from points |
| Spinning speed | 100% | multiplies `spinTicks` (inverse) |
| Longest siege | 3 days | `maxSiegeDays` |
| Spiders wrap doors | on | off = no door wrap |
| Downed colonists are cocooned | on | off = downed pawns are left as ordinary downed |
| Spun silk stays after the siege | per Q5 | |
| Test hook: ignore the Webwork-neighbour check | off | for dev fires on quicktest maps only; tooltip says so |

All-off degrades to "no siege". Defaults are the shipped behaviour.

## 7. Failure modes to design against

1. **Fired with nothing arriving** (skill trap 1): `TryExecuteWorker` returns true only after the
   spiders are spawned and the lord made.
2. **Spiders asleep at the edge**: spawn awake; a guard row checks no siege pawn is dormant.
3. **Stuck at the edge forever** (no plannable road): the planner fails → the lord goes straight
   to Break with a letter, never an idle pack. Timeout at `maxSiegeDays` regardless.
4. **Scald deaths that read as a bug**: every death in sun carries the hediff and the letter says
   why.
5. **Shade grid cost**: one prompt recompute per spun span is too many on a 400-span road; batch
   recomputes on a short interval and only around new spans.
6. **Door wrap leaking to every door**: the patch reads only the wrap state; a guard row checks
   an unwrapped door still opens.
7. **Save/load mid-spin**: lord, road plan and wrap state are Scribed; the road plan is
   recomputed on load rather than saved cell by cell.
8. **Insect-faction side effects**: Hive insects share the faction and would not fight the
   siege; accept and note it (they never meet on these maps in practice).
9. **Wild ollathrix**: factionless; untouched by the lord.
10. **Thrixweave faucet**: siege silk that yields hyperweave on cutting is a new route outside the
    Webwork (`the_webwork.md` §6 ban 4); Q2 decides it before build.
11. **Fog**: a road spun in fogged cells is still real; the letter jumps to the entry.

## 8. Tests

**Offline first (no bridge):**
- `RM_SiegeRoadPlanner` is a pure kernel with a selftest on synthetic grids: all-shade map (zero
  spans spun), all-sun map (one span per cell, path straight), wall-ring base (anchors used),
  blocked map (planner fails cleanly → Break).
- Phase machine selftest: each break condition moves to Break; road cut detection on a grid.
- Adjacency selftest with a mock world grid (Webwork neighbour yes / no / Webwork tile itself no).
- `validate_patch.py --defs` on the new IncidentDef, ThingDefs and JobDef; every def resolves in
  `src/RimMandrake/Webwork/validation.py` static checks; `selftest_sound_paths.py` for the vanilla
  sounds.
- `code_review_status.py check` on every new file.

**Live script rows** (added to `src/RimMandrake/Webwork/validation.py` and the walk
`design/validation_walks/RimMandrake/Webwork.md` `## must be true`, debug_process §2; one quicktest
map, the test-hook setting on):

| row | reads |
|---|---|
| `siege.def_resolves` | IncidentDef present, category ThreatBig |
| `siege.fires_and_spawns` | forced fire → N>0 `RM_Ollathrix` of the insect faction, none dormant |
| `siege.setting_off_refuses` | master off → CanFireNow false; control on → true |
| `siege.spins_a_span` | within 2 game hours, ≥1 `RM_Webwork_SiegeCanopy` spawned, each with a spinner job recorded |
| `siege.canopy_is_shade` | `ExposedAt` false under a canopy cell, true beside it in open sun |
| `siege.never_stands_in_sun` | sampled over 1 game hour, no siege pawn on an exposed cell unless forced |
| `siege.snares_slick` | a test pawn stepping into a snare gains `RM_Webwork_Slick` |
| `siege.door_wraps_and_cuts` | wrapped door: PawnCanOpen false; after the cut job, true; an unwrapped control door opens throughout |
| `siege.fire_strands` | burn the road behind them → lord reports stranded; spiders gain scald |
| `siege.breaks_on_losses` | kill half → lord in Break; survivors exit along the road; letter text present |
| `siege.cocoon_rescue` | downed pawn → cocoon; cut job → pawn out, alive |
| `siege.no_hyperweave_leak` | per Q2's answer: cutting siege silk yields what was ruled |

Flight is not involved (the ollathrix does not fly); no live test needs the owner present.

## 9. Build list (for when he says go)

1. IncidentDef + worker + settings (XML + small C#).
2. `LordJob_RM_WebworkSiege` with toils Arrive / Spin / Press / Break.
3. `RM_SiegeRoadPlanner` kernel + selftest.
4. `RM_JobDriver_SpinSiegeWeb` + JobDef; `RM_JobDriver_CutSilk` for doors and cocoons.
5. `RM_Webwork_SiegeCanopy`, `RM_Webwork_SiegeCocoon` ThingDefs; art through the art ledger
   (`art install`), searched first with `artpipe_state.py find`.
6. Shade adapter: canopy registers overhead shade with the grid (the `RM_CompShadeGear` prompt
   recompute pattern), re-pointed at the unified Direct Sun model when it ships.
7. Door wrap: one Harmony postfix on the door's can-open check, reading the wrap state only.
8. First script rows (§8) in the same change.

Estimate: two to three days of FOUNDRY build, plus one quicktest sitting.

## 10. Open questions for the owner

Each is a plain choice; one is recommended.

**Q1. Can they siege a desert map, where canon says they cannot beat the dry heat?**
1. **Yes, by the shade road** (this spec). Buys: the siege happens where most Webwork neighbours
   are; the road is a strong, visible siege line and fire beats it. Costs: reads canon's *"Nothing
   they do overcomes the dry heat"* as "they can come, but cannot stay".
2. **Only onto maps that already have shade** (canopy neighbours, or only while overcast/webfall).
   Buys: canon kept to the letter. Costs: on the day side, most neighbours never see a siege.
3. **Desert maps only under overcast or webfall weather, with the road as well.** Buys: a weather
   omen ("the sky went grey; they're coming"). Costs: rarer; ties the siege to the weather system.

Recommended: **1**, with Q5's "silk dries on desert" so they truly cannot stay.

**Q2. Does cutting siege silk give thrixweave (hyperweave)?**
1. **Yes, a small amount.** Buys: *"it makes treasure"*, a reward for beating a siege. Costs: a
   new route for the sole-source silk outside the Webwork (ban 4 needs an amendment).
2. **No, siege silk is worthless when cut** (it dries brittle). Buys: the sole-source law stays
   whole. Costs: beating a siege pays nothing in silk.
3. **Only the spiders' bodies yield it** (butchery, already built). Buys: law intact (butchery is an
   existing route), killing spiders pays. Costs: none new; the silk itself is inert.

Recommended: **3**.

**Q3. What happens to a colonist the spiders cocoon?**
1. **Cocooned where they fell; dies after about a day unless cut out.** Buys: a rescue clock,
   a reason to push into the road. Costs: can kill a colonist the player could not reach.
2. **Carried off along the road into the Webwork** (a kidnapping; a rescue at the Webwork later).
   Buys: the biggest story. Costs: needs animals to carry pawns (new code) and a rescue route.
3. **Cocooned but never killed by it** (bound until cut). Buys: gentlest; no surprise deaths.
   Costs: the threat is weaker.

Recommended: **1**.

**Q4. Your 2026-10-15 ruling says no new cross-biome effect. This event is one by nature.**
1. **The siege is an exception: it fires next to the Webwork whatever the neighbour biome is.**
   Buys: what you ordered ("into neighboring biomes"). Costs: one cross-biome effect we must
   validate on whatever borders the Webwork.
2. **Only onto neighbours that are our biomes.** Buys: stays inside what we validate. Costs: a
   border with a vanilla biome never gets sieged.

Recommended: **1**, since you asked for it by name; on the frozen world we can list the actual
neighbours at the end paint.

**Q5. When the siege ends, what happens to the silk they spun?**
1. **It stays until cut or burned, except on a desert map, where it dries and falls in about 5
   days.** Buys: the Webwork's mark stays on humid neighbours (made by spiders, not a creep);
   canon's dry heat wins on deserts. Costs: one decay rule to build.
2. **It stays everywhere until cut or burned.** Buys: simplest. Costs: a desert map keeps a
   jungle-silk road forever.
3. **It all falls when the siege ends.** Buys: cleanest map. Costs: a siege leaves no mark.

Recommended: **1**.

# The Webwork siege: the ollathrix come to you and spin (design spec, 2026-10-22)

Item: `WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE`. Written by FOUNDRY, offline; built by FOUNDRY the same day on the
owner's order. Numbers marked PROVISIONAL are first guesses under the 2026-10-03 provisional-numbers ruling.

**The order (owner, 2026-10-22, verbatim):** *"Make a webwork event into neighboring biomes where
spiders come in and start spinning webs as a map attack. Their version of a raid. Siege"*

**His answers to this spec's questions (by question card, 2026-10-22):** *spider siege questions →
shaded only / yields thrixweave / dies after a day / stays until cut.*
1. Only **shaded** neighbour maps are besieged. No desert map is ever besieged, so the spiders never
   need to bring shade of their own.
2. Cutting siege silk **yields thrixweave**, capped per siege so a siege is not a silk farm (§4).
3. A cocooned colonist **dies after a day** unless cut out.
4. Siege silk **stays until the player cuts or burns it**. It never dries or falls.

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
- Ban 4 (thrixweave comes only from the Webwork) gains one route by the owner's answer 2: silk the
  Webwork's own spiders spun, cut on your map, capped per siege.

## 0. Search first: what already exists

Searched `src/` (all tiers), `infrastructure/state/items/` (live and closed) and `design/` for
siege, web raid, spider raid, incursion, swarm. **No Webwork siege, raid or incursion existed.**
Machinery the siege reuses rather than rebuilds:

| need | existing piece |
|---|---|
| sticky ground web | hediff `RM_Webwork_Slick` (sticky / slicked / locked) and CreatureBehaviors' adhesive settings, the `RM_CompAdhesiveSlick` recipe |
| sheet-web look | the `RM_Webwork_Web` picture (`Things/Building/Natural/RM_Webwork_Web`) |
| wrapped-silk look for a cocoon | the urraveth's wrapped limb pile (`RM_Urraveth/RM_Urraveth_LimbPile_Wrapped`) |
| ranged bind | `RM_Gun_LoomSpit` via `CompTurretGun`, hediff `RM_LoomBound` (already on the race) |
| "would this spider burn here?" | `RM_Hediff_SunScald.ExposedAt(map, cell)` — the one sun predicate |
| "is this map shaded?" | `RM_MapComponent_ShadeGrid.ShadeAt` (roof, cast shade from trees and rock, gear) |
| walking through shade | the shade grid's sun path cost (`RM_SunHeatPatches`), already applied to every undrafted pawn on a sun-heat map |
| cutting web yields silk | the `RM_CompHarvestYield` pattern (Deconstruct drops thrixweave = Hyperweave) |
| a pawn held in a container, opened by a colonist | vanilla `Building_Casket` (`IOpenable`: right-click Open, the Open designator) |
| an animal lord that issues its own jobs | `RM_LordJob_KurrethTheft` (FeverWood) |
| incident recipe and traps | skill `rimworld-custom-incidents` |

## 1. The one hard fact: they cannot cross sun

Canon (`the_webwork.md` §4, §5, §7b): *"helpless in direct sunlight"*, *"the owners physically
cannot cross open sunlit ground"*, *"Nothing they do overcomes the dry heat of the desert."* On
Ash'karr's tidally locked day side there is no night; only weather and shade turn the sun off.

By the owner's answer 1, the siege goes only where the map already gives them shade: tree canopy,
rock, ruins. The spiders move through that shade (the shade grid's sun path cost, which every
undrafted pawn on a sun-heat map already uses) and every cell they choose to work on passes
`ExposedAt` = false. Light is the colony's moat: a cleared, sunlit margin is ground they will not
spin on. This follows the One Direct Sun ruling: no biome-specific sun, only geometry and the shade
model, so it follows whatever tree shade model ships.

## 2. Trigger

- **Where:** a player home map on the surface layer whose world tile is a **neighbour** of a
  Webwork tile (`Find.WorldGrid.GetTileNeighbors`; `RM_Webwork` or `RUT_Webwork` until the end
  paint retires the twin). Never on a Webwork map itself (there, the native ambush and the
  ship-landing response are the threat). A biome on zero tiles today is expected; the siege simply
  cannot fire until the paint, and that is not a defect.
- **Shaded (answer 1), measured, failing closed:** the map qualifies only when the shade grid can
  answer for the scald (`RM_MapComponent_ShadeGrid` present, sun heat active on the biome, the
  scald set to read tree shade) **and** at least `siegeMinShadedFraction` (PROVISIONAL 30%) of the
  sampled open-sky standable cells (every third cell each way, roofed cells left out so a roofed
  base does not count) read `ShadeAt` at or above the scald's own shade threshold. A map the grid
  cannot answer for (no grid, a biome without sun heat, a grid not yet computed, fewer than 50
  sampled cells) is **not** shaded: no siege. A desert reads almost no shade and never qualifies.
- **Vehicle:** `IncidentDef RM_WebworkSiege` (category `ThreatBig`, `targetTags` Map_PlayerHome,
  surface layer by vanilla default) + `RM_IncidentWorker_WebworkSiege`. Adjacency and shade cannot
  be said in XML. `TryExecuteWorker` re-checks its own target and returns **false, stamping
  nothing**, if that map does not qualify or nothing could be spawned.
- **Weight and pacing (PROVISIONAL):** `baseChance` 1.2, `earliestDay` 20, `minRefireDays` 20,
  `minThreatPoints` 300. Shares a refire tag with nothing; it competes with ordinary raids by
  category weight.
- **Who comes:** `parms.points / 160 × siegeStrength`, clamped 2 .. 8 × strength (PROVISIONAL).
  Spawned **awake** (the race's `CompCanBeDormant startsDormant` would otherwise leave a siege
  asleep at the edge).
- **Faction:** a lord needs a faction. Vanilla `Faction.OfInsects` (hidden, permanently hostile,
  present in every save). A NEW hidden faction would have to exist when the world freezes (*"A
  faction ... absent when it freezes is absent from every player's game forever"*), so none is
  added. Letters name the ollathrix, never "insects". No insect faction in the save: no siege.
- **Entry:** the map edge facing the Webwork tile (`WorldGrid.GetRotFromTo`), at an edge cell the
  scald reads unexposed and that can reach the colony; failing that, any reachable cell on that
  edge; failing that, any reachable edge cell. None: `TryExecute` returns false.

## 3. Phases (one `RM_LordJob_WebworkSiege`)

1. **Spin** (the siege proper). A letter, threat-big: *"The web has come out of the Webwork. N
   ollathrix have come onto the map under the trees and are spinning toward the colony."* Each
   spider takes `RM_WebSiegeSpin`: walk to a cell it chose, face it, work `spinTicks`
   (PROVISIONAL 600 = 10 s game time ÷ `siegeSpinSpeed`) with a progress bar and the tailoring
   sound, and only then does the silk appear. If it is shot, burned or pulled off mid-job, the
   span is not spun. A cell is chosen by a pure kernel (`RM_WebworkSiegeKernel.SpinScore`) over
   the cells within 8 of the spider that the scald reads **unexposed**, standable, with no edifice
   and no web already: nearer the colony scores higher, beside their own silk higher (the web
   grows from web), beside an anchor (a tree, wall or rock) higher. Cap: 400 spun cells per siege
   (PROVISIONAL). Close enemies are fought (radius 8).
2. **Press.** When any spun web lies within 12 cells (PROVISIONAL) of a colony building, or 60
   webs are spun, or 18 game hours have passed (both PROVISIONAL), the lord presses: in order of
   priority each spider cocoons a downed colonist near it (`RM_WebSiegeCocoon`), wraps an
   unwrapped colony door (`RM_WebSiegeWrapDoor`), fights (radius 20), keeps spinning, and trashes
   what is close. Mechanoids and droids are targeted by ordinary combat AI (the droid-priority
   scorer stays with `WEBWORK_MECHANICS_1`).
3. **Break.** Half the spiders dead, or `siegeMaxDays` (PROVISIONAL 3) since arrival. Survivors walk
   off the map (`LordToil_ExitMap`). A letter reports it: *"The siege has broken. K ollathrix went
   back toward the Webwork; J are dead. What they spun stays until you cut or burn it."*
4. **Aftermath (answer 4).** What they spun stays where they spun it, until cut or burned. No
   drying, no decay timer.

Readable-sign rule (*"no animal or pawn ever vanishes without a readable sign"*): a spider that
scalds shows the sun-scald hediff; one that leaves walks off; every cocoon and every cocoon death
gets its own letter; the break gets a letter with the counts.

## 4. What the spiders physically build, and how a colony beats it

| spun thing | what it does | how you defeat it |
|---|---|---|
| **siege web** (`RM_Webwork_SiegeWeb`, a sheet of sticky silk on the ground; passable, non-edifice so trees and items stay) | slows (pathCost 14) and sticks: standing in it applies `RM_Webwork_Slick` (sticky → locked) to anyone but an ollathrix (its own comp applies it, so the spiders never stick in their own silk) | **fire** (Flammability 1.6); cut it (vanilla Deconstruct, yields thrixweave, capped); shoot the spinner mid-job |
| **wrapped door** (`RM_Webwork_SiegeDoorWrap`, a silk wrap on the door's cell) | the door opens for no one while the wrap is on it (one Harmony postfix on `Building_Door.PawnCanOpen`, reading only "is a wrap on this cell") | cut it (vanilla Deconstruct, 4 s PROVISIONAL); fire |
| **cocoon** (`RM_Webwork_SiegeCocoon`, a `Building_Casket` holding a downed colonist) | a downed colonist is wrapped where they fell; after `siegeCocoonDeathHours` (default 24, answer 3) inside, they die | cut them out: right-click **Open**, or the Open designator (4 s); burning or breaking the cocoon also drops them, downed |
| **ranged bind** (existing loom spit, `RM_LoomBound`) | already in the race | doctors; already built |

**Thrixweave farm guard (answer 2):** cutting a siege web yields 2 thrixweave (PROVISIONAL), but each
siege has a total of `siegeSilkYieldCap` (default 40, PROVISIONAL): once the colony has cut that
much from one siege's webs, further cuts of that siege's silk yield nothing. Breaking a siege web by
force (fire, damage) yields nothing, so the only route is a colonist's cut. Door wraps and cocoons
yield nothing. The spiders' bodies still butcher for thrixweave as before (the existing route).

**Counterplay summary for the player:** fire is the main answer, as canon says. Light is the moat:
a cleared, sunlit margin is ground they will not spin on, so a base in the open is besieged only at
its tree line. Cut cocoons open fast; cut wraps off doors.

## 5. Sun-scald, honestly

- They never choose a work cell where `ExposedAt` is true: spin cells, cocoon targets and door
  targets all filter through it. Their walking routes take the sun path cost like every other pawn
  on a sun-heat map.
- A spider forced into sun (chasing a target, the trees burned over it, pulled by the traction
  lance) takes the existing scald build-up; nothing new.
- Night on an ordinary planet is shade through the same predicate; no extra rule.

## 6. Mod Settings (Webwork's settings window, section "The siege")

| setting | default | note |
|---|---|---|
| `siegeEnabled` — The ollathrix lay siege to shaded neighbouring maps | on | master switch; off = `CanFireNowSub` false, nothing else changes. Label: *affects maps next to the Webwork* |
| `siegeStrength` | 1.0× | multiplies spider count from points |
| `siegeSpinSpeed` | 1.0× | divides `spinTicks` |
| `siegeMaxDays` | 3 | longest siege before they leave |
| `siegeWrapDoors` | on | off = no door wrap |
| `siegeCocoonDowned` | on | off = downed colonists are left as ordinary downed |
| `siegeCocoonDeathHours` | 24 | hours inside a cocoon before death (answer 3) |
| `siegeSilkYieldCap` | 40 | thrixweave a colony can cut from one siege (0 = none) |
| `siegeMinShadedFraction` | 0.30 | share of open ground that must be shaded for a map to qualify |
| `siegeTestIgnoreMapChecks` — Test hook: ignore the Webwork-neighbour and shade checks | off | for dev fires on quicktest maps only; tooltip says so |

All-off degrades to "no siege". Defaults are the shipped behaviour. Reset per section follows the
Webwork's own `ResetFields` pattern (Webwork is not a FlowWorks-hosted mod).

## 7. Failure modes designed against

1. **Fired with nothing arriving** (skill trap 1): `TryExecuteWorker` returns true only after the
   spiders are spawned and the lord made; generated-but-unspawned pawns are discarded.
2. **Spiders asleep at the edge**: spawned awake; a live row checks no siege pawn is dormant.
3. **Nothing to spin** (no unexposed cell within reach): the spider fights or wanders near its
   duty focus; the siege still ends by losses or `siegeMaxDays`, never an endless idle pack.
4. **Scald deaths that read as a bug**: every death in sun carries the hediff.
5. **Door wrap leaking to every door**: the postfix answers false only where a wrap stands on the
   door's own cell, and is one integer compare while no wrap exists anywhere; a live row checks an
   unwrapped door still opens.
6. **Save/load mid-siege**: lord job (siege id, start tick, colony point, counters), the map
   component's per-siege yield ledger, each web's siege id and each cocoon's clock are Scribed.
7. **Insect-faction side effects**: hive insects share the faction and would not fight the siege;
   accepted (they never meet on these maps in practice).
8. **Wild ollathrix**: factionless; untouched by the lord.
9. **Thrixweave faucet**: the per-siege cap (§4); force-broken silk yields nothing.
10. **Fog**: silk spun in fogged cells is still real; the letter targets the spiders.
11. **A cocooned pawn's own wounds**: a cocoon does not tick its pawn (vanilla casket), so bleeding
    is paused and the cocoon's clock is the only killer. The cocoon letter and its inspect line
    name the hours left.

## 8. Tests

**Offline (no bridge), shipped with the build:**
- `RM_WebworkSiegeKernel` (Verse-free) is fuzzed by the Webwork selftest's `siege` family
  (`python3 src/RimMandrake/Utils/selftest_webwork_fuzz.py --fuzz-only siege`): eligibility
  (each refusal reason, fail-closed when unmeasurable, the test hook), spider count (clamps,
  monotone in points), spin score (nearer colony and beside web never score lower), press and
  break decisions, the yield cap (a siege's total never exceeds the cap however the cuts fall),
  and the cocoon clock.
- `validation.py` static: every new def parses, the incident is ThreatBig with the siege worker,
  the siege web is non-edifice, sticky, flammable, carries the capped-yield comp and has no
  killedLeavings, the door wrap and cocoon have their classes, every setting is Scribed, has a
  control and is read by code. `validate_patch.py --defs` on the new XML.
- `code_review_status.py check` on every new file.

**Live script rows** (in `src/RimMandrake/Webwork/validation.py` chain `siege`, proof class
`RM_WebworkSiegeProof`, and the walk `design/validation_walks/RimMandrake/Webwork.md`; one
quicktest map, the test hook on):

| row | reads |
|---|---|
| `defs_resolve` (existing chain) | every new def resolves live, parsed from the XML |
| `siege.setting_off_refuses` | master off → CanFireNow false, reason Disabled; control on (hook on) → true |
| `siege.unshaded_or_unbordered_map_refuses` | hook off on an ineligible map → not eligible, reason named (UNMEASURED on a real shaded neighbour) |
| `siege.fires_and_spawns_awake_ollathrix` | forced fire → one new siege lord, N>0 `RM_Ollathrix` of the insect faction, none dormant |
| `siege.spider_spins_a_web_on_an_unexposed_cell` | a spider given a spin job on the production finder's cell: real ticks until one tagged `RM_Webwork_SiegeWeb` stands there, on a cell `ExposedAt` reads false |
| `siege.siege_web_slicks_others_not_ollathrix` | a test colonist on siege silk gains `RM_Webwork_Slick`; an ollathrix on it does not |
| `siege.cut_yield_is_capped_per_siege` | 30 cuts of one siege's webs yield exactly min(cap, 30 × 2); a force-broken web yields 0 |
| `siege.wrapped_door_shut_until_cut` | wrapped door: PawnCanOpen false; after the wrap is cut, true; an unwrapped control door opens throughout |
| `siege.cocoon_cut_open_frees_the_colonist` | downed test colonist → in a cocoon; Open → out, alive, cocoon gone |
| `siege.cocoon_kills_after_the_deadline` | cocoon clock one tick short: alive; at the deadline: dead, silk suffocation on the body |
| `siege.half_lost_breaks_the_siege` | kill half → lord in `LordToil_ExitMap`; break letter sent |

Flight is not involved (the ollathrix does not fly); no live test needs the owner present.

## 9. Build (done 2026-10-22, offline)

1. `Defs/IncidentDefs/RM_WebworkSiege.xml`; `Source/RM_WebworkSiege.cs` (worker, lord job and toils,
   job givers, job drivers, map component, the siege web's capped-yield comp, cocoon and door-wrap
   classes, the door postfix); `Source/RM_WebworkSiegeProof.cs`.
2. `Defs/ThingDefs_Buildings/RM_WebworkSiege.xml` (siege web, door wrap, cocoon), `Defs/JobDefs/
   RM_WebworkSiege_Jobs.xml`, `Defs/DutyDefs/RM_WebworkSiege_Duties.xml`, `Defs/HediffDefs/
   RM_WebworkSiege_Hediffs.xml` (the cocoon death cause).
3. `Source/Kernel/RM_WebworkSiegeKernel.cs` + the `siege` fuzz family.
4. Settings in `RM_WebworkMod.cs`; Harmony added to Webwork (already loaded through
   CreatureBehaviors' hard dependency, now declared directly).
5. Art: none queued. Every new thing uses an existing Webwork picture (sheet web, wrapped limb pile).

## 10. Open questions for the owner

Each is a plain choice; one is recommended. The build ships the recommended option.

**Q4. Your 2026-10-15 ruling says no new cross-biome effect. This event is one by nature.**
1. **The siege is an exception: it fires next to the Webwork whatever the shaded neighbour biome is.**
   Buys: what you ordered ("into neighboring biomes"). Costs: one cross-biome effect we must
   validate on whatever borders the Webwork.
2. **Only onto neighbours that are our biomes.** Buys: stays inside what we validate. Costs: a
   border with a vanilla biome never gets sieged.

Recommended and built: **1**. Fact that narrows it: the shade test fails closed on any biome
without our sun-heat extension (the grid cannot answer for the scald there), so today every
vanilla neighbour already reads "not shaded"; in practice the siege reaches only our biomes until
the shade grid runs on others.

**Q6. On an ordinary planet with night, a forest map next to the Webwork is shaded by its trees
only if its biome runs our shade grid. Should the shade test also accept "it is night" there?**
1. **No: shade is geometry only** (built). Buys: one rule, the One Direct Sun ruling. Costs: a
   vanilla forest beside the Webwork on a generated planet is never besieged.
2. **Yes: night counts as shade on a biome the grid does not run on.** Buys: standalone players
   see sieges. Costs: a second shade rule outside the grid.

Recommended: **1** (the frozen world is the shipped world; no generated planets).

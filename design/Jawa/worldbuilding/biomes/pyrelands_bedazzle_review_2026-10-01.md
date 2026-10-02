# Pyrelands: bedazzle review (grandfathered sitting, movements 1-2, turn-1 card drafted)

Item: `PYRELANDS_BEDAZZLE_SITTING_1` (BENCH). Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 3.

_BENCH design pass, 2026-10-01. Third sitting of the grandfathered track, worst-first by
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Pyrelands; sitting order row 3). The sheet
`the_pyrelands.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07) and owner-ratified; its
roster was ruled in `rosters/the_pyrelands.json` and wired by `PYRELANDS_FAUNA_WIRING_1` /
`PYRELANDS_DONOR_PORT_4`. **Nothing ruled there is re-argued here.** The biome is also mid-way up the
north-star ladder (`PYRELANDS_NORTHSTAR_TRIAL_1`, `PYRELANDS_SHIP_READINESS_1`, both FOUNDRY), so every
slate row below is ordered so as not to move a bar under that trial while it runs._

Sources read, all on `origin/main`: `src/RimMandrake/Pyrelands/` (BiomeDef `Defs/BiomeDefs/Pyrelands.xml`,
`RM_PyrelandsHediffs.xml`, the 24 C# files' headers), `src/RimUtinni/PyrelandsMechanics/` (fire rite,
flame harvest, fire raid), `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`,
`Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml`, `RUT_PyrelandsPortedFauna.xml`, `RUT_Ashwallow.xml`,
`RUT_Emberscythe.xml`, `rosters/the_pyrelands.json`, the `RM_SunHeatExtension` uses in the Stillsand,
Long Shade and Forge BiomeDefs, `SOLAR_HEAT_EXPOSURE_1`, `STILLSAND_SUN_FROM_LATITUDE_1`,
`salvation_rites_2026-10-01.md`, `biome_rites_pass_2026-10-01.md` (coverage table) and
`divine_satiation_engine.md` §2.0b. Rosters were parsed as XML elements. No tile counts are reported
(the planet is painted once, at the end).

## 1. What is there: ruled vs built

### The mod is the most-built biome of the twelve

`src/RimMandrake/Pyrelands/` (`mandrake.rm.pyrelands`) is a real kit. `RM_Pyrelands` (its own
placement worker), ember grass and Rakatan quickgrass as the only wild plants (every other plant ruled
out), the four-rung ash ladder (`RM_FE_Ash_Trace` to `_Deep`), scorchable ground and firebreak
terrain, scorched ruins at mapgen (`RM_FE_ScorchRuins`), fulgurite from lightning, scorch fruit that
only grows where fire just was, the firefoam sprayer, and three weathers of its own (ash fall,
cinderfall, BlackRain, which the fire wrings out of its own smoke: no vanilla rain is in the table, so
BlackRain's roll jumps whenever a large fire burns). Two clocks run the burn: `MapComponent_BurnLine`
(the standing burn exists somewhere, always; where-is-the-burn intelligence) and
`PyrelandsFireFront` (a line of grass goes up and walks every 2 to 4 days, the owner's cadence). The
igniters' machinery ships here too: the fire-hawk's ember carry, the furnace-beast's thermal cycle,
bed-down ignition and warmth aura, burrow-on-fire, and the world-map furnace herd.

The campaign layer (`src/RimUtinni/PyrelandsMechanics/`) adds the Deep Desert Tribes' flame harvest,
the fire raid (arson-justice for an unplanned burn), and the Tribes' own fire rite
(`LordJob_RUT_FireRite`). That rite is **theirs**: a Salvation colony cannot learn another faith's
rite (ruled 2026-10-01).

### Fauna, merged (inline + patch-added), read as XML elements

The free def's `<wildAnimals>` is **13 vanilla rows** (Hare, Rat, Gazelle, Ostrich, Emu, Dromedary,
Muffalo, Iguana, Elephant, Rhinoceros, Cougar, Fennec fox, Warg). `WildAnimals_Pyrelands.xml`
**replaces** that whole list, then adds the cast. The cast as shipped:

| def | label | bs | commonality | role | origin |
|---|---|---|---|---|---|
| `RUT_FireHawk` | fire-hawk | 0.65 | 0.15 | igniter, flier (`MaxFlightTime` 30) | ours, owner-named |
| `RUT_FurnaceBeast` | furnace-beast | 3.2 | 0.08 | igniter megafauna, world-map herd | ours, owner-named |
| `RUT_Flamefang` | flamefang | 1.5 | 0.5 | venom ambusher ahead of the front | ours, owner-named |
| `RUT_Sytheclaw` | sytheclaw | 1.0 | 0.2 | fire-follower pack hunter | ours, owner card; authored for the Pyrelands |
| `RUT_Barbslinger` | barbslinger | 2.5 | 0.15 | ash-turning scorpion, tail volley | ours (re-authored off a donor) |
| `RUT_FireWasp` | fire wasp | 0.79 | 0.4 | swarm inside the heat, flier | ours (re-authored off a donor) |
| `RUT_Ashwallow` | ashwallow | 1.3 | 0.18 | burrower grazer | ours, from scratch |
| `RUT_Emberscythe` | emberscythe mantis | 1.3 | 0.05 | large predator at the burn's edge | ours (re-authored) |
| `RSW_Anooba`, `RSW_Iriaz`, `RSW_Nuna`, `RSW_Orray`, `RSW_Zeer`, `RSW_Dalgo`, `RSW_Gizka` | canon | — | 0.18 to 1.0 | the herds, the grain-forager, a predator | Star Wars canon, SWBestiary |

🔴 **Finding 1: the free tier ships the machinery and none of the animals.** All eight invented
species are `RUT_` defs in UtinniPatches, so on the free tier the Pyrelands is vanilla savanna fauna
walking through a fire ecology whose four igniters are half missing (lightning and hands remain; no
hawk, no furnace-beast). Q11a (*"rich enough to stand alone"*) fails. The remedy is ruled:
`biome_mod_architecture.md` §7 Q11a / Q12, invented names live in the free `RM_` tier, moved at the
biome's sitting. This is that sitting (§4 row 0). The seven canon rows stay in the patch layer.

🔴 **Finding 2: once the port is done, the free tier still has no herd.** The sheet calls this
*"the planet's herd country at last"* and names three families: fire-followers, burrowers and
**ash-grazers, the great herds eating the regrowth sprint**. Every herd animal in the cast (zeer,
iriaz, dalgo, nuna, gizka) is canon, so the free mod's herd country has no herd. §3 fills it.

⚠️ **Multi-homed, noted as rows, not evicted:** `RUT_Sytheclaw` is also wired into the Greentide
(`WildAnimals_Greentide.xml`) and the Contagion's `RUT_` twin; it was authored for the Pyrelands, and
those biomes' sittings rule their own rows. The canon herd rows are shared widely (gizka in four
biomes, nuna in five); each biome's sitting rules its own.

### Heat: the biome has not declared its kind

🔴 **Finding 3: the Pyrelands breaks the one-heat law twice, and both are cheap to fix.**

- **No heat kind is declared.** The law (owner, 2026-09-29/30): every extreme-heat biome declares
  `overhead`, `lowSun` or `ambient`, and takes its sun angle from its tile's latitude. The Stillsand,
  Long Shade, Flooded Canyon, Forge, Greentide and Scald carry `RM_SunHeatExtension`; the Pyrelands
  (temperature median 53.6 °C, sun median +56°, range about +21° to +84° across its scattered tiles)
  carries nothing, so its sun adds no heat and shade gear does nothing here.
- **The furnace-beast's warmth is a heat hediff.** `RM_FurnaceWarmth` (applied by
  `CompFurnaceWarmthAura`) shifts a pawn's comfort range (−14 °C cold, −6 °C heat) instead of
  changing the temperature the pawn feels. It predates the law (2026-09-10). The built sun-heat path
  (`RM_SunHeatPatches`, a postfix on `Thing.AmbientTemperature`) is exactly the hook a local warmth
  should use: a pawn near the beast simply feels a warmer temperature, and vanilla hypothermia and
  heatstroke do the rest. That keeps *"welcome company in the cold and terrible company in the dry"*
  with one kind of heat.

**Declared here (§4 row 0b):** the Pyrelands' kind is **`overhead`** (the sheet's *"hard high sun over
gold"*), with the sun angle from the map tile's latitude, and the built elevation switch
(`overheadAboveElevationDegrees`, as the Stillsand uses it) so a low-sun Pyrelands tile falls back to
`lowSun` rules. The burn itself is ordinary vanilla fire heat, not a third kind.

### Ruled mechanics, built and unbuilt

- **Built:** the standing burn and its cadence, the ash ladder, fulgurite, scorch fruit, BlackRain,
  firebreaks, scorched ruins, the fire-hawk's ember carry, the furnace-beast's thermal circuit and
  world herd, burrowing, the flame harvest, fire raids, the Tribes' rite.
- **Ruled, thin:** *"the Tribes notice how you do it"* (walking the burn-line yourself); the herds as
  *"the wealth"* (on the free tier there are none, finding 2); *"warmth on the hoof"* caravans routing
  with furnace herds toward the cold country (the world herd moves; nothing routes a caravan by it).
- **Unruled marks:** sound (7), the ship (6), learned technology (2), a Salvation rite (9).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `MapComponent_BurnLine` and `PyrelandsFireFront`: where the burn is, and when the next line walks.
- `RM_SunHeatExtension` / `RM_SunHeatPatches` / `RM_MapComponent_ShadeGrid` (CreatureBehaviors): the
  heat kind, the felt-temperature postfix, latitude-pinned sun.
- `RM_HeatSoundscapeExtension` (Long Shade): a camera-cell sound bed keyed to a map condition.
- `RM_SeekTargetExtension`, `RM_BurrowOnFireExtension`, `RM_CompVerminBreeder` (CreatureBehaviors and
  this kit).
- `Patch_LightningStrike_Fulgurite`: every lightning strike already knows where it fell.
- The Rites tab's found-rites row and `RUT_ResearchMod_GrantRite` (register §d).

### Weather, sound, ship, gods

- **Weather:** a strong HIT. Dry thunder 20, ash fall 14, cinderfall 4, BlackRain 3 (and much more
  while a big fire burns).
- **Sound:** `Ambient_NightInsects_Standard`. The sheet writes a whole soundscape (grass hiss, the
  crackle that arrives before the light, hawk screams, *"after BlackRain, the loudest silence on the
  dayside"*); none of it exists.
- **Ship:** nothing.
- **Gods:** the Tribes' rite is another faith's. The Salvation has no rite here.

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against
the sheet and the source.

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | yes | the standing burn on its own clock |
| 2 | Discoverable technology | PARTIAL | PARTIAL | firefoam sprayer, firebreak terrain | buildings, not something the colony learns |
| 3 | Unique resources | **HIT** | **HIT** | yes | scorch fruit, fulgurite, ash; campaign adds furnace hide and the flame harvest |
| 4 | Surprising creatures | MISS | **HIT** | free 0 of ours; campaign 8 | finding 1: all eight are `RUT_` |
| 5 | GIANT beast | MISS | PARTIAL | furnace-beast bs 3.2 | the sheet says *"great shimmering beasts"*; it ships calf-to-cow sized |
| 6 | Gravship touch | MISS | MISS | 0 | |
| 7 | Soundscape | MISS | MISS | night insects | the sheet's soundscape is written, not built |
| 8 | Interesting weather | **HIT** | **HIT** | yes | |
| 9 | Relationship to the gods | MISS | PARTIAL | the Tribes' rite | another faith's; no Salvation rite (scores doc read this as HIT; under the 2026-10-01 ruling it is PARTIAL) |

**Free 3 / 1 / 5. Campaign 4 / 3 / 2.** Built and ruled agree here: the Pyrelands' problem is not
unbuilt rulings but marks nobody ruled, plus the free tier's missing animals.

## 3. Roster fill

### The gaps, read from the sheet and the ruled roster only

| hole | why it is a hole | fill |
|---|---|---|
| The free tier has none of our animals | Q11a; four igniters ruled, two absent on free | **port the eight** (Q11a/Q12, ruled; §4 row 0) |
| The free tier has no herd | sheet §4: *"ash-grazers — the great herds eating the regrowth sprint"*; every herd row is canon | **the ullai** (one new `RM_` grazer, proposed below) |
| No giant | sheet §1: *"great shimmering beasts wade through it warm as stoves"*; the furnace-beast ships at bs 3.2, smaller than a vanilla thrumbo (4) | **grow the furnace-beast** (no new species; proposed below) |
| Fire-followers, burrowers | sytheclaw, emberscythe, flamefang (followers); ashwallow, orray (burrowers) | none needed |

### Proposed: one new herd and one grown giant, both free `RM_` tier, one home each

- **The ullai** (`RM_Ullai`, invented, Pyrelands accent: vowel onset, doubled consonant, *-ai*; no
  name collision in `src/` or `design/`, no Wookieepedia hit). A long-legged ash-grazer, bs about 1.8,
  herds of 8 to 20. It eats the regrowth sprint: a herd drifts to the freshest black, so **where the
  ullai graze is where it burned two days ago**, a readable map of the burn's last address. Meat,
  hide, tameable as a herd animal; the free tier's answer to *"the herds are the wealth"*. Reuses
  `RM_SeekTargetExtension` pointed at scorched terrain and `MapComponent_BurnLine`'s record. No new
  behaviour code beyond a terrain target. Static art (three facings), no animation.
- **The furnace-beast, grown** (`RM_FurnaceBeast` after the port). bs 3.2 → about **6**, a few per
  map, drawn huge on an ordinary pawn footprint (the Orun-Ghal shape). Everything it already does
  scales with it: a wider warmth (row 0b), a bigger smouldering bed, a bigger fire hazard when tamed
  (ruled tameable; the owner called that *"insane... I love it"*). Its art is a redraw at larger draw
  size, not a new rig. Commonality falls (0.08 → about 0.04) so it stays an event.

All eight ported animals keep their ruled weights. The seven canon rows stay in
`WildAnimals_Pyrelands.xml`, which shrinks to an `Add` of those seven only (it no longer replaces the
free list).

## 4. The slate

The sheet is ratified, so rows 0 to 0b are the law applied, and only the order and the new marks
(§5, §6) need the owner. Nothing here touches the north-star trial's bars except row 0, which the
trial must re-measure (it adds the `RM_` animals the trial's census reads); FOUNDRY sequences it with
`PYRELANDS_SHIP_READINESS_1`.

**0. Housekeeping (ruled by Q11a/Q12, no card needed).** Port the eight invented residents from
`RUT_` to `RM_` defs inline in `RM_Pyrelands`, replacing the 13 vanilla placeholder rows and carrying
their labels, descriptions, art, flight and comps. Repoint every C# and XML name that reads them
(`PyrelandsMechanicsDefOf`, the ember carry, the thermal cycle, burrowing, the furnace herd
seeder). Shrink `WildAnimals_Pyrelands.xml` to the seven canon rows. Size M.

**0b. The heat law (ruled 2026-09-29/30, no card needed).** Add `RM_SunHeatExtension` to
`RM_Pyrelands`: `heatKind overhead`, sun from the tile's latitude, `overheadAboveElevationDegrees`
so a low-sun tile uses `lowSun` rules, `heatScalesWithElevation true`, `heatOffsetC` an invented first
value tuned in live play. Retire the `RM_FurnaceWarmth` hediff: the furnace-beast's warmth becomes a
local felt-temperature offset through the built `Thing.AmbientTemperature` postfix, so it is
ordinary heat and ordinary cold relief. Size S.

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The herd and the giant** (§3): the ullai; the furnace-beast grown. | 4, 5 | `RM_SeekTargetExtension`, the burn line; the furnace comps | M |
| 2 | **The soundscape the sheet wrote.** Grass hiss on the open plain; the burn's crackle and roar keyed to the camera's distance from the nearest front (`MapComponent_BurnLine` knows it), arriving before the light; dry thunder with no rain in it; hawk screams over the flame line; and after BlackRain, the ambient bed cut to near nothing for a while. Placeholder audio first, as the Long Shade did. | 7 | `RM_HeatSoundscapeExtension` pattern (camera-cell bed) | S to M |
| 3 | **New marks from the GPT five, as ruled** (§5): candidates the Walking Kiln (2), Branchglass reclosers (2), the Black Column launch (6), cinder-call posts (7). | 2, 6, 7 | §5 per idea | M to L each |
| 4 | **The Salvation's rite, as ruled** (§6). | 9 | found-rites row | M |
| 5 | **Art commission.** The ullai; the furnace-beast at giant draw size; per ruled §5 idea, static art only. Check `artpipe/done/` and `_artsrc/` first; `RUT_Ashwallow`'s missing art is already on `PYRELANDS_SHIP_READINESS_1`. | all | artpipe | — |

Recommended: **0, 0b and 1 together first.** They make the free tier stand alone and bring the biome
under the heat law; the giant and the herd ride the same port.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-01/pyrelands.md` (prompt beside it), run 2026-10-01
under the standing rule: exactly five ideas, each different from the others and from every other
biome's signature (the prompt lists them all, the Lantern Deeps' and Nightside Ice's rulings
included), with research on other games and RimWorld mods cited. The prompt carried today's rulings
(no evil god; favour only through events, world state and odds; rites give cohesion, not power;
powerful tech balanced by cost; no new animation rigs; the one-heat law) and listed this sitting's own
proposals as off-limits. Model `gpt-5.6-sol`, via `codex exec`.

GPT's own check lines: verbs *rewire, ride, signal, account, temper*; systems *electrical faults,
gravship launch, colony zoning, religion and storyteller, manufacturing.*

| # | GPT's idea (faithful summary) | marks | GPT cites | BENCH judgement |
|---|---|---|---|---|
| 1 | **Branchglass reclosers.** Study enough fulgurite and a research row reveals how its branching arrests electrical faults. A built recloser on a grid line opens when a short circuit (*Zzztt*) strikes, spending a cartridge and keeping the rest of the grid alive. Free tier, M. | 2 | ONI power transformer, Factorio power switch | **Unique and portable, recommended.** It turns the sheet's *"worthless to sell, satisfying to find"* glass into something the colony *learns*, without making it sellable, and it works on any map afterwards. Powerful (it tames short circuits), balanced by cartridges and by the study needed. **UNMEASURED:** the exact vanilla short-circuit entry point; read it in RimSage before building. |
| 2 | **Ride the Black Column.** When a large burn stands near a landed gravship, the pilot may choose a column launch: a countdown during which the fire must stay big and close; if it holds, the ship gains one launch's extra lift; if the fire collapses, the launch aborts with a letter. Free tier, L. | 6 | Odyssey gravship, Surviving Mars dust storms, SOS2 ship heat | **The best ship idea any sitting has had for a fire biome**, and it is the opposite of every other biome's ship mark (the land threatens or reads the ship; here the player *uses* the land). Costs: a large build, an **UNMEASURED** Odyssey launch-capacity hook, and it asks the player to let fire stand near the hull, which is the point. Not the Leaning Scrub's (there the plain reacts to the ship). |
| 3 | **Cinder-call posts.** Cheap ceramic posts on the approach lines, each with its own note. When real fire reaches one it cracks loudly and switches chosen colonists and animals into a prepared allowed area; bass, middle and treble tell you which flank is burning without moving the camera. Free tier, M. | 7 | Factorio programmable speaker, Project Zomboid emergency broadcast | **Sound that matters, and cheap.** It is partly an automation convenience (zone switching) dressed as sound; the sound half is the strong half. Distinct from the Stillsand's Listening (that detects at range) and the Long Shade's heat bed (ambient). GPT's own first pick. |
| 4 | **The Ninth Name of Ash.** After real fire losses, the colony names up to nine lost things (people, bonded animals, masterworks, rooms) at their ash marks. Cohesion only; later the gods' events lean on what the colony does next. Campaign, L. | 9 | Ideology rituals, Frostpunk cemetery | **Not recommended.** It collides with the register: Ozzik's *Named Grief* (B5) and the Lightless Burial (B2) already name and lay down loss. Its "who notices afterwards" engine is the satiation engine that already exists. §6 carries a narrower rite instead. |
| 5 | **The Walking Kiln.** Research learned by watching fronts pass unlocks sealable kiln-beds placed in the burn's predicted path. Shape how long the fire surrounds them (firebreaks, firefoam) and the batch comes out as ceramics, glass or hard component casings; underfire wastes time, overfire ruins the batch (visibly, never vanishing). Free tier, M. | 2 | ONI kiln, Don't Starve wildfire | **Unique and the most Pyrelands of the five, recommended.** It is the sheet's own doctrine, *"burn it first — farm the fire"*, carried from agriculture into industry: the burn is a visiting workshop. Not the Forge's (lava and a vent forge, a fixed place); here the fire comes to you on its clock. Works elsewhere with your own fire, but only the Pyrelands makes it cheap. |

GPT's own build-first ranking: cinder-call posts, then the Walking Kiln. BENCH ranks the Walking Kiln
first (it fills mark 2 in the biome's own voice) and Branchglass second (portable learned tech), with
the Black Column as the ship answer if the owner wants a large build for mark 6.

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. Today's rulings bind both: **no god is evil** (Sh'kaar and Zizzik are the hungry gods);
**a rite gives cohesion, never a power** (outcomes are shared memories and the rite's own world
sign); **favour shows only through events, world state and subtle odds**, voiced by the Narrator,
never a hediff or a stat.

God balance (coverage table in `biome_rites_pass_2026-10-01.md`, plus the two sittings since):
Oomo 4 (overfed), Ohm 4, Zizzik 4 (with Nine Faults), Mob'Unloo 3, Sh'kaar 3, the rest 3. Sh'kaar has
been starved, vented and warded, but **never fed**. Zizzik has never been **vented**, but he is at
four, the cap.

**Not taken: an offering made to a fire you set** (the scores doc's seed). That is the Leaning
Scrub's Calling-Pyre (Zizzik, own field fired), already ruled as the controlled waking's form.
**Not taken: GPT's Ninth Name of Ash** (§5 row 4), a near-copy of Ozzik's Named Grief.
**Not taken: the Tribes' fire rite.** Another faith's; not learnable (ruled 2026-10-01).

### R1. The Unfought Front, for Sh'kaar: feeding (PROPOSED, recommended)

- **Grounding:** Sh'kaar is the searing sun, *"perverse: fed by destruction and exposure, including
  our own losses... then lenient a while"* (§2.0b ⑧). The Pyrelands is where the sun's heat comes
  down into the grass and burns. Every other people here fights the burn or farms it; the Salvation
  feeds it to the hungry god by **not fighting**.
- **Found:** a ring of fire-blackened marker stakes around a scar where a field once stood, and a
  burnt hull plate propped among them with a Jawa hand's scratch: the field was given, and the clan
  that gave it was not touched that season.
- **Asks:** when a wild front is walking toward the colony (the fire-front clock's line), the organiser
  stakes out one of the colony's own planted fields in its path. No firebreak is cut around it, no one
  fights fire inside the stakes, and everyone stands at the stake line and watches it go. **The
  colony does not light it**: the land's own burn takes it. The field is the cost.
- **Outcomes (cohesion only):** Poor, the front jumps the stakes and someone has to fight it after
  all (the rite breaks; a sour memory). Fair, "we gave the field" (a shared memory). Good, a stronger
  shared memory, and the Narrator speaks of Sh'kaar eating. Excellent, plus the stakes stand charred
  where they are, a mark on the map that stays. Favour, if any, shows only as Sh'kaar's lenience
  through his own events (the vanilla "fed, then lenient a while" of §2.0b), never as a buff.
- **Readable sign:** the staked, blackened field; a letter naming what was given; the stakes.
- **Collision check:** the Calling-Pyre (Leaning Scrub, Zizzik) *lights* the colony's own field as a
  last rite with herds and enemies present; here nothing is lit and no one is harmed: the act is
  restraint before a fire that was coming anyway. The Anvil Gift (Forge, Sh'kaar, venting) throws a
  weapon into lava. First **feeding** rite for Sh'kaar; he goes 3 → 4. ⚠️ The coverage table read
  *"never fed outright, as a dangerous, hungry god should be"*; today's *no god is evil* ruling is the
  case for feeding him once, here, where the sun is literally eating.

### R2. The Struck Glass, for Zizzik: venting (PROPOSED, over the cap)

- **Grounding:** Zizzik is the wrong spark; he *"rises with every breakdown, jam, fire"* (§2.0b ⑦). The
  Pyrelands' dry lightning is the wrong spark made weather, and fulgurite is where it went into the
  ground instead of into a mind or a machine.
- **Found:** a ring of old fulgurite branches laid on bare ash, one of them fused into a crown, with
  wires twisted into it the way the clan twists a bypass.
- **Asks:** during a dry thunderstorm, the colony lays a ring of fulgurite on firebreak or ash (never
  grass), and stands back. The rite ends when lightning finds the ring (the rite worker calls the
  strike at the ring; the strike is a real, visible strike).
- **Outcomes (cohesion only):** Poor, the strike lands outside the ring and lights the grass (Zizzik's
  joke). Fair, "we grounded the spark" (shared memory). Good, stronger memory and the Narrator's word
  that the spark went into the earth. Excellent, plus the ring fuses into a glass crown that stays
  (a mark, no stats).
- **Collision check:** no rite vents Zizzik (he has been warded, starved, settled with and fed).
  ⚠️ He is already at **four**, the cap; taking this means trimming one of his pitched rites (the
  Kept Mistake or the Capping) at `SALVATION_RITES_RENORMALIZE_PASS_1`.

## 7. Owner turn-1 card (DRAFT, not yet put)

Four questions, plain words. Headers are 12 characters or fewer, for `AskUserQuestion`. Above the
card, BENCH re-describes the biome in two lines: *the Pyrelands is the burning savanna, gold grass
that grows too fast and burns on its own clock every few days, with fire-hawks that carry embers,
furnace-beasts warm as stoves, and the Deep Desert Tribes farming the fire.* Already decided by
standing rulings and done without a question: the eight invented animals move into the free mod,
and the biome declares its heat (high overhead sun; the furnace-beast's warmth becomes ordinary heat
instead of a status effect).

**Q1 · header "Build first" · What should FOUNDRY build first for the Pyrelands?**
- **The animals and the heat law, together (recommended).** The eight animals move into the free
  mod, the new herd and the grown giant come with them, and the sun starts to count as heat. Buys: a
  free Pyrelands that stands alone, in one pass. Costs: a medium build that the north-star trial must
  re-measure. *Why: it fixes the biggest gap and the law breach at once.*
- **The soundscape first.** Grass hiss, the fire's roar growing as a front nears, thunder with no rain,
  the hush after black rain. Buys: the silent biome gets its voice quickly and cheaply. Costs: the free
  tier stays empty of our animals a while longer.
- **A new mark first** (whatever you pick in Q3). Buys: the newest, most surprising piece soonest.
  Costs: it lands on a free tier with no animals of its own.
- **Everything at once.** Buys: every row ordered in one go. Costs: largest and slowest to see, and
  it all competes with the north-star trial running on this biome now.

**Q2 · header "Animals" · Which animal additions do you want?**
- **Both (recommended).** The **ullai**, a new long-legged grazer in herds of 8 to 20 that always
  drifts to the freshest burned ground, so where it grazes is where it burned two days ago; and the
  **furnace-beast grown into a true giant** (about twice its size, rarer). Buys: the free mod gets its
  herd country and its giant. Costs: one new creature's art and a giant redraw. *Why: the sheet
  already promises both "the great herds" and "great shimmering beasts".*
- **Only the ullai herd.** Buys: herds on the free tier. Costs: the giant mark stays a miss.
- **Only the grown furnace-beast.** Buys: a giant with no new species. Costs: the free tier has no
  herd; its herd country is empty.
- **Neither.** Buys: nothing new to draw. Costs: both marks stay missing on the free tier.

**Q3 · header "New marks" · Which of GPT's new pieces do you want? (pick any)**
- **The Walking Kiln (learned tech, recommended).** Watch the fires pass and learn to set kiln-beds in
  a front's path; steer how long the fire sits on them and get ceramics, glass or hard casings, or a
  ruined batch if you misjudge. Buys: the biome teaches a method, in its own "farm the fire" voice.
  Costs: a medium build, and fire deliberately invited near your stuff. *Why: the most Pyrelands idea
  of the five.*
- **Branchglass breakers (learned tech, recommended).** Study lightning-glass and learn to build
  breakers that stop a short circuit from spreading through your power grid, burning a cartridge each
  time. Buys: a powerful tool that works on every map afterwards. Costs: a medium build; cartridges to
  keep stocked.
- **Ride the Black Column (ship).** When a big fire stands near your landed ship, launch on its
  updraft for one launch's extra lift; if the fire dies down, the launch aborts and tells you. Buys:
  the boldest ship idea yet, using the land instead of fearing it. Costs: a large build, and it asks
  you to let fire close to the hull.
- **Cinder-call posts (sound).** Cheap posts with different notes that crack when fire reaches them
  and send chosen people into a safe zone; the notes tell you which flank is burning. Buys: a sound
  that matters in play. Costs: a medium build, partly an automation convenience.

**Q4 · header "Rites" · Which rite should the Pyrelands teach the Salvation? (pick any)**
- **The Unfought Front, for Sh'kaar (recommended).** When a wild fire walks toward you, stake out one
  of your own fields, cut no firebreak, fight no fire inside the stakes, and watch the burn take it.
  You never light it. Buys: shared memories for the colony, and the hungry sun-god fed for the first
  time ever, shown only by his lenience in later events. Costs: a whole field's crop. *Why: it is the
  one act no other people on this plain would do, and it gives Sh'kaar his first feeding.*
- **The Struck Glass, for Zizzik.** In a dry thunderstorm, lay a ring of lightning-glass on bare ash
  and wait for lightning to find it; a miss lights the grass. Buys: shared memories, and the first
  rite that vents the spark-god. Costs: Zizzik already has four rites, so one of his unruled ones
  would have to go.
- **None for now.**

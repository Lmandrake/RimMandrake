# Pyrelands: bedazzle review (grandfathered sitting, turn 1 ruled, ticketed)

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

### Ruled: one new herd and one grown giant, both free `RM_` tier, one home each (owner turn 1, by card)

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

Owner turn 1: **animals and heat together first.** Every row below is ruled and ticketed (§7).
🔴 **Row 0 changes what the north-star trial measures** (it adds the `RM_` animals its census reads
and removes the vanilla placeholders), so `PYRELANDS_NORTHSTAR_TRIAL_1` must re-measure after it
lands; FOUNDRY sequences it with `PYRELANDS_SHIP_READINESS_1`.

**0. The animal move (ruled by Q11a/Q12).** Port the eight invented residents from `RUT_` to `RM_`
defs inline in `RM_Pyrelands`, replacing the 13 vanilla placeholder rows and carrying their labels,
descriptions, art, flight and comps. Repoint every C# and XML name that reads them
(`PyrelandsMechanicsDefOf`, the ember carry, the thermal cycle, burrowing, the furnace herd seeder).
Shrink `WildAnimals_Pyrelands.xml` to an `Add` of the seven canon rows. Size M.

**0b. The heat law (ruled 2026-09-29/30).** Add `RM_SunHeatExtension` to `RM_Pyrelands`:
`heatKind overhead`, sun from the tile's latitude, `overheadAboveElevationDegrees` so a low-sun tile
uses `lowSun` rules, `heatScalesWithElevation true`, `heatOffsetC` an invented first value tuned in
live play. Retire the `RM_FurnaceWarmth` hediff: the furnace-beast's warmth becomes a local
felt-temperature offset through the built `Thing.AmbientTemperature` postfix. Size S.

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The herd and the giant** (§3): the ullai; the furnace-beast grown to about bs 6. | 4, 5 | `RM_SeekTargetExtension`, the burn line; the furnace comps | M |
| 2 | **Lightning breakers** (§5, revised by the owner). | 2 | `RM_GlassSand`, `RM_FE_Ground_Sand`, `RM_FE_Fulgurite` | M |
| 3 | **The Struck Glass** (§6, revised by the owner). | 9 | found-rites row, `Patch_LightningStrike_Fulgurite` | M |
| 4 | **The soundscape the sheet wrote.** Grass hiss; the burn's crackle and roar keyed to the camera's distance from the nearest front, arriving before the light; dry thunder with no rain in it; hawk screams; near-silence after BlackRain. Placeholder audio first. | 7 | `RM_HeatSoundscapeExtension` pattern | S to M |
| 5 | **Art commission:** the ullai, the giant furnace-beast redraw, the breaker building, the glass ring. Lightning glass already has art (`RM_FE_Fulgurite.png`, artpipe `RM_FE_Fulgurite_real`). | all | artpipe | — |

Row 4 was not on the card; it stays as the ordered backlog for mark 7, not yet filed.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-01/pyrelands.md` (prompt beside it), run 2026-10-01
under the standing rule: exactly five ideas, each different from the others and from every other
biome's signature, with research on other games and RimWorld mods cited. Model `gpt-5.6-sol`, via
`codex exec`. The owner took one of the five, changed. The others were not taken; the consult file
keeps the record.

### Lightning breakers (ruled, revised from GPT's "Branchglass reclosers")

His words, typed: *"The Lightning breakers is a neat idea. They should be made of metal and sand in a
recipe in the forge. Only learnable here because of the frequent lightning and sandy soil. Desert sand
works just fine too once you know how"*.

- **What it is:** a power-grid breaker. When a short circuit strikes a grid, a breaker on the line
  opens and keeps the rest of the grid alive, spending itself (or a charge) as it trips. Powerful,
  balanced by its cost and by the learning gate, not by narrowing what it protects.
- **Made of:** metal and sand, by a recipe at the smithy (the forge). The sand is `RM_GlassSand`:
  shovelled here from the Pyrelands' sand ground (`RM_FE_Ground_Sand`), or from desert drifts.
- **Learned only here:** the research can be learned only on a Pyrelands map, because this is where
  frequent lightning fuses sandy soil into glass (studying fulgurite where it fell is the natural
  trigger). Once known, it works on every map, and **desert sand works just as well**.
- **Readable signs:** a tripped breaker shows its state, the power overlay shows the open line, a
  sharp crack plays, and a message names the protected and the lost sections.
- **Mod Settings:** on/off, the learning gate (Pyrelands-only on by default), recipe cost, how a trip
  is paid. **UNMEASURED:** the vanilla short-circuit entry point; read it in RimSage before building.

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. Today's rulings bind it: **no god is evil** (Sh'kaar and Zizzik are the hungry gods);
**a rite gives cohesion, never a power**; **favour shows only through events, world state and subtle
odds**, voiced by the Narrator. The blast below is a world event and a risk, not a reward.

**Not taken:** an offering made to a fire you set (the Leaning Scrub's Calling-Pyre already is one);
the Tribes' fire rite (another faith's, not learnable).

### R1. The Struck Glass, for Zizzik: feeding, by breakage (RULED, owner turn 1, revised)

His words, typed: *"Struck Glass. Make a ~ring of the lightning glass, and then during any lightning
storm step on them violently to break them. Triggers a REALLY powerful lightning blast somewhere
randomly on the map (maybe even the ship) and utter delight within the god."*

- **Grounding:** Zizzik is the wrong spark, delighted by breakage and fire (§2.0b ⑦). Lightning glass
  is the spark caught in the ground; breaking it lets the spark loose again.
- **Found:** a rough ring of old lightning-glass shards on bare ash, every piece stamped to splinters,
  with a scorched crater somewhere off across the plain.
- **Asks:** lay a rough ring of lightning glass (`RM_FE_Fulgurite`, consumed) anywhere. During **any**
  lightning storm (dry thunderstorm or ordinary thunderstorm, on any map), the participants stamp the
  pieces to break them.
- **The blast:** the rite triggers a **really powerful** lightning strike at a **random** cell on the
  map: far stronger than a vanilla strike (a real blast radius and fire), and it may land on anything,
  **the ship included**. That risk is the point; nothing aims it.
- **Outcomes (cohesion only):** shared memories by quality (the stamping as a wild, joyous act). The
  god's **utter delight** is told by the Narrator vividly and shows only through events and odds,
  never as a buff.
- **Readable sign:** the shattered ring, the strike and its crater (with new fulgurite), a letter
  naming where it fell and what it hit.
- **Collision check:** the Calling-Pyre (Zizzik, settlement) fires the colony's own field on purpose;
  Nine Faults (Zizzik, feeding) is a favour transfer on a found machine. Here a found mineral is
  broken and the strike falls where it will.

**Zizzik's rites, counted in the register with this one** (owner: *"Just leave them all for now"*,
so the four-rite cap is waived for him and nothing is cut): the controlled waking / Calling-Pyre
(ruled-merged), Nine Faults (ruled), the Struck Glass (ruled), the Kept Mistake (pitched), the Capping
(pitched). Five.

## 7. Turn 1 rulings (owner, 2026-10-01) and ticket-out

Recorded on the ledger at `571847c06` (OWNER note on this item).

| Card item | Ruling | Ticket |
|---|---|---|
| 1. Build first | **Animals and the heat law together.** | Decision taken by question card. Rows 0 and 0b. |
| 2. Animals | **Both:** the ullai herd and the furnace-beast grown into a giant. | Decision taken by question card. `PYRELANDS_ULLAI_GIANT_BUILD_1` |
| 3. New marks | **Only the lightning breakers, revised** (typed, quoted in §5). The Walking Kiln, the updraft launch and the cinder-call posts are not taken. | `PYRELANDS_LIGHTNING_BREAKER_BUILD_1` |
| 4. Rites | **Only The Struck Glass, revised** (typed, quoted in §6), added to the register as ruled. The Unfought Front is not taken. | `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` |

FOUNDRY items, each `--caused-by PYRELANDS_BEDAZZLE_SITTING_1`:

| slate row | item |
|---:|---|
| 0 | `PYRELANDS_FAUNA_TIER_PORT_BUILD_1` (the eight `RUT_` animals to `RM_`) |
| 0b | `PYRELANDS_HEAT_KIND_BUILD_1` (heat kind; furnace warmth onto the sun-heat code) |
| 1 | `PYRELANDS_ULLAI_GIANT_BUILD_1` |
| 2 | `PYRELANDS_LIGHTNING_BREAKER_BUILD_1` |
| 3 | `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` |
| 5 | art: `infrastructure/artpipe/art_lists/pyrelands_bedazzle_cast.csv` |

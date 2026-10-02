# Greentide: bedazzle review (grandfathered sitting, turn 1 drafted)

Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 6. Item to be filed by the
parent (`GREENTIDE_SCORING_SITTING_1` shape).

_BENCH design pass, 2026-10-02. Sixth sitting of the grandfathered track, worst-first by
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Greentide; sitting order row 6). The sheet
`the_greentide.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07). Already ruled and **not
re-argued here**: the risk/reward cards (`greentide_risk_reward_2026-09-22.md` Q1 survivors become
specialists, Q2 own jungle diseases, Q3 a new canopy swarm layer, Q4 danger stays flat), the tree and
understory rosters (`greentide_tree_roster_2026-09-22.md`), the dianoga's removal and its two
replacements, the **Illisk** and the **Vurrak** (`GREENTIDE_TERROR_REPLACEMENT_1`, owner card
2026-09-23), and the humming grove (camera-attached, `GREENTIDE_HUMMING_GROVE_1`). The six hard bans
of sheet §6 bind every slate row (above all: no truce; no Earth names; no flammable native flora,
fire is not the tool; no safe standing water)._

Sources read, all in the BENCH clone: `src/RimMandrake/Greentide/` (BiomeDef
`Defs/BiomeDefs/RM_Greentide_Biome.xml`, the three race files, both plant rosters, items, the
fauna-hooks patch, `About.xml`, the C# file list and `RM_GreentideMod.cs` settings), the twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml`, every op of
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml` (xpath resolved per op),
`RUT_RoilLock_BiomeWiring.xml`, `RUT_GreentideWetBulbLock_BiomeWiring.xml`, the two GenStep
registers, the placeholder Lunger/Gnawer defs, `RSW_CanopySwinger.xml`, `RUT_PyrelandsPortedFauna.xml`
(sytheclaw), `src/RimUtinni/GreentideRaidAnt/`, `src/RimMandrake/TerminalBiomes/.../RUT_SteamDevilAppears.xml`,
the items `GREENTIDE_TERROR_REPLACEMENT_1`, `GREENTIDE_MECHANICS_2`, `GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1`,
`GREENTIDE_HUMMING_GROVE_1`, the roster `rosters/the_greentide.json`, the register
`design/Jawa/salvation_rites_2026-10-01.md`, the ledger's Webwork and Sump turn rulings (2026-10-02),
and the Webwork review for shape. Rosters were parsed as XML elements; the creature census reads
descriptions, not defNames.

## 0. The Greentide in plain words (for the card)

The Greentide is the steaming river jungle of the dayside: a green ribbon a few tiles wide that
follows every river falling off the storm peaks, under full desert sun. The rivers steam all the
time and the steam cannot rise, so a hot fog rolls at waist height over black mud that swallows
dropped things and traps the careless, and the jungle grows fast enough to watch, right into your
doors. It is the loud, lawless opposite of its silent neighbour the Webwork: everything eats
everything, trees crash down all day, and the scariest sound is the moment the jungle goes quiet.
Its giant today is a tree, the greatbole, a living tower you can mine rooms into while it slowly
tries to heal you out.

## 1. What is there: ruled vs built

### A rich kit, most of it on the wrong side of the tier line

`src/RimMandrake/Greentide/` (`mandrake.rm.greentide`) ships churnmud (`RM_MapComponent_TerrainMire`,
`_MudSwallow`, `_CrossBiomeChurnmud`, the dig-out and free-mired jobs), toxin sealant and the sealed
floor, sap/resin, the frenzy disease and its survivor mark (`RM_HediffComp_MarksFeverSurvivor`), the
stench-smoke grenade, the 14-tree and 7-understory invented rosters with the free-tier greatbole
(`RM_Greatbole`, fellable, hardwood via `RM_FellableTreeExtension`), the humming grove on the
thalquith (`RM_ProximitySoundscapeExtension`), 8 invented river fish, the skerrel gall, the krannock,
the greatbole grub, a full Mod Settings screen (`RM_GreentideMod.cs`), and the steam-devil incident
fires on `RM_Greentide` from `mandrake.rm.terminalbiomes` / `mandrake.rm.environmentalhazards`.

The campaign layer (`UtinniPatches`) carries the rest of the sheet: the Roil (`RUT_RoilWeather`, whose
overlay C# already lives in the free mod), the roil lock and wet-bulb lock conditions, the dry-air
blower (`RUT_DryAirBlower`), Breaklight, the **mineable greatbole landmark**
(`RUT_GreatboleHeartwood` / `RUT_GreatboleCore`, threshold ladder, fruitfall incident that spawns the
grub), living-bole and root-causeway map generation (extensions on the twin), the 22-row canon cast,
the raid ant, and two placeholders (Lunger = alligator fields, Gnawer = recoloured squirrel).

🔴 **Finding 1: the free tier lacks the biome's spine, and none of it is IP.** The Roil, Breaklight,
the wet-bulb condition, the dry-air blower (*"the owner's machine"*, sheet §4b), root causeways and
the mineable living greatbole (sheet §7b, *"the most alien base-type in the campaign"*) are all
campaign-only, yet nothing in them is Star Wars. Q11a (*"rich enough to stand alone"*) and the
2026-09-23 split rulings (mechanisms move to the free tier) put them in `mandrake.rm.greentide`. The
free player today gets a muddy jungle with vanilla weather, no survival kit and a tree that is only
felled, never lived in.

🔴 **Finding 2: the campaign's kit is wired to the frozen twin, so it dies at the repaint.**
`RUT_RoilLock_BiomeWiring.xml` and `RUT_GreentideWetBulbLock_BiomeWiring.xml` target
`BiomeDef[defName="RUT_Greentide"]`, and the living-bole and causeway extensions sit only in
`RUT_Greentide.xml`'s `modExtensions`. When the planet is painted onto `RM_Greentide`, the campaign
Greentide loses the Roil lock, the wet-bulb lock, the boles and the causeways at once, with no error
(a patch that matches nothing logs nothing). Fixing finding 1 fixes this too: once the free def
carries the mechanisms, the campaign only re-skins them.

### Fauna, merged (inline + patch-added), read as XML elements, census by description

**Free tier, `RM_Greentide/wildAnimals` (7 rows, all vanilla):** Warg 0.25, Muffalo 0.5, Elephant 0.2,
Cobra 0.4, Megaspider 0.1, Rat 1.0, Hare 0.6. Sheet ban 2 (*no Earth-named fauna*) fails on six of
seven, and the mod's own header calls it a Core-only placeholder. The free mod's own creatures are
**in no `wildAnimals` row**: the skerrel arrives only from a disturbed gall (a plant reaction), the
krannock's def says it *"carries no commonality/band assignment"*, and the grub's only spawn route
found is the campaign's `RUT_IncidentWorker_GreatboleFruitfall` (UNMEASURED whether felling the free
`RM_Greatbole` drops one).

**Campaign, `WildAnimals_Greentide.xml`, op by op:**

| op | xpath | operation | effect |
|---|---|---|---|
| 1 | `BiomeDef[RM_Greentide]/wildAnimals` | 🔴 **Replace** | throws away the free list and seats `RUT_Sytheclaw` 0.2 |
| 2 | same | Add (`Operation MayRequire="mandrake.rsw.swbestiary"`) | 22 `RSW_` rows: gizka 1.0, clodhopper, whisperbird, worrt 0.7; shiro, shiro trap 0.5; diggerpede, klorslug, mott, nuna 0.4; convor, falumpaset, gelagrub, kinrath, canopy swinger 0.3; fambaa 0.25; peko peko 0.2; dalgo, hawkbat, hssiss 0.18; dragonsnake 0.12; lylek 0.05; beldon 0.008 |
| 3 | same | Add (`sarg.alphaanimals`) | needlepost 0.3, blood shrimp 0.2 |
| 4 | same | Add (`oskarpotocki.vfe.insectoid2`) | swarmling 0.4 |
| 5 | `RM_Greentide/wildPlants` | Add | `RUT_YearningFruit` 1.2 |
| 6, 7 | `fishTypes/freshwater_Common`, `_Uncommon` | Add | canon catches mee, faa, laa |

🔴 **Finding 3: op 1 is the Cracked Lands shape: a campaign patch that wholesale-REPLACES the free
tier's list.** Today it replaces vanilla filler, so nothing of ours is lost, but it also strips the
**Warg, the only carrier of the silence cue** (`RM_Greentide_FaunaHooks.xml`), so the campaign
Greentide has no creature that makes the jungle go quiet, though the sheet calls silence *"its
scariest signal"*. Once the free tier gets its own cast (§3), op 1 must become an Add, or it will hide
the free creatures exactly as Cracked Lands did. ⚠ Ops 2 to 4 also put `MayRequire` on a top-level
`<Operation>`, which the 1.6 engine ignores (CLAUDE.md, `PATCH_MAYREQUIRE_GUARD_INERT_1`): without
the bestiary loaded, op 2 adds 22 unresolvable names. Same sweep, listed here so it is not lost.

**Invented content sitting in the campaign tier (Q11a flags):**
- `RSW_CanopySwinger` (*"a lean, long-limbed climber… lets go, trusting the river below"*): an
  invented creature, the sheet's own Swinger sort, filed under `RSW_` because it borrows a canon
  body's art. The creature is not IP; it belongs in the free tier with its own art.
- `RUT_Sytheclaw` (*"pack predator built for the tall gold grass of the burning plains… trails the
  fire fronts"*): invented, written for the Pyrelands, cast here at 0.2. Its description has nothing
  of the Greentide in it. **Multi-homed** (Greentide + Pyrelands); listed, not evicted.
- `RUT_YearningFruit`: an invented plant (the sheet's *"the fruit yearns to be eaten"*, §4) in the
  campaign tier only.
- The ruled **Illisk** and **Vurrak** have no tier yet (`GREENTIDE_TERROR_REPLACEMENT_1`, open); both
  names are invented, so Q11a points them at `RM_`.
- Placeholders `RUT_Placeholder_GreentideLunger` (vanilla alligator fields) and `_Gnawer` (a recoloured
  squirrel) are Earth animals under ban 2; neither is in any roster. The Gnawer is now the krannock;
  the Lunger is still owed a real creature.

🔴 **Finding 4: the header says the canopy swinger "fills the reserved slot" of the dianoga. It does
not.** The owner's ruling filled that slot with **two** new terrors, the Illisk and the Vurrak
(`GREENTIDE_TERROR_REPLACEMENT_1`, card 2026-09-23); the swinger is a harmless climber. The comment
should say so (correct on sight; the dianoga stays out, per the owner's 2026-09-23 ruling).

**Dianoga:** absent from both files, as ruled. Not proposed anywhere below.

**Multi-homed species** (listed only, never evicted; each goes to that biome's own sheet): `RUT_Sytheclaw`
(Pyrelands); `AA_Needlepost` (Arid Shrubland, per the noncanon-names census); `AA_SmallButterfly` is
named for the Greentide and Fever Wood by the owner's own placement but is not wired here. The 22
canon ports were not re-censused for other homes this pass (UNMEASURED; the 55-species figure of
2026-09-22 includes some of them).

### Flora, merged

Free: 14 invented trees (veluthar, kaddrath, mourvel, sarnstilt, ghemmel, nemmer, mirrelbole, zhorrel,
brunnock, vurmeloth, quathis, cundral, thalquith the humming tree, gorbeleth), the greatbole at 0.03,
7 invented understory plants (brakkel the forage staple, tumbel, sarquin, phorrik, wollick, maddrick,
illurin), plus vanilla `Plant_Grass` 2.0 and `Plant_TallGrass` 1.0 kept as floor filler (ban 2 says
*no vanilla-Earth flora*; generic grass was a build-seat call, flagged here, not argued). Campaign
adds the yearning fruit. The twin's 8 canon plants wait on `DONOR_DEFS_PORT_TO_OURS_1` and are not
patched on (correctly; casting donor names is forbidden). The campaign op 5 is an **Add**, so the
free flora survives: good.

### Heat

`RM_SunHeatExtension heatKind ambient` is declared (steam: shade does nothing), offset 8 °C, an
invented first value. One heat; the wet-bulb lock is a campaign map condition over vanilla heat, not a
new kind. Consistent with the law; nothing owed.

### Ruled mechanics, built and unbuilt

- **Built (free):** churnmud mire/swallow/dig-out, sealant floor, sap/resin, frenzy disease + survivor
  mark, seek-shade (on Muffalo), silence cue (on Warg), humming grove, the three owned creatures,
  greatbole felling + hardwood + the fruit economy, fish, Mod Settings, steam devils.
- **Built (campaign only):** Roil, roil lock, wet-bulb lock, Breaklight, dry-air blower, mineable
  greatbole landmark + ladder + fruitfall, living-bole and causeway generation, raid ant.
- **Built, wired to nothing:** the Shatterer tree-felling aura (`fellsTreesBelowHealthFraction` on
  `HediffComp_PeriodicAreaAttack`), the Lunger ambush (`RM_CompAquaticAmbusher`), the gnaw AI's
  carrier krannock (no roster row).
- **Ruled, unbuilt:** the Illisk and the Vurrak; grazing suppresses encroachment (blocked on
  `EXPLOSIVE_PLANT_GROWTH_1`); the greatbole's song, thermal sanctuary and pilgrims
  (`GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1`); river salinity and river graves (sheet "Owed").
- **Unruled marks:** learned technology (2), a living giant (5), the ship (6), a free sky (8), a
  Salvation rite (9).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `HediffComp_PeriodicAreaAttack.fellsTreesBelowHealthFraction` (the Shatterer's whole behaviour) and
  `RM_TreeFallUtility` / `RM_FellableTreeExtension` (the fall itself).
- `RM_CompAquaticAmbusher` (the Lunger), `RM_GnawTreeBaseExtension` + JobGiver (the Gnawer).
- `RM_MapComponent_SilenceCue` + `RM_SilenceAuraExtension`; `RM_ProximitySoundscapeExtension`.
- `RM_WeatherOverlay_GreentideRoil` (already free-tier C#), `RM_MapComponent_RoilVortexSpawner`,
  `RUT_IncidentWorker_SteamDevil` (free mod, campaign prefix: a naming leak to fix on the move).
- `RM_MapComponent_LivingRegrowth` + `RM_ToxinSealant` (regrowth and its one counter).
- `RM_CompDryFieldEmitter` (the blower's free-tier engine) and `RM_SeekShadeExtension`.
- `RM_MapComponent_MudSwallow` (buried things as a map record) and `RM_BuriedCache`.
- The Rites tab's found-rites row and `RUT_ResearchMod_GrantRite` (register §d).

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against
the sheet, the rulings and the source. Two marks move from the scores doc, both on evidence.

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | churnmud, buried caches, frenzy + fever mark: both | the greatbole you live in is campaign-only (finding 1) |
| 2 | Discoverable technology | PARTIAL | PARTIAL | sealant, stench grenade (recipes) | nothing is learned here and kept |
| 3 | Unique resources | **HIT** | **HIT** | greatbole hardwood, fruit, royal rind, sap/resin, sealant, skerrel gall, brakkel, fish: both | greenwood and the bottled growth extract (sheet §7) are campaign or unbuilt |
| 4 | Surprising creatures | PARTIAL | **HIT** | skerrel, krannock, grub: both, but in no free roster row; campaign adds 22 canon + raid ant | the free list is vanilla filler (finding 3); Illisk and Vurrak ruled, unbuilt |
| 5 | GIANT beast | MISS | PARTIAL | greatbole (a tree); campaign: fambaa 0.25, beldon 0.008 (canon, bs 6) | **moved from PARTIAL**: the free tier has no giant beast at all; the sheet's Shatterers exist only as an unwired aura |
| 6 | Gravship touch | MISS | MISS | 0 | |
| 7 | Soundscape | **HIT** | **HIT** | humming grove both; silence cue free only | campaign op 1 drops the Warg, the silence cue's only carrier (finding 3) |
| 8 | Interesting weather | PARTIAL | **HIT** | free: steam devils (incident); campaign: Roil, Breaklight, roil and wet-bulb locks | **moved from MISS**: steam devils already fire on the free def; the sky itself is vanilla. Campaign HIT is on the twin only (finding 2) |
| 9 | Relationship to the gods | MISS | MISS | 0 | no god, precept or shrine |

**Free 3 HIT / 4 PARTIAL / 2 MISS. Campaign 5 HIT / 2 PARTIAL / 2 MISS.** The scores doc had free
3/3/3; the giant drops to MISS and the weather rises to PARTIAL. Unlike the Webwork, most of the
Greentide's free-tier trouble is **built-but-misplaced** (campaign-only kit, an unwired Shatterer, an
empty roster), not unbuilt.

**Rite: none.** The scores doc's hint (a rite that marks or consecrates fever survivors) collides
with the ruled survivor mark, which already *is* the marking; and Sh'kaar, Ishko, Mob'Unloo, Oomo
and Ohm are all now at the cap of four (Sh'kaar took the Felled Noon and Ishko the Sinking on
2026-10-02). §6 offers rites for the three gods with room: Ozzik, Rekko, Ta'Baa.

## 3. Roster fill

### The gaps, read from the sheet's six fauna sorts and the ruled roster only

| sort (sheet §4) | free tier today | campaign today | fill |
|---|---|---|---|
| Gnawers | krannock built, no roster row | same, no row | **wire the krannock** into `wildAnimals` (no new creature) |
| **Shatterers** (the giant) | nothing; aura unwired | fambaa, beldon at trace (canon, not Shatterers) | **the thurrock**, new `RM_` giant, below |
| Brakes (big fast grazers) | Muffalo, Elephant (vanilla) | gizka, falumpaset, mott (canon) | **the sulleth**, new `RM_` grazer, below |
| Lungers | nothing (placeholder alligator, campaign, unused) | same | **the dhollock**, new `RM_` lunger, below; plus the ruled Illisk and Vurrak |
| Swingers | nothing | `RSW_CanopySwinger` (invented) | **move the swinger to `RM_`** with its own art (the invented creature, not the canon body) |
| Fliers (everywhere, screaming) | nothing | whisperbird, convor, hawkbat (canon) | **the yammeth**, new `RM_` flier, below |

Names are in the Greentide accent (the tree roster's *-eth/-ock/-el* endings, doubled *ll/mm/rr*,
shared with the Fever Wood by ruling). Collision-proven on both instruments 2026-10-02: zero hits in
`src/`, `design/`, `infrastructure/`, and zero Wookieepedia search results for thurrock, sulleth,
dhollock, yammeth (sanity probes: `wyyyschokk` returns 10 on Wookieepedia, `krannock` returns 3 files
in `src/`; *kerrith* and *mirreth* were rejected on hits). All four are one-home, free tier, and alien
in colour. None is a neighbour's species; none is fire-themed (§4b); none is Earth-nameable.

- **The thurrock** (`RM_Thurrock`, the Shatterer, the giant). A towering, slab-shouldered browser,
  bs about 8, drawn huge on an ordinary footprint (no new rig), hide a wet copper-teal sheened with
  mineral bloom, a short trunk-like upper lip for stripping canopy. It knocks trees down *as a way of
  life*: to feed on the crowns, to cross, and in rut to brawl. A herd passing a treeline is a
  weather event: crash after crash, the fallen trunks open sun-gaps and drop greenwood across the
  causeways. Provoked, it is a living siege engine that shoulders walls the way it shoulders trees.
  **Reuses all of it:** the built Shatterer aura (`fellsTreesBelowHealthFraction`), `RM_TreeFallUtility`
  for the fall; the one new piece is the "always has this hediff at spawn" wiring the krannock pass
  found missing (a small `CompProperties` that adds a hediff on spawn, S). Wild, never a mount.
  *Not a neighbour's giant:* the furnace-beast is warmth, the tar beast a catastrophe you evacuate,
  the hessarund a ridge, the urraveth a skeleton; the thurrock is **the jungle's third feller**, the
  biome's percussion made flesh, and the reason the canopy has holes.
- **The sulleth** (`RM_Sulleth`, the Brake). A big, fast-metabolism grazer in loose herds, bs about 2,
  long low body, hide a dusky violet with lime-green flank bars, always eating, always shitting (the
  carpet of filth and sprouts is the strategy working, sheet §4). Herds mow the growth line. When
  `EXPLOSIVE_PLANT_GROWTH_1` lands, a penned herd suppresses encroachment (ruled sort; the hook is
  already specced). Tameable as livestock is allowed (no truce ban touches grazers).
- **The dhollock** (`RM_Dhollock`, the Lunger). A long, flat river ambusher, bs about 2.5, back a
  mottled slate-blue with ochre eye-ridges, invisible on deep water until the lunge
  (`RM_CompAquaticAmbusher`, built, settings toggle #11). Replaces the alligator placeholder outright.
  It sits *inside* the deep water; the ruled Vurrak owns the bank and the Illisk the open reach, so
  the three divide the water rather than repeat each other.
- **The yammeth** (`RM_Yammeth`, the Flier). A screaming canopy flier in flocks, bs about 0.3, real
  1.6 flight (`MaxFlightTime`, Locust shape, `canLeaveMapFlying`), plumage-like membranes of hot
  magenta and acid yellow. **Its calls are the soundscape's top layer, and it is the silence cue's
  free-tier carrier:** a flock that falls silent is the tell that something big is near
  (`RM_SilenceAuraExtension` moves off the Warg onto the predators; the yammeth is the one that
  *stops*). No animated flight frames needed (flight without frames is correct, plainer).
- **Wire, don't invent:** krannock into `wildAnimals`; skerrel stays plant-spawned (the gall is the
  creature's home, by design); the grub gets a free spawn route if felling `RM_Greatbole` lacks one
  (UNMEASURED, check the fell drop first).
- **The vanilla seven come out** of the free list once these land (Warg's silence aura moves to the
  dhollock and thurrock; Muffalo's seek-shade demo moves to the sulleth).

## 4. The slate

Proposed for owner turn 1. Rows 0 and 0b execute existing rulings (Q11a, the 2026-09-23 split
rulings, the sheet's fauna sorts, `GREENTIDE_TERROR_REPLACEMENT_1`); rows 1 onward need his word.
Nothing here touches tiles.

**0. The free tier gets its spine (ruled: Q11a, sitting split rulings; findings 1 and 2).** Move into
`mandrake.rm.greentide`, under `RM_` names and Mod Settings toggles: the Roil weather (its overlay is
already free C#), Breaklight, the wet-bulb condition, the dry-air blower (`RM_CompDryFieldEmitter`
exists free), root-causeway and living-bole generation as extensions on `RM_Greentide`, and the
mineable greatbole landmark (heartwood, core, regrowth, sealant, the ladder and fruitfall). Rename the
free-mod `RUT_IncidentWorker_SteamDevil` / `RUT_SteamDevilAppears` to `RM_`. The campaign then only
re-skins (names, canon cast, Wildsteam). Retarget or delete the two `RUT_Greentide` biome-condition
patches in the same change. Size L (mostly moves, no new design).

**0b. The cast (ruled sorts; §3).** Author the thurrock, sulleth, dhollock and yammeth; move the
canopy swinger to `RM_` with its own art; wire the krannock; build the ruled Illisk and Vurrak in the
`RM_` tier; take the vanilla seven out of the free list. Then change campaign op 1 from **Replace** to
**Add** (finding 3) and correct the "fills the reserved slot" comment (finding 4). Size L (four new
creatures, two ruled ones, art).

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The giant** (§3 thurrock, optionally with §5 idea 2's single moult): the Shatterer as a living tree-feller herd; the moult makes one visit a contested feast of plate and meat. | 5 | Shatterer aura, `RM_TreeFallUtility`, a spawn-hediff comp (S) | M (thurrock) / L (with moult) |
| 2 | **Nethr lace** (§5 idea 1): observe a severed native branch close its own vessels; research a cartridge that stops all bleeding, usable everywhere. | 2 | sap/resin (free), vanilla research | M |
| 3 | **Skrith rasp** (§5 idea 3): a colonial organism rasps exposed metal, the landed ship included; scrape it off by hand; the bite scars fly home and the rasp dies away from the jungle. | 6 | `RM_CompDryFieldEmitter` (the blower keeps it off), vanilla hit points | M |
| 4 | **Work between the crashes** (§5 idea 5): the jungle's noise masks your work; creatures hear tools in the quiet and come. | 7 | silence cue, tree-fall callbacks, the yammeth's calls | M |
| 5 | **A Salvation rite** (§6 R1, R2, or §5 idea 4). | 9 | found-rites row, `RUT_ResearchMod_GrantRite` | M |
| 6 | **Art commission:** thurrock (two body states if the moult is taken), sulleth, dhollock, yammeth, the free swinger, Illisk, Vurrak, the lace and its branch specimen, the rasp marks, the rite's inscription. | all | artpipe (check existing renders first) | — |

🔴 **Sequencing:** row 0 first. Row 3 needs the free blower (row 0) as its counter; row 4 needs the yammeth
and the silence-cue carriers (row 0b); row 1 rides row 0b's art batch. Mark 8 on the free tier is
filled by row 0 itself (the Roil and Breaklight move down), so no new weather is proposed.
`GREENTIDE_FIRST_SCRIPT_1` should be written against row 0's state, not today's.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-02/greentide_gpt.md` (prompt beside it,
`greentide_gpt.prompt.md`), run 2026-10-02 under the standing rule (`BEDAZZLE_TOP_SHAPE_PROGRAM_1`,
ruling 2026-10-01): exactly five ideas, different from each other (GPT's own check: verbs stabilize /
contest / scrape / declare / mask; systems emergency medicine / megafauna life cycle / ship-carried
building damage / ideology and incident history / acoustic detection) and from every other biome's
signature, which the prompt listed in full, **including the Webwork's 2026-10-02 rulings** (dead
urraveth, traction lance, Felled Noon) and its unchosen pitches. Model `gpt-6.1-sol`, high effort,
via `gpt_consult.py`, answered in 753 s. GPT cites Green Hell, VFE Ancients, Grounded, VFE Insectoids 2,
Subnautica, Odyssey, Ideology, VFE Tribals, Rain World and Project Zomboid; its links are not verified
here. Names checked: *varkhoss* is clear on both instruments; **nethr** (5 repo files) and **skrith**
(1 repo file) collide in `src/`/`design/` and must be renamed at build (zero Wookieepedia hits each).

| # | GPT's idea | mark | tier | size | BENCH read |
|---|---|---|---|---|---|
| 1 | **Nethr lace:** a doctor watches a cut native branch close its own vessels; that observation opens research for a cartridge (vascular film + refined sap + medicine) that stops **every** bleed on a pawn, amputation stumps included, usable anywhere. Wounds still need tending. | 2 | free | M | Strong. Learn-here, use-anywhere like the lightning breakers, a new verb (stop the bleed), and powerful, balanced by cost not scope. The Greentide's growth turned into medicine fits its *"most frantic pharmacopoeia"* (sheet §7). Rename needed. |
| 2 | **The varkhoss moult:** a giant so overgrown with armour it barely turns; after eating enough it moults once, smashing trunks to lever plates off, while every predator on the map attacks the soft body and the shed plates. You contest the leavings. | 5 | free | L | The best giant angle offered: a free-for-all around one body, which is the biome's law (*no truce*). It is a **Shatterer** (reuses the aura), so it merges with §3's thurrock: the thurrock is the herd, the moult is one adult's event. Two static body states, no animation. |
| 3 | **Skrith rasp:** a colonial organism rasps exposed wet metal, the landed ship as one more feeding surface; scrape it off by hand in the heat; take off and the damage flies home, the rasp blanches and dies away from the jungle. | 6 | free | M | The biome acting on the ship in its own voice, on every metal building alike, so no ship special case. The blower (row 0) is its natural counter. Close in kind to Subnautica's larvae; different from the Webwork's root pitch (material, not doorways). Rename needed. |
| 4 | **Ozzik's Open Boast:** found in a ruined assembly hall; each participant declares an ambition and the colony answers with its name; days later a warned hostile challenge may arrive. Once per colony. | 9 | campaign | M | Fits the rulings (cohesion only, consequence as an event). It competes with §6 R1 for Ozzik's one likely slot. ⚠ It is less of the Greentide than R1 (any loud place could teach it), and "once per colony" is a non-repeatable choice; say so on the card. |
| 5 | **Work between the crashes:** the jungle's own noise (a feeding fight, a tree crash) masks your workers' tools; in the quiet, nearby creatures hear the work and come to look. Captions mirror the sound. | 7 | free | M | Makes the loudest biome's noise a resource and its silence a danger, which extends the silence cue rather than repeating it. Distinct from Stillsand's geophone (that locates buried predators). A behaviour system, not weather. |

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. The binding rulings: **no god is evil**; **a rite gives cohesion, never a power**;
**favour shows only through events, world state and subtle odds**, voiced by the Narrator; a rite's
effect may be a dramatic, risky world event. Five-rite cap per god (raised from four 2026-10-02, card).

**Cap count, by hand from the register plus the 2026-10-02 ledger rulings:** at four, Oomo (Sunning,
Chime Vigil, Filtered Cup, Unspilled March), Ohm (Engine Hour, Last Track, Deserter's Welcome, the
Answering), Sh'kaar (Snuffing, Anvil Gift, Shade Tithe, Felled Noon), Ishko (Dark Vigil, Charged Reed,
Stall-Hold, the Sinking), Mob'Unloo (Blind Offering, Storm's Receipt, Cold Ledger, the Sump's effigy
Price). Room: **Ozzik 3, Rekko 3, Ta'Baa 3.** Zizzik avoided.

**Not taken, and why:** consecrating fever survivors (the scores doc's hint) duplicates the ruled
survivor mark, which already is the consecration, and would read as a buff; digging out and mending
what the mud swallowed, for Rekko (too close to the Cracked Lands' Mud Claim, Rekko, salvage after a
recede); anything with fire (fire is not the tool here, sheet §4b, and the Calling-Pyre owns set
fires); offering water back (Oomo, capped); cutting a held person free (the Webwork's Cut Cocoon
pitch); any truce or feeding of the jungle's beasts (ban 1).

### R1. The Ceded Room, for Ozzik: venting pride, by giving the green your best room (PITCHED)

- **Grounding:** the Greentide is the one place where the world visibly eats buildings: growth comes
  through doors, roots take what dry heat does not defend. Ozzik is pride and grief; the proudest
  thing a colony owns is usually a room, not an object.
- **Found:** a windowless mud dome in the habitable band, its blower cold, its door wedged open, the
  room inside fully grown through, a carved chair and a sculpture still visible inside the green, and
  on the lintel a scratched mark: *we were proud of this.*
- **Asks:** the colony chooses a finished room of real beauty (an impressiveness floor), carries
  nothing out, wedges the door open, kills its cooling, and the participants scatter wild seed across
  its floor while the speaker names what the room was for. The room is then **ceded**: its door
  stays open, wild growth fills it over days (the `EXPLOSIVE_PLANT_GROWTH_1` engine where loaded,
  vanilla wild-plant spread elsewhere), its furniture weathers, and nothing may be reclaimed for a
  season, or the rite's memories sour.
- **Risk (the point):** in the Greentide the ceded room is a breach the jungle will push from, into
  the rooms beside it; anywhere, it is a real loss of a beautiful space and its comfort.
- **Outcomes (cohesion only):** shared memories by quality. Ozzik's ease is told by the Narrator and
  shows only as odds (his high pressure, the trap that raises Sh'kaar and Zizzik, eases), never a buff.
- **Readable signs:** the open, overgrown room on the map; the lintel mark the colony scratches; the letter.
- **Collision check:** the Unburdening destroys wealth at once; the Salted Keeping buries one finest
  thing in a crater; the Flawed Masterwork mars an object. None surrenders a lived room to time, kept
  in sight.

### R2. The Uprooting, for Ta'Baa: feeding, by refusing what has rooted (PITCHED)

- **Grounding:** the Greentide is the most rooting place on the planet (*"darkness brings roots"*;
  causeways are roots; homes go down into the earth). Ta'Baa the Unrooted is fed by refusal to root.
- **Found:** at the jungle's dry edge, a whole young tree lying on bare ground, roots in the air,
  dragged there along a causeway (the furrow still runs back into the green), a wing-mark cut into
  its bark, facing away from the jungle.
- **Asks:** at dusk, when roots grow, the participants pull up by hand the oldest living thing the
  colony planted (a tree, the first field's oldest plant, a garden), and drag it to the map edge with
  no hauling machine, and leave it there facing outward, roots to the sky.
- **Risk (the point):** a long, slow, heavy carry in the open; in the Greentide, across churnmud
  under the Roil at dusk, with mire and whatever lunges from the water. Losing the oldest planting is
  a real cost.
- **Outcomes (cohesion only):** shared memories by quality. Ta'Baa's favour is told by the Narrator
  only.
- **Readable signs:** the drag furrow across the map, the uprooted tree at the edge, the letter.
- **Collision check:** the Shadow Walk crosses a gloomcast; the Vindication Walk walks a Settling's
  prints; the Returned seals a body aboard; the launch-rite is a launch. None uproots and carries out
  something the colony grew.

GPT's rite idea, if any, is in §5 and is not repeated here.

## 7. Draft turn-1 card

Plain language, no def names in option labels, headers 12 characters or fewer, every question ends
in "?", and no option is a "none" (the card's own write-in line covers that). Above the card, read
him §0's description of the Greentide, per the standing rule that he is never assumed to remember.

**1. Build first** — *What should be built first for the Greentide?*
- **Fix the base first (recommended):** move the hot ground fog, the sun-break, the wet-heat danger,
  the dry-air door blower, the root roads and the giant tree you can live inside from the campaign
  into the free mod, and give the free mod its own jungle animals in place of the vanilla seven.
  Buys: the biome works as written for every player, and the campaign stops losing these when the
  planet is repainted. Costs: a large first batch, mostly moving existing work; no new mark lands
  this round. *Why: half of what makes the Greentide itself is built but sits on the wrong side.*
- **Base fixes and the giant together:** Buys: one visible new creature alongside the repair. Costs: a
  bigger first batch, and art waiting on it.
- **New ideas first, base later:** Buys: new marks sooner. Costs: the hull rasp has no counter until
  the blower moves, and the campaign still loses its fog at the repaint.

**2. The giant** — *Which giant should the Greentide get?*
- **A tree-felling herd (recommended):** huge copper-teal browsers that knock trees down to eat the
  crowns, cross, and fight in season; a passing herd is crash after crash, opening sun gaps and
  dropping wood across the roads; provoke one and it shoulders walls like trees. Buys: the jungle's
  missing third tree-feller and its percussion, made flesh; the code for it already exists. Costs:
  one new animal, its art and a small spawn hook. *Why: the sheet already asks for it, and it is
  cheap.*
- **The herd, plus a once-in-a-life moult:** an old adult levers its armour off by smashing trees,
  and every predator on the map attacks the soft body and the shed plates while you try to grab
  plate and meat. Buys: a free-for-all feast around one giant, the biome's law in one scene. Costs:
  two body states, a moult behaviour, a larger build.
- **Only the moulting giant:** Buys: the dramatic event without a herd. Costs: the felling herd and
  its constant crashing stay missing.

**3. New marks** — *Which new ideas should be built (pick any)?*
- **Blood-stopping lace:** a doctor studies a cut jungle branch that closes its own veins, and the
  colony learns to make a cartridge that stops all bleeding on a wounded pawn, anywhere. Buys: the
  biome's discoverable technology, powerful and kept. Costs: a medium build; costly cartridges.
- **Hull rasp:** a tiny colony organism rasps wet metal, your landed ship included; scrape it off by
  hand in the heat, or fly with the bite scars; it dies away from the jungle. Buys: the jungle marks
  your ship in its own voice. Costs: a medium build and some chore work while landed.
- **Noise cover:** the jungle's racket hides your workers' tools; in a quiet spell, nearby creatures
  hear the work and come to look. Buys: the loudest biome's noise and silence become something you
  play. Costs: a medium build; careful tuning so it never feels unfair.
- **All three (recommended):** Buys: technology, ship and sound marks in one sitting, none repeating
  another biome. Costs: three medium builds. *Why: each fills a different gap and they do not depend
  on each other beyond the base fixes.*

**4. Rite** — *Which rite should the Salvation find in the Greentide?*
- **The Ceded Room, for the god of pride (recommended):** the colony chooses its finest room, leaves
  everything in it, opens the door, and lets the green take it while they watch; nothing may be
  taken back for a season. Buys: a rite only this biome could teach (the place where the world eats
  buildings), with a real cost and risk. Costs: a medium build. *Why: it vents pride by surrender,
  which no other rite does.*
- **The Uprooting, for the god of flight:** at dusk the colony pulls up the oldest thing it planted
  and drags it by hand to the map's edge, roots to the sky. Buys: a hard, exposed carry that refuses
  roots in the most rooted place on the planet. Costs: a medium build; the oldest planting is lost.
- **The Open Boast, for the god of pride:** each member declares an ambition and the colony shouts
  its name; days later a warned enemy may come to answer the boast. Once per colony. Buys: a proud,
  risky moment. Costs: a medium build, a one-time choice, and it is less tied to this jungle.

## 8. Turn 1 rulings (2026-10-02) and ticket-out

Decisions taken by question card 2026-10-02 07:43 PDT (items 1 to 3) and 07:52 PDT (the Open Boast's
home), except the sentence quoted under item 4, which the owner typed.

| Card item | Ruling | Ticket |
|---|---|---|
| 1. Build first | **Base fixes and the giant together.** The base is rows 0 and 0b: the Roil, Breaklight, the wet-bulb lock, the dry-air blower, root causeways and the living greatbole move from the campaign tier into the free mod (Q11a; findings 1 and 2), the two `RUT_Greentide` lock patches go, and the free mod gets its own jungle animals in place of the vanilla seven, with campaign op 1's wholesale Replace deleted so the campaign only Adds canon (finding 3; precedent `CRACKEDLANDS_PLANT_LIST_OWNED_1`). Also fixed: the false "the canopy swinger fills the dianoga's slot" note (finding 4; the owner filled that slot with the Illisk and the Vurrak) and the invented swinger, sytheclaw and yearning fruit sitting in the campaign tier. Decision taken by question card. "Fix the base first" alone and "new ideas first" are **not chosen**. | Row 0: `GREENTIDE_BASE_PORT_BUILD_1`. Row 0b: `GREENTIDE_FREE_ROSTER_OWNED_1` |
| 2. The giant | **The tree-felling herd** (§3, the thurrock): huge copper-teal browsers that fell trees to eat the crowns, open sun gaps, drop wood across the roads and shoulder walls when provoked. Decision taken by question card. "The herd plus a once-in-a-life moult" and "only the moulting giant" (§5 idea 2, the varkhoss) are **not chosen**: no moult is built. Name collision-checked 2026-10-02 (python sweep of `src/`, `design/`, `infrastructure/`: only this review; Wookieepedia 0; artpipe 0; probes `korrum`, `wyyyschokk`). | `GREENTIDE_THURROCK_HERD_BUILD_1` |
| 3. New marks | **The blood-stopping lace only** (§5 idea 1). Decision taken by question card. GPT's name *nethr* collides and is replaced by **stellock** (clear in the repo, on Wookieepedia and in artpipe, 2026-10-02). The hull rasp (§5 idea 3) and noise cover (§5 idea 5) are **not chosen** and not ticketed; "all three" is **not chosen**. | `GREENTIDE_STELLOCK_LACE_BUILD_1` |
| 4. Rite | Owner, typed: *"Use first and third. First can be here. Build it outside the ship and let it be taken.  Works better the better the room. The third works on another map that doesn’t have one for this god yet. Likely one with open sight lines."* **The Ceded Room, for Ozzik** (§6 R1) is the Greentide's found rite: the room is built outside the ship (never on the gravship), the jungle takes it, and its effect scales with the room's quality. **The Open Boast, for Ozzik** (§5 idea 4) is admitted and found in **the Warscar** (decision taken by question card 07:52 PDT). The Uprooting (§6 R2, Ta'Baa) is **not chosen**. Both added to the register as B11 (`design/Jawa/salvation_rites_2026-10-01.md`). ⚠️ Ozzik now carries **five** found rites, one over the four-rite cap (only Zizzik is waived); recorded there for the owner, nothing cut. | `GREENTIDE_CEDED_ROOM_RITE_1`, `WARSCAR_OPEN_BOAST_RITE_1` |

FOUNDRY items, each `--caused-by GREENTIDE_SCORING_SITTING_1`:

| slate row | item |
|---:|---|
| 0 | `GREENTIDE_BASE_PORT_BUILD_1` (Roil, Breaklight, wet-bulb, blower, causeways, living greatbole to `RM_`; twin lock patches deleted) |
| 0b | `GREENTIDE_FREE_ROSTER_OWNED_1` (sulleth, dhollock, yammeth; swinger and yearning fruit to `RM_`; vanilla seven out; op 1 deleted, ops 2 to 4 re-gated) |
| 1 | `GREENTIDE_THURROCK_HERD_BUILD_1` (no moult) |
| 2 | `GREENTIDE_STELLOCK_LACE_BUILD_1` |
| 5 | `GREENTIDE_CEDED_ROOM_RITE_1`; `WARSCAR_OPEN_BOAST_RITE_1` |
| 6 | art: `infrastructure/artpipe/art_lists/greentide_turn1_2026-10-02.csv` |

Slate rows 3 and 4 are not ticketed (not chosen). The ruled Illisk and Vurrak stay with
`GREENTIDE_TERROR_REPLACEMENT_1` (now pointed at the `RM_` tier by Q11a and this ruling); the swinger's and
fruit's shipping names stay with `GREENTIDE_SHIPPING_NAMES_1`; the sytheclaw's def move stays with
`PYRELANDS_FAUNA_TIER_PORT_BUILD_1`. `GREENTIDE_FIRST_SCRIPT_1` should be written against row 0's state.

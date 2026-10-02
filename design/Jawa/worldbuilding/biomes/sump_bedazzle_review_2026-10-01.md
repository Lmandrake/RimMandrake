# The Sump: bedazzle review (grandfathered sitting, turn 1 card drafted)

Item: `SUMP_BEDAZZLE_SITTING_1` (BENCH). Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 4.

_BENCH design pass, 2026-10-01. Fourth sitting of the grandfathered track, worst-first by
`grandfathered_bedazzle_scores_2026-10-01.md` (§ The Sump; sitting order row 4). The sheet
`the_sump.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07) and owner-ratified (*"YES! Ship
the Sump! It's ready."*). The Sump then had a full design sitting of its own on 2026-09-24
(`SUMP_DESIGN_SITTING_1`, closed: 8 roster cards, then 11 synthesis rulings: gaslight, the tar
vault, walkways, nastiness, the skellarn, ship gifts). **Nothing ruled there is re-argued here.**
This sitting scores what those rulings left, and fixes where the built content landed._

Sources read, all on `origin/main`: `src/RimMandrake/TheSump/` (BiomeDef
`Defs/BiomeDefs/RM_TheSump_Biome.xml`, `About/About.xml`, `RM_SumpFauna.xml`, `RM_SumpFlora.xml`,
`RUT_BeastBulge.xml`, `RUT_SumpDuskLock_BiomeWiring.xml`), the twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Sump.xml`, `Patches/WildAnimals_Sump.xml`,
`RUT_Sump_Research.xml`, the `RUT_Tarred_*`, `RUT_Sumpgas`, `RUT_GaslightLamp`, `RUT_TarVault`,
`RUT_SumpWalkways` and `RUT_HolyFlame*` defs, `RM_FlameStatuary.xml` (EnvironmentalHazards), the
rosters `sump_fauna_roster_2026-09-24.md` and `sump_flora_roster_2026-09-24.md`, the items
`SUMP_GASLIGHT_1`, `SUMP_TAR_NASTINESS_1`, `SUMP_WALKWAYS_1`, `SUMP_TAR_FIRE_NETWORK_1`,
`SUMP_TAR_LIVING_SYSTEMS_1`, `SUMP_INHABITED_NOTES_1`, `BIOME_SHIP_CONTRIBUTIONS_1`, and closed
`SUMP_DESIGN_SITTING_1`, `SUMP_UTINNI_LAYER_1`, `SUMP_TAR_VAULT_1`; and
`salvation_rites_2026-10-01.md`. Rosters were parsed as XML elements, both halves (inline and
patch-added). No tile counts are reported (the planet is painted once, at the end).

## 1. What is there: ruled vs built

### The free mod is the bare biome; everything the 2026-09-24 sitting ruled ships in the campaign patch

`mandrake.rm.thesump` carries the BiomeDef, the dusk lock, the tar moat and fuse posts, the dig
shaft and strata lottery, the vault seal comp, the deep black mere, the belch, the beast bulge, the
ten flora and nine fauna. Its own `About.xml` then says the rest *"are not biome-gated and stay in
mandrake.rut.patches for now"*: the tar coating, the tarred hediff, the solvents and their surgery,
the walkways (duckboards and glasswalk), the gaslight lamp, Sumpgas, the tar vault, and both
research projects (`RUT_GaslightChemistry`, `RUT_TarRendering`).

🔴 **Finding 1: the free tier has no nastiness, no gaslight, no vault and no learned tech.**
Those were ruled for the mod, not for the campaign. The gaslight ruling says outright *"the free
mod may require"* Helixien, and *"free"* means franchise-free only (Q16); the only thing ruled to
the campaign was the **name** Sumpgas (*"the utinni layer should rename it to our own form of gas"*)
and the holy-act meaning of the statues. The flame statuary is the one piece that did land RM-tier
(`RM_FlameStatuary`, EnvironmentalHazards). Under Q11a (*"the top mod without star wars will look
precisely the same"*), a free Sump with no tar on anyone and no warbling light is not the Sump.

🔴 **Finding 2: the free BiomeDef names a campaign def.** `RM_TheSump`'s
`RM_CarriedFilthHediffExtension` sets `hediffDef` to `RUT_Tarred`, which is defined only in
`src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_Tarred_Hediffs.xml`. With the free mod alone, that
is an unresolved cross-reference at load. Moving the tar content down (Finding 1) fixes it; the
hediff becomes `RM_Tarred` and the campaign relabels it if it wants.

### The dusk is on the free def (the scores doc was wrong)

`RM_TheSump` lists `RUT_SumpDuskLock` in its own `<biomeMapConditions>`;
`RUT_SumpDuskLock_BiomeWiring.xml` adds the same condition to the twin only because the twin lacks
it. So mark 8 is a **free HIT**, not a miss, and the dusk survives the repaint. The scores doc's
"wired to the twin only" line was false and is corrected there in this commit. The real leftover is
cosmetic tier grammar: `RUT_SumpDuskLock`, `RUT_SumpWeather`, `RUT_TarPitBelch`, `RUT_TarMoat`,
`RUT_MoatFusePost`, `RUT_DigShaft`, `RUT_DigStratumTable`, `RUT_BeastBulge`, `RUT_Plant_Wick`,
`RUT_WickStem` and the `RUT_GenStep_*` ship inside the RM mod under campaign prefixes (filed as
cleanup under `BIOME_TIER_CLEANUP_1`; renaming carries a savegame cost on the frozen world).

### Fauna, merged (inline + patch-added), read as XML elements

| def | label | bs | comm. | where | state |
|---|---|---|---|---|---|
| `RM_SumpMouse` | sump-mouse | 0.15 | 0.8 | inline | wired; the instrument (mouse-lines) |
| `RM_Brommet` | brommet | 0.45 | 0.4 | inline | wired |
| `RM_Dredgel` | dredgel | 0.35 | 0.2 | inline | wired |
| `RM_Skarrid` | skarrid | — | 0.25 | inline | wired; mimics the bulge |
| `RM_Skellarn` | skellarn | — | 0.15 | inline | wired; real flight, stilt legs |
| `AA_TarGuzzler`, `AA_Bumbledrone`, `AA_BumbledroneHierophant`, `AA_BumbledroneQueen` | donor | — | 0.5 / 0.35 / 0.2 / 0.5 | inline, `MayRequire sarg.alphaanimals` | wired |
| `RM_Gulveth` | gulveth | 1.5 | (0.45 ruled) | — | **built, not wired** |
| `RM_Thrummel`, `RM_ThrummelWarden`, `RM_ThrummelBroodmother` | thrummel family | 0.3 / 0.5 / 0.9 | (0.35 / 0.15 / 0.05 ruled) | — | **built, not wired** |
| `RSW_Hssiss` | canon | — | 0.18 | `WildAnimals_Sump.xml` (Utinni) | wired, campaign |

The roster doc's §7 proposes the four donor rows be **replaced** by the gulveth and the thrummels
*"at this biome's own sitting"*. Evictions are stopped, so this sitting does not remove them; it
can **wire ours beside them** (§3) and leave the donor rows for a later per-biome ruling. The twin
`RUT_Sump` still carries only the three donor rows; that world is repainted at the end, so it is
not chased here.

⚠️ **`WildAnimals_Sump.xml` relies on an inert guard.** Its
`<Operation Class="PatchOperationConditional" MayRequire="mandrake.rsw.swbestiary">` gate does
nothing (1.6 never reads `MayRequire` on an `<Operation>`); the Conditional only tests that
`RM_TheSump` exists. Without SWBestiary the patch still adds `<RSW_Hssiss>`, an unresolved
cross-reference. Low harm (a red log line, not the corrupted-mods reset the two TheSump-ingredient
patches caused), but it is one of the 74 in `PATCH_MAYREQUIRE_GUARD_INERT_1`. The two live-hit
files (`RUT_Bitumen_KorvethSource.xml`, `RUT_ThrummelSeepwax_RosterSource.xml`) are already fixed:
they gate on the donor def through a Conditional.

### The giant is ruled and has no body

The sheet rules the tar beasts (§4): *"slow, huge things IN the tar ... dormant set-pieces; deep
digs, explosions, or greedy pumping wake one, and a woken tar beast is a slow, unstoppable,
station-eating catastrophe you evacuate ahead of, not fight"*; ban 2 forbids it as a fightable
spawn. Built: `RUT_BeastBulge` (a dormant building placed by `RUT_SumpTarBeastGenStep`) wakes on
damage or on construction within 20 cells, then emerges a pawn through
`CompProperties_PawnSpawnOnWakeup`, and **that pawn is a Thrumbo**, marked *"WIRING PLACEHOLDER —
roster pass replaces with the real tar-beast kind"*. The roster pass deliberately left the beast
out. 🔴 **Finding 3: the Sump's giant is ruled, and its wake machinery is built, but nobody ever
gave it a body.** The whole set is `DEPLOY_HOLD`'d. Digs and pumping, two of the three ruled wake
causes, are not wired.

### Ruled mechanics, built and unbuilt

- **Built, free:** dusk lock, tar moat and fuse posts, dig strata lottery (traps weighted first),
  vault seal comp, deep black mere, the belch (filth splash), mouse-line telegraphy
  (`RM_MapComponent_DreadField`, `RM_CompFilthTrail`), the ten flora, flame statuary.
- **Built, campaign patch only (Finding 1):** tar coating and tarred hediff, solvents and their
  surgery (scrubbing spawns gas), walkways, gaslight lamp with the warbling glow, Sumpgas, tar
  vault, both research projects, the Holy Flame precept.
- **Ruled, unbuilt:** the **natural seep flames** and the **discovery pilot** (*"the flickering
  light or geyser both can teach"*, `SUMP_GASLIGHT_1` §5–6); `RUT_TarRendering`'s *"first meeting
  tar"* trigger (its own description: *"Unwired flavor tech for now"*); network fire with gate
  firebreaks and the belch as a real flood (`SUMP_TAR_FIRE_NETWORK_1`); the living map and tar rain
  (`SUMP_TAR_LIVING_SYSTEMS_1`, the latter blocked on a design fork); the tar beast's body; the
  Inhabited faction weighting (`SUMP_INHABITED_NOTES_1`, gated on that pass).

### Heat

Not an extreme-heat biome: temperature p10 / median / p90 −4.3 / 1.2 / 14.9 °C, sun median
−10.6° (below the horizon). **No heat kind is owed.** The cold is vanilla cold.

### Weather, sound, ship, gods

- **Weather:** the dusk lock (sun held just below the horizon, forever) forces `RUT_SumpWeather`. HIT, both tiers.
- **Sound:** none. The sheet writes one (§9): derrick creak and pump thud carrying for miles in cold
  air, mouse skitter on glass tar, and *"underfoot, rarely, a bubble the size of a room, rising
  slowly."*
- **Ship:** ruled by the owner on 2026-09-24 (`BIOME_SHIP_CONTRIBUTIONS_1`): glasswalk ship
  flooring and the gas lamps and flame statues aboard (his own examples); a vault larder module is a
  candidate. Built in the campaign patch only. Plus the campaign arrival letter, *"The Ship
  Remembers the Sump"*.
- **Gods:** more than the scores doc found. `RUT_HolyFlamePrecepts.xml` (built) makes standing
  before a flame statue *"the holy act"* for Sh'kaar (register §B6, "Revering the Holy Flame",
  warding). It is an ideoligion precept, not a found Salvation rite.

🔴 **Finding 4: shipped text still calls Sh'kaar "the evil sun god".** Today's ruling: no god is
ever evil (Sh'kaar and Zizzik are the hungry gods). Player-visible: `TheSump/About/About.xml`'s
description (*"holy-act-to-the-evil-sun-god ideoligion meaning"*), shown in the mod manager.
Comments only: `RM_FlameStatuary.xml`, `RUT_HolyFlameEvents.xml`, `RUT_HolyFlameIssue.xml`,
`RUT_HolyFlamePrecepts.xml`. The owner's own 2026-09-24 phrase (*"a holy act to the evil sun god"*)
stays quoted where it is cited as history; the descriptive text gets corrected. FOUNDRY slate row 0c.

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `RUT_BeastBulge` + `CompCanBeDormant` / `CompWakeUpDormant` / `CompPawnSpawnOnWakeup` +
  `RM_CompBeastWakeRelay`: the giant's whole wake path, minus the giant.
- `RM_MapComponent_DreadField` + `RM_JobGiver_DreadAvoidWander`: mice already detour around dread
  sources; a surfaced beast is one more source.
- `RM_TarCoatingUtility` / `RM_Comp_TarCoating*` (vault and coating): tar laid onto any terrain.
- `RM_Comp_WarblingGlow`: the warbling light, any glower.
- `RM_HeatSoundscapeExtension` (Long Shade): a camera-keyed sound bed.
- `RUT_ResearchMod_GrantRite` and the Rites tab's found-rites row (register §d).
- The dig strata lottery and dig shaft (`RUT_DigStratumTable`, `RUT_DigShaft`).

## 2. Scorecard

Ruled counts as HIT; built is reported beside it.

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | yes | moats and fuse posts, the dig lottery, mouse-lines, the vault |
| 2 | Discoverable technology | PARTIAL | PARTIAL | campaign only: gaslight chemistry (research gated, not discovered) | the ruled discovery (*"the flickering light or geyser both can teach"*) is unbuilt; tar rendering is unwired |
| 3 | Unique resources | **HIT** | **HIT** | yes | korveth pitch, seepwax, brommet wool, chitins; Sumpgas campaign-only today |
| 4 | Surprising creatures | **HIT** | **HIT** | yes, five wired | gulveth and thrummels built, unwired |
| 5 | GIANT beast | PARTIAL | PARTIAL | wake path built; the body is a Thrumbo placeholder | Finding 3 |
| 6 | Gravship touch | **HIT** | **HIT** | campaign only | glasswalk deck and flame statues aboard (owner, 2026-09-24) |
| 7 | Soundscape | MISS | MISS | none | the sheet's sound is written, not built |
| 8 | Interesting weather | **HIT** | **HIT** | yes | the dusk lock is on both defs (the scores doc was wrong) |
| 9 | Relationship to the gods | MISS | PARTIAL | the Holy Flame precept | an ideoligion precept, not a found Salvation rite |

**Ruled: free 5 / 2 / 2, campaign 5 / 3 / 1. Built: free 4 / 2 / 3, campaign 5 / 3 / 1** (free
loses mark 6 and is weaker on 2 under Finding 1). The Sump's problem is not a lack of rulings. The
rulings sit on the wrong tier, the giant has no body, and nobody has ruled sound or a Salvation
rite.

## 3. Roster fill

### The gaps, read from the sheet and the ruled roster only

| hole | why it is a hole | fill |
|---|---|---|
| The tar's own grazer and the under-layer are donor animals | roster §7: gulveth and the thrummel family were built for these slots and never wired | **wire the four built animals beside the donors** (no eviction) |
| No giant | sheet §4 rules the tar beasts; the bulge emerges a Thrumbo | **the tar beast, given a body** (below) |
| Everything else | instrument, grazers, hunter, flier, under-layer all present | none; the Sump is "sparse-but-strange" by ruling |

### Proposed: wire the four, no eviction

`RM_Gulveth` 0.45, `RM_Thrummel` 0.35, `RM_ThrummelWarden` 0.15, `RM_ThrummelBroodmother` 0.05,
inline in `RM_TheSump`, at the roster's ruled weights. The four `AA_` rows stay (evictions stopped).
⚠️ The thrummel mound (defend-radius aggression on a `Hive`-like Thing) is the one new mechanism and
is still UNMEASURED against the engine; wiring the three castes as plain animals first is honest and
cheap, and the mound follows.

### Proposed: the tar beast (`RM_TarBeast`, free tier)

Label **tar beast**, the sheet's own name (*"the tar beasts (owner, prior canon confirmed)"*); no
collision in `src/` or `design/`. The third of the Patient family (sarlacc, the Fever Wood's deep
thing), and it must rhyme with them: huge, buried, patient, unmoving until it moves.

- **Body:** about **bs 9**, the largest thing on the planet's night edge. A low glossy mound with
  no clear head, tar sheeting off it. Static art at a huge draw size on an ordinary footprint, three
  facings, no new rig (the Orun-Ghal shape).
- **What it does when woken (ban 2 holds):** it does not hunt or fight. It moves very slowly, about
  a tenth of a pawn's walk, toward the densest cluster of buildings, the *"station-eating"* line.
  Every cell it crosses becomes shallow tar (the built coating). A building it reaches is
  swallowed: destroyed, with a tar mound left where it stood and a letter naming what was taken. It
  ignores pawns unless they block it, and then it shoves them aside (a stagger, not a bite). Damage
  barely slows it: very high health and armour, so **the answer is evacuation, not a fight**. After
  a set time, or after swallowing enough, it sinks back into the deepest tar and becomes a bulge
  again, at a new address.
- **Wake causes:** the built two (an explosion nearby, construction within 20 cells), plus the
  sheet's other two: a deep dig at a dig shaft, and pumping (a derrick or deep drill) within range.
- **Readable signs, before and after:** the bulge itself; mouse-lines that bend around it (the
  built dread field); the sheet's *"bubble the size of a room, rising slowly"* as a sound and a
  slow ring of filth for a day before a wake; the tar trail and the swallowed-building mounds after.
  Nothing it takes disappears without a mound and a letter.
- **Mod Settings:** on/off; wake sensitivity; speed; how many buildings it takes before sinking.

**Not a hunter, not a raid, not fightable:** the same ban that the roster honoured.

## 4. The slate

Rows 0 to 0c execute rulings already made, so they need no card; rows 1 to 4 wait on turn 1.

**0. The tier move (Finding 1 and 2), shape on the card (Q1).** Move the tar coating, `RUT_Tarred`
(as `RM_Tarred`), solvents and their surgery, walkways, gaslight lamp, the gas, the tar vault and
both research projects from `mandrake.rut.patches` into `mandrake.rm.thesump` (or the shared
EnvironmentalHazards kit where they are not Sump-specific) under `RM_` names. The campaign keeps
only the Sumpgas label, the Holy Flame precept and the arrival letter. Repoint the free BiomeDef's
`RM_CarriedFilthHediffExtension`. ⚠ Rename cost on the frozen world: a placed `RUT_` Thing in the
campaign save needs a back-compat alias. Size M.

**0b. Wire the four built animals beside the donors** (`RM_Gulveth`, `RM_Thrummel`,
`RM_ThrummelWarden`, `RM_ThrummelBroodmother`, roster weights). Additive; no donor row removed. Size S.

**0c. Strike "evil" from the descriptive text** (Finding 4): `TheSump/About/About.xml` (player
visible) and the four def-file comments. Sh'kaar is a hungry god. The owner's dated quote stays
where it is cited as history. Size S.

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The tar beast's body** (§3), Q2. | 5 | the bulge and its wake path; dread field; tar coating | M to L |
| 2 | **The natural seep flames and the discovery pilot** (ruled 2026-09-24, unbuilt): little dancing flames over seeps; the first pawn to see one learns gaslight chemistry; the first to handle tar learns tar rendering. Once learned, usable everywhere. | 2 | `RM_Comp_WarblingGlow`; the Anomaly encounter-unlock shape | M |
| 3 | **Whatever turn 1 takes from the GPT five** (§5), Q3. | 2, 5, 7 | per idea | — |
| 4 | **The soundscape the sheet wrote**: derrick creak and pump thud carrying for miles; mouse skitter on glass tar; a room-sized bubble rising, which doubles as the tar beast's warning a day before a wake. Placeholder audio first. | 7 | `RM_HeatSoundscapeExtension` pattern | S to M |
| 5 | **Found rites** (§6), Q4. | 9 | found-rites row | M |
| 6 | **Art commission:** the tar beast, the gulveth and thrummels if their art is still owed (check `artpipe/done/` first), the seep flame, whatever the card takes. | all | artpipe | — |

Row 2 needs no card: it is ruled. Row 4 is offered as the ordered backlog for mark 7, not carded
(the Pyrelands precedent).

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-01/sump.md` (prompt `sump.prompt.md` beside it),
run 2026-10-01 under the standing rule: exactly five ideas, different from each other and from
every other biome's signature (the prompt carried all of them, now including the Pyrelands'
breakers and Struck Glass), with research on other games and RimWorld mods cited. Model
`gpt-5.6-sol`, via `codex exec`. GPT's own check: verbs winch · retime · aim · reckon · induce;
systems displacement · pump acoustics · terrain transformation · ritual diplomacy · item custody.

| # | GPT's idea | what it is, plainly | BENCH's assessment |
|---|---|---|---|
| 1 | **The Blackline Capstan** | Two preserved draw-joints from the dig strata teach a hidden research row: a hand capstan with tar-glass bearings and seepwax-packed cable that winches one visible pawn, corpse, animal or item along a straight line, dragging a downed colonist out, pulling an enemy off a firing position, recovering something beyond a burning moat. A heavy or resisting load can tear the anchor out and exposes the operator. | **Recommended.** Exactly the shape he picked in the Pyrelands: learned only here (from what the tar kept), made from local materials, then buildable anywhere (the learned recipe uses ordinary cloth, chemfuel and steel). Powerful and balanced by the exposed operator and anchor wear, not narrowed. Risk: dragging a pawn through RimWorld's pathing is real C# (a tether state machine), M. |
| 2 | **The Fifth Stroke** | Every derrick's pump thud is slightly different. A neat bank of pumps started together slowly falls into one perfect beat, and then something beneath the glass answers with a fifth. Players send a pawn to re-time pumps by hand, losing output; ignore it and the tar beast's wake pressure builds. | **Strong on the biome's law** (*"frustrate neat, tidy, controlled"*) and the one sound idea that matters in play (mark 7). It also gives the ruled "greedy pumping wakes the beast" cause a body. Cost: it is a re-timing chore, close to the "repeatable choice" he dislikes, and needs pump-phase bookkeeping, M. |
| 3 | **The Buried Reach** | A rare dig exposes one knuckle of a buried ancient dragline (never a whole machine). Mouse-line bends reveal its buried arc; an expensive restoration buys one enormous, aimed sweep that crushes everything in a lane and heaps every loose thing at its end, then the machine seizes forever. | **A giant of a different kind** (mechanical, irreversible, once), which fits both his love of giants and his dislike of reversible choices. Costs: L, a big preview-and-sweep system; and it competes with the tar beast for the mark-5 slot. Second choice if he wants only one new idea beyond the capstan. |
| 4 | **The Reckoning of Owners** | A preserved tally-plate teaches a Mob'Unloo rite: nine owned objects laid out openly and their histories recited. Days later, two delegations may arrive with contradicting records for one valuable thing, and the colony must return it, pay, or hold it by force. | **Carried to Q4 as a rite.** Its effect is a risky world event, not a reward, which is the rite shape he picks. Weaknesses: its tie to the Sump is thin (it would work in any biome), Mob'Unloo already has the Cold Ledger in Nightside Ice, and two-faction claim incidents are L. |
| 5 | **The Kethrel's Borrowed Skeleton** | A boneless surface hydrocarbon animal that picks up loose rigid things (dropped weapons, slag, components) and wears them as armour, getting slower and louder. A handler can induce a molt to get everything back, risking a panicked charge. | **Alien fauna he would likely enjoy**, and the item custody keeps nothing vanishing (an inspect tab lists every carried thing; a molt cairn and letter if it leaves). Costs: four static shell overlays (no rig), M; and property theft can read as a nuisance. The Sump is "sparse-but-strange" by ruling, so a tenth resident is a choice, not a gap. |

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. Today's rulings bind them: **no god is evil**; **a rite gives cohesion, never a
power or a material reward**; **favour shows only through events, world state and subtle odds**,
voiced by the Narrator. The Zizzik cap is waived, and there is no cap pressure, but neither pitch
uses Zizzik (he already has five).

**Not pitched:** a rite at the flame statues (the Holy Flame precept already is one, Sh'kaar); any
rite in darkness (the Abyss); sealing an offering in the tar (too close to the Cold Ledger).

### R1. The Giving-Back, for Rekko: consolation (PITCHED)

- **Grounding:** Rekko is salvage and the discarded rewoken. The tar keeps everyone it took,
  perfectly; the sheet's own rite seed is the ship's memory of others sinking here.
- **Found:** at the edge of the deep black mere, a ring of tar-stiff coats hung on stakes, one per
  name, the Junkers' memorial to the gangs the ponds took. A plate on the tallest stake carries the
  words.
- **Asks:** the participants stand at the edge of deep tar (any deep tar: the mere, a pond, a
  poured moat) and call the names of the lost, the colony's own dead first.
- **The event:** the tar answers, and that is the risk. Within the hour it **heaves**: a slow belch
  at the spot (the built belch) that gives back what it kept. Most often preserved bodies of the long
  drowned, whole and unrotted, which the colony may bury; sometimes an armed trap of the old era
  surfaces with them (the dig lottery's own weighting); and if a tar beast's bulge lies within range,
  it may stir. Nothing is aimed; the risk is the point.
- **Outcomes (cohesion only):** shared memories by quality; a funeral for the returned dead is the
  natural sequel. Rekko's pleasure is told by the Narrator and shows only in events and odds.
- **Readable signs:** the heave and its tar splash; the bodies on the surface; a letter naming what
  came up and whether anything stirred.
- **Collision check:** the Lightless Burial (Ozzik, Abyss) buries in the dark; the Returned (Ta'Baa,
  Blue Desert) seals a body the ablation line gave up aboard the ship; the Cold Ledger (Mob'Unloo)
  seals a gift in ice. Here nothing is given: the colony calls, and the ground gives back, with
  whatever else it was holding.

### R2. The Deep Draw, for Ozzik: venting (PITCHED)

- **Grounding:** Ozzik is ambition, pride and grief. The sheet: *"Everyone at the derricks knows
  which ponds you don't pump deep."* Pumping the forbidden pond is pride made into a rite.
- **Found:** a derrick standing alone over a pond no station will touch, its pump rod snapped at the
  stroke, a single tar-stiff glove still on the handle.
- **Asks:** the colony's proudest pawn (highest skill or highest ambition, chosen as the rite's
  role) works a hand pump on deep tar for a night while the others watch.
- **The event:** the deep answers once, at random. A gusher of gas that lights into a field of
  dancing seep flames across part of the map (real fire, real danger, very beautiful); a great
  belch; or, if a bulge is near, a wake. Or nothing, and the silence is its own story.
- **Outcomes (cohesion only):** memories by quality; the role pawn's pride is vented, not rewarded.
- **Readable signs:** the gusher or the belch, the flames, a letter; a wake gets the full tar-beast
  warning (the bubble sound, the mouse-lines bending).
- **Collision check:** the Struck Glass (Zizzik) breaks found glass for a random lightning blast;
  the Unburdening (Ozzik) destroys wealth. Here the colony provokes the ground itself, by work.

GPT's **Reckoning of Owners** (§5 #4, Mob'Unloo) is the third candidate on Q4.

## 7. Draft turn-1 card

For BENCH to put to the owner. Four questions; Q3 and Q4 are multi-select. Each subject is
explained in full, because he does not rely on memory. Headers are 12 characters or fewer and every
question ends in "?".

**Q1. Header: `Free tier`.** *The free Sump mod (the one without Star Wars) is missing almost
everything you ruled on 24 September: tar sticking to pawns and the ground, the acid that cleans
it, the warbling gaslight lamps and the gas, the tar vault larder, the duckboards and glasswalk, and
both Sump research projects. They were all built into the campaign patch instead, and the free
biome even points at a campaign-only "tarred" condition, which breaks it when the campaign is
absent. Where should that content live?*

| Option | What it buys | What it costs |
|---|---|---|
| **Move it all into the free mod** *(recommended: the free Sump then plays the same as the campaign one, which is the rule you set)* | The free mod is the full Sump; the broken reference is gone; the campaign keeps only the Sumpgas name, the Holy Flame worship and the ship's arrival letter. | A medium build, and the free mod then requires Helixien gas, which you already allowed. Renamed defs need a compatibility alias on the frozen world. |
| **Move the tar mess only** | Tar on pawns and ground, the acid and the walkways come down; the broken reference is fixed. | The free Sump has no gaslight, no vault and nothing to learn; it plays thinner than the campaign. |
| **Fix the broken reference only** | Smallest job: the free mod loads clean. | The free Sump stays a bare biome with none of the 24 September content. |

**Q2. Header: `Tar beast`.** *The sheet says huge, slow tar beasts lie in the deepest tar and wake
when you dig deep, blast nearby or pump greedily, and that a woken one is an unstoppable,
station-eating catastrophe you run from, never fight. The waking machinery is built, but the thing
that comes out is a placeholder thrumbo; the beast has never had a body. What should it be?*

| Option | What it buys | What it costs |
|---|---|---|
| **The full station-eater** *(recommended: it is the giant the sheet already rules, and the one thing the Sump's dread has never delivered)* | A body more than twice a thrumbo's size that crawls very slowly toward your buildings, swallows each one it reaches (leaving a tar mound and a letter), turns its trail to tar, shoves pawns aside without biting, shrugs off damage, and after a while sinks back to a new spot. Mice and a rising room-sized bubble warn you a day ahead. | A medium-to-large build plus giant art (static, no new animation). It can wreck a colony that built in the wrong place, which is the point. |
| **It surfaces, then sinks** | The giant rises, oozes tar over the area around it and sinks again: a spectacle and a terrain change, with no buildings swallowed. | Less dread; the sheet's "station-eating" stays unbuilt. Cheaper art and code. |
| **It never surfaces** | A wake becomes a huge belch only; the beast stays a rumour under the bulge. | Cheapest; the Sump keeps no giant you ever see. |

**Q3. Header: `New ideas`.** *GPT was asked for five ideas unlike any other biome's. Four are
offered here (the fifth is a rite, in the next question). Which should be built? Pick any.*

| Option | What it buys | What it costs |
|---|---|---|
| **Blackline capstan** *(recommended: it is the lightning-breaker shape you picked, tech learned only from what the tar kept and then usable everywhere)* | Study two ancient winch joints dug out of the tar to learn a hand capstan that drags one pawn, body, animal or item in a straight line: pull a downed colonist out of a fight, an enemy off a wall, a crate back across a burning moat. Learned here, built anywhere from ordinary materials. | A medium build. The operator stands exposed, and a heavy or struggling load can rip the anchor out. |
| **Pump rhythm** | Your pumps' thuds drift into one perfect beat if you keep them neat, and something under the tar answers with a fifth beat; let it go and the tar beast wakes. Re-timing a pump by hand costs output. A sound that matters, and tidiness punished. | A medium build, and a recurring chore: someone has to keep re-timing pumps. |
| **Buried dragline** | A rare dig finds one joint of a buried ancient dragline; you trace its arc, pay to restore it, and fire it once: one enormous sweep that crushes everything in a lane and heaps every loose thing at the end, then it seizes forever. | A large build, and a second giant beside the tar beast. |
| **Kethrel** | A new boneless tar-country animal that picks up dropped weapons and scrap and wears them as armour, getting slower and louder; a handler can coax it to molt and give everything back. | A medium build plus four armour-stage pictures; it sometimes walks off with your things (always visible, always recoverable). |

**Q4. Header: `Rites`.** *The Sump has no Salvation rite you can find and learn. A rite's effect is
a world event and its gift is cohesion, never a reward. Which should be found here? Pick any.*

| Option | What it buys | What it costs |
|---|---|---|
| **The Giving-Back** *(recommended: it is the rite the Sump's own memory of the drowned asks for, and its effect is a risky world event)* | For Rekko. Found at a ring of tar-stiff coats on stakes beside the black mere. The colony calls the names of its lost at deep tar, and within the hour the tar heaves up what it kept: the long-drowned dead, whole, to bury; sometimes an old armed trap with them; and if a tar beast lies near, it may stir. | A medium build. Anyone the heave catches is in danger, and it can wake the giant. |
| **The Deep Draw** | For Ozzik. Found at a lone derrick over a pond nobody pumps, a glove still on the snapped handle. The colony's proudest pawn pumps the forbidden pond by hand for a night; the deep answers once at random: a gas gusher that lights a field of dancing flames, a great belch, a beast waking, or nothing. | A medium build. Real fire and real danger near the pump. |
| **Reckoning of Owners** | GPT's idea, for Mob'Unloo. Lay out nine owned things and recite how each changed hands; days later, two groups may arrive with rival claims to one valuable, and you return it, pay, or hold it by force. | A large build (two-faction claim visits); it is barely tied to the Sump and would work anywhere. |

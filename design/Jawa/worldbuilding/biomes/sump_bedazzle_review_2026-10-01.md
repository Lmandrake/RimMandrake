# The Sump: bedazzle review (grandfathered sitting, turns 1 and 2 ruled; the tar rites ruled)

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
patches caused); `PATCH_MAYREQUIRE_GUARD_INERT_1` closed with this one still standing, so the
tier-move item (§7) re-gates it. The two live-hit
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

### Wire the four, no eviction (executes the ruled roster; ticketed)

`RM_Gulveth` 0.45, `RM_Thrummel` 0.35, `RM_ThrummelWarden` 0.15, `RM_ThrummelBroodmother` 0.05,
inline in `RM_TheSump`, at the roster's ruled weights. The four `AA_` rows stay (evictions stopped).
⚠️ The thrummel mound (defend-radius aggression on a `Hive`-like Thing) is the one new mechanism and
is still UNMEASURED against the engine; wiring the three castes as plain animals first is honest and
cheap, and the mound follows.

### RULED: the tar beast, the full station-eater (`RM_TarBeast`, free tier; owner turn 1, by card)

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


### RULED: the kethrel (`RM_Kethrel`, free tier; owner turn 1, by card)

From the GPT consult (§5). A boneless hydrocarbon animal of the tar's surface that picks up loose
rigid things (dropped weapons, slag, components, scrap) and wears them as an armour shell, getting
heavier, slower, better armoured and louder as it loads. A handler can coax a molt, and everything
it carried drops where it stands; a badly handled molt can end in a panicked charge. Sump-only (one
home: it needs tar to bind the shell). It never digs and never comes out of deep tar.

- **Four armour stages, static art:** bare, light shell, heavy shell, full carapace. Drawn as four
  whole-body sprite sets (three facings each), swapped by load. No rig, no animation.
- **Nothing vanishes:** every carried object stays a real `ThingOwner` item, listed on an inspect
  tab, and drops on molt, death or leaving the map (a molt cairn and a letter if it leaves). Taking
  colony property is a Mod Settings toggle.
- **Mod Settings:** on/off, density, the value ceiling of what it will pick up, taking colony
  property, molt threshold and handling difficulty.

## 4. The slate

All rows are ruled and ticketed (§7). The rite (§6) is still open.

**0. The tier move (owner Q1).** His words, typed: *"Move it all into the free mod that is now
part of the Baroque Biomes mod"*. The free tier is now `mandrake.rm.biomes` ("RimMandrake: Baroque
Biomes", `BIOME_MOD_UNIFICATION_1`), composed at deploy time by `biomes_compose.py` from the per-biome
dev folders listed in `src/RimMandrake/Biomes.compose.json`; `TheSump` and `EnvironmentalHazards` are
both entries. So the content moves into `src/RimMandrake/TheSump/` (Sump-specific) and
`src/RimMandrake/EnvironmentalHazards/` (the generic tar coating and hediff), under `RM_` names: tar
coating, `RUT_Tarred` as `RM_Tarred`, solvents and their surgery, walkways, gaslight lamp, the gas,
the tar vault, both research projects. The campaign keeps only the Sumpgas label, the Holy Flame
precept and the arrival letter. Repoint `RM_CarriedFilthHediffExtension`. Re-gate
`WildAnimals_Sump.xml` (its `<Operation MayRequire>` is inert).
- ⚠ **No new hard dependency on Helixien.** A `modDependencies` entry in `TheSump/About.xml` is
  unioned into Baroque Biomes' own About, so it would make all 29 biomes require Helixien. The gas
  is already its own ThingDef (`RUT_Sumpgas`, not a disguised `VHGE_Helixien`), so it needs none.
- ⚠ **The frozen world.** A placed `RUT_` Thing or a pawn's `RUT_Tarred` in the campaign save
  orphans on rename: each moved def needs a back-compat alias (a `BackCompatibilityConverter` or
  the 1.6 def-rename mechanism; which one is UNMEASURED and is the item's first read).

**0b. Wire the four built animals beside the donors** (`RM_Gulveth`, `RM_Thrummel`,
`RM_ThrummelWarden`, `RM_ThrummelBroodmother`, roster weights). Additive. Art for these exists in
the artpipe registry (gulveth: 28 registry lines).

**0c. Strike "evil" from the descriptive text.** Re-verified on `origin/main` today: still in
`TheSump/About/About.xml` l.70 (player visible) and comments in `RM_FlameStatuary.xml`,
`RUT_HolyFlameEvents.xml`, `RUT_HolyFlameIssue.xml`, `RUT_HolyFlamePrecepts.xml`. Sh'kaar is a
hungry god; the owner's dated 2026-09-24 quote stays where it is cited as history.

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The tar beast, the full station-eater** (§3). | 5 | the bulge and its wake path; dread field; tar coating | M to L |
| 2 | **The capstan turret** (§5, revised by the owner). | 2 | Melee Animation's lasso pull | M |
| 3 | **The kethrel** (§3). | 4 | `RM_CompFilthTrail`-style comps; ThingOwner | M |
| 4 | **The natural seep flames and the discovery pilot** (ruled 2026-09-24, unbuilt). | 2 | `RM_Comp_WarblingGlow` | M |
| 5 | **The soundscape the sheet wrote** (not carded; ordered backlog for mark 7, not filed). | 7 | `RM_HeatSoundscapeExtension` | S to M |
| 6 | **The lasso removal** (owner Q3). | — | Cherry Picker | S |
| 7 | **Art:** tar beast, kethrel's four stages, the capstan turret. | all | artpipe | — |

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-01/sump.md` (prompt beside it), model
`gpt-5.6-sol` via `codex exec`, run 2026-10-01 under the standing rule (five, different from each
other and from every other biome's signature, research cited). The owner took two (Q3): the
Blackline capstan, revised, and the kethrel (§3). The pump rhythm, the buried dragline and the
Reckoning of Owners were not taken; the consult file keeps the record.

### The capstan turret (RULED, revised from GPT's "Blackline Capstan")

His words, typed: *"I love the Blackline Capstan. Model it after the Lasso already built in the
game (pulls people towards you, weirdly nonphysical since it doesn't move you at all. But if that
mechanic is attached to a turret, it makes complete sense and is awesome. Remove lasso's from the
game, but keep this)"*.

**The lasso he means, measured:** Melee Animation (packageId `co.uk.epicguru.meleeanimation`,
workshop 2944488802, active). `1.6/Defs/Lassos.xml` defines three lassos, all **apparel** on its own
hip layer (`AM_Hip`), not weapons: `AM_LassoCloth`, `AM_LassoDevilstrand`, `AM_LassoHyperwave`.
The pull is the job `AM_GrapplePawn` (driver `AM.Grappling.JobDriver_GrapplePawn`), tuned by the
stats `AM_GrappleRadius` ("Max Lasso Distance", base 10), `AM_GrappleCooldown` (base 20 s) and
`AM_GrappleSpeed` (reel speed); the mod's settings cap it by the target's mass and body size and
by how much a building in the way fills its cell.

- **What it is:** a fixed turret that ropes one visible pawn (enemy, animal, or a friendly downed
  colonist) and reels it in toward the turret, along the ground, through anything it can pass. The
  pull is the lasso's, made physical by the anchor: the turret does not move, so pulling toward it
  finally makes sense.
- **Learned here:** studying two preserved draw-joints from the Sump's dig strata teaches the
  research (GPT's discovery), once; after that it is built anywhere. The first one is made from
  local materials (tar-glass bearings, seepwax-packed cable); the learned recipe uses steel,
  components and cloth.
- **Powerful, balanced by cost:** range, reel speed and cooldown come from the turret's own stat
  values (the lasso's three stats, set on the building). It needs a crew or power (FOUNDRY to pick
  the vanilla shape that reads cleanest), and a heavy or struggling target can snap the line and
  damage the anchor. It is not narrowed to enemies or to small targets beyond the lasso's own mass
  and size caps.
- **Readable signs:** a visible line from turret to target, the reel's ratchet sound rising, and a
  snapped-line mote and message when it fails.
- **The hook (UNMEASURED):** how `JobDriver_GrapplePawn` moves the target, and whether a building's
  verb can start it with the turret as the anchor, is read from the decompiled mod (RimSage or
  `zAnimationMod.dll`) before anything is written. If the pull cannot be driven from a non-pawn,
  the turret re-implements the pull (a flight-free forced move along a cell line) and keeps the
  lasso's numbers.
- **Mod Settings:** on/off; range, reel speed, cooldown; friendly-pull on/off; snap chance.

### The lasso removal (RULED, its own item)

"Remove lasso's from the game": by Cherry Picker, never by uninstalling Melee Animation (its
animations stay). `CherryPicker.SHIP.xml` and the live config already cut `AM_LassoHyperwave` and
`AM_LassoDevilstrand`; the live list still carries `AM_LassoCloth`, so it is the one to add, with
its tailoring recipe (`recipeMaker`).
- **The disarm check, measured:** lassos are apparel, so no pawnkind weapon tag depends on them.
  The def dump (`defs.sqlite`, capture 2026-10-01) holds **0** PawnKindDefs with apparel tag
  `Lasso` (probe: 51 carry `Neolithic`). Pawns get lassos from Melee Animation's own C# spawn roll
  (its setting "Lasso Commonality", a % of melee fighters), not from pawnkind tags.
- ⚠ **So the cut needs the mod setting too.** With every lasso def cut, that spawn roll has nothing
  to give; whether it then no-ops or errors is UNMEASURED. The safe order is the mod's own
  "No Lassos" preset (*"enemies will not spawn with or use lassos"*), or "Lasso Commonality" at 0,
  plus the Cherry Picker cut. No saved Melee Animation settings file exists in the Config folder
  today, so it runs on defaults.

## 6. The tar offerings: two rites (ruled)

The owner's first rite (turn 1, typed) asked for one object of value plus an effigy of something
hated. At turn 2 he split it, typed:

> *"I could see two rites here. Throwing one thing in the tar of value lowers heat, erases ownership
> as part of RimProperty (perhaps of something you still keep...), and lowers raid frequency.
> Whereas throwing in one good thing and one hated effigy to Mob'Unloo brings about unfortunate
> consequences on someone else, paid for by you."*

Both are campaign-tier Salvation rites, found at the Sump, learned through the Rites tab's
found-rites row (`mandrake.rut.rites`), performable after at any tar: the mere, a pond, a poured
moat, a tar vault. Both keep the laws: **cohesion, never a material reward**; **favour shows only
through events, world state and subtle odds**, told by the Narrator; a risky world event is welcome.
Nothing living or dead is ever thrown in.

### Rite A, the Sinking (one thing of value; god Ishko)

- **Found:** at a Junker barrel yard, a sunk ring of tar where the stations throw a thing of worth
  before a hard season; a tally board lists what went down, and no owner is written beside any of it.
- **Asks:** one object of value, thrown into the tar by the participants and gone for good. Its
  value sets the rite's quality with attendance and roles. A market-value floor is a Mod Settings
  number.
- **God: Ishko** (god of hiding; decision taken by question card, 2026-10-02).
- **Effect 1, the next Imperial probe or raid is pushed 5x further away.** His words, typed: *"We already
  ruled this I thought. It doesn't actually reduce heat, it just pushes the next Imperial probe or raid
  away x5"*. Imperial Heat is untouched: the K2 rule that Heat is *"never scrubbed by success"*
  (`kyber_trade_plot_spec.md`; `cathedral_surveyor_misdirection_quest.md`) stands with no override. The
  mechanism is the hold-off Rite B's Empire effigy uses (`RUT_ImperialHoldOff`, this map's
  orbital-detection time multiplied by 5), built once and shared by the two build items. The real
  constants are placeholders in `src/RimMandrake/Utils/gm_blackboard_shadow.py`; the vanilla-side Empire
  raid gate is UNMEASURED and rides M4.
- **Effect 2, ownership erased (RimProperty, measured).** RimProperty (`mandrake.rm.property`,
  `src/RimMandrake/RimProperty/`) is a decaying-claim engine. Every Thing can carry recorded claims,
  each a (claimant, strength 0–1, basis, timestamp). The recorded bases are `Stolen`, `Purchased`,
  `ClaimFeePaid`, `Gifted`, `Inherited`, `Looted` and `BattleLootOrigin` (the pre-loot owner's
  record, kept alongside the looter's at about 1.0); `Territorial` and `Situational` are computed
  live, never stored (`ClaimBasis.cs`). A claim decays linearly to zero over a lifetime set by the
  Thing's **recognizability** (quality, market value, a persistent name, mechanoid identity;
  `RecognizabilityUtility.cs`): *"a steel bar's stolen-claim dies in days; a named astromech's never
  does."* Separately, each faction keeps a **FactionRecord** of witness entries against individual
  pawns (suspicion that propagates "to the top"). The Bazaar's ruled stolen-goods trade reads these
  claims (`bazaar_trade_window_design.md`, *"this may be stolen"*).
  - **So "erase ownership" means:** strip every **other party's** recorded claim off one item the
    colony keeps (its `Stolen`, `BattleLootOrigin`, and any rival `Purchased`/`Gifted`/`Inherited`
    records), leaving only the colony's own. The thing is now plainly the colony's: its old owner
    cannot recognise it, a fence or registry scan reads it clean, and no recovery or bounty can
    point at it. That is *"perhaps of something you still keep"*: the tar takes the offering, and
    the **kept** thing's history goes down with it. It is laundering a stolen item's provenance, and
    it is exactly what makes a high-recognizability theft (a named droid, a legendary weapon) safe.
  - **Built today:** `GameComponent_PropertyLedger` exposes `TryGetRecords` and `RecordClaim` only;
    there is **no remove or clear call**, and nothing reads `FactionRecord.GetSuspicion` yet (the
    consequence layer is unbuilt). The rite needs one new ledger method (clear the records of other
    claimants on a Thing).
  - **Ruled 2026-10-02 (typed):** *"I like Vault forgets, but it should be true about almost
    anything you own"*: other parties' claims are wiped on almost everything the colony owns, not one
    chosen item (§9). Whether the faction's suspicion of the thief is erased too is not ruled; the
    build leaves `FactionRecord` alone.
- **Readable signs:** the offering sinking with a slow bubble; a letter naming the cleansed item and
  whose claim was wiped; the pushed-back probe or raid voiced by the Narrator, shown as a map
  condition with its days left.
- **Collision check:** the Unburdening (Ozzik) destroys wealth to vent pride, with no effect on the
  world's attention; the Cold Ledger (Mob'Unloo) seals a counter-gift to pay one dead man's debt.
  The Sinking hides the colony: from the Empire, from raiders, from its own thefts.

### Rite B, Mob'Unloo's Price (one good thing plus one hated effigy; RULED)

- **God: Mob'Unloo** (his words). Debt and exchange; his devotion "the Collected Grudge" is this
  rite's plainest form. Kind: settlement. *"Unfortunate consequences on someone else, paid for by
  you."*
- **Found:** at a Junker station's edge, a sunk ring of effigies half-swallowed by the black,
  straw-and-rag figures in half the planet's colours, one still holding a carved stormtrooper's
  helmet above the tar; a tally board names what each cost.
- **Asks:** one good thing (the price, destroyed) and one effigy (the curse), both thrown in. The
  effigy is a cheap craftable item whose target is picked when it is made ("effigy of the Galactic
  Empire"). ⛔ Never a god (no god is evil or an enemy; the effigy cannot be made with one).
- **The Empire effigy (RULED, turn 2):** his words, *"(3) but it effectively holds off the Empire for
  x5 the normal time on this map"*. Imperial Heat is untouched (so this rite never launders Heat:
  Rite A does not either: it only pushes the next Empire probe or raid away). Instead the Empire's pressure on **this map** is held off for five times its
  normal interval. The "normal time" is the GM layer's **orbital-detection timer**, which drains
  toward the Empire finding the colony (placeholder start 60,000 ticks, about a day, in
  `gm_blackboard_shadow.py`); the curse multiplies the time left on this map's timer by 5 and holds
  any Empire raid or inspection off this map for the same span. ⚠ The real constants are still
  placeholders, and the vanilla-side Empire raid gate is UNMEASURED; it rides M4.
- **A faction effigy (RULED, turn 2):** **all** members of the next group of that faction seen on any
  map the player sees (raid, caravan, visitors, quest camp) arrive covered in tar: the moved
  `RM_Tarred` condition (slowed, stinking, filthy), black-coated, leaving a tar trail. One curse, one
  appearance. Goodwill untouched; they never learn who did it. The Narrator names it when they arrive.
- **A beast effigy** (proposed at turn 1, not ruled): the next of that species to wander in arrive
  tarred. Carried as a card option only if the owner wants it.
- **Readable signs:** the effigy sinking; the Narrator's line when the cursed group arrives; the
  black coats and trails; for the Empire, a map condition with its days left.

### What else could go in the tar: round 2, things a player on THIS map cares about

Round 1 (`sump_tar_rite.md`) missed. His words, typed: *"These are all really poignant, but they're
just not hitting. But so close! Try again, and try to make it something a player on THIS map would
care about. Really close though."* Round 1 reached outward (a faction's officers, a visitor, the
Narrator's past, a distant Junker station). Round 2 (`sump_tar_rite_r2.md`, prompt beside it, model
`gpt-5.6-sol`, his feedback quoted to GPT verbatim) asked for offerings from this colony with
consequences on this map within a day or two. The rule BENCH added on top: **the offering decides
where the rite's gamble lands**. Each is a further offering inside Rite A or B; the thrown thing is
destroyed, nothing comes back out.

| # | Offering | Rite | What happens on this map | BENCH's assessment |
|---|---|---|---|---|
| 1 | **The beast turns over:** the colony's ground-penetrating scanner, still holding its last survey | A | Within a day and a half the mice run outward from the tar beast's bulge and the Narrator marks a radius. The beast does not wake: it rolls once in its sleep, sending two or three slow pressure rings across the ground that crack glasswalk, collapse dig shafts and damage whatever was built in reach. | **Strongest:** it uses the giant he just ruled, on his own map, and punishes building where you knew you should not. L. |
| 2 | **The pump pays backward:** a sealed barrel of a day's output from the busiest pump | A | Within a day the pump's gauges reverse, the mice abandon its pipe route, and tar floods back out of its own barrel yard and pump shed. Depowering slows it; it cannot be stopped. | **The Sump's industry turned on itself**, and layout decides the damage. M. |
| 3 | **The empty stall:** the bed a bonded animal last slept in (never the animal) | A | Next night a thin ring of tar closes slowly around that animal's pen; the animal is named and visible, and the colony has hours to rope the herd out or lay duckboards across. The ring slumps back after a day. | **A beloved animal at stake** without sacrificing it; a rescue scene. M. |
| 4 | **The grudge at the table:** the best dining table as the price, and an effigy of a colonist another colonist truly hates | B | At the next meal, tar handprints appear at the gathering place, the hated pawn and up to four colonists with real grudges against them gather, and a visible lottery gives accusations, a social fight, or smashed furniture. All of it through ordinary social mechanics. | **The most personal**: the colony's own people. ⚠ It breaks BENCH's turn-1 line "no effigy of your own colonist"; that line was BENCH's, not his, and the card asks. M. |

Not carried: GPT's fifth (*the field keeps one candle*: a wick harvest thrown in, and a fire walks
the wick-garden's exact footprint), small and good, but it overlaps the seep-flame work already
ruled; kept in the consult file.

## 7. Turn 1 rulings (owner, 2026-10-01) and ticket-out

Recorded on the ledger at `372642ebb` and `c71911f79` (OWNER notes on this item).

| Card item | Ruling | Ticket |
|---|---|---|
| 1. Free tier | *"Move it all into the free mod that is now part of the Baroque Biomes mod"* (typed). | Rows 0, 0b, 0c |
| 2. Tar beast | **The full station-eater.** Decision taken by question card. | row 1 |
| 3. New ideas | **The Blackline capstan, revised into a turret on the lasso's pull** (typed, §5), **and the kethrel**. Pump rhythm and the buried dragline not taken. Lassos removed from the game. | rows 2, 3, 6 |
| 4. Rites | **None of the three offered.** His own rite, typed (§6), split into two at turn 2. | ruled (turn 3) |

FOUNDRY items, each `--caused-by SUMP_BEDAZZLE_SITTING_1`:

| slate row | item |
|---:|---|
| 0 | `SUMP_FREE_TIER_MOVE_BUILD_1` (into Baroque Biomes; the `RUT_Tarred` reference; frozen-world aliases; the inert Hssiss guard) |
| 0b | `SUMP_FAUNA_WIRING_BUILD_1` |
| 0c | `SUMP_HUNGRY_GOD_TEXT_1` |
| 1 | `SUMP_TAR_BEAST_BUILD_1` |
| 2 | `SUMP_CAPSTAN_TURRET_BUILD_1` |
| 3 | `SUMP_KETHREL_BUILD_1` |
| 6 | `LASSO_CHERRYPICKER_REMOVAL_1` |
| 7 | art: `infrastructure/artpipe/art_lists/sump_bedazzle_cast.csv` |

Rows 4 (seep flames and the discovery pilot) and 5 (sound) are not filed in this pass: row 4 is
ruled under `SUMP_GASLIGHT_1` pieces 5–6 and rides the tier move; row 5 stays the ordered backlog.

## 8. Turn 2 rulings

Turn 2, ledger `6daef10b1` (OWNER notes on this item), all typed:

| Card item | Ruling |
|---|---|
| Which god | Two rites: Rite A (one thing of value: ownership erased through RimProperty, the next Imperial probe or raid pushed away; see §9); Rite B to Mob'Unloo (a good thing plus a hated effigy, consequences on someone else, paid for by you). §6. |
| Empire heat | *"(3) but it effectively holds off the Empire for x5 the normal time on this map"*: the lull, five times the normal hold-off on this map, Heat untouched (now Rite B's Empire effigy). |
| Faction tar | All of the next group arrive tarred. |
| More offers | None of round 1 (*"just not hitting... make it something a player on THIS map would care about"*); round 2 in §6. |

## 9. Turns 2 and 3 ruled (2026-10-02) and ticket-out

OWNER and BENCH notes on `SUMP_BEDAZZLE_SITTING_1`, 2026-10-02. The offerings card was built from
`Transient/bedazzle_gpt_enrich_2026-10-01/sump_tar_offerings_redo_2026-10-02.md` (the redo), not from
§6's round-2 table.

| Subject | Ruling |
|---|---|
| Rite A, the Sinking | One thing of value into the tar: other parties' ownership claims are erased through RimProperty (typed). **God: Ishko**, decision taken by question card. **Empire effect (turn 3, 06:24 PDT), typed:** *"We already ruled this I thought. It doesn't actually reduce heat, it just pushes the next Imperial probe or raid away x5"*: Imperial Heat is not lowered; the next Imperial probe or raid is pushed 5x further away, the same hold-off as Rite B's Empire effigy. **Raid lull kept** (question card 06:28 PDT): other factions' raids also come less often on this map for a while. |
| Rite A offerings | By card: **the beast sleeps a season** (pitch thrown in: bulges ignore building, digging and pumping for a season; explosions still wake it) and **the ancient traps fizzle** (a dig find thrown in: the next three era traps the shafts roll click and go out harmlessly). Typed: *"I like Vault forgets, but it should be true about almost anything you own"*: the ownership wipe covers almost everything the colony owns, not only the tar vault. |
| Rite B, Mob'Unloo's Price | A good thing plus a hated effigy, consequences on someone else, paid by you (typed). **Empire effigy:** Heat untouched, the Empire held off this map for 5× the normal time (typed). **Faction effigy:** all of the next group of that faction arrive tarred (card). None of the redo's three further Rite B offerings taken. |
| Solvent wake | Typed: *"Oh! Throwing solvent into the pit should INSTANTLY wake the beast in Manhunter"*. By card: a deliberate player **weapon**, a scorched-earth last resort, not a rite and not a passive hazard; it serves **both** Sh'kaar and Zizzik at once (a rare shared offering). |

FOUNDRY items, each `--caused-by SUMP_BEDAZZLE_SITTING_1`:

| Unit | Item |
|---|---|
| RimProperty clear-claims call | `PROPERTY_CLAIM_ERASE_API_1` |
| Rite A with its two riders | `SUMP_SINKING_RITE_BUILD_1` |
| Rite B, the effigy and both effects | `SUMP_EFFIGY_RITE_BUILD_1` |
| The solvent wake | `SUMP_SOLVENT_WAKE_BUILD_1` |

They rely on `SUMP_TAR_BEAST_BUILD_1`, `SUMP_FREE_TIER_MOVE_BUILD_1`, `SALVATION_RITES_UNIFICATION_1`
and `GM_BLACKBOARD_SHADOW_M4_1`. Art owed: the effigy item and the two rites' inscriptions (the
Sinking's tally ring, the effigy ring); the solvent already has art.

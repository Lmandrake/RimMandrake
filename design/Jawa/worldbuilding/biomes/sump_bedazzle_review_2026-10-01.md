# The Sump: bedazzle review (grandfathered sitting, turn 1 ruled and ticketed; the tar-offering rite open)

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

## 6. The tar offering: the owner's rite (OPEN, turn 2)

None of the three offered rites was taken (the Giving-Back, the Deep Draw, the Reckoning of Owners;
the consult file and git keep them). The owner wrote his own, typed:

> *"There should be a rite where the tribe tosses an object of value as sacrifice into the tar, as
> well as an effigy of something hated. If it's the Empire, it might reduce the current heat level.
> If it's one of the factions, perhaps some of their members when next seen appear covered in tar.
> You should keep going on these ideas and flesh them out more. What else could be put in the tar?
> What else could it do?"*

Working name: **the Tar Offering**. Campaign tier (a Salvation rite: found here, learned through the
Rites tab's found-rites row, performable anywhere there is tar after: the mere, a pond, a poured
moat, a tar vault). The laws hold: **cohesion, never a material reward or a power**; **favour shows
only through events, world state and subtle odds**, told by the Narrator; a risky world event is
welcome.

### The shape

- **Found:** at a Junker station's edge, a sunk barrel-ring of effigies half-swallowed by the black,
  straw-and-rag figures in the colours of half the planet's factions, one still holding a carved
  stormtrooper's helmet out of the tar. A tally board names what each cost.
- **Asks:** two things, carried to the tar's edge and thrown in by the participants: **an object of
  value** (the sacrifice) and **an effigy of something hated** (the curse). Both are gone for good:
  the tar keeps them perfectly, and nothing comes back.
- **The object of value:** any single item over a market-value floor (a Mod Settings number). Its
  value sets the rite's quality, alongside the usual attendance and role terms. Weapons, art, gold,
  a masterwork: the tar takes them all. ⛔ No pawn, prisoner, corpse or animal: no living or dead
  body is ever thrown in (no human sacrifice; nothing vanishes without a sign).
- **The effigy:** a new craftable, cheap item made at a crafting spot, with a target picked when it
  is made (its label then reads "effigy of the Galactic Empire", etc.). The effigy carries the
  curse; the object carries the price.

### What the effigy can be

| Effigy | Allowed | Effect (the world, never a buff) |
|---|---|---|
| **The Galactic Empire** | yes | Imperial Heat falls (below). |
| **Any other faction** (Hutt Cartel, Homestead Defense League, Deep Desert Tribes, Free Droid Enclaves, Wildsteam Clan, Deepwater Compact, Geonosian Foundry Hive, Ascendant Helix, Blackstar Company, Jawa Trade Moot, the Junkers) | yes | Some of their members, the next time any group of theirs is seen, arrive covered in tar (below). Goodwill is untouched: they never learn who did it. |
| **A hated beast** (a species: the skarrid that took a child, a thrummel warden) | yes, proposed | For a while, that species keeps its distance from the colony: the next ones that wander in arrive tarred and slow, and the mouse-lines bend around where they lie up. Never deleted, never vanished. |
| **A god** | **no** | No god is ever evil, and no god may be made an enemy; the Salvation does not curse its own gods. The rite refuses a god as a target (the effigy cannot be made with one). |
| **The colony's own faction or a colonist** | no | A curse on your own is a different story and this rite does not tell it. |

### "The current heat level" is Imperial Heat

The campaign's Empire attention mechanic is **Imperial Heat**: one number kept by the GM layer
outside the save, not a stat in the game (`design/Jawa/build_plan.md` §2 and milestone M4,
*"Put all GM state outside the game. Imperial Heat, the orbital timer, the dark-tile flag..."*).
Sales of kyber raise it (`kyber_trade_plot_spec.md` §2–3); the Cathedral arc reads it
(`cathedral_concealment_arc_spec.md`). **Built state:** `src/RimMandrake/Utils/gm_blackboard_shadow.py`
computes it in **shadow mode only** (it logs what it would fire and fires nothing), under the open
item `GM_BLACKBOARD_SHADOW_M4_1`; the in-game gauge is a fast-follow at M4, not v1.

So the Empire effigy's effect is an **input to that blackboard**: the rite fires a history event
(`RUT_TarOffering_Empire`), and the blackboard reads it and lowers Heat. Until M4 leaves shadow
mode, the effect is logged, and the Narrator still speaks it. ⚠ **It collides with a standing
rule:** the kyber spec's K2 anti-laundering law says Heat is *"never scrubbed by success"*. The
owner's rite is a deliberate exception, and how big it is decides whether it becomes a laundering
loop (turn-2 card Q2).

### Covered in tar: the faction curse as a readable sign

The next time any group of the cursed faction appears on any map the player sees (a raid, a
caravan, visitors, a camp on a quest site), a share of its members (proposed: a third to a half,
scaled by rite quality) arrive **tarred**: the moved `RM_Tarred` condition (slowed, stinking,
filthy), black-coated sprites, and a tar trail of filth behind them. One curse, one appearance:
after that group it is spent. The Narrator names it when they arrive (*"the tar remembers who you
gave it"*). This is the readable sign the owner asked for; it is also an advantage in a fight, which
he chose, and the odds stay subtle (some, not all).

### Which god: Mob'Unloo, proposed

Mob'Unloo is debt, trade and exchange, and his catalog devotion already includes **the Collected
Grudge**. The rite is an exchange in its plainest form: a price paid (the object) for a grudge
collected (the effigy). Kind: **settlement**. Collision check: his Blind Offering (Abyss) is left in
the dark overnight; his Cold Ledger (Nightside Ice) seals a counter-gift to pay a dead man's debt.
Here a price is paid to curse a living enemy, and the tar keeps both. Alternatives are on the card.

### What else could go in the tar, and what else could it do? (GPT, five)

Consult: `Transient/bedazzle_gpt_enrich_2026-10-01/sump_tar_rite.md` (prompt beside it), model
`gpt-5.6-sol`, run 2026-10-01 on exactly the owner's question, five ideas, each a further offering
within this one rite. Assessed:

| # | GPT's idea | What goes in → what follows | BENCH's assessment |
|---|---|---|---|
| 1 | **The Weapon That Lost the Argument** | A weapon that has killed, bent first → the effigy faction's next armed group halts while its commanders quarrel, then either splits into two hostile groups or reconciles into one sharp, coordinated attack. | **Good gamble**: it can make the fight worse, which is the rite shape he picks. Needs a second lord job for a split force, M. |
| 2 | **The Threshold the Tar Keeps** | A door torn from the colony's cleanest room → hours later, tar seals every doorway of another very clean room until cut or dissolved with acid. | **Most Sump of the five** (the tidy are punished, the law he set), and small (S). It is a cost to the player, so it is a pure gamble with nothing gained. |
| 3 | **The Last Tool Has Standing** | A dead colonist's last tool or relic → a visitor who knew them (friend, rival, creditor) comes to argue the story of their life; no reward either way. | **Consolation, honestly grounded** in the pawn's real relations and tales. Weaker tie to the tar; M. |
| 4 | **A Black Box for Yesterday** | A recorder holding the colony's last three big incidents → the Narrator stages a dangerous "rhyme" of one of them. | **Not carded**: L, and it hands the storyteller a new authoring system that overlaps the GM layer. Kept in the consult file. |
| 5 | **Give the Pump Its Answer** | A working derrick head → a tar beast sets off toward one pumping site picked by an open lottery: it may wipe out a Junker station or cross the player's map. | **The biggest gamble**, and it uses the giant he just ruled. L (a tracked world journey); nothing spawns that can be fought. |

## 7. Turn 1 rulings (owner, 2026-10-01) and ticket-out

Recorded on the ledger at `372642ebb` and `c71911f79` (OWNER notes on this item).

| Card item | Ruling | Ticket |
|---|---|---|
| 1. Free tier | *"Move it all into the free mod that is now part of the Baroque Biomes mod"* (typed). | Rows 0, 0b, 0c |
| 2. Tar beast | **The full station-eater.** Decision taken by question card. | row 1 |
| 3. New ideas | **The Blackline capstan, revised into a turret on the lasso's pull** (typed, §5), **and the kethrel**. Pump rhythm and the buried dragline not taken. Lassos removed from the game. | rows 2, 3, 6 |
| 4. Rites | **None of the three offered.** His own rite, typed (§6). | open: turn 2 |

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

## 8. Draft turn-2 card: the Tar Offering

For BENCH to put to the owner. Four questions; Q4 is multi-select. Each explains its subject in
full.

**Q1. Header: `Which god`.** *Your tar rite: the colony throws a valuable object and an effigy of
something it hates into the tar, and the tar keeps both forever. Every Salvation rite belongs to one
of the nine gods. Which god does the tar offering speak to?*

| Option | What it buys | What it costs |
|---|---|---|
| **Mob'Unloo** *(recommended: he is debt and exchange, and "a price paid for a grudge collected" is his plainest form)* | A clean fit: the object is the price, the effigy is the grudge. His existing devotion "the Collected Grudge" already names the idea. | He already has two offering rites (the Blind Offering in the dark, the Cold Ledger in the ice); this is his third. |
| **Ishko** | The god of hiding and the prepared ambush: the curse is a trap laid ahead for an enemy who has not arrived yet. | A looser fit for a rite that pays a price; Ishko's rites so far are about stillness and the dark. |
| **Zizzik** | The wrong spark: the tar fouls the enemy's works and their next group arrives broken and filthy. He loves this kind of mischief. | He already has five rites, so he keeps growing while others stay thin. |

**Q2. Header: `Empire heat`.** *"The current heat level" is Imperial Heat: one number the game-master
layer keeps outside the save, measuring how hard the Empire is looking for you. Selling kyber raises
it; raids, inspections and orbital detection key off it. Today it runs in a watch-only test mode
that fires nothing. A standing rule says Heat is never lowered by success, so it cannot be
laundered. How strong should an Empire effigy be?*

| Option | What it buys | What it costs |
|---|---|---|
| **A modest drop, once a season** *(recommended: your rite stays real without becoming a way to wash Heat clean)* | Each Empire offering lowers Heat by a small step, scaled by the value thrown in, at most once a season. The Narrator tells it. | The effect is quiet: a slight easing you feel over weeks, not a reprieve. |
| **A big drop, with a gamble** | A large drop, but sometimes the Empire hears of a burned stormtrooper and Heat rises instead. A real bet. | Can backfire badly; the odds need tuning in play. |
| **A lull, not a drop** | Heat is untouched (the no-laundering rule holds), but the Empire's next raid or inspection is delayed for a while. | It does not lower "the heat level" as you said; it only buys time. |

**Q3. Header: `Faction tar`.** *An effigy of any other faction curses that faction: the next time a
group of theirs is seen (a raid, a caravan, visitors), some of its members arrive covered in tar:
slowed, stinking and leaving a black trail, and the Narrator says why. Goodwill does not change;
they never learn who did it. How much tar?*

| Option | What it buys | What it costs |
|---|---|---|
| **Some of the next group** *(recommended: your words were "some of their members", and subtle odds are the rule for a god's favour)* | A third to a half of that one group arrives tarred, more if the offering was rich. One curse, one appearance. | A modest edge in that one fight or trade. |
| **All of the next group** | Unmistakable: every member arrives black with tar. | A big edge against a raid, which leans toward a reward. |
| **Lasting, thinning** | Their groups arrive with a few tarred members for a season, fewer each time. | Longer bookkeeping; the curse becomes a background condition rather than an event. |

**Q4. Header: `More offers`.** *You asked what else could go in the tar and what else it could do.
GPT gave five; four are here (the fifth, a recorder whose incidents the Narrator re-stages, is too
large and overlaps the game-master layer). Each is a further offering within the same rite. Pick any.*

| Option | What it buys | What it costs |
|---|---|---|
| **Threshold kept** *(recommended: it is the Sump's own law, the tidy punished, and it is the smallest build)* | Throw in a door torn from your cleanest room; hours later the tar seals every doorway of another very clean room until you cut it free or dissolve it with acid. | Pure risk to yourself, nothing gained but the rite's cohesion. Small build. |
| **Pump's answer** | Throw in a working derrick head; a tar beast sets off toward one pumping site picked by an open lottery: it may wipe out a Junker station or cross your own map. | The biggest gamble, and a large build (a tracked journey across the world map). |
| **Weapon's quarrel** | Throw in a weapon that has killed; the cursed faction's next armed group halts while its commanders argue, then splits into two hostile bands or comes at you as one sharper attack. | Can make the fight worse. Medium build. |
| **Last tool** | Throw in a dead colonist's last tool; someone who knew them (a friend, a rival, a creditor) comes to argue the story of their life, with no reward either way. | A quiet, sad event; the weakest tie to the tar. Medium build. |

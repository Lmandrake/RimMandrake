# The Rot: bedazzle review (grandfathered sitting, turn 1 drafted)

Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 8. Item:
`ROT_SCORING_SITTING_1`. Turn 1 is ruled: §8.

_BENCH design pass, 2026-10-02. Eighth sitting of the grandfathered track, in the order of
`grandfathered_bedazzle_scores_2026-10-01.md` (§ The Rot; sitting order row 8). The sheet `the_rot.md` is
frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07) with two ratified amendments (the cold-tail repaint,
2026-09-08; the def tails, 2026-09-08). Already ruled and **not re-argued here**: the Sheen and its
exposure ladder, warm ground, the rot clock, living produce, the come-here-and-brew law (teas and
symbionts die off-site), guardianship as a law of potency, hybrid-or-out fauna, health-sharing in both
variants, the pale tree's lightest touch, the blastpod chain wild-only, the fungal power generator CUT,
and the 2026-09-24 cast sitting (10 ports to `RM_`, names thozzik / illoth / brullith / brogg / grellik /
skerrith; our own spore allergy). The nine hard bans of sheet §6 bind every slate row; the ones that bite
hardest here: **no green plants** (1), **every resident a fungus/animal hybrid** (2), **no water rain**
(3), **no stockpilable teas or symbionts** (4), **no active bioweapon** (7), **no undefended prizes** (8)._

Sources read, all in the BENCH clone: `src/RimMandrake/TheRot/` (BiomeDef
`Defs/BiomeDefs/RM_TheRot_Biome.xml`, every def folder, `About.xml`, `Source/RM_TheRotMod.cs` and the
biome worker, `Patches/RotSpecies_NamesAndSizes.xml` parsed per op), the frozen twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml`, every patch or C# file under `src/` that
names the biome (`WildAnimals_TheRot.xml`, `BiomeDescriptions_Ashkarr.xml`, `BiomeFlora_Ashkarr.xml`,
the EnvironmentalHazards warm-ground / accelerated-rot / living-produce sources, and
`src/RimUtinni/FungalSoilTrade/`, whose gate is read below), `RSW_BiomesTeamPort_Races.xml` for the ten
ports' bodies and descriptions, `rot_rm_cast_proposal_2026-09-24.md` and its ruling, the closed
`THEROT_RM_MOD_BUILD_1` and its ledger trail, `THE_ROT_FIRST_SCRIPT_1`, the CreatureBehaviors wound-link
and kin-mending sources, `divine_satiation_engine.md` §①–⑨, the register
`design/Jawa/salvation_rites_2026-10-01.md`, the ledger's 2026-10-02 rulings (Webwork, Greentide, the
Open Boast, the Rust Cathedral's turn 1), and the Rust Cathedral review for shape. Rosters were parsed as
XML elements; the creature census reads descriptions (the free tier's donor bodies carry our own names
and descriptions through the names patch), not defNames.

## 0. The Rot in plain words (for the card)

The Rot is the planet's gut: a pale fungal continent on the cold night side of the great storm wall,
where everything the sky blows off the day side falls and is digested. Towers of bone-white and lilac
fungus stand under a black sky, the floor is a glowing mat that is warm to lie on while the air above
it would freeze you, and the ponds are milky not-water. The jungle breathes out a sticky fog, the
Sheen, that sickens anyone who has not adapted, so the place guards its own border with its breath.
Meat rots in a day, harvested food stays alive and warm, and every creature is half animal, half
fungus; hurt one and the others come. Its treasures are live brews that work like a body-sculpting
machine in a cup, and they die if you try to take them away: you come here and brew on the spot, past
mushrooms that defend themselves with choking spores. It has no voice of its own, nothing to do with
the ship, a giant borrowed from another mod, and no god's rite yet.

## 1. What is there: ruled vs built

### A deep free kit, with its creatures still borrowed

`src/RimMandrake/TheRot/` (`mandrake.rm.therot`, absorbed whole from the retired RotSporeKit on
2026-09-25, `THEROT_RM_MOD_BUILD_1`, closed) ships: the three Sheen weathers (`RM_SheenFall`,
`RM_SheenStorm`, `RM_SheenMist`, 30 of 39 weather weight) and the exposure lock (`RM_SheenExposureLock`,
`RM_SheenCoating`, `RM_SheenProtection` stat); warm ground, accelerated rot and living produce (shared
`mandrake.rm.environmentalhazards` extensions; the mat warms rooms through vanilla room temperature,
capped at 21 °C, so it obeys the one-heat law); the spore kit (`RM_ToxicSpores`, `RM_StunningSpores`,
`RM_SporeCloud`, `RM_SporeFlesh`, `RM_SporesBuildup`); **the three teas and four symbionts plus the
toxic injection**, brewed live in `RM_BrewingVessel` and dying off-site; three **guardian groves**
(ageless cap: spore gas; regenerant veil: network alarm; euphoric crown: a ring of false fruit); the
treasure conscience; the grown furnace, the furnace cap and the heat gene `RM_Gene_Furnaceblood`;
mushroom leather, bridges, floors, glow-goo torches, fungiponics, blastpod chemfuel; the thrumbungus
grenade; one research project (`RM_AdvancedFungi`); the pale tree; 30 wild-plant rows (17 ours, 13 Alpha
Biomes donor, renamed and retextured by `RotSpecies_NamesAndSizes.xml`); its own biome worker and ground
terrains. Every gate names **`RM_TheRot`**. The campaign layer's biome content is the frozen twin
`RUT_TheRot` (donor worker, the same 20-row roster before the split) and `mandrake.rut.fungalsoiltrade`.

### 🔴 The two systemic defects of the last three sittings: checked, and BOTH ARE PRESENT here

- **(a) Invented content stranded in the campaign tier: YES, ten creatures, already ruled to move.**
  The 2026-09-24 card ratified moving the ten Biomes! Team ports to `RM_` (they are invented, not Star
  Wars: Q11a). The art for six of them was regenerated the next day (`rot_thozzik*`, `rot_illoth_*`,
  `rot_brullith_*`, `rot_brogg_*`, `rot_skerrith_*` are in the artpipe `done/`, MEASURED with
  `artpipe_state.py find`). **The defs never moved:** `RM_Thozzik`, `RM_Illoth`, `RM_Brullith`,
  `RM_Brogg`, `RM_Grellik` and `RM_Skerrith` exist nowhere in `src/` (searched), all ten still ship as
  `RSW_` rows in the campaign patch `WildAnimals_TheRot.xml`, and `THEROT_RM_MOD_BUILD_1` closed
  2026-09-25 without them. So the free mod has **zero creatures of its own body**; every one of its
  eight rows is an Alpha Animals donor wearing our name and description. The ratified spore-allergy
  port is unbuilt too: the free def still names `AB_Disease_SporesAllergy` (searched; no `RM_` allergy
  exists). A second strand: **the fungal-soil trade** (dig the mat, the hybrids rise in distress) is
  invented, not IP, and lives only in `mandrake.rut.fungalsoiltrade`.
- **(b) Campaign mechanics wired to a def that will not carry the biome: YES, and it is dead today, not
  only at the repaint.** `FungalSoilTrade`'s C# and its GenStep self-gate to
  `RotBiomeDefName = "AB_MycoticJungle"` (`MapComponent_RotFungalDistress.cs`,
  `RUT_FungalSoilScatter.xml`), the **donor** def. `BIOME_WORLD_SWITCH_WAVE_1`'s mapping table records
  the Rot repainted from `AB_MycoticJungle` onto `RM_TheRot` (its record, not re-measured live this
  pass), so on a repainted Rot map the knots never scatter and the distress never fires, and after the
  final paint it is dead everywhere: a built mechanic that silently does nothing (the kind
  `FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1` exists to catch). The fix is one string and one GenStep gate.
  The cast patch itself is clean of the other half of (b): `WildAnimals_TheRot.xml` uses
  `PatchOperationAdd` onto `RM_TheRot`, never a Replace, and the twin carries no mechanic the free def
  lacks. ⚠ Its first op's guard is `<Operation … MayRequire="mandrake.rsw.swbestiary">`, the top-level
  form the engine ignores (`PATCH_MAYREQUIRE_GUARD_INERT_1`'s family); harmless while the bestiary is
  always loaded, listed for that sweep.
- **The reverse slip, IP in the free tier:** `RM_PaleTree`'s description says *"a faint, tugging sense
  of the Force"* inside an `RM_` def (the scores doc flagged it). One sentence; the free text should say
  something franchise-free and the campaign should patch the Force back in.

### Fauna, merged (inline + patch-added), read as XML elements, census by description

**Free tier, `RM_TheRot/wildAnimals` (8 rows, all `MayRequire="sarg.alphaanimals"` on the element):**
rennok (`AA_Agaripawn` 0.2, *"hurt one and the others in the grove feel it and come"*), gromma
(`AA_Agaripod` 0.25, *"feels the wounds"* of its kin), vorrugath (`AA_MycoidColossus` 0.25, *"a walking
piece of the pale forest… six-legged colossus… its back a grove of full-grown caps"*), chittik
(`AA_Swarmling` 0.3, *"a single body with a hundred mouths that shares every wound it takes"*), durrok
(`AA_Wildpawn` 0.2), mullgoth (`AA_Wildpod` 0.2, *"its kin heal faster near it"*), plus `AA_AngelMoth`
0.5 and `AA_AnimaColossus` 0.5 (no names-patch rows read for these two). `animalDensity 1.9`. Without
Alpha Animals the free Rot has **no animals at all**; Q9 allows donor rows inline, but Q11a asks the
free mod to stand alone, and it does not.

**Campaign patch-adds to `RM_TheRot` (12 rows, xpath resolved, `PatchOperationAdd`):** the ten ports
(thozzik ×3 forms and 2 queens at 0.2–0.5, smog moth 0.5, thrumbungus 0.5, yooka 0.5, grellik 0.4,
skerrith 0.15) plus `RSW_ShiroTrap` 0.5 and `Snoruuk` 0.5 (the two genuine Star Wars rows, correctly
campaign-side).

**Flora:** 35 rows (30 base + the three tea mushrooms, the false fruit and the pale tree), all fungal.
Not a gap.

**Findings in the cast:**
- **Health-sharing is ruled, promised in five descriptions, and wired to nothing.** CreatureBehaviors
  ships `RM_CompWoundLink` (true splitting) and `RM_HediffComp_KinMending` (the tend-aura), the exact two
  variants the sheet rules, but no Rot creature carries either (searched every XML for `WoundLink` /
  `KinMending`: comment references only). Whether the Alpha Animals bodies do something similar on their
  own is UNMEASURED; our sentence promises it either way. The sheet's *"your herd bleeds as one"* is
  unbuilt.
- **Two ports fail ban 2 by their own descriptions.** The yooka (to become the brogg) is *"closely
  related to camels and llamas"* with no fungus in it, and the smog moth (to become the illoth) is a
  plain bioluminescent moth. The thozzik hornets are wasps with toxic gas, also no fungus. The migration
  is the moment to rewrite their descriptions as hybrids (the grellik's and skerrith's already are).
- **The thrumbungus's description says it was *"created from… a failed genetics experiment"***: ban 7
  territory (no engineered organisms). The brullith rewrite should drop the lab origin.
- **The Rot's own giant is donor-bodied** (vorrugath) and its second colossus is the anima colossus, a
  donor with no description of ours.
- **Multi-homed species:** not re-censused this pass (UNMEASURED); listed only, never evicted.

### Heat

The Rot is **not** an extreme-heat biome (median −18.8 °C, floor −42 °C): the one-heat law needs no
heat-kind declaration here. Its warmth is vanilla room temperature from the mat (measured in
`RM_MapComponent_WarmGround.cs`), and the heat gene and grown furnace are vanilla heat sources. Clean.

### Ruled mechanics, built and unbuilt

- **Built (free):** Sheen weathers and exposure, warm ground, accelerated rot, living produce, the spore
  kit, the teas, symbionts and injection with their viability clock, three guardian groves, the treasure
  conscience, grown heaters and the heat gene, the materials and buildings, the pale tree.
- **Built but hollow (free):** **the Mod Settings screen is scaffolding.** `RM_TheRotMod.cs` says so in
  its own header: *"Toggling a switch below therefore does not yet change whether the shared mechanic
  runs"*; the real gates read the EnvironmentalHazards settings. Fourteen toggles and sliders a player
  can move that do nothing breaks the Mod Settings rule outright.
- **Ruled, unbuilt (free):** health-sharing (both variants; comps exist elsewhere), the ten-creature
  migration with hybrid descriptions, the own spore allergy, the guardian repertoire beyond three groves
  (*"hybrid defenders summoned through the mycelial network, the mat itself grasping"*, §7), the milk
  ponds as not-water terrain (owed in the sheet's feasibility list; not found as a terrain in the kit),
  instant composting as a service, the sound (§9: *"the donor's insect hum day and night; wet settling;
  the hiss of Sheen-fall; warmth you can hear as slow subterranean movement"*).
- **Ruled, unbuilt (campaign):** the Wildsteam sacred groves and pilgrim paths, brewing stations
  *"maintained by whoever came last"*, digestion sites richer in genepacks (§8), the fungal-soil trade
  (built, gated on the dead donor def).
- **Unruled marks:** our own giant (5), a ship touch (6), a sound (7), a god and a rite (9); a learned
  technology that travels (2).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `RM_CompWoundLink`, `CompProperties_KinMending` / `RM_HediffComp_KinMending`
  (`mandrake.rm.creaturebehaviors`, already a hard dependency of the Rot): health-sharing is wiring, not
  a build; a giant built around shared wounds starts from these.
- `RM_SheenCoating` and `RUT_HediffComp_SheenExposure`: anything the Sheen does to a hull or a pawn reads
  the existing coating, never a new meter.
- `RM_MapComponent_WarmGround`, `RM_AcceleratedRotExtension`, `RM_LivingProduceExtension`: a sound that
  reads the mat, or a giant whose resting place warms or digests, reuses them.
- `RM_BrewingVessel` and the live-prep viability patch (`RM_Patch_LivePrepViability`): a learned
  technology must route **around** this, never make a tea portable (ban 4).
- `RM_RotTreasureConscience` / `RM_SoldRotTreasureMemory`: the trade-identity hook already exists.
- `MapComponent_RotFungalDistress` (campaign): the distress-rise is the right shape for a network alarm,
  once regated to `RM_TheRot`.
- The Rites tab's found-rites row and `RUT_ResearchMod_GrantRite` (register §d).
- The artpipe already holds finished renders for thozzik, thozzik queen, illoth, brullith, brogg and
  skerrith (three facings each): the migration needs no new art.

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against the
sheet, the 2026-09-24 cast ruling and the source. Two marks move from the scores doc, both on evidence.

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | Sheen exposure lock, warm ground, rot clock, living produce, live preparations, guardian groves: all free | health-sharing is ruled and unwired; the settings screen is hollow |
| 2 | Discoverable technology | PARTIAL | PARTIAL | one generic research project (`RM_AdvancedFungi`) | the teas and symbionts are recipes and may not travel (ban 4); nothing learned here works elsewhere |
| 3 | Unique resources | **HIT** | **HIT** | teas, symbionts, toxic injection, furnace cap, mushroom leather, blast spores, ambrosyx, moonless silk: all free | |
| 4 | Surprising creatures | **HIT** | **HIT** | 0 owned bodies: 8 donor bodies under our names (free), 10 invented ports still `RSW_` (campaign) | **moved from PARTIAL**: the 2026-09-24 card ruled the ten ports into the free tier with the skerrith (a mantis that passes as a cap) and the grellik (a weevil in partnership with its fungus); ruled, art done, defs never moved |
| 5 | GIANT beast | PARTIAL | PARTIAL | vorrugath and the anima colossus, both donor bodies | the brullith (ruled ours, bs 4) is large, not giant |
| 6 | Gravship touch | MISS | MISS | 0 | nothing in the mod, the twin or the campaign touches the ship |
| 7 | Soundscape | PARTIAL | PARTIAL | 0 (no SoundDef in the mod) | **moved from MISS**: sheet §9 rules the sound (*"insect hum day and night; wet settling; the hiss of Sheen-fall; warmth you can hear as slow subterranean movement"*); nothing plays it and nothing does work with it |
| 8 | Interesting weather | **HIT** | **HIT** | Sheen-fall, Sheen-storm, Sheen-mist (30 of 39 weight), spore clouds | |
| 9 | Relationship to the gods | PARTIAL | PARTIAL | the pale tree (sacred to the wild creed) | the Wildsteam groves are ruled, unbuilt; no Salvation god, no rite; the tree's text names the Force inside an `RM_` def |

**Free 4 HIT / 4 PARTIAL / 1 MISS. Campaign 4 HIT / 4 PARTIAL / 1 MISS.** The scores doc had 3/4/2 on
both; mark 4 rises on the ratified cast, mark 7 on the sheet's ruled sound. Unlike the Rust Cathedral,
**the Rot's top problem is not a missing mark but ruled work that never landed**: ten ratified creatures,
the own spore allergy, health-sharing, a real settings screen, and a campaign trade gated on a dead def.
The genuinely unruled misses are a giant of our own, the ship, a sound that does work, a learned
technology that travels, and a god.

**Rite: none.** The scores doc's seed (*"a meditation/communion rite before the pale tree"*) is taken
in kind and in tier: meditation before a sacred tree is the Wildsteam's (the wild creed, not the
Salvation), and a still vigil is Ishko's (the Dark Vigil, the Stall-Hold). §6 pitches for the three gods
with the most room and the clearest tie to a gut that digests everything: Mob'Unloo, Ta'Baa and Oomo.

## 3. Roster fill

### The gaps, read from the sheet's sorts (§4, §7) and the ruled roster only

Ban 2 shapes every fill: a new resident must be a fungus/animal hybrid, never a pure animal.

| sort (sheet §4, §7) | free tier today | campaign today | fill |
|---|---|---|---|
| Hybrid natives (the mounds) | rennok, gromma, durrok, mullgoth: donor bodies, our names | same | **wire health-sharing** onto them (the comps exist) |
| Swarm vermin | chittik (donor body) | same | wire its *"shares every wound"* |
| Hive insects | none | thozzik ×5 forms (`RSW_`) | **apply the ruled migration**; rewrite the description as a hybrid (today: plain wasps) |
| Lure-light flier | angel moth (donor, no text of ours) | illoth (`RSW_SmogMoth`) | migrate; rewrite as a hybrid (today: a plain moth); confirm it flies (`MaxFlightTime`) |
| Fungus partners | none | grellik, skerrith (`RSW_`) | migrate (descriptions already hybrid) |
| Large grazers | none | brogg (`RSW_Yooka`), brullith (`RSW_Thrumbungus`) | migrate; the brogg's *"related to camels and llamas"* fails ban 2 and is rewritten; the brullith drops its lab origin (ban 7) |
| **Network defenders** (§7: *"hybrid defenders summoned through the mycelial network, the mat itself grasping"*) | none | none | a hole the sheet opened; filled by the giant below if he picks the wound-bearer, otherwise left for the guardian-repertoire pass |
| **The giant, our own** | vorrugath, anima colossus: donor bodies | same | **the yssomar** or **the hwelgrue**, below (card Q2) |
| The milk ponds | flora only (nuitae, wrinklecap, nogtyl, arpeau marsh forms) | same | none: the roster ruled no fish (*"the milk ponds are not-water"*) |

Names follow this biome's own accent, which is **coined two- and three-syllable names** (rennok, gromma,
vorrugath, thozzik), unlike the Rust Cathedral's plain compounds. Collision-proven 2026-10-02: **yssomar**
and **hwelgrue** return zero files in `src/`, `design/`, `infrastructure/`, their four-letter stems
(`ysso`, `hwel`) open no other word in `src/` or `design/`, and both return zero Wookieepedia search hits
(sanity probes: `korrum` 94 repo files; `mynock` and `wyyyschokk` 10 Wookieepedia hits each). Rejected on
the stem rule: *ossumbrel* (ossuvel, ossumar), *oruvanth* (oruvell), *thessmaw* (thessmoss, thessamor),
*pellagorm* (pellorax, pellareth), *murrogaunt* (murrelith, murrek), *ghessimor* (ghessum). Both are one
home, free tier, alien in colour, never tamed.

- **The yssomar** (`RM_Yssomar`, the wound-bearer: the law of the place made a body). A colossal, slow
  hybrid, a hill of grey-lilac caps over a long body like coral grown over a beached whale, six stubby
  legs hidden under a skirt of gills, its hide a patchwork of healed scars **that are not its own**. When
  any hybrid on the map is badly hurt, the yssomar draws part of the wound into itself and walks toward
  the pain; the small ones live, the giant carries it. So hunting in the Rot calls the giant to the kill,
  and every wound you deal on the map piles onto it. It never attacks first and never hunts (it is the
  forest's sink, not its fist); hurt it and every hybrid near it shares *its* wound in return and comes
  (the network defenders the sheet asked for, made of the creatures already there). Killing it is the
  worst thing you can do here: when it falls, every linked creature takes back its share at once, a
  mass bleeding across the map, readable as a letter, a sound and dozens of sudden wounds. Your tamed
  hybrids near it share too (*"your herd bleeds as one"*, ruled). **Reuses:** `RM_CompWoundLink`
  (map-scope, one-way into the giant) and `RM_HediffComp_KinMending`, the warm-ground map component for
  the warm hollow it sleeps in, a vanilla wander-to-target think node. Static art in three facings, no
  new rig. Not a neighbour's giant: the furnace-beast is warmth you stand near, the tar beast a
  catastrophe you evacuate, the thurrock herd a noise that fells trees, the Cathedral's mining droid a
  dim, armoured peaceful machine; the yssomar is **the one giant whose danger is your own violence**.
  - *Plot hooks (owner's style; pick or rewrite):* (1) its oldest scars are not organic: a line of
    old blaster burns and one wide brand the ship's Narrator recognises as the pattern of its own
    guns, so the gravship fired on this continent in an age before the Jawa found it, and the giant
    still carries that wound. (2) Offworld healers pay fortunes for a scar-cap shed from it, which the
    clan can sell only if it was shed, never cut: a trader's temptation the treasure conscience
    already reads. (3) A Wildsteam pilgrim asks the clan to escort the yssomar's slow walk to a dying
    grove; on the way every fight costs the giant.
- **The hwelgrue** (`RM_Hwelgrue`, the gut that walks: the rot clock on legs). A colossal decomposer,
  low and broad as a hull, bone-white with a lilac underside and a mouth like a dredge rimmed with
  feeding hyphae. It eats what lies down: carcasses, wrecks, rotten stockpiles, ruins, and digests all
  of it except metal. Where it rests the mat spreads warm and everything near rots three times faster.
  It never hunts, but a downed colonist on open ground is *lying down*, so it is a giant you guard your
  wounded from. **Jawa tie:** it passes what it cannot digest as Sheen-glazed salvage castings, polished
  metal parts in a glossy shell, so scavengers follow it as crows follow a plough, and its trail is a
  salvage line. **Reuses:** `RM_AcceleratedRotExtension` (local multiplier), the warm-ground component,
  vanilla corpse-eating, a custom drop on a timer. Not a neighbour's giant: the Lantern Deeps' methane
  giant is pinned to a ceiling, the Sump's tar beast preserves, the hwelgrue **digests**, and it is the
  one giant the clan follows for profit.
  - *Plot hooks:* (1) long ago it swallowed a piece of a Rakatan ship, and the gravship's sensors ping
    it on every landing in the Rot; the part comes out only when it dies or passes it. (2) Imperial
    salvage crews have started following it too; a trail shared with rivals. (3) Its castings sell well
    in the bazaar, but one day a casting holds a sealed data core.
- **Wire, don't invent:** the ten ports (ruled), health-sharing (ruled), the own spore allergy (ruled).
- **Retire on the move:** the ten `RSW_` rows from `WildAnimals_TheRot.xml` once the `RM_` defs exist;
  `RSW_ShiroTrap` and `Snoruuk` stay campaign-side (genuine Star Wars).

## 4. The slate

Proposed for owner turn 1. Row 0 executes existing rulings (the 2026-09-24 cast card, the sheet's
health-sharing and sound, the Mod Settings rule, the tier grammar); rows 1 onward need his word.
Nothing here touches tiles, and nothing on the slate makes a tea or symbiont portable (ban 4).

**0. Land what was already ruled (free tier, plus one campaign string).** In `mandrake.rm.therot`:
- **The ten creatures:** create `RM_Thozzik` (+ colony, spawned, two queens), `RM_Illoth`,
  `RM_Brullith`, `RM_Brogg`, `RM_Grellik`, `RM_Skerrith` from the `RSW_BiomesTeamPort_Races.xml` bodies,
  wired to the finished artpipe renders; rows inline on `RM_TheRot`; drop them from
  `WildAnimals_TheRot.xml`. Rewrite four descriptions as hybrids (thozzik, illoth, brogg: today pure
  animals, ban 2; brullith: drop the lab origin, ban 7). The illoth is a moth: real flight (the flyers
  rule).
- **Health-sharing:** attach `RM_CompWoundLink` to the species whose text promises splitting (chittik,
  rennok, gromma) and kin-mending to the ones that promise healing (mullgoth, durrok), tamed included.
- **The own spore allergy:** two `RM_` hediff/incident pairs replacing the `AB_` pair (ruled 2026-09-24).
- **A real Mod Settings screen:** make `RM_TheRotSettings` gate what it claims (or delete its dead
  toggles and point at the EnvironmentalHazards screen); every toggle a player can move must do
  something.
- **The pale tree's text:** franchise-free in the free def; the campaign patches the Force line back.
- **Campaign, one string:** regate `FungalSoilTrade` from `AB_MycoticJungle` to `RM_TheRot` (C# const and
  the GenStep), so the dig-and-distress trade fires at all.
Size M (no new design; the art exists; the comps exist).

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The giant** (§3): the yssomar (the wound-bearer), the hwelgrue (the gut that walks), or §5 idea 2 (the brullith that cannot lie down), with a plot hook. | 5 | wound-link and kin-mending comps (yssomar); accelerated-rot extension, warm ground (hwelgrue) | M to L |
| 2 | **The sheened hull** (BENCH, merged with §5 idea 3): a ship landed in the Rot slowly takes the Sheen; it matures in stages (film, then pale fruiting pockets along seams and cargo bays; late pockets cost deck sections to cut out). Scrape them off before launch (hours of work in the Sheen, exposure running) or launch with them: at the next landing anywhere they drop, and a small warm patch of Rot mat with a few Rot fungi takes root around the landing site and spreads slowly unless burned. The biome marks the ship by **using it to travel**, which is what the Sheen is for. | 6 | `RM_SheenCoating`, warm-ground terrain, the Rot's flora defs, a landing hook | M |
| 3 | **The mat's pulse** (BENCH): the warm ground has a slow heartbeat (sheet: *"a heartbeat of rot"*) you hear underfoot; it quickens when a guardian grove is roused, when the hybrids converge to share a wound, and before a spore cloud vents, so the sound is the network's alarm. Plus §5 idea 4, each guardian grove's audible breath (in-breath, clicks, hiss, quiet) as the local timer for a brewing trip, and the ruled ambient bed: insect hum, wet settling, the hiss of Sheen-fall. | 7 | SoundDefs, a map component reading groves, wound-link events and the spore incident | S to M |
| 4 | **Unseaming** (§5 idea 1): learned from a defended digestive fungus at a digestion site; take damaged weapons and machines apart into their component assemblies instead of smelting them, anywhere. (BENCH's wound-tie, below, is the alternative.) | 2 | research row, recipes, a teardown profile def | M |
| 5 | **A Salvation rite** (§6 R1, R2, R3, or §5 idea 5, the Bought Quarrel). | 9 | found-rites row, `RUT_ResearchMod_GrantRite` | M |
| 6 | **Art commission:** the giant (three facings, plus a carcass; the brullith option reuses its finished render plus a yoke overlay), the fruiting hull overlay, the unseaming bench, the dead-symbiont husk, the rite's inscription. The ten ports need **no** new art. | all | artpipe (check existing renders first) | — |

**BENCH's own mark-2 candidate, the wound-tie:** researchers study how the hybrids share wounds and learn
a surgery that ties two colonists together (or a colonist and an animal): for a season, any injury one
takes is split between them, after which the tie withers and leaves a scar. Usable anywhere, powerful
(a bodyguard and a ward share a life), costly (each tie needs a nerve-cord harvested from a hybrid that
shares wounds, which defends itself by calling its kin; both tied pawns feel every hit). It travels
because it is a *technique and an organ*, not a live brew. ⚠ It shares its root with the yssomar (both
grow from the shared-wounds law); if he picks the yssomar, prefer a GPT tech so the biome does not say
one thing twice.

🔴 **Sequencing:** row 0 first; it is the largest part of this sitting's value and every later row leans
on it (the yssomar needs wound-link working on the small ones; the pulse reads wound-link events; the
sheened hull reads the coating). `THE_ROT_FIRST_SCRIPT_1` should be written against row 0's state.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-02/rot_gpt.md` (prompt beside it, `rot_gpt.prompt.md`),
run 2026-10-02 under the standing rule (`BEDAZZLE_TOP_SHAPE_PROGRAM_1`, ruling 2026-10-01): exactly five
ideas, different from each other (GPT's own check: verbs unseam / triage / quarantine / time /
underwrite; systems salvage fabrication / shared-injury medicine / gravship biosecurity / acoustic hazard
timing / ritual diplomacy) and from every other biome's signature, which the prompt listed in full,
**including the Webwork's, the Greentide's and the Rust Cathedral's 2026-10-02 rulings** (urraveth,
traction lance, Felled Noon; thurrock, blood-stopping lace, Ceded Room, Open Boast; the mining-droid
giant, the spying stowaway bolts, the Mending Weld and the droid-repair rite). Model `gpt-6.1-sol`, high
effort, via `gpt_consult.py`, answered first try (started 10:07, written 10:18 PDT, 11 minutes). GPT cites
Anomaly's fleshsacks, Terra Nil, Dwarf Fortress medicine, VFE Insectoids 2, Death Stranding, Against the
Storm's Blightrot cysts, Odyssey gravships, Rain World, ReGrowth's ambience, Pathologic 2's barter and
Ideology rituals; its links are not verified here. GPT answered all five gaps it was given.
Names checked in the repo (zero files each for *unseaming*, *bought quarrel*,
*grove breath*, *hull brood*; probe `korrum` 95): all clear. English phrases, so no Wookieepedia check.

| # | GPT's idea | mark | tier | size | BENCH read |
|---|---|---|---|---|---|
| 1 | **Unseaming:** study how a defended digestive fungus strips organic binders off machinery and leaves the metal assemblies intact; learn an industrial process (fired fungal rind, reagent, precision clamps) that takes apart a damaged weapon or machine into its **component assemblies** instead of smelting it. Usable anywhere. | 2 | free | M | **Strongest, and the best fit with the clan.** The gut that digests everything but metal teaches the scavengers to do the same: a salvage specialism, learned here, that travels (ban 4 holds: nothing live leaves). Powerful, balanced by tooling, reagent and skill. Different from the Rust Cathedral's remnant rebuilding (that rebuilt an item; this sacrifices one to recover parts). Pairs naturally with the hwelgrue's castings. |
| 2 | **The brullith that cannot lie down:** an enormous brullith with a swallowed loading-frame yoke grown through its chest; every time it lowers itself the wound reopens and spreads through its attendants by wound-sharing (your tamed hybrids too). Save it by treating the small patients first, then staged surgery whose incisions also enter the network. | 5 | free | L | A real third giant option and very much his style: a specific animal with a history, a medical crisis rather than a fight, built on the ratified brullith (art exists). Needs wound-sharing (row 0) and conserved damage. Offered on the card beside the wound-bearer and the gut that walks. |
| 3 | **The ship becomes a spore:** Sheen films gather under a long-landed ship, mature into reproductive pockets in the cargo bays; scrape early, replace infected deck later, abandon a compartment, or launch carrying a declared discharge of Sheen inside the ship after the next landing. | 6 | free | L | Same seed as BENCH's sheened hull (§4 row 2), with a sharper escalation (deck replacement) and a worse payload (Sheen discharged **inside** the ship). **Merged:** the hull row takes GPT's maturity stages and the deck-cost choice; the payload offered is BENCH's (a Rot patch seeded at the next landing), which reads as the jungle travelling rather than a trap, and is cheaper. |
| 4 | **A breath you can work inside:** a guardian grove's defence becomes audible: a long wet in-breath (gathering spores), cap clicks (imminent discharge), a hiss, then quiet (depleted); you time the brewing trip to the quiet. | 7 | free | S | Excellent, cheap, and it makes the built guardian groves legible. **Merged** into BENCH's mat's pulse (§4 row 3): the pulse is the network-wide alarm, the grove's breath is the local timer. Unique against Stillsand's and Nightside Ice's rumbles, the Greentide's silence cue and the Warscar's Geiger choir. |
| 5 | **The Bought Quarrel (Mob'Unloo):** found on a weighing slab at a digestion site; the clan publicly guarantees a living, unpaid trade claim between two parties and invites both to collect at its camp; armed delegations arrive with incompatible demands, and the clan's trading and security decide settlement or bloodshed. | 9 | campaign | L | Bold, dramatic, risky, Jawa to the bone, and it respects the rulings (cohesion only, odds only). It competes with §6 R1 for Mob'Unloo's **one** slot. It is less of this place (any counting-house could teach it) and needs a claim-tracking system that does not exist; R1 uses the Rot's own digestion and its built treasure conscience. Offered on the card as the second Mob'Unloo option. |

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. The binding rulings: **no god is evil**; **a rite gives cohesion, never a power**;
**favour shows only through events, world state and subtle odds**, voiced by the Narrator; a rite's
effect may be a dramatic, risky world event. Five-rite cap per god (raised from four 2026-10-02, card).

**Cap count, by hand from the register plus the 2026-10-02 ledger rulings** (found rites only; the
liturgy tab's B1 rows and the B5 devotions are not found rites). Starting from the Rust Cathedral
review's table and adding that sitting's turn-1 ruling (ledger, 2026-10-02 17:02Z):

| God | Found rites | Count |
|---|---|---|
| Ishko | Dark Vigil, Charged Reed, Stall-Hold, the Sinking | 4, one slot |
| Ohm | Engine Hour, Last Track, Deserter's Welcome, the Answering | 4, one slot (⚠ see below) |
| Oomo | Sunning, Chime Vigil, Filtered Cup, Unspilled March | 4, one slot |
| Mob'Unloo | Blind Offering, Storm's Receipt, Cold Ledger, the Sump's effigy Price | 4, one slot |
| Sh'kaar | Snuffing, Anvil Gift, Shade Tithe, Felled Noon | 4, one slot |
| Ozzik | Lightless Burial, Salted Keeping, Flawed Masterwork, the Ceded Room, the Open Boast | 5, at cap |
| Zizzik | five (cap waived for him at the Pyrelands sitting) | at cap |
| **Rekko** | Unfinished Laid Down, Inherited Wreck, Mud Claim, **the Mending Weld** (Rust Cathedral, ruled 2026-10-02) | 4, one slot |
| **Ta'Baa** | the Returned, Shadow Walk, Vindication Walk | 3, two slots |

⚠ **One rite ruled today has no god yet:** the Rust Cathedral's **droid-repair rite** (it pleases Ohm in
both endings, so it most likely lands on Ohm, taking his last slot); the card should not lean on Ohm's
slot. (The Sump's Rite A is the Sinking, Ishko's, counted above.)

**Not taken, and why:** a meditation or communion before the pale tree (the wild creed's, not the
Salvation's; and stillness is Ishko's); offering the teas to a god (ban 4: they cannot be carried to an
altar, and a cup offered on the spot is the Filtered Cup's shape); a burial in the warm mat (the
Lightless Burial and Salted Keeping already bury); letting the jungle take a room (the Greentide's Ceded
Room); anything that explains the war material the Rot composted (ban 7's spirit); a wound shared
between colonists as a rite (that would be a power, and spilled blood offends Oomo).

### R1. The Gut's Due, for Mob'Unloo: settlement, by paying the gut for what you sell (PITCHED)

- **Grounding:** Mob'Unloo is *"debt, trade, the sacred exchange"*; his ledger rises on settled debts
  and falls on unpaid obligations. The Rot already keeps a ledger of its own: selling Rot treasure gives
  a bad memory (`RM_RotTreasureConscience`, built), the sheet's *"treasure conscience"*. The Jawa are
  traders above all; a rite that **pays the place for what the clan takes out and sells** turns that
  unease into a deal, which is exactly Mob'Unloo's sacrament.
- **Found:** at a digestion site, a trader's pack frame grown through by the mat, its contents long
  digested, and beside it a neat stack of trade goods set on the warm ground, half eaten by the rot,
  with a tally scratched on a plate: one mark for each thing taken from the grove, one for each thing
  left.
- **Asks:** before (or after) selling something taken from the Rot, the participants lay goods **of
  equal market value** on the warm mat at a digestion site or on any fungal ground, and stand by while
  the rot clock takes them. The goods are really gone, eaten in a day. Anywhere off the Rot, the goods
  are laid on bare earth and must stay untouched until they rot or weather.
- **Risk (the point):** real wealth lost at a trader's price; on Rot ground the offering draws the
  hybrids that eat what lies down (and the hwelgrue, if built), so the participants guard it in the
  Sheen for hours, exposure ladder running.
- **Outcomes (cohesion only):** shared memories by quality; the treasure conscience's bad memory is
  settled for that sale (the debt paid, not a buff). Mob'Unloo's favour is told by the Narrator and shows
  only as his Exalted odds (*"better trade opportunities, favorable caravan timing"*).
- **Readable signs:** the offering visibly rotting on the mat, the tally plate, the letter.
- **Collision check:** the Sump's effigy Price throws a good thing and an effigy into tar to hold a
  faction off; Rite A throws one valuable into tar to erase claims; the Cold Ledger seals a gift in ice
  for a dead man's debt; the Storm's Receipt claims exhumed cargo. None **pays for a sale with equal
  value**, and none uses the place's own digestion as the witness. ⚠ It shares "valuables given up" with
  the two tar rites; the act (an equal-value payment watched while it rots) is the difference. Say so on
  the card.

### R2. The Unjoining, for Ta'Baa: feeding, by refusing to take root in your own body (PITCHED)

- **Grounding:** Ta'Baa is *"the refusal to root"*; his lever is *leave vs. entrench*. The Rot's
  Sheenblood symbiont is, in the sheet's words, *"how you join the biome instead of resisting it"*: a
  colonist who takes it has let the jungle root **in their body**. Giving that up before the clan leaves
  is the purest Ta'Baa act the planet offers.
- **Found:** on a Wildsteam pilgrim path in Hanging Wood, an empty brewing vessel overturned at a grove's
  edge, a rag stiff with dried Sheen, and footprints that stop shining halfway down the path.
- **Asks:** a colonist carrying a Rot symbiont (any of the four) is unjoined: the participants hold them
  through a hard purge (a vanilla-style sickness and pain for a day) and the symbiont dies. The rite is
  held within a few days of a planned departure; it counts more the more of the colony takes part.
- **Risk (the point):** the bargain's benefit is gone for good (Sheen immunity, fast healing, no sleep),
  the colonist is weak while it passes, and if the clan then does **not** leave within the season the
  memories sour (Ta'Baa's own clock).
- **Outcomes (cohesion only):** shared memories by quality. Ta'Baa's favour shows only as his Exalted
  odds (*"better landing sites, travel opportunities, a sense of momentum"*).
- **Readable signs:** the purge on the patient, the dead symbiont as an item (a grey husk), the letter.
- **Collision check:** the launch-rite is a launch; the Returned seals a body aboard; the Shadow and
  Vindication Walks are walks; the Left Behind devotion leaves working things. None **gives up a benefit
  rooted in a colonist's own body**.

### R3. Standing in the Sheen, for Oomo: feeding, by accepting the jungle's waters (PITCHED)

- **Grounding:** Oomo is god of water **and all the body's waters**, and *"the passing of waters
  between each other"* pleases him. The Sheen is literally the jungle's reproductive water, flung out to
  colonise. A rite that stands bare in it and accepts it is the place's strangest love-act.
- **Found:** a ring of standing stones on the Sheen line, every one glossed thick on its windward face,
  and the faint shapes of people pressed into the gloss where they stood.
- **Asks:** during a Sheen-fall (in the Rot) or any rain elsewhere, the participants stand in the open
  unprotected for an hour, faces up; no gear, no roof.
- **Risk (the point):** in the Rot the Sheen is disease-certain for the unadapted (the exposure ladder,
  built); elsewhere, a cold soaking. Real sickness, real downtime.
- **Outcomes (cohesion only):** shared memories by quality; Oomo's Exalted odds only (*"the desert
  provides"*).
- **Collision check:** the Sunning stands in red water under a Burn; the Unspilled March carries sealed
  jars; the Chime Vigil holds a ledge. ⚠ The Sunning is the nearest (exposure to a biome's water); the
  difference is the Sheen is the jungle's own living, reproductive water, accepted on the body. The
  weakest of the three; offered only if he wants Oomo.

GPT's rite idea, if any, is in §5 and is not repeated here.

## 7. Draft turn-1 card

Plain language, no def names in option labels, headers 12 characters or fewer, every question ends
in "?", and no option is a "none" (the card's own write-in line covers that). Above the card, read
him §0's description of the Rot, per the standing rule that he is never assumed to remember. Say in
one line above it that **both of last sittings' defects are present here** (ten creatures ruled into
the free mod on 2026-09-24 never moved, though their art is done; the fungal-soil trade is gated on a
retired donor biome and never fires), and that the Mod Settings screen is hollow.

**1. Build first** (header `Build first`) — *What should be built first for the Rot?*
- **Land what was already decided (recommended):** move the ten creatures you approved in September
  into the free mod, with their finished art, and rewrite the four that are plain animals as
  fungus-animal hybrids; make the wounded creatures really share wounds, as their descriptions promise;
  our own spore allergy; a settings screen whose switches work; fix the soil trade so it fires; take the
  Star Wars line off the free pale tree. Buys: the free Rot stands on its own creatures, and every
  promise in its text comes true. Costs: a medium batch with no new mark this round. *Why: it is most of
  this biome's value, the art already exists, and the giant and the sound lean on the shared wounds.*
- **Land it and add the giant together:** Buys: a visible giant of our own alongside the repair. Costs:
  a bigger first batch; giant art waits on the queue.
- **New ideas first, landing later:** Buys: new marks sooner. Costs: the creatures stay borrowed, and
  the wound-bearer giant has nothing to share wounds with.

**2. The giant** (header `The giant`) — *Which giant should the Rot get?*
- **The wound-bearer (recommended):** a hill of grey-lilac fungus over a long, coral-grown body, its
  hide covered in scars that are not its own. When any creature nearby is badly hurt, it takes part of
  the wound into itself and walks toward the pain; hunting here calls it to the kill. It never attacks
  first, but hurt it and the whole forest shares its wound and comes; kill it and every creature on the
  map bleeds at once. A hook: its oldest scars are blaster burns the ship recognises as its own guns'.
  Buys: the place's own law made into a giant, whose danger is your own violence. Costs: one large
  creature, its art, and wiring the wound-sharing first. *Why: it is the Rot's ruling made visible, and
  nothing on any other biome works like it.*
- **The gut that walks:** a huge, low decomposer with a dredge mouth that eats whatever lies down
  (carcasses, wrecks, a downed colonist) and digests everything but metal; it passes polished
  salvage, so the clan follows it like crows behind a plough. A hook: it swallowed a piece of an old
  ship and the gravship pings it on every landing. Buys: a giant that pays the scavenger clan. Costs:
  one large creature and its art; guarding the wounded becomes a chore.
- **The giant that cannot lie down:** one enormous brullith (the big gentle fungus-beast you already
  approved) with an old cargo yoke grown through its chest; every time it tries to rest the wound
  reopens and spreads to the small creatures around it, your tame ones too. Save it by treating them
  first, then careful surgery. Buys: a giant met as a patient, not a fight, using art that already
  exists. Costs: a large build (surgery that shares its cuts), and it needs the wound-sharing first.

**3. New marks** (header `New marks`) — *Which new ideas should be built (pick any)?*
- **The sheened hull:** a ship landed here slowly takes the jungle's sticky fog; pale mushrooms bloom on
  its seams. Scrape them off in the fog before you leave, or fly with them and they seed a small warm
  patch of the Rot wherever you land next. Buys: the place uses your ship to travel, which is what the
  fog is for. Costs: a medium build.
- **The ground's heartbeat:** the warm mat has a slow pulse you hear underfoot; it quickens when a
  guarded mushroom is roused, when creatures gather to share a wound, and before a spore cloud vents.
  Plus the hum, the wet settling and the hiss of falling fog. Buys: a voice that warns you. Costs: a
  small to medium build.
- **Unseaming:** learn from a fungus that eats everything but metal how to take a damaged weapon or
  machine apart into its working parts instead of melting it down; usable anywhere after. Buys: a
  scavenger's craft learned here, the thing the clan sells. Costs: a medium build (tools, reagent,
  skilled work).
- **All three (recommended):** Buys: ship, sound and technology marks in one sitting, none repeating
  another biome. Costs: one larger and two smaller builds. *Why: each fills a different missing mark,
  and with row 0 and a giant they bring the Rot to the full bar except the god.*

**4. Rite** (header `Rite`) — *Which rite should the Salvation find in the Rot?*
- **The Gut's Due, for the god of debt and trade (recommended):** before or after selling something
  taken from the Rot, the colony lays goods of equal value on the warm ground and guards them while the
  rot eats them in a day. Buys: a trader's rite only this place could teach, settling the unease of
  selling its treasure. Costs: a medium build; real wealth lost; guarding it in the fog. *Why: it ties
  the Rot to the clan's trading heart, and the rot itself is the witness.*
- **The Bought Quarrel, for the god of debt and trade:** the colony publicly guarantees an unpaid trade
  dispute between two living parties and invites both to collect at its camp; armed delegations arrive
  wanting incompatible things, and your dealing decides settlement or bloodshed. Buys: a dramatic,
  risky trader's rite. Costs: a large build (tracking claims); less tied to this place.
- **The Unjoining, for the god of flight:** a colonist who let the jungle into their body (a symbiont)
  is held through a hard purge until it dies, just before the clan leaves. Buys: a real sacrifice of
  belonging, in the one place you can join. Costs: a medium build; the benefit is gone for good; if the
  clan stays, it sours.

Held off the card (in the doc only): §6 R3, Standing in the Sheen for Oomo (the weakest; close to the
Sunning), and BENCH's wound-tie (it would repeat the yssomar's root).

## 8. Turn 1 rulings (2026-10-02) and ticket-out

Items 1 and 4 decision taken by question card 2026-10-02 10:20 PDT. Item 2 the owner answered in typed words
(ledger `ROT_SCORING_SITTING_1`, seat OWNER, 17:44 UTC). Item 3's three ideas he turned down in typed words the
same minute; six new ideas were pitched in `design/Jawa/worldbuilding/biomes/rot_new_marks_redo_2026-10-02.md`
and ruled by question card 2026-10-02 10:50 PDT, with a typed extension (OWNER, 17:56 UTC). His typed words are
quoted verbatim below.

| Card item | Ruling | Ticket |
|---|---|---|
| 1. Build first | **Land what was already decided, and add the giant together.** Decision taken by question card. Row 0 in full: the ten creatures ruled into the free mod on 2026-09-24 (art done, MEASURED in the artpipe `done/` for all seven sets incl. `rot_fungalweevil_v2_*` for the grellik) move from `RSW_` campaign patch rows into `RM_` defs in the free mod, the thozzik, illoth and brogg rewritten as fungus-animal hybrids and the brullith's lab origin deleted (ban 7); real wound-sharing on the five creatures whose descriptions promise it (chittik, gromma, rennok: wound-link; mullgoth, durrok: kin-mending); our own spore allergy; a settings screen whose every control works; the fungal-soil trade regated from `AB_MycoticJungle` to `RM_TheRot`; the Force taken off the free pale tree (the campaign patches it back). "Land what was already decided" alone and "new ideas first" are **NOT CHOSEN**. | `ROT_RM_CAST_MIGRATION_1`, `ROT_WOUND_SHARING_WIRING_1`, `ROT_SPORE_ALLERGY_PORT_1`, `ROT_MOD_SETTINGS_WIRING_1`, `ROT_TIER_LEAKS_FIX_1` |
| 2. The giant | Owner, typed: *"(2) is AWESOME. Like a huge maggot slow maggot covered in small wriggling tentacles and eye spots, I love the old ship that's pinging from within begging the players to figure out how to kill it."* = **the gut that walks**, named **the hwelgrue** (`RM_Hwelgrue`; collision-checked §3, re-checked 2026-10-02: 0 artpipe hits). Its body is his: a huge slow maggot, small wriggling (fungal) tendrils, eye spots; it eats whatever lies down, digests all but metal and passes polished salvage; the gravship pings the swallowed piece on every landing. The wound-bearer (the yssomar) and the giant that cannot lie down are **NOT CHOSEN**; no yssomar is built. | `ROT_HWELGRUE_GIANT_BUILD_1` |
| 3. New marks | Owner, typed, on the sheened hull, the ground's heartbeat and Unseaming: *"none of these hit the mark"*; all three **NOT CHOSEN** (and "all three"). Redo, by question card: **ship = the Swallowed Navigator** (the pinging core feeds the console a dead ship's log revealing salvage sites; killing the gut ends the log), extended by the owner, typed: *"(1) but more. The thing inside would also be a significant upgrade to your ship if extracted. But you can't use ship weapons on the giant without harming it, making the fight much harder. Would upgrade your range, as it was part of a drive system of an older ship."* (range is Odyssey's `GravshipRange` stat, offset by facilities like the thrusters: MEASURED in RimSage, see the item); **sound = Still Alive In There** (the gut swallows downed pawns; muffled knocking says who is inside and how long they have; cut them out in time; modelled on Anomaly's `CompDevourer`, MEASURED, not attached as-is); **technology = BOTH the Gut-Mother** (a sac cut from the dead gut grows a vat anywhere that gives back implants and gear from corpses; starter cultures are a trade good) **and the Unjoining Draught** (learned from the rite: a brutal purge driving out parasites, symbionts and Anomaly metalhorrors, anywhere). 🔴 **Ruled exception to ban 4:** the Gut-Mother was chosen with the card's stated condition that **a gut-mother culture may leave the Rot**; it is neither a tea nor a symbiont, and the ban is otherwise unchanged. The Rot Won't Let Them Go (S2) and the Joined Ear (O2) are **NOT CHOSEN**. | `ROT_SWALLOWED_NAVIGATOR_1`, `ROT_STILL_ALIVE_SWALLOW_1`, `ROT_GUT_MOTHER_VAT_1`, `ROT_UNJOINING_DRAUGHT_1` |
| 4. Rite | **The Unjoining, for Ta'Baa** (§6 R2), decision taken by question card: a symbiont-joined colonist held through a hard purge until the symbiont dies, just before the clan leaves. Ta'Baa is *"the Unrooted — flight, the refusal to root"* (`divine_satiation_engine.md` ⑥), confirmed. Added to the register as B13 (`design/Jawa/salvation_rites_2026-10-01.md`). Cap check (five per god): **Ta'Baa four** (the Returned, the Shadow Walk, the Vindication Walk, the Unjoining), one under the cap. The Gut's Due and the Bought Quarrel (Mob'Unloo) are **NOT CHOSEN**; Standing in the Sheen (§6 R3) and BENCH's wound-tie were held off the card and stay unticketed. | `ROT_UNJOINING_RITE_1` |

FOUNDRY items, each `--caused-by ROT_SCORING_SITTING_1`:

| slate row | item |
|---:|---|
| 0 | `ROT_RM_CAST_MIGRATION_1` (ten `RM_` defs, hybrid descriptions, illoth flight, `RSW_` rows retired) |
| 0 | `ROT_WOUND_SHARING_WIRING_1` (wound-link and kin-mending on five donor bodies; the *Health sharing* toggle) |
| 0 | `ROT_SPORE_ALLERGY_PORT_1` |
| 0 | `ROT_MOD_SETTINGS_WIRING_1` |
| 0 | `ROT_TIER_LEAKS_FIX_1` (FungalSoilTrade regate; pale-tree text) |
| 1 | `ROT_HWELGRUE_GIANT_BUILD_1` |
| 2 (redo) | `ROT_SWALLOWED_NAVIGATOR_1` |
| 3 (redo) | `ROT_STILL_ALIVE_SWALLOW_1` |
| 4 (redo) | `ROT_GUT_MOTHER_VAT_1`; `ROT_UNJOINING_DRAUGHT_1` |
| 5 | `ROT_UNJOINING_RITE_1` |
| 6 | art: `infrastructure/artpipe/art_lists/rot_turn1_2026-10-02.csv` (10 subjects, 14 jobs: the hwelgrue, the casting, the drive core and its ruined form, the sac, the vat, the starter, the draught, the husk, the rite's vessel). The ten ports need **no** new art; their existing thozzik, illoth and brogg renders show plain animals, and whether to redraw them as hybrids is open for the owner. |

Sequencing: row 0 first (`THE_ROT_FIRST_SCRIPT_1` is written against row 0's state); the hwelgrue before its
three dependants (navigator, swallow, gut-mother); the draught before the rite. The Rot is **not** an
extreme-heat biome; no heat-kind declaration is owed.

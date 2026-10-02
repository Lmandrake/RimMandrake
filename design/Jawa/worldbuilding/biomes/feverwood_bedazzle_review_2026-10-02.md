# The Fever Wood: bedazzle review (grandfathered sitting, turn 1 ruled)

Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 9. Item to be filed by the
parent (`FEVERWOOD_SCORING_SITTING_1` shape).

_BENCH design pass, 2026-10-02. Ninth sitting of the grandfathered track, in the order of
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Fever Wood; sitting order row 9). The sheet
`the_fever_wood.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07); its ban 1 was superseded at the
2026-09-23 sitting (`fever_wood_deep_and_mud_2026-09-23.md` §0: the thing below is ambient and named).
Already ruled and **not re-argued here**: the sekkulaath and its six limbs, the drive-off ladder and the
radioactive suppressant, the porter's loot and its anger, the prison tank and the escapee, the
plot-reserved full emergence, the four sap-suckers and their refusals, the thornbug's calm-gated deal,
the four birds and the emergent chorus, the two-front war and the lure stake, the reactive ant hives,
ground refusal and the boughways, bough-soil, the 2026-09-24 cast sitting (5 new names, 3 renames, the
skreth as the free face of the Webwork brood, the gorrameth's doomed-herd incident), and the dianoga
ruling (*"It belongs only in tank prisons and the Fever Wood"*, 2026-09-23). The seven hard bans of sheet
§6 bind every slate row; the ones that bite hardest: **no native chase predators** (3), **no heavy
structures on the ground** (4), **no flowing water, no rain** (5), **thornbugs never yield under fear**
(6), **no Earth flora or fauna** (7)._

Sources read, all in the BENCH clone: `src/RimMandrake/FeverWood/` (BiomeDef
`Defs/BiomeDefs/RM_FeverWood.xml`, every def folder, `About.xml`, all 31 `Source/*.cs` by grep and the
settings, two-front-lure, tentacle-watch and sap-sucker files read), the frozen twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_FeverWood.xml`, the cast patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_FeverWood.xml` (every op's xpath resolved), every other
file under `src/` naming the biome or its donor `COMIGO_GreaterSwamp_Tropical` (`BiomeDescriptions_Ashkarr`,
`BiomeNames_Ashkarr`, `AncientDangerGenSteps_AmbientDoctrine`, `FishTypesStrip_NoFishBiomes`,
`PlantGrowthConfig.cs`, the EnvironmentalHazards haul/stun/kidnap sources, `RSW_Shokk_FeraliskBrood.xml`),
`RSW_SekkulaathTank_DianogaSwap.xml`, `RSW_BiomesTeamPort_Races.xml`, the sheet, the deep-and-mud
sitting, both 2026-09-23 rosters, the cast proposal and its rulings, the syllable pass, the open Fever Wood
items, the register `design/Jawa/salvation_rites_2026-10-01.md`, the ledger's 2026-10-02 rulings (Webwork,
Greentide, Rust Cathedral, the Rot and its new-marks redo), and the Rot review for shape. Rosters were
parsed as XML elements; the creature census reads descriptions.

## 0. The Fever Wood in plain words (for the card)

The Fever Wood is where the trees finally won. Behind the delta swamp, trunks wider than houses rooted
the wet ground still; their limbs grew together into roads of living wood high above shallow, perfectly
black pools that never ripple. Life, trade and safety are up in the crown: insects that give sweet nectar
only while they feel safe, an amber bug that sets into armour, a sac that swells until it cannot be
pulled off, alien birds whose calling means the water is quiet, and the Wildsteam's treetop town of
Sporefall. Below is the thing nobody swims with: the sekkulaath, a monster too big to ever see whole,
which reaches up out of the pools with six kinds of tentacle, sets the gear of the people it took at the
water's edge as bait, and can only be driven off. Ants raid from one side and the Webwork's spiders from
the other, and the oldest trick here is to let them meet. It is hot, windless and dry above (no rain,
ever), the marsh refuses heavy buildings, and oil seeps up out of the mud. It has nothing to do with the
ship, ordinary weather, nothing learned here that travels, and no god at all.

## 1. What is there: ruled vs built

### A deep free kit, with half its ratified cast never built

`src/RimMandrake/FeverWood/` (`mandrake.rm.feverwood`, `FEVERWOOD_RM_MOD_BUILD_1`) ships: its own biome
worker; the sekkulaath's six limbs (`RM_Sekkulaath_Feeler/Snare/Lash/Porter/Sentinel/Bloom`, driven by
`RM_MapComponent_TentacleWatch`) with loot, porter anger and the great-emergence gate; the drive-off by
fouling a pool (`RM_RadioactiveSuppressant`, designator, work giver, job); the prison tank
(`RM_SekkulaathTank`, `RM_Sekkulaath_Juvenile`, escape and captivity memory); the lure stake and the
two-front raid (`RM_MapComponent_TwoFrontLure`); the reactive ant-hive dungeon (`RM_GenStep_AntHiveDungeon`,
`RM_MapComponent_AntHive`, `RM_Kurreth`, the hidden `RM_FactionDef_KurrethSwarm`); the four sap-suckers
with their refusals (`RM_CompSapSuckerRefusal`, the Harmony mishandle patch) and their products; four
flying birds; 19 invented plants on bough-soil; the mirror pools, mirror-break incident, ground refusal,
boughways, stilt platforms and the trunk core and heartwood. The shared hazards (mirror pools, causeways,
ground refusal, the calm-gated thornbug, the living bole) ride `mandrake.rm.environmentalhazards`. The
campaign layer adds the canon cast patch, the dianoga swap, the feralisk brood faction
(`mandrake.rsw.shokk`) and the donor-def label and description patches.

### 🔴 The systemic defects of the last sittings: checked, and the Fever Wood carries a lighter set

- **(a) Invented content stranded in the campaign tier: YES, three creatures, smaller than the Rot's
  ten.** The campaign patch `WildAnimals_FeverWood.xml` casts `RSW_GlowSlug` 0.5, `RSW_JewelBeetle` 0.2
  and `RSW_AcidSlug` 0.05. None is Star Wars: all three are Biomes! Team ports
  (`RSW_BiomesTeamPort_Races.xml`, the same donor as the Rot's ten), so under Q11a they are invented, not
  IP, and belong in the free tier or nowhere. Their own descriptions place them somewhere else (*"a
  pale-blue slug of the deep voids"*, *"native to the desert shallows"*, *"one of the most dangerous
  predators in the earthen depths… originally designed for combat"*), and all three are also cast in the
  Webwork and the Lantern Deeps. The 2026-09-24 cast sitting already filled their free-tier holes with
  ratified names (the grolth takes the acid slug's slot), so nothing here is lost when they are judged;
  they are **rows for this sitting's review, never an eviction** (the multi-homing ruling of 2026-09-22).
  The other seven campaign rows (urusai, nuna, gelagrub, convor, longtail gorg, whisperbird, fambaa) and
  the hydenock, jogan and chak-root are genuine canon, correctly campaign-side.
- **(b) Campaign patches replacing an `RM_` list, or campaign mechanics gated on the twin or a donor: the
  cast is clean, and three campaign patches still point only at the donor.** All three ops of
  `WildAnimals_FeverWood.xml` are `PatchOperationConditional` → `PatchOperationAdd` onto
  `RM_FeverWood/wildAnimals` and `/wildPlants`; nothing is replaced. No C# mechanic gates on `RUT_FeverWood`
  or the donor: every hazard extension rides the `RM_` def, and `PlantGrowthConfig.cs` lists both
  names. But four campaign patches target **only** `COMIGO_GreaterSwamp_Tropical`, the donor: the Ashkarr
  label (`BiomeNames_Ashkarr.xml`), the Ashkarr description (`BiomeDescriptions_Ashkarr.xml`), the ancient
  danger DENY (`AncientDangerGenSteps_AmbientDoctrine.xml`) and the no-fish strip
  (`FishTypesStrip_NoFishBiomes.xml`, on the abstract parent). The `RM_` def has its own label and
  description, so the first two cost only the campaign's wording; the **ancient-danger DENY is the one
  that changes play**: `RM_FeverWood` carries no `preventGenSteps`, so after the final paint ancient
  dangers will generate in the Fever Wood that today's donor-painted tiles refuse (UNMEASURED live; read
  from source). Same family as the Rot's soil trade, smaller. ⚠ All three cast ops (and both ops of the
  dianoga swap) carry the top-level `<Operation … MayRequire=…>` guard the engine ignores
  (`PATCH_MAYREQUIRE_GUARD_INERT_1`); harmless while the bestiary is always loaded, listed for that sweep.
- **The reverse slip, IP in the free tier: YES, three sentences.** The free `RM_` limbs' descriptions name
  canon outright: the snare (*"canon dianoga tentacles are suckered"*), the lash (*"the giant form's own
  tentacles are barbed, canon-confirmed"*) and the sentinel (*"Canon dianoga have excellent hearing"*).
  The free text should describe the sekkulaath; the campaign patches the dianoga in.
- **A tier-grammar slip the scores doc's list missed:** the free mod ships **ten `RUT_`-prefixed defs**
  (`RUT_FeverWoodMirrorPool`, `RUT_Boughway`, `RUT_BoughSoil`, `RUT_StiltPlatform`, `RUT_FeverTrunkCore`,
  `RUT_FeverTrunkHeartwood`, `RUT_FeverWood_MirrorBreak`, `RUT_FeverWood_MirrorList`,
  `RUT_GenStep_GroundRefusal`, `RUT_GenStep_ScatterPools`). The scores doc named the Sump, Miasma, Rust
  Cathedral and Lantern Deeps for this and not the Fever Wood; it belongs on `BIOME_TIER_CLEANUP_1`. A
  rename of placed terrain is a save question, so it is listed, not slated.

### Fauna, merged (inline + patch-added), read as XML elements, census by description

**Free tier, `RM_FeverWood/wildAnimals` (9 rows, `animalDensity 2.3`):** thornbug 0.6 (*"yields only
while it feels safe"*), vaulm 0.3 (*"floods its own shell and sets: armour, not flesh"*), ollareth 0.3
(*"it screams, and the whole crown answers"*), drommath 0.3 (*"handled, it swells rather than yield"*),
chellow 0.5 (flies; *"as long as they are calling, the water below is quiet"*), murrelith 0.35 (flies;
ribbon plumes, *"sell the plumage and you have sold part of your own early warning"*), thavrik 0.3
(flies; *"a furred thing that flies"*), skellick 0.25 (flies; the thief), and `VFEI2_Megathrips` 0.5
(donor wood-borer, `MayRequire` on the element; Q9 allows it). Off-roster by design: the kurreth (raider
and hive only) and the sekkulaath (limbs, tank juvenile). Every owned creature is alien in body and
colour; none is Earth-like. The flyers fly (`MaxFlightTime` 6–10).

**Campaign patch-adds to `RM_FeverWood` (10 animal + 3 plant rows, `PatchOperationAdd`):** the seven canon
ports and the three Biomes! Team ports above; hydenock 1.5, jogan 0.6, chak-root 0.4.

**Flora:** 19 invented rows, the thulvane and skethral towers through the margin plants. Not a gap.

**Findings in the cast:**
- **Seven ratified creatures were never built.** The 2026-09-24 card ratified the whole cast. Of it,
  `RM_Lommerel` (the under-bough grazer), `RM_Silloch` (the bark-coloured wait-ambusher), `RM_Brathek`
  (the borer that keeps digging), `RM_Gorrameth` (the terribly lost), `RM_Grolth` (the carrion-dissolver),
  `RM_Nemmel` (the ground grazer) and `RM_Skreth` (the Webwork brood's free face) exist nowhere in `src/`
  (searched by defName). So the free ground level has **no animal at all**, the crown has no grazer and no
  ambusher, the "crown keeps changing" borer (§6q) is only the donor megathrips, and the free tier's
  "terribly lost" (the pools' visible victims, sheet §4) is absent.
- **The free two-front war has one front.** The ruling said the war is *"identical in both tiers"*, with
  the skreth as the free brood. `RM_MapComponent_TwoFrontLure` names `RSW_Shokk_FeraliskBrood` as the
  second front and, when it is absent, quietly falls back to ants (its own comment says so). Without the
  skreth the free player never sees the sheet's central dynamic.
- **The ants do not steal.** Sheet §4: *"Ant raids haul thornbugs away ALIVE: theft, not slaughter… so
  every loss is a recoverable quest: track the column, raid it back."* The parts exist in
  EnvironmentalHazards (`RM_HaulVictimAIUtility`, `RM_JobDriver_StunVictim`, `RUT_HaulPawnAndExit`), but
  the utility's own header says the LordJob that would call them was not built, and the lure raid runs
  `LordJob_AssaultColony(…, canKidnap: false, …, canSteal: false)`. No raid-back quest exists.
- **The dianoga is only half mapped.** *"Map it to the Dianoga when Utinni is active"* (owner,
  2026-09-23). `RSW_SekkulaathTank_DianogaSwap.xml` swaps the **tank** occupant to `RSW_Dianoga`
  (FEVERWOOD_DIANOGA_PRISON_1, built). Nothing maps the **giant**: the six limbs keep their sekkulaath
  labels and texts in the campaign. The dianoga **is** wired to the Fever Wood's tank, and is correctly
  absent from every wild roster (the Greentide row was removed on the ruling).
- **Multi-homed species:** the three Biomes! ports (above) and the canon urusai and fambaa (also cast
  elsewhere) are listed only, never evicted.

### Heat

The Fever Wood **is** an extreme-heat biome (sheet §0: median 45.5 °C, 42.0 p10 to 51.5 max), and
`RM_FeverWood` declares **no heat kind** (`RM_SunHeatExtension` is absent from its def, where the
Greentide, Stillsand, Long Shade, Forge and Flooded Canyon carry it). The one-heat law requires one.
BENCH's read of the sheet is **ambient**: a windless, closed crown over standing water, where shade is
already everywhere and does nothing (overhead sun in the open crown tops is the alternative reading). It
uses vanilla temperature only.

### Ruled mechanics, built and unbuilt

- **Built (free):** the sekkulaath's six limbs, loot, porter anger, drive-off ladder and suppressant; the
  prison tank and escape; the lure stake and two-front raid (one front, above); the reactive ant hives;
  the sap-sucker refusals; the calm-gated thornbug; the birds (flying); bough-soil and the crown flora;
  mirror pools, mirror break, ground refusal, boughways, stilts, the living bole.
- **Built but hollow (free):** **the silence has nothing to silence.** The sentinel hushes
  `map.Biome.soundsAmbient` through `RM_MapComponent_SilenceCue` (`RM_FeverWoodBirds.xml`'s header says
  the chorus *is* that ambient list), but neither `RM_FeverWood` nor the twin declares any
  `soundsAmbient`. So the ruled warning (*"that silence is the loudest warning"*) cuts a sound that never
  plays; the scores doc's "built" HIT on mark 7 reads the wiring, not the ears.
- **Mod Settings:** all 25 fields of `RM_FeverWoodSettings` are read by the code they claim to gate
  (each field grepped to its reader). Clean, unlike the Rot.
- **Ruled, unbuilt (free):** the seven creatures; the gorrameth's doomed-herd incident (a later wave by
  ruling); ant theft and the raid-back; the heat kind; the crown sound itself (sheet §9: *"the crown hums
  with work (taps, herds, boardwalk steps, steam); the ground is the quietest wet place on the planet"*).
- **Ruled, unbuilt (campaign):** the dianoga over the giant; Sporefall as a treetop town and its pool list
  (sheet §8); the herd-groves.
- **Unruled marks:** a ship touch (6), weather (8), a god and a rite (9); a learned technology that
  travels (2).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `RM_MapComponent_TentacleWatch` (noise, sentinel count, porter anger, great-emergence pressure) and
  `RM_CompTentacleLimb`: anything that reacts to noise near a pool, or to the ship's noise, reads these.
- `RM_MapComponent_SilenceCue` (`BeginSustainedHush`/`EndSustainedHush`): a sound that falls silent is
  wiring, once there is a sound.
- `RM_HaulVictimAIUtility`, `RM_JobDriver_StunVictim`, `RUT_HaulPawnAndExit`: the theft is a LordJob away.
- `RM_CompCapturedSpecimen` / `RM_CompEscapedCaptive`: anything about the deep's young reads the tank.
- `RM_GroundRefusalBiomeExtension`: a ship that lands on refusing ground reads the same refusal.
- `RM_GenStep_RootCauseways` with `additionalPasses`: a grown structure is a second paint pass.
- `RM_CompGatherableCalmGated`: calm as an economy already exists.
- The Rites tab's found-rites row and `RUT_ResearchMod_GrantRite` (register §d).

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against the
sheet, the 2026-09-23/24 rulings and the source. No mark moves; one "built" claim is corrected (mark 7).

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | mirror pools, the porter's bait, ground refusal, the lure stake, the reactive ant hives: all free | the two-front war has one front in the free tier; the ants do not steal |
| 2 | Discoverable technology | PARTIAL | PARTIAL | the prison tank (husbandry), the suppressant (a recipe); no research project | nothing learned here is kept or travels |
| 3 | Unique resources | **HIT** | **HIT** | nectar, vaulm lacquer, drommath sap, murrelith plumage, sekkulaath products, ossagrel sap, seep oil, clay | |
| 4 | Surprising creatures | **HIT** | **HIT** | 8 owned free creatures + the kurreth and the sekkulaath; 7 ratified creatures unbuilt | three invented Biomes! ports ride the campaign patch (Q11a) |
| 5 | GIANT beast | **HIT** | **HIT** | the sekkulaath, six limbs and the eye: free | the campaign's dianoga covers the tank, not the giant |
| 6 | Gravship touch | MISS | MISS | 0 | |
| 7 | Soundscape | **HIT** | **HIT** | the silence cue is wired; **no ambient sound is declared**, so it silences nothing | ruled (sheet §9, §6k); hollow today |
| 8 | Interesting weather | MISS | MISS | `Clear` 30, `Fog` 10, `Overcast` 2, `DryThunderstorm` 1: all vanilla | no rain is a ban; nothing else is the Fever Wood's own sky |
| 9 | Relationship to the gods | MISS | MISS | 0 | no god, precept, shrine or rite in the sheet, the free mod or the campaign layer |

**Free 5 HIT / 1 PARTIAL / 3 MISS. Campaign 5 HIT / 1 PARTIAL / 3 MISS.** The same as the scores doc.
Unlike the Rot, the Fever Wood's top problem is **missing marks**, not missing landings: the ship, the
sky and the gods are blank, and nothing learned here travels. The landing debt is real but smaller: seven
creatures (one of them the free tier's second front), the ants' theft, the dianoga over the giant, a sound
to silence, a heat kind and three IP sentences.

**Rite: none.** The scores doc's seed (*"an offering rite at the pool's edge (feeding, Ishko or Rekko)"*)
is read below: an offering into water is Oomo's taken shape (offering water), and Rekko's salvage-returned
shape is crowded (the Inherited Wreck, the Mud Claim, the Stranger's Overhaul). §6 instead pitches from
the place's own oldest trick and its pools.

## 3. Roster fill

### The gaps, read from the sheet's sorts (§4, §7b) and the ruled roster only

Ban 3 shapes every fill: natives wait or graze; only the two raiders bring pursuit. **Every hole the
sheet opens already has a ratified name**; this sitting coins no new creature.

| sort (sheet §4, deep-and-mud §6) | free tier today | campaign today | fill |
|---|---|---|---|
| Sap-drinker guild (four refusals) | thornbug, vaulm, ollareth, drommath | same | none: built |
| The four birds (the chorus) | chellow, murrelith, thavrik, skellick, all flying | + urusai, convor, whisperbird | **give the chorus a sound** (§1 heat-and-hollow) |
| Crown grazer slung under the boughs | none | gelagrub (canon) | **build `RM_Lommerel`** (ruled 2026-09-24) |
| Crown wait-ambusher | none | longtail gorg (canon) | **build `RM_Silloch`** (ruled) |
| The borer that keeps digging (§6q) | megathrips (donor) | same | **build `RM_Brathek`** (ruled) |
| Ground grazer, the floor's one honest meal | none | nuna (canon) | **build `RM_Nemmel`** (ruled) |
| Ground-slow carrion-dissolver | none | acid slug (Biomes! port, wrong home) | **build `RM_Grolth`** (ruled) |
| The terribly lost (the pools' visible victims) | none | fambaa 0.02 (canon) | **build `RM_Gorrameth`** (ruled), its doomed-herd incident later (ruled) |
| Raider, the dry front | kurreth (built, does not steal) | same | **wire the theft and the raid-back** (ruled) |
| Raider, the Webwork front | none (falls back to ants) | feralisk brood (`mandrake.rsw.shokk`) | **build `RM_Skreth`** as the free brood (ruled "identical in both tiers") |
| The thing below | the sekkulaath | the sekkulaath, dianoga only in the tank | **map the dianoga over the six limbs** in the campaign (ruled) |
| Invented ports in the campaign tier | n/a | glow slug, jewel beetle, acid slug | **owner's call on this sheet** (card Q1's recommended option judges them out of the Fever Wood campaign roster, since the ratified free cast fills each slot and their texts describe other places; they stay in the Webwork and the Lantern Deeps untouched) |

Names follow this biome's ruled register (§6o: *-eth/-ith/-ock/-el* endings, doubled *ll/mm/rr*) and were
collision-proven at the 2026-09-24 sitting (`check_pseudo_sw_name.py` 5/5, `src/` sweep zero, Wookieepedia
zero with a `dewback` control). No new name is needed. Every creature is one home, free tier, alien in
colour.

**The giant needs no new body**: the sekkulaath is built and is the best-realised giant of the twelve. The
card asks instead **which story it carries**, because he rewrites giants into a specific creature with a
plot hook (the Rot's gut that walks with an old ship pinging inside; the Rust Cathedral's borehulk and the
Worn Bit). Three stories, each tying the deep to the ship, the gods or the trade:

- **The Brood Ransom** (BENCH; recommended). The tank juveniles that every town keeps are the
  sekkulaath's own young, and it knows. Each juvenile held in a tank anywhere on the planet is felt in the
  pools: the porter's gifts thin and the snares grow bolder the more of its young the world holds. Release
  a juvenile into a Fever Wood pool (bought, stolen or bred in your own tank) and the porter sets down one
  great gift at that pool's edge: not a dead stranger's gear but something old and heavy from the very
  bottom (an ancient ship component, an archotech fragment, a sealed crate). **The plot hook:** Sporefall's
  famous display tank, the one that teaches newcomers *"the lore at last"*, holds the largest juvenile ever
  caught, and the Wildsteam's quiet canton depends on keeping it: freeing it would buy the clan a gift from
  the deep and break the treetop town's peace. Jawa trade tie: juveniles become a black-market good the
  clan can buy from prison towns and "return" for salvage, and the Narrator says what the deep thinks of
  traders in its children. **Reuses:** `RM_CompCapturedSpecimen`, `RM_CompEscapedCaptive`, the porter's
  loot table, `RM_MapComponent_TentacleWatch` pressure; a world-scope tally of held juveniles is new (S–M).
  Not a neighbour's giant: the Rot's gut is a treasure map you kill; the borehulk is a machine you mend;
  this is a monster you **bargain with by returning its children**.
- **The Lost Crawler** (BENCH). Over a long stay, the porter's gifts are not random: pieces of one old
  Jawa sandcrawler keep turning up, each crew tag scratched with a family mark the Narrator recognises as
  the clan's own (a crawler lost generations ago crossing the delta). Collect enough pieces and the
  crawler's whereabouts are clear: it lies in the mud under the largest pool, and its clan plate comes up
  only if the bloom is forced open and the eye driven down. **The plot hook:** the clan elders want the
  plate back for the founding shrine, so the biome becomes the clan's own lost history. ⚠ Shares "an old
  vehicle inside a giant" with the Rot's swallowed navigator, ruled today; offered, not recommended.
- **The Wildsteam Drum** (BENCH). Sporefall keeps a drum made of a dead limb's hide; struck at a pool, it
  calls the whole animal up once, the plot-reserved full emergence spent by the player as a weapon on a
  raid between two gates. **The plot hook:** the Wildsteam will lend it only to a clan that has earned it,
  and once it is struck the deep is awake on that map for a season. ⚠ This spends the plot reserve the
  sheet keeps for the plot; his call alone.

## 4. The slate

Proposed for owner turn 1. Row 0 executes existing rulings (the 2026-09-24 cast card, the 2026-09-23
dianoga ruling, sheet §4's theft and §9's sound, the one-heat law, the tier grammar); rows 1 onward need
his word. Nothing here touches tiles; nothing builds heavy on the ground (ban 4); nothing makes it rain
(ban 5).

**0. Land what was already ruled (free tier, plus three campaign strings).** In `mandrake.rm.feverwood`:
- **The seven creatures:** `RM_Lommerel`, `RM_Silloch`, `RM_Brathek`, `RM_Nemmel`, `RM_Grolth`,
  `RM_Gorrameth` (rows inline on `RM_FeverWood` at the ruled commonalities) and `RM_Skreth` (off-roster,
  the free second front: a hidden brood faction beside `RM_FactionDef_KurrethSwarm`, which
  `RM_MapComponent_TwoFrontLure` falls back to when the Shokk brood is absent). Art: check the artpipe
  first (`artpipe_state.py find`), generate only what is missing.
- **The ants steal:** a LordJob that stuns a thornbug (or a tamed sap-sucker) and hauls it off alive with
  `RM_HaulVictimAIUtility` + `RM_JobDriver_StunVictim` + `RUT_HaulPawnAndExit`, a letter naming what was
  taken, a readable track to the column, and a raid-back (the stolen animal recoverable at the column's
  camp or at the hive dungeon). No silent vanishing.
- **The crown's sound:** declare `soundsAmbient` on `RM_FeverWood` (sheet §9: taps, herd noise, boardwalk
  steps, steam, and the four birds' calls), so the sentinel's hush has something to cut.
- **The heat kind:** `RM_SunHeatExtension` on `RM_FeverWood`, **ambient** (BENCH's read; card Q1 says so).
- **Free text without canon:** rewrite the snare, lash and sentinel lines about the sekkulaath itself.
- **Campaign:** a dianoga mapping over the six limbs (labels and descriptions, the canon facts the free
  text drops); retarget the ancient-danger DENY and the Ashkarr label/description patches to `RM_FeverWood`
  as well as the donor; the three Biomes! ports per his card answer.
Size M (the names and rulings exist; the theft is the only real C#).

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The giant's story** (§3): the Brood Ransom, the Lost Crawler or the Wildsteam Drum. | 5 | the tank comps, the porter's loot, tentacle-watch pressure | S to M |
| 2 | **The Mooring** (BENCH, ship): the gravship is the heaviest, loudest thing that ever came to the Fever Wood. The marsh refuses it (ground refusal: a ship on mud lists and mires a few hull cells a day), and the landing's noise is heard below: the nearest pool's sentinel rises and, if the ship stays, a snare wraps a hull edge and holds. Launch while moored and the wrapped section tears off into the pool (the porter sets its pieces down at the margin weeks later); or drive the deep off first with the ladder, or pay Sporefall's toll to land on a trunk-top pad, out of reach and rented (GPT's §5 idea 2 sharpens this: the only strong pad may mean cutting a living road the herd-groves use). The biome acts on the ship in its own two voices: the ground that refuses and the thing that hears. | 6 | `RM_GroundRefusalBiomeExtension`, `RM_MapComponent_TentacleWatch` (noise), the snare limb, the porter's loot | M |
| 3 | **The Seep Boil** (BENCH, weather): on the hottest still days the seep-oils boil up faster and the ground level fills with a low rainbow-sheened oil haze (a WeatherDef plus a GameCondition, no rain). Seep-oil gathering doubles while it lasts; but the haze is fuel: any spark at ground level (gunfire, a torch, a cooking fire, lightning from the dry storm) flashes a fire along the haze, and a burning pool margin wakes the deep. A harvest window you work in silence and without guns. | 8 | seep-oil plant, vanilla fire, tentacle-watch noise | M |
| 4 | **The pressure wedge** (§5 idea 1, GPT): a cartridge of seep-oil and vaulm lacquer, learned from the drommath's swelling, that slowly cracks open a wall, door or rock face without a blast; usable anywhere, a trade good. **BENCH's alternative, bough-grafting:** learned from how the trunks knit their limbs into roads, grow a living-wood bridge or platform from any tree across water, marsh or a chasm, anywhere; slow, needs a living tree at each end, burns, but needs no foundation. | 2 | the drommath's swell refusal, seep-oil and lacquer products (wedge); `RM_GenStep_RootCauseways` pass logic, the boughway terrain (grafting) | M |
| 5 | **A Salvation rite** (§6 R1, R2 or §5's rite). | 9 | found-rites row, `RUT_ResearchMod_GrantRite` | M |
| 6 | **Art commission:** the seven creatures (check renders first), the trunk-top pad, the oil haze overlay, the graft-knife and grown bridge, the rite's inscription. | all | artpipe | — |

🔴 **Sequencing:** row 0 first. The skreth makes the free two-front war real, the theft makes the ants the
sheet's ants, and the Mooring and the Seep Boil both read the tentacle-watch noise and the crown sound.
`FEVER_WOOD_FIRST_SCRIPT_1` should be written against row 0's state.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-02/feverwood_gpt.md` (prompt beside it,
`feverwood_gpt.prompt.md`), run 2026-10-02 under the standing rule (`BEDAZZLE_TOP_SHAPE_PROGRAM_1`, ruling
2026-10-01): exactly five ideas, different from each other (GPT's own check: verbs split / berth / reroute
/ admit / expose; systems demolition tech / gravship landing / weather navigation / ritual outcome / quest
evidence) and from every other biome's signature, which the prompt listed in full, **including today's
rulings for the Webwork, the Greentide, the Rust Cathedral and the Rot** (urraveth, traction lance, Felled
Noon; thurrock, blood-stopping lace, Ceded Room, Open Boast; borehulk, spying stowaway bolts, Mending Weld,
Stranger's Overhaul; the gut that walks, Swallowed Navigator, Still Alive In There, Gut-Mother, Unjoining
Draught, the Unjoining) and every Rot pitch he turned down. Model `gpt-6.1-sol`, high effort, via
`gpt_consult.py`, answered first try (started 11:02, written 11:15 PDT). GPT cites Grounded's resource
analysis, VFE Insectoids 2's hivetech, Odyssey and Vanilla Gravship Expanded, Death Stranding's shared
roads, Against the Storm's warned seasons, ReGrowth's weather visuals, Ideology rituals, Pathologic 2's
barter, Kenshi's rescues and Anomaly's Pit Gate; its links are not verified here. It independently read
the heat kind as **ambient** (agreeing with §1).

**Names checked:** *sarruth*, *urveth*, *nereth*, *varruth* and *last customer* return zero files in
`src/`, `design/`, `infrastructure/` (probe `korrum` 100 files), and zero Wookieepedia search hits each
(probe `mynock` 10). Stems: `sarr` opens *sarrash*, *sarrowhisk*, *Sarrick* (fails the four-letter stem
rule; the wedge is a technology and needs no alien name, so the card calls it the pressure wedge);
`varr` opens nothing (nearest the flora `RM_Varnoth`, `varn`); `nere` opens only English *nereid*; ⚠
*urveth* is clean on its stem but rhymes aloud with the Webwork's ruled giant *urraveth*, so the berth idea
is named in plain words if it is ever chosen.

| # | GPT's idea | mark | tier | size | BENCH read |
|---|---|---|---|---|---|
| 1 | **The pressure wedge (Sarruth):** watch a crown carpenter's drommath split its own mounting when pulled; reproduce the swelling with seep-oil, vaulm lacquer and a metal casing; a dangerous bench trial opens the research; the disposable wedge slowly cracks a chosen wall, locked door or rock face open without a blast. Sold planet-wide by the clan: the way into a sealed ruin without shelling what is inside. | 2 | free | M | **Strongest of the five, and the best tech any sitting has offered the clan since the lightning breakers.** It grows out of a built creature's built refusal (the drommath swells rather than yield), uses two Fever Wood products, and is exactly a scavenger's tool: open the vault, keep the loot. Powerful, balanced by cartridges, time and noise (cracking still calls the deep). Different from Unseaming (that took machines apart; this opens structures) and the traction lance (moves targets). **On the card.** |
| 2 | **The berth that costs a road (Urveth):** the only trunk shoulder strong enough for your ship crosses the living road two herd-groves use; cut the limb (cheap; their road is gone for good, a stump and an abandoned toll sign remain) or build a steel saddle across two trunks (dear). | 6 | free | L | A real decision with the biome's voice (the crown carried a civilisation before your ship), and it reads ground refusal correctly. Heavier than BENCH's Mooring (a landing quest and a Harmony hook into Odyssey's placement) and its victim is the grove-keepers, not the deep. **Folded into the Mooring as its expensive option** (the rented trunk-top pad becomes a pad you may have to cut a road for); not a separate row. |
| 3 | **When the crown closes (Nereth):** a still front folds the giant leaves down over boughway junctions; routes close on a countdown, herds and caravans must be moved before they are cut off, and the black pools become the forbidden shortcut. | 8 | free | M | Good and specific (the weather changes where you can walk), uses the built giant leaf, and no rain. Against BENCH's Seep Boil it changes **paths**, where the Boil changes **what you dare do** (no sparks, oil harvest). Either fills mark 8; the Boil ties to the deep and the oil, the closing ties to the crown. Held in the doc as the alternative; offered if he turns the Boil down. |
| 4 | **The Last Customer (Mob'Unloo):** in an abandoned crown tollhouse, a counter whose keeper could not close while a customer was unheard; the rite names the clan's fiercest enemy and sends an irrevocable invitation to hear its price; an armed delegation comes to parley, extort or attack. | 9 | campaign | M | Bold and Jawa, but ⚠ it is the **Bought Quarrel's shape** (an invitation, an armed delegation, trade or bloodshed), pitched at the Rot this morning and not chosen. Different in letter (one enemy invited, not two claimants), close in play. On the card as the second rite option, with that said. |
| 5 | **Varruth's Catalogue:** a porter's gift is a merchant's coat holding one of your own delivery receipts; a salvage house sells the same merchant's goods dated before he vanished. Follow the receipts: the house sends debtors forged notices to particular pool margins so the deep strips them and the house sells the salvage. Expose it and save the next victim, or take a hush payment and drop the case for good. | 5 | free | L | **Exactly his kind of giant hook**: the monster stays a monster, and the story is about traders using it, which is the clan's own business turned dark. A forensic quest built on the built porter. It competes with BENCH's Brood Ransom for the giant's story; the Ransom is cheaper and ties the tanks and the deep's young, the Catalogue is the richer story. **On the card** as the second giant option. |

GPT's ranking: the pressure wedge first, Varruth's Catalogue second. BENCH agrees on the wedge.

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. The binding rulings: **no god is evil**; **a rite gives cohesion, never a power**;
**favour shows only through events, world state and subtle odds**, voiced by the Narrator; a rite's
effect may be a dramatic, risky world event. Five-rite cap per god.

**Cap count, by hand from the register plus the 2026-10-02 ledger rulings** (found rites only). Starting
from the Rot review's table and adding the Rot's turn-1 ruling (ledger, 2026-10-02 17:44Z: the Unjoining
to Ta'Baa) and the register's B12 (the Stranger's Overhaul to Ohm):

| God | Found rites | Count |
|---|---|---|
| Ishko | Dark Vigil, Charged Reed, Stall-Hold, the Sinking | 4, one slot |
| Ohm | Engine Hour, Last Track, Deserter's Welcome, the Answering, the Stranger's Overhaul | **5, at cap** |
| Oomo | Sunning, Chime Vigil, Filtered Cup, Unspilled March | 4, one slot |
| Mob'Unloo | Blind Offering, Storm's Receipt, Cold Ledger, the Sump's effigy Price | 4, one slot |
| Sh'kaar | Snuffing, Anvil Gift, Shade Tithe, Felled Noon | 4, one slot |
| Ozzik | Lightless Burial, Salted Keeping, Flawed Masterwork, the Ceded Room, the Open Boast | **5, at cap** |
| Zizzik | five, all kept (owner, 2026-10-01) | **at cap** |
| Rekko | Unfinished Laid Down, Inherited Wreck, Mud Claim, the Mending Weld | 4, one slot |
| Ta'Baa | the Returned, Shadow Walk, Vindication Walk, **the Unjoining** (Rot, ruled 2026-10-02) | 4, one slot |

(The Sinking and the Price are counted from the Sump sitting as the Rot review recorded them; they are not
yet rows in the register, which should gain them.) **Every open god has exactly one slot**, so every rite
below spends a god's last one; the card says so.

**Not taken, and why:** an offering thrown into a pool (Oomo's *offering water*, and it feeds the thing,
which no god asked for); returning the porter's gear to the dead's kin (the Cold Ledger pays a dead man's
debt; too close); mending the porter's gear (the Inherited Wreck, the Mud Claim and the Stranger's
Overhaul crowd Rekko's salvage-returned shape); a silence held when the sentinel rises (Ishko's stillness
vigils); felling or opening the crown to the sun (the Felled Noon); a drink from a mirror pool (the Filtered
Cup and the Passed Cup); anything that rouses the full emergence (plot-reserved).

### R1. The Gate Between, for Ishko: feeding, by the prepared ambush that is never sprung (PITCHED)

- **Grounding:** Ishko is hiding, ambush and the prepared dark. The Fever Wood's oldest trick (sheet §7b)
  is *"when both come at once, open the gates between them and stand back"*: the Wildsteam survive by
  being the ambush nobody sees, letting two enemies destroy each other while they stay hidden. That is
  Ishko's whole teaching in one act.
- **Found:** on the churned no-man's-land where the columns met (sheet §8), a Wildsteam gate left standing
  open between two walls, ant-chitin heaped on one side and feralisk silk on the other, and a gate-pin hung
  on a nail, scratched *we were not here*.
- **Asks:** the participants open their defences to the world: a gate or wall section is left open
  between two marked approaches, the colony goes under cover and holds fire. The rite **calls two hostile
  forces that hate each other** (any two mutually hostile factions or manhunting packs the storyteller can
  field, chosen by the Narrator, warned a day ahead) to arrive at once from opposite sides; the rite
  succeeds the longer the colony stays hidden and unfiring while they fight through the gap.
- **Risk (the point):** real raids, at the colony's door, with its defences opened; a single shot or a
  pawn seen breaks the rite and both sides turn on the colony.
- **Outcomes (cohesion only):** shared memories by quality; Ishko's favour is told by the Narrator and
  shows only as his Exalted odds. Whatever the two sides leave behind is ordinary loot, never a reward.
- **Readable signs:** the warning letter, both columns on the map, the open gate, the letter after.
- **Collision check:** the Open Boast (Ozzik) invites one challenge **against you**; the Gate Between sets
  two enemies on **each other** while you hide. The Fever Wood's lure stake makes the same fight with a
  staked animal on this map only; the rite is the liturgy of it, performed anywhere, with the colony itself
  as the bait. The Dark Vigil and the Stall-Hold are stillness, not ambush.

### R2. Cutting the Stilts, for Ta'Baa: feeding, by leaving no root behind (PITCHED)

- **Grounding:** Ta'Baa is the refusal to root, and his lever is *leave vs. entrench*. In the Fever Wood
  nothing roots in the ground at all (ban 4): everything the races build stands on stilts or hangs in the
  crown, a camp that can be cut loose. Cutting it loose before the clan leaves is Ta'Baa's act made
  physical.
- **Found:** at an abandoned stilt-camp over a mirror pool, every post sawn through at the waterline and
  the platform sunk; on the one stump left, a Wildsteam knot-sign meaning *gone on*.
- **Asks:** within a day of a planned launch, the participants cut down every structure the clan built on
  that map (anywhere: walls, platforms, rooms), leaving nothing standing; the more the colony built and
  the less it keeps, the better.
- **Risk (the point):** real work destroyed (resources only partly returned), the clan unhoused until it
  launches; in the Fever Wood the falling stilts are the loudest noise of the season, and every pool
  wakes: the clan launches with the deep roused at its feet.
- **Outcomes (cohesion only):** shared memories by quality; Ta'Baa's Exalted odds only (*"better landing
  sites, travel opportunities, a sense of momentum"*).
- **Collision check:** the launch-rite is the launch; the Left Behind devotion leaves working things for
  others (the opposite); the Ceded Room gives one room to the jungle; the Unjoining purges a body. None
  **destroys the clan's own camp so nothing roots**. ⚠ It spends Ta'Baa's last slot, and he received the
  Unjoining today.

GPT's rite idea, if any, is in §5 and is not repeated here.

## 7. Draft turn-1 card

Plain language, no def names in option labels, headers 12 characters or fewer, every question ends
in "?", and no option is a "none" (the card's own write-in line covers that). Above the card, read
him §0's description of the Fever Wood, per the standing rule that he is never assumed to remember. Say in
one line above it that **seven creatures he approved on 2026-09-24 were never built (one of them the
free game's second raider), the ants do not steal, the bird silence cuts a sound that never plays, and
the dianoga covers only the tank**, while the Mod Settings screen is clean.

**1. Build first** (header `Build first`) — *What should be built first for the Fever Wood?*
- **Land what was already decided (recommended):** build the seven creatures you approved in September
  (the spider brood that makes the free game's two-sided war real, the ground grazers, the crown
  ambusher, the digging borer, the doomed wanderer at the pools); make the ants carry thornbugs off alive
  so you can track the column and raid it back; give the crown its working sound so the sudden silence
  means something; set its heat as still, shadeless heat; take the Star Wars lines out of the free
  tentacles and put the dianoga over the whole monster in the campaign; and judge the three borrowed slugs
  and beetle out of this campaign roster (they stay in their other homes). Buys: every promise in the
  sheet comes true in both games. Costs: a medium batch, no new mark this round. *Why: the war, the theft
  and the silence are the sheet's own heart, and the ship and weather ideas read that silence.*
- **Land it and add the giant's story together:** Buys: a hook on the monster now. Costs: a bigger first
  batch.
- **New ideas first, landing later:** Buys: new marks sooner. Costs: the free game keeps a one-sided war
  and a silence with nothing behind it.

**2. The giant** (header `The giant`) — *Which story should the monster under the pools carry?*
- **The ransom of its young (recommended):** the small tentacled things every town keeps in prison tanks
  are its own young, and it knows: the more of them the world holds, the bolder the pools get. Free one
  into a pool and the deep sets down one great gift from the very bottom. The hook: the Wildsteam
  treetop town's famous display tank holds the biggest young one ever caught, and freeing it would buy a
  gift and break the town's peace; the clan can also buy young ones from prisons and "return" them for
  salvage. Buys: a monster you bargain with, tied to the tanks you ruled. Costs: a small to medium build.
  *Why: it gives the dianoga-tank ruling a reason, and makes the deep a trading partner, not a boss.*
- **The salvage house that feeds it:** a coat the monster sets down holds one of your own delivery
  receipts; a salvage house is selling a merchant's goods dated before he vanished. Follow the paper:
  the house sends debtors forged notices to certain pools so the deep strips them and the house sells
  the leavings. Expose them and save the next victim, or take the hush money and drop it for good.
  Buys: a dark trader's mystery on the monster you already have. Costs: a large quest build.
- **The lost crawler:** the gifts the monster sets down slowly turn out to be pieces of one of the clan's
  own sandcrawlers, lost crossing the swamp generations ago; its clan plate lies under the biggest pool
  and comes up only if you force the great eye open. Buys: the clan's own history in the mud. Costs: a
  medium build, and an old vehicle inside a giant echoes the Rot's ship in the maggot.

**3. New marks** (header `New marks`) — *Which new ideas should be built (pick any)?*
- **The mooring:** your ship is the heaviest, loudest thing that ever came here. On the marsh it slowly
  mires, and the noise wakes the deep: if you stay, a tentacle wraps a hull edge and holds. Launch anyway
  and that section tears off into the pool (its pieces wash up at the edge weeks later), drive the
  monster off first, or pay the treetop town to land on a trunk-top pad, which may mean cutting a road
  the herd-keepers use. Buys: the place acts on your ship in its own voice. Costs: a medium build.
- **The oil boil:** on the hottest still days the swamp oil boils up into a low rainbow haze; oil
  gathering doubles, but one spark (a gunshot, a torch, dry lightning) flashes fire along the haze and a
  burning pool edge wakes the deep. Buys: weather that changes what you dare do. Costs: a medium build.
- **The pressure wedge:** learn from the swelling sac-creature how to make a cartridge of swamp oil and
  amber lacquer that slowly cracks open a wall, locked door or rock face without a blast; usable anywhere,
  and something the clan can sell. Buys: a scavenger's tool for opening vaults without wrecking the loot.
  Costs: a medium build (cartridges, time, and cracking is still noisy).
- **All three (recommended):** Buys: ship, weather and technology marks in one sitting, none repeating
  another biome. Costs: three medium builds. *Why: each fills a different missing mark, and all three
  lean on the deep's hearing and the swamp oil, so the biome says one thing three ways.*

**4. Rite** (header `Rite`) — *Which rite should the Salvation find in the Fever Wood?*
- **The Gate Between, for the god of hiding (recommended):** the colony opens a gate between two marked
  approaches, hides and holds fire; two enemies that hate each other are called to arrive at once and
  fight through the gap. One shot or one pawn seen and both turn on you. Buys: the Fever Wood's oldest
  trick made sacred, a dramatic, risky event. Costs: a medium build; real raids at an open door; it uses
  that god's last free rite. *Why: it is the place's own lesson, and nothing else on the planet teaches
  hiding while enemies kill each other.*
- **The Last Customer, for the god of debt and trade:** the clan names its fiercest enemy and sends an
  invitation to hear its price; an armed delegation comes to bargain, extort or attack. Buys: a bold
  trader's rite. Costs: a medium build; close to the disputed-claim rite you passed on for the Rot; uses
  that god's last free rite.
- **Cutting the Stilts, for the god of flight:** before leaving, the clan tears down everything it built
  on the map so nothing roots; in the Fever Wood the crash wakes every pool as you launch. Buys: a real
  sacrifice of a home. Costs: a medium build; work destroyed; uses that god's last free rite, a day after
  the Rot's rite went to him.

Held off the card (in the doc only): the Wildsteam drum (§3; it spends the plot-reserved emergence),
the closing crown (§5 idea 3, the weather alternative), bough-grafting (§4 row 4, the tech alternative).

## 8. Turn 1 rulings (2026-10-02) and ticket-out

Items 1, 2 and 3 decision taken by question card 2026-10-02 11:12 PDT (ledger `FEVERWOOD_SCORING_SITTING_1`,
seat BENCH, 19:07 UTC). Item 4 the owner answered in typed words (seat OWNER, 19:07 UTC), quoted verbatim below.

| Card item | Ruling | Ticket |
|---|---|---|
| 1. Build first | **Land it and add the giant's story together.** Decision taken by question card. Row 0 in full (§4): the seven creatures ratified on 2026-09-24 (`RM_Lommerel`, `RM_Silloch`, `RM_Brathek`, `RM_Nemmel`, `RM_Grolth`, `RM_Gorrameth`, and `RM_Skreth` as the free second front, which replaces the lure's ants-only fallback; art MEASURED done for all seven in the artpipe `done/`/`_artsrc/` as `feverwood_<name>_*`); the ants carry thornbugs off alive so the column can be tracked and raided back (the haul parts exist and nothing calls them; the lure raid runs with stealing off); the crown's ambient sound so the sentinel's silence cuts something; the heat kind **ambient** (still, shadeless heat; one kind of heat); the canon dianoga lines out of the free tentacles and the dianoga over the whole monster in the campaign; the three Biomes! ports (glow slug, jewel beetle, acid slug) judged out of this campaign roster, their other homes untouched; the free mod's ten `RUT_` defs renamed; the ancient-danger block the donor alone carries put on `RM_FeverWood`. "Land what was already decided" alone and "new ideas first" are **NOT CHOSEN**. The gorrameth's doomed-herd incident stays in its ruled later wave (2026-09-24). | `FEVERWOOD_RM_CAST_COMPLETION_1`, `FEVERWOOD_ANT_THEFT_RAIDBACK_1`, `FEVERWOOD_CROWN_SOUND_HEAT_1`, `FEVERWOOD_DIANOGA_GIANT_MAP_1`, `FEVERWOOD_TIER_LEAKS_FIX_1`; amended: `BIOME_TIER_CLEANUP_1` (the ten `RUT_` defs; its (b) already owned the free canon text), `FEVERWOOD_TWO_FRONT_LURE_TUNING_1` (spec 4 moved to the cast item; its "NOT owner-ruled" line was false since 2026-09-24 and is corrected) |
| 2. The giant | **The ransom of its young** (§3, the Brood Ransom), decision taken by question card: the small tentacled things towns keep in prison tanks are the sekkulaath's young; the more of them the world holds, the bolder the pools get; freeing one into a pool makes the deep set down one great gift from the bottom; Sporefall's famous display tank holds the biggest young ever caught, and freeing it buys a gift and breaks the town's peace; the clan can buy young from prisons and "return" them for salvage. The salvage house that feeds it (GPT's Varruth's Catalogue) and the lost crawler are **NOT CHOSEN**; the Wildsteam drum was held off the card and stays unticketed (it spends the plot-reserved emergence). | `FEVERWOOD_BROOD_RANSOM_1` |
| 3. New marks | **The oil boil (weather) only**, decision taken by question card: on the hottest still days the swamp oil boils into a low rainbow haze; oil gathering doubles; one spark (a gunshot, a torch, dry lightning) flashes fire along the haze, and a burning pool edge wakes the deep. The mooring (ship), the pressure wedge (technology) and "all three" are **NOT CHOSEN**; marks 6 (ship) and 2 (technology) stay open. The closing crown (§5 idea 3) and bough-grafting (§4 row 4) were held off the card and stay unticketed. | `FEVERWOOD_OIL_BOIL_WEATHER_1` |
| 4. Rite | Owner, typed: *"none, move on"*. **Recorded as none: the Fever Wood teaches no rite.** The Gate Between (Ishko), the Last Customer (Mob'Unloo) and Cutting the Stilts (Ta'Baa) are **NOT CHOSEN**; no god's last slot is spent here, and the cap table in §6 is unchanged. Per the register's R1 rule (*"A biome may answer "none"; the question must still be asked and recorded"*), this row is that record. | none |

FOUNDRY items, each `--caused-by FEVERWOOD_SCORING_SITTING_1`:

| slate row | item |
|---:|---|
| 0 | `FEVERWOOD_RM_CAST_COMPLETION_1` (six roster creatures inline, the skreth and its brood faction as the free second front; art deployed, not regenerated) |
| 0 | `FEVERWOOD_ANT_THEFT_RAIDBACK_1` (the theft LordJob, the letter and track, the column camp and the hive leg) |
| 0 | `FEVERWOOD_CROWN_SOUND_HEAT_1` (`soundsAmbient` the hush can cut; `RM_SunHeatExtension` ambient) |
| 0 | `FEVERWOOD_DIANOGA_GIANT_MAP_1` (campaign labels and texts over the six limbs; after `BIOME_TIER_CLEANUP_1` (b)) |
| 0 | `FEVERWOOD_TIER_LEAKS_FIX_1` (ancient-danger block, Ashkarr label/description and fish strip onto `RM_FeverWood`; the three ports out of this roster; inert `MayRequire` guards replaced) |
| 0 | `BIOME_TIER_CLEANUP_1`, 2026-10-02 additions (the ten `RUT_` defs and `RUT_HaulPawnAndExit` renamed `RM_`) |
| 1 | `FEVERWOOD_BROOD_RANSOM_1` |
| 3 | `FEVERWOOD_OIL_BOIL_WEATHER_1` |
| 6 | art: `infrastructure/artpipe/art_lists/feverwood_turn1_2026-10-02.csv` (3 jobs: the young's cask, Sporefall's display tank, the oil-boil haze overlay). The seven creatures need no new art (MEASURED, above). |

Sequencing: row 0 first (`FEVER_WOOD_FIRST_SCRIPT_1` is written against row 0's state); the cast item before the
theft (the lure's two fronts are tested together); `BIOME_TIER_CLEANUP_1` (b) before the dianoga mapping; the
crown sound and heat before the oil boil (same heat reading, and the boil wakes the same deep the silence warns
of).

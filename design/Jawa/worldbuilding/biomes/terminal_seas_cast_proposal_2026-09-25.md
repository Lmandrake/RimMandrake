# Terminal seas cast proposal — 2026-09-25

**Status: PROPOSAL, complete — awaiting the owner's sitting. Nothing here is ruled; nothing here has been built.**

For the owner to rule at a bench sitting. Scope: floor-resident fauna + catchable fish for the four terminal seas, plus the Propane Lake two-biome structure question. Everything proposed here is invented, RM_-tier, franchise-free.

## Framing

Sources: `TERMINALBIOMES_RM_MOD_BUILD_1` (measured state §§1–10 + the three 2026-09-24/25
ledger notes, which are the authority over the item's older prose) · the four frozen sheets
(`the_grey_deep.md`, `the_twilight_deep.md`, `the_propane_lakes.md`, `the_scald.md`) · the four
rosters (`rosters/the_grey_sea.json`, `the_twilight_sea.json`, `the_propane_lakes.json`,
`the_scald.json`) · the four defs (`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_*.xml`,
`Defs/TerrainDefs/RUT_ScaldWater.xml`) · the two noncanon naming docs (style rules + Appendix C
register) · `rot_rm_cast_proposal_2026-09-24.md` as the pattern.

**The gap this proposal fills.** The sea-biome ruling (owner, 2026-09-21) says a sea biome
describes BOTH its floor and its catch: each sea species owes a floor resident in
`<wildAnimals>` and a catchable in `<fishTypes>` (`MayRequire="Ludeon.RimWorld.Odyssey"`).
`RUT_TheScald` is the worked precedent (5 catch species + 4 floor animals). Today
(item §8, MEASURED): the Twilight Sea has a patched-in 10-species catch but only 2 floor
animals; the Grey Sea and Propane Lake have **no `fishTypes` anywhere** and 2 floor animals
each. Worse for the standalone requirement: after the §3 wildAnimals split the `RM_` defs keep
only their donor rows — `RM_TheScald` **zero**, `RM_TwilightSea` and `RM_GreySea` **one each**
(`AA_Aerofleet`), `RM_PropaneLake` two (`AA_AuroraSylph`, `AA_Skyeel`) — against the standing
law that the free mod must be rich enough to stand alone. The rosters commissioned `new_defs`
for exactly these holes and nothing has built or even *named* most of them. This proposal names
them.

**Engine fact that frames everything below (MEASURED 2026-09-24, RimSage on the Desktop,
recorded on the item):** no vanilla route creates a map on an impassable-biome tile, and the
wild-animal spawn path never reads `BiomeDef.impassable` — so on these `impassable=true` seas,
`<wildAnimals>` is inert until dive-mechanism maps with walkable floor terrain exist, and WILL
populate normally once such a map does. ⇒ Authoring floor casts now is harmless and
future-correct; the `fishTypes` catch, by contrast, is live the moment a coastal map borders
the sea. The catch rows are the player-visible half of this proposal.

**Everything proposed is invented, franchise-free, `RM_`-tier** (Q11a: the tier line is IP,
not flavour — "Star Wars style" invented names live in `RM_`). No proposal here moves an
existing row, executes an eviction (stopped by owner ruling), or paints a tile. Donor rows
(`AA_*`) stay in the free defs per §3b, alongside the new cast. Per the biome-specific-fauna
law, every new creature is a NEW species with one home; no neighbour's species is re-used.

**Naming.** Names follow the noncanon naming docs' style rules; each ran the three gates —
`check_pseudo_sw_name.py`, repo collision grep (bare + `RM_`/`RSW_`/`RUT_` forms), and a
Wookieepedia search probe with a positive control. Results in the Names-checked table.

## The Grey Sea

**Identity** (`terminator_sea.md` + `the_grey_deep.md`): hypersaline, terminal, shrinking
fastest; grey-green murk over a floor of salt pillars, brine pools with underwater shores, and
the statuary — everything that ever sank, mineral-jacketed. Monoculture (the pillar-mason),
solitary everything, **no schools in the Grey** (cap released 2026-09-10, but schooling life was
routed to the Twilight). Liquid: **brine** (FlowWorks matrix ruling 2026-09-24). Today the def
carries 2 floor animals (`AA_Aerofleet` stays; `RSW_Reefback` patches out to Utinni) and **no
fishTypes**. Sparse-by-law: this sea's sheet says a rich roster is a *failure*, so the proposal
stops at four.

| proposed name | syll. | floor-resident role | catchable? | size (bs) | commonality | art brief |
|---|---|---|---|---|---|---|
| **fessk** | 1 | the ossuary shrimp (commissioned `new_defs` row): man-sized skeletal-seeming picker working the fresh dead before the minerals take them; shy, evasive, never attacks, never tamed (grey_deep ban 3) | no — never caught, per its whole def | 0.9 | 0.01, single-spawn | bone-white angular articulation, always half-behind a pillar; long forelimbs, no bulk, watching posture |
| **sorruth** | 2 | pillar-rasp snail: fist-sized crust-grazer rasping mineral film off the mason columns; the giant's shed-crust niche at harvestable scale | **yes** — uncommon (shore-dredged at pool margins) | 0.15 | 0.4 | grey coiled shell so mineral-caked it reads as a pillar knuckle; one pale foot |
| **essarn** | 2 | pale eyeless brine-swimmer: the one lineage that osmoregulates in the open murk, cruising the density interface above the pools | **yes** — the Grey's common staple catch | 0.1 | 0.6 | finless bone-white ribbon, no eyes, salt-rime dusting; dull steel water behind it |
| **otheska** | 3 | statuary-crawler: slow shelled detritivore grazing the crystal jackets of the encased dead; harmless, ancient, few | no | 0.35 | 0.2 | flat oval shell in every grey, crystal flecks; drawn beside a jacketed silhouette for scale |

`fishTypes` shape: copy `RUT_TheScald.xml`'s block exactly — `MayRequire="Ludeon.RimWorld.Odyssey"`,
`freshwater_Common`/`freshwater_Uncommon` shorthand rows, `rareCatchesSetMaker` — with essarn
common and sorruth uncommon. ⚠️ **Conflict to rule on:** this roster's `fish.ruling` says
*"no fish … FISH_BY_BIOME_1: ruled no-fish, no analogs owed"* (2026-09-09), which the 2026-09-21
two-def sea law appears to supersede. Proposed reading: the newer law wins and the Grey's catch
is brine *chemistry-life*, not fish — but that is his call (open question 1). If no-fish stands,
essarn/sorruth land as floor residents only and `RM_GreySea` ships `fishTypes` absent,
documented.

## The Twilight Sea

**Identity** (`terminator_sea.md` + the Twilight Deep sheet): the moldy sister — one mat,
shore to shore, the last ordinary sea; placid where the Grey is ill-tempered. **Schools are
legal only below the mat-roof** (owner ruling 2026-09-10); the surface is fishable (owner,
2026-09-20, verbatim *"Just make the surface fishable"* — 10 catch species already ship via
`BiomeFishTypes_TwilightDeep.xml`: `RUT_Niim`, `RUT_Aluun`, `RUT_Hollu`, `RUT_Kellu`,
`RUT_Liiru`, `RUT_Murrol`, `RUT_Nuudal`, `RUT_Oobo`, `RUT_Pallu`, `RUT_Tikkarr` +
`RUT_RareTwilightCatches`; the build folds these into the `RM_` def). Liquid: **salt water**
(matrix 2026-09-24). So the Twilight's catch is already rich; **its hole is the floor** — after
the split the def keeps one animal (`AA_Aerofleet`).

| proposed name | syll. | floor-resident role | catchable? | size (bs) | commonality | art brief |
|---|---|---|---|---|---|---|
| **noolim** | 2 | the silver-shoal analog (commissioned, deferred-Deep set): darting cloud working beneath the mat-roof — the one place on the planet schooling is legal | **yes** — common (joins the existing 8) | 0.08 | 0.8 | slivers of dull silver in green-cast murk; drawn as a cloud, not an individual |
| **loohn** | 1 | the one true predator of the under-roof (commissioned, deferred-Deep set): patient shape hanging where the roof-light dapples | no | 2.5 | 0.01, single-spawn | long dark body mottled in roof-shadow camouflage; one saturated mate-mark, nothing else bright |
| **weloon** | 2 | soft-shelled floor crustacean-analog picking the mat-fall (dead mat tissue raining from the roof) | **yes** — uncommon | 0.2 | 0.4 | rounded felt-textured shell, mold-green; slow walker among mat drifts |
| **lunoowa** | 3 | mat-fragment mimic: drifting detritivore indistinguishable from a torn piece of roof until it moves | no | 0.3 | 0.3 | ragged mat-coloured sheet with trailing filaments; the reveal is the silhouette shifting |

No new `fishTypes` block owed beyond folding the existing patch into the def; noolim and weloon
join it as two more uncommon/common rows so the floor cast and the catch describe the same sea.

## The Propane Lake

**Identity** (`the_propane_lakes.md`): a black mirror of liquid fuel at ~−79 °C under the
brightest aurora on the planet; the war lab beneath; the V-wake creature and its kin ruled
2026-09-02 (*"the lake with exotic creatures within it"*). Today: 2 floor animals, both donor
and both ruled placements (`AA_AuroraSylph`, `AA_Skyeel` — batch-3 names auvenn/hoozan), no
fishTypes, and the roster's old note *"no fish possible (liquid propane at ~−79 °C)"*. Admission
test: hydrocarbon/ammonia-metabolic, cold-loving, untransportable dayside (R-H10). Names join
the ruled Propane Lakes accent (style rule 11: *h-*/*v-* onsets, long *au/oo/ee*, nasal codas,
no stops).

| proposed name | syll. | floor-resident role | catchable? | size (bs) | commonality | art brief |
|---|---|---|---|---|---|---|
| **vaunoom** | 2 | THE V-wake creature (ruled 2026-09-02, never built): the lake's one giant, propane-native, agitated by pumping, attacks pawns and pipe on sight | no | ~4 | 0.005, single-spawn | never seen whole — a V of parted fuel on the black mirror, one glassy back-ridge breaking it |
| **heemin** | 2 | the V-wake's kin (the ruled "+ kin"): palm-length glassy swimmers in the top fuel layer | **yes** — the propane "catch", IF fishing is ruled in (open question 2) | 0.05 | 0.7 | near-transparent sliver, aurora green/violet refracting through it; visible only as distortion |
| **oovanam** | 3 | tholin-sifting bottom crawler: works the aurora-ash fallout and the Blue Desert's arrived dead on the solid-propane floor | **yes** — uncommon dredge, same gate as heemin | 0.25 | 0.3 | soot-dark flattened crawler leaving a clean wake through pale tholin dust |
| **hoolen** | 2 | ice-sheet rim skimmer for the SURFACE face (§ structure below): runs the frozen sheets between lake pools, licking condensed fuel frost | no — surface `wildAnimals`, not a catch | 0.15 | 0.4 | long-legged, wide-footed silhouette on black ice, faint blue combustion shimmer at the joints (a lesser Burner-line reading) |

`fishTypes`, if ruled in, copies the Scald shape (`MayRequire="Ludeon.RimWorld.Odyssey"`)
with heemin common and oovanam uncommon; if the −79 °C objection stands, `RM_PropaneLake`
ships `fishTypes` absent with a comment saying so and both species stay floor-only —
either way the lake's cast finally exists.

## The Scald — gap check

Not a terminator sea (herds legal, no one-giant cap); already the fishTypes precedent. Gaps
found this pass:

1. **The item's §2 table is stale on the catch:** it says 5 fishTypes species; the def on disk
   now carries **8** (`RUT_Eesh`, `RUT_Muddal`, `RUT_Doss`, `RUT_Thuum`, `RUT_Karrash`,
   `RUT_Saal`, `RUT_BladderboilCatch`, `RUT_Ekkel`) + `RUT_RareScaldCatches`. The catch side is
   healthy. (Not a defect — a later `FISH_BESTIARY_BUILD_1` pass extended it.)
2. **The floor side goes to ZERO on the split:** all 4 wired floor animals are `RSW_` and patch
   out to Utinni, leaving `RM_TheScald` with an empty `wildAnimals` — the worst standalone gap
   of the four. The roster's commissioned `new_defs` fill it:

| proposed name | syll. | floor-resident role | catchable? | size (bs) | commonality | art brief |
|---|---|---|---|---|---|---|
| **noohm** | 1 | the bubble-sailor jelly-analog (commissioned): rides boiling bubble-lines like a little solar sail — the signature silhouette. Slime-law monosyllable applied (gel-bodied; open question 5) | no | 0.3 | 0.4 | translucent bell heeled over on a bubble-line, sail-membrane up, steam behind |
| **shulla** | 2 | the silver shoal fish-analog (commissioned): thermophile dung-fall feeder darting between vent plumes | **yes** — joins the existing 8 as a common row | 0.06 | 0.9 | hot-white sliver with a heat-shimmer double edge; drawn as a shoal |

3. **Tier note:** the shipped fish names (Eesh…Ekkel, and the Twilight's Niim set) are
   *invented*, franchise-free coinages sitting on `RUT_` defNames only because they were
   authored in Utinni. Per Q11a the tier line is IP, not flavour — they can move to `RM_` with
   the files the build already moves (`RUT_ScaldFish.xml` → the RM mod). Open question 4.

## Propane Lake: two-biome structure (owner question)

His typed input (2026-09-24, by card): *the Propane Lake is TWO biomes — a "sea floor" version
inside the lake, and the surface biome of propane lakes lying on frozen ice sheets.* Three ways
to build that, with the constraint that the 2026-09-23 settlement (ROSTER_DEAD_BMT_NAMES_SWEEP_1
step 2) put every OTHER sea's floor and catch on ONE def — floor residents in `wildAnimals`,
catch in `fishTypes`, no separate deep def:

- **Option A — two BiomeDefs, floor stays on the water def (RECOMMENDED).**
  `RM_PropaneShelf` (new): the walkable SURFACE biome — frozen ice sheets carrying propane
  pools as local-map terrain patches (exactly the shape the donor `AB_PropaneLakes` itself
  uses — a land biome whose lake is a terrain patch, per the `LIQUID_BIOMES_MAP_1`
  reconciliation finding). `RM_PropaneLake` (existing): the engine-water lake disc, carrying
  the floor cast in `wildAnimals` and any catch in `fishTypes`, same one-def pattern as the
  other three seas. Honors his two-biome wording; adds one paint-list row; no third def.
- **Option B — one def + terrain patches only.** Cheapest, but a walkable surface and an
  `impassable=true` sea cannot be one BiomeDef without contradiction (the lake tiles are
  painted engine-water; the shelf must be settleable), so his two-biome input can't actually
  be expressed. Listed for completeness, not proposed.
- **Option C — three defs (shelf / sea / floor).** Most literal reading of "sea floor
  version", but it re-opens the separate-floor-def question the 2026-09-23 settlement closed
  for every other sea, doubles the dive-mechanism's biome surface, and adds two paint rows.
  Only right if he means the floor to LOOK categorically different from the lake body when
  dived.

Under Option A, hoolen (and the existing auvenn/hoozan flyer placements, which hang OVER the
lake) would live on the shelf def's `wildAnimals`; vaunoom/heemin/oovanam on the lake def.
⚠️ Rides with fact 4: the lake def's donor terrains (`AB_PropaneLake`/`AB_SolidPropane`) get
own-authored `RM_` equivalents (`RM_PropaneLakeDeep`, `RM_SolidPropane`) — BENCH's standing
reading of the three same-day donor rulings, **flagged for his confirmation**, and the shelf
biome would use the same two terrains from the other side (solid propane walkable, lake
liquid impassable).

## Names-checked table

Gates run this pass (all three, per the framing): `check_pseudo_sw_name.py` (shape + the
137-entry canon library) · repo collision grep over `design/` + `src/` (md/json/xml, bare
name) · Wookieepedia search-API probe (`action=query&list=search`), positive control
**sarlacc → 3 hits** so the instrument can find things. Appendix C of both naming docs plus
the shipped fish registers (Eesh/Muddal/Doss/Thuum/Karrash/Saal/BladderboilCatch/Ekkel;
Niim/Aluun/Hollu/Kellu/Liiru/Murrol/Nuudal/Oobo/Pallu/Tikkarr) swept for four-letter opening
stems.

| name | coined, not compound | canon collision | register/roster collision | 4-letter stem unique | slime law |
|---|---|---|---|---|---|
| fessk | PASS | none (0 hits) | none | `fess` free | n/a |
| sorruth | PASS | none | none | `sorr` free | n/a |
| essarn | PASS | none | none | `essa` free | n/a |
| otheska | PASS | none | none | `othe` free | n/a |
| noolim | PASS | none | none | `nool` free | n/a |
| loohn | PASS | none (search 0; one hit was base64 noise in an HTML register) | none | `looh` free | n/a |
| weloon | PASS | none | none | `welo` free | n/a |
| lunoowa | PASS | none | none | `luno` free (`lund`obas differs) | n/a |
| vaunoom | PASS | none | none | `vaun` free — ⚠️ one letter off the unruled ALTERNATE *vaumeen* (batch 3); alternates don't bind, noted | n/a |
| heemin | PASS | none | none | `heem` free (alternate *heevun* = `heev`) | n/a |
| oovanam | PASS | none | none | `oova` free | n/a |
| hoolen | PASS | none | none | `hool` free (`hooz`an/`hoor`van differ) | n/a |
| noohm | PASS | none | none | `nooh` free | **applied** — gel-bodied, long-vowel monosyllable |
| shulla | PASS | none | none | `shul` free | n/a |

**Swapped after failing a gate (provenance):** *washoo* (checker: English stem "ash") →
weloon · *lohm* (Wookieepedia: Lom Pyke homophone) → loohn · *haleen* (Wookieepedia: Haleen
Snowline, exact canon name) → hoolen · *oosh* (repo: a JawaVoice interjection in 4 patch
files; Wookieepedia: Dar'oosh) → noohm · *shessa* (repo: shessa-fowl already lives in
`Alien_Bestiary.md`) → shulla. UNCERTAIN flags: none remaining — every listed name cleared
all three gates; the only soft note is vaunoom/vaumeen above.

**Accents** (style rule 5/11 — one per biome, each new, none colliding with the fifteen in
use): Grey Sea — *salt hiss and bone*: voiceless s/f/th onsets, flat a/e/o, dry codas.
Twilight Sea — *damp felt*: n/l/w onsets, long oo/ee, soft codas. Propane Lake — joins its
already-ruled accent (h-/v- onsets, long au/oo/ee, nasal codas, no stops). Scald — joins its
shipped fish register's shape (short, vowel-heavy, doubled letters).

## Syllable distribution

Across all 14 proposed names: **3 one-syllable (fessk, loohn, noohm) · 8 two-syllable · 3
three-syllable = 21% / 57% / 21%** — on the owner's 2026-09-24 fifth/half/quarter target.

## Open questions for the owner

- **Grey Sea catch:** FISH_BY_BIOME_1 ruled the Grey no-fish (2026-09-09); the 2026-09-21
  two-def sea law appears to supersede it. Proposed: it does, and the Grey's catch is brine
  chemistry-life (essarn, sorruth). Confirm, or the Grey ships `fishTypes` absent, documented.
- **Propane fishing:** is a shore catch wanted at −79 °C liquid propane (heemin/oovanam rows),
  or is the Propane Lake the one sea allowed a documented `fishTypes` exception, floor cast
  only?
- **Propane structure:** Option A confirmed (shelf def + lake def, floor staying on the lake
  def)? And the donor-terrain replacement (`RM_PropaneLakeDeep`/`RM_SolidPropane` in place of
  `AB_*`) — BENCH's standing reading, your word makes it a ruling.
- **Fish retier:** move the invented `RUT_` fish names (Eesh…Ekkel, Niim…Tikkarr) to `RM_`
  defNames as their files move into `mandrake.rm.terminalbiomes`, or keep the defNames stable
  and accept invented content on `RUT_` ids?
- **Slime-law scope:** does a gel-bodied jelly-analog count as a slime (noohm drafted as a
  long-vowel monosyllable on that reading)? If no, it can take a two-syllable Scald-register
  name instead.

# The Long Shade — bedazzle to full-mod status (2026-09-27)

**Intent:** the design proposal that takes the livable desert (`RUT_Desert` → `RM_LongShade`, mod `mandrake.rm.longshade`) from a donor-cast biome def to a full standalone RM_ mod — cast partition, invented replacements, flora, marquee rewards, feasibility, ship row, and the card agenda for the owner's sitting. Prepared for a sitting; nothing here is ruled.

_DESIGN pass, 2026-09-27, written against the frozen sheet `desert.md` (amendments add
detail, never change a ruling), `LONGSHADE_RM_MOD_BUILD_1`, `rosters/desert.json`, the
Desert accent of `noncanon_beast_names_poison_miasma_desert_scar_rot_dune_waste_cracked.md`
batch 4c, and normalized against `the_twilight_deep_bedazzle_2026-09-26.md`,
`fever_wood_rm_cast_proposal_2026-09-24.md` and `greentide_risk_reward_2026-09-22.md`.
Tier law: `biome_mod_architecture.md` §7 Q11/Q11a/Q12. Nothing here is a def; nothing here
is filed; every DRAFT name awaits the owner._

**State correction this pass rests on (MEASURED from `src/`, 2026-09-27):**
`LONGSHADE_RM_MOD_BUILD_1`'s STATE table (steps 1–3 "OWED", measured 2026-09-23) is
**stale**. The mod exists: `src/RimMandrake/LongShade/` carries `About/About.xml`, a built
DLL, `Defs/BiomeDefs/RM_LongShade.xml`, and the whole `RM_Vorrel*` family (plant, fruit,
dish, hediffs, recipes, thoughts) moved in and renamed per Q8. The twin `RUT_Desert.xml`
is frozen (header dated 2026-09-24), and
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_LongShade.xml` routes all 51 RSW_ fauna
rows AND the 6 RSW_ flora rows onto `RM_LongShade`. Phase A steps 1–4 are done; this
document is the layer above the split — what the biome is FOR, and what the sitting rules.

## 1. Thesis

**The Long Shade is the biome where position is the whole game.** Its neighbours have
already claimed the other registers: the Stillsand is the desert where time does not pass
and a shadow is property held for life; the Pyrelands boom and burn on a fire calendar;
the seas are dives, leases and hosts. The Long Shade is the one place on the dayside a
colony can actually *live off* — and the sheet built its entire biology from one number,
the distance from this shadow to the next.

Three facts of the frozen sheet are the whole personality, and every idea in this
document is one of them made playable:

- **The sprint economy.** Rest, dash, rest. Body size maps to dash range, so the
  landscape is sorted by size; rest is thermal accounting, not fatigue. Nothing is
  nocturnal because there is no night — activity has a *map*, not a rhythm.
- **Nothing pursues.** Predator and prey both solve positional problems: the predator
  bursts from shadow and is bounded by the trip *back*; the herbivore navigates to a
  patch beyond that return radius. Every patch is a commons holding both at once,
  stratified centre-to-rim. The chase does not exist here.
- **Shade is the only currency — and a roof mints it.** Building a roof manufactures the
  scarce resource, and the moment you do, your base is the best harbour on the route.
  The sheet calls this "the player consequence the biome's gameplay is built on", ending
  with something whale-sized that has walked this line for a very long time and does not
  know you have moved in.

Against the register table the Twilight doc set up: the Grey's reward is a preserved
thing, the Twilight's a living process, the Scald's an industry. **The Long Shade's
reward is a POSITION** — a rim, a staging post, a toll point, the lee of a rock, the best
roof for miles. You do not dig it out, tend it, or get admitted to it. You *hold ground*,
and everything alive contests it with you, politely and permanently. Its emotional shape
is **appraisal, then tenure**: first the player counts distances the way every animal
here does, then they own the address everything else needs.

⇒ **The test for any Long Shade idea: can you point at the ground it happens on — and is
it still worth holding tomorrow?** If a reward is not anchored to a rim, a patch, a gap
or a shadow, it belongs to another biome; if it arrives as a windfall or a boom, it
violates the biome's own law of steadiness (ban 4) and belongs to the Pyrelands. Every
idea in §4 passes both halves; §4's cost lines say what each takes.

## 2. Cast partition table

All **53** fauna rows of the frozen `RUT_Desert.xml` (= the 51-row Utinni patch + the 2
inline `JOE_` rows on `RM_LongShade`), partitioned per Q11/Q11a/Q12. The naming census is
batch 4c of the Desert naming doc (its "36 SWAC canon kept" + 15 in-scope rows + bokka +
feral grazer = 53 checks out against the def exactly). **Verdicts here are
recommendations for the sitting, not rulings.**

Key: **canon** = genuine Star Wars name, stays in the Utinni patch layer forever (Q11).
**→RM** = invented-name port; Q12 says this sitting decides its move to the RimMandrake
tier. **inline** = already native on `RM_LongShade`.

### 2a. The 36 canon rows — stay in `WildAnimals_LongShade.xml`, no action

| band | rows (commonality) |
|---|---|
| huge-herd | Bantha 0.8 · Ronto 0.4 · Skalder 0.3 |
| herd | Jamel 0.4 (Wookieepedia page verified this pass) · Eopie 0.3 · Hrumph 0.3 · IridonianReek 0.3 · Jimvu 0.3 · Kwi 0.3 · Uvak 0.3 · Varactyl 0.3 · Zeer 0.3 · Falumpaset 0.2 · Jakobeast 0.2 · Nerf 0.2 · Shaak 0.2 · TeeMuss 0.2 · FeralGrazer 0.1 (canon Legends, census-corrected 2026-09-24) · Runyip 0.1 |
| herd-small | Nuna 0.2 · Iriaz 0.1 |
| burst-predator | Wraid 0.4 · Gutkurr 0.4 (both owner-slowed to 4.4, legal under ban 3) |
| ambush-small | Kreetle 1.3 · Sketto 0.8 · Gorg 0.4 · LongtailGorg 0.4 · Worrt 0.2 · FrilledGorg 0.2 · Clodhopper 0.1 · Gizka 0.1 · Krykna 0.1 · Voorpak 0.05 |
| ambush-flier | Shyrack 0.6 — **already a real flyer** (`MaxFlightTime` 30, MEASURED in its def; the roster's "flier claim UNMEASURED" note is stale) |
| megafauna | Horax 0.01 |

Uvak also carries `MaxFlightTime` 60 (MEASURED) — the flyers-fly rule is already
satisfied on both canon flyers; no flight work is owed by this sitting.

`RSW_WraidAlpha` 0.15 (the 37th SW-tier row) is an invented *variant of a canon species*
— per the naming rules a variant takes the canon variant shape, so it stays SW-tier
beside its parent. It already carries `RM_CompHeatBurstPredator` (MEASURED): the sheet
§4's burst-grab-retreat flagship is **built and wired**.

### 2b. The 14 invented-name rows — Q12 says THIS sitting moves them to the RM tier

| row (comm.) | name state | evidence | recommendation |
|---|---|---|---|
| `RSW_Bokka` 0.5 | **bokka**, RULED | one home = Long Shade (owner 2026-09-22, recorded in the roster json) | →RM (`RM_Bokka`) |
| `RSW_Ossik` 0.4 | **ossik**, RULED (batch 2 port name) | port of AA_DesertAve, the navigator | →RM |
| `RSW_Kudda` 0.2 | **kudda**, RULED | ⚠️ dual-homed with the Stillsand *by the roster's own law field* — agenda Q6 | →RM, home question to the owner |
| `RSW_Thurra` 0.05 | **thurra**, RULED | port of AA_Gigantelope | →RM |
| `RSW_Vosska` 0.05 | **vosska**, RULED | sand-burrow ambusher (legal off pavement, ban 6) | →RM |
| `RSW_Khorrak` 0.035 | **khorrak**, RULED | flat terrain-mimic (§4 "flat and oriented") | →RM |
| `RSW_Ommok` 0.025 | **ommok**, RULED | slow sand-filter, reads the buried canopy | →RM |
| `RSW_Ulgga` 0.015 | **ulgga**, RULED | slow soft-sand burrower-predator | →RM |
| `RSW_Jellypot` 0.7 | **pommik**, DRAFT (batch 4c) | donor coinage; sits in a shadow and waits — "own a shadow" in one def | →RM; rename rides the batch-4c ruling |
| `RSW_TruffleMole` 0.5 | **pikkut**, DRAFT | ⚠️ wired in BOTH deserts; owner's "desert & extreme desert" note is a CANDIDATE set per his 2026-09-22 correction — agenda Q6 | →RM, home question |
| `RSW_GreatDevourer` 0.5 | **hakkro**, DRAFT | owner's note "relative of the Sarlacc wandering the desert"; kinship goes in the description | →RM |
| `RSW_Groundrunner` 0.5 | **dobbak**, DRAFT | docile mining bear-mole | →RM |
| `RSW_MatureFleshbeast` 0.5 | **vukkoroth**, DRAFT | "immature sarlacc" per the owner's note | →RM |
| `RSW_ShadeWhale` 0.015 | ⚠️ "shade whale" is an English compound, unruled | our own §4c flagship; **fully wired** (MEASURED): `RM_ShadeSeekingWanderExtension` + `RM_FilterFeedExtension` + `RM_CompProperties_DungSeeder` — the item's "filter-feeding C# unbuilt" line is stale | →RM; name offer **thommak** (DRAFT, checker-clean, 0 Wookieepedia hits) — agenda Q5 |

Already inline on `RM_LongShade` (no move needed): `JOE_Landopus` 0.5 (**ippok** DRAFT)
and `JOE_Cephalope` 0.5 (**qorrax** DRAFT) — non-SW donor absorptions, Q9. ⚠️ Cephalope
carries a live CONFLICT: the 2026-09-09 roster *evicted* it under ban 3 (predator, spd
8.8 MEASURED — the fastest thing in the biome) and the owner's round-2 review *imported*
it at 0.5. Both entries stand in `desert.json` today. Agenda Q7.

### 2c. What the free tier looks like after the move — and the holes

If the sitting ratifies 2b, `RM_LongShade` standing alone carries **16 fauna**: a
navigator, a grain-feeder, five subsurface/flat specialists, two shadow-sitters, a
digger, two sarlacc-kin, the megafauna flagship, the two JOE natives, and the bokka.
Rich in the weird bands — and **empty in exactly the bands the sheet calls the campaign's
livelihood**:

| hole (free tier) | why it matters | invented replacement (all DRAFT, Desert accent: doubled consonant, -a/-ik/-ok, 5–7 letters; all pass `check_pseudo_sw_name.py` 6/6, `src/` label sweep clean, Wookieepedia probe 0 exact hits) |
|---|---|---|
| huge-herd / mobile shade wall | every huge-herd row is canon; §4's "a herd is a mobile shade structure" has no free-tier bearer, and §7 names herd beasts the campaign's pack stock | **sollak** (`RM_Sollak`, bs ~4.0) — leggy tower-shouldered giant; standing herds shade each other; `packAnimal true`; carries `RM_ShadeSeekingWanderExtension` (shipped) |
| herd / draught endurer | all ~17 herd rows canon; free tier has **zero pack animals** (all five `allowedPackAnimals` are canon, MayRequire-guarded) | **gennok** (`RM_Gennok`, bs ~2.4) — slow strong endurer that navigates patch to patch, never sprints; `packAnimal true`; plain stats + shade-seeking, no new C# |
| herd-small | Nuna/Iriaz canon; the dense-patch small-life stratum (§4's size-sorting law) is unrepresented | **tebbra** (`RM_Tebbra`, bs ~0.35) — quick close-country grazer confined to dense-patch hills; shade-seeking wander only |
| burst-predator | Wraid/Gutkurr canon, WraidAlpha canon-derived; the free tier has **no predator embodying the biome's signature mechanic** | **dakkra** (`RM_Dakkra`, bs ~1.6) — bursts from shadow, grabs, retreats to cool; carries `RM_CompHeatBurstPredator` (shipped — WraidAlpha's wiring is the copy template) |
| the glitter-birds | owed by the sheet itself (§4c, "Owed": name and def) — tiny shadow commensals living in the whale's shade | **pirrik** (`RM_Pirrik`, bs ~0.1) — real flyer (`MaxFlightTime`, Core stat); v1 = shade-seeking + spawn-weighted near the flagship; true follow-the-whale C# deferred. ⚠️ Wookieepedia fuzzy near-miss *Pirrip* — flag for taste |

Two coins were struck during drafting for real collisions and replaced: *rukka* (live Rot
plant label "rukka cap") and *zhurra* (ruled crags stem *zhurrakor*). The ambush-flier
band (Shyrack's) is left canon-only deliberately — agenda Q4 asks whether it needs a
free-tier bearer or whether pirrik's flock reads close enough.

Pyramid check: of the five, only sollak exceeds bs 2; smalls dominate, and the biome's
45.0%-small pyramid pressure (the roster's own worst-in-sweep reading) is eased, not
worsened.

## 3. Flora

*(to fill)*

## 4. The marquee — rewards, experiences, interactions

*(to fill)*

## 5. Weather / terrain / mechanics feasibility

*(to fill)*

## 6. Ship contribution row

*(to fill)*

## 7. Card agenda

*(to fill)*

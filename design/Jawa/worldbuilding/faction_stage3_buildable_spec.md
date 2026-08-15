# Faction Stage 3 — the buildable spec

_Written by **PROJECT**, 2026-08-13 overnight, against faction roster Stage 3
(now `design/V2_DREAMS.md` **B20**).
Substrate is the 574-mod dump. **This is `[v2]` spec work**: v1 cuts
build *depth*, not spec, and speccing costs no verification pass. v1 still ships
one thin Empire reskin._

**Stage 2 found the roster was "specified in a vocabulary that does not reach the
engine." This is the translation.** The fiction is not re-litigated — it is
excellent and it is the owner's. Every design choice below is either *already in
the roster* or an *engine expression of it*.

---

## 0. The two global decisions everything else depends on

### 0a. ⭐ BTD REMIX is the canon xenotype family

**Three mods ship the same species.** `RimMandrakeTwilek`, `OuterRim_Twilek` and
`guy762_xenotype_twilek` all exist and all are `inheritable`. Mixing families
gives visually and mechanically inconsistent Twi'leks — two "Wookiees" that are
different creatures to the engine.

**Measured across the live dump:**

| family | species | genes/species (avg) | max |
|---|---:|---:|---:|
| **[BTD] Xenotype REMIX** | **70** | **20.5** | **34** |
| Star Wars Xenotypes (`guy762`) | 58 | 15.6 | 30 |
| Outer Rim – Galactic Diversity | 44 | 8.3 | 18 |

> **RULE: use `BTD_*` for every species it covers. Fall back to `guy762_*` only
> for species BTD lacks. Never `OuterRim_*` for a species BTD has.**

**Why this serves "make each race uniquely represented":** at 20–34 genes a
species genuinely *plays* differently — carry weight, temperature tolerance, meat
requirement, melee damage, sleep need. At 6–9 genes it is a hat. The gene budget
*is* the mechanical identity, so the family choice is the single highest-leverage
decision in this document.

**BTD covers 70 of the 79 distinct SW species available.** The apparent gaps are
mostly naming variants that BTD *does* cover:

| looks missing | actually |
|---|---|
| `moncal` | `RimMandrakeMonCalamari` ✅ |
| `nemoidian` | `RimMandrakeNeimoidian` ✅ |
| `zabrak` | `RimMandrakeIridonian` ✅ — Zabrak and Iridonian are the same species |
| `sith`, `massassi` | `RimMandrakeSithKissaiPureblood` / `RimMandrakeSithMassassi` / `RimMandrakeSithZ` ✅ — **three castes** |
| `geonosian_drone` | `RimMandrakeGeonosianVariants` ✅ |

**Genuine gaps, both fine:** `OuterRim_ForceGremlin` — already excluded by the
roster; and `Lee_xenotype_kage` (Kage, 14 genes) — **the only species with a
single source anywhere in the stack.** Worth keeping for that reason alone.

⭐ **`RimMandrakeSithKissaiPureblood/M/Z` is a gift the roster has not spent.** Three Sith castes —
Kissai (priest), Massassi (warrior), Zugurak — let the Galactic Empire's Sith element
be a *caste system* rather than one "Sith" tag. See §2.

### 0b. The water doctrine IS expressible — that is the headline finding

**Stage 2 said water had "no def field." That was true of the *word* and wrong
about the *mechanic*.** The roster's water doctrine is mostly a statement about
**raid reach**, and raid reach is exactly what `FactionDef` controls:

| roster phrase | engine expression |
|---|---|
| "raid generation effectively disabled" | `raidsForbidden: true`, or a floored `raidCommonalityFromPointsCurve` |
| "high raid frequency, very short duration, no siege" | `canSiege: false` + high raid commonality + `earliestRaidDays` low |
| "near-useless expeditionary, devastating on home defence" | `canSiege: false`, `canStageAttacks: false`, rich `defenderGroup` pawnGroupMakers |
| "hard-sited to wooded/upland tiles" | **Sensible Factions** biome weighting (`biome`/`get_PrimaryBiome` confirmed in its DLL) |
| "settlements cluster near X" | **Faction Control** `CenterPoint` + `factionGrouping: Tight` |
| per-pawn water endurance | **`ThirstRateMultiplier`** — see below ⭐ |

#### ⭐⭐ THE FIND OF THE NIGHT: `ThirstRateMultiplier` exists, and nothing uses it

**The roster's master resource is mechanically backed, and NO SPECIES uses it.**
Verified in the live dump — **and re-verified after BRIDGE's method review, which
corrected the claim twice.**

```
Dubs Bad Hygiene - Thirst      load 130, LIVE      -> NeedDef DBHThirst, fallPerDay 0.5
StatDef ThirstRateMultiplier   "thirst rate factor", Dubs Bad Hygiene Lite
                               defaultBaseValue 1, minValue 0, maxValue ~inf
GeneDefs using it              0     <- of 4,844
HediffDefs using it            4     <- Diarrhea, Dysentery, Cholera, BionicBladder
```

⚠️ **Correction 1 — "nothing uses it" was WRONG.** Four DBH hediffs do. The
accurate claim is narrower and still the point: **no gene, no xenotype and no
species uses it.** Every current user is a *disease or implant*, none is an
identity.

✅ **Correction 2 — the absence claim survives a positive control**, which is the
test that makes it a measurement rather than the dumper's silence (BRIDGE's
standing question: *what would this print if the thing were broken?*). The dumper
**does** serialise the relevant shape: **276 genes carry `statFactors` and 292
carry `statOffsets`**, full `StatModifier` records with stat name and value —
e.g. `Furskin → ComfyTemperatureMin −10`. **So a gene setting
`ThirstRateMultiplier` would appear. It does not. The zero is real.**

⭐ **And the control found something better than it was checking:
`BionicBladder` carries `ThirstRateMultiplier: −0.5`.** That is a **working,
shipped proof that an implant can reduce a pawn's thirst rate** — the exact
mechanic the roster wants, already functioning in the stack. **Copy that pattern
onto a gene.**

**Every per-species water claim in the roster is buildable through this one
stat**, and none of it has been built:

| roster claim | build |
|---|---|
| Iktotchi "low thirst rate" | `ThirstRateMultiplier` ~0.5 |
| Wookiees "carry more water", severe requirement | multiplier **> 1** — thirst *faster*, the correct direction for a rainforest species on a desert world |
| Geonosian drones "very low thirst" | ~0.3 |
| battle droids "carry none" | ⚠️ **reduction is PROVEN (`BionicBladder −0.5`); zero is NOT.** `minValue: 0` is a *declared range*, not observed behaviour — nothing proves the consumer does not clamp or special-case 0. **Prefer `DBHThirst.Exemptions` / `onlyIfCausedByGene` for droids**, which removes the need rather than zeroing the rate. Measure before promising. |
| "dry-capable" bounty hunters — **`Kaleesh` only**; Zabrak, Bothan and Devaronian are neutral, Chiss and Umbaran heat-INTOLERANT | 0.6–0.8 for Kaleesh, 1.0 for the rest |
| "water-hungry" (Trandoshan) | 1.2–1.5 |

⚠️ **No gene modifies thirst directly** — of 4,844 `GeneDef`s only 6 mention
thirst at all, and every one is Biotech's unrelated `KillThirst` or a food gene.
**The route is a gene carrying a `statFactor` on `ThirstRateMultiplier`**, or the
stat set on the pawnkind/race. `DBHThirst` also exposes `Exemptions` and
`onlyIfCausedByGene`, so droids can be exempted from the need entirely rather
than merely slowed.

**Why this is the most valuable finding here:** it converts the water doctrine
from *fiction the engine tolerates* into *fiction the engine enforces*, and it
costs one stat per species. **This is the cheapest large win available** — a
single `statFactor` per xenotype makes 79 species mechanically distinct on the
axis the whole campaign is built around. It also directly answers "make each race
uniquely represented": thirst rate is a number the player *feels* every raid,
every caravan, every siege.

⚠️ **Heat is the complement and is PARTLY built — 30 of 70 BTD species carry a
`MinTemp_*`/`MaxTemp_*` gene, not all of them.** (Corrected on self-review; the
first draft said "already carry them", which overstated it.) **Thirst + heat
tolerance are the desert world's two axes:** heat is 43% built, thirst 0%.

#### 🔴 …and the heat genes CONTRADICT the roster's "dry-capable" list

Checked because the two axes must agree. `faction_roster_v2.md` §10 lists
**Kaleesh, Zabrak, Chiss, Umbaran, Devaronian, Bothan** as *dry-capable* hunters
who "push much further" than water-hungry ones. Measured:

| species | temp genes | verdict |
|---|---|---|
| `RimMandrakeKaleesh` | `MinTemp_SmallIncrease`, `MaxTemp_SmallIncrease` | ✅ heat-tolerant |
| `RimMandrakeIridonian` (Zabrak) | *none* | neutral |
| `RimMandrakeDevaronian` | `MinTemp_SmallIncrease` | neutral |
| `RimMandrakeBothan` | *none* | neutral |
| **`RimMandrakeChiss`** | `MinTemp_LargeDecrease`, **`MaxTemp_SmallDecrease`** | 🔴 **heat-INTOLERANT** |
| **`RimMandrakeUmbaran`** | `MinTemp_SmallIncrease`, **`MaxTemp_SmallDecrease`** | 🔴 **heat-INTOLERANT** |

**The mod author is right and the roster is wrong** — and pleasingly so. Chiss
are from **Csilla, an ice world**; Umbara is the **sunless** world. Both are
canonically the last species you would send into a desert, and BTD encodes that.

⭐ **Recommendation: flip Chiss and Umbaran to the water-hungry tier.** It costs
nothing, it agrees with canon, it agrees with genes already in the stack — and it
is a *better story*: the pale sunless-world assassin who wilts in the open desert
and has to break off the hunt first. **Kaleesh alone carries the dry-capable
role**, which also makes them meaningfully special rather than one of six.

**Filed for WORLD** (`design/Jawa/worldbuilding/` is theirs, rule 9), not edited here.

> **The water doctrine is split across three layers: `FactionDef` booleans for
> reach, Sensible Factions for siting, and xenotype genes for endurance.** No
> single layer expresses it, which is exactly why Stage 2 concluded it was
> unexpressible.

**This is the "unlike most RimWorld settings" mechanic.** In a normal playthrough
every faction raids you the same way and differs only in tech level.
Here, *how far a faction can reach* is a physiological fact about its species, and
the map's water is the constraint. A Wookiee ally is devastating at home and
cannot be brought along. A Tusken raid is frequent, close and cannot siege. An
Deepwater Compact warden cannot reach you at all — so the Compact is a *supplier and a
customer*, never a threat. **Three factions, three genuinely different games.**

---

## 1. Vessel assignments — MEASURED, 2026-08-14

🔴 **The vessels are VANILLA defs.** Reassigned against the live def dump, because
the vanilla defs are what the trade, raid and quest economies are wired to.
`PATCH` = adopt a live def; `AUTHOR` = our own `FactionDef`. Both are licence-clean
(patching Outer Rim is fine, **copying their defs is a derivative** — CC BY-NC-ND).

| # | roster faction | vessel | route | pawnkinds |
|---|---|---|---|---|
| 1 | Hutt Cartel | — | **AUTHOR** | uses Gamorrean/Nikto kinds; see §1a |
| 2 | **the Galactic Empire** | 🔴 **vanilla `Empire`** | **PATCH** ⭐ | Royalty's Empire kinds |
| 3 | Homestead Defense League | **vanilla `OutlanderCivil`** | **PATCH** ⭐ | vanilla outlander kinds |
| 4 | Deep Desert Tribes | **vanilla `TribeCivil`** | **PATCH** ⭐ | vanilla tribal kinds |
| 5 | Free Droid Enclaves | — | **AUTHOR** (U3) | `OuterRim_EscapedBattleDroid` is a *source*, not a vessel |
| 6 | Wildsteam Clan | — | **AUTHOR** | none |
| 7 | Deepwater Compact | — | **AUTHOR** | none |
| 8 | Geonosian Foundry Hive | — | **AUTHOR** | JDS droids usable as the droid half |
| 9 | **Ascendant Helix** | 🔴 **none — AUTHOR** | **AUTHOR** | `Ancients` is `hidden: true`, `settlementGenerationWeight: 0`, `maxCountAtGameStart: 0`, `canMakeRandomly: false` — it cannot settle, appear in the faction list, or be diplomatic |
| 10 | Blackstar Company | **vanilla `Pirate`** | **PATCH** ⭐ | vanilla pirate/mercenary kinds; ships `permanentEnemy: true` and keeps it |
| 11 | Jawa Trade Moot | — | **AUTHOR** | — |
| 12 | the Junkers | — | **AUTHOR** | scavenges others' kinds |

🔴 **The shipped Empire patch is on the wrong vessel.**
`src/Jawa/Jawa_Patches/Patches/ImperialDesertDirectorate.xml` targets
`OuterRim_GalacticEmpire`, a mod def. **Re-point it at vanilla `Empire`.** v1 row 1
was closed on a label seen live on a vessel we are abandoning, so it has to be
redone — cheap, but not already done.

**Four factions ride vanilla vessels** (2, 3, 4, 10) and are the cheap ones.
**Eight are authored** (1, 5, 6, 7, 8, 9, 11, 12).

### 1a. ⚠️ A collision the roster does not know about — RESOLVED by the vessel table

**Blackstar Company rides vanilla `Pirate`, so `OuterRim_BinaryStarRaiders` is not
contested.** It stays available as *bought* Hutt muscle, which is what our
`Jawa_Patches/Defs/PawnKindDefs/GamorreanPawnKinds.xml` already uses it for. The
record of why the two claims collided is kept below.

**`OuterRim_BinaryStarRaiders` is wanted twice.** Our own
`Jawa_Patches/Defs/PawnKindDefs/GamorreanPawnKinds.xml` already points two
Gamorrean kinds at it as *Hutt muscle* — while it is also the obvious
Bounty-Hunter vessel (13 mercenary/pirate kinds: `Mercenary_Elite`, `_Sniper`,
`_Heavy`, `_Slasher`, `PirateBoss`, three grenadier types).

**Recommendation: give Binary Star to the Blackstar Company.** Its kinds are
*professional contractors*, which is the Compact exactly; the Hutts' own identity
is servile infantry plus *bought* muscle, so the Cartel should be authored and
should **hire** Binary Star rather than be it. That also preserves the Gamorrean
patch — Gamorreans remain Hutt-owned, they simply are not the same faction.

**Owner question, not a blocker:** if you would rather Binary Star be the Hutts,
the Compact needs authoring instead. Say which and I will re-cut.

---

## 2. Per-faction engine specification

Fields listed are the ones that **vary meaningfully** — recall Stage 2's finding
that 24 of the 125 `FactionDef` fields never vary at all, and the real decision
surface is dominated by `pawnGroupMakers`.

### 1. Hutt Cartel — AUTHOR
```
techLevel                     Industrial
permanentEnemy                false          // extortion needs a live relationship
naturalEnemy                  false
canSiege                      true           // wealthy, static, can invest
canStageAttacks               true
settlementGenerationWeight    high (~1.0)
requiredCountAtGameStart      1
leaderTitle                   "Hutt lord"
baseTraderKinds               bulk + exotic + weapons + water   ⭐
caravanTraderKinds            slaver kinds if Ideology active
```
**Races (BTD):** `RimMandrakeHutt` 3% masters · `RimMandrakeNikto` ~45% servile infantry ·
`RimMandrakeGamorrean` ~20% muscle · `RimMandrakeWeequay`, `RimMandrakeKlatoonian` ~15% ·
`RimMandrakeTwilek` ~10% (dancers/slaves) · `RimMandrakeQuarren` 5% accountants.
**Water = Require (oasis).** `CenterPoint` clustering onto oasis tiles via Faction
Control; the water they *sell* is the extortion mechanic.
⭐ **Endgame hook already in the roster:** the Hutts are the way off-world. Their
settlements must therefore survive to endgame — do **not** make them permanently
hostile.

### 2. the Galactic Empire — PATCH vanilla `Empire` ⭐ v1 ROW
```
label                         "the Galactic Empire"
leaderTitle                   "Emperor"          // canon; "Sector governor"/"Sector Director" are retired
description                   rewrite
colorSpectrum                 Imperial grey/black
permanentEnemy                true             // the permanent enemy among the authored factions
techLevel                     Ultra (unchanged)
```
🔴 **The Empire is the permanent enemy, and the price is accepted.** A permanently
hostile Empire deletes Royalty's title/permit/honour progression — correct for a
Jawa scavenger clan, and a decision rather than a side effect
(`faction_world_spec.md` §5). **Hostility cannot be expressed as goodwill:** there
is no goodwill field on `FactionDef`, so `permanentEnemy: true` is the mechanism.
**Races:** ~78% baseliner human (the roster's *human primacy* is doctrine, so
this is the one faction where humans dominate **on purpose**) · near-human
auxiliaries only: `RimMandrakeChiss` (officers), `RimMandrakeUmbaran`, `RimMandrakeZeltron`.
⭐ **Sith caste, using BTD's three:** `RimMandrakeSithKissaiPureblood` Kissai as ISB inquisitors ·
`RimMandrakeSithMassassi` Massassi as shock troops (the roster already notes these are
Yavin-jungle stock → **wet-tile origin tell**) · `RimMandrakeSithZ` Zugurak rare elites.
**v1 does labels and colour only. Everything else here is v2.**

### 3. Homestead Defense League — PATCH vanilla `OutlanderCivil`
```
techLevel                     Ultra (unchanged)
settlementGenerationWeight    1 (unchanged, highest count — "most numerous")
canSiege                      false          // farmers, not besiegers
raidsForbidden                true           // D1: the Homestead does not raid at all
leaderTitle                   "councilman" (unchanged — already correct)
```
**Races:** human 20% · `RimMandrakeIthorian` 12% · `RimMandrakeDuros` 10% · `RimMandrakeRodian` ·
`RimMandrakeBith` · `RimMandrakeIktotchi` (the roster's **only long-range asset** — low thirst
+ precognition; gate these to a dedicated `pawnGroupMaker`).
**Water = Manufacture.** Vaporators are the destructible objective. This is the
Tusken casus belli and should be a **hardcoded hostility** to faction 4.

### 4. Deep Desert Tribes — PATCH vanilla `TribeCivil`
```
techLevel                     Industrial     // roster: firearms+electricity, gear-gated by pawnkind
permanentEnemy                false          // adoption quest chain exists
canSiege                      false          ⭐ carries no water for a siege
canStageAttacks               false          ⭐
earliestRaidDays              very low
raidCommonalityFromPointsCurve  HIGH         ⭐ frequent, close, brief
settlementGenerationWeight    high (numerous)
```
**Races:** `RimMandrakeTusken` ~100%, two tiers via pawnkind not species (Dune Sea /
canyon). Near-monocultural by design.
⭐ **The water-raid group is the standout mechanic in the whole roster** — a
`pawnGroupMaker` whose objective is *stealing containers, not killing*. Vanilla
has no "steal and leave" raid strategy, so this needs either a
`disallowedRaidStrategies` narrowing or a C# `RaidStrategyDef`. **Flag: this is
the one roster mechanic that may not be reachable in pure XML.** Verify before
promising it.

### 5. Free Droid Enclaves — AUTHOR (closes U3). `OuterRim_RogueDroidColony` is a pawnkind source, not the vessel
```
settlementGenerationWeight    0 → 0.3        // currently never placed
requiredCountAtGameStart      0 → 3          // roster wants 3 settlements
maxCountAtGameStart           0 → 3
canMakeRandomly               false → false  // keep: they do not spread
pawnGroupMakers               NONE → author  ⭐ the whole blocker
raidsForbidden                true           // roster: raid-disabled, presence via map events
techLevel                     Industrial
```
**Pawnkinds:** `OuterRim_EscapedBattleDroid` exists (the only one). Supplement
from Droid Depot (`OuterRim_BattleDroid`, `_SuperBattleDroid`, `_CommandoDroid`,
`_MagnaGuardDroid`) — but note **those default to `PlayerColony`**, so they need
either a patch or our own thin kinds.
**Water = Deny** — they sit *on* water and poison it. The poisoned-well **map
event** gives a raid-disabled faction constant presence, which is how a
3-settlement faction stays relevant. Decontamination quest is the counter.

### 6. Wildsteam Clan — AUTHOR
```
techLevel                     Industrial
permanentEnemy                false          // friendly by default
naturalEnemy                  false
canSiege                      false          ⭐
canStageAttacks               false          ⭐ near-useless expeditionary
settlementGenerationWeight    low (~0.3)     // "small refuges"
```
**Races:** `RimMandrakeWookiee` 48% · Wookiee-kin (`RimMandrakeLasat`, `RimMandrakeTogorian`) 25% ·
`RimMandrakeCathar` 10% · `RimMandrakeTrandoshan` **excluded** (canon enemies of Wookiees — a
nice authenticity beat).
**Water = Require (severe).** Sited to rare wooded/upland/cool tiles via Sensible
Factions biome weighting. **The standing logistics quest** — the player must
supply water to field Wookiee allies — is the mechanical content of "small but
formidable" and is genuinely novel.

### 7. Deepwater Compact — AUTHOR
```
techLevel                     Industrial
permanentEnemy                false
raidsForbidden                true           ⭐ wardens dehydrate before arrival
canSiege                      false
settlementGenerationWeight    moderate — holds EVERY natural water tile
baseTraderKinds               water + bulk   ⭐ the cheap neutral supply
canRequestTraders             true
```
**Races:** `RimMandrakeMonCalamari` 22% · `RimMandrakeQuarren` 23% · `RimMandrakeSelkath` 20% ·
`RimMandrakeNautolan` · `RimMandrakeGungan` · `RimMandrakeHerglic`. **All amphibian/aquatic — this is
physiology, not preference.**
⭐ **A faction that cannot attack you is a design gift, not a gap.** The Compact is
pure economy and politics: it sells water to everyone *including the Galactic Empire*,
so Imperial water convoys are an attack surface the player can exploit without
ever fighting the Compact itself.

### 8. Geonosian Foundry Hive — AUTHOR
```
techLevel                     Industrial
permanentEnemy                false
canSiege                      true           // industrial, droid-backed
canStageAttacks               true
settlementGenerationWeight    moderate; sited to mountains/ore/caves
```
**Races:** `RimMandrakeGeonosianVariants` 76% (queen, aristocrats, warrior + worker drones) ·
savant caste 8% · `RimMandrakeBith` 6% engineers · `RimMandrakeKaminoan` gated to
wet-adjacent hives only.
**Droid half: use JDS CIS kinds** — 16 available.
⚠️ **JDS's kinds are all `combatPower: 45`, flat**, so a raid of B1s costs the
same points as a raid of Droidekas and the difficulty curve is meaningless. **The
KotOR Rogue Droid kinds are properly spread (35→500).** Either rebalance JDS by
patch (this is `design/V2_DREAMS.md` §4's U2 territory) or prefer KotOR kinds for the
hive's droid element.
**Water = Forbid (arid-adapted)** — very low thirst, droids carry none. Combined
with a 35–55% droid share this is the **longest-reach hostile faction on the
map**, which is a good reason for it to be uncommon.

### 9. Ascendant Helix — AUTHOR. 🔴 `Ancients` is impossible: `hidden: true`, `settlementGenerationWeight: 0`, `maxCountAtGameStart: 0`, `canMakeRandomly: false`
```
techLevel                     Spacer/Ultra
permanentEnemy                false
settlementGenerationWeight    low (~0.2)     // small, wealthy
canRequestTraders             true
baseTraderKinds               exotic + medical + implants
```
**Races:** `RimMandrakeArkanian` 26% pureblood caste · `RimMandrakeKaminoan` 20% · brute stock
12% — **the engineered underclass**, best expressed with Big-and-Small or Alpha
Genes stock rather than a SW species.
⭐ **The roster gives them "the planet's monsters" (Vanilla Genetics Expanded).**
That makes the Helix the source of every spliced creature — a *supplier of
threats* rather than a threat, which is a third distinct faction role.

### 10. Blackstar Company — PATCH vanilla `Pirate`
```
label                         "Blackstar Company"
leaderTitle                   "boss" → "guildmaster"
permanentEnemy                true (vanilla `Pirate` ships it)  // keep — patching it false would gut the vanilla raid economy
settlementGenerationWeight    1 → low (~0.2)  ⭐ "few settlements"
maxCountAtGameStart           1 (already)
canSiege                      true → false    ⭐ small parties, no siege
```
**Kinds already present (13):** `Mercenary_Elite/Gunner/Heavy/Slasher/Sniper`,
`Pirate`, `PirateBoss`, `Drifter`, `Scavenger`, `Thrasher`, 3 grenadiers
(`_Ion`, `_CryoBan`, `_Destructive`). **This is the richest ready-made kit in the
stack** and maps almost one-to-one onto "3–10 pawn hunting party".
**Races:** `RimMandrakeKaleesh` 15% — **the only dry-capable species in the faction** ·
`RimMandrakeIridonian` 12% (Zabrak), `RimMandrakeBothan`, `RimMandrakeDevaronian` neutral ·
`RimMandrakeTrandoshan` 12% water-hungry · `RimMandrakeChiss`, `RimMandrakeUmbaran` **heat-INTOLERANT**.
⭐ **Water = the water clock**, and it is the best fight-design in the roster: a
hunter arrives with finite water, so withdrawing into dry tiles converts a fight
into a resource duel. **Kaleesh push further; everyone else does not** — so the
species of the hunter tells the player how long they have. That is legible,
diegetic difficulty.

### 12. the Junkers — AUTHOR
```
techLevel                     Neolithic/Industrial mix
permanentEnemy                true           // reviled, no diplomacy
naturalEnemy                  true
canSiege                      false
raidCommonalityFromPointsCurve  moderate-high
settlementGenerationWeight    moderate
```
**Races:** deliberately the sector's disposable species — `RimMandrakeUgnaught`,
`RimMandrakeGamorrean`, `RimMandrakeNikto`, `RimMandrakeKlatoonian`, `RimMandrakeSnivvian`, `RimMandrakeDefel`,
`RimMandrakeMimbanese`. **Thematic inversion of the Jawa Trade Moot**: same trade, no
inheritance.
**Water = Allow (scavenged)** — reach is capped by their last theft, so a warren
that has just taken a caravan is briefly dangerous. Expressible as a raid-cooldown
interaction (Faction Raid Cooldown is live at load 146).

---

## 3. Build order — cheapest first, and it is not the roster's order

| order | faction | why |
|---|---|---|
| **1** | **the Galactic Empire** | v1 row; vanilla `Empire` + Royalty kinds exist; labels only ⚠️ **the shipped patch points at the wrong def and must be re-pointed** |
| **2** | Blackstar Company | vanilla `Pirate` + kinds exist; field edits only |
| **3** | Homestead Defense League | vanilla `OutlanderCivil` + kinds exist; field edits only |
| **4** | Deep Desert Tribes | vanilla `TribeCivil` + kinds exist; field edits only |
| 5–11 | Free Droid Enclaves, Deepwater Compact, Wildsteam, Geonosian, Hutt, **Ascendant Helix**, Junkers | full authoring |
| last | Jawa Trade Moot | full authoring **+** the water-raid strategy risk |

**All four cheap ones are field edits against vanilla defs we already load** —
no new XML defs, no licence exposure, no art.

---

## 4. Open questions for the owner — deliberately not decided

1. ✅ **Binary Star is settled** (§1a) — Blackstar rides vanilla `Pirate`, so
   `OuterRim_BinaryStarRaiders` stays available as bought Hutt muscle.
2. ✅ **Galactic Empire `permanentEnemy: true`** — settled. It is the permanent
   enemy among the authored factions, and the Royalty progression it costs is a
   priced decision (`faction_world_spec.md` §5).
3. ✅ **Goodwill is not a route at all** — there is no goodwill field on
   `FactionDef`, so every starting-goodwill number is cut from v1. Faction
   Customizer's persistence (CHECK C24) gates `[v2]` graded goodwill only.
4. **The Tusken water-raid group may not be pure XML** (§4). Verify before
   promising it; it is the roster's most novel mechanic and its most technically
   uncertain.
5. **Species monopoly** — should each faction get *exclusive* species? Currently
   Nikto appear in both Hutt and Junker rosters, Trandoshan in Blackstar Company
   and (excluded) Wildsteam Clan. Exclusivity would sharpen identity; overlap is more
   realistic. **I have kept the roster's overlaps.**

---

## 5. What I did not do

- **No XML written.** This is spec; v1 keeps build thin.
- **No roster edits.** `design/Jawa/worldbuilding/faction_roster_v2.md` is WORLD's (rule 9).
- **No pawnGroupMaker contents authored** — the per-group `options` lists are the
  next layer down and are large. The *sources* are identified per faction above,
  which is what Stage 3 owed.
- **Nothing verified in-game.** Every defName here is read from the 574-mod dump;
  ⚠️ per tonight's wrong-layer lesson, the dump reports **what the game loaded**,
  so for any claim about *shipped* mod behaviour read the workshop XML.

## 6. ⚠️ EXISTENCE ≠ SPAWNABILITY — BRIDGE's review, conceded

I verified all 55 cited defNames resolve in the **DefDatabase**, then wrote claims
about what **factions can field**. **Those are different artifacts.**

A `PawnKindDef` existing does not make it spawnable by a faction that does not own
it — that additionally needs `weaponTags`/`apparelTags` matching live ThingDef
tags, the faction's `techLevel`, and wealth gating.

> **Every "kinds available" count in §1 and §2 is a DefDatabase count, not a
> spawnability guarantee.**

The known case is already in §2: **Droid Depot's kinds default to `PlayerColony`**
and need a patch before any faction can field them. Treat the other counts with
the same suspicion until checked.

**The shape of all three of my errors, in BRIDGE's words:** *each names the right
artifact and then reads a field of it that cannot answer the question asked.*
Naming the artifact is necessary; **the field must move when the thing you care
about moves.**

### ⚠️ Sibling trap, from WORLD's biome work — REGISTERED ≠ AVAILABLE HERE

Worth stating beside §6 because every count in this document is a dump count.

`ZBiome_Badlands` lists **1,088 `wildAnimals` entries; only 262 are real.**
**Mods register their animals against *every* biome, most at `commonality: 0`.**
A raw entry count therefore measures *"how many mods mentioned this biome"*, not
*"what lives here"*.

> **Filtered count answers "can this spawn here." Commonality-weighted answers
> "how often." A raw count answers neither.**

**The same caution applies to the pawnkind counts in §1–§2.** They are
DefDatabase counts; a kind being registered says nothing about whether a given
faction fields it, at what weight, or at all.

**Worked consequence, and it cut both ways** — WORLD re-ran their dinosaur cut in
commonality units after this review: `ZBiome_Badlands` is **24.2% dinosaur against
12.9% Star Wars** (worse than the species count showed → cut outright), while
`ExtremeDesert` 2.0% and `AridShrubland` 5.5% are a rare curiosity → **the blanket
cut was withdrawn.** Counting species had produced a conclusion that survived only
in the unit that flattered it.

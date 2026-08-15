# FACTION_SPEC.md — the buildable faction layer

DECIDE owns this file. It is what BUILD executes. `faction_roster_v2.md` holds the
fiction and stays authoritative for tone and lore; **this file holds the engine
layer, and where they disagree about a FIELD, this file wins.**

Rulings R1–R15 live in `infrastructure/state/V1_CHAIN.md` and are not repeated
here. R16–R19 below are new and were made to unblock this spec.

## New rulings

**R16 · Authored factions REUSE an existing name maker for v1.**
A bespoke `RulePackDef` per faction is `[v2]`. This closes the "0 of 12 name
makers" gap outright — pick the closest shipped namer and move on. A faction with
a null `factionNameMaker` is the only unacceptable outcome.

**R17 · Authored factions REUSE an existing `factionIconPath` and
`colorSpectrum`.** Bespoke faction art is `[v2]`. Two factions sharing an icon is
a cosmetic defect; a missing icon is a broken faction screen.

**R18 · defNames are `Jawa_<Name>`.** That is already the mod's namespace for
non-Jawa content — `Jawa_Gamorrean_Guard`, `Jawa_SaltCrust`, `Jawa_TheClaim` — so
it is a namespace, not a claim about who the faction is. The 6 reskins get **no
new defName**; they are patches on the vanilla def.

**R19 · `Jawa_IndigenousTribes` IS the Jawa Trade Moot.** R8's rename table maps
"Indigenous Jawa Clans / the Duneborn" → "Jawa Trade Moot", and the shipped def
already carries `leaderTitle` **Prime Trader** and `ideoName` **The Salvation**.
⇒ **Keep the defName** — it is deployed, and renaming a live defName risks the
world and buys nothing — and **change the `label`** from "Jawa tribes".

## The 14 factions

| # | faction | defName | vessel | religion |
|---|---|---|---|---|
| 1 | Galactic Empire | *(patch)* `Empire` | **reskin** vanilla `Empire` + `OuterRim_Imp*` kinds (R15) | The Rising Order |
| 2 | Hutt Cartel | `Jawa_HuttCartel` | **authored** | the Reckoning of Debts |
| 3 | Homestead Defense League | *(patch)* `OutlanderCivil` | **reskin** | the Covenant of Free Wells |
| 4 | Deep Desert Tribes | *(patch)* `TribeCivil` | **reskin** | the Sun-Debt |
| 5 | Free Droid Enclaves | `Jawa_FreeDroidEnclaves` | **authored** — `OuterRim_RogueDroidColony` is an empty shell (R14) | the Continuity Protocol |
| 6 | Wildsteam Clan | `Jawa_WildsteamClan` | **authored** | the Green Oath |
| 7 | Deepwater Compact | `Jawa_DeepwaterCompact` | **authored** | the Balance |
| 8 | Geonosian Foundry Hive | `Jawa_GeonosianFoundryHive` | **authored** | Meckgin |
| 9 | Ascendant Helix | `Jawa_AscendantHelix` | **authored** — `Ancients` cannot host a faction (R9) | the Ascendant Genome |
| 10 | Blackstar Company | *(patch)* `Pirate` | **reskin** — keeps `permanentEnemy` (R12) | the Contract |
| 11 | Jawa Trade Moot | `Jawa_IndigenousTribes` | **authored — ALREADY SHIPS** (R19) | The Salvation *(shared with the player)* |
| 12 | the Junkers | `Jawa_Junkers` | **authored** | no doctrine, only the ladder |
| 13 | the Forgotten Arsenal | *(patch)* `Mechanoid` | **reskin**, label only — `hidden`, no settlements, no diplomacy | none |
| 14 | the Unbound Hive | *(patch)* `Insect` | **reskin**, label only | none |

**6 reskins · 8 authored, of which 1 already ships.** ⇒ **7 new `FactionDef`s.**

## What each kind of faction owes

### A reskin (6) — a `PatchOperation`, not a def
Patch only what changes the fiction. **Never touch `pawnGroupMakers` except for
the Empire (R15).** Everything else — group makers, name makers, icons, raid
curves — is inherited and already balanced.

```
label · description · pawnSingular · pawnsPlural · leaderTitle
fixedName            only where the world must say a specific name
permanentEnemy       only where it differs from the vessel's default
raidsForbidden       Homestead only (R2)
fixedIdeo + ideoName + ideoDescription + forcedMemes (+ deityPresets)
```

### An authored faction (7 new) — a full `FactionDef`
Model: `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`.
⚠️ **That model is itself incomplete** — it ships with no `humanlikeFaction`, no
`factionNameMaker`, no `settlementNameMaker`, no `factionIconPath`, no
`colorSpectrum` and no `basicMemberKind`. **Fix it to this contract too; it is
faction 11, not a template exempt from the rules.**

| group | fields | note |
|---|---|---|
| identity | `defName` `label` `description` `pawnSingular` `pawnsPlural` `leaderTitle` | all literal, all in this file |
| generation | `humanlikeFaction` `categoryTag` `techLevel` `settlementGenerationWeight` `maxCountAtGameStart` `canMakeRandomly` | |
| naming | `factionNameMaker` `settlementNameMaker` | **reuse a shipped namer** (R16) |
| art | `factionIconPath` `colorSpectrum` | **reuse** (R17) |
| hostility | one of `permanentEnemy` / `naturalEnemy` / `permanentEnemyToEveryoneExcept` / `raidsForbidden` | ⛔ **no goodwill number — the field does not exist** (R1) |
| pawns | `pawnGroupMakers` | must reference PawnKindDefs that **already exist**. `basicMemberKind` is **OPTIONAL** — set on only 30 of 87 live defs and on none of the six vanilla vessels |
| ideo | `fixedIdeo` `ideoName` `ideoDescription` `forcedMemes` (+ `deityPresets`) | text is the product |

## Per-faction detail

`settlementGenerationWeight` is scaled so **7 settlements = 1.0**, from the
dossiers' own counts. The RATIO is the design; the absolute numbers are a first
pass and tunable after one worldgen. `maxCountAtGameStart` is how many instances
of the faction exist, not how many settlements.

### 1 · Galactic Empire — PATCH vanilla `Empire`

```
label            The Galactic Empire
description      The occupier and the only permanent enemy - not hateful but
                 procedural. Standardised infantry, drop-pods, security droids,
                 rare Sith, and a reach that is mostly orbital.
pawnSingular     stormtrooper          pawnsPlural  stormtroopers
leaderTitle      Emperor                                          (R11)
fixedName        Galactic Empire       -- REQUIRED: NamerFactionEmpire would
                                          otherwise generate a random name
permanentEnemy   true                                             (pillar 5)
techLevel        Spacer                (vessel default, no change)
settlementGenerationWeight  0.45       -- 3 surface settlements BY DESIGN;
                                          the other 7-8 are orbital fiction
pawnGroupMakers  COMBAT groups only -> OuterRim_Imp* kinds        (R15)
                 leave Trader and Settlement groups untouched
fixedIdeo/ideoName  The Rising Order   -- deityPresets authored, spec entry 1
```
⚠️ Do NOT patch `factionNameMaker` away — `fixedName` overrides it for the
faction, and the namer is still used for settlements.

### 2 · Hutt Cartel — AUTHORED `Jawa_HuttCartel`

```
label       Hutt Cartel
description Wealthy, decentralised, transactional. Owns the oases and sells
            water at extortion rates, and holds the only non-Imperial orbital
            node - the door off-world.
pawnSingular Cartel enforcer   pawnsPlural Cartel enforcers
leaderTitle  Lord              techLevel Industrial   categoryTag Outlander
humanlikeFaction true    canMakeRandomly true   maxCountAtGameStart 1
settlementGenerationWeight 1.15        -- 8 settlements, all oasis tiles
permanentEnemy false · naturalEnemy false   -- hostile but negotiable
canRequestTraders true · high caravan frequency
ideoName  the Reckoning of Debts        -- spec entry 2, deityPresets authored
groups   Collection crew · Punitive raid · Deep-country escort ·
         Slave caravan · Water toll party · Elite retaliation
         ⚠️ a Hutt NEVER appears in a raid group - caravans, base defence and
            distress quests only. Exactly one Hutt or proxy per group.
```

### 3 · Homestead Defense League — PATCH vanilla `OutlanderCivil`

```
label        Homestead Defense League
description  The most numerous and least centralised faction - farmers on dry
             flats living off vaporator water. Decent, tired, badly armed.
pawnSingular moisture farmer   pawnsPlural moisture farmers
leaderTitle  High Marshal
raidsForbidden true                                (R2 - the mechanism, not a precept)
settlementGenerationWeight 1.9        -- 13 settlements, the most on the map
ideoName     the Covenant of Free Wells    -- Structure_TheistAbstract,
                                             deity "the Withdrawn"       (D2)
```

### 4 · Deep Desert Tribes — PATCH vanilla `TribeCivil`

```
label        Deep Desert Tribes
description  Territorial clans for whom water is sacred and moisture farming
             sacrilege. They arrive fast, hit hard, and are gone.
pawnSingular Tusken raider     pawnsPlural Tusken raiders
leaderTitle  War Chief
settlementGenerationWeight 1.3         -- 9, deep desert and canyons only
permanentEnemy false                   -- hostile, convertible via adoption
ideoName     the Sun-Debt
groups       inherits TribeCivil's 12 group makers.
             ADD ONE: the water raid - fast, light, targets containers and
             cisterns, disengages once loaded. It is the faction's signature
             and vanilla has no equivalent.
```

### 5 · Free Droid Enclaves — AUTHORED `Jawa_FreeDroidEnclaves`

```
label        Free Droid Enclaves
description  Battle droids abandoned after the war who woke up and decided they
             belong to themselves. They settle on water and crack it for fuel,
             so attackers arrive thirsty at a source they cannot drink.
pawnSingular droid            pawnsPlural droids
leaderTitle  First Speaker    techLevel Spacer     categoryTag Outlander
humanlikeFaction  🔴 MUST BE SET EXPLICITLY - load-bearing here    (R3)
settlementGenerationWeight 0.45        -- 3, on water tiles and remote ruins
permanentEnemy false · raids suppressed except post-goodwill-collapse retaliation
canRequestTraders true, very rare caravans
ideoName     the Continuity Protocol
             ⚠️ the religions spec flags this may not run if the droid race is
                not Humanlike. Settle that before authoring the ideo block.
groups       Technical caravan · Recovery team · Enclave defence ·
             Retaliation strike.  0% biological pawns. Never takes prisoners.
```

### 6 · Wildsteam Clan — AUTHORED `Jawa_WildsteamClan`

```
label        Wildsteam Clan
description  A forest people on the wrong planet, hard-sited to the few cool
             upland springs, holding a covenant that treats every living thing
             as kin. Devastating at home, near-useless anywhere else.
pawnSingular freehold warrior  pawnsPlural freehold warriors
leaderTitle  Elder             techLevel Industrial   categoryTag Outlander
settlementGenerationWeight 0.6         -- 4, wooded/upland/spring tiles
permanentEnemy false                   -- friendly ally
ideoName     the Green Oath
groups       Trade delegation · Rescue force · Freehold defence ·
             Liberation raid (hostile/slaver factions only)
             melee 45-60% of combat points, animals 5-15%
```

### 7 · Deepwater Compact — AUTHORED `Jawa_DeepwaterCompact`

```
label        Deepwater Compact
description  The amphibian peoples who live in the deep water and sell it to
             everyone, including the Empire hunting you. Their neutrality is a
             monopoly with teeth, and their wardens cannot follow you inland.
pawnSingular water warden     pawnsPlural water wardens
leaderTitle  High Warden      techLevel Industrial   categoryTag Outlander
settlementGenerationWeight 0.7         -- 5, holding every oasis and coast
raidsForbidden true                    -- wardens dehydrate off-water
ideoName     the Balance
             structure is SECULAR - this is what differentiates it from the
             Homestead's theist covenant                              (D2)
groups       Water caravan (trades with EVERY faction, Empire included) ·
             Reservoir patrol · Settlement defence · Purification expedition
```

### 8 · Geonosian Foundry Hive — AUTHORED `Jawa_GeonosianFoundryHive`

```
label        Geonosian Foundry Hive
description  A hive mass-producing droids in ancient factories under the rock,
             ruled by winged aristocrats under one immobile queen. The only
             power on the planet that can sustain a siege in deep desert.
pawnSingular warrior drone    pawnsPlural warrior drones
leaderTitle  Archduke         techLevel Spacer      categoryTag Outlander
humanlikeFaction  🔴 MUST BE SET EXPLICITLY                          (R3)
settlementGenerationWeight 0.7         -- 5, mountains/caves/ancient factories
permanentEnemy false                   -- hostile, high raid reach, sieges
canRequestTraders FALSE                -- no trade at all
xenotypeSet   Geonosian                -- the ONLY route; PreferredXenotype has
                                          no XML path                 (D3)
ideoName     Meckgin
groups       Drone swarm · Foundry assault · Deep-desert siege train ·
             Jedi-hunt detachment · Elite recovery unit
```

### 9 · Ascendant Helix — AUTHORED `Jawa_AscendantHelix`

```
label        Ascendant Helix
description  A small, obscenely wealthy gene-cult that believes the body is a
             rough draft and the species a project - and despises the
             manufactured underclass it made itself. It does not raid; it
             retrieves.
pawnSingular curator          pawnsPlural curators
leaderTitle  Director         techLevel Spacer      categoryTag Outlander
                              -- "Director" belongs HERE, not to the Empire (R11)
settlementGenerationWeight 0.45        -- 3, isolated and secure
permanentEnemy false                   -- neutral; retrieval ops, not raids
ideoName     the Ascendant Genome
🔴 AUTHORED, not a reskin: `Ancients` is hidden, settlementGenerationWeight 0,
   canMakeRandomly false. It cannot host a faction.                   (R9)
groups       Research caravan · Retrieval raid · Acquisition team ·
             Containment response · Settlement defence
```

### 10 · Blackstar Company — PATCH vanilla `Pirate`

```
label        Blackstar Company
description  Not a faction so much as one dangerous person with a name who is
             coming for you. Independent hunters bound by a professional code,
             taking contracts rather than pillaging.
pawnSingular hunter           pawnsPlural hunters
leaderTitle  Captain
permanentEnemy true   -- KEEP the vessel default. The dossier says No; R12
                         amends pillar 5 instead, because patching this false
                         would gut the vanilla raid economy.
settlementGenerationWeight 0.6         -- 4
ideoName     the Contract    -- deliberately NO Raider meme
```

### 11 · Jawa Trade Moot — `Jawa_IndigenousTribes` — ALREADY SHIPS, FIX IT

```
label        Jawa Trade Moot          🔴 CHANGE - currently reads "Jawa tribes",
                                         a name retired by R8
leaderTitle  Prime Trader             ✅ already correct
ideoName     The Salvation            ✅ already correct, shared with the player
techLevel    Neolithic  categoryTag Tribal  settlementGenerationWeight 1.0 (7)
maxCountAtGameStart 2                 ✅ already set

🔴 MISSING and required by the contract:
   humanlikeFaction · factionNameMaker · settlementNameMaker ·
   factionIconPath · colorSpectrum · basicMemberKind
```

### 12 · the Junkers — AUTHORED `Jawa_Junkers`

```
label        the Junkers
description  The bottom of the scrap heap given weapons and a grudge.
             Scavengers who arrive second and kill whoever arrived first,
             welded into warcaskets cut off other people's bodies.
pawnSingular Junker           pawnsPlural Junkers     -- the only dossier that
                                                         states these outright
leaderTitle  Scraplord        techLevel Industrial   categoryTag Pirate
settlementGenerationWeight 1.15        -- 8, wreck fields and tailings
permanentEnemy FALSE          -- owner's ruling; they are authored, so pillar 5
                                 binds them (R12). Hostile on sight, bribable.
canRequestTraders FALSE       -- no caravans. A loot source, not a market.
ideoName     The Weight       -- no doctrine, only the ladder
groups       Casket Line · Warren Boss · Casket-Wright · Scrap-Runner ·
             Broken-Fang · Cartel Scout (rare)
```

### 13 · the Forgotten Arsenal — PATCH vanilla `Mechanoid`, LABEL ONLY

```
label / description only. No leader, no settlements, no diplomacy, no ideo.
`hidden true` and settlementGenerationWeight 0 are CORRECT and stay.
Inherits vanilla pawnGroupMakers wholesale. Do not touch anything else.
```

### 14 · the Unbound Hive — PATCH vanilla `Insect`, LABEL ONLY

```
label / description only. Same treatment. Named to distinguish it from the
Geonosian Foundry, which is the authored insectoid faction.
```

## Hard-coded relations

`permanentEnemyToEveryoneExcept` is the only list-shaped relation field, so
most of these are FICTION ONLY in v1 and must not be specced as engine state:

| stated in the dossiers | v1 status |
|---|---|
| Homestead ↔ Deep Desert Tribes hostile | fiction |
| Wildsteam hostile to Hutt / Blackstar / Empire | fiction |
| Jawa Trade Moot hostile to Junkers | fiction |
| Geonosian hostile to the Empire | fiction |
| Free Droid hostile to Junkers | fiction |

⛔ **Do not invent a mechanism for these.** Inter-faction goodwill is not a
`FactionDef` field any more than player goodwill is (R1). They are `[v2]`,
gated on the same Faction Customizer question as CHECK C24.

## Standing constraints

- **Every `<li>` naming a def from another mod needs the right `MayRequire`.** An
  unwrapped defName from a disabled mod is a silent no-op, and
  `validate_ideoligion.py` only reports it as INFO.
- **`pawnGroupMakers` options must name kinds that resolve in the live dump.**
  An invented kind name is the single most likely way this spec fails silently.
- **Ideo text is the deliverable.** `ideoName`, `ideoDescription` and the deity
  name/type pairs are the only strings the engine renders; 9 of 11 entries in
  `faction_religions_spec.md` still have none.

## The pawn layer — measured, and it forces a ruling

**R20 · Donor kinds are FLAT SPECIES kinds. Role differentiation does not exist
and must be authored.** Measured across 1,766 `PawnKindDef`s in the live dump:
every Galactic Diversity kind is a single entry per species at `combatPower 40`
— `OuterRim_Nikto`, `OuterRim_Wookiee`, `OuterRim_Geonosian`, `OuterRim_Quarren`,
`OuterRim_Arkanian`. There is no Nikto lieutenant, no Wookiee elite, no Quarren
specialist. Counts by theme:

| theme | kinds | note |
|---|---|---|
| Hutt / Nikto / Gamorrean | 5 | **Weequay ZERO** — the dossier's 16% has no kind |
| droid | 77 | the one rich seam |
| Wookiee | 2 | |
| Mon Cal / Quarren | 4 | |
| Geonosian | 2 | |
| Arkanian / Kaminoan | 4 | |
| scavenger / scrapper | 17 | **"junker" ZERO** — generic scavengers from 6 mods |

⇒ **The dossiers' group compositions cannot be built from donors alone.**
"Lieutenant, 4–8 Nikto levies, 2 Gamorreans" needs three kinds where the dump
offers one. **The 48 kinds in `pawnkind_roster.md` are therefore REQUIRED, not
optional** — this is chain step 7 and it is real work.

**⇒ v1 ships factions against FLAT kinds now, and upgrades them when the 48
land.** A faction referencing `OuterRim_Nikto` five times is undifferentiated but
correct, spawns, and closes the row. Waiting for 48 pawn kinds before any faction
exists would put the whole faction layer behind step 7. This is the "everything
ships THIN" doctrine applied exactly where it was meant to apply.

### 🪤 Three traps the dump settles

1. **`combatPower 99999` is the exclude-from-raid sentinel.** Eight Droid Depot
   civilian kinds carry it. Legal in `traders` / `carriers` / `guards`; putting
   one in `options` poisons the group.
2. **`minTotalPoints` DOES NOT EXIST.** Zero occurrences across 404 group makers.
   Every one has exactly `kindDef · commonality · maxTotalPoints · options ·
   traders · carriers · guards`.
3. **`PawnGenOption` has exactly two keys** — `kind` and `selectionWeight`.
   Nothing else, across all 3,150 instances.

Legal `kindDef` values: `Combat` · `Settlement` · `Peaceful` · `Trader` ·
`Miners` · `Hunters` · `Loggers` · `Farmers` · `Settlement_RangedOnly`.

### Namers and icons — the R16/R17 assignments

🔴 **There are ZERO Star Wars faction namers in the whole 585-mod set.** Reuse
means vanilla namers, which will generate non-Star-Wars settlement names. That is
a real and visible fiction cost, accepted for v1; bespoke `RulePackDef`s are the
first `[v2]` item off this spec.

| faction | factionNameMaker | settlementNameMaker | factionIconPath |
|---|---|---|---|
| Hutt Cartel | `NamerFactionOutlander` | `NamerSettlementOutlander` | `World/WorldObjects/Expanding/Town` |
| Free Droid Enclaves | `NamerFactionOutlander` | `NamerSettlementOutlander` | ⭐ `World/RogueDroids` |
| Wildsteam Clan | `NamerFactionTribal` | `NamerSettlementTribal` | `.../Expanding/VillageSavage` |
| Deepwater Compact | `NamerFactionOutlander` | `NamerSettlementOutlander` | `.../Expanding/Village` |
| Geonosian Foundry Hive | `NamerFactionTribal` | `NamerSettlementTribal` | ⭐ `.../Expanding/Insects` |
| Ascendant Helix | `NamerFactionEmpire` | `NamerSettlementEmpire` | `.../Expanding/Empire` |
| the Junkers | `NamerFactionSalvagers` | `NamerSettlementPirate` | ⭐⭐ `UI/FactionIcons/JunkersOutpost` |
| Jawa Trade Moot | `NamerFactionTribal` | `NamerSettlementTribal` | `OuterRim/WorldObjects/MoistureFarmers` |

⚠️ Vanilla ships a typo, `NamerSettlementTribalNeaderthal` (no second "n"). If
you ever reach for it, copy it exactly.

### `pawnGroupMakers` — kinds that resolve today

Every defName below was verified present in the 2026-08-14 dump. Weights are a
first pass; the shape is the design.

```
Jawa_HuttCartel
  Combat    OuterRim_Nikto 10 · OuterRim_NiktoTribal 6 ·
            Jawa_Gamorrean_Guard 4 · Jawa_Gamorrean_Enforcer 1
  Trader    traders: OuterRim_Nikto · guards: Jawa_Gamorrean_Guard 6,
            Jawa_Gamorrean_Enforcer 2 · carriers: Bantha, Dewback
  Settlement OuterRim_Nikto 8 · Jawa_Gamorrean_Guard 4 · Jawa_Spawn_Hutt 1
  🔴 Jawa_Spawn_Hutt appears ONLY here and in Trader guards. Never in Combat.

Jawa_FreeDroidEnclaves
  Combat    OuterRim_EscapedBattleDroid 8 · OuterRim_BattleDroid 6 ·
            OuterRim_SuperBattleDroid 3 · OuterRim_CommandoDroid 2 ·
            OuterRim_MagnaGuardDroid 1 · OuterRim_TacticalDroid 1
  Trader    traders: OuterRim_ProtocolDroid · guards: OuterRim_KXSecurityDroid
  Settlement OuterRim_BattleDroid 6 · OuterRim_SuperBattleDroid 2
  ⚠️ OuterRim_GNKDroid / _MSEDroid / _FX7Droid are cp 99999 — carriers/guards ONLY.

Jawa_WildsteamClan
  Combat    OuterRim_Wookiee 10 · OuterRim_WookieeTribal 8      -- only 2 exist
  Trader    traders: OuterRim_Wookiee · carriers: Muffalo, Bantha
  Settlement OuterRim_WookieeTribal 10 · OuterRim_Wookiee 5

Jawa_DeepwaterCompact
  Combat    OuterRim_Quarren 10 · OuterRim_MonCalamari 8 ·
            OuterRim_QuarrenTribal 4
  Trader    traders: OuterRim_MonCalamari · guards: OuterRim_Quarren
  Settlement OuterRim_MonCalamari 8 · OuterRim_Quarren 8
  ⛔ NO Combat group reaches the player - raidsForbidden true. Keep the group
     anyway for settlement defence.

Jawa_GeonosianFoundryHive
  Combat    OuterRim_Geonosian 10 · OuterRim_GeonosianTribal 6 ·
            JDSCIS_B1_Battle_Droid 8 · JDSCIS_B2_Super_Battle_Droid 3 ·
            JDSCIS_Droideka_Droid 1 · JDSCIS_T1_Tactical_Droid 1
  Settlement OuterRim_Geonosian 10 · JDSCIS_B1_Battle_Droid 6
  NO Trader group - canRequestTraders false.

Jawa_AscendantHelix
  Combat    OuterRim_Arkanian 8 · OuterRim_Kaminoan 4 ·
            OuterRim_ArkanianTribal 2
  Trader    traders: OuterRim_Kaminoan · guards: OuterRim_Arkanian
  Settlement OuterRim_Arkanian 8 · OuterRim_Kaminoan 6

Jawa_Junkers
  Combat    Jawa_Gamorrean_Guard 10 · Jawa_Gamorrean_Enforcer 3 ·
            OuterRim_Scavenger 6 · OuterRim_Thrasher 6 ·
            VFEP_Scrapper 4 · Scavenger 3 · Thrasher 3
  Settlement Jawa_Gamorrean_Guard 8 · OuterRim_Scavenger 5
  NO Trader group - canRequestTraders false, they are a loot source.
  ⭐ Gamorrean-led matches the dossier's 26% Gamorrean composition exactly.

Jawa_IndigenousTribes  (already ships - verify these still resolve)
  Combat/Trader/Settlement over Jawa_Tribal_Scavenger · _Slinger · _Elder
  🔴 the shipped groups reference vanilla Combat/Peaceful/Trader kindDefs;
     confirm the OPTIONS name our kinds and not vanilla ones.
```

**Not expressible from donors, and deliberately dropped from v1:** Weequay (no
kind exists), Trandoshan/Rodian/Aqualish/Snivvian role splits, the Junker
warcasket tiers, the Hutt "proxy" distinction, and every lieutenant/champion/
specialist rank. All of them return with the 48 authored kinds.

## Three things that would otherwise bounce an item

**R21 · `basicMemberKind` is OPTIONAL. Omit it.** Measured: set on 30 of 87 live
`FactionDef`s and on **none** of `Empire`, `OutlanderCivil`, `TribeCivil`,
`Pirate`, `Insect` or `Mechanoid`. The contract over-specified it. Do not invent
a value; the group makers carry the composition.

**R22 · `colorSpectrum` — literal values, assigned here.** It is set on 76 of 87
live defs, so a faction without one looks broken on the world map. These are the
v1 values; they are a design call, not a placeholder, and they read against
desert terrain.

| faction | colorSpectrum |
|---|---|
| Hutt Cartel | `(0.72,0.62,0.25)` `(0.58,0.48,0.18)` — sickly gold |
| Free Droid Enclaves | `(0.55,0.62,0.70)` `(0.40,0.48,0.58)` — cold steel |
| Wildsteam Clan | `(0.30,0.45,0.25)` `(0.22,0.34,0.18)` — deep green |
| Deepwater Compact | `(0.20,0.55,0.58)` `(0.14,0.40,0.45)` — teal |
| Geonosian Foundry Hive | `(0.65,0.35,0.18)` `(0.48,0.25,0.12)` — rust |
| Ascendant Helix | `(0.78,0.74,0.85)` `(0.62,0.58,0.72)` — pale violet |
| the Junkers | `(0.55,0.35,0.20)` `(0.38,0.24,0.14)` — scrap brown |
| Jawa Trade Moot | `(0.70,0.55,0.30)` `(0.52,0.40,0.20)` — sand, with the ember |

The six reskins keep their vessel's spectrum. Do not patch it.

**R23 · BUILD THE FACTION WITHOUT ITS IDEO BLOCK. The ideo lands second.**
Chain step 9 formally needs step 6, and **9 of 11 faiths have no
`ideoDescription`** — so a strict reading blocks every authored faction behind a
writing task. It does not have to: `fixedIdeo` / `ideoName` / `ideoDescription` /
`forcedMemes` / `deityPresets` are OPTIONAL fields. A faction shipped without
them generates an ideo at worldgen and works.

⇒ **Ship the 13 step-9 items now with the ideo group OMITTED**, and add it in one
pass when D18 delivers the text.
🔴 **The ideo block MUST land before the worldgen click (chain step 10).** An ideo
is generated once, at world creation, and a `fixedIdeo` added afterwards does not
retrofit an existing world. This is the one hard deadline on D18.

⛔ **Exception — the three faiths that already have their text ship WITH it:**
the Galactic Empire (The Rising Order), the Hutt Cartel (the Reckoning of Debts),
and the Jawa Trade Moot (The Salvation, already in the shipped def). Those three
carry authored `deityPresets` and there is no reason to defer them.

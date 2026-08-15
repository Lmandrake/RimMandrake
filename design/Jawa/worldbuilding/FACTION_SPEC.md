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
| pawns | `basicMemberKind` · `pawnGroupMakers` | must reference PawnKindDefs that **already exist** |
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

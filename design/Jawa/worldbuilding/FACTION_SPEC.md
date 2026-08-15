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

*(Filled from the dossier extraction and the pawn-kind census — see the sections
below. Anything still reading TBD is not releasable to BUILD.)*

## Standing constraints

- **Every `<li>` naming a def from another mod needs the right `MayRequire`.** An
  unwrapped defName from a disabled mod is a silent no-op, and
  `validate_ideoligion.py` only reports it as INFO.
- **`pawnGroupMakers` options must name kinds that resolve in the live dump.**
  An invented kind name is the single most likely way this spec fails silently.
- **Ideo text is the deliverable.** `ideoName`, `ideoDescription` and the deity
  name/type pairs are the only strings the engine renders; 9 of 11 entries in
  `faction_religions_spec.md` still have none.

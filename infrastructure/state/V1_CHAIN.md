# V1_CHAIN.md — what v1 is, in the order the engine forces

DECIDE owns this file. It is the content half of v1. `V1.md` is the eight-row
scoreboard; **this is the dependency graph underneath it**, and where the two
disagree about scope, this file is newer.

## Owner's rulings, 2026-08-14

1. **v1 = the 8 rows + the FULL faction roster + one playable session.**
2. **Row 4 is closed.** Scrapfields ships at whatever density it produces; the
   count is `[v2]`.
3. **Row 3 is reopened.** Registration is not resolution — the quest must reach
   an end state.
4. **The playable session has a four-part gate** (§ Act 5).
5. **The head of the chain is four steps, in this order:** freeze the mods →
   cherrypick out unwanted items → normalize weapons / armour / beasts →
   assign equipment types to the pawns.
6. 🔴 **WORLDGEN IS MANUAL AND IT IS THE OWNER'S.** *"I will manually make a world
   and save it. Then we will use it as a resource we simply enable. Let's not try
   to solve automated worldbuilding at this time in v1."*
   ⇒ **The sea is OUT of v1** — `JawaSeaShaper`, the 5-part sea gate, the seed
   sweep and the ocean-percentage problem all move to `V2_DREAMS.md`. The owner
   picks a world he likes by eye.
   ⇒ **THE DEADLINE INVERTS.** Every `FactionDef` and every ideo block must exist
   and be DEPLOYED *before the owner sits down to make that world*, because
   factions and ideos are read once at world creation. This is no longer an
   abstract "before the worldgen click" — it is before a human event we do not
   schedule.
7. **The item cherrypick (step 1) is deferred to an interactive session with the
   owner.** Do not block on it. Author against the item set as it stands today
   and revise if the cherrypick later removes something.
8. **The scenario is FIXED, not generated** — fixed map, fixed ship, fixed pawns.

### DECIDE rulings made against those

- **The vessel column is ruled and measured — see R9, R14 and R15.**
  `faction_stage3_buildable_spec.md` is stale wherever it assigns a vessel; the
  world spec's vanilla column wins **except for `Ancients`, which cannot host a
  faction at all**.

## The chain

A def can only reference something that already exists. That is the whole reason
for this order; it is not a preference.

| # | domain | needs | state |
|---|---|---|---|
| 0 | **Mod freeze** | — | ✅ done — 584 active, two files frozen |
| 1 | **Item cherrypick** | 0 | **deferred — interactive session with the owner. Do not block.** |
| 2 | **Normalize weapons · armour · beasts** | 1 | open — balance pass over what survives |
| 3 | **Equipment types → pawns** | 2 | open — the tags a `PawnKindDef` actually consumes |
| 4 | **Xenotypes** | — | enforced in shipped XML (`ea5cfb4`), **not yet proven live** — this process read the broken copies at launch |
| 5 | **Droids** | 0, 4 | taxonomy ruled; pawn track unbuilt; NRE route open |
| 6 | **Religions** | — | ✅ text written and DEPLOYED for all 11. §12 is the owner's |
| 7 | **Pawntypes** | 3, 4, 5 | 48 proposed, 0 literal defNames. 19 ship, none matching |
| 8 | **Biomes** | 2 | ✅ ratified (W3) |
| 9 | **Factions** | 6, 7 | ✅ 5 reskins + 8 authored, all BUILT AND DEPLOYED |
| 10 | **Worldmap** | 9 | 🔴 **MANUAL — the owner makes and saves it.** Blocked on step 9 shipping first |
| 11 | **Gravship** | 2 | ✅ built and exported |
| 12 | **Scenario** | 2, 7, 11 | specced — `SCENARIO_SPEC.md`. Waits on the owner's world |
| 13 | **Quests** | 9 | row 3 reopened on resolution |

🔴 **Everything through 9 is upstream of 10, and 10 cannot be redone.** A
`FactionDef` that does not exist at world creation never gets settlements.

**0 → 1 → 2 → 3 is a single unbroken run and it is the head of all of v1.**
Nothing in 5–13 can be authored honestly until 3 lands, because every one of them
either equips a pawn or references something 1 might cut.

## Per domain

### 0 · Mod freeze — reversible, do it first
Cutting a mod deletes defs and takes its tags with it, so every downstream
decision made first is invalidated. Prefer reversible suppression (ModsConfig,
zeroing generation weights, clearing `designationCategory`) over def culls.

**THE FROZEN BASELINE — measured 2026-08-14, and there is no drift.**

```
activeMods in ModsConfig.xml   585
loaded by the game             585
listed but not installed         0
loaded but not listed            0
sources        564 workshop · 15 local · 6 Core+DLC
```

⇒ **These 585 ARE the frozen set — owner's ruling, 2026-08-14.** A mod ships
unless it is explicitly cut. The freeze is not an audit of 585 mods; it is a
reconciliation of the decision docs against this list, and only the divergences
need a ruling.

🔴 **The freeze is TWO files, not one.** Cherry Picker runs at load order 11 and
deletes defs the mod list still contains, so `ModsConfig.xml` alone leaves half
the def universe undefined. Both are frozen at
`deployed/config/v1_freeze/` — see its README. Two of the owner's gene picks
had gone missing from the live Cherry Picker config and are restored (24 keys).

**Seven tooling mods stay in**, deliberately, and are recorded as tooling:
Better Stacktraces · Cherry Picker · Character Editor + retexture · Slower Pawn
Tick Rate · Dubs Performance Analyzer · Performance Optimizer · RimDefDump.

**The 624 installed-but-inactive mods are OUT OF SCOPE** — owner's ruling,
2026-08-14. Do not sweep them and do not file an item to. They remain available
as a RESEARCH reference — "does a mod already do X" is a fair question to answer
against them — but nothing in them is v1 work.
**Load ORDER is not pinned** (B25a); that one is still open.

**Two claimed contradictions, both settled:**
- `lee.theforce.lightsaber` "active but not installed" is **false** — it is
  active and loaded ("Star Wars : The Force - Lightsaber"). The note in
  `cherrypick_inbox.md` is stale.
- KotOR is **fully present** — `guy762.mm.kotorcore`, `guy762.kotorweapons`,
  `guy762.kotordroids`, `btd.gbp.shippack.kotor.vge`. ⇒ **KotOR is KEPT**, and
  `required_mods.md`'s "DECLINE for the lean stack" is the stale side. This
  matters: `guy762.kotorweapons` is the single largest entry in
  `armoury_keeplist.md` at 137 weapons.

### 3 · Equipment types → pawns — the artifact that was never written
A `PawnKindDef` consumes `weaponTags`, `apparelTags` and a few literal
`apparelRequired` defNames. **It does not consume a per-item verdict**, which is
why the 674-weapon keeplist was never the blocker. `pawnkind_roster.md` declined
to invent tag values on purpose. What is owed: the actual tag strings carried by
the surviving weapon and apparel defs, read out of the live dump.

### 6 · Religions
✅ **All eleven carry `ideoName`, `ideoDescription`, `forcedMemes` and
`requiredPreceptsOnly` as literal XML, and are deployed.** Section 12 (Jawa) is
deliberately empty and stays that way: the player faith ships as
`src/Jawa/ideoligion/The Salvation.rid`.

### 7 · Pawntypes
48 kinds proposed (12 factions × Grunt/Heavy/Specialist/Leader), zero literal
defNames, `combatPower` unset on all of them. 19 PawnKindDefs ship and none
match the roster.
🔴 **`Jawa_Colonist` has no `weaponTags` and no `apparelRequired`.** The Jawa
robe-and-hood lock exists in the repo but was applied to a **donor** kind
(`OuterRim_Jawa`) and never mirrored onto ours.

### 9 · Factions
`Jawa_IndigenousTribes` is the model of done — `pawnGroupMakers`, `xenotypeSet`,
`forcedMemes`, `fixedIdeo`, and its three referenced kinds exist. Author the
8 authored factions against it; the 6 reskins are patches (R14).

**One gap survives the rulings below: not one faction has a defName.** Everything
else that was open — the 12/14 count, the vessel column, goodwill, the leader
titles, D1–D6 — is ruled in R1–R15 and must not be re-opened from the roster.

### 9 · Factions — DECIDE's rulings, 2026-08-14

Read out of the live dump's complete `FactionDef` field set (87 defs, captured
2026-08-14T21:10Z). These are engine facts, not preferences.

**R1 · Starting goodwill is not authorable. The 12 numbers are cut from v1.**
There is **no goodwill field on `FactionDef`.** The entire relation vocabulary is
`permanentEnemy` · `naturalEnemy` · `mustStartOneEnemy` ·
`permanentEnemyToEveryoneExcept` · `permanentEnemyToEveryoneExceptPlayer` ·
`hostileToFactionlessHumanlikes`. ⇒ `faction_roster_v2.md:42` is wrong and every
number it authorised is unbuildable. v1 expresses hostility through those six and
nothing else. Graded goodwill is `[v2]` and gated on Faction Customizer
persistence (CHECK C24).

**R2 · The Homestead's "never raids" is `raidsForbidden`, not a precept.**
The field exists. Use it. `VME_Raiding_Abhorrent` may stay as flavour but is not
the mechanism, and the roster's "never raid (Rw 0)" vs "Very low" contradiction
resolves to `raidsForbidden: true`.

**R3 · `humanlikeFaction` must be set explicitly on every faction.** It exists
and it is load-bearing for Geonosian and the Free Droid Enclaves, both of which
the audit flagged and no dossier mentions.

**R4 · `leaderTitle` is a real field**, so the three live leader titles are a
naming choice, not a mechanism problem.

**R5 · The vessel swap has a first-class field — `replacesFaction`.** Prefer it
to a label patch wherever we are truly replacing a vanilla faction rather than
dressing one.

**R6 · Unproven foundation.** `Jawa_IndigenousTribes` is absent from the live
dump because the game launched at 01:03:26 and the def deployed at 01:13 — the
running process never read it. Disk is correct, repo and deployed are
md5-identical. **It has still never been loaded, and it is the template for the
other 11–13.** It goes on the next cold load's verification list before anyone
authors against it.

**R7 · 12 versus 14 was never a conflict — both counts are right.**
The roster counts *dossiers* (12). `faction_world_spec.md` counts *factions on the
map* (14): the same 12, plus the Forgotten Arsenal and the Unbound Hive, which
are label reskins of vanilla `Mechanoid` and `Insect`. Both are described as
having no leader, no settlements and no diplomacy, so they inherit vanilla's
`pawnGroupMakers` wholesale. ⇒ **They cost two label patches, not two dossiers.**
Authoring load stays at 12.

**R8 · `faction_world_spec.md`'s names are canon.** Its rename table at `:110-123`
stands, and the roster's own dossier headings already use 6 of the 8. Fix the
roster's stale species table (Aquifer / Bounty / Wookiee). Zero design cost.

**R9 · The vessel column, measured against the live dump — 6 of 7 work.**

| faction | vessel | verdict |
|---|---|---|
| Galactic Empire | `Empire` | ✅ `hidden false`, settles |
| Homestead Defense League | `OutlanderCivil` | ✅ |
| Deep Desert Tribes | `TribeCivil` | ✅ |
| Blackstar Company | `Pirate` | ✅ — but see R12 |
| Forgotten Arsenal | `Mechanoid` | ✅ `hidden true`, no settlements — which is the intent |
| Unbound Hive | `Insect` | ✅ |
| **Ascendant Helix** | `Ancients` | 🔴 **IMPOSSIBLE** |

🔴 **`Ancients` is `hidden: true`, `settlementGenerationWeight: 0`,
`maxCountAtGameStart: 0`, `canMakeRandomly: false`.** It cannot settle, cannot
appear in the faction list and cannot be diplomatic. The spec's own fallback
takes effect: **the Ascendant Helix is authored from scratch.** Authored count
goes 7 → 8. Do not book a feasibility check; it is answered.

**R10 · The shipped Empire patch is on the wrong vessel.**
`Jawa_Patches/Patches/ImperialDesertDirectorate.xml` targets
`OuterRim_GalacticEmpire`, a mod def. R9 and `WORLDGEN_FACTION_CHECKLIST` R3 both
put the Galactic Empire on vanilla `Empire`. ⇒ **Re-point the patch.**
⚠️ **Consequence: v1 row 1 was closed on a label seen live on a vessel we are
abandoning. It has to be redone.** Cheap, but it is not already done.

**R11 · Leader titles — one faction had three, and the spec already killed two.**
**Galactic Empire → `Emperor`** (canon, spec `:85`, roster `:584`; "Sector
governor" is explicitly retired). **Ascendant Helix → `Director`** — the spec
`:106-108` strikes "Sector Director" from the Empire and gives the word to the
Helix. The shipped patch's `Sector Director` dies with R10 anyway. Update the
roster's ritual text at `:610` and `:612`, which still uses it.

**R12 · Pillar 5 is amended: "one permanent enemy among the AUTHORED factions."**
Vanilla `Pirate` ships `permanentEnemy: true` and Blackstar Company reskins it.
Patching that false would gut the vanilla raid economy for no gain. ⇒ Blackstar
keeps it, the Galactic Empire is the authored permanent enemy, and the two are
not in conflict. **The Junkers still lose theirs** (they are authored) — BUILD B9
stands.

**R13 · The six stage-2 defects, disposed.**
- **D1** Homestead raid frequency → `raidsForbidden: true` per R2. "Very low" is struck.
- **D2** Homestead structure either/or → `Structure_TheistAbstract`, deity *the
  Withdrawn*. This also differentiates it from the Deepwater Compact, which is
  secular — the 24% Jaccard complaint is answered by the split, not by a cut.
- **D3** Geonosian → there is **no XML route to `PreferredXenotype`**. Retarget to
  the `xenotypeSet` field on the `FactionDef` (it exists) plus `PawnKindDef`
  xenotype chances. The precept ambition is dropped.
- **D4** Delete the stale dry-capable rows. **Kaleesh only.**
- **D5** "ten NPC factions" → **twelve**. Two lines.
- **D6** → resolved by R12.

**R14 · A reskin inherits its `pawnGroupMakers` and its name maker. Only the
AUTHORED factions owe them.** Measured across every candidate vessel:

| vessel | settleW | groupMakers | nameMaker |
|---|---|---|---|
| `Empire` | 1 | 5 | `NamerFactionEmpire` |
| `OuterRim_GalacticEmpire` | 0.3 | 12 | **none** |
| `OutlanderCivil` | 1 | 8 | `NamerFactionOutlander` |
| `TribeCivil` | 1 | 12 | `NamerFactionTribal` |
| `Pirate` | 1 | 8 | `NamerFactionPirate` |
| `OuterRim_RogueDroidColony` | **0** | **0** | none — an empty shell |

⇒ **The "#1 blocker" and "0 of 12 name makers" apply to 8 factions, not 12.**
The 6 reskins get both free. `OuterRim_RogueDroidColony` brings nothing, so the
**Free Droid Enclaves is AUTHORED** — now measured, not inferred.

**R15 · The Galactic Empire takes vanilla `Empire` as its vessel AND the Outer
Rim Imperial pawn kinds as its troops.** Neither document proposed this and it
is strictly better than either half:

- vanilla `Empire` keeps `settlementGenerationWeight 1` (against 0.3, which is
  why the Directorate held 1 settlement to the Fallen Dominion's 4) and a working
  `NamerFactionEmpire`, and it satisfies the ratified checklist R3.
- its combat kinds are `Empire_Fighter_Cataphract` / `Janissary` / `Champion` —
  Royalty's medieval imperials, wrong for this campaign.
- `OuterRim_GalacticEmpire` ships `OuterRim_ImpDeathTrooper`, `ImpISBAgent`,
  `ImpRangeTrooper`, `ImpStormArty`, `ImpStormIncinerator`, `ImpStormJump`.

⇒ **Patch vanilla `Empire`'s combat `pawnGroupMakers` options to the
`OuterRim_Imp*` kinds.** Both mods are active, so they resolve. Keep the
`fixedName` patch — `NamerFactionEmpire` would otherwise generate a random name
and the world must say *Galactic Empire*.

### The buildable `FactionDef` contract

Every faction owes all of this. A dossier missing any line is not releasable to
BUILD. `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml` is the worked
example.

| group | fields |
|---|---|
| identity | `defName` `label` `description` `pawnSingular` `pawnsPlural` `leaderTitle` |
| art | `factionIconPath` `colorSpectrum` `settlementTexturePath` |
| naming | `factionNameMaker` `settlementNameMaker` — **owed by the 8 authored only; reskins inherit (R14)** |
| generation | `humanlikeFaction` `categoryTag` `techLevel` `settlementGenerationWeight` `maxCountAtGameStart` `canMakeRandomly` |
| hostility | one of `permanentEnemy` / `naturalEnemy` / `permanentEnemyToEveryoneExcept` / `raidsForbidden` |
| pawns | `basicMemberKind` · `pawnGroupMakers` with `options` and weights — **owed by the 8 AUTHORED factions only; the 6 reskins inherit them (R14)** |
| ideo | `fixedIdeo` + `ideoName` + `ideoDescription` + `forcedMemes` (+ `deityPresets` where the faith has deities) |
| optional | `apparelStuffFilter` `backstoryFilters` `xenotypeSet` `raidCommonalityFromPointsCurve` `disallowedRaidStrategies` `styles` |

### 12 · Scenario — the hole
No document. It is the first thing the player touches: starting pawns, starting
gear, the ship, the landing.

## Act 5 — the playable session

The owner's gate, four parts, all four required:

1. One in-game day with no red errors in the log.
2. Pawns eat, sleep, haul and work — no stuck jobs, no pathing deadlock.
3. The clan reads as Jawas on a desert world. ⚠️ **Taste. The owner's eyes are
   the instrument — do not fake a call for it.**
4. One save / reload round trip without loss.

Anything found in act 5 that is not one of these four is `[v2]`.

## What this file supersedes

`faction_stage3_buildable_spec.md` on the vessel column.

# V1_CHAIN.md — what v1 is, in the order the engine forces

DECIDE owns this file. It is the content half of v1. `V1.md` is the eight-row
scoreboard; **this is the dependency graph underneath it**, and where the two
disagree about scope, this file is newer.

## Owner's rulings, 2026-08-14

1. **v1 = the 8 rows + the FULL faction roster + one playable session.**
   ⚠️ This **supersedes `V1_SCOPE.md`**, which defers the 11 dossiers,
   `pawnGroupMakers` and the ideoligions to v2. They are v1. The cost was stated
   and accepted.
2. **Row 4 is closed.** Scrapfields ships at whatever density it produces; the
   count is `[v2]`.
3. **Row 3 is reopened.** Registration is not resolution — the quest must reach
   an end state.
4. **The playable session has a four-part gate** (§ Act 5).
5. **The head of the chain is four steps, in this order:** freeze the mods →
   cherrypick out unwanted items → normalize weapons / armour / beasts →
   assign equipment types to the pawns.

### DECIDE rulings made against those

- **The vessel is vanilla `Empire`.** `WORLDGEN_FACTION_CHECKLIST.md` R3 is
  ratified and says so; `faction_stage3_buildable_spec.md` says patch
  `OuterRim_GalacticEmpire` and is older and unratified. Stage 3 is stale on this
  point and everywhere it repeats the pattern (Homestead, Tribes, Pirates,
  Ancients — the world spec's vanilla column wins).

## The chain

A def can only reference something that already exists. That is the whole reason
for this order; it is not a preference.

| # | domain | needs | state |
|---|---|---|---|
| 0 | **Mod freeze** | — | open — the gate on everything |
| 1 | **Item cherrypick** | 0 | open — cut what the campaign does not permit |
| 2 | **Normalize weapons · armour · beasts** | 1 | open — balance pass over what survives |
| 3 | **Equipment types → pawns** | 2 | open — the tags a `PawnKindDef` actually consumes |
| 4 | **Xenotypes** | — | ✅ done — `MandrakeJawa` enforced in shipped XML |
| 5 | **Droids** | 0, 4 | taxonomy ruled; pawn track unbuilt; NRE route open |
| 6 | **Religions** | — | 2 of 11 have authored text. §12 is the owner's |
| 7 | **Pawntypes** | 3, 4, 5 | 48 proposed, 0 literal defNames. 19 ship, none matching |
| 8 | **Biomes** | 2 | ✅ ratified (W3) |
| 9 | **Factions** | 6, 7 | 1 of 12–14 ships. **`pawnGroupMakers` is the #1 blocker** |
| 10 | **Worldmap** | 8, 9, sea | 🔴 IRREVERSIBLE. Held on the sea |
| 11 | **Gravship** | 2 | ✅ built and exported |
| 12 | **Scenario** | 2, 7, 11 | 🔴 **no design doc exists anywhere** |
| 13 | **Quests** | 9 | row 3 reopened on resolution |

🔴 **Everything through 9 is upstream of 10, and 10 cannot be redone.** A
`FactionDef` that does not exist at world creation never gets settlements.

**0 → 1 → 2 → 3 is a single unbroken run and it is the head of all of v1.**
Nothing in 5–13 can be authored honestly until 3 lands, because every one of them
either equips a pawn or references something 1 might cut.

## Per domain

### 0 · Mod freeze — reversible, ~60 rows, do it first
Cutting a mod deletes defs and takes its tags with it, so every downstream
decision made first is invalidated. Prefer reversible suppression (ModsConfig,
zeroing generation weights, clearing `designationCategory`) over def culls.
🔴 **Two live contradictions to resolve here, not later:** `required_mods.md`
rules DECLINE on KotOR for the lean stack while `armoury_keeplist.md` makes it
the single largest keep (137 weapons) and `mod_config_rulings.md` treats it as
present; and `lee.theforce.lightsaber` is **active in `ModsConfig.xml` but not
installed**.

### 1 · Tag vocabulary — the artifact that was never written
A `PawnKindDef` consumes `weaponTags`, `apparelTags` and a few literal
`apparelRequired` defNames. **It does not consume a per-item verdict**, which is
why the 674-weapon keeplist was never the blocker. `pawnkind_roster.md` declined
to invent tag values on purpose. What is owed: the actual tag strings carried by
the surviving weapon and apparel defs, read out of the live dump.

### 5 · Religions
`faction_religions_spec.md` is the strongest doc in the set — real memes and
precepts read from the live dump — but its own heading says **the text is the
product**, and 9 of 11 have no authored player-facing text. Section 12 (Jawa) is
deliberately empty and stays that way: the player faith ships as
`src/Jawa/ideoligion/The Salvation.rid`.

### 6 · Pawntypes
48 kinds proposed (12 factions × Grunt/Heavy/Specialist/Leader), zero literal
defNames, `combatPower` unset on all of them. 19 PawnKindDefs ship and none
match the roster.
🔴 **`Jawa_Colonist` has no `weaponTags` and no `apparelRequired`.** The Jawa
robe-and-hood lock exists in the repo but was applied to a **donor** kind
(`OuterRim_Jawa`) and never mirrored onto ours.

### 8 · Factions
`Jawa_IndigenousTribes` is the model of done — `pawnGroupMakers`, `xenotypeSet`,
`forcedMemes`, `fixedIdeo`, and its three referenced kinds exist. Author the
other 11–13 against it.
**Open, and DECIDE owes every one:** the roster says 12 and
`faction_world_spec.md` says 14 with 8 renamed · no defNames · no
`pawnGroupMakers` anywhere · starting goodwill has no mechanism and rides
unproven Faction Customizer persistence · `faction_roster_v2.md:42` is a
known-wrong line that authorised all 12 goodwill numbers · D1–D6 in
`faction_stage2_gap_audit.md`, of which D2/D3 are answered in the religions spec
but never written back · leader title has three live values.

### 8 · Factions — DECIDE's rulings, 2026-08-14

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

### The buildable `FactionDef` contract

Every faction owes all of this. A dossier missing any line is not releasable to
BUILD. `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml` is the worked
example.

| group | fields |
|---|---|
| identity | `defName` `label` `description` `pawnSingular` `pawnsPlural` `leaderTitle` |
| art | `factionIconPath` `colorSpectrum` `settlementTexturePath` |
| naming | `factionNameMaker` `settlementNameMaker` — **0 of 12 exist today** |
| generation | `humanlikeFaction` `categoryTag` `techLevel` `settlementGenerationWeight` `maxCountAtGameStart` `canMakeRandomly` |
| hostility | one of `permanentEnemy` / `naturalEnemy` / `permanentEnemyToEveryoneExcept` / `raidsForbidden` |
| pawns | `basicMemberKind` · `pawnGroupMakers` with `options` and weights — **the #1 blocker, written nowhere** |
| ideo | `fixedIdeo` + `ideoName` + `ideoDescription` + `forcedMemes` (+ `deityPresets` where the faith has deities) |
| optional | `apparelStuffFilter` `backstoryFilters` `xenotypeSet` `raidCommonalityFromPointsCurve` `disallowedRaidStrategies` `styles` |

### 11 · Scenario — the hole
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

`V1_SCOPE.md` on the v1/v2 line for factions, pawnGroupMakers and ideoligions.
`faction_stage3_buildable_spec.md` on the vessel column. Both remain correct on
everything else and are not deleted.

# Quest authoring — what the installed modset actually does

_Research pass, 2026-08-14. Every number below is measured off the game install, the
Workshop tree, or this repo, and the command that produced it is given so it can be
re-run rather than trusted. Two full sweeps of all 1,246 workshop mods ran to
completion (XML side and DLL side) and reconcile._

## Contents

1. [The baseline: what vanilla ships](#1-the-baseline-what-vanilla-ships)
2. [Mods that add quests, and the technique each contributes](#2-mods-that-add-quests-and-the-technique-each-contributes)
3. [Does authoring need C#?](#3-does-authoring-need-c)
4. [Custom Quest Framework, and the mod that proves it works](#4-custom-quest-framework-and-the-mod-that-proves-it-works)
5. [What THIS project already built](#5-what-this-project-already-built)
6. [Failure modes — symptom → cause → catching it offline](#6-failure-modes--symptom--cause--catching-it-offline)
7. [Already documented in the repo — cite, do not re-derive](#7-already-documented-in-the-repo--cite-do-not-re-derive)
8. [Open / undetermined](#8-open--undetermined)

---

## 1. The baseline: what vanilla ships

Read from `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data`:
Core 23, Royalty 62, Ideology 15, Biotech 10, Anomaly 14, Odyssey 32 — **156
`QuestScriptDef`s.**

**The single most useful structural fact.** Of those 156, **88 have
`<root Class="QuestNode_Sequence">`** — the whole quest composed in XML from stock
nodes. The remaining ~68 name a bespoke `QuestNode_Root_*` C# class
(`QuestNode_Root_Bossgroup`, `QuestNode_Root_RefugeePodCrash`,
`QuestNode_Root_Gravcore_*`, …). **Ludeon itself splits roughly 56 / 44 between "XML
composition" and "one C# class does it", and makes that choice per quest.**

```bash
D="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
grep -rhoE '<root Class="[A-Za-z0-9_]+"' "$D"/*/Defs | sort | uniq -c | sort -rn
```

**The node vocabulary is large and entirely XML-addressable.** 301 distinct
`QuestNode_*` types in `Assembly-CSharp.dll`, read out of the TypeDef table — the real
roster, not a byte scan (a `strings` match once made it 268, and the blind-scan hook now
refuses `strings` on a `.dll` at all). From the repo root:

```bash
python3 -c "import sys;sys.path.insert(0,'src/RimMandrake/Utils/ilprobe');import meta_core as m;\
print(sorted({t[0] for t in m.typedefs if t[0].startswith('QuestNode_')}))"
```

Vanilla usage is dominated by plumbing: `QuestNode_Set` 262, `_Sequence` 259,
`_SubScript` 158, `_End` 146, `_Letter` 88, `_Signal` 84, `_Delay` 41, `_IsSet` 37.

**`Util_*` subscripts are the reuse layer, and there are 30 of them** —
`Util_GenerateSite`, `Util_Raid`, `Util_AdjustPointsForDistantFight`,
`Util_ArriveByDropPodsOrShuttle`, `Util_SendItemPods`, `Util_MechCluster`,
`Util_MaybeGenerateHelpers`, … Pulled in with
`<li Class="QuestNode_SubScript"><def>Util_X</def></li>`. **Reach for these first;
they are why `Jawa_TheClaim` is 223 lines and not 800.**

---

## 2. Mods that add quests, and the technique each contributes

Full sweep: **368 XML files mention `QuestScriptDef`, resolving to 64 mods that ship
real quest defs and 8 that only patch existing ones.** Counts are `<QuestScriptDef`
opening tags **deduplicated across per-version folders** — see failure mode 5.

### The leaders, and what each is worth stealing

| Mod | packageId | ws id | defs | technique it contributes |
|---|---|---|---|---|
| VFE - Deserters | `OskarPotocki.VFE.Deserters` | 3025493377 | 16 | 🔴 **The heaviest custom-C# quest mod installed** — ~30 distinct `VFED.QuestNode_*` classes (`_ValueFromTitle` ×24, `_GetEmpire` ×18, `_ImperialResponse` ×12). Its lesson is the *composition*, not the C#: 16 root defs that lean on `QuestNode_SubScript` into shared sub-scripts rather than 16 flat scripts. |
| Ancient mining industry | `XMB.AncientMiningIndustry.MO` | 3141472661 | 16 | 🔴 **The XML-only exemplar at scale.** Pure vanilla nodes — `GetSiteTile` + `GetSitePartDefsByTagsAndFaction` + `SpawnWorldObjects`. No custom root, no DLL node. |
| Ancient hydroponic farm | `XMB.AncientHydroponicFarmFacilities.MO` | 3075384838 | 13 | Same author, **same template cloned per theme**. Site-generation quest packs are a copy-paste genre. |
| Romance On The Rim | `telardo.RomanceOnTheRim` | 2654432921 | 13 | 13 defs, **13 bespoke `QuestNode_Root_*`** — one C# root per quest, XML is a 6-line shell. Also marks most `<isRootSpecial>` (see failure mode 7). |
| Dungeon Pack (Continued) | `Mlie.DungeonPack` | 3765496911 | 11 | 🔴 **11 quests authored through Custom Quest Framework, from XML, with no DLL of its own** — every def uses `QuestEditor_Library.QuestNode_RandomCustomMap` and declares `HaiLuan.CustomQuestFramework` as a dependency. §4. |
| VFE - Empire | `OskarPotocki.VFE.Empire` | 2938820380 | 9 | Vanilla nodes + `defaultChallengeRating` + goodwill manipulation on every quest. Its one patch file **adjusts Royalty's quests rather than adding new ones.** |
| VQE - The Generator | `vanillaquestsexpanded.generator` | 3411401573 | 7 | Mixed roots — some `QuestNode_Sequence`, some custom. Ships `QuestNode_Site`, a **reusable site node its own other quests call.** |
| Rim-Effect Renegade | `RimEffectRenegade.Core` | 3473370247 | 7 | `RimEffect.QuestNode_GetPawn` ×8 — a **narrow override of one vanilla node**, the cheapest kind of custom node. |
| VQE - Ancients | `vanillaquestsexpanded.ancients` | 3618306875 | 6 | One custom root per quest; XML is a thin shell, almost no inline node graph. |
| Reunion | `Kyrun.Reunion` | 1985186461 | 5 | **XML-only.** 5 defs, root `QuestNode_Sequence`, zero non-vanilla classes in XML. Its DLL's `QuestNode_PawnsArrive` is a Harmony target the XML never names. |
| Caravan Adventures | `iforgotmysocks.CaravanAdventures` | 2558957509 | 5 | All 5 are `<isRootSpecial>` sharing one placeholder `QuestNode_Temp`. **Arc state lives entirely in code; the XML is a manifest.** |
| [RH2] Faction VOID | `RH2.Faction.VOID` | 2883208829 | 5 | Faction-specific joiner/threat scripts. |
| Anomalies Expected | `MrHydralisk.AnomaliesExpected` | 3240752689 | 5 | `QuestNode_Root_AEMysteriousCargo` — a **vanilla root subclassed and re-pointed**. |
| Ancient urban ruins | `XMB.AncientUrbanrUins.MO` | 3316062206 | 5 | `AncientMarket_Libraray.QuestNode_GenerateCustomSite` ×8 — a custom **site generator** other quests can reuse. |
| Void Universe | `HaiLuan.VoidUniverse` | 3587277884 | 5 | `QuestNode_Root_SightstealerArrival_Space` — a vanilla Anomaly quest **re-authored for the space layer.** Directly relevant to a gravship campaign. |
| VQE - Cryptoforge | `vanillaquestsexpanded.cryptoforge` | 3461526070 | 4 | **Chaptered arc:** `QuestNode_Root_CryptoforgeChapter1..4`, one def per chapter. The vanilla-shaped way to do multi-stage. |
| New Anomaly Threats · Better Beggars · Alien\|Rimworld | `GoGaTio.NewAnomalyThreats` · `Mlie.BetterBeggars` · `niz.xenomorphtype` | 3274840013 · 3006899215 · 3596077324 | 4 each | Better Beggars is the clean case of **cloning a vanilla root** (`QuestNode_Root_Beggars_*`) to vary one behaviour. |
| Real Ruins | `Woolstrand.RealRuins` | 1552146295 | 1 | `QuestNode_FindBlueprint` + `_GenerateRuinsObject` inside a stock sequence — custom world-object generation, minimal surface. |
| Trader ships | `automatic.traderships` | 2046222331 | 1 | 🔴 **The hybrid worth copying:** stock `QuestNode_Sequence` skeleton with exactly two custom verbs spliced in. |
| Vanilla Gravship Expanded | (VGE) | 3609835606 | — | Shows **both modes at once**: transpiler patches on vanilla `QuestNode_Root_Gravship_Wreckage.RunInt` *and* a new `QuestNode_Root_MechanoidSignal_Expanded` referenced once from XML. |

### Patch-only mods — the "modify, don't author" route (0 new defs)

| Mod | ws id | patch files | note |
|---|---|---|---|
| [FSF] FrozenSnowFox Tweaks | 2893432492 | 7 | largest quest-patching surface installed |
| [RH2] Uncle Boris' - Used Furniture | 2563508405 | 2 (10 quests) | rewrites `Hospitality_*`, `PawnLend`, … |
| Medieval Fantasy Themed Relic Quests | 3035624471 | 2 | ⚠️ **misleadingly named** — zero quest defs; only rewrites `questNameRules` on vanilla `AncientComplex_Standard` |
| FIP - RobCo · Toddlers · Museums | 3563825876 · 2903359152 · 3204176859 | 1–2 | |
| RimQuest (Continued) | 2263331727 | 1 | fully C#-driven; ships a documented modder hook (`FOR MODDERS: You can add the below to your own mod to patch your own incidentDefs/QuestScriptDef`) |
| Call For Intel | 8Z.CallForIntel · 2557139479 | 1 | patches `questDescriptionRules/rulesStrings` on another mod's quest — **exactly the operation this repo used for the BTD grammar fix** |

---

## 3. Does authoring need C#?

**Verdict: no for a recombination, yes for a new verb — and this project has already
demonstrated the "no" by shipping a complete quest in pure XML.**

**The measurement that settles the direction.** Across all workshop mod XML:
**4,837 references to bare vanilla node names vs 410 references to 126 distinct
namespaced (mod) classes — ≈ 12 : 1.** Quest XML is overwhelmingly vanilla plumbing:
`QuestNode_Sequence` 662, `_SubScript` 649, `_End` 554, `_Set` 315, `_Letter` 288,
`_Signal` 207.

**Evidence that XML alone suffices:**

- `Jawa_TheClaim` (§5) — 223 lines, **14 node classes, all vanilla**, each verified
  present in `Assembly-CSharp.dll`. No assembly written.
- Vanilla composes **88 of its own 156 quests** from `QuestNode_Sequence` + stock nodes.
- Third-party existence proofs at scale: **Ancient mining industry ships 16 quests and
  Ancient hydroponic farm 13, both pure vanilla nodes, neither with a custom root.**
  Reunion (5) and VFE Settlers (2) likewise.
- `Class=` resolves **any loaded assembly's type**, so you can borrow another mod's
  node with no compilation — Dragons Descent uses `VEF.QuestNode_GetFaction`, and
  Dungeon Pack builds 11 quests on CQF's node. Both the short and fully-qualified
  forms work (`QuestNode_Sequence` and `RimWorld.QuestGen.QuestNode_Sequence` appear
  side by side in Dungeon Pack).

**Evidence that a new verb needs C#:**

- **Every one of the ~40 mods that adds structurally new quest content shipped a DLL
  to do it. Across 62 QuestNode-defining assemblies there is not a single
  counterexample** of new quest *mechanics* built from vanilla nodes alone.
- The convention is uniform: bespoke logic goes in a **`QuestNode_Root_*`**, and the
  XML def shrinks to a name, weights and text rules.
- Nothing at the XML layer expresses a new site type, a custom shuttle behaviour, a
  new reward formula, or faction-specific pawn selection.

**Three authoring paths, in increasing order of C#:**

1. **Pure XML** — compose vanilla nodes, plus any loaded mod's node by namespaced
   `Class=`. Covers every recombination of verbs that already exist. **Start here.**
2. **CQF's editor / node** — §4. No compilation, and a shipping mod proves it.
3. **C#** — required for a new verb, and **the only route** to altering vanilla quest
   logic in place. 62 mods define `QuestNode` symbols but only ~40 appear in XML; the
   ~22-mod gap is **Harmony patch targets** — a type name identical to a vanilla one,
   referenced nowhere in XML (`AlienRace.dll`, `MorePauseEvents.dll`,
   `VisibleRaidPoints.dll`, `Reunion.dll`, `BiomesCore.dll`). That route has no XML
   equivalent by construction.

**Practical rule for this project:** _if vanilla already knows how to do the thing —
put a site somewhere, hand over pawns or items, run a timer, branch on a signal, pay
out — write XML. Before reaching for C#, check the 30 `Util_*` subscripts and the ~300
nodes._

---

## 4. Custom Quest Framework, and the mod that proves it works

`HaiLuan.CustomQuestFramework`, ws 2978572782, installed and active (position 104 in
the load order).

**It ships zero `QuestScriptDef`s of its own — it is a library plus an in-game editor.**
Its `QuestEditor_Library.QuestNode_RandomCustomMap` is referenced **15 times** across
the workshop tree, one of the highest custom-node counts anywhere in the collection.

- **Nodes** (`1.6/Assemblies/net48/QuestEditor_Library.dll`):
  `QuestNode_Root_CustomMap`, `QuestNode_Root_MainMap`, `QuestNode_RandomCustomMap`,
  `QuestNode_DoCQFActions`, `QuestNode_GenerateCustomWorldObject`,
  `QuestNode_FindTileOnCoast`, `QuestNode_GameUnique`, `QuestNode_RemoveDataWhenEnd`.
- **Def types**: `QuestEditor_Library.CustomMapDataDef`, `DialogTreeDef`,
  `GroupDataDef`, `SpecialPawnGenerateDef`, `PawnModDef`, `LootDataDef`,
  `InteractionDataDef`, plus `HotLoad*Def` — the runtime-loaded editor output.
- **Authored content lives in `Quests/` at the mod root, not under `Defs/`**:
  `Quests/{Data,DialogTree,Duty,Group,Map,Pawn,Rule}`. Today it holds only the
  author's tests (`Quests/Map/Start.xml`; `Quests/Rule/Test_Name.xml`, a `<RuleText>`
  with `questName -> 帝国营地`).
- `loadFolders.xml` adds conditional folders (`IfModActive` for Odyssey, and three
  HaiLuan frameworks) — read it before counting anything in this mod.
- 🔴 **Nothing has been authored here on this install.** No CQF folder under
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`.

🔴 **Dungeon Pack (Continued) `Mlie.DungeonPack`, ws 3765496911, is the proof the
route works for a third party**: 11 quests, every def built on
`QuestEditor_Library.QuestNode_RandomCustomMap`, CQF declared as a dependency, **no
DLL of its own.** If we want authored dungeon set-pieces, that mod is the template to
read before writing anything.

**The full CQF capability write-up already exists and must not be re-derived:**
`D:\Luke\dev\Rimworld\vendor\wisdom\cqf_quest_types_explainer.md` — 4 building blocks,
4 `SpawnType` triggers, the complete 21-verb `CQFAction` list, conditions, signals,
required-items, 7 quest shapes. ⚠️ It was written from an `-Old-src` snapshot and its
§8 flags possible drift; the class names above were re-read from the **installed 1.6
DLL** and match.

---

## 5. What THIS project already built

Two defs, one patch, one bridge tool. All deployed. **None seen working in game.**

### `Jawa_TheClaim` — the quest
`D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Defs\QuestScriptDefs\Jawa_TheClaim.xml`
(223 lines; present in the deployed copy at `…\RimWorld\Mods\Jawa_Patches\…` — checked).

Shape: `Util_AdjustPointsForDistantFight` → `GetMap(canBeSpace)` → accept-letter →
`SetItemStashContents` (fixed haul: 1 spacer + 8 industrial components, 4 slag) →
`GetSiteTile(preferCloserTiles)` → threat chance behind `ViolentQuestsAllowed` →
`GetSitePartDefsByTagsAndFaction` → `GetDefaultSitePartsParams` → `Util_GenerateSite`
→ `SpawnWorldObjects` → a `WorldObjectTimeout` fail branch disabled by
`site.MapGenerated` → a `SignalActivable` success branch armed by `site.MapGenerated`
and fired by `site.MapRemoved`.

**What the header (lines 4–61) claims was verified against a shipping Ludeon def —
file and line, all under `…\common\RimWorld\Data`:**

| claimed | provenance cited |
|---|---|
| `rootSelectionWeight`, `rootMinPoints`, `expireDaysRange`, `everAcceptableInSpace`, `defaultChallengeRating` | `Core/…/Script_BanditCamp.xml:6-11` |
| `QuestNode_Sequence`, `GetMap(canBeSpace)`, `GetSiteTile(preferCloserTiles)`, `ViolentQuestsAllowed`, `Set`, `GetSitePartDefsByTagsAndFaction`, `GetDefaultSitePartsParams`, `SubScript`, `SpawnWorldObjects`, `WorldObjectTimeout(isQuestTimeout, inSignalDisable)`, `Letter`, `End` | `Core/…/Script_ItemStash.xml` |
| `QuestNode_SetItemStashContents`, `QuestNode_SignalActivable` | `Royalty/…/Script_Intro_Deserter.xml:91-96, 160-166` |
| a top-level `QuestNode_Letter` with no `inSignal` fires on accept | `Royalty/…/Scripts_Permits.xml:79` |
| `Util_AdjustPointsForDistantFight`, `Util_GenerateSite` | `Core/…/Scripts_Utility_ThreatsCore.xml:152, 346` |
| `ComponentSpacer`, `ComponentIndustrial`, `ChunkSlagSteel` | `Core/…/Items_Resource_Manufactured.xml:153,123`; `Various_Stone.xml:105` |
| **`everAcceptableInSpace` gates ACCEPTANCE, not site placement** | two independent proofs, header lines 35–57: the keyed string `QuestNotSpace` sits among *accept-requirement* strings in `Core/Languages/English/Keyed/MainTabs.xml:198`, **and** Odyssey's six genuinely-orbital quests never set the field while `Script_TradeRequest.xml` sets it true and forces a ground target — the "site placement" reading is inverted by both |

**Independently re-verified this pass:** all 14 node classes exist as exact-line
matches in `Assembly-CSharp.dll`. Core-only — DLC files are cited for *provenance*,
never as a dependency, so no DLC change can orphan it.

### `Jawa_ClaimRumour` — the on-demand trigger
`D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Defs\ThingDefs_Items\Jawa_ClaimRumour.xml`
(95 lines). A usable item that gives the quest and destroys itself:
`CompProperties_Usable(useJob UseItem)` + `CompProperties_UseEffectDestroySelf` +
`CompProperties_UseEffectGiveQuest(quest Jawa_TheClaim)`.

Header claims: the pattern was **borrowed from Space Tower's `ST_TowerMap`**, not
invented; every comp verified against a shipping def (`CompProperties_Usable` and the
two use-effects at `Biotech/…/Items_Various.xml:144,152,153`; `JobDef UseItem` at
`Core/…/Jobs_Misc.xml:461`; `ThingCategoryDef ItemsMisc` at
`Core/…/ThingCategories.xml:259`) — **and the classes live in `Assembly-CSharp`, so
the Biotech citations create no dependency.** Its stated reason for existing is a
load-budget one: a root-selected quest fires on the storyteller's cadence, and at
~23–30 min a cold load, "wait for the storyteller" is the most expensive way to clear
a gate.

### `BTDGravshipQuest_GrammarFix.xml` — the patch
`D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\BTDGravshipQuest_GrammarFix.xml` —
the repo's worked example of failure mode 1.

### `jawa/fire_quest` — the bridge tool
`D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\JawaBench.BridgeTools\JawaBenchTerrainTools.cs:3310-3380`.
Calls `QuestUtility.GenerateQuestAndMakeAvailable(QuestScriptDef, float)`,
IL-confirmed to reach `QuestManager::Add`, and **reads the quest back out of
`QuestManager`** because a method returning is not evidence. 🔴 **Built, deployed,
never run.**

---

## 6. Failure modes — symptom → cause → catching it offline

| # | symptom | cause | catch it offline |
|---|---|---|---|
| 1 | Quest fires and is playable but its **description is completely empty**. Log: `Grammar unresolvable. Root 'questDescription'`. | **Square brackets in a rule string are a grammar symbol reference.** `[BTD] Gravship Blueprints Quest` makes the resolver look for a rule named `BTD`. **One unresolvable symbol fails the WHOLE rule — it does not degrade to plain text.** | `grep -n '\['` every `rulesStrings` you write or adopt. Worked fix + verbatim resolution trace: `…\Jawa_Patches\Patches\BTDGravshipQuest_GrammarFix.xml` |
| 2 | Quest appears in the Quests tab but **Accept is greyed out** — only while the colony is on a space map. | `everAcceptableInSpace` unset ⇒ `QuestGen.Generate` attaches `AcceptanceRequirementNotSpace` (string `QuestNotSpace`). **Core's own `OpportunitySite_ItemStash` omits the field, and so do most vanilla quests.** | `grep -L everAcceptableInSpace` your quest defs. 🔴 **In a gravship campaign this is invisible in testing** — a ground colony sees the quest work perfectly. Standing rule: `design\Jawa\worldbuilding\v1_quest_the_claim.md:106-193` |
| 3 | You make a quest space-acceptable and nothing changes on the storyteller path. | `GiveQuest_Random` is tagged `targetTags World`, and `World.Tile` is `PlanetTile::Invalid`, so **both `CanQuestOccurOnTile` overloads return true on their first branch — the layer checks are dead code there.** `autoAccept` skips the requirement too. | Same file, 141–159. Do not attribute a symptom to a filter that never runs. |
| 4 | A `PatchOperationReplace` on another mod's quest throws a **red error every launch** once that mod is unsubscribed or fixed upstream. | An unmatched xpath in an unguarded operation always throws. | Wrap in `PatchOperationFindMod`. ⚠️ **`FindMod` matches the mod NAME, not the packageId** — read it from that mod's `About.xml`, never guess. Rationale: `BTDGravshipQuest_GrammarFix.xml:74-88` |
| 5 | 🔴 **Your census of a Workshop mod's quests is 3–8× too high.** | The mod ships `1.1/ 1.3/ 1.4/ 1.5/ 1.6/` folders each holding the same defs. Reunion looks like 25 quest defs; it has **5**. Romance On The Rim looks like 30; it has **13**. | Count only what the running version loads — skip any `1.[0-5]` path component and read `loadFolders.xml` when present. ⚠️ Counts may still include abstract `ParentName` base defs, so playable quests can be fewer than the tag count. |
| 6 | 🔴 **A tree-wide `grep` returns a confident, wrong, SMALLER answer.** | `timeout N grep …` over 1,246 folders on this mount is killed mid-scan and leaves a **partial file that looks complete**. Ours returned 75 files / 14 mods and silently omitted all three VQE modules — every one installed and shipping quests. The correct answer was 368 files / 64 mods. | Never read a short result from a slow-mount sweep as a negative. Verify a known-positive is in the output before believing any absence. Directly generalises `traps-tooling.md` "absence of output read as a negative result". |
| 7 | Quest def loads clean, shows in the def dump, and **never fires in play**. | Two separate causes. (a) `rootSelectionWeight` only puts it in the storyteller's pool — with hundreds of quests the wait is long, and `rootMinPoints` / `defaultChallengeRating` can gate it out. (b) **`<isRootSpecial>` removes it from the roll entirely** — it is then triggered only by mod code (Romance On The Rim and all 5 Caravan Adventures quests are like this). | Read `isRootSpecial` before you conclude anything about weights. And **never gate a verification on the storyteller**: give yourself a deterministic trigger — a `CompProperties_UseEffectGiveQuest` item, or `jawa/fire_quest`. The reasoning is written out at `Jawa_ClaimRumour.xml:4-13`. |
| 8 | A quest quietly stops being offered, with no error and no def change on disk. | **Cherry Picker does not delete a `QuestScriptDef` — it zeroes `rootSelectionWeight` and `decreeSelectionWeight` in place** (IL_0b09–IL_0b15), and its list lives only in the in-game settings UI. | `infrastructure\archive\2026-08-13_mechanoid_removal_study.md:100-118`. Read the **live** def, not the shipped XML. |
| 9 | `Class="SomeMod.QuestNode_X"` silently fails to resolve. | `Class=` resolves against loaded assemblies ⇒ borrowing another mod's node is a hard dependency **and** a load-order constraint. VEF ships `QuestNode_GetFaction` under **three** namespaces in live XML (`VFECore.` ×16, `VEF.Storyteller.` ×6, `VEF.` ×2) — the namespace moved and the old names are still referenced. | Read that mod's TypeDef table before writing the name — point `DLL` in a copy of `src/RimMandrake/Utils/ilprobe/meta_core.py` at its assembly and list every `QuestNode_*` in `typedefs` (the namespace comes with it). ⛔ Not `strings … \| grep QuestNode_`: the hook refuses it, and a byte scan of a .NET assembly sees a minority of names, so an absence proves nothing. Add the mod to `<modDependencies>`. Never guess a namespace, and never assume the one you saw is the only one. |
| 10 | Class name looks right; def still fails to load. | A guessed node name. There are ~300, and the near-misses are real (`QuestNode_GetSitePartDefsByTagsAndFaction` vs `QuestNode_GetDefaultSitePartsParams`). | 🔴 **The one-command gate — run on every quest def before it ships:** extract every `Class="…"` and confirm each is an exact TypeDef name, not a `strings` hit — `python3 src/RimMandrake/Utils/ilprobe/meta.py <ShortName>` prints the type with its namespace and prints **nothing** when it does not exist, which is the whole gate. (a `strings` of `Assembly-CSharp.dll` is refused by the blind-scan hook, and answers the wrong question anyway: a substring of a longer name is a hit.) All 14 of `Jawa_TheClaim`'s passed. |
| 11 | Success branch fires the instant the quest starts, or expiry races success. | Branch arming is signal-driven and easy to invert: a top-level `QuestNode_Letter` with **no `inSignal` fires on accept**; `WorldObjectTimeout` needs `inSignalDisable`; `SignalActivable` needs `inSignalEnable` **and** `inSignal`. | Read the pairing at `Jawa_TheClaim.xml:174-217` — `site.MapGenerated` disables the timeout *and* arms success; `site.MapRemoved` fires it. |
| 12 | You write the quest into the repo and the game never sees it. | The game loads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>`. Nothing syncs the repo. | `skills\rimworld-deploy\SKILL.md`. |
| 13 | A `strings` sweep says a mod ships 250–310 QuestNode types. | It bundles a **publicized copy of vanilla `Assembly-CSharp.dll`** under `Source/obj/*/PublicizedAssemblies/`. Also seen: a mod re-shipping another mod's `VEF.dll` verbatim. | Exclude `*/Source/*` and any `PublicizedAssemblies` path; a count near the vanilla total is the tell. |

---

## 7. Already documented in the repo — cite, do not re-derive

| what it settles | path |
|---|---|
| **CQF's complete capability surface** — 4 building blocks, 4 `SpawnType` triggers, all 21 `CQFAction` verbs, conditions, signals, required-items, 7 quest shapes, and the tradeoffs vs save-editing | `D:\Luke\dev\Rimworld\vendor\wisdom\cqf_quest_types_explainer.md` |
| **The space-acceptance ruling, campaign-wide** — mechanism, the IL-level refinement ("friction, not silence"), and the ⛔ *do not sweep 200 vanilla quest defs* decision | `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\v1_quest_the_claim.md` §106-193 |
| **What Cherry Picker does to a `QuestScriptDef`**, and that it does nothing to an existing save | `D:\Luke\dev\Rimworld\infrastructure\archive\2026-08-13_mechanoid_removal_study.md:100-180` |
| **The `questScriptDef`-referenced-by-`IncidentDef` gate** in the cherry-pick builder | `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\cherrypick_build.py:30,166-180,300` |
| **The grammar-bracket failure with verbatim log trace**, and the guarded-patch rationale | `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\BTDGravshipQuest_GrammarFix.xml` |
| **Row 3's gate, and why "blocked on a human" was the wrong conclusion** | `D:\Luke\dev\Rimworld\infrastructure\state\V1_CHAIN.md` |
| **The step-by-step in-game verification script** for rumour → quest (3 screenshots; PASS = any end state) | `D:\Luke\dev\Rimworld\infrastructure\state\TEST_PLAN.md:103-118` |
| `rimworld/right_click_cell` **is measured broken** — reports success, does nothing; why the float-menu route needed replacing | `D:\Luke\dev\Rimworld\skills\rimbridge\references\traps.md` |

⚠️ **`skills\rimworld-modding\` currently says nothing about quests** — grepped
`SKILL.md` and all six `references\traps*.md`; the only hits are incidental uses of
the word. This is new ground; cross-link from `traps.md`'s index rather than
duplicating into it.

---

## 8. Open / undetermined

- **Nothing in §5 has been observed in game.** `Jawa_TheClaim`, `Jawa_ClaimRumour`,
  the grammar fix's rendered description, and `jawa/fire_quest` are all *built ·
  deployed · never seen*. Every claim about them here is an offline claim.
- **The vanilla `QuestNode_*` count is 301 by exact-line `strings` match and 268 by a
  looser method.** Not reconciled. Immaterial for authoring — always check the
  specific name — but do not quote either as settled.
- **Def counts vs playable quests.** Counts are `<QuestScriptDef` tags; abstract
  `ParentName` bases are included, so playable totals are slightly lower. Not
  separated per mod.
- **How much of this campaign is spent on the Orbit layer** is unmeasured, and it
  decides whether failure mode 2 is an annoyance or a campaign stopper. Owner-level
  question, flagged in `v1_quest_the_claim.md:161-180`.
- **CQF's editor palette has never been opened**, and no quest has been authored with
  it here. The installed 1.6 DLL's class names match the `-Old-src` explainer, but the
  UI surface is unverified — and `Mlie.DungeonPack` (ws 3765496911) should be read
  first as a working template.
- **Not attempted:** whether `QuestScriptDef` supports `PatchOperationAdd` of a node
  into another mod's existing `<root>` graph. Every patch found here replaces text
  rules or whole defs, never splices a node.

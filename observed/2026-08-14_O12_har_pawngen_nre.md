# O12 — `GenerationChanceGenderless` NRE: settled, 2026-08-14

**Question (OPS queue O12):** were the 9 `Error while generating pawn. Rethrowing.
NullReferenceException` from `AlienRace.HarmonyPatches.GenerationChanceGenderless`
an artefact of debug spawning, or a defect that will also fire during
ordinary/worldgen pawn generation? And what is the 9th, unattributed occurrence?

---

## VERDICT — (b) REAL DEFECT. **And it is ours: `Jawa_Doctrine/Patches/DroidsAreMachines.xml` caused it.**

**It is NOT a worldgen defect.** No KotOR droid pawn is generated during worldgen —
verified below — and two measured worldgens produced zero occurrences. **The
worldgen run is unblocked; do not hold it for this.**

**It IS a raid defect, on the one faction the campaign cannot afford to lose.**
Every pawn of a KotOR droid race now has `relations == null`, and relation
generation dereferences it without a guard. The **second and every later pawn of
the same droid race** in a generation batch throws. `guy762_KotORFaction_RogueDroids`
raids are groups of repeated same-race droids — and that faction is the
quest-critical antagonist of the KotOR distress call, a v1 KEEP.

⚠️ **This supersedes an earlier draft of this file that called it a debug artefact.**
The artefact reading fitted every log observation and was still wrong; what broke it
was decompiling `PawnComponentsUtility`, not reading more log.

---

## 1. Two premises in the queue entry were wrong. Both corrections stand.

### 1a. There is no 9th occurrence. It is one burst of 9 on one pawn.

`D:\Luke\dev\Rimworld\observed\2026-08-14\Player.log.prelaunch`
(md5 `567fb44888001ac04c86a3055843d155` — **byte-identical to the live
`Player-prev.log`**: the session that started 17:31:34 and ended 2026-08-13 21:10,
i.e. the ion-weapon-test session):

| line(s) | content |
|---|---|
| **6793** | `Error while generating pawn…` — **the head**, tagged `[Ref E66AFB4E]` |
| 6794–6846 | the full stack trace for that ref |
| **6847, 6849, 6851, 6853, 6855, 6857, 6859, 6861** | 8 × the same error, each followed by `[Ref E66AFB4E] Duplicate stacktrace, see ref for original` |
| 6863 | `Tried to generate 2 traits for 3C-T0 over 500 extra times and failed.` |
| 6864 | `[Isekai Forge] Enhancing 3C-T0…, Utility droid (rank E)` |

`grep -c "Error while generating pawn"` = **9**, all carrying `Ref E66AFB4E`. The
"8 + 1 unattributed" split was a counting artefact — the head was counted apart
from its own 8 duplicates. There is no second pawn and no second context.

### 1b. "A failure at worldgen would be SILENT" is false.

`Error while generating pawn. Rethrowing.` is a `Log.Error` **that rethrows**;
`Verse.PawnGenerator.GeneratePawn` does not swallow it. The caller gets an
exception and no pawn. The premise that drove O12's priority — a leader quietly
generated without relations — does not exist. The failure is loud and it aborts.

## 2. The chain, every link verified independently this session

### Link 1 — our patch sets `isOrganic=false` on the KotOR flesh type
`D:\Luke\dev\Rimworld\src\Jawa\Jawa_Doctrine\Patches\DroidsAreMachines.xml`
lines 108–123 (`PatchOperationFindMod` → conditional Replace/Add) on
`FleshTypeDef[defName="ABF_FleshType_Synstruct_Base"]`. Authorised by the owner
2026-08-11. Deployed copy present at
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Doctrine\Patches\DroidsAreMachines.xml`.

### Link 2 — it applied, confirmed against the LIVE def dump
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs\FleshTypeDef.json`
(dumped 2026-08-14 01:20):
`ABF_FleshType_Synstruct_Base` → `"fields": { … "isOrganic": false … }`.
⚠️ Note for anyone re-checking: the dump nests it under `fields`, so a top-level
`x.get("isOrganic")` returns `None` and reads as "the flag is absent". It is not.

### Link 3 — `isOrganic` is exactly what decides whether a pawn gets a relations tracker
Decompiled from
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`
(ilspycmd, this session):

```csharp
// Verse.RaceProperties
public bool IsFlesh => FleshType.isOrganic;

// RimWorld.PawnComponentsUtility.CreateInitialComponents   — the ONLY general creation site
if (pawn.RaceProps.IsFlesh)
{
    if (pawn.relations == null) pawn.relations = new Pawn_RelationsTracker(pawn);
    if (ModsConfig.RoyaltyActive && pawn.psychicEntropy == null) …
}

// RimWorld.PawnComponentsUtility.AddAndRemoveDynamicComponents — the only other site
if (ModsConfig.BiotechActive && MechanitorUtility.IsPlayerOverseerSubject(pawn))
{ if (pawn.relations == null) pawn.relations = new Pawn_RelationsTracker(pawn); … }
```

⇒ **`isOrganic=false` on a Humanlike race means `pawn.relations` is never created.**
The Biotech fallback needs a player-faction mechanitor subject and cannot rescue
these. **Setting a faction on the spawn does not help** — that was the obvious
hypothesis and it is wrong.

### Link 4 — the KotOR droid races are Humanlike, genderless, and HAR-typed
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3047371944\1.6\Defs\ThingDefs_Races\AlienRace_*.xml`
— 13 `guy762_DroidRace_*` defs, every one `<hasGenders>false</hasGenders>`
(`AlienRace_T3series.xml` line 286; `guy762_DroidRace_3Cseries` at line 426 inherits
it), all `AlienRace.ThingDef_AlienRace`, all `intelligence: Humanlike` and
`fleshType: ABF_FleshType_Synstruct_Base` inherited from
`ABF_Thing_Synstruct_HumanlikeBase`. **Confirmed live, not just from XML** —
`D:\Luke\dev\Rimworld\observed\2026-08-13_ion_weapon_live_test.md` line 13 read
both fields off the running game for `guy762_DroidRace_3Cseries`.

### Link 5 — HAR's patch fires for exactly this shape, and derefs the null
`erdelf/AlienRaces`, `Source/AlienRace/AlienRace/HarmonyPatches.cs`. **Line numbers
match the shipped stack exactly** (2614, 2615, 2669), and the loaded assembly is
`…\294100\839005762\1.6\Assemblies\AlienRace.dll` (**not** the legacy
`…\839005762\Assemblies\AlienRace.dll`, which is the 1.0-era build; `loadFolders.xml`
routes 1.6 to `1.6/`, and the `.pdb` beside it is why the trace has line numbers at all).

```csharp
2591  public static bool GeneratePawnRelationsPrefix(Pawn pawn, ref PawnGenerationRequest request)
2595      if (!pawn.RaceProps.Humanlike || pawn.RaceProps.hasGenders || pawn.def is not ThingDef_AlienRace) return true;
2599      List<Pawn> enumerable = PawnsFinder.AllMapsWorldAndTemporary_AliveOrDead
2600                                .Where(x => x.def == pawn.def).ToList();       // SAME RACE ONLY
2605      if (current.Discarded) Log.Warning(…); else /* add (current, relationDef) pairs */
2614      … list.RandomElementByWeightWithDefault(x => … GenerationChanceGenderless(x.Value, pawn, x.Key, localReq), 82f);

2667      else if (relationDef == PawnRelationDefOf.Parent)
2669          generationChance = ChanceOfBecomingGenderlessChildOf(current, pawn,
2670              current.relations.GetFirstDirectRelationPawn(PawnRelationDefOf.Parent, p => p != pawn));
```

The PDB sequence-point table pins the trace's `[0x00195]` to the statement spanning
lines 2669–2670, i.e. the **`Parent`** branch. Within it:
`IL_019d: ldfld Verse.Pawn::relations` then
`IL_01b3: callvirt Pawn_RelationsTracker::GetFirstDirectRelationPawn`. `current` is
provably non-null (the caller already called `current.Discarded` on it), so
**`current.relations == null` is the fault**, exactly as Link 3 predicts.
`ChanceOfBecomingGenderlessChildOf` is ~200 IL bytes — far past Mono's inline
budget, and it would have its own stack frame.

### Link 6 — the trigger condition, and why the 10th attempt succeeded
`RandomElementByWeightWithDefault` evaluates the weight selector for **every**
element, so the throw is deterministic for a given world state. Line 2600 means the
candidate list is empty unless another pawn of **the same def** exists in
world-or-maps. Therefore:

> **The first pawn of a KotOR droid race always succeeds. The second and every
> later one throws, until no other pawn of that def remains in
> `AllMapsWorldAndTemporary_AliveOrDead`.**

That is the whole observed sequence. `observed/2026-08-13_ion_weapon_live_test.md`
lines 39–41 record it in plain words without knowing why: *"The first spawn
'succeeded' then the pawn vanished. Every later attempt NRE'd."* The 9 failures ran
while that earlier 3C droid was still in the finder; attempt 10 succeeded once it
was gone. It matches the rest of the corpus too — `ID-662` (Mining droid,
prelaunch 6765) and session2's `KM1` / `ID-825` / `R-8009` (6965, 6972, 6976) were
each the **first** of their own def that session, so all four are clean.

## 3. Why worldgen specifically is clear — and it is, on four independent grounds

1. **`guy762_KotORFaction_RogueDroids` generates no leader.**
   `…\294100\3047371944\1.6\Defs\FactionDefs\Factions_RogueDroids.xml`:
   `humanlikeFaction=false` (30), `hidden=true` (31), `leaderTitle` commented out (51).
   `RimWorld.Faction.TryGenerateNewLeader` (decompiled) builds its candidate list
   only from Combat-group options with `kind.factionLeader == true`; in
   `PawnKinds_RogueDroids.xml` **both** `factionLeader` entries are commented out
   (lines 797, 872). Empty list ⇒ no leader pawn.
2. **The other droid faction is not affected at all.** `JDSCIS_CIS_Faction`
   (Separatist Droid Army, 3276499495) is `intelligence: ToolUser` and not a HAR
   race — vanilla `PawnGenerator.GeneratePawnRelations` returns at
   `if (!pawn.RaceProps.Humanlike) return;`.
3. **No KEEP faction has a droid leader.** All `factionLeader` pawnkinds in the
   Outer Rim mods are organic humanoids (`OuterRim_TownCouncilman`,
   `OuterRim_PirateBoss`, `OuterRim_ImpStormCommander`,
   `OuterRim_ImperialArmyCommander`); Droid Depot (3096501398) declares **zero**
   `factionLeader`. And a leader is one-per-faction, so even a droid leader would
   be first-of-def and safe (§2 Link 6).
4. **Measured, twice, zero.** Two full worldgens with the offending faction present
   (it is `requiredCountAtGameStart=1`) produced no occurrence:
   the prelaunch session's own worldgen (Isekai enhancement lines 5827–6097; the
   burst came 700 lines later, post-mapgen, at 17:55 inside the RimBridge window),
   and `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`
   — **a session newer than the harvest**, already ended 2026-08-14 12:05 (7453 lines,
   terminating in the Unity shutdown block), `Initializing new game with mods:` at
   line 6142, `grep -c "Error while generating pawn"` = **0**.
   `observed\2026-08-13\logs\Player.startup.585.2026-08-14.log` = **0**.

## 4. Blast radius

| family | Humanlike | HAR race | genders | `isOrganic` now | relation path | verdict |
|---|---|---|---|---|---|---|
| **KotOR droids** (13 races, `guy762_DroidRace_*`) | yes | yes | **none** | **false (ours)** | HAR `GeneratePawnRelationsPrefix` | 🔴 **BROKEN — proven** |
| **Outer Rim droids** (`Asimov.PawnDef`, 3096501398) | yes | **no** (plain `ThingDef`) | **mixed** — the mod ships both `hasGenders` true and false bases | **false (ours)** | **vanilla** `GeneratePawnRelations` | ⚠️ **UNSETTLED — see below** |
| **JDS / CIS battle droids** (3276499495) | no (`ToolUser`) | no | none | false (vanilla `Mechanoid`) | early-returns | ✅ unaffected |

⚠️ **The Outer Rim question is genuinely open and I am not calling it.** Vanilla's
`GeneratePawnRelations` is gated only on `Humanlike`, so it *does* run on them, and
`PawnRelationWorker_Parent.GenerationChance` calls
`other.GetFirstSpouseOfOppositeGender()` — which derefs `other.relations`. **But it
only reaches that call inside `if (other.gender == Gender.Male/Female)`**, so a
genderless Outer Rim droid skips it and returns 0 harmlessly. A **gendered** one
would not. Whether any *droid* race uses the gendered base is unresolved — the
`hasGenders` counts above are 3-and-3 across the mod's 1.4/1.5/1.6 folders and I did
not attribute them to specific defs. **No Outer Rim occurrence exists anywhere in
the corpus**, so this is a hypothesis, not a finding.

## 5. Recommended actions

| | |
|---|---|
| **Worldgen run** | **UNBLOCKED. Do not add a gate to `WORLDGEN_RUN.md` and do not spend a load.** §3 is four independent reasons. |
| **O12 disposition** | 🔴 **Do NOT close as waived, and do NOT add it to `benign_log_errors.md`.** Re-file as a live defect against the KotOR droid raid path. |
| **The decision the owner has to make** | Three routes, all v1-relevant: **(a)** drop `ABF_FleshType_Synstruct_Base` from `DroidsAreMachines.xml` — restores tending of KotOR droids and loses vanilla EMP/stun on them, but **does not touch our ion weapon**, whose guard was moved to `RaceProps.IsMechanoid` on 2026-08-13 (patch header lines 22–33); **(b)** keep the doctrine and add ~5 lines of Harmony to an assembly we already ship, giving Humanlike pawns a `Pawn_RelationsTracker` regardless of `IsFlesh`; **(c)** accept it and let RogueDroids raids fail. **(c) is not viable — that faction is the antagonist of the KotOR distress call.** ⛔ Retargeting the races to vanilla `Mechanoid` is NOT an option: it would make them `IsMechanoid`, which our ion weapon deliberately blocks. |
| **Cheap live confirmation, ~30 s, rides any bridge** | **Spawn `KotORDroidGood_3C` twice on the same map.** The first succeeds; the second must NRE with `Ref`-tagged `GenerationChanceGenderless`. If the second one succeeds, §2 Link 6 is wrong and everything above needs re-opening. |
| **Follow-up, filed not chased** | Settle the Outer Rim row in §4: which `Asimov.PawnDef` droid races use the `hasGenders=true` base. Offline, no load needed. |

## 6. Reusable lessons (for `traps-*.md`)

- 🔴 **Changing `isOrganic` on a Humanlike race silently deletes its
  `Pawn_RelationsTracker`.** `IsFlesh => FleshType.isOrganic`, and
  `CreateInitialComponents` gates the tracker on `IsFlesh`. Nothing warns. The
  doctrine patch's own "WHAT TO WATCH" list (lines 57–60) named tending, EMP and
  `IsFlesh` checks — **it did not know a whole tracker goes with it.** Generalises
  to: *a flag consumed by one system is rarely consumed by only one system — grep
  the engine for the property, not for the flag.*
- ⭐ **A story that explains every observation can still be wrong.** The
  "debug-spawn artefact" reading fitted all nine errors, the timestamps, the clean
  droids and the eventual success. It died to a decompile, not to more log.
  *When the question is "is this OURS", read the code that consumes the field.*
- ⚠️ **`x.get("isOrganic")` on the def dump returns `None` for a field that is
  present.** The dump nests real values under `fields`. An absent input read as an
  empty one — the instrument could not see it, and a top-level lookup would have
  "proved" the patch never applied.

## Evidence index

| file | lines / values used |
|---|---|
| `D:\Luke\dev\Rimworld\observed\2026-08-14\Player.log.prelaunch` | 3332, 6722, 6750, 6765, **6793**, 6794–6846, **6847/6849/6851/6853/6855/6857/6859/6861**, 6863, 6864, 6867 |
| `D:\Luke\dev\Rimworld\observed\2026-08-13\logs\Player.2026-08-13_session2.log` | 6924, 6965, 6972, 6973, 6976 (⚠️ its 2 NREs are `Pawn_IdeoTracker.SetIdeo` — a **different** defect, do not merge with O12) |
| `D:\Luke\dev\Rimworld\observed\2026-08-13\logs\Player.startup.585.2026-08-14.log` | count 0 |
| `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log` | 6142; count 0 (session ended 2026-08-14 12:05) |
| `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs\FleshTypeDef.json` | `ABF_FleshType_Synstruct_Base.fields.isOrganic = false` |
| `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Doctrine\Patches\DroidsAreMachines.xml` | 22–33, 57–60, 108–123 |
| `D:\Luke\dev\Rimworld\observed\2026-08-13_ion_weapon_live_test.md` | 12, 13, 39–41, 66 |
| `Assembly-CSharp.dll` (ilspycmd) | `Verse.RaceProperties.IsFlesh`; `RimWorld.PawnComponentsUtility.CreateInitialComponents` / `AddAndRemoveDynamicComponents`; `Verse.PawnGenerator.GeneratePawnRelations`; `RimWorld.PawnRelationWorker_Parent.GenerationChance`; `RimWorld.Faction.TryGenerateNewLeader` |
| `…\294100\839005762\1.6\Assemblies\AlienRace.dll` + `.pdb` | `GeneratePawnRelationsPrefix` 2591–2624, `GenerationChanceGenderless` 2626–2690, seq-point `0x0195` → 2669–2670 |
| `…\294100\3047371944\1.6\Defs\ThingDefs_Races\AlienRace_*.xml` | `hasGenders` false ×13; `AlienRace_T3series.xml` 286, 426 |
| `…\294100\3047371944\1.6\Defs\FactionDefs\Factions_RogueDroids.xml` | 6, 11, 30, 31, 36, 47, 51 |
| `…\294100\3047371944\1.6\Defs\FactionDefs\PawnKinds_RogueDroids.xml` | 797, 872 (`factionLeader` commented out) |
| `…\294100\3096501398` (Droid Depot) · `…\294100\3276499495` (JDS CIS) | `intelligence` Humanlike ×3 / ToolUser; `hasGenders` 3 true + 3 false; zero `factionLeader` |
| `D:\Luke\dev\Rimworld\infrastructure\state\WORLDGEN_FACTION_CHECKLIST.md` | 241–256 |

**Tooling note for whoever re-runs this:** `ilspycmd` is at
`C:\Users\Mandrake\.dotnet\tools\ilspycmd.exe` and needs
`WSLENV=DOTNET_ROLL_FORWARD DOTNET_ROLL_FORWARD=Major` from WSL (only the .NET 8
runtime is installed, and a bare env var does **not** cross into the Windows
process without `WSLENV`). Types are under their real namespace —
`RimWorld.PawnComponentsUtility`, `Verse.PawnGenerator`.

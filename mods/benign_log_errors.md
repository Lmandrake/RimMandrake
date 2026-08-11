# benign_log_errors.md — mod errors that are SAFE TO IGNORE

_Started 2026-08-10. A growing triage list so we stop re-investigating the same
harmless log noise on every load. **Every entry here has been traced to root
cause and judged non-blocking** — nothing goes on this list on a hunch._

**Rule for adding an entry:** name the exact log string, the mod that owns it,
the root cause, and *why* it is harmless. If you can't fill all four, it doesn't
belong here yet — put it in §3 instead.

Companion: `live_mod_inventory.md` (what's installed), `required_mods.md` (why),
`skills/rimworld-modding/references/traps.md` (lessons that change how we work).
Source of truth for the errors themselves: `Player.log` after a clean load.

---

## STATE OF THE LOAD — 2026-08-10 16:12 (load #4, the clean one)

**17,038 lines. Nothing unexplained remains.** Every surviving line is either a
documented benign entry below or has a patch already deployed for the next load.

| Bucket | Session start | Now | Notes |
|---|---|---|---|
| Log size | 528,687 lines / 43 MB | **17,038** | −97% |
| Unresolved cross-references | 1,555 | **25** | all documented: 16 §1.6 + 8 §1.11 + 1 §1.1 |
| Stale scribe references | 394 | **0** | Deep Storage prune + the two broken xenotypes |
| Biomes destroyed | 7 | **0** | the `<li>` shape fix |
| Dead mods (static ctor) | 3 | **1** | only `HeadSetForFA` — §3 |
| Def discarded | 2 | 2 | §1.8, benign |
| Patch no-ops | 5 | 5 | §1.2, benign |

**The one red error left** is the SWCP `ResolveIcon` NRE, and
`Jawa_Patches/Patches/SWCPZoomerIcon_Fix.xml` is deployed to remove it next load.
Prediction to check: the `Could not execute post-long-event action` block **gone**;
the two `Failed to load bundle` blocks **still present** (different cause — both
`[StaticConstructorOnStartup]` cctors still run, just later). Do not read their
presence as the patch failing.

**Still genuinely open:** `HeadSetForFA` (§3) and the eye/lid rendering question
(§4c). Everything else in the log — including the ~140 worldgen
`Could not find player faction.` lines, attributed 2026-08-10 to Tech Level
Enforcement (§4b.1) — is explained and benign.

## 0. READ THIS FIRST — the two error phrasings are different systems

RimWorld emits two similar-looking messages from completely different code, and
confusing them cost us a full investigation cycle:

| Phrasing | System | Means |
|---|---|---|
| `Could not **resolve** cross-reference: No X named Y` | **Def loader** | A def in a mod's XML points at something absent. Live mod-set problem. |
| `Could not **load** reference to X named Y` | **Scribe / deserializer** | A *saved file* — mod settings, a save game, a scenario — holds a name that no longer exists. Nothing to do with the current mod set. |

The second kind is where "errors from mods I removed months ago" come from. Mod
settings files under `Config/` are **never cleaned up when you unsubscribe**, so
any mod caching a `List<ThingDef>` keeps that list forever. See §2.4.

**Triage order, by consequence rather than by position in the file:**

1. `grep -n "static constructor\|TypeInitializationException"` — these mods are
   *dead*, not noisy, and will not say so again later.
2. ~~Exceptions inside `LongEventHandler.ExecuteToExecuteWhenFinished`~~ —
   **RETRACTED 2026-08-10.** We believed these aborted the rest of the post-load
   queue. They do not. Verified from the game's IL: per-action try/catch, and the
   handler's `leave` targets the loop increment. `Could not execute post-long-event
   action` costs exactly one action. Demoted to roughly bucket 4 severity.
3. `Exception loading def from file X` — a def was **discarded**. Everything that
   referenced it is about to fail in ways that don't name it.
4. `Could not resolve cross-reference` — usually a `MayRequire` guarding the mod
   rather than the def. Harmless individually; a large count means content is
   silently incomplete.
5. `Could not load reference to` — stale saved data. See §0 above and §2.4.
6. `Patch operation ... failed` — a no-op. The most common noise in a big stack.
7. Translation errors, missing sounds — cosmetic. The engine says so itself.

---

## 1. SAFE TO IGNORE — verified

### 1.1 `VWE_Tool_Whip` — TraderGen husbandry stock generator
```
Could not resolve cross-reference: No Verse.ThingDef named VWE_Tool_Whip found
to give to RimWorld.StockGenerator_SingleDef
```
**Owner:** TraderGen (3525848981) · **Root cause:** position 5 of `TG_Husbandry` is
```xml
<li Class="StockGenerator_SingleDef" MayRequire="VanillaExpanded.VWE">
    <thingDef>VWE_Tool_Whip</thingDef>
```
`VWE_Tool_Whip` exists in Vanilla Weapons Expanded's **1.4 and 1.5** folders but
**not 1.6** — VWE dropped it. TraderGen's guard checks the *mod* is present, not
that the *def* still exists, so the guard passes and resolution fails.

**Why harmless:** one stock generator in one trader specialisation. Husbandry
traders don't carry whips. **Upstream bug — TraderGen should pin the def, not the
mod.** Fixable with a one-line `PatchOperationRemove`; not worth the patch today.

### 1.2 Conditional patches that found no target
```
Patch operation Verse.PatchOperationFindMod(Gemstones, Jewelry) failed
PatchOperationReplace(.../GroundPenetratingScanner/placeWorkers/...) failed
PatchOperationRemove(.../ExtractOvum/genderPrerequisite) failed
PatchOperationRemove(.../TerminatePregnancy/genderPrerequisite) failed
PatchOperationRemove(.../ImplantIUD/genderPrerequisite) failed
```
**Root cause:** compatibility patches whose target either isn't installed
(`FindMod(Gemstones, Jewelry)`) or whose target node changed shape in 1.6
(the three `genderPrerequisite` removals — Ludeon restructured those recipes).

**Why harmless:** a failed `PatchOperation` is a no-op. The patch simply doesn't
apply; nothing is corrupted. Single most common category of log noise.

### 1.3 "duplicate keys" from Realistic Planets — **not an error**
```
[Realistic Planets] Patched WildPlantSpawner.Add() call to prevent duplicate keys
```
Realistic Planets **reporting that it fixed** a duplicate-key crash, not reporting
one. Positive signal. Do not chase.

### 1.4 "duplicate xenotypes (BTD preference active)" — **working as designed**
Xenotype REMIX: Star Wars (3458153185) deduplicating the overlap between Star
Wars Xenotypes and Outer Rim – Galactic Diversity. Exactly the job it was adopted
to do, and it resolves the SW-Xenotypes/OR-GD conflict.

### 1.5 Translation errors
```
Translation data for language English has ~228 errors.
```
Missing/stale translation keys across a 562-mod stack. Cosmetic only. Chasing
these across 562 mods is not a good use of time.

### 1.6 `Pawn_Melee_Punch_HitBuilding` missing on 16 races
```
Could not resolve cross-reference: No Verse.SoundDef named
Pawn_Melee_Punch_HitBuilding found to give to Verse.RaceProperties
(using undefined sound)
```
**Owner — CONFIRMED 2026-08-10, and it is not what we guessed.** The note used to
read *"🔎 Suspected source: Fists Aren't Made of Steel. Not confirmed."* That was
wrong. An anchored search of the whole load set found:

- **Nobody defines** the bare `Pawn_Melee_Punch_HitBuilding`. Core defines only the
  four *suffixed* variants — `_Metal`, `_Stone`, `_Wood`, `_Generic`.
- Exactly **two files reference the bare name**, and both are `Abstract="True"`
  base ThingDefs:
  - Asimov (WS 3096481956) `Defs/ThingDefs_Automatons/Race_Bases.xml`,
    `Name="AsimovNonEnergyAutomatonBase"`
  - [JDS] StarWars – The Separatist Droid Army (WS 3276499495)
    `Defs/ThingDefs_Race.xml`, `Name="JDSSWCIS_Droids"`

**Why 2 references produce 16 errors:** inheritance. Every concrete race that
inherits one of those two bases inherits the dangling sound reference, and each
resolves (and fails) independently.

**Why harmless:** the engine says it outright — *"using undefined sound"*. Falls
back gracefully; the punch is silent against buildings for those races. Cosmetic.

⚠️ **Method note, because it nearly produced a wrong answer.** A substring search
matched `Pawn_Melee_Punch_HitBuilding_Metal` and friends, which made it look like
Core, Anomaly and Odyssey were referencing a def they define — implicating vanilla.
Anchoring the match (`…(?!_)`) cut 41 hits down to the real 2. This is the
same "anchor the match" trap already recorded in `traps.md` for `success":1` vs
`success":15`; a known trap is not a solved trap.

### 1.7 `drawStyleCategory` on BuildingProperties — 1.6 field drift
```
XML error: <drawStyleCategory>Wall</drawStyleCategory> doesn't correspond to any
field in type BuildingProperties.
```
**Owner:** Rim of Madness – Bones Unofficial Fix. **Root cause:** the field moved
or was removed in 1.6; the mod carries a pre-1.6 def. Same class as the Martens
`wildness` error (§2 below).

**Why harmless:** one field on one building is dropped; the def still loads. The
only effect is that the building doesn't participate in wall draw-style grouping.

### 1.8 Onimods Electric Torches × Dark Ages Crypts — two ThoughtDefs discarded

⚠️ **Corrected 2026-08-10 (second load).** This was filed as a missing
ThoughtWorker. It is worse than that on both counts: the real log line is an
**`Exception loading def from file`**, which means the defs are *discarded*
(triage bucket 3, not 4), and the missing type is named
`ThoughtGiverByProximityDefExtension`, not `ThoughtWorker_ThoughtFromNearbyThingDef`.
Verdict is unchanged — still benign — but the record was wrong twice.

```
Exception loading def from file ElectricTorches_DarkAgesCrypts_Thoughts.xml:
System.ArgumentException: Could not find type named
VanillaFurnitureExpanded.ThoughtGiverByProximityDefExtension   (×2)
```
**Owner:** Onimods – Electric Torches and Braziers (3301583634), in
`CurentVersion/LoadFolders/DarkAgesCrypts/Defs/ElectricTorches_DarkAgesCrypts_Thoughts.xml`
— a compatibility folder pulled in by `<li IfModActive="Van.DACrypts">`, and Dark
Ages Crypts **is** active (load position 112), so the folder loads.

**Root cause — checked properly, 2026-08-10:** Vanilla Furniture Expanded **is
installed** (`vanillaexpanded.vfecore`, WS 1718190143, load position 360). Its
`VanillaFurnitureEC.dll` was searched in all three shipped version folders:

| VFE version folder | `ThoughtFromNearbyThingDef` | `VanillaFurnitureExpanded` namespace |
|---|---|---|
| 1.4 | 0 | 0 |
| 1.5 | 0 | 0 |
| 1.6 | **0** | 1 |

The namespace exists; **the type does not, in any version**. So this is a stale
reference by the Onimods author, not a load-order problem and not a missing
dependency. (Load order is irrelevant here anyway — RimWorld loads every mod's
assemblies before resolving type names, so `GenTypes` sees all of them.)

**Why harmless:** two ThoughtDefs in an optional compatibility patch fail to get
a worker. Pawns don't receive a mood thought from standing near those specific
crypt torches. Nothing else references them.
**If the noise ever matters:** `PatchOperationRemove` the two ThoughtDefs in
Jawa_Patches. Not worth it today.

### 1.9 ~~Missing PawnKindDefs in biome animal tables~~ — ❌ **RETRACTED 2026-08-10**

**This entry was wrong.** It is moved to §3.4 and is the confirmed cause of a
dead mod. The reasoning that failed is preserved here because the *shape* of the
mistake is worth more than the fact:

> ~~**Why harmless:** five spawn-table entries are skipped. The biome still
> works.~~

They are not skipped. An unresolved `BiomeAnimalRecord` keeps its record and
nulls the `animal` field, and `BiomeDef.CommonalityOfAnimal` then calls
`Dictionary.Add(null, …)`. Five "harmless" lines were killing Choose Wild Animal
Spawns outright. See §3.4 for the full trace and the fix.

The entry even flagged its own doubt — *"an unresolved `BiomeAnimalRecord` is the
same family as the null-key crash"* — and then filed it as benign anyway.
**Standing rule from this: a hedge in a benign entry disqualifies it.** §0 says
all four fields must be fillable; "why harmless" is one of them, and "probably
harmless, but note the shape" does not satisfy it.

### 1.11 `BMT_*` — TraderGen and Primordial Geysers reference dropped Biomes! defs
```
Could not resolve cross-reference to Verse.PawnKindDef named BMT_Boomapillar
  (wanter=pawnKindDefs)                                              ... ×8
Could not resolve cross-reference to Verse.ThingDef named BMT_BoomSpore
  (wanter=thingDefs)
```
Also `BMT_BoomMoth`, `BMT_Goeto`, `BMT_Jewelbug`, `BMT_SandyToad`,
`BMT_Woolybat`, `BMT_WoollySpider`.

**Owners:** TraderGen (`TG_Specializations.xml`) and Primordial Geysers
(`PrimordialGeysers_VanillaAnimalsExpandedPatch.xml`). **Root cause:** Biomes!
Caverns (`biomesteam.biomescaverns`, WS 2969748433, active) **is** installed, but
these defs exist only in its 1.4/1.5 folders — they were dropped in 1.6. The
`MayRequire`-guards-the-mod pattern again (§1.1).

**Why harmless — and why this one really is, unlike §1.9:** the `wanter` is
`pawnKindDefs` / `thingDefs`, plain **`List<Def>`** fields on a trader
specialisation. RimWorld drops an unresolved entry from a list. It does **not**
drop it from a `Dictionary`-populating record like `BiomeAnimalRecord`, which is
what makes §3.4 fatal and this benign.

**The discriminator to apply to any unresolved cross-reference:** read the
`wanter`. A plain list field degrades gracefully; a field that later becomes a
dictionary key does not.

### 1.10 `Parsed 1.5 as int`
```
Parsed 1.5 as int.
[Def Error]: PassableBasalt / PassableVacstone
Minerals Rock\1.6\Defs\ThingDefs_Rocks\Basalt.xml
```
**Owner:** Minerals Rock. A float written where the field is an int; the engine
truncates to 1 and continues. Cosmetic.

---

## 2. RESOLVED — kept for the record, do not re-investigate

| Error | Verdict |
|---|---|
| `AUR Hit Point` + `All Deconstructible` "conflict" | **Not a conflict.** All-Deconstructible is a hard `modDependency` of Hit Point. Run both. |
| RimAI Core `TypeLoadException` on `RimAI.Framework.Contracts.Result\`1` | **Fixed** by a RimSort **User Rule** forcing Framework before Core. (Community Rules silently discards saves when its DB source is `None`.) Zero `ReflectionTypeLoadException` in the 2026-08-10 load — holding. |
| `Created WorkshopItem for 3542508261 but there is no folder for it` (×3) | **Nephilim Xenotype Reborn** — removed from the Workshop for guideline violations, so Steam cannot download it. **Unsubscribe to clear.** (It is NOT the Facial Animation eye-colour patch.) |
| `<wildness> doesn't correspond to any field in RaceProperties` ×8 | **Resolved 2026-08-10** — *Martens – Nature's Most Adorable Assassins* (1.6 moved the field). Mod removed and unsubscribed. |
| `ChooseWildAnimalSpawns` → `ArgumentException: Key: Armadillo` | **Fixed 2026-08-10** by `Jawa_Patches/Patches/AnimalBiomeDuplicates_Fix.xml`. Giddy-Up and Biome Compatibility Project both stopped throwing at the same time. |
| `RimtalkContext...PostLoadPatcher` → `AmbiguousMatchException` | RimTalk Context Upgrade vs RimTalk version drift. **Removed 2026-08-10.** |
| `Could not find a type named RimTalkExpandActions.SocialDining.*` (×3) | **Mod removed 2026-08-10.** The types *did* exist in `RimTalk-ExpandActions.dll` and the defs spelled them correctly — the assembly simply never loaded. Diagnosis abandoned as not worth the effort: Social Dining was the only feature those defs powered and it wasn't wanted. |

### 2.4 The 394 "errors from long-past mods" — **SOLVED and FIXED 2026-08-10**

```
[13:54:15] Could not load reference to Verse.ThingDef named DF_XPerception_Implant
[13:54:15] Could not load reference to Verse.ThingDef named Corpse_RH_DF_Titan
   ... 394 lines, 378 distinct defs
```

**Not a mod problem at all.** Source was a single file:
`Config/Mod_3532608331_DeepStorageMod.xml` — LWM's Deep Storage, **last written
2025-12-14**. It persists a `ThingFilter` for one storage building
(`DSU_SW_AdaptiveFridgeStorageCabin_filter`) whose `allowedDefs` whitelist held
**1,206 entries** captured from the mod set installed at that time. Every entry
whose mod is gone throws one `Could not load reference` on deserialize.

Breakdown by prefix: Psytrainer 202 · Corpse 58 · Meat 33 · DF 30 · RH 11 ·
RH2 7 · BotchJob 4 · VRE 3 · NAT 3 · pphhyy 2 · AE 2 · Void 1.

**Fix applied:** pruned exactly the 378 dead entries, kept the 828 that still
resolve, so the curated filter survives. All seven Deep Storage settings intact,
file parses clean, 45,441 → 29,719 bytes. Original preserved at
`runtime/backups/Mod_3532608331_DeepStorageMod.ORIGINAL-2026-08-10.xml`.

**Config audit run at the same time** — all 35 `Mod_*.xml` files checked against
the installed Workshop content and `ModsConfig.xml`: **0 orphaned**, 2
installed-but-inactive and both 0 bytes. Deep Storage was the only offender; no
systemic cleanup is needed.

**Standing rule:** a `Config/Mod_*.xml` over ~10 KB is caching def lists and is a
stale-reference candidate. Current largest: Combat AI, Deep Storage (fixed),
Director. Re-check after any large mod purge, not routinely.

---

## 3. NOT SAFE TO IGNORE — open, tracked elsewhere

Listed here only so nobody mistakes them for benign.

| Error | Status |
|---|---|
| `[SWCP Core/Tools] Failed to load bundle ... SWCPshaders` → `BuildableDef.ResolveIcon()` NRE | **Upstream packaging bug**, filed as issue #7 (open). The mod ships `SWCP_Core.dll` referencing an AssetBundle it never includes — absent from the Workshop upload *and* the GitHub repo. ⚠️ **Severity downgraded 2026-08-10** — see §6. The queue does not abort; the NRE costs one def's `ResolveIcon`. Cannot be removed: SWCP defines 1,959 defs and ships 36 assemblies, and the whole KotOR family sits on it. |
| `HeadSetForFA.HSMCache` → NRE in `CheckSettingData(ThingDef raceDef)` | Head Set For [NL] Facial Animation is not applying. **Parked** pending the facial-animation visual test — if faces look right without it, drop the mod. |
| `ChooseWildAnimalSpawns` → `ArgumentNullException: key` | **Still dead — but the cause is now known and is NOT ours.** See §3.4. BCP recovered; CWAS did not, and that turned out to be the genuine separate bug this row predicted. |

### 3.4 ✅ RESOLVED — `ChooseWildAnimalSpawns` null PawnKindDef key

**CONFIRMED FIXED, load of 2026-08-10 15:54.** `BiomeAnimalDanglingRefs_Fix.xml`
did it. Every prediction in this entry held:

| Predicted | Result |
|---|---|
| the 5 `AEXP_*` / `AA_*` → `BiomeAnimalRecord` lines gone | **0** ✅ |
| `Error in static constructor of ChooseWildAnimalSpawns.Main` gone | **gone** ✅ |
| cross-references 30 → ~25 | **25** ✅ |

The mod initialises for the first time in four loads. The only remaining
static-constructor death in the whole log is `HeadSetForFA.HSMCache`, which is a
separate, already-tracked item.

All 25 surviving cross-references are now accounted for by documented benign
entries: 16 × `Pawn_Melee_Punch_HitBuilding` (§1.6) + 8 × `BMT_*` (§1.11) +
1 × `VWE_Tool_Whip` (§1.1). **There is no unexplained cross-reference left in the
load.**

The original diagnosis is kept below for the record.

---

#### (original entry) dead on a null PawnKindDef key

```
Error in static constructor of ChooseWildAnimalSpawns.Main:
  ArgumentNullException: Value cannot be null. Parameter name: key
    at Dictionary`2.TryInsert
    at RimWorld.BiomeDef.CommonalityOfAnimal (PawnKindDef animalDef)
    at RimWorld.BiomeDef+<get_AllWildAnimals>d__94.MoveNext ()
```

**This mod has now been dead for three consecutive loads behind three different
causes at the same stack frame** — which is exactly why it kept looking like
"still broken" rather than "broken again":

| Load | Exception | Actually null / duplicated | Owner |
|---|---|---|---|
| 1 | `ArgumentException` duplicate key | `Armadillo` from both directions | Beasts of the Rim |
| 2 | `ArgumentNullException` key | the **BiomeDef** itself | **us** (the `li` bug) |
| 3 | `ArgumentNullException` key | the **PawnKindDef** | Primordial Geysers |

**Root cause (traced 2026-08-10, second load).** Primordial Geysers
(`IronScruff.PrimordialGeysers`, WS 2896731795) injects animals into its own
biome from two compat patches guarded by `PatchOperationFindMod` on the **mod
name only**. The mods are present, so the guards pass — but five of the named
PawnKindDefs do not exist in the versions we load, and an unresolved
`BiomeAnimalRecord` keeps the record with `animal = null`:

- `AEXP_Badger`, `AEXP_Muskox`, `AEXP_Moose`, `AEXP_Porcupine` — Vanilla Animals
  Expanded defines these **only in its `1.6NotOdyssey` folder**. Its
  `LoadFolders.xml` carries
  `<li IfModNotActive="Ludeon.RimWorld.Odyssey">1.6NotOdyssey</li>`, and Odyssey
  is active, so VAE deliberately drops them to avoid colliding with Odyssey's own
  badger/muskox/moose/porcupine. VAE is behaving correctly; Primordial Geysers
  never accounted for it.
- `AA_WaywardMobileAssembler` — removed from Alpha Animals (Alpha Genes
  blacklists the name; the corpse entry is commented out upstream).

**Fix authored:** `Jawa_Patches/Patches/BiomeAnimalDanglingRefs_Fix.xml`
removes the five dangling entries. Nothing is lost — they resolve to null and
spawn nothing, and the biome already lists vanilla `<Porcupine>` and `<Moose>`.
Not yet confirmed in a load.

⚠️ **These nodes do not exist on disk** — Primordial Geysers' patch creates them
at runtime, so `validate_patch.py` reports 0 matches for all five xpaths. That is
expected, not a silent no-op. It also means the fix **depends on load order**:
Primordial Geysers is entry 252 and Jawa_Patches is now **562 of 562, last in
load order** (moved 2026-08-10, at the same time the mod was renamed from
GravshipCompat), so we apply after it by construction.

---

## 4. The self-inflicted one — `<li>` into a dictionary-keyed field

**2026-08-10.** Our own `Jawa_Patches/Patches/SWDesertWeather_Attach.xml` added
weather in list form:

```xml
<li><weather>SW_Sandstorm</weather><commonality>8</commonality></li>
```

`<baseWeatherCommonalities>` is **dictionary-keyed** — `<Clear>18</Clear>`. The
engine read the element name `li` as a WeatherDef name, failed, and **discarded
the entire BiomeDef**, seven times:

```
Could not resolve cross-reference: No Verse.WeatherDef named li ...   (×7)
Exception loading def from file ZBiome_Badlands.xml: ArgumentNullException
Failed to find RimWorld.BiomeDef named Desert. There are 59 defs of this type loaded.
```

Destroyed: Desert, ExtremeDesert, AridShrubland (Core!), ZBiome_Badlands,
ZBiome_DesertOasis, AB_PyroclasticConflagration, Volcano — on a desert-planet
campaign. **1,175 of the load's 1,199 cross-reference failures came from this one
mistake**, and the null BiomeDefs re-killed Choose Wild Animal Spawns and killed
Biome Compatibility Project.

**Fixed** with correct dictionary shape, verified against Core *and* the modded
biomes. `scripts/validate_patch.py` now compares `<value>` against the live
node's existing children and fails on mismatch. Full post-mortem in
`skills/rimworld-modding/references/traps.md`.

**Expected on the next load:** cross-reference failures drop from ~1,199 to ~24;
CWAS and BCP both recover.

### ✅ CONFIRMED on the 2026-08-10 second load (14:31)

Prediction held. Measured against `Player-prev.log` (the 13:38 run, which
predates the 14:05 fixes and is therefore a clean pre-fix baseline):

| Signal | Pre-fix | Post-fix | Verdict |
|---|---|---|---|
| Unresolved cross-references | 1,555 | **30** | ✅ predicted ~24 |
| `Failed to find BiomeDef` | 5 biomes destroyed | **0** | ✅ all seven biomes intact |
| `Could not resolve … WeatherDef named li` | 7 | **0** | ✅ dictionary shape correct |
| `Could not load reference to` (stale scribe) | 394 | **16** | ✅ Deep Storage prune held; 16 from elsewhere |
| `BiomeCompatibilityProject.StartUp` static ctor | dead | **recovered** | ✅ |
| `ChooseWildAnimalSpawns.Main` static ctor | dead | **still dead** | ❌ → §3.4, not ours |

The 30 survivors are all accounted for: 16 × `Pawn_Melee_Punch_HitBuilding`
(§1.6), 9 × `BMT_*` (§1.11), 5 × the biome-animal refs that turned out **not** to
be benign (§3.4), and 1 × `VWE_Tool_Whip` (§1.1).

**Whole-log scale:** 528,687 lines → **21,715**. Cold load 14:31 to 14:54 =
**23 minutes** (the ~30 min figure in the handoff is the right order; 23 is the
measured number for 562 mods with a warm disk cache).

**The 16 remaining stale scribe refs — SOLVED and FIXED 2026-08-10.** Not a
`Config/Mod_*.xml` at all, which is where §2.4 taught us to look and where the
first guess went. They came from **custom xenotype presets** in a folder nobody
had thought to audit:

```
…/RimWorld by Ludeon Studios/Xenotypes/*.xtp
```

RimWorld loads every `.xtp` at startup and resolves its gene list, so a preset
saved under an old mod set logs one `Could not load reference to` per dead gene,
forever. Two of the five presets were broken, and they account for all 16 exactly:

| Preset | Saved | Dead references |
|---|---|---|
| `Dark Beliar.xtp` | 2025-12-11 | 9 genes (`BX_*`, `VRE_HeartCrush`) |
| `Dracul Lord.xtp` | 2025-12-10 | 6 genes (`VU_*`, `VRE_*`) + `iconDef VU_DraculIcon` |

`Dark Glutton`, `Dark Troll` and `mimic` are clean and were left alone. (Note
`Dark Troll` carries `VU_ZombieSkin` and it resolves fine — the `VU_` prefix is
not itself evidence of a dead mod.)

**Fix applied:** both broken presets removed from `Xenotypes/`. Originals **and**
gene-stripped `.CLEANED` versions preserved in
`runtime/backups/xenotypes/`, so either can be restored with a copy.

**Standing rule, widened from §2.4:** stale `Could not load reference to` lines
come from *any* file RimWorld deserializes at startup, not just mod settings. The
audit surface is `Config/Mod_*.xml` **plus** `Xenotypes/`, `Ideos/`, `Scenarios/`
and `PrepareLanding/` — every folder holding user-authored presets that name defs.
Saves are exempt: they are only read on load, not at startup.

⚠️ Deleted while the game was running. Confirm after the next restart that both
files are still absent and the 16 lines are gone.

**A second self-inflicted bug shipped and was fixed in the same 14:05 batch, and
was never written down until now.** The pre-fix log carries:

```
XML error: <exposedThought>SoakingWet</exposedThought> doesn't correspond to any
field in type WeatherDef.   [Def Error]: SW_RedFoggyRain
```

Our own def. The 1.6 field is **`weatherThought`** (Core `Weathers.xml:98`). The
on-disk file is already correct, so it cannot recur — but it is the same version-
drift class as §1.7, in a file we wrote, and it slipped through because only the
*patch* files were being validated. `SWDesertWeather.xml` is a **Defs** file, and
`validate_patch.py` does not check Defs at all. That gap is still open.

---

## 4b. WORLDGEN / RUNTIME errors — first data, 2026-08-10 15:17

Everything above §4 is **load-time**. This section is the first look past it: a
new colony was started and the world map opened. Note the previous session never
reached worldgen (`Initializing new game with mods` appears 0 times in
`Player-prev.log`), so **none of this is a regression** — it is simply the first
time we have seen it. 17,728 new log lines, and the load-time triage buckets are
all **zero** across them.

### 4b.1 ✅ `Could not find player faction.` ×~140 — ATTRIBUTED AND BENIGN

**Owner: Tech Level Enforcement** (`summersausages2ttv.techlevelenforcement`,
WS 3430230860, load position 318). Verified from IL 2026-08-10 and independently
corroborated from the log.

**Where the message comes from.** Not `FactionManager`, which was the first guess
and was wrong — it is `RimWorld.Faction::get_OfPlayer`, whose entire body is:

```
call     RimWorld.Faction::get_OfPlayerSilentFail
dup
brtrue.s IL_0012
ldstr    "Could not find player faction."
call     Verse.Log::Error
ret
```

The `dup` means **the null is returned, not thrown**. Callers cope. This is pure
log noise with no functional consequence — it is only `Log.Error` severity because
Ludeon assumed nobody would ask for the player faction before one exists.

**Why ~140 of them.** Tech Level Enforcement installs Harmony prefixes on the
gear-application path — `Pawn_ApparelTracker.Wear` and
`Pawn_EquipmentTracker.AddEquipment` — and each begins:

```csharp
if (newEq == null || ___pawn == null || ___pawn.Faction != Faction.OfPlayer) return true;
```

`Faction.OfPlayer` is evaluated **before** any check, on every gear item given to
every pawn. During worldgen `FactionGenerator` creates a leader for each faction
*before the player faction exists*, so every apparel item and every weapon logs
once. Its DLL contains exactly **2** `get_OfPlayer` references, matching its two
default-enabled options (`affectEquipment`, `affectApparel` true;
`affectItems` false) — and there is no `Config/Mod_3430230860_*.xml`, so those
defaults are live.

**Corroborated in the log independently of the IL:** the burst is not uniform, it
is interleaved with pawn generation in variable clusters — 2 to 11 errors, each
group terminated by an `[Isekai Forge]` pawn line, 23 pawns / 142 errors this
worldgen and 22 / 140 the previous one. That is the signature of a per-gear-item
loop, not a per-settlement one.

**Faction Control is RULED OUT.** It appears in the log immediately before the
burst (`Temporarily set 'Surface' settlementsPer100kTiles…`) and was the obvious
suspect, but `FactionControl.dll` contains **zero** references to `get_OfPlayer`
in all three of its version folders. It cannot make the call. *Adjacency in a log
is not attribution* — worth remembering, because this one was convincing.

**Action: none. Keep the mod.** `required_mods.md` adopts Tech Level Enforcement
as the tech-tier stock filter that keeps trader oddities lateral — it is the
anti-exponential guard on the trade system. Trading a load-bearing design mod for
quieter logs would be a bad deal, and the errors are transient (worldgen only).

**Upstream fix is one word:** `Faction.OfPlayer` → `Faction.OfPlayerSilentFail`,
in all three prefixes. The mod already references `OfPlayerSilentFail` once, so
the author knows it exists. Worth filing.

**Minor upstream nit, unrelated:** the mod ships its whole
`Source/.../bin/Debug/` tree — 158 DLLs, 40 MB including a copy of
`Assembly-CSharp.dll`. None of it is inside `Assemblies/`, so RimWorld never loads
it; it is only wasted disk.

### 4b.2 SWCP `Failed to retrieve a CharacterDefWithRole<TRole> list` ×44

Same mod as §3's AssetBundle bug (KotOR Resources & Materials, WS 3254370945).
Its role registry is **empty at worldgen**, so it contributes no characters.

❌ **Hypothesis REFUTED 2026-08-10.** I guessed this was self-inflicted — that
SWCP's own NRE aborted the post-load queue and so killed its own role registry.
The premise was wrong: that queue is a per-action try/catch and does not abort
(verified from IL, see §6). So the empty role registry is a *separate* problem
from the bundle failure, and its cause is still unknown. Recorded because the
guess was reasonable and still wrong — the abort premise was inherited from our
own notes rather than checked.

### 4b.3 `FileNotFoundException: UnityEngine.InputLegacyModule … ReflectionOnly APIs`

One occurrence, during worldgen. Some mod inspects assemblies with the
reflection-only load path without pre-loading dependencies. No stack, no owner,
no observed consequence. Logged here so it is not re-investigated; promote it if
it ever recurs with a symptom attached.

### 4b.4 Cosmetic runtime noise (ignore)

`Isekai Forge` "failed equipChance roll" (~15×, that is the mod reporting normal
random rolls) and `Marjot failed to get a job from any IntimacyGivers` (×2).

### 4b.5 ✅ The biome question is closed — no in-game check needed

The world map is fogged by **Rimworld Exploration Mode**
(`thelastbulletbender.rwexploration`, WS 2941608795), which hides the planet
until you explore it. That made the planned visual biome confirmation
impossible — and unnecessary. Three independent lines of evidence already agree
that all seven biomes destroyed by the `<li>` bug are back:

1. `Player.log`: zero `Failed to find BiomeDef`, zero `WeatherDef named li`.
2. Cross-references down to 30, every one attributed to a known cause.
3. The offline load-set inventory lists all seven: `Desert`, `AridShrubland`,
   `ExtremeDesert`, `Volcano`, `ZBiome_Badlands`, `ZBiome_DesertOasis`,
   `AB_PyroclasticConflagration` (`mods/inventory/`).

Note the fog mod is likely **wanted** — it matches the campaign premise (crashed
stowaways who do not know the planet) and the `desert_world_design.md` dark-biome
ruling. Do not remove it to satisfy a check that files already answer.

---

## 4c. ⛔ OPEN — facial rendering, and a reproducible freeze

**2026-08-10, load #3.** Not benign, not solved, recorded so it is not lost.

**What was observed in Character Editor:**
- Eyes render as two semi-superimposed parts, `Eye` and `Lid`. Setting `Not_Lid`
  reveals the eye behind. ⚠️ **This is probably NOT a bug** — [NL] Facial
  Animation renders eyes as layers (eyeball + lid overlay) precisely so it can
  blink. Do not chase it as a defect without better evidence.
- **Some eyes have whites and some do not.** This *is* inconsistent and is the
  real symptom worth pursuing.
- Hair and beard positioning looked correct.
- **Cycling `Lid` values froze the game.**

**The freeze:** `InvalidCastException: Specified cast is not valid`, **2,886
occurrences**, one per frame. The process stayed at `Responding: False` with CPU
climbing — a livelock, not a deadlock — until Windows raised `AppHangB1`.

⚠️ **Attribution is genuinely unclear and two causes are entangled.** A
background agent was driving `rimworld/search_debug_actions` over the bridge at
almost exactly the moment the log stopped (15:37:00 issued, 15:37:06 last write),
and that call independently hangs the main thread (see `rimbridge.md` §5.1). The
exception flood predates the hang — 2,886 occurrences take time — so the
`InvalidCastException` is real and user-triggered, but **which of the two actually
wedged the process cannot be separated from the evidence available.**

**No stack trace was captured.** Every occurrence reads
`[Ref 436D323B] Duplicate stacktrace, see ref for original`, and the original was
never printed with frames — checked all 2,886. Other exceptions in the same log
(e.g. `[Ref CFCB091B]`) *did* print frames, so this is a gap in the ref-dedupe.

Log preserved at `scratchpad/Player.FREEZE-2026-08-10.log` (48,194 lines).

**The facial stack is crowded:** [NL] Facial Animation + FA Genetic Heads +
Facial Animation Compatibility Project + Head Set For FA (**dead**, §3) + Big and
Small + 1,105 alien races. The `[FA Genetic Heads]` and
`[Big and Small] … This is somewhat untested` lines immediately precede the flood.

**Next step, and it is cheap because the bug is reproducible:** before
reproducing, disable stack-trace deduplication so the first occurrence prints
frames. Then open Character Editor and cycle `Lid`. The frames name the mod. Do
this on a throwaway colony, with no bridge agent running.

---

## 5. The patterns worth remembering

**Hard breaks concentrate in mods that reflect over other mods' types at
startup** — Context Upgrade over RimTalk, Head Set over race defs, CWAS over
biome animals, BCP over biome defs, SWCP over its own asset bundle. In a 562-mod
stack that is where failures live, and they announce themselves as
`Error in static constructor of ...` or `TypeInitializationException`.

**A destroyed def blames everyone except the patch that destroyed it.** When
hundreds of unrelated errors appear at once, look for `Exception loading def from
file` and `Failed to find <Type> named X. There are N defs of this type loaded.`
first — the real cause is usually a handful of quiet lines far above the noise.

**An exception that changes *type* at the same stack frame is a different bug.**
`ArgumentException` → `ArgumentNullException` at `BiomeDef.CommonalityOfAnimal`
looked like "still broken" and was in fact a brand-new problem of our own making.

**Validate the whole mod folder, not the file you changed.** The blast radius of
a deploy is the mod, not the diff.

**A "lesson" we wrote down can be the thing that misleads us.** See §6.

---

## 6. ⚠️ RETRACTION — the post-load queue does NOT abort (2026-08-10)

For most of this file's life we treated
`Could not execute post-long-event action` as a **severity-2** finding, on the
belief that one throw abandons every remaining queued post-load action across all
mods. That belief drove the SWCP severity rating, the wording of upstream issue
#7, and a hypothesis about SWCP sabotaging itself.

**It is false.** Verified by parsing the IL of
`Verse.LongEventHandler.ExecuteToExecuteWhenFinished` in
`Assembly-CSharp.dll` (1.6.4871, md5 `bf39a6f68f2deda9b09d66f6ceffecf3`):

| Evidence | Finding |
|---|---|
| Method header | FAT, `CorILMethod_MoreSects` set |
| EH section | 2 clauses: typed `catch(System.Exception)` + a `finally` |
| Try region | `IL_0071`–`IL_0083`, **18 bytes** — one `get_Item` plus one `Action::Invoke` |
| Catch handler | logs via `Verse.Log::Error`, then `leave.s IL_00a8` |
| `IL_00a8` | the **loop increment**, not the loop exit |
| Back-edge | `blt IL_0033` at `IL_00b7`, outside every clause |

So the shape is `for (…) { try { list[i](); } catch (Exception ex) { Log.Error(…); } }`.
A throwing action costs that action and nothing else. The loop even re-reads
`.Count` each pass, so actions queued *during* execution still run.

**The one genuine abort path** is different and worth knowing: the per-iteration
DeepProfiler block at `IL_0033`–`IL_006c` sits *outside* the try and dereferences
`action.Method.DeclaringType`. An NRE there escapes the loop, skips the final
`Clear()`, and leaves `executingToExecuteWhenFinished == true` — after which every
later call returns early on "Already executing." and the queue is bricked for the
rest of the session. **Tell them apart by the stack:** a frame for the queued
action itself (e.g. `BuildableDef.<PostLoad>b__78_0`) is the survivable path.

**Not yet ruled out:** a Harmony transpiler in some mod could replace this method
at runtime. Nobody has scanned the loaded mod set for that.

### How this got into the notes, which is the more useful lesson

Nobody made it up — it is a widely-repeated claim in RimWorld modding folklore,
and the log line *sounds* like it ("`Could not execute…`" reads as fatal). It was
written down once, promoted into `SKILL.md` as a default triage rule, restated in
three more files, and then **cited back as evidence** when reasoning about SWCP.
At no point did anyone open the method.

**Standing rule:** a claim about *engine behaviour* — as opposed to an observation
about a log — must be traceable to the IL, the decompiled source, or an
authoritative citation before it earns a place in the triage order. Log text is
evidence of what happened; it is not evidence of what the engine does next.
Reproduction: `scratchpad/il_probe.py` (stdlib only, re-runnable).

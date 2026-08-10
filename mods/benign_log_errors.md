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
2. Exceptions inside `LongEventHandler.ExecuteToExecuteWhenFinished` — these
   abort the rest of the post-load queue, so unrelated mods silently lose work.
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
**Why harmless:** the engine says it outright — *"using undefined sound"*. Falls
back gracefully; the punch is silent against buildings for those races.
🔎 Suspected source: **Fists Aren't Made of Steel**. Not confirmed. Cosmetic.

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
| `[SWCP Core/Tools] Failed to load bundle ... SWCPshaders` → `BuildableDef.ResolveIcon()` NRE | **Upstream packaging bug**, reported 2026-08-10. The mod ships `SWCP_Core.dll` referencing an AssetBundle it never includes — absent from the Workshop upload *and* the GitHub repo. Serious because the NRE fires inside `LongEventHandler.ExecuteToExecuteWhenFinished` and **aborts the rest of the post-load queue**. |
| `HeadSetForFA.HSMCache` → NRE in `CheckSettingData(ThingDef raceDef)` | Head Set For [NL] Facial Animation is not applying. **Parked** pending the facial-animation visual test — if faces look right without it, drop the mod. |
| `ChooseWildAnimalSpawns` → `ArgumentNullException: key` | **Still dead — but the cause is now known and is NOT ours.** See §3.4. BCP recovered; CWAS did not, and that turned out to be the genuine separate bug this row predicted. |

### 3.4 `ChooseWildAnimalSpawns` dead on a **null PawnKindDef key** — fix authored, not yet loaded

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

### 4b.1 `Could not find player faction.` ×140 — ⚠️ open, unattributed

Bare line, no stack. It is vanilla `FactionManager.OfPlayer`, which does
`if (ofPlayer == null) Log.Error("Could not find player faction.")`. So some mod
queries `Faction.OfPlayer` during world generation, before the player faction
exists.

**This is almost certainly why the debug window popped up** — RimWorld
auto-opens it on `Log.Error`, and these are 140 of them.

Fires in two bursts during worldgen. Probably harmless in itself (the getter
returns null and callers generally cope) but the volume is bad and it drowns the
window. **Not attributable from the log as it stands** — the message carries no
stack trace. To pin it: dev mode, then in the debug log window enable stack
traces / "log all messages", regenerate a world, and read the first occurrence.
Worth doing on a world we are throwing away anyway.

### 4b.2 SWCP `Failed to retrieve a CharacterDefWithRole<TRole> list` ×44

Same mod as §3's AssetBundle bug (KotOR Resources & Materials, WS 3254370945).
Its role registry is **empty at worldgen**, so it contributes no characters.

🔎 **Hypothesis worth testing, not yet confirmed:** this may be self-inflicted by
the *same* bundle bug. SWCP's NRE fires inside
`LongEventHandler.ExecuteToExecuteWhenFinished`, which aborts the remainder of
the post-load queue — and if SWCP populates its own role registry from an action
queued behind the thrower, the mod kills its own initialisation. If so, one
missing file explains both symptoms, and the mod is currently contributing
nothing but errors. That would upgrade it from "watch upstream" to "disable
until fixed."

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

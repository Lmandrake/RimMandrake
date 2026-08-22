# BUILDABLE.md — what the stack can and cannot give us

> 🔴 **STANDING OWNER RULING — 2026-08-15. THERE IS NO WORLDGEN FEATURE, IN ANY VERSION.**
>
> Verbatim: *"There is no auto worldgen we are building. The world will be user-made and
> frozen. We are NOT enabling worldgen, we will provide players a savegame with a fixed
> world, period. That's it. True worldgen is OUT of any version, even v2."*
> Clarified moments later: *"(but designing worldgen by hand and design documents to
> guide that are in)"*
>
> **OUT, permanently — this is not a deferral:**
> - Any automated or programmatic worldgen we build. No tool, script, DLL or bridge verb
>   that generates a world as a product.
> - Worldgen as a player-facing capability. **Players never generate anything.** They
>   receive a savegame containing the fixed world.
> - Any v2 worldgen item. ⛔ **v2 is NOT a parking space for this** — mark such work
>   dead, do not move it to `design/V2_DREAMS.md`.
>
> **IN, unchanged and still wanted:**
> - The owner building the world **by hand, once**. That is how the fixed world exists.
> - **Design documents that guide him doing it** — `WORLDGEN_FACTION_CHECKLIST.md`,
>   `SCENARIO_SETTINGS_SPEC.md`, the faction, biome and terrain specs. Keep writing them.
>
> 🔑 **The consequence, and it got stronger rather than weaker:** one hand-made world,
> frozen, then shipped to every player. **A faction, ideoligion or setting absent when he
> builds it is absent from every player's game forever, with no regenerate to fall back
> on.** That is why the faction roster and the faith text stay v1.


BUILD publishes here. **One line per fact**, written when a limit or a capability is
learned that DECIDE would otherwise have to ask about: what a def type supports, what
a mod already gives us, what the engine refuses.

**Replace a superseded line. Never append a correction under it** — a stale line above
its own correction still gets read first.

Every line carries the date and how it was measured. A fact with no measurement behind
it does not belong here.

---

## What the stack already gives us

- **Lightsabers are LIVE and plentiful — 14 `ThingDef`s.** `Force_Lightsaber_Custom`
  (plain), `_Dual`, `_Curved`, `_Crossguard`, `_Shoto`, `_Inquisitor`,
  `_BuildYourOwn`, `_UniqueObi`, `_UniqueAnakin`, `Force_Ezra_BlasterLightsaber`,
  plus throw/whip/projectile defs. Mod `lee.theforce.lightsaber`, active.
  *Measured 2026-08-15 against the def dump refreshed at that load.* ⚠️ Absence from
  a screenshot is not absence from the build — that inference nearly became a
  "missing weapon" item.
- **All 8 authored Jawa `FactionDef`s load.** `Jawa_IndigenousTribes` (label "Jawa
  Trade Moot"), `Jawa_HuttCartel`, `Jawa_Junkers`, `Jawa_DeepwaterCompact`,
  `Jawa_GeonosianFoundryHive`, `Jawa_WildsteamClan`, `Jawa_AscendantHelix`,
  `Jawa_FreeDroidEnclaves`. *Live via `jawa/get_def`, 8/8, 2026-08-15.*

## What the engine refuses, and what that costs

- **Only `Jawa_IndigenousTribes` carries `requiredCountAtGameStart`.** The other
  seven are `canMakeRandomly` with no required count, so they default to **0** at the
  Configure Factions screen and a world generated without hand-ticking them contains
  none of them. **Worldgen happens once.** *Measured on disk 2026-08-15; filed as
  `seven-factions-have-no-required-count-9c4e17`.*
- **A `PatchOperationFindMod` that FAILS proves the mod is PRESENT.** An absent mod
  returns **true** and logs nothing, so the failure can only mean an inner op broke.
  `<mods>` matches the About.xml `<name>`; `<activeMods>` lists the `packageId`.
  *2026-08-15, cost one wrong diagnosis and two seats' time.*
- **Patches run on RAW XML, before `ParentName` inheritance.** A def that only
  *inherits* a container has no such node to patch, so an add-if-missing `<nomatch>`
  aimed at that container fails — and `PatchOperationSequence` stops at the first
  failure, silently killing every op after it. **Any generator that decides what to
  patch by reading a RESOLVED def dump will emit this bug.** *2026-08-15.*
- **Nothing on the 155-tool bridge can order an attack.** `jawa/order_pawn` issues a
  GOTO even with a `targetId`; drafted pawns hold at `Wait_Combat`; spawned hostiles
  have no lord and idle. Blocks every combat test. *2026-08-15,
  `bridge-cannot-order-a-melee-attack-3f8c21`.*

- 🔴 **A `ThingOwner<Pawn>` on a custom `WorldObject` IS TICKED, and copying `Caravan`
  literally would delete the cast.** Two shipped mechanisms bite, and neither is
  documented anywhere: (1) `WorldObject.DoTick` walks its child holders and calls
  `ThingOwner.DoTick` on each, skipping only owners that are `is Map` or `is Caravan`
  — a hardcoded type test a mod cannot join, so an off-map roster's needs fall and it
  starves in a box. The supported opt-out is `IThingHolderTickable` with
  `ShouldTickContents => false`. (2) `Caravan.pawns` uses `LookMode.Reference` and is
  safe only because caravan pawns are registered with `WorldPawns` AND
  `WorldPawnGC.GetCriticalPawnReason` carries an explicit `p.IsCaravanMember()` test;
  a custom holder matches none of that method's tests, so every pawn would be
  collected between visits. Use `LookMode.Deep` and keep them out of `WorldPawns`.
  *Read off the 1.6 decompile 2026-08-20 — `RimWorld.Planet/WorldObject.cs` DoTick,
  `RimWorld.Planet/WorldPawnGC.cs` GetCriticalPawnReason — while building `Inhabited`.*
- **The last moment a departing map's pawns are still enumerable is a prefix on
  `Verse.Game.DeinitAndRemoveMap`.** It runs `Notify_MyMapAboutToBeRemoved()`, then
  `MapDeiniter.Deinit`, whose FIRST act is `PassPawnsToWorld` — which despawns every
  pawn and hands it to `WorldPawns`. `MapComponentUtility.MapRemoved` fires after
  that and is too late to recover anybody. *1.6 decompile, 2026-08-20.*
- **`Lord.ExposeData_StateGraph` saves the current toil and each toil's data by
  POSITIONAL INDEX**, then re-runs `CreateGraph()` on load and looks those indices up
  in the freshly built graph. Any `LordJob` we intend to re-tune must therefore return
  a graph of exactly one toil, forever, and put the schedule in ordinary C# inside it.
  *`Verse.AI.Group/Lord.cs`, 1.6 decompile, 2026-08-20.*

- 🔴 **`requiredCountAtGameStart` is a WORLDGEN-ONLY field. There is NO load-time top-up.**
  It is read in exactly one place — `FactionGenerator.InitializeFactions`, reached only
  from `WorldGenStep_Factions`. The only load-time faction top-up is
  `BackCompatibility.cs`, and it is a **hardcoded list of five**: `Empire`, `HoraxCult`,
  `Entities`, `TradersGuild`, `Salvagers`. ⇒ **A faction absent when the world was
  generated can NEVER appear by patching a def afterwards** — it must be created by hand
  or the world regenerated. This is the owner's *"absent when he builds it is absent
  forever"* wearing its mechanism. *1.6 decompile, 2026-08-20. It corrects a claim that
  was written into `RebelAlliance_Suppress.xml` and `Jawa_Patches/About/About.xml`; both
  are fixed.*
- 🔴 **`replacesFaction` SILENTLY DELETES a faction from worldgen, and it is another mod's
  field.** `InitializeFactions` skips def X entirely when ANY def Y has
  `requiredCountAtGameStart > 0 && Y.replacesFaction == X`. **Biotech's `PirateWaster`
  replaces vanilla `Pirate`** — the def our `BlackstarCompany.xml` reskins — so the
  Blackstar Company can never be generated while Biotech is active, no matter what weight
  or count we patch onto it. **Before reskinning ANY vanilla faction, check what replaces
  it:** six defs in this 578-mod build declare `replacesFaction`, three of them aimed at
  `OutlanderRough`. *1.6 decompile + the 578 def dump, 2026-08-20.*
- **A faction's NAME is not its def's label.** `Faction.Name` returns a stored name if one
  was generated and only falls back to `def.LabelCap` when that is null, so patching
  `label` after worldgen changes nothing the player sees. `fixedName` on the def prevents
  the generated name in the first place; `jawa/faction_name_set action=clear` repairs a
  world that already has one. *Measured live 2026-08-20: ten of eleven campaign factions
  were wearing generated names.*

- 🔴 **`weaponMoney` is a CEILING rolled ONCE, and `min` is what decides whether a kind
  arms RELIABLY.** `PawnWeaponGenerator.TryGenerateWeaponFor` rolls
  `weaponMoney.RandomInRange`, keeps every weapon priced **at or below** that roll, and if
  the pool comes back empty **the pawn spawns bare, silently**. ⇒ `max >= cheapest` means
  the kind *can* arm; **`min >= cheapest` is what makes it always arm.** A `min` below the
  cheapest tagged weapon leaves a band of rolls that arm nobody — this project's own notes
  had it backwards twice. Check with
  `python3 src/RimMandrake/Utils/weapon_affordability.py`. *1.6 decompile + the 578 dump,
  2026-08-20.*
- 🔴 **A weapon with no `MarketValue` statBase is not cheap — it is COMPUTED, and the def
  dump cannot show you the number.** `StatWorker_MarketValue` falls through to
  `CalculatedBaseMarketValue`, which prices the thing from its recipe:
  `Σ(costList.count × ingredient.BaseMarketValue)` plus `WorkToMake × 0.0036`, over the
  product count. **Every Outer Rim weapon is in this state** — they declare MaxHitPoints,
  Flammability, DeteriorationRate and Beauty and nothing else — so "read the value off the
  def" returns nothing and treating a missing number as 0 makes an empty pool look like the
  cheapest one. `OuterRim_DroidWeapon_BlasterCannon` computes to **982.5**.
  `weapon_affordability.py` reproduces the formula. *2026-08-20.*

## 🪤 A WSL SYMLINK UNDER `LocalLow` IS INVISIBLE TO THE GAME — measured 2026-08-21

`ln -s` on `/mnt/c/...` **succeeds**, and `ls -la` shows a normal-looking
`lrwxrwxrwx ptr -> target`. It is not a normal symlink. Windows sees the reparse
point (`Mode d----l`) but resolves **nothing** — `LinkType` and `Target` both come
back empty, and reading a file through it fails `PathNotFound`:

```
ptr    d----l  {}      <- PowerShell, same directory, same second
target d-----  {}
Get-Content ...\ptr\probe.txt : Cannot find path ... because it does not exist.
```

⇒ **RimWorld and any C# tool cannot follow a symlink WSL created there.** It is a
WSL-format link, not an NTFS one, and only WSL can read it back — so a check done
from bash reports success and the game still cannot see the file.

🔑 **Consequence for any layout that needs a "pointer".** Use a plain FILE holding
a name, or derive the pointer from the data. `DUMP_STORAGE_LAYOUT_RULING_1`
originally proposed `current`/`official` symlinks; measured, it needs neither —
capture ids are ISO-8601 timestamps, so **current is `max(dirname)`** and
**official is whatever `dumps/REGISTRY.jsonl` freezes**. Nothing to desync.

⚠️ This does NOT say symlinks are broken everywhere. `.claude/skills/<name>` →
`skills/<name>` works fine — those are inside WSL's own view and nothing Windows
reads. The rule is narrower: **a link the GAME must traverse cannot be made from
bash.**

## Deploy targets that are not `Mods/`

- **`Xenotypes/*.xtp` and `Ideos/*.rid` are deploy targets.** They live under
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`,
  nothing syncs them from the repo, and `deploy_custom_mods.py` does not cover them.
  A `.xtp` **bakes at world creation** and a stale one drops renamed genes **silently
  in play**. *2026-08-15: `MandrakeJawa.xtp` had been correct in the repo since
  `c57f347` and stale in the game for a day, dropping four genes.*
- **An offline validator cannot catch a stale `.xtp`.** It validates the file you
  point it at; the game reads a different copy. Check the deployed one.
- 🔴 **An offline validator answers "is this file self-consistent", never "is the file
  the game reads correct".** `validate_save_artifact.py` returned **36/36 resolve** on
  `MandrakeJawa.xtp` twice — once on a file the running engine was contradicting, once
  on a freshly deployed one it had not yet read. Same output, opposite meanings. A
  deploy is **FIX DEPLOYED, UNVERIFIED** until a startup log shows zero
  `Could not load reference to`. *2026-08-15.*

## Limits found 2026-08-20 — the repo's filesystem, and four def-dump blind spots

- 🔴 **`/mnt/d` is a 9p / DrvFs mount, NOT a local filesystem, and `O_APPEND` is not
  atomic there.** 12 writers × 250 events of ~160 bytes lost **five of every six** and
  tore hundreds of lines, twice; the same test on tmpfs was 3000/3000. An exclusive
  `flock` fixes it completely at ~2 ms/event, and flock ALONE is sufficient — 9p fails
  to serialise the *writes*, not the append offset. ⚠️ flock is advisory, so
  `rimflow.model.append()` is the only safe writer of the ledger; a shell `>>` still
  tears lines. *Anything appending concurrently from more than one process on this repo
  needs a lock, whatever POSIX says.*
- ⚠️ **Per-file syscalls on that mount cost ~0.8 ms.** `stat`-ing 144 files is 130 ms,
  `open`+read is 209 ms; on tmpfs the same loop is 0.8 ms. **Any freshness-checking
  cache is over a 100 ms budget before it parses anything** — the floor is the
  filesystem, not the code. Cache in-process instead: warm replay is ~1 ms.
- 🔴 **`pawnGroupMakers` for `OutlanderCivil` lives on the ABSTRACT parent
  `OutlanderFactionBase`.** An xpath at `FactionDef[defName="OutlanderCivil"]/
  pawnGroupMakers` **matches nothing, and a patch that matches nothing logs nothing.**
  Wiring a pawnkind into that faction means patching the abstract base, which reaches
  every Outlander faction. *This is why five authored `Jawa_Homestead_*` kinds spawn
  nowhere.*
- 🔴 **`TileMutatorDef` in the def dump carries ONLY `defName` and `label`.** No
  `biomeWhitelist`, no `averageTemperatureRange`, no `workerClass`. A whitelist question
  can only be answered from the mod's own XML. *Checking the dump for
  `ZBiome_DesertOasis` in the `Oasis` whitelist returned "absent" — from a field that
  does not exist in the dump at all. A false negative that reads exactly like a real one.*
- ⚠️ **`GameConditionDef.temperatureOffset` reads `-10` for ALL 89 defs in the dump.**
  That is a dump default, not a per-def value. Do not use those numbers for anything.
- 🔑 **A long-running server is a cached copy of the code.** The board on `:8787` had
  been up five days and predated the `/board` route, so every module request fell through
  to the HTML page and the browser imported markup as JavaScript. **Every check that day
  had spun up a fresh instance on a spare port and passed.** Verify against the process
  that is actually running, not one you just started.
- 🔴 **A missing facing does NOT go magenta, and that makes "no magenta" useless as an
  art-gap test for any `Graphic_Multi` thing.** Read off `Verse/Graphic_Multi.Init`
  2026-08-21: `_north` absent falls back to `_south` with
  `drawRotatedExtraAngleOffset = 180f`; `_east`/`_west` absent fall back to each other
  **flipped**; `_south` absent falls back to whatever filled slot 0. `BaseContent.BadMat`
  and the log line `Failed to find any textures at <path>` fire **only when all four
  suffixed paths AND the bare path miss**. ⇒ Magenta is the right instrument for a
  WHOLLY missing texture (that is how the D-CHK2 heads were found); it can never see a
  partially-shipped directional set.
- 🪤 **Overriding another mod's texture is PER FILE, so a partial reskin mixes the two
  mods' art on one thing.** `ContentFinder<T>.Get` walks `LoadedModManager.
  RunningModsListForReading` **backwards** (`for (num = Count-1; num >= 0; num--)`) and
  returns the first hit for that exact itemPath — last mod loaded wins, one path at a
  time. Ship `AV_OxCart_south.png` at the donor's own path and leave `_north` out, and
  the game draws OUR south beside the DONOR's north: banthas from one side, oxen from
  the other, **no error and no magenta**. Author every facing the donor authors.
- 🔴 **A VEHICLE's `_north` cannot be derived, and the fallback that looks like it can is
  a trap.** Corrected 2026-08-21, same day the line above first said otherwise.
  `Vehicles.Graphic_Rgb.GetTextures` does set `drawRotatedExtraAngleOffset = 180f` when
  `_north` is absent — but **the vehicle BODY never reads it.**
  `Graphic_Rgb.ParallelGetPreRenderResults` builds its quaternion from
  `orientation.AsRotationAngle + rotation` alone, and `AdjustAngle`'s North case is an
  empty `break`. The only two readers are `CompDrawLayer.AngleFromRot` and
  `CompDrawLayerTurret.AngleFromRot`, which draw ADD-ON LAYERS rather than the body, and
  both sit behind `ShouldDrawRotated` (`MatEast == MatNorth && MatWest == MatNorth`),
  which is false the moment a real `_east` ships. ⇒ Ship `_south` with no `_north` and
  the north facing draws the south sprite **unrotated, rear end pointing north**, in
  silence. ✅ `_west` IS genuinely derived (`westFlipped`), which is why neither Alpha
  Vehicles Neolithic nor our DogSled ships one: **the authored set is north+east+south.**
- ⚠️ **A mod DLL that references `Vehicles.dll` or `SmashTools.dll` must target `net48`,
  not `net472`.** Both are built against 4.8 and MSBuild refuses to resolve them from a
  4.7.2 target with `MSB3274`. Measured 2026-08-21 building `DesertVehicleReskin.dll`.
  Everything else in this repo is `net472` and stays there.
- 🔑 **`RimWorld.FoodTypeFlags` values are NOT the obvious powers of two, and two of them
  decide what a herbivore will eat.** Read off `RimWorld/FoodTypeFlags.cs`:
  `Seed = 0x10` (16, standalone) · `Fungus = 0x1001` (4097, i.e. it CARRIES the
  `VegetableOrFruit` bit) · `Kibble = 2048` (standalone, **not** part-plant).
  ⇒ A `Plant | VegetableOrFruit | Meal` test admits `RawFungus` for free, and silently
  REJECTS `RawRice` and `Kibble`.
- 🪤 **`jawa/texture_audit` reports a DEAD texPath for any def whose art is resolved by a
  MOD'S OWN `graphicClass`, and those are false positives.** Measured 2026-08-21 against
  the 01:23 first-light run: of 53 "dead" paths, **39 belong to Tribal Furniture**
  (`xercaine.tribal.furniture`), whose 13 flagged defs all declare
  `<graphicClass>TribalFurniture.Graphic_Appearances_Multi</graphicClass>` out of its own
  `TribalFurniture.dll`. Its `texPath` is a STEM the class expands with a stuff infix, so
  the file on disk is `XERTribalBed_Bricks_north.png`, not `XERTribalBed_north.png` — all
  138 PNGs are present and the furniture renders. The audit assumes vanilla
  `Graphic_Multi`/`Graphic_Single` suffixing and cannot see a custom resolver.
  ⇒ **Before acting on any texture_audit row, read that def's `graphicClass`.** A row
  whose class is not a `Verse.Graphic_*` is UNJUDGED, not broken.
- 🔴 **THE DEF DUMP SILENTLY DESTROYED 824 DEFS, AND A TYPE READING `0` THERE MEANS
  NOTHING.** `defs/<Type>.json` was keyed on the type's SIMPLE name, but 532 def types
  share only **517** distinct simple names — so 13 files were written two or three times
  and the last writer won. Measured on the 2026-08-21 08:20:20Z capture: `AbilityDef`
  **612 → 0**, `FaceTypeDef` **152 → 0**, and depending on write order `SymbolDef` (9,099),
  `StructureLayoutDef` (301) and `CharacterDef` (269) are the same coin landing the other
  way. ⇒ **"Zero X in the dump" is UNMEASURED, never negative** — the type may simply have
  lost the race. Fixed 2026-08-21 (`d7cf154`): colliding types now write `<FullName>.json`
  and the manifest carries `defTypes` / `defTypeCollisions`. ⚠️ That fix is in the
  ASSEMBLY, so it does nothing until the dumper is redeployed and the game reloaded — any
  dump captured before that is still lying.

---

## 🔴 INSTRUMENTS THAT RETURN A CONFIDENT WRONG ANSWER

Owner, 2026-08-21, after the def-dump collision: *"Did we fix all of these string issues so
we don't keep generating false negative results? This is very disturbing."*

**The honest answer was no.** Seven instruments were caught lying in a single session, and
only some were fixed. This is the register; it is here rather than in seven ledger notes
because a note is not on anyone's path.

🔑 **The shared shape, and it is worth naming once:** every one of these returns a NUMBER.
None errors, none warns, none returns null. A wrong count reads exactly like a right one,
so the failure is invisible unless you already suspect the instrument. ⇒ **When a count
decides something expensive, check the instrument against a case whose answer you already
know** before you trust the case you don't.

| # | instrument | what it returned | status |
|---|---|---|---|
| 1 | `strings -a -el` on a .NET assembly | **16** of 115 tool names — implying 99 live tools were missing | 🛡️ **refused at the tool call** |
| 2 | `grep` a `.rws` for biome defNames | **2**, where the CSV holds 3 / 233 / 31 | 🛡️ **refused at the tool call** |
| 3 | def dump `defs/<Type>.json` | `AbilityDef` **0**, having written 612 | ✅ **fixed** `d7cf154` (undeployed) **+ caught offline** |
| 4 | `weapon_tag_audit` "emptied by the cut" | **0**, structurally guaranteed | ✅ **fixed** |
| 5 | `jawa/texture_audit` | **53** dead paths, 39 of them present art | 📋 **filed**, `TEXTURE_AUDIT_CUSTOM_GRAPHICCLASS_1` |
| 6 | `validate_patch.py`, bare `Defs/` xpath | **0 nodes** on patches live in game | ✅ **fixed**, selftest 36 cases |
| 7 | `first_light` "no weaponTags" | counts a disarmed combat role as a civilian | ⚠️ **known only** |

### ⭐ THE ANSWER TO THE OWNER'S QUESTION — `measure`, 2026-08-21

He asked whether these were all fixed. They were not, and three of them never can be by
fixing a tool: `strings`, `grep` and `wc` are not broken, they are being pointed at
encodings they do not read. So the fix is a different shape — **you no longer get a bare
number from a large artifact at all.**

```
measure count AbilityDef     -> UNMEASURED, and why
measure count ThingDef       -> MEASURED 24904
measure coverage             -> what is NOT captured
measure explain <path>       -> what may read this file
```

🔑 **Every answer is `MEASURED` / `UNMEASURED` / `REFUSED`, and they are not
interchangeable.** `0` can now only mean measured zero; ignorance has its own word and its
own exit status (2 and 3). One line per question, so a count costs no context.

🛡️ **`.claude/hooks/block_blind_scan.py` refuses the scan before the wrong number exists**
— `grep`/`strings`/`wc` against a `.rws`, a `.dll`, `DefDump/**`, a world CSV or
`Player.log`. It names the right instrument in the refusal, fails OPEN on any error, and
`MEASURE_ALLOW_SCAN=1` overrides it for a legitimate literal-string search.

⚠️ **The register above is still the antidote for anything the tool does not cover.** A
`0` from a listed instrument is UNMEASURED until validated against a known answer.

🪤 **AND THE LESSON THAT COST THE MOST, because it happened while building the fix:** the
first cut of `measure` passed 16/16 and answered `MEASURED 0 AbilityDef`. It cross-checked
three sources — the manifest's count, the file's own trailing `count`, and the parsed rows
— and all three said 0. **They agreed because one collision corrupted all three
identically.** ⇒ *Agreement between sources is not correctness when the sources share a
failure mode.* The only surviving evidence was `manifest.json`'s **duplicate keys** (532
`defCounts` entries under 517 names), and `json.load` destroys it silently at parse time.

🪤 **AND THE SECOND LESSON, which is the same lesson: I called a KNOWN, HANDLED thing a
new defect.** I first reported those 19 types as "a gap nobody had recorded — counted and
readable, but nothing cross-checks them." **That was wrong, and the correction is the
useful part.** `defs/` **ACCUMULATES**: RimDefDump writes a file per type that exists now
and never deletes the file for a type that has stopped existing. Measured 2026-08-21: all
19 undeclared files are **126–243 HOURS older than the manifest**, while every declared
file was written within **17.8 seconds** of it. They are stale leftovers from removed
mods — and `skills/rimworld-modding/scripts/validate_patch.py` has skipped them
deliberately since 2026-08-13, for a reason it states plainly: *a dead defName in the
index makes a patch that references a REMOVED def validate clean.* Fail-toward-success.

⚠️ **So `measure` had the bug, not `validate_patch.py`** — it was ingesting 174 dead
defNames and reporting them `MEASURED`. Fixed: `coverage=orphan`, their defs never enter
the index, and the db now holds **78,057** defs, which is exactly the manifest's declared
sum — two numbers reached by wholly different routes landing on one integer.

🔑 **The rule worth carrying: before reporting a finding against another tool, check
whether that tool already handles it and says why.** A guard that looks like a gap is
usually a guard.

**1 — `strings` cannot read .NET attribute metadata.** It found 16 `jawa/` names in a DLL
carrying 115, because .NET keeps attribute strings in metadata blobs a byte scan does not
reach. I nearly rebuilt and redeployed the companion on that reading.
⇒ Use `ilspycmd`, the live tool list, or file dates. **Never conclude a type or method is
absent from an assembly because `strings` did not find it.**

**2 — a `.rws` does not store world biomes as text.** They are indices into a compressed
grid; a defName appears once or twice in a lookup table no matter how many tiles wear it.
⇒ `jawa/world_stats`' histogram. Same class as (1): a byte scan of a structured file.

**4 — Cherry Picker NEUTERS, it does not delete.** 1,170 of 1,344 cut defs are still in the
dump with their `weaponTags` stripped, so a tag whose every carrier was cut is **absent**
from a dump-built index rather than **empty** in it — and a counter over that index cannot
return anything but zero. ⇒ Attribute cuts from the mod's SOURCE XML.

**12 — `jawa/faction_name_get` flagged the factions that were RIGHT** (fixed 2026-08-21,
`37ac949`; **undeployed until the next shutdown window**). Its `isGenerated` compared
`currentName` against `defLabel` — but a faction with a `fixedName` is SUPPOSED to differ
from its label, that is what a reskin is. Live on 578 mods it reported 24 generated, of
which **9 were false positives wearing their own `defFixedName`**: `Empire`,
`Jawa_Junkers`, `PirateYttakin`, `DV_PirateKeshig`, `AG_XenohumanPirates`,
`CannibalPirate`, `BS_Muspelheim`, `BS_Niflheim`, `BS_OgreFaction`. 🔴 **Worse than a wrong
number: it aimed the repair at the wrong targets.** `faction_name_set action=clear` rewrote
the name to `defLabel`, so running the documented fix against `generatedCount` would have
DELETED nine authored names. ⇒ Until the deploy lands, treat any `generatedCount` from a
live game as wrong, and do not run `clear`.

**11 — a generator's own success line cannot tell you it just deleted a def.**
`gen_pawnkind_roster.py` emits 48 pawn kinds; the committed XML held **49**. The odd one
was `Jawa_Homestead_DesertRanger`, hand-added to the OUTPUT after an owner ruling, with
thirty lines of provenance the generator's table has nowhere to put. Re-running printed
`wrote … 48 pawn kinds` — the same sentence it prints when nothing is wrong. ⇒ **Before
re-running ANY generator whose output is committed, count the defs in the output and
compare to what the generator claims to emit.** A count is not a roster, and a generator
that no longer knows about an entry deletes it in silence. Fixed 2026-08-21 with a verbatim
`EXTRAS` block; the same audit is owed by every other emitter in `Utils/`.

**9 — a tag table pairs kinds that a tag table cannot pair.** Losing the sole carrier of a
weapon tag disarms a kind ONLY if that kind also blocks inheritance. `Flamebow`'s cut emptied
`NeolithicRangedFlame`, which both `Tribal_Archer_Fire` and `Tribal_Hunter_Fire` declare — but
only the archer writes `<weaponTags Inherit="False">`. The hunter appends to `Tribal_Hunter`'s
live `NeolithicRangedDecent` and is fully armed, and `weapon_tag_audit.py` correctly does not
list it. ⇒ **Read the `Inherit` attribute in the source def before pairing kinds off a tag.**
Measured 2026-08-21 (`FIRE_ARCHERS_GET_BOWS_1`); `CUT_DISARMED_VANILLA_KINDS_1` had them
paired and is corrected at its head.

**10 — `NeolithicRanged` does not exist; a patch naming it is a silent no-op.** The vanilla
neolithic ranged tags are `NeolithicRangedBasic` (5 carriers), `NeolithicRangedDecent` (6) and
`NeolithicRangedHeavy` (3). A bare `NeolithicRanged` has zero, and `validate_patch.py` passes
it — the op is well-formed and the xpath matches; only the POOL is empty, which nothing
offline reports. ⇒ Before appending a weapon tag, count its carriers in the dump.

**7 — a heuristic that is right in general hides the case you care about.** 291 kinds have
no `weaponTags` and are meant not to; a combat role that LOSES its tags looks identical.
⇒ `weapon_tag_audit.py` has no such blind spot; prefer it for that question.

⚠️ **And one that is not a count.** `validate_patch.py --live` CANNOT prove independence
from a mod you are about to REMOVE — every reference still resolves while the donor is
installed. That check needs a separate pass that drops the departing packageId.

**8 — `rimsage` MCP answers "not found" for every MODDED def.** Measured 2026-08-21: asked
for six `OuterRim_*` droid `ThingDef`s that demonstrably exist, plus bare-substring searches
for `Droid`, `OuterRim` and `guy762`, it returned **zero hits on all of them**. Vanilla and
expansion names resolve fine (`Gun_Revolver`, `Muffalo`, `Mech_Cyclops`), so its index is
**vanilla + expansions only**. ⇒ its `not found` means **not indexed**, never **not present**,
and it says so with no error and no caveat — the exact shape this register exists for.
🔴 **Never conclude a modded def is absent because `rimsage` did not find it**, and treat any
past finding that leaned on a rimsage miss as UNMEASURED rather than settled. Use the frozen
capture instead — read-only SQL over `DefDump/defs.sqlite`'s structured `defs` table, with a
known answer (`Human`) run first to validate the query shape.

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
> frozen **once he saves it**, then shipped to every player. ⚠️ *2026-08-22: `canon.yml` says
> `planet.status: remaking` — the owner is rebuilding the planet, so no frozen world exists
> YET. The no-worldgen ruling above is untouched; only the tense is.* **A faction, ideoligion or setting absent when he
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
- **Nothing on the bridge can order an attack.** ⚠️ *The tool count that used to open this
  line was wrong three ways over; the measured count is below.* `jawa/order_pawn` issues a
  GOTO even with a `targetId`; drafted pawns hold at `Wait_Combat`; spawned hostiles
  have no lord and idle. Blocks every combat test. 🔑 **Re-measured 2026-08-22 from the
  companion SOURCE** (regex over the `[Tool("…")]` attribute across 53 `.cs` files, never
  `strings`): **119 distinct `jawa/` tools**, of which exactly three are combat-adjacent —
  `fire_raid`, `order_pawn`, `raid_preview` — and repo-wide the only `JobDefOf` members
  referenced anywhere are `Goto` and `LayDown`. ⚠️ **The LIVE total is UNMEASURED offline**:
  it is those 119 plus RimBridgeServer's own `rimworld/*`, which only a running bridge can
  enumerate. *2026-08-15, `bridge-cannot-order-a-melee-attack-3f8c21`; count corrected
  2026-08-22.*

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
  every Outlander faction. ⚠️ **The five `Jawa_Homestead_*` kinds this used to cite are now
  FIELDED** — `Jawa_Patches/Patches/HomesteadDefenseLeague.xml` patches the abstract base. The
  live orphan set is nine different kinds; see `AUTHORED_KINDS_MUST_FIELD_1` (`38cabab0`), which
  also **rejects `Inherit="False"` as the fix** — it drops all twelve inherited groups.
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
  and the manifest carries `defTypes` / `defTypeCollisions`. ✅ **Deployed and captured**
  (`d4bdad92` / `0a3c310b`): the live `RimDefDump.dll` is md5-identical to the repo copy, and
  the OFFICIAL-2026-08-21 capture (`capturedUtc 2026-08-21T22:44:59Z`) carries **533 `defTypes`
  and 13 `defTypeCollisions`**. ⚠️ **A dump captured BEFORE that timestamp is still lying** —
  read `capturedUtc` before trusting a zero out of an older capture.

---

## 🔴 INSTRUMENTS THAT RETURN A CONFIDENT WRONG ANSWER

Owner, 2026-08-21, after the def-dump collision: *"Did we fix all of these string issues so
we don't keep generating false negative results? This is very disturbing."*

**The honest answer was no.** Seven instruments were caught lying in a single session, and
only some were fixed. This is the register; it is here rather than in seven ledger notes
because a note is not on anyone's path.

🔴 **RENUMBERED 2026-08-26 (`BUILDABLE_ENTRY_NUMBERS_COLLIDE_1`): numbers 9–15 were each
reused for a second, unrelated entry.** The seven later entries that collided — the ones
this section appended after the original 9–15 run — are now **25–31**. The original 9–15
keep their numbers unchanged, because `CUT_TABLE_PAIRED_WRONG_1`, `CUT_DISARMED_VANILLA_KINDS_1`,
`FIRE_ARCHERS_GET_BOWS_1` and `FIRE_ARCHER_SPEC_STILL_WRONG_1` already cite "9 and 10", and
`GENIDEO_REVERTS_DEAD_KINDS_1` already cites "11" — all five citations already resolve to the
kept originals, so none needed updating. If you have an old note citing "12", "13", "14" or
"15" for a def-dump-poisoning, stale-capture-id, kill-list, or `<li>`-in-dictionary-field
topic rather than the faction-name/weaponMoney/weapon_affordability/weapon_tag_audit topics
listed under those numbers below, it means 28–31.

🔑 **The shared shape, and it is worth naming once:** every one of these returns a NUMBER.
None errors, none warns, none returns null. A wrong count reads exactly like a right one,
so the failure is invisible unless you already suspect the instrument. ⇒ **When a count
decides something expensive, check the instrument against a case whose answer you already
know** before you trust the case you don't.

| # | instrument | what it returned | status |
|---|---|---|---|
| 1 | `strings -a -el` on a .NET assembly | **16** of 115 tool names — implying 99 live tools were missing | 🛡️ **refused at the tool call** |
| 2 | `grep` a `.rws` for biome defNames | **2**, where the CSV holds 3 / 233 / 31 | 🛡️ **refused at the tool call** |
| 3 | def dump `defs/<Type>.json` | `AbilityDef` **0**, having written 612 | ✅ **fixed** `d7cf154`, **deployed + captured** `2026-08-21T22:44:59Z` |
| 4 | `weapon_tag_audit` "emptied by the cut" | **0**, structurally guaranteed | ✅ **fixed** |
| 5 | `jawa/texture_audit` | **53** dead paths, 39 of them present art | 📋 **filed**, `TEXTURE_AUDIT_CUSTOM_GRAPHICCLASS_1` |
| 6 | `validate_patch.py`, bare `Defs/` xpath | **0 nodes** on patches live in game | ✅ fix real (`fc10b9a5`) — 🔴 **AND IT SHIPPED AGAIN** as `1c3a673f`; still **no selftest**, which is why |
| 6b | `validate_patch.py`, lxml branch | **0 matches for EVERY** `text()` / `contains()` / `starts-with()` / `not()` / axis / union xpath | ✅ fixed `1c3a673f` (`rebase_for_root_element`, line 587, called at 1156). ⚠️ **Same bug class as row 6, second occurrence** |
| 6c | `validate_patch.py --defs`, def created by ANOTHER MOD'S PATCH | **0 matches** on an xpath that is live and load-bearing | ⚠️ **KNOWN ONLY, and it is a third false-zero class** — see below |
| 7 | `first_light` "no weaponTags" | counts a disarmed combat role as a civilian | ⚠️ **known only** |
| 8 | `Utils/animal_inventory.py` biome/animal conflicts | **3**, while the game was dying on a 4th it cannot see — the true count is **27** | ✅ **superseded** by `Utils/biome_animal_conflicts.py`, which reads the CAPTURE |
| 9 | `Utils/refresh.py` artefact staleness | **"never stamped → REBUILD"**, forever, on artefacts it had just correctly generated | ✅ **fixed** `797b034c` — writes the stamp atomically and READS IT BACK |

🔴 **THE FOURTH FALSE ZERO, and it is the same lesson on the CENSUS side — BUILD, 2026-08-26.**
Row 6c is about an xpath that reads 0 against a def a patch creates. Row 8 is a whole census with
the same blind spot. `animal_inventory.py` cross-references biome→animal against animal→biome by
reading every active mod's **Defs**, and reported **3** duplicate pairs while `Player.log` carried
`ArgumentException: An item with the same key has already been added. Key: JRWTorosaurus` — a pair
that is **not in any def file**. `More Vanilla Biomes` patches the animal's `wildBiomes`; our own
`BiomeCast_Ashkarr.xml` patches the biome's `wildAnimals`. Neither side declares it.

- **The true number, from the def dump capture (post-patch, from the running game): 27 pairs
  across 12 biomes.** `Utils/biome_animal_conflicts.py`.
- 🔑 **And the LOG undercounts too, structurally.** `BiomeDef.CommonalityOfAnimal` throws on the
  first duplicate key **per biome** and stops, so the log can only ever name one key per biome —
  it named 12. Fixing what the log names would have surfaced the other 15 one load at a time.
- ⇒ **The rule, restated for censuses:** if a PatchOperation could CREATE the thing you are
  counting, mod XML cannot answer and a number from it is UNMEASURED, not small. The capture is
  the instrument. Same family as 6c; different tool, same false zero.

🔴 **AN INSTRUMENT THAT COULD NOT READ BACK ITS OWN OUTPUT — BUILD, 2026-08-26.** Row 9.
`refresh.py` is the tool that answers *"do I need a game load?"*. Its stamp writer left a leftover
tail from a longer previous note in `GENERATED_FROM.json`, producing valid JSON followed by
garbage; `read_stamp()` swallows `ValueError` and returns `None`; the artefact table then reads
**"never stamped → REBUILD"** and the verdict says *"Offline artefacts are stale. Run --all"* —
forever, for free, with no error, about artefacts it had just generated correctly. ⇒ **A tool that
writes a file it will later read must read it back at write time and fail loudly if it cannot.**
Fixed `797b034c`: temp file, `os.replace`, then a readback that raises.

🔴 **THE THIRD FALSE ZERO: a def that exists only as another mod's PATCH OUTPUT — CHECK,
2026-08-22.** `--defs` scans mods **on disk**. A def that no XML file declares, because a
different mod's `PatchOperationAdd` creates it during the patch phase, is **invisible to that
scan** — so an xpath targeting it reports **0 matches while being perfectly live**.

- **The case:** `Jawa_Patches/Patches/HeadSetForFA_Revive.xml` targets
  `FacialAnimation.FaceAdjustmentDef[defName="BS_InsectoidHumanoid_FourArmed_FaceAdjustment"]`.
  It reads 0 on disk. The def is created by Big and Small's
  `Patches/BS_Insectoid_FacialAnimation.xml` at load order **560**; Jawa Patches is **572**, so
  we patch *after* it and the xpath reaches it fine.
- ⚠️ **This entry corrects a 2026-08-22 sweep note that called that operation dead and
  harmless.** Measured against the capture: the def reads `"generated": false` — it is
  **patch-created, not runtime-created**; what actually distinguishes it is having no
  `modContentPack`/`fileName`. And its `AgeBasedParams: []` is **evidence our patch fired**,
  not evidence the patch was redundant — the upstream XML supplies no such node. Reading the
  empty list as "already present" is circular.
- 🔑 **The rule:** a 0 from `--defs` means *not found on disk*, never *not reachable*. Settle
  it against a **live dump**, which is downstream of the patch phase and therefore sees
  patch-created defs. `--live` exists for exactly this.

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
`37ac949`; **deployed — the live companion DLL is dated 2026-08-22 12:47, 19 h after that
commit, and is md5-identical to the repo build**). Its `isGenerated` compared
`currentName` against `defLabel` — but a faction with a `fixedName` is SUPPOSED to differ
from its label, that is what a reskin is. Live on 578 mods it reported 24 generated, of
which **9 were false positives wearing their own `defFixedName`**: `Empire`,
`Jawa_Junkers`, `PirateYttakin`, `DV_PirateKeshig`, `AG_XenohumanPirates`,
`CannibalPirate`, `BS_Muspelheim`, `BS_Niflheim`, `BS_OgreFaction`. 🔴 **Worse than a wrong
number: it aimed the repair at the wrong targets.** `faction_name_set action=clear` rewrote
the name to `defLabel`, so running the documented fix against `generatedCount` would have
DELETED nine authored names. ⇒ **The deploy has landed; only a LOAD is still owed.** Treat a
`generatedCount` from a game that has not restarted since 2026-08-22 12:47 as wrong, and do not
run `clear` against it. `FACTION_NAME_CHECK_TRUSTWORTHY_1` is the item that proves it live.

**13 — `weaponMoney` is a CEILING rolled once, not a budget, and "raise the floor" is the
wrong reflex.** `PawnWeaponGenerator.TryGenerateWeaponFor` rolls `weaponMoney.RandomInRange`
ONCE and admits every weapon priced at or below the roll; `min ≥ cheapest` means the kind
ALWAYS arms, `max < cheapest` means it NEVER does. ⇒ Before proposing a money fix, compute
`P(bare) = (cheapest − min) / (max − min)` and check it is not already zero. Measured
2026-08-22 on the seven kinds a live run named worst: **all seven predict 0.0%**, and
`Jawa_Junkers_Grunt` has a floor of 60 against a cheapest of 1. Money was not the lever and
three independent routes said so. ⛔ Raising it is also not free — `gen_pawnkind_roster.py`
derives `max` AND `combatPower` from the same number, so lifting a floor re-tiers the raids.

**14 — `weapon_affordability.py` will answer with a resource.** It named
`BMT_ResourceBlueCrystal` (Biomes! Caverns, `stackLimit` 75) as a pawn kind's cheapest
eligible weapon at price 1. Not strictly wrong — the def carries `equipmentType Primary`,
`weaponTags`, `weaponClasses` and a Cut tool at power 11 — but a resource stack answering a
weapon question makes "this kind is safe" mean less than it reads. ⚠️ And the tool's prices
are `MarketValue`, i.e. UNSTUFFED; the engine compares `ThingStuffPair.Price`, which is
dearer. **Its pass is a floor, never a truth** — it says so in its own header, and a live
run has already contradicted it.

**15 — `weapon_tag_audit.py --emit-patch` had two guards and BOTH were disarmed by
caution.** Fixed 2026-08-22. `refuse_shrink` and `preserved_block` read the OUTPUT path, so
aiming `--emit-patch` at a scratch file to inspect the result first — the careful move, the
one a reviewer makes — meant there was nothing on that path to lose, the shrink guard stayed
silent, and the hand-authored block was dropped. Measured: a scratch emit produced **9
operations against the 151 on disk**, silently losing 142, with no warning. 🔑 **The failure
mode is the inversion: the safe workflow was the unsafe one.** Both guards now read the
canonical `WeaponTags_Renormalise.xml` regardless of where output goes, and a scratch emit
correctly refuses. ⛔ The underlying non-idempotency is unfixed and is not a bug: the dump is
captured with the patch already applied, so every weapon it tagged reads as already-tagged.
**A real regenerate needs a dump taken with `Jawa_Patches` DISABLED.**

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
capture instead — read-only SQL over the structured `defs` table of
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs.sqlite`
(788 MB, mtime 2026-08-21 16:10; there is no copy in the repo), with a
known answer (`Human`) run first to validate the query shape.

**25 — A gene's `disabledWorkTags` matches a work TAG, so checking a WorkGiver's `workType`
answers the wrong question.** Measured 2026-08-22 in the live def set (capture
`2026-08-23T05-05-29Z`, 578 mods): vanilla's `Drill` WorkGiver is **not** `workType Mining`
on this stack — it is `FSFDrilling`, retyped by **[FSF] Complex Jobs**. `Jawa_MiningDisabled`
still bars a Jawa from the deep drill only because `FSFDrilling`'s WorkTypeDef happens to
carry the **`Mining` workTag**. ⇒ To answer "does this gene stop this job", read the
**WorkTypeDef's `workTags`**, never the WorkGiver's `workType`. ⚠️ And note the dependency:
if [FSF] Complex Jobs is removed or drops that tag, the ban silently lapses with no error.

**26 — Def-dump JSON records nest every field under `fields`, so a top-level read returns
`None` for everything and looks like a measured absence.** `e["disabledWorkTags"]` is `None`
on all 3,846 GeneDefs; `e["fields"]["disabledWorkTags"]` is the real value. The keys that ARE
top-level are only `defName defType defTypeFull fields label modName packageId shortHash`.
⇒ Any census that reads a def field must go through `fields`, and a script returning all-`None`
across a whole type is the signature of this mistake, not of an empty field.

**27 — The live def set answers "is it in the running game" WITHOUT a bridge call.** A capture
under `DefDump/captures/<id>/` is post-load, post-patch, post-override — so it settles
"did the patch apply", "did the def survive a dedup mod", "which xenotypes carry gene X"
offline. ⚠️ It cannot answer anything about BEHAVIOUR (can this pawn do this job), and the
game appends parts of its own at load — a `ScenarioDef` reads 5 parts in the dump where the
XML authors 3, because Odyssey adds two `ScenPart_PlanetLayer`. Count authored parts in the
file, not in the dump.

**28 — `validate_patch.py` now REFUSES an `<li>` inside a dictionary-keyed field, and that
class of bug is the most expensive one this project has hit.** A `List<Foo>` whose `Foo`
declares `LoadDataFromXmlCustom` and reads the NODE NAME as a def reference takes
`<SomeDefName>value</SomeDefName>`; an `<li>` there throws inside the loader and RimWorld
**discards the ENTIRE def**, silently, with nothing in the patch or the load to show for it.
It cost **101 CharacterDefs** (`skillGains`) and **26 BiomeDefs — 94.8% of the planet**
(`wildAnimals`) on the same day. ⇒ **45 fields are guarded**, list measured from the 1,558
vanilla def files against the 578-mod capture (a field whose distinct child tag names are
≥80% defNames and which vanilla never writes with `<li>`), not remembered. Includes
`statBases`, `costList`, `skillGains`, `skillRequirements`, `xenotypeChances`, `wildAnimals`,
`wildPlants`, `baseWeatherCommonalities`. Derivation:
`observed/2026-08-22/biome_cast/custom_loader_fields.txt`.
🔑 **Run the validator on any generated XML before deploying it** — both generators that hit
this shipped clean-looking files that passed every check we had.

**29 — A def-dump capture can be POISONED BY THE BUG YOU ARE INVESTIGATING, and it then
reports your fix as broken.** Validating the *repaired* `BiomeCast_Ashkarr.xml` against
capture `2026-08-23T05-05-29Z` produced **36 errors** of the form *"'AB_MycoticJungle' does
not exist in the LIVE game"* — true, and only because the OLD patch had deleted those 18
biomes before the capture was taken. ⇒ When a fix targets defs that the defect destroyed,
the `--live`/`--defnames` check is circular until a clean reload. **Read the xpath match
counts against the mod folders on disk instead** — those said 26 of 26 matched.


**30 — An instrument can print a FRESH capture id over STALE data, and a modlist
fingerprint will never catch it.** `defs.sqlite` lives at the DefDump **root** and serves
every capture, so it survives a new load untouched while the capture beside it moves on.
`weapon_tag_audit.py` read its tags from a 2026-08-21 database and its header from the
newest capture's manifest, and reported **12** disarmed pawn kinds where the capture it
named says **2** — it would have closed two already-fixed items as still-broken. ⇒ The
fingerprint doctrine ("fingerprint, not timestamp") is **necessary but not sufficient**:
both captures were the same 578 mods, and what changed between them was OUR OWN XML.
🔑 **Compare CAPTURE IDENTITY** — `defs.sqlite`'s `provenance.captured_utc` against the
capture's `manifest.capturedUtc`. `dump_projection.py` now does this and falls back to that
capture's JSON with a one-line warning; the fast path returns after `measure build`.

**31 — A kill list is INTENT; the capture is REALITY, and the capture is already post-cut.**
Cherry Picker does not delete a cut weapon, it strips `weaponTags` at load — so a genuinely
cut weapon contributes no tag to a dump at all. Subtracting the kill list from dump-derived
carriers therefore removes it TWICE, and any weapon deliberately restored (e.g. `Gun_Needle`,
which is on the list and carries `MechanoidGunLongRange` live) counts as cut while visibly
armed. ⇒ **Presence in the capture with the tag attached IS survival.** Never re-subtract a
written intent from a measured fact.

**16 — The def dump cannot audit its own attribution.** `packageId`/`modName` in a capture
credit whoever PATCHED a def last, not who DEFINED it: `Desert`, `ExtremeDesert` and
`AridShrubland` are Core biomes that the capture attributes to
`grimterra.terrainretexturemod`. Emitting that as `MayRequire` gated three vanilla biomes on
a retexture mod. ⚠️ A check that asks the capture about this returns a confident **0**,
because it reads the same poisoned field — measured, I wrote that check first. 🔑 **The
independent source is the game's own `Data/` tree**: whatever Core and the DLCs define there
needs no `MayRequire`, however many mods touched it afterwards.


**17 — A live test proves what the RUNNING game holds, never what disk holds — and a
byte-identical deploy check does NOT close that gap.** RimWorld parses defs at **startup**, so
anything deployed after the current session began is invisible to it. This cost two items in
one night: `JAWA_ROBES_NEVER_WORN_1` concluded that `apparelRequired` is unreliable, and
`EMPIRE_GRUNT_SPAWNS_BARE_1` measured a weapon roll against a budget that had already been
raised. Both had verified repo == game-folder and both were still testing yesterday's defs.
🔑 **Before filing a live observation as a defect, read the def out of the NEWEST CAPTURE** —
that is the running game's own copy of what it loaded — and confirm it says what you think you
deployed. In the robe case every observed garment was explained by the live def, which made
the result positive evidence that the mechanism WORKS.

**18 — `apparelRequired` is honoured and ignores `apparelMoney`; `apparelTags` is the budgeted
half.** Measured 2026-08-23 across the Jawa and Empire rosters: required items appear on the
pawn regardless of budget (`Jawa_Blackstar_Heavy` requires a 14,500-silver Mandalorian set on a
600 budget and wears it), while tag-driven purchases are capped by `apparelMoney`. ⇒ Use
`apparelRequired` for anything that MUST appear — a uniform, a robe, a warcasket — and
`apparelTags` only for variety you are willing to lose. ⚠️ And check body coverage: a tag family
can be all helmets and cuirasses, leaving the pawn with no trousers, which no validator reports.


**19 — The def dump does NOT serialise `drawSize` (or `Color`), so a resize or recolour job
cannot be done from the capture.** All 25 creatures in `CREATURE_RESIZE_PATCH_1` read
`graphicData.drawSize = null` AND `lifeStages[].bodyGraphicData.drawSize = null` in capture
`2026-08-23T07-12-04Z`, while their mod XML on disk declares real values. Same for
`FactionDef.colorSpectrum`, which the dump renders as `"<skipped:Color>"`. ⇒ **Vector2 and
Color fields are absent from the dump by construction, not missing from the game.** Read them
from the mod's own source XML. 🔑 And note where `drawSize` lives for animals: on
`PawnKindDef.lifeStages[].bodyGraphicData`, never on the ThingDef's `graphicData`.

**20 — A `PawnKindDef` block contains TWO drawSize families and a naive regex doubles your
operations.** `dessicatedBodyGraphicData` carries its own `<drawSize>` beside
`bodyGraphicData`'s, so `re.findall(r'<drawSize>...')` over a whole PawnKindDef returns twice
as many values as there are life stages. That built a 170-operation patch indexed `li[1..6]`
against defs with three life stages — and **`validate_patch.py` reported "OK - 0 errors" for
both the broken and the correct version**, because the surplus xpaths simply match nothing and
a no-op is not an error. ⇒ Extract from inside `<bodyGraphicData>` only, and **always print
what a generator produced and read it** before trusting a clean validate.

**21 — Cherry Picker publishes its own removal roster, and it is the only instrument that
answers "was this actually cut?"** The config is INTENT (see 15); the capture keeps the def
row with `weaponTags` emptied to `[]` (see 4), so neither says what happened. `Player.log`
carries `[Cherry Picker] The database was processed in … the following defs were removed:`
followed by one ` - <DefType>/<defName>, ` line per removal. Measured 2026-08-23 on the
581-mod load: **1212 removal lines against 1342 typed config entries, and zero removed that
the config did not ask for.** That comparison is the only cheap proof the list did not die —
one malformed key loses all 1342 and nothing in the game says so. ⚠️ **Three parsing traps,
all silent:** the lines carry a **trailing space**; the **last line has no trailing comma**
(it was `Plant_TreePoplar` this load), so any `grep -F "/Name,"` reads the final entry as
not-cut; and `grep -n` on `Player.log` disagreed with a Python line index by 3, so find the
header by CONTENT, never by a remembered line number. The 130-entry shortfall is benign —
128 name defs absent from the 581-mod dump (uninstalled mods) and 2 are `UnfinishedThing`
products (`UnfinishedLEGO`, `Unfinished_VerdantBow`) that Cherry Picker will not take.

**22 — A `[ModuleInitializer]` in a RimBridge companion does NOT fire when the assembly
loads.** It fires on the first code EXECUTED in the module, and RimBridge discovers tools by
reading `[Tool]` attributes off assembly **metadata** — reflection over metadata executes
nothing. Measured 2026-08-23: both `[JawaBench]` lines were absent from all 10,358 lines of
the load and appeared as L10359–10360 the instant a `jawa/` tool was called, while the live
bridge already answered **246 tools, 121 of them `jawa/`**. ⇒ **Absence of a companion's init
line from a log is UNMEASURED, never "the deploy did not take."** `JawaBenchInit.cs` chose a
module initializer over a static constructor precisely to avoid waiting for the first
invocation; it waits anyway. The instrument that settles it is one command from any seat:
`python.exe src/RimMandrake/Utils/rimbridge_client.py --list-tools`.

**23 — The bridge SILENTLY IGNORES a parameter the deployed tool does not declare.**
Measured 2026-08-23: `jawa/world_tile_export` was asked for `extended=true` against a
companion built before that parameter existed. It returned **`success: true`**, wrote the
old nine-column file, and reported no warning of any kind. ⇒ **A successful call is not
evidence that your argument was honoured**, and a client that infers "the new build is
deployed" from "the call did not fail" will confidently mislabel its own output —
`vivify_world.py` did exactly that for one run, printing `(EXTENDED)` over a nine-column
file. ✅ **Verify from the RESULT, not from the absence of an error:** `world_tile_export`
returns its own `columns` list, built from the same constant that writes the header, so
`"tempMin" in columns` cannot disagree with the file. Any tool gaining a parameter should
return something a caller can test the same way.

**24 — `river_flow` is OURS and has no engine counterpart.** The column in
`world/ASHKARR_WORLDMAP_tiles.csv` is authored by `ashkarr_headwaters.py` and
`ashkarr_join_mouths.py` — RimWorld models rivers as links carrying a `RiverDef`, plus a
per-tile `riverDist`, and stores no flow scalar anywhere. ⇒ A harvest from the live game
can never MEASURE it; it is CARRIED from the authored bundle by construction, and a
future tool that claims to have measured it has invented it.

**25 — A biome animal at `commonality: 0` is REGISTERED AND UNSPAWNABLE, and a mod puts it
there on purpose.** `BiomeDef.AllWildAnimals` only yields kinds whose commonality is `> 0f`,
so a zeroed animal is not in the biome's animal list at all — the def is present, the patch
applied, the entry exists, and nothing reports it. ⇒ **CHERRY PICKER does this — it suppresses a def the
owner cut by REPLACING the biome value with 0 rather than removing the entry**, and the cut list
is the owner's own `Config/Mod_3521312241_Mod_CherryPicker.xml`, 1,342 entries.
🔴 **Its cuts are INVISIBLE to the def dump: the cut animals are still PRESENT as ThingDef and
PawnKindDef in the capture.** Validated over the population — 167 of 168 always-off animals are
on that list, and 0 of 414 always-alive animals are. Proven on
`TemperateForest`, which this project never patches: Core declares 36 animals and 9 read 0 in
the capture while the other 27 keep their vanilla values. ⛔ **Two explanations are DEAD and
must not be proposed a third time** — it is not `BiomeDef.CommonalityOfAnimal`'s duplicate-key
cache (that method only ever READS a record) and it is not a dumper defect (these zeros are in
`defs/BiomeDef.json`'s record field, not the computed value in `animals.json`). 🔑 **Measure it
with `src/RimMandrake/Utils/biome_commonality_zeroed.py`**, which reads the record: 181 of our
744 authored entries are switched off, 157 distinct animals ALWAYS off in the 26 biomes we
author, 168 always off across all 67. **A roster that names one of them is designing around an
animal that cannot appear.**

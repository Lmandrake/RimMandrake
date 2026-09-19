# RENAME_VERIFY_WINDOW_1 — proving the three-tier rename end to end

Naming Phase 2 (`aa759446` · `0772bec7` · `54a8e28d` · `972d168f`) changed 4904
defNames, 255 packageIds, 275 paths and 164 namespaces across 468 files and moved 31
mod folders into tier directories. This item is the proof pass that was deferred out
of it.

## the landmine the checklist did not name

🔴 **Every saved mod list held PRE-RENAME packageIds, and nothing warns you.** A saved
list is a bare `<li>packageId</li>` sequence with no folder, name or version beside it.
RimWorld drops an id it cannot resolve **at startup, silently**, and the entry count is
unchanged — so `modlist_swap.py --status` read `UNRECOGNISED`, which is the identical
verdict it gives when the owner adds one mod.

⇒ `modlist_swap.py --restore` would have written 23 dead ids over the live file and
silently deactivated every renamed mod of ours before the owner's next session. The
19-mod `MINIMAL` list would have loaded without Inhabited, JawaIonWeapons or Droidworks
— i.e. every cheap bridge test after the rename would have been testing the wrong stack.

**Live was checked, not assumed, before being made the source:** all 24 `mandrake.*`
ids in the live `ModsConfig.xml` resolve to an installed mod's own `About.xml`
packageId; the other 561 entries are order-identical to the pre-rename list; the
mapping is 23-for-23 with `mandrake.jawa.patches` deliberately unrenamed (Jawa_Patches
is parked in `SPLIT_Phase3`). Live is correct because the migration rewrote it at
23:22 on 2026-08-30 — the saved copies were simply never propagated.

**Fixed** (`0fda62c9`):
- `ModsConfig.FULL.LATEST.xml` re-captured from live, md5 `e9819939`, 585 either way.
  The pre-rename file kept as `ModsConfig.FULL.20260830_pre_rename.xml`.
- `ModsConfig.MINIMAL.xml` hand-mapped: `mandrake.inhabited` → `mandrake.rm.inhabited`,
  `mandrake.jawaionweapons` → `mandrake.rsw.ionweapons`, `mandrake.droidworks` →
  `mandrake.rsw.droidworks`.
- `infrastructure/state/modlists/README.md` carries the mapping table and the rule.

### the same landmine, second site — RimSort's own database

`C:\Users\Mandrake\AppData\Local\RimSort\dbs\userRules.json` held **13 pre-rename ids**
(18 occurrences) and `dbs\ignore.json` held **24**. These are the owner's hand-authored
load-order rules. They cost nothing today — the live `ModsConfig.xml` order is intact —
but the next RimSort **Sort** would have matched none of them and re-ordered the renamed
mods by RimSort's defaults, silently dropping constraints the repo depends on (e.g. the
`DesertVehicleReskin` must-load-after-`sarg.alphavehiclesneolithic` rule that
`src/DEPLOY_HOLD.txt` documents as the difference between the reskin being visible and
invisible).

**Migrated in place**, 29-entry map derived from `naming_rename_map.csv` and filtered so
a row is applied only when the NEW id exists in an installed `About.xml` and the OLD one
does not. Both files backed up beside themselves as `*.pre_rename_20260831_*` and
re-parsed as JSON before the write.

⚠️ **RimSort.exe was running (PID 2400) when this was written.** RimSort holds its DB in
memory; if it saves before it is restarted, it writes the stale ids back. This is not
destructive — the fix simply reverts — but **RimSort must be restarted, not merely
Refreshed, to pick this up**, and if the owner edits rules in the open instance first,
re-run the migration.

## the five checks

### 1. `refresh.py` dump rebuild + re-fingerprint — PASS (the fingerprint works)

`python.exe src/RimMandrake/Utils/refresh.py` reads fingerprint `0245d9fd5f108808`,
585 listed / 585 resolved against 1293 installed. It correctly reports the live DefDump
as not matching and names all 23 renamed ids as mod-set changes — the packageId rename
moves the fingerprint, so the currency check is not fooled. Offline artefacts
(`observed/2026-08-13/inventory`, contact sheets, `Jawa_Armoury/Patches`) are STALE and
rebuildable with `--all`, no load needed.

🔴 **But a fresh DEF CAPTURE still needs a game load, and its own freshness check does
not see this.** Every capture on disk, including `2026-08-31T04-57-37Z`, reports
`modCount: 585` matching live while holding **pre-rename defNames** — the capturing
session's in-memory defs predate the rename. `modCount` is a check on the mod SET, not
on def CONTENT.

### 2. `validate_patch.py --defs` on every patch mod — PASS

Run against the deployed copies (repo and game copy are byte-identical: 
`deploy_custom_mods.py` reports 0 drift, 14 files held), with all three def roots:

```
python3 skills/rimworld-modding/scripts/validate_patch.py \
  "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods" \
  --defs .../RimWorld/Data --defs .../RimWorld/Mods \
  --defs .../steamapps/workshop/content/294100 \
  --mods-config ".../Config/ModsConfig.xml" --quiet
```

436 XML files (96 `<Patch>`, 303 `<Defs>`, 31 About/LoadFolders, 6 translation) against
a 585-mod / 9,160-def-file load set. Full output:
`Transient/rename_verify/vp_deployed.txt`.

⛔ **`--live` was deliberately NOT passed.** It resolves against the DefDump, which holds
pre-rename names — it would have reported the whole rename as broken.

**PASS — 436 files, 10 errors, 5629 warnings, 0 of them rename-related.**

All 10 errors are missing donor texPaths inside Armoury's absorbed KotOR content
(`guy762_OrbMote`, `guy762_throwngrenade_foam`, `guy762_PoweredWallBase` ×2,
`guy762_DoubleAutoDoorBase`, `KOTOR_Mineable`, `KotORDart_stun/_toxic/_saber`,
`BulletDeflected`) — the same pre-migration set the texture sweep found, traceable to
`dede5dc0` and earlier. 5,444 of the warnings are the benign "inner xpath differs from
the conditional test" add-if-missing shape; the rest are patch-created nodes and
multi-match notes.

**Cross-checked mechanically, not by eye:** every token in the 12,127-line output was
intersected with the `old` column of `naming_rename_map.csv`. 22 names matched, and all
22 are accounted for — 8 are mod FOLDER names appearing in file paths, 3 are identity
rows where old == new (`RM_OpenPitBase`, `RM_PitCellBase`, `RM_PitDigSiteBase`), and 11
are `TBD_SPLIT` rows belonging to Jawa_Patches, which Phase 3 has not triaged yet and
which is parked on purpose. **No def, packageId or namespace that should have been
renamed is still being referenced by its old name.**

### 2a. the check nobody listed — **does the C# still compile?**

⭐ **A build is the one detector this rename never got, and it found the two worst
defects in the whole pass.** Every shipping `.csproj` was built with
`C:\Users\Mandrake\.dotnet\dotnet.exe` (the user-local SDK; `C:\Program Files\dotnet`
is runtime-only and cannot build). Two of eighteen did not compile at all:

| mod | what Phase 2a did | consequence |
|---|---|---|
| **Inhabited** | rewrote the enum member `Inhabited,` inside `enum InhabitedState` to `RimMandrake.Inhabited,`, plus 3 `InhabitedState.RimMandrake.Inhabited` call sites | the assembly could not be built at all — 5 compile errors |
| **EmpirePursuit** | rewrote `<Compile Include="RuthlessPursuingMechanoids.cs" />` to a filename that does not exist | `CS2001`, no build |

Both fixed; **all 18 shipping assemblies now build with 0 errors** and have been
rebuilt against the renamed namespaces (`e2fdf908`, `644cd945`).

### 2b. 🔴 EmpirePursuit was a LIVE break, already deployed

Phase 2a rewrote the forked ScenPart's C# namespace, `<AssemblyName>` and
`<RootNamespace>` to `RUT_RuthlessPursuingMechanoids` — a defName prefix rule applied
to a C# identifier — and rewrote the XML to match:

```
<ScenPartDef Class="RUT_RuthlessPursuingMechanoids.ScenPartDef_RuthlessPursuit">
<scenPartClass>RUT_RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids</scenPartClass>
```

⛔ **No assembly has ever exported that name**, so the deployed
`ScenParts_EmpirePursuit.xml` has named a nonexistent type since the migration
deployed. This one was not latent — the next load would have lost the ScenPartDef.

🔑 **And the rename should never have touched it.** The fork holds upstream's
namespace, class name and ScenPartDef defName **identical on purpose**
(`EMPIRE_PURSUIT_SURVEY_SHADOW_1`): a `ScenPart` is scribed into savegames and `.rsc`
scenario files by its **full type name**, so renaming it makes every existing save and
scenario unloadable. Restored to `RuthlessPursuingMechanoids`, a
`src/RimUtinni/EmpirePursuit/.naming-vendored` marker now records the exemption so no
later pass repeats it, and the XML was **deployed immediately** — it makes the file
agree with the already-deployed 2026-08-28 assembly, which never carried the RUT_ name.

### 2c. 🔴 45 XML type references left behind on the old namespace

Phase 2a moved every C# namespace under the `RimMandrake.*` root but did **not** update
the XML that names those types. Four mods, 24 distinct types, 45 references across 16
files:

| mod | XML still says | source now declares |
|---|---|---|
| Droidworks | `Droidworks.*` (16 types) | `RimMandrake.StarWars.Droidworks` |
| Inhabited | `Inhabited.*` (3) | `RimMandrake.Inhabited` |
| JawaIkee | `JawaIkee.*` (2) | `RimMandrake.StarWars.JawaIkee` |
| JawaIonWeapons | `JawaIonWeapons.*` (3) | `RimMandrake.StarWars.JawaIonWeapons` |

**Invisible today only because the deployed assemblies are pre-rename builds**, so XML
and DLL still agree. The regression fires the moment anyone rebuilds — and RimWorld
resolves a dotted `Class=` value only against that exact full name
(`GenTypes.GetTypeInAnyAssemblyInt` falls back only through `IgnoredNamespaceNames`,
which is `Verse`/`RimWorld`/… and nothing of ours), so every affected def would be
discarded or lose its comp, silently.

XML fixed, assemblies rebuilt, and **both halves held together in
`src/DEPLOY_HOLD.txt`** — either alone breaks the mod, in opposite directions. Lift the
whole block in one `--apply` per mod at the next game-down window.

⚠️ Also fixed: `BoltCorePatches.cs` declared
`namespace RimMandrake.StarWars.RimMandrake.StarWars.Droidworks` — a double-prefix
Phase 2c's corruption sweep missed.

### 3. magenta texture sweep — FAIL, two real regressions, both fixed

960 `texPath` values across the 31 tiered mods resolved against disk following the
`reading-rimworld-graphics` ladder, in both the repo and the deployed copy.

🔴 **The global defName replace also rewrote two `<texPath>` values whose text happened
to equal the old defName**, while the PNGs on disk kept their names:

| def | texPath after migration | file that exists |
|---|---|---|
| `RSW_Thermal_Detonator_Thowable` | `Things/Projectile/RSW_Thermal_Detonator_Thowable` | `Thermal_Detonator_Thowable.png` |
| `RSW_ECD_Grenade_Thowable` | `Things/Projectile/RSW_ECD_Grenade_Thowable` | `ECD_Grenade_Thowable.png` |

Both are `Graphic_Single`, so both would have rendered **magenta** rather than failing
silently. Every sibling texPath in
`src/RimStarWars/Armoury/Defs/ThingDefs/Absorbed_JDSArmory_Projectiles.xml` is
unprefixed, so the texPath was reverted to match the files rather than the files
renamed. Fixed and deployed, `8d96b8b3`.

Everything else the sweep flagged is pre-migration and traceable to commit `dede5dc0`
or earlier: 12 donor paths that live in vanilla Core's `resources.assets` (the
loose-scan blind spot), 5 genuinely absent KotOR-absorption textures, and
`WreckedMachines` deployed as About.xml only, which `DEPLOY_HOLD.txt` has held since
2026-08-12. None appear in the rename map's `old` column.

### 4. 22 s minimal-list load — NOT DONE, and it is the owner's to start

⛔ **The running game proves nothing about the rename.** It launched at ~21:57 on
2026-08-30 and Phase 2 landed after it — the process holds PRE-rename defs in memory
while the disk holds post-rename ones. It is sitting at the entry screen with no game
loaded.

🔴 **A save taken from this session would bake defNames that no longer exist on disk**,
and the next launch would answer with `Could not load reference to …` on every one. The
session should be closed rather than played in.

Launching or closing the game is the owner's act (global CLAUDE.md), and he is AFK, so
this check and the fresh def capture in §1 are **owed to his next load**, not skipped.
⚠️ Noting a genuine conflict rather than obeying the narrower rule silently: the
`rimworld-load-round` skill §10 (written 2026-08-30) contemplates "a driver-initiated
restart for a def/content change" and gives the Steam command for it. If that is meant
to authorise an agent restart, say so and this closes in about a minute.

**Everything the load needs is already staged.** `MINIMAL` is correct, `FULL.LATEST` is
correct, repo and game copy are in sync, and the def dump can be armed with
`echo all > ".../DefDump/dump_request.txt"`.

### 5. `rid` / `xtp` `validate_save_artifact` — .rid PASS, .xtp PASS on content

- **`The Salvation.rid`** — 267/267 references resolved. Exhaustive grep against all
  1399 rows of the rename map finds no residual functional name: the four hits are
  `mandrake.jawa.patches` (deliberately unrenamed, `new = TBD_SPLIT`) and three
  substring false positives inside provenance mod display names. The live game copy
  under `…\Ideos\` is md5-identical to the repo.
- **`MandrakeJawa.xtp`** — the validator reports 6 missing genes
  (`RSW_BodySizeGene_smaller`, `RSW_Jawa_Skittish`, `RSW_Eyes_HugeYellow`,
  `RSW_Jawa_Eyes_HugeOrange`, `RSW_Jawa_Eyes_HugeAmber`, `RSW_Jawa_Head_Plain`). All six
  are the **correct post-rename names**; the repo defs declare them, the deployed mod
  copy is byte-identical, and the live game copy under `…\Xenotypes\` is md5-identical
  to the repo. The six read as missing only because no def capture yet exists
  post-rename (§1). ⇒ **UNMEASURED against a current dump, not wrong.** Re-run after the
  next load for a clean 0.

`deployed/config/xenotypes/MandrakeJawa.xtp` (dated Aug 14) still holds names from two
generations back (`guy762_*`). It is an orphaned staging copy — the file the game reads
is the LocalLow one, which is current — but it should be deleted or refreshed so nobody
diffs against it.

## residual pre-rename names, triaged

| where | verdict |
|---|---|
| `deployed/config/**`, `infrastructure/state/logs/**`, dated `ModsConfig.FULL.2026*.xml`, `src/Jawa/ideoligion/witness/**` | historical records, correct as of their date — leave |
| `skills/skills-workspace/**` | frozen eval fixtures — leave |
| `skills/rimbridge/references/map-authoring.md`, `skills/rimworld-xenotypes/SKILL.md` | carried `mandrake.starwarsraces`; corrected in `8d96b8b3` |
| `src/RimUtinni/Doctrine/…/DoctrinePatches.cs` — `new Harmony("mandrake.jawadoctrine.core")` | a Harmony instance id, not a packageId; arbitrary and unique, so functionally correct. Cosmetic only |
| `mandrake.missingartfixes` in `src/Jawa/README.md`, `harvest_log.py`, `KotORBandolierNorthFix/About/About.xml` | the mod is retired and no longer in `src/` or the live list; all three are prose |
| docs under `design/`, `infrastructure/state/facts/`, `canon.yml`, `V1_CHAIN.md`, `LOAD_PROCEDURE.md` | doc propagation, Phase 3's scope — not touched here |

## what a load still owes

| owed | why it cannot be done from here |
|---|---|
| §4, the 22 s minimal-list load | launching or closing the game is the owner's act, and the running process is a pre-rename session |
| §1, a fresh def capture | the dump is armed before launch and written at startup |
| §5, a clean `validate_save_artifact` on the `.xtp` | it resolves against that capture |
| `NAMESPACE_PAIR_DEPLOY_1` | assemblies cannot be written while the game holds them open |

## state

`blocked` on a game load. Everything reachable without one is done, deployed where it
could be, and pushed: two mod lists and RimSort's two databases repaired, two magenta
texPaths fixed and deployed, two mods that could not compile made to build, a live
EmpirePursuit break repaired and deployed, 45 stale XML type references fixed and held
with their rebuilt assemblies, and validate_patch clean across 436 files.

Commits: `0fda62c9` (mod lists) · `8d96b8b3` (texPaths, skill docs) · `838a41ff`
(lessons) · `e2fdf908` (namespaces, EmpirePursuit, holds) · `644cd945` (nine
assemblies) · `7edae811` (`NAMESPACE_PAIR_DEPLOY_1`).

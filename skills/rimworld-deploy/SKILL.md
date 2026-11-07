---
name: rimworld-deploy
description: Writing a file is not deploying it — RimWorld loads C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>, never this repo, and nothing syncs the two. Covers src/RimMandrake/Utils/deploy_custom_mods.py plan-first then --apply, reading the plan and refusing another seat's files, what a `-` line means and rescuing a hand-edited game copy with --pull, validating with validate_patch.py using BOTH --live and --defs, DEPLOY_HOLD.txt for files undeployed on purpose, why a mod with no About.xml or packageId is not deployable, why a companion DLL cannot be written while the game runs, and how to tell whether a derived artifact is still CURRENT — fingerprint over timestamp, the folder-mtime and capturedUtc traps, the ModsConfig knownExpansions overcount, and empty def-type files that make a --defs check UNMEASURED rather than passed. Use before testing any patch, def, texture, mod folder or assembly in game, and whenever a change appears not to have taken.
---

# Deploying to the game

## 1. "Written" and "the game can see it" are two claims

```
<repo>/custom_patches/<ModName>/   ← source of truth, committed
        ↓  deploy_custom_mods.py
C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>   ← what loads
```

The game names its own copy on every launch:
`Adding mandrake.jawa.patches(C:\...\RimWorld\Mods\Jawa_Patches)`.

**Nothing syncs them.** Editing only the repo means the change silently never
reaches the game — no error, no red text, the def simply is not there. That cost a
whole test cycle once: a xenotype and its pawnkinds authored, reported ready, and
invisible in game because the deployed copy was untouched. **And never edit in
place under `Mods/`** — that copy is disposable, overwritten by the next `--apply`,
and not in version control.

🔑 **Where you run it.** Edit and commit in your seat clone (`/home/mandrake/rm/<seat>`);
`deploy_custom_mods.py` runs from the clone and plans/copies from it. C# mods are built with
`python3 src/RimMandrake/Utils/winbuild.py <Mod|csproj>` (stages on `D:\ClaudeWork\rimmandrake\build`, Windows
dotnet, DLL and `.srchash` copied back as a pair). `D:\Luke\dev\RimMandrake` is a read-only
mirror of origin/main: Windows tools read it, nothing writes it.

🔴 **A subagent's clean `dotnet build`/`validate_patch.py` pass, plus a real
commit+push, is NOT proof the fix was deployed.** Twice in one wave a
genuinely-fixed patch/DLL sat undeployed in the repo while a live re-test still
showed the old failure. Deploying static def/XML output needs no running game —
always run `deploy_custom_mods.py --mod <X>` (plan-only first) before trusting a
live re-check of anything a prior pass claims fixed.

🔑 **"Deployed" and "active" are separate states with nothing reconciling
them.** `deploy_custom_mods.py` writes files and (correctly) never touches the
mod list — it even PRINTS "not enabled in ModsConfig" where nobody reads it. A
mod can be deployed and inert (present on disk, absent from `ModsConfig.xml`,
so it silently never spawns anything) for a long time before anyone notices;
check both states independently, never infer one from the other.

## 2. Plan first. Always read the plan.

```bash
python src/RimMandrake/Utils/deploy_custom_mods.py                 # plan only -- changes nothing
python src/RimMandrake/Utils/deploy_custom_mods.py --apply         # repo -> game, then self-verifies
python src/RimMandrake/Utils/deploy_custom_mods.py --mod Jawa_Patches
python src/RimMandrake/Utils/deploy_custom_mods.py --apply --prune # also delete deployed files gone from the repo
```

Safe by default, skips authoring-side files (`Source/`, `*.py`, `README.md`), warns
when a mod is not enabled in `ModsConfig.xml`, verifies every copy, and exits
non-zero while drift remains — so the plan doubles as a pre-flight check.

🔴 **`--apply` overwrites the game copy with whatever is in the repo *right now*,
including another seat's half-finished work.** Five seats share this tree.

> **Read the plan. `--apply` only if every listed file is yours.** A file you do not
> recognise is a live hazard, not a todo — tell the owner before you write.

⚠️ **With no `--mod`, the walk is alphabetical and a 120s tool-call timeout can
TRUNCATE it mid-list.** A run that stopped at "Cuisine" would have been read as
"only Armoury drifts"; the real answer that day was 5 mods including one the
caller owned. Redirect the run to a file and confirm it printed its final
`Drift found` / `Everything in sync` line before believing any drift list.
- **Deploy a CLEAN tree, never while agents edit, and read the Player.log error classes after.** A deploy copies half-written files and the launch gate then refuses. `deploy_custom_mods.py --compose biomes --apply` is a SEPARATE step from plain `--apply`. A full-sweep `--apply` is not proof every mod deployed: before blaming a third-party mod for a fresh-restart crash, run `deploy_custom_mods.py --mod <each mod touched today>` for drift. A stale `CreatureBehaviors.dll` left 6+ XML-registered classes "Could not find type named", one broken def left `PawnKindDef.race` null, and GeneticRim.Core's static constructor dereferences it unguarded (`item.race.tradeTags`), crashing it and every later call (Need Food, `jawa/spawn_pawn`), looking like GeneticRim's own bug.
- **`--apply --mod X` syncs the WHOLE mod, not just your files.** When a peer is mid-wave in the same mod, a one-file apply also ships their undeployed WIP (275 files where ~8 were yours, and their content then rides the next restart ahead of schedule). Count the files in the plan BEFORE `--apply`; if the count is not yours, stop.
- **Deploy leaves stale copies, and stale defs load.** Deleting or moving a file in the repo does NOT undeploy it: plain `--apply` keeps `-` strays, a `DEPLOY_HOLD` entry never removes a copy already in the game's Mods tree, and a def that moves between mods leaves the old file as a duplicate creature. `--prune` fixes it but sweeps EVERY stray including peers', so the precise fix is a targeted `rm` of the named files in the Mods folder. Clean deploy = `--apply --prune`, then `--compose biomes --apply --prune`, then delete deployed copies of held paths. Plain `--apply` SKIPS the composed `mandrake.rm.biomes` mod. Effects seen: a held TheSump biome plus 3 held files gave 20 dangling cross-refs; a moved `ThingDefs_Abyss.xml` named a missing comp, left a raceless PawnKind and killed three mods' static ctors; a restart on stale biome files reads as 'the fix did nothing'. A defName rename sweep (`RSW_X -> RM_X`) also rewrites history comments ('Moved here from ...'), which then lie: restore them by hand.
- **`deploy_custom_mods.py` with no `--mod` can under-report and under-deploy while exiting 0.** A full-tree plan called FlowWorks 'in sync' while a `--mod` plan minutes later found 4 drifted files (a full 635-mod load then ran with every water terrain discarded); a full-sweep apply left `CreatureBehaviors.dll` drifted until `--mod CreatureBehaviors --apply` wrote it. Re-plan and apply per mod before trusting a full-tree result. Root cause not isolated.
- **A cross-mod check of the game copy must not scope on the live `ModsConfig.xml`** (a 26-mod spike would pass a deploy that breaks the owner's full list). Scope = every deployed `mandrake.*` folder, minus orphan folders (no repo source) that are off `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`; 9 such orphans (GreentideRaidAnt, ManyWaters...) produced false refusals before being scoped out.
- **Run ONE plan and ONE apply per batch** (`--mod A --mod B` in a single invocation) and trust its 'VERIFIED in sync' line. Do not add md5 / PNG-hash / XML census passes afterward: the plan already compares bytes, and each `/mnt/c` stat costs ~1.7 ms (a re-proof burned ~280 s). A full plan is ~118 s / 72k stats; every extra full pass costs that again.
- **A checker comparing 'repo == deployed' must apply every transform the deploy tool applies on the way out**, or it reports drift right after a clean deploy: `deploy_custom_mods` ships `biomes_compose.stage_rewritten` copies (folded-id MayRequire/FindMod rewritten) for ordinary mods, and a raw-src compare read ~28 guard sites as drift. When a deploy gains a transform, grep its verifiers (preflight `c_deploy`, `check_load`) in the same commit.
- **`deploy_custom_mods.py` exits 1 on a Python crash too.** A wrapper must count only rc 0 as deployed, or a crash records the candidate as deployed while the game runs the old build.
- **Reading a whole large file through `/mnt/c` with `os.read` can raise ENOMEM in WSL**, even with free memory and 64 KiB chunks (it failed again at 477 MB free with 30 GB page cache). The read must wait and retry, as `deploy_custom_mods._read_retry` does; any hash or compare over the Steam Mods mount needs the same.

## 3. A `-` line means someone hand-edited the deployed copy

`-` = present in the game, absent from the repo: an edit made directly in `Mods/`
that `--apply` is about to destroy.

```bash
python src/RimMandrake/Utils/deploy_custom_mods.py --pull <ModName>   # game -> repo, rescue it first
```

`--pull` before overwriting, every time.

## 4. Validate BEFORE it goes near the Mods folder — BOTH flags

```bash
python skills/rimworld-modding/scripts/validate_patch.py <file> \
  --live <dump> \
  --defs "C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" \
  --defs "C:/Program Files (x86)/Steam/steamapps/workshop/content/294100" \
  --defs "C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
```

🔴 **The Mods folder is not optional.** First-party `mandrake.*` mods live
there, not in Workshop content — omit it and a real, working cross-mod
`ParentName` inheritance reports as "resolves to no def" (a false failure).

⚠️ **`--live` and `--defs` are orthogonal, and only `--defs` checks xpaths.**
`--live` checks defName existence; `--defs` walks the XML and reports xpath hit
counts. `validate_patch.py <file> --live <dump>` prints `OK - 0 errors` having
evaluated **zero xpaths**, and says so above: `no --defs given; static checks only`.
**If only `--live` ran, nothing was validated.**

🔴 **`measure` is not executable on the Mac laptop** (`permission denied`) and
there is no local def dump there either — "does this def resolve against the
live mod list" is UNMEASURABLE from the laptop. Say so and hand the check to a
session on the Windows Desktop rather than closing the item on an assumption
(2026-09-22).

⚠️ **`--defs` inherits the LIVE `ModsConfig.xml`**, which another seat may have cut
to a spike. Pass the **newest** backup, never a pinned filename, and never a small
spike config — every xpath then legitimately matches nothing and the wall of false
failures burns a day:

```bash
--mods-config infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
```

🔴 **CORRECTED 2026-08-22 by CHECK — the command this section used to give was
`$(ls -t deployed/config/ModsConfig.full-*.xml | head -1)`, and it resolved to the
WRONG STACK.** Measured on the day: that glob returns
`deployed/config/ModsConfig.full-574.2026-08-12.xml` — **574 mods, ten days old, and
it still carries `thereallemon.factioncontrol`**, a mod the owner removed on
2026-08-21 because it aborted three save loads. The live list is **578 and clean**.

The advice ("pass the newest backup, never a pinned filename") was right; the command
was globbing the wrong directory. `deployed/config/` is an ARCHIVE of dated snapshots
and its newest member is only as fresh as the last time someone happened to write one
there. **`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` is the owner's
real list** — it is what `modlist_swap.py --restore` restores FROM (`modlist_swap.py:24`),
so it is maintained rather than merely deposited.

⚠️ **It is still not the LIVE file.** Confirm they agree before trusting a verdict:
```bash
diff <(grep -o '<li>[^<]*</li>' infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml) \
     <(grep -o '<li>[^<]*</li>' "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml")
```

Read the `N active mods → M def files` line before trusting any verdict. **If it does
not say 578, you are validating against a stack the game does not load.** 0 errors
is the bar.

⚠️ **It reads `Patches/` only — never `Defs/`.** New content under `Defs/` is
unvalidated, so parse every XML in the mod folder yourself, `About.xml` included.
- **`validate_patch.py` run without `--defs` cannot see ANOTHER mod's texPath coverage.** It checks only the edited mod's own `Textures/`, so a 'missing texture' result is a false positive when an ArtOverride-style mod supplies that texPath and loads later. Always pass `--defs` with the installed mod dirs including the Mods folder (first-party `mandrake.*` lives there), or every cross-mod `ParentName` check against a first-party def reports a false failure.
- **`validate_patch.py` after a def MOVE/RENAME, and `--live` on an unlisted mod, mislead.** The def dump predates the move, so new names (`RM_Ikee`) read as missing and old ones as fine; `--live` on a mod absent from the live list/dump reports 'does not exist in LIVE game' for every def: that is UNMEASURED, not failed. `--defs src` or `--all-versions` with the workshop path runs past 8 minutes. Recipe that took 2m17s for 8 patch files: a scratch defnames list = dump + every repo defName - every alias `<from>` name; a scratch ModsConfig with only Core+DLCs+harmony+the touched mods (or FULL.LATEST plus the missing mods in load order); a folder of symlinks to those repo mods; then `--mods-config <scratch> --defnames <list> --defs <RimWorld/Data> --defs <symlink folder>`. Remaining errors naming only donor/workshop defs outside that set are conditional no-ops, not defects.
- **`validate_patch.py --defs` against only the game's Data/workshop/Mods folders sees the DEPLOYED copy of our mods.** A patch on defs new in the clone then shows '0 nodes ... probably CREATED by another mod's patch' as a WARN that reads advisory. Add the clone's own `src/<Group>` folders as extra `--defs` roots (stasis ladder patches went from 22 WARN to 0).

## 5. Files undeployed ON PURPOSE — `DEPLOY_HOLD.txt`

`src/DEPLOY_HOLD.txt` is read by the deploy script; anything matching is
reported **HELD** instead of as drift, and `--apply` will not write it.

```
<glob>    # <reason, including who ruled it and when>
```

Paths are relative to `src/`, forward slashes, and **`*` matches across
directory separators** — `WreckedMachines/*` holds the whole tree.

**A reason is REQUIRED.** Without one the plan can only say "the repo and the game
differ": *parked on purpose* and *half-finished* render identically, and both end
with "Drift found. Re-run with `--apply`." Acting on that overrides an owner ruling
while looking like housekeeping. **It is PER-FILE, not per-mod** — a live mod can
have two held files while the rest of it keeps deploying, and inferring the hold
from `ModsConfig.xml` only proves a mod is INERT, never that it is INTENDED.

🔑 **"Not in the Workshop folder" is not "not available."** Donor mod sources
are vendored at `vendor/mod_sources/` — check there before concluding a donor
mod's own XML/source is unreachable.
- **`DEPLOY_HOLD.txt` keys are `<ModFolder>/<path in mod>` (`deploy_custom_mods.hold_for`), NOT src-relative.** A line starting `RimStarWars/...` or `RimMandrake/...` silently holds nothing. After adding a hold, run `deploy_custom_mods.py --mod <Mod>` and confirm the file shows `H`, not `+`.

## 6. Not every folder is deployable

**A mod with no `About/About.xml`, or no `packageId` in it, is not a mod.**
Deploying it creates a `Mods/` folder RimWorld ignores; the plan flags
`no packageId in About.xml`. That is **a ruling to ask for, not a file to invent** —
a packageId is an identity, and guessing one ships a name nobody chose. Hold the
mod with its reason and put the decision in the owner's path. Minimum viable folder:

⚠️ **That refusal message can point at the wrong field.** It also fires when
`ET.parse` throws on a genuinely malformed `About.xml` — a raw `<=`/`<` inside
plain description text parses as a tag start (`harvestAfterGrowth <= 0f` written
straight into a description broke one this way). The tool refused correctly; the
message named `packageId` when the real defect was that the file does not parse
at all. Check the file actually parses before assuming the packageId is absent.

🔴 **`[ -e "$dir" ]` is not a test for "a mod lives here."** `src/RimMandrake/Pits`
passed that test while holding only `__pycache__` — the mod had merged elsewhere
and the folder was a shell. Test `$dir/About/About.xml` instead; existence of a
directory is not identity of a mod.

```
<ModName>/
├── About/About.xml          (packageId, name, supportedVersions, description)
└── Patches/<Something>.xml  (or Defs/ for new content)
```
- **Mod folder basenames must be unique across tiers.** `deploy_custom_mods.py` builds its mod map keyed on the bare folder name while iterating the tiers (`RimMandrake`, `RimStarWars`, `RimUtinni`, `SPLIT_Phase3`) in fixed order; two mods with the same folder name in different tiers silently overwrite each other (later tier wins, no warning) and the shadowed one, even the one carrying the compiled hook, never appears in the plan. The game uses the packageId, so give each mod a distinct folder name.

## 7. Assemblies deploy in the shutdown window, not now

A DLL the game has loaded **cannot be written while RimWorld runs** — memory-mapped,
and Windows refuses with `WinError 1224`. The copy is impossible, not merely
ineffective. Deploy in the gap after the game closes and before it launches, and
tell CHECK before any shutdown: `skills/rimworld-load-round/SKILL.md` §6.

🔴 **`deploy_custom_mods.py --mod <X>` deploys only that one mod, not the mods it
depends on.** A new mod referencing a class from a SIBLING mod's assembly (a
`<li Class="RimMandrake.SomeNamespace.SomeExtension">` pointing at another mod's
compiled comp) got enabled and deployed while the DEPENDENCY mod's own rebuilt
DLL had never actually been redeployed — confirmed by comparing deployed-vs-repo
DLL mtimes (the deployed copy was hours stale). A stale dependency DLL missing a
referenced type can crash mod-loading badly enough to trip RimWorld's own
corrupted-mods safety net (§ below), resetting `ModsConfig.xml` — not just log a
quiet config error. **When enabling a mod that leans on another mod's C# (a
shared "engine" assembly), deploy BOTH mods explicitly before the next launch.**

⚠️ **But `WinError 1224` is not the only lock failure, and the other one is
silent.** `deploy_custom_mods.py --apply` has printed the DLL's `~` plan line
and "Deployed N file(s)" while silently SKIPPING a locked assembly — the file
count printed is the only tell that it did not match the plan-line count.
Mechanism: a TRUNCATING copy (`shutil.copy2`, `open(dst, "wb")`) fails on a
locked file with `[Errno 22] Invalid argument` while an in-place
`open(dst, "r+b")` write + `os.truncate` lands byte-identical. Without the
in-place route, the XML half of a deploy lands and the DLL half silently does
not — which discards every def whose comp `Class` lives in that DLL. Re-run
once the game is really gone, and check the deployed vs. plan file counts
before trusting either "Deployed" line.

⚠️ **`MayRequire` checks the MOD, never the TYPE — it is no protection against
an assembly that is PRESENT but STALE.** New C# written and never rebuilt can
leave types missing from the deployed DLL while every `Class=` reference
guards correctly on the mod being active: the guard passes, the type still
isn't there, and the def carrying it is silently discarded. Check that the
type is actually IN the deployed DLL's bytes, not merely that the owning mod
is active. (2026-09-21)

## 7b. 🔴 Is this artifact CURRENT? Never answer from a timestamp

Half the deploy questions in this project are really one question — *does this
derived thing still describe what the game loads?* — and reading **age** to answer
it has now been wrong four separate times in one day. The rule:

> **Trust a fingerprint of the load-set. Never a clock, on any layer:
> folder mtime, file mtime, or the artifact's own captured timestamp.**

Each of these was believed, acted on, and false:

| the reading | why it lied |
|---|---|
| **A folder's mtime** | `DefDump/defs/` read `Aug 14` while every file inside was written `Aug 15`. A dump that **overwrites a fixed set of filenames** creates and deletes nothing, so the directory mtime never moves. Generalises to any tool that rewrites the same names. |
| **The artifact's own `capturedUtc`** | Fresh in TIME is not fresh in SET. A dump captured 08:10 missed a mod deprecated at 11:58. **Direction matters**: that dump is a *superset* — everything live is described correctly, but it still carries defs from a mod that no longer loads, so an xpath onto *those* validates **clean** and matches **nothing** in game. |
| **A bare `<li>` count in `ModsConfig.xml`** | Reads 580 against a true 575. The file holds a second list, `knownExpansions`, duplicating the DLC ids. **Scope the count inside `<activeMods>`.** |
| **`Version.txt`** | Reads `rev590` while every engine-written file reads `rev591`. **The build stamp comes from the RUNNING game**, not from the file that appears to name it. (BUILD, 2026-08-15) |
| **A flat `DefDump/manifest.json` reader** | Silently degrades to `Version.txt` since the dump layout migrated to `captures/` — the flat path is gone, the reader finds nothing, and it resurfaces the exact rev590/591 lie one row up. `sync_mod_state.py` nearly stamped `rev590` over `rev591` saves before this was caught (fixed `801bd127`; swept as `FLAT_MANIFEST_READER_SWEEP_1`). |
| **`refresh.py` calling `defs.sqlite` "current"** | `DumpDB.stale` checks the mod-set **fingerprint**, not whether the capture it names still **exists on disk**. Retention had already PRUNED the source capture (built 08-23) while a newer one existed (08-29); the fingerprint still matched, so the verdict read current anyway. Rebuild whenever provenance names a missing capture — a matching fingerprint is not proof the file behind it survives (BENCH 2026-08-29). |
| **A generator's own "regenerating is a no-op" header comment** | Can drift silently from a renamed/moved target and never say so. `gen_pawnkind_roster.py`'s own claim was stale — it emitted pre-rename defNames across 49 `PawnKindDef`s, and a routine re-run per the file's own instructions would have silently reverted a whole naming migration. **Verify a generator's no-op claim with `git diff --stat` against committed output, never the exit code** (2026-09-18). |

✅ **What was right the whole time: `refresh.py`'s `STALE` verdict**, because it
keys on the load-set fingerprint rather than the clock — and it named the one real
mod while two seats were escalating the wrong thing. **Believe it over your own
timestamp arithmetic.**

⬜ **Coverage is a third axis, after time and set.** 79 of 529 def-type files in
the 2026-08-15 dump are **empty** (`AbilityDef` among them), so for those types
"absent from the dump" says nothing at all about the game. A `--defs` check
against an empty type is **UNMEASURED, not passed** — give it its own exit code
and its own word, or it silently becomes a green tick.

📌 Dump location, freshness and known holes are published by the seat that
measures them: `observed/LIVE.md`. **Read it; do not
re-derive it**, and do not copy its numbers into another doc where they will rot.
- **A stale or mismatched DLL fails silently, so confirm the code is the code you think.** (1) A deployed DLL older than the fix just does not print its startup self-test line: 'no crash' reads old code as a pass, so confirm the line is present. (2) An interrupted or locked `--apply` can update the `.srchash` sidecar but not the binary; only the plan's drift check (`~` line) catches it, and the symptom is unrelated 'missing ThingDef' cross-ref errors. (3) A committed DLL can be stale vs its source ('type missing'): rebuild with `winbuild.py` before trusting a 'type missing' error. (4) A deployed DLL referencing a type that a stale sibling DLL lacks (composed biomes deployed without FlowWorks: FloodedCanyon's DLL named a FlowWorks type, `ReflectionTypeLoadException` at boot) kills the load: dry-run every tier mod for drift before launching. (5) A live session on a DLL older than the repo's gives MOD verdicts on code nobody can name: check assembly identity (type_probe sha vs repo DLL) BEFORE reading any setting, since a newer setting the old build lacks aborts the sweep with a misleading 'No public field'.

## 8. After deploying

- **Restart RimWorld.** Defs are parsed once at startup; reloading a save does not
  pick up new XML. Adding brand-new defs is safe for an existing save; changing or
  removing a def a save already references is not.
- **Enable compatibility-patch mods LAST in load order.** Patches apply in load
  order, so a fix-up mod loading before the mod it fixes patches a def that has not
  been redefined yet, and the redefine wins. This is the most common reason a
  correct patch appears to do nothing.
- **One mod at a time**, verified before the next — `skills/rimworld-load-round/SKILL.md` §3.
- Test on a dev-mode throwaway world and read `Player.log` for the patch's own name
  before trusting it in the campaign save.
- 🔴 **"Deployed and VERIFIED" is true only until the next writer.** Every clone
  deploys to the same Mods folder: a subagent's verified UtinniPatches deploy was
  overwritten within minutes by another clone deploying from an older sha. Before
  calling a fix live, re-run the deploy dry run from a clone AT the fix sha — a
  clean plan (no `~`/`-` lines for your files) is the proof; the earlier report is not.
A "done" or "reverted" claim about a deploy is only as good as its last re-measure against the live Mods folder. A deployed folder can carry a different mod identity than `ModsConfig.xml` references (a full successor sat under the old packageId for two days, found only when a load check refused). Compare deployed packageId and files with ModsConfig's own references, not the item's prose.
- **A build/move that says content 'moved' may have COPIED.** TerminalBiomes left 16 byte-identical twins in UtinniPatches and 8 pairs deployed as duplicate defNames. After any move, diff BOTH trees before believing it, and a duplicate-defName load error means look for the old copy.
- **A new `MapComponent` never activates on a map generated and saved before its DLL was deployed:** `FinalizeInit()` runs once, at map creation, so an older save carries no instance whatever the tick count. Verify its live behaviour on a map generated AFTER the fix is deployed, never by reloading an older save.
- **A Wave/list deploy must plan BOTH `deploy_custom_mods.py` (whole tree) AND `deploy_custom_mods.py --compose biomes`.** The whole-tree plan does not cover the composed `RimMandrake.Biomes` mod, so a deployed UtinniPatches BiomeDef naming new composed defs xref-failed and aborted a load. `--compose biomes` is all-or-nothing: it ships every committed change in every folded folder whatever seat made it (it once carried another seat's CreatureBehaviors, GelatinousSlime and Webwork DLLs). It has no seat markers, so read its DLL `~` lines before `--apply` and name the seats in the report; only uncommitted work is out of bounds.

## 9. Validation plan — what you owe whoever holds the game

**A deploy ends with a validation plan, not with `--apply`.** You are almost never
the seat that will see it work: a game load costs **23–30 minutes** and one game is
shared by five seats, so whoever holds it needs your prediction, not a nudge to
"have a look at the Jawa stuff".

### The six fields

**1. The observable** — what a player SEES when it works. 🔴 A positive
observation, never "no error"; absences are the cheapest thing in the world to
produce by accident.
**2. The route** — the exact call, defName or click path that produces it.
**3. The prediction** — a number or specific string, written BEFORE the look.
**4. The threshold** — what CLOSES it, and the minutia explicitly out of scope. An
item with no threshold is inspected forever; one observation, not a battery.
**5. Batch or solo** — most checks ride together; **a new assembly goes solo**,
because if the load comes up wrong nobody can tell whether it was the DLL or the
three def changes beside it.
**6. What a FALSE PASS looks like** — the way this particular check lies.

```
PROVE    <exact call / defName / click path>
EXPECT   <number or string, written before the look>
LIES     <how this check produces a false pass>
```

Three lines: the call, the expected reading, and how a pass could be false. 🔴 And first
ask whether it needs the game at all — the default is source. Rule and false-pass catalogue:
`skills/rimworld-modding/references/validation-plan.md`.

### The four ways a DEPLOY produces a false pass

1. **A successful write says nothing about the running game.** RimWorld parses defs
   and loads assemblies **once, at startup**. `--apply` reporting every file copied
   and verified is a statement about the filesystem; the process that matters read
   its copy minutes or hours ago. ⇒ **LIES** must name what the game last loaded
   and when, not what the plan printed.
2. **An assembly the game holds cannot be overwritten — and the failure is easy to
   file and forget.** Windows refuses with `WinError 1224` (§7), so the copy does
   not silently succeed; but the game folder is now carrying a **different build**
   from the repo, and nothing in the plan output distinguishes "same DLL" from
   "yesterday's DLL". **md5 both copies — it is the only way to know:**
   ```bash
   md5sum src/<Mod>/Assemblies/<Name>.dll "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/<Mod>/Assemblies/<Name>.dll"
   ```
3. **An unscoped `--apply` deployed more than you think.** Five seats share one
   working tree, so a bare `--apply` sweeps up whatever else is dirty — including
   another seat's half-finished work — and any breakage in that load gets
   attributed to your change. ⇒ **Scope every deploy: `--mod <ModName>`**, and say
   in the plan which mods moved.
4. **"Deployed" and "live" are different words.** A folder under `Mods/` changes
   nothing until it is **enabled in the load order** (and, for a compatibility
   patch, enabled LAST — §8). The plan warns when a mod is absent from
   `ModsConfig.xml`; a plan that was not read is a mod that is on disk and inert.

### Worked example

A Harmony patch shipped as a new DLL for `Jawa_Patches`, deployed in the shutdown
window:

```
PROVE    Spawn Jawa + MeleeWeapon_Vibroblade, spawn a muffalo, draft and attack; watch the combat log
EXPECT   A Jawa with a vibroblade attacks twice in the time a vanilla knife pawn attacks once · Cooldown 1.4s (was 2.6s); Player.log prints "[Jawa_Patches] 3 patches applied"
LIES     Game copy may be the PREVIOUS build if RimWorld was running at deploy (WinError 1224); md5 both DLLs before the load. Absent Harmony line = patch never applied, not "nothing to report".
```

⚠️ **Write it in the same commit as the deploy.** The alternative is that whoever
holds the game invents a check, and theirs will not carry your prediction — which
is the field that turns a look into evidence.

## The deployed companion DLL runs behind source, and a missing tool is ambiguous

A companion assembly deploys only in a game-down window, so the game copy drifts behind the
repo for as long as the game stays up. Measured once at **166 tool names deployed against
238 built** — 670 KB of IL, everything written that day.

⇒ **A tool missing from `--list-tools` proves nothing on its own:** undeployed, gated out of
the build, or genuinely absent all read identically. Disambiguate with `build.py`'s own
`tool_surface()` over both DLLs.

⚠️ **That is a BYTE SCAN.** Its "added" list is untrustworthy — encoding differences make
tools that shipped weeks ago look new. Trust it for `LOST` being empty and for a name being
PRESENT; corroborate a gap with file size and the build commit stamped in the assembly.

⛔ **A `jawa/` literal written in PROSE inside a tool description becomes a phantom tool
name**, which makes `build.py`'s "THIS DEPLOY WOULD REMOVE TOOLS" guard lie in both
directions. After any description edit: `[x for x in surface if x.endswith('_')]`.

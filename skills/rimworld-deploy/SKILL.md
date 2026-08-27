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
  --defs "C:/Program Files (x86)/Steam/steamapps/workshop/content/294100"
```

⚠️ **`--live` and `--defs` are orthogonal, and only `--defs` checks xpaths.**
`--live` checks defName existence; `--defs` walks the XML and reports xpath hit
counts. `validate_patch.py <file> --live <dump>` prints `OK - 0 errors` having
evaluated **zero xpaths**, and says so above: `no --defs given; static checks only`.
**If only `--live` ran, nothing was validated.**

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

## 6. Not every folder is deployable

**A mod with no `About/About.xml`, or no `packageId` in it, is not a mod.**
Deploying it creates a `Mods/` folder RimWorld ignores; the plan flags
`no packageId in About.xml`. That is **a ruling to ask for, not a file to invent** —
a packageId is an identity, and guessing one ships a name nobody chose. Hold the
mod with its reason and put the decision in the owner's path. Minimum viable folder:

```
<ModName>/
├── About/About.xml          (packageId, name, supportedVersions, description)
└── Patches/<Something>.xml  (or Defs/ for new content)
```

## 7. Assemblies deploy in the shutdown window, not now

A DLL the game has loaded **cannot be written while RimWorld runs** — memory-mapped,
and Windows refuses with `WinError 1224`. The copy is impossible, not merely
ineffective. Deploy in the gap after the game closes and before it launches, and
tell CHECK before any shutdown: `skills/rimworld-load-round/SKILL.md` §6.

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

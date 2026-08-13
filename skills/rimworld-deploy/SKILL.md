---
name: rimworld-deploy
description: Writing a file is not deploying it — RimWorld loads C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>, never this repo, and nothing syncs the two. Covers src/RimMandrake/Utils/deploy_custom_mods.py plan-first then --apply, reading the plan and refusing another seat's files, what a `-` line means and rescuing a hand-edited game copy with --pull, validating with validate_patch.py using BOTH --live and --defs, DEPLOY_HOLD.txt for files undeployed on purpose, why a mod with no About.xml or packageId is not deployable, and why a companion DLL cannot be written while the game runs. Use before testing any patch, def, texture, mod folder or assembly in game, and whenever a change appears not to have taken.
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
--mods-config "$(ls -t deployed/config/ModsConfig.full-*.xml | head -1)"
```

Read the `N active mods → M def files` line before trusting any verdict. 0 errors
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
tell BRIDGE before any shutdown: `skills/rimworld-load-round/SKILL.md` §6.

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

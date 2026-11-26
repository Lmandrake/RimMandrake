---
name: rimworld-deploy
description: Writing a file is not deploying it — RimWorld loads C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>, never this repo, and nothing syncs the two. Covers src/RimMandrake/Utils/deploy_custom_mods.py plan-first then --apply, reading the plan and refusing another seat's files, what a `-` line means and rescuing a hand-edited game copy with --pull, validating with validate_patch.py using BOTH --live and --defs, DEPLOY_HOLD.txt for files undeployed on purpose, why a mod with no About.xml or packageId is not deployable, why a companion DLL cannot be written while the game runs, and how to tell whether a derived artifact is still CURRENT — fingerprint over timestamp, the folder-mtime and capturedUtc traps, the ModsConfig knownExpansions overcount, and empty def-type files that make a --defs check UNMEASURED rather than passed. Use before testing any patch, def, texture, mod folder or assembly in game, and whenever a change appears not to have taken.
---

# Deploying to the game

The evidence and the old lines that are no longer true are in [references/history.md](references/history.md).

## 1. "Written" and "the game can see it" are two claims

```
<repo>/src/<tier>/<ModName>/       ← source of truth, committed
        ↓  deploy_custom_mods.py
C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>   ← what loads
```

- `<tier>` is `RimMandrake`, `RimStarWars`, `RimUtinni` or `SPLIT_Phase3`. The deployed folder has the bare mod name.
- The `Mods` path in the figure is the folder of ArchBig, Steam's install. A deploy with no game named writes ArchBig's
  folder.
- ArchSmall on Archmagi has its own install and its own `Mods` (`D:\ClaudeWork\rimmandrake\instances\b\game\Mods`).
- To deploy to ArchSmall, run `deploy_custom_mods.py --mod <name> --instance ArchSmall` (or set `RM_GAME_INSTANCE=b`). That
  deploy writes only under ArchSmall.
- Deploy to the game that your run drives, never to another run's game.
- Each plan prints the folder that it compares, on its `game :` line. Read that line before `--apply`.
- To see which copy a game loaded, read the paths in its `Player.log`. Its XML messages name the file, as in
  `[File: C:\...\RimWorld\Mods\UtinniPatches\...]`.

**Nothing syncs them.** If you edit only the repo, the change never reaches the game, and nothing tells you. There is no
error and no red text. The def is simply not there.

- An edit of the repo alone cost a whole test cycle once. A xenotype and its pawnkinds were written and reported ready. The new defs were invisible in game, because nobody had touched the deployed copy.
- **And never edit in place under `Mods/`.** That copy is disposable and is not in version control. The next `--apply`
  overwrites it.

🔑 **Where you run it.**

- Edit and commit in your seat clone (`/home/mandrake/rm/<seat>`) or in the helper clone that your brief names.
- Run `deploy_custom_mods.py` from that clone. The tool plans and copies from the clone that holds it.
- Build a C# mod with `python3 src/RimMandrake/Utils/winbuild.py <Mod|csproj>`. The tool stages on
  `D:\ClaudeWork\rimmandrake\build` and builds with Windows dotnet. Then the tool copies the DLL and the `.srchash` back as a pair.
- `D:\Luke\dev\RimMandrake` is a read-only mirror of origin/main. Windows tools read it. Nothing writes it.

🔴 **A subagent's clean `dotnet build`/`validate_patch.py` pass, plus a real commit+push, is NOT proof the fix was deployed.**

- Twice in one wave, a patch or DLL that was truly fixed sat undeployed in the repo. A live test still showed the old
  failure.
- A deploy of static def or XML output needs no running game.
- Before you trust a live check of a fix that an earlier run claims, always run `deploy_custom_mods.py --mod <X>`. Run the
  plan first.

🔑 **"Deployed" and "active" are separate states with nothing reconciling them.**

- `deploy_custom_mods.py` writes files. The tool never touches the mod list, and that is correct. The tool even
  PRINTS "not enabled in
  ModsConfig", but nobody reads that flag.
- A mod can be on disk and absent from `ModsConfig.xml`. Such a mod is inert: it spawns nothing, with no message. That state
  can last a long time before anyone sees it.
- Check both states, each on its own. Never infer one from the other.

## 2. Plan first. Always read the plan.

```bash
python3 src/RimMandrake/Utils/deploy_custom_mods.py                 # plan only -- changes nothing
python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply         # repo -> game, then self-verifies
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod UtinniPatches
python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply --prune # also delete deployed files gone from the repo
```

What the tool does:

- The default run is safe: it changes nothing.
- The tool skips authoring-side files (`Source/`, `*.py`, `README.md` and every other `.md`, and more). The plan's `skip :`
  line names the skipped folders and extensions.
- The tool warns when a mod is not enabled in `ModsConfig.xml`.
- After `--apply`, the tool compares each mod that differed again, byte for byte.
- **Drift** is any difference between the repo copy and the game copy. Held files (§5) and skipped files are not drift. A
  plan
  exits non-zero while drift remains. So the plan is
  also a pre-flight check.
- A folder that is folded into the composed biomes mod (`mandrake.rm.biomes`) is refused by name. The refusal prints the
  `--compose biomes` command. A run with no `--mod` skips those folders. So a clean plan proves nothing about the composed
  biomes: plan them with `--compose biomes`.

🔴 **`--apply` overwrites the game copy with whatever is in the repo *right now*, including another seat's half-finished
work.**

- "The repo" here is your clone, with its uncommitted files. A subagent that edits in your clone is in it too.
- Each clone is separate, but every clone deploys to the same `Mods` folder of a game. A clone that is behind puts an old
  file over a newer deployed file.

> **Read the plan. `--apply` only if every listed file is yours.** A file you do not recognise is a live hazard, not a
> todo.

- Before you write a file that you do not recognise, read its `git log`. A file that nobody ever
  committed has none, and a log does not name the author of an uncommitted edit. Bring your
  clone level with origin/main
  (`clone-landing-commits` skill). Then plan again.
- If the file is still in the plan, tell the Conductor before you write. A helper puts it in a note on its item.

⚠️ **With no `--mod`, the walk is alphabetical and a 120s tool-call timeout can TRUNCATE it mid-list.**

- One truncated run stopped at "Cuisine". A reader of that run would have said "only Armoury drifts". The real answer that
  day was 5 mods, and one of them was the caller's.
- Send the run to a file. Believe a drift list only after the file holds the last line, `Drift found` or
  `Everything in sync`.

More traps for this section: [references/traps.md](references/traps.md) § 2. Plan first. Always read the plan..

## 3. A `-` line means someone hand-edited the deployed copy

`-` = present in the game, absent from the repo. The heading names one cause. The plan tells three kinds apart, and each `-`
line
names its kind:

| the `-` line says | cause | what `--apply` does |
|---|---|---|
| `deleted in repo` | a commit deleted or moved the file | deletes the game copy |
| `deleted in repo working tree, UNCOMMITTED` | a delete or a move that nobody committed yet | keeps the game copy, unless you pass `--prune` |
| `kept — use --prune to delete, or --pull to rescue` | a file that your clone's history never deleted: a hand edit, or a file that a newer clone deployed | keeps the game copy, unless you pass `--prune` |

- If your clone is behind origin/main, a file of another clone's newer deploy can read `kept`. Level your clone and plan
  again
  before you use `--pull` or `--prune`. `--pull` would import that file, and `--prune` would delete it from the game.
- `--apply --prune` deletes every `-` file that no hold covers (§5), so it destroys a hand-made file. After a refusal or a
  failed write, the tool deletes nothing in that mod.
- A hand edit to a file that the repo also has is a `~` line, not a `-` line. Plain `--apply` destroys that edit.

```bash
python3 src/RimMandrake/Utils/deploy_custom_mods.py --pull <ModName>   # game -> repo, rescue it first
```

- `--pull` before overwriting, every time. The tool refuses `--pull` for a folded biome member and for the composed biomes mod.
  In a `--compose biomes` plan, an uncommitted delete reads `kept`.
- `--pull` copies every file of that mod that differs, also a file whose repo copy is newer. That copy also
  brings back a file that the repo deleted. Read `git diff` before you commit. One malformed XML in the game copy stops the
  whole pull.

## 4. Validate BEFORE it goes near the Mods folder — BOTH flags

```bash
python3 skills/rimworld-modding/scripts/validate_patch.py <file> \
  --live <dump> \
  --defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" \
  --defs "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100" \
  --defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
```

- `<dump>` is the `DefDump` folder of the game's user data. The tool takes the newest capture in it and prints which one.
- These paths are for WSL. With a `C:/` root, WSL python prints `UNMEASURABLE` and gives no verdict. Windows python takes the
  `C:/` form.
- One patch file took about 4 minutes with all three roots (2026-11-23). Run it with a timeout above that, to a file.

🔴 **The Mods folder is not optional.** Our own `mandrake.*` mods are there, not in the Workshop content. Without that
root, a correct `ParentName` that points into another mod of ours reads as "resolves to no def". Such a reading is a false failure.

⚠️ **`--live` and `--defs` are orthogonal, and only `--defs` checks xpaths.**

- `--live` checks that a defName exists. `--defs` walks the XML and reports the hit count of each xpath.
- `validate_patch.py <file> --live <dump>` can print `OK - 0 errors` with **zero xpaths** evaluated. The top of that run says
  `no --defs: ParentName and Class checks are SKIPPED and no xpath is executed`.
- **If only `--live` ran, nothing was validated.**

🔴 **`measure` is not executable on the Mac laptop** (`permission denied`), and that laptop has no local def dump
(2026-09-22).

- So "does this def resolve against the live mod list" is UNMEASURABLE from the laptop.
- Say so. Give the check to a session on Archmagi, the Windows Desktop. Do not close the item on an assumption.

⚠️ **`--defs` inherits the LIVE `ModsConfig.xml`**, and another seat may have cut that list to a spike (a small test list).

- Pass the mod's small list (`design/concepts/<Mod>/version/small_list.json` names its tier), never a dated backup with
  its date in the name (`CLAUDE.md` §Mod development runs on small lists).
- Never pass another seat's spike config in its place. That config may lack a mod that this mod patches. Every xpath into an
  absent mod then matches nothing, and the wall of false failures burns a day.

```bash
--mods-config infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
```

- **`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` is the owner's real list.** `modlist_swap.py --restore` writes
  that file back to the live list. `modlist_swap.py --capture-full` updates that file. So the list is maintained.
- `deployed/config/` is an ARCHIVE of dated snapshots. Its newest member is only as fresh as the last write. Never glob it
  for "the newest list": on 2026-08-22 that glob gave a ten-day-old stack.

⚠️ **It is still not the LIVE file.** Compare the two lists before you trust a verdict:

```bash
diff <(grep -o '<li>[^<]*</li>' infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml) \
     <(grep -o '<li>[^<]*</li>' "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml")
```

- That path is ArchBig's live list. ArchSmall's is `D:\ClaudeWork\rimmandrake\instances\b\Config\ModsConfig.xml`.
- If the lists differ, find the cause first. The live file can hold a tier (a smaller test list) on purpose, or `FULL.LATEST` can be behind.
- Read the `N active mods … -> M def files` line before you trust any verdict. **If N is not the count of the list that the
  game will load, you are validating against a stack the game does not load.** Parse `activeMods` for that count.
- 0 errors is the bar.

⚠️ **`validate_patch.py` reads `Patches/` and `Defs/`, and each run prints what it did not scan.**

- For a def file, the tool checks the XML parse, the comment bodies and missing or duplicate defNames. The tool also checks `ParentName`, `Class` attributes and texture paths.
- The tool does not check field names, field types, value ranges or C# class members. The tool cannot see a node that a patch
  creates at load.
- Give the tool the whole mod folder, so that it lists every XML, `About.xml` included. If you give it less, parse every
  other XML
  in the mod folder yourself.

More traps for this section: [references/traps.md](references/traps.md) § 4. Validate BEFORE it goes near the Mods folder — BOTH flags.

## 5. Files undeployed ON PURPOSE — `DEPLOY_HOLD.txt`

The deploy script reads `src/DEPLOY_HOLD.txt`. A file that matches a line there is **HELD**. The plan does not count a held
file as drift. `--apply` does not write that file, and `--prune` does not delete it. A hold does not remove a copy that is
already in the
game.

```
<glob>    # <reason, including who ruled it and when>
```

- A path is `<ModFolder>/<path in the mod>`, with forward slashes and no tier in front.
- **`*` matches across directory separators.** So `WreckedMachines/*` holds the whole tree.

**A reason is REQUIRED.** The script does not refuse a line with no reason. The plan then prints `NO REASON GIVEN`.

- Without a reason, nobody can tell a file that is *parked on purpose* from a file that is *half-finished*. Both look the
  same.
- With no hold line at all, the plan can only say "the repo and the game differ". Both files end with "Drift found. Re-run
  with
  `--apply`." If you act on that, you override an owner
  ruling, and it looks like housekeeping.

**A hold is PER-FILE, not per-mod.** A live mod can have two held files while the rest of it keeps deploying.

- Do not infer a hold from `ModsConfig.xml`. Absence from that list proves only that a mod is INERT. Absence never proves that the state is INTENDED.

🔑 **"Not in the Workshop folder" is not "not available."** Copies of donor mod sources are in `vendor/mod_sources/`. Look
there before you decide that a donor mod's XML or source is out of reach.

- The copies are not in git: a clone has only `SOURCES.md`. The copies are in `D:\Luke\dev\RimMandrake\vendor\mod_sources`.

More traps for this section: [references/traps.md](references/traps.md) § 5. Files undeployed ON PURPOSE — `DEPLOY_HOLD.txt`.

## 6. Not every folder is deployable

**A mod with no `About/About.xml`, or no `packageId` in it, is not a mod.**

- RimWorld ignores such a folder under `Mods/`.
- With no `About/About.xml`, the tool does not see the folder: `--mod` says `no such mod in the repo`.
- With no `packageId`, the plan flags `no packageId in About.xml`, and `--apply` refuses that mod.
- The packageId is **a ruling to ask for, not a file to invent**. A packageId is an identity. A guess ships a name that
  nobody
  chose.
- Add a `DEPLOY_HOLD.txt` line for the mod with its reason (§5), and put the decision to the Conductor. A new packageId follows
  `design/NAMING_SCHEME_PLAN.md`.

⚠️ **That refusal message can point at the wrong field.**

- The message `no packageId in About.xml` also appears when `ET.parse` throws on a malformed `About.xml`.
- A raw `<=` or `<` in plain description text parses as the start of a tag. `harvestAfterGrowth <= 0f`, written straight into
  a description, broke one file this way.
- The tool was right to refuse. But the message named `packageId`, and the real defect was that the file does not parse.
- Check that the file parses before you assume that the packageId is absent.

🔴 **`[ -e "$dir" ]` is not a test for "a mod lives here."** One mod's folder passed that test while it held only
`__pycache__`. The mod had merged elsewhere, and the folder was a shell. Test `$dir/About/About.xml` instead. A directory
that exists does not prove which mod it is.

The smallest folder that deploys:

```
<ModName>/
├── About/About.xml          (packageId, name, supportedVersions, description)
└── Patches/<Something>.xml  (or Defs/ for new content)
```

More traps for this section: [references/traps.md](references/traps.md) § 6. Not every folder is deployable.

## 7. Assemblies deploy in the shutdown window, not now

A DLL that a game has loaded **cannot be written while that game runs**. The file is memory-mapped, and Windows refuses with
`WinError 1224`. The copy is impossible, not merely ineffective.

- Deploy in the **shutdown window**: the gap after the game closes and before it launches.
- The lock is per install. ArchBig locks the DLLs in ArchBig's `Mods`, and ArchSmall locks those in ArchSmall's `Mods`.
- A reboot is yours to call: `infrastructure/GAME_STATE_WORKFLOW.md` § A REBOOT IS YOURS TO CALL. Before you close a game,
  its
  bridge must be free or yours. Take the bridge for the reboot, so that the other runs can read the reason.
- Do not close a game while his OWNER hold or `./pipe off game:<name>` stands on it (a look at staged work, on
  ArchBig or ArchSmall). Stop a broken
  game at once, and report it.
- Deploy in the gap. Then run `preflight_bridge.py` before the launch, as that section says. Announce the restart in your
  reply
  after the fact.
- The window is described in `skills/rimworld-load-round/SKILL.md` §6.

🔴 **`deploy_custom_mods.py --mod <X>` deploys only that one mod, not the mods it depends on.**

- A new mod named a class from a SIBLING mod's assembly. Its XML held
  `<li Class="RimMandrake.SomeNamespace.SomeExtension">`, which points at a compiled comp of that other mod.
- The new mod was enabled and deployed. The rebuilt DLL of the DEPENDENCY mod had never been deployed again.
  The deployed copy was hours older than the repo copy.
- A stale dependency DLL that lacks a referenced type can crash mod loading. The crash can trip RimWorld's own corrupted-mods
  safety net, which resets `ModsConfig.xml`. A reset is worse than a quiet config error. The reset is described in
  `skills/rimworld-load-round/SKILL.md` § Automated sweeps across many mod-list batches: `loadsweep/`.
- **When enabling a mod that leans on another mod's C# (a shared "engine" assembly), deploy BOTH mods explicitly before the
  next launch.**

⚠️ **But `WinError 1224` is not the only lock failure, and the other one is silent.**

- `deploy_custom_mods.py --apply` once printed the `~` plan line of the DLL and "Deployed N file(s)". But the tool had
  SKIPPED the locked assembly with no message. The only sign was the printed file count: it did not match the count of plan
  lines.
- A TRUNCATING copy (`shutil.copy2`, `open(dst, "wb")`) of a locked file fails with `[Errno 22] Invalid argument`. An
  in-place `open(dst, "r+b")` write landed once. On 2026-11-24 a write to a DLL that the running game had loaded failed
  with Errno 22 after a good r+b open, and the partial deploy left the new .srchash beside the old DLL (lesson
  `20261124T155533Z-BENCH-deploy-open-probe-misses-locked-dll`). An open is no test that a deploy can land. Deploy DLLs
  with the game down. The deploy tool has no in-place route: it uses `shutil.copy2`.
- So the XML half of a deploy can land while the DLL half does not. Then every def whose comp `Class` is in that DLL is
  discarded.
- The tool now prints `FAILED to write`, then `STILL DIFFERS`, and exits 1. The tool still prints "Deployed N file(s)" when any
  other
  file landed.
- Run again when the game is really gone. Compare the deployed count with the plan count before you trust either "Deployed"
  line. `VERIFIED in sync` is the proof for each `+` and `~` file that no hold covers. That line does not count a `-` file that the tool kept: the game still loads that file.

⚠️ **`MayRequire` checks the MOD, never the TYPE — it is no protection against an assembly that is PRESENT but STALE.**
(2026-09-21)

- New C# that nobody rebuilt leaves its types out of the deployed DLL. Every `Class=` reference still guards correctly on the
  mod, and the mod is active.
- The guard passes, the type is not there, and the def that carries it is discarded with no message.
- Check that the type is IN the bytes of the deployed DLL. An active owning mod does not prove it.

A game_lock.py claim made in one Bash call is held by that call's process tree, so a detached waitalive job is refused by your own lock when it stops or restarts the game. Wrap the job: `waitalive.py run -- game_lock.py run <Game> --for ... -- CMD`. The exiting game holds BridgeTools DLLs for a few seconds (cp: Invalid argument), so retry the copy.

## 7b. 🔴 Is this artifact CURRENT? Never answer from a timestamp

Half the deploy questions in this project are one question: *does this derived thing still describe what the game loads?* A
**derived** thing is made from the mod set, for example a def dump. Seats answered that question from **age**, and the answer
was wrong four separate times in one day. The rule:

> **Trust a fingerprint of the load-set. Never a clock, on any layer:
> folder mtime, file mtime, or the artifact's own captured timestamp.**

The **load-set** is the list of mods that the game loads. Its **fingerprint** is a hash of that list. `refresh.py` prints one
that
also holds the load order and leaves out a listed mod that is not installed. The fingerprint that a def dump's database
stores
does not hold the order; a second one does.

Somebody believed each of these readings and acted on it, and each was false:

| the reading | why it lied |
|---|---|
| **A folder's mtime** | `DefDump/defs/` read `Aug 14` while every file inside was written `Aug 15`. A dump that **overwrites a fixed set of filenames** creates and deletes nothing, so the directory mtime never moves. The same is true of any tool that rewrites the same names. |
| **The artifact's own `capturedUtc`** | Fresh in TIME is not fresh in SET. A dump captured 08:10 missed a mod that was deprecated at 11:58. **Direction matters**: that dump is a *superset*. It describes everything live correctly. But it still carries defs from a mod that no longer loads, so an xpath onto *those* validates **clean** and matches **nothing** in game. |
| **A bare `<li>` count in `ModsConfig.xml`** | It read 580 against a true 575. The file holds a second list, `knownExpansions`, which repeats the DLC ids. **Scope the count inside `<activeMods>`.** |
| **`Version.txt`** | It read `rev590` while every file that the engine wrote read `rev591`. **The build stamp comes from the RUNNING game**, not from the file that appears to name it. (BUILD, 2026-08-15) |
| **A flat `DefDump/manifest.json` reader** | The dump layout moved to `captures/`, so the flat path is gone and the reader finds nothing. It then falls back to `Version.txt` with no message, and repeats the rev590/591 lie of the row above. `sync_mod_state.py` nearly stamped `rev590` over `rev591` saves before this was caught (fixed `801bd127`; the other readers were swept as `FLAT_MANIFEST_READER_SWEEP_1`). |
| **`refresh.py` calling `defs.sqlite` "current"** | `DumpDB.stale` once checked only the mod-set **fingerprint**. It did not check that the capture it names still **exists on disk**. Retention had already PRUNED the source capture (built 08-23) while a newer one existed (08-29). The fingerprint still matched, so the verdict read current (BENCH 2026-08-29). `DumpDB.stale` now reads STALE when the newest capture is not the named one, also when the named one is gone. Rebuild whenever the provenance names a missing capture: a matching fingerprint does not prove that the file behind it survives. |
| **A generator's own "regenerating is a no-op" header comment** | The comment can drift from a renamed or moved target and never say so. `gen_pawnkind_roster.py`'s own claim was stale: it emitted pre-rename defNames across 49 `PawnKindDef`s. A routine run, as the file itself instructed, would have reverted a whole naming migration with no message. **Verify a generator's no-op claim with `git diff --stat` against committed output, never the exit code** (2026-09-18). |

✅ **What was right the whole time: `refresh.py`'s `STALE` verdict.** That verdict compared the load-set fingerprint, not
the clock. The verdict named the one real mod while two seats escalated the wrong thing. **Believe it over your own timestamp
arithmetic.** The table shows one way that a `current` verdict of `refresh.py` failed.

- While a dump is frozen, `refresh.py` prints `FROZEN` for the dump row. That word says nothing about the live mod set.
- The `defs.sqlite` row compares the database with the newest capture, not with `ModsConfig.xml`.
- For a `--live` run, `validate_patch.py` warns when the dump's mod count differs from the count of `activeMods`. Equal
  counts
  do not prove equal sets.

⬜ **Coverage is a third axis, after time and set.** Coverage is which def types the dump holds with rows in them.

- 79 of 529 def-type files in the 2026-08-15 dump are **empty** (`AbilityDef` among them). For those types, "absent from the
  dump" says nothing at all about the game. Which types are empty changes with each dump, so read the dump that you use.
- A `--defs` check against an empty type is **UNMEASURED, not passed**. Give it its own exit code and its own word. If you do
  not, it becomes a green tick with no message.

📌 Where to read the dump facts:

- `DUMP_ROOT` in `src/RimMandrake/Utils/game_paths.py` is the `DefDump` folder. `DEF_DUMP` there is its newest capture. The
  freshness verdict is `refresh.py`'s.
- The known holes are in `observed/LIVE.md`. Its list of empty types is of the 2026-08-15 dump. Read it for the kinds of
  blind spot, not for a count.
- **Do not re-derive those facts**, and do not copy the numbers into another doc. Copied numbers rot there.

More traps for this section: [references/traps.md](references/traps.md) § 7b. 🔴 Is this artifact CURRENT? Never answer from a timestamp.
## 8. After deploying

- **Restart RimWorld.** The game parses defs once, at startup. A reloaded save does not pick up new XML.
  - A brand-new def is safe for an existing save. A change to a def that a save already references is not safe, and neither
    is
    its removal.
- **Enable compatibility-patch mods LAST in load order.** Patches apply in load order. A fix-up mod that loads before the mod
  it fixes patches a def that has not been redefined yet. Then the redefinition wins. A fix-up mod that loads too early is the most common reason why a
  correct patch appears to do nothing.
- **One mod at a time, verified before the next, unless the load is shared on purpose.**
  `skills/rimworld-load-round/SKILL.md` §3 says which changes can share a
  load. A new assembly or a mod that patches broadly goes alone, except as the owner's
  three-assembly waiver there says.
- Test on a dev-mode throwaway world. Read `Player.log` for the patch's own name before you trust the patch in the campaign
  save.
- 🔴 **"Deployed and VERIFIED" is true only until the next writer.** Every clone deploys to the same Mods folder. A
  subagent's verified UtinniPatches deploy was overwritten within minutes by another clone that deployed from an older sha.
  - Before you call a fix live, run the deploy dry run again from a clone AT the fix sha.
  - A clean plan (no `~`, `+`, `-` or `H` lines for your files) is the proof. The earlier report is not.

More traps for this section: [references/traps.md](references/traps.md) § 8. After deploying.

## 9. Validation plan — what you owe whoever holds the game

**A deploy ends with a validation plan, not with `--apply`.** You are almost never the one who will see the change work. A
load
of the full list costs many minutes (readings run from ~15 to **23–30 minutes**). One process drives a game at a time. So
whoever holds the game needs your prediction, not a nudge to "have a look at the Jawa stuff".

### The six fields

**1. The observable** — what a player SEES when it works. 🔴 Write a positive observation, never "no error". An absence is the
cheapest thing in the world to produce by accident.

**2. The route** — the exact call, defName or click path that produces the observable.

**3. The prediction** — a number or a specific string. Write it BEFORE the look.

**4. The threshold** — what CLOSES the item, and which details are explicitly out of scope. Without a threshold, people
inspect
an item forever. Ask for one observation, not a battery.

**5. Batch or solo** — most checks ride together. **A new assembly goes solo.** If that load comes up wrong, nobody can tell
whether the cause was the DLL or the three def changes beside it.

**6. What a FALSE PASS looks like** — the way that this particular check lies.

```
PROVE    <exact call / defName / click path>
EXPECT   <number or string, written before the look>
LIES     <how this check produces a false pass>
```

The plan is those three lines: the call, the expected reading, and how a pass can be false. 🔴 And first ask whether it needs
the game at all. The default is source. The rule and the catalogue of false passes are in
`skills/rimworld-modding/references/validation-plan.md`.

### The four ways a DEPLOY produces a false pass

1. **A successful write says nothing about the running game.** RimWorld parses defs and loads assemblies **once, at
startup**.
   - When `--apply` reports every file copied and verified, the report is about the filesystem. The running process read its
     copy minutes or hours ago.
   - ⇒ **LIES** must name what the game last loaded and when, not what the plan printed.
2. **An assembly the game holds cannot be overwritten — and the failure is easy to file and forget.** Windows refuses with
   `WinError 1224` (§7), so the copy does not silently succeed. But the game folder now carries a **different build** from
   the repo.
   - The plan compares bytes. So a new `--mod <Mod>` dry run still shows the `~` line of the DLL. A DLL with no line at all
     (no `~`, `+` or `H`) has the same bytes on both sides.
   - The line does not say how old the game copy is. To compare the two files with no plan, md5 both copies:
   ```bash
   md5sum src/<tier>/<Mod>/Assemblies/<Name>.dll "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/<Mod>/Assemblies/<Name>.dll"
   ```
   - That path is ArchBig's. For ArchSmall, use its own `Mods` (§1).
3. **An unscoped `--apply` deployed more than you think.** An unscoped run takes every mod where your clone
   differs from the game, except the folded biome members (§2). The run ships a subagent's half-finished work, and it puts an
   old file over another clone's newer
   deploy. Any breakage in that load is then blamed
   on your change.
   - ⇒ **Scope every deploy: `--mod <ModName>`.** Say in the plan which mods moved.
4. **"Deployed" and "live" are different words.** A folder under `Mods/` changes nothing until it is **enabled in the load
   order**. A compatibility patch must be enabled LAST (§8).
   - The plan warns when a mod is absent from `ModsConfig.xml`. If nobody reads the plan, the mod is on disk and inert.

### Worked example

A Harmony patch shipped as a new DLL for `Jawa_Patches` (an old mod name), deployed in the shutdown window:

```
PROVE    Spawn Jawa + MeleeWeapon_Vibroblade, spawn a muffalo, draft and attack; watch the combat log
EXPECT   A Jawa with a vibroblade attacks twice in the time a vanilla knife pawn attacks once · Cooldown 1.4s (was 2.6s); Player.log prints "[Jawa_Patches] 3 patches applied"
LIES     Game copy may be the PREVIOUS build if RimWorld was running at deploy (WinError 1224); md5 both DLLs before the load. Absent Harmony line = patch never applied, not "nothing to report".
```

⚠️ **Write it in the same commit as the deploy.** If you do not, whoever holds the game invents a check. That check does not
carry your prediction, and the prediction is the field that turns a look into evidence.

## The deployed companion DLL runs behind source, and a missing tool is ambiguous

The **companion** is the JawaBench assembly that adds bridge tools (`rimbridge-companion` skill). A companion assembly
deploys
only in a game-down window. So the game copy falls behind the repo for as long as the game stays up. One measurement read
**166
tool names deployed against 238 built** — 670 KB of IL, everything written that day.

⇒ **A tool missing from `--list-tools` proves nothing on its own.**

- Three causes look the same. The tool is not deployed, the tool is gated out of the build, or the tool does not exist.
- To tell the first cause apart, run `tool_surface()` of `src/RimMandrake/bridgetools/build.py` over the bytes of both DLLs.
  One is the built DLL, and one is in the `BridgeTools` folder of the game's install.
- To tell the other two apart, read `tool_names_from_source` of `src/RimMandrake/bridgetools/tool_metadata.py`. A tool in the
  source and in neither DLL is gated out of the build, or nobody has built its DLL since.
- `tool_surface()` reads the exact set of `[Tool]` names from the metadata of the DLL. The function is no longer a byte scan.
  A name in
  one DLL and not in the other is a real difference. The read compares names only: a tool that got worse shows no difference.
- A `jawa/` literal in the PROSE of a tool description no longer counts as a tool name. So a name in the "THIS DEPLOY WOULD
  REMOVE TOOLS" list of `build.py` is a real difference. Its usual cause is a missing `--gm` flag.
- If a doubt is left, read the file size and the build commit that is stamped in the assembly.

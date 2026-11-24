---
name: rimworld-start-prep
description: Getting the mod list and load order into the state you actually intend BEFORE RimWorld launches — the three uncoordinated writers (RimWorld, RimSort, Steam) that never tell each other. Covers why RimSort needs Refresh to see the disk and Save to write it (closing the window writes nothing), why RimWorld does NOT rewrite ModsConfig.xml on exit, why a Steam subscribe or unsubscribe changes disk folders but not the mod list, why Steam stalls or defers while the game is running, why "load at end" fails once every mod claims it and a patch belongs just after the mod it patches, why RimSort's "all clear" still needs a manual ordering pass, and the safe ordering that avoids all of it. Use this whenever mods are being added, removed, subscribed, unsubscribed, reordered or re-sorted, before any load, when a change "didn't take", when a mod is listed but missing or present but inactive, when a patch appears not to apply, or when anyone is about to reason about load order, User Rules or ModsConfig.xml at all.
---

# Preparing for a RimWorld start

Plan 15 to 30 minutes for a cold load of the owner's full list (the top of `skills/rimworld-load-round/SKILL.md`). A
launch with the wrong mod list is the most expensive way to spend a cold load. The wrong list is a list that is not
the list you thought you had. This skill covers the work *before* the launch. The skill covers only the *list* and the
*order* of the mods.

- **How to spend the load once it is running**: `skills/rimworld-load-round/SKILL.md`. That skill covers batches,
  decision strings and the log harvest. That skill starts where this skill ends.
- **How to get your own files into the game's Mods folder**: `skills/rimworld-deploy/SKILL.md`.
- The paths in this skill are the paths of ArchBig, the owner's game. ArchSmall has its own `ModsConfig.xml`, `Mods` and
  Saves (`skills/rimworld-load-round/SKILL.md` §0).
- Dates, measurements and corrected claims: [references/history.md](references/history.md).

---

## 1. The mental model: three writers, two truths, no conversation

Almost every "the change didn't take" in this project has one shape. Someone assumes that one of three programs did a
thing that the program does not do. The three programs do not coordinate, and they do not notify each other. None of
them is wrong. Each program owns a different thing.

There are **two** pieces of state. Each one answers a different question:

| | what it is | the question it answers |
|---|---|---|
| **The list** | `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` | *which* mods, in *what order* |
| **The content** | `…\steamapps\workshop\content\294100\<id>\` and `…\common\RimWorld\Mods\<name>\` | what is actually **on disk** to load |

There are **three** programs that write this state. Each program writes only part of it:

| writer | writes the list? | writes the content? | when |
|---|---|---|---|
| **RimWorld** | on an **in-game** change of the list, and in a few start cases (§3) | no, but RimWorld holds files **open** while it runs | never on exit (§3) |
| **RimSort** | on **Save**, and on a few other owner actions (§2) | not through Sort or Save; its Troubleshooting tab can delete folders (§2) | never on close (§2) |
| **Steam** | 🔴 **never** | yes: Steam downloads and deletes folders | on a subscribe or unsubscribe, but deferred while the game runs (§4) |

Our own tools and other windows write the list also (§3).

**The trap always has the same shape: someone credits a writer of one column with the other column.**

- When Steam removes a mod, the mod stays in the list.
- When RimWorld exits, RimWorld does not save your new order.
- When RimSort shows a tidy order, the order is not yet on disk.

---

## 2. RimSort: **Refresh** reads, **Save** writes, and closing does neither

RimSort keeps its own view of the list in memory. The view is not the file. The view and the file drift apart in both
directions.

**→ Refresh (the label can read Reload) pulls disk into RimSort.**

- Click Refresh after *anything* external changed. Examples: a Steam subscribe or unsubscribe, a deploy, an edit of
  `ModsConfig.xml` by another window, or a write by RimWorld after an in-game change.
- Without a Refresh you look at an old picture.

**→ Save pushes RimSort into the file.** Refresh, Sort, a drag and a close never write the list.

- Three other actions write `ModsConfig.xml`: the **Save and Run** button of the prompt below; an import in the
  Troubleshooting tab; and the clear-mods action of that tab.
- 🔴 The clear-mods action **deletes everything in the game's `Mods` folder** and resets the list to Core only. The
  action leaves `ModsConfig.xml.backup` beside the list.
- The same tab can delete the game config files, `ModsConfig.xml` included.
- RimSort creates the file when the file is missing.

🔴 **Sorting is not saving, and closing the window is not saving.**

- A click on **Sort** changes the order of the *view*. A drag of a mod changes the order of the *view*.
- If you close RimSort without a click on **Save**, none of the changes happened. The same is true if you leave RimSort
  open and launch the game some other way.
- The loss is silent. RimSort shows no prompt and no "unsaved changes" warning when it closes, and no log shows the
  loss.
- RimSort asks about unsaved changes in one case only: you launch the game with RimSort's own Run button. Then
  **Save and Run** writes the file, and **Run Anyway** does not write it.

⚠️ **RimSort's filesystem watchdog is ON** (`watchdog_toggle: true`), so the view *sometimes* updates itself.

- The watchdog watches the mod folders and the `.acf` files of Steam. The watchdog does not watch `ModsConfig.xml`.
- A view that is only sometimes fresh teaches you to trust it. **Click Refresh anyway.** A Refresh is free.

⛔ **"Close RimSort first" is never a precondition for anything.**

- RimSort locks no list file, and RimSort writes nothing to the list until the owner acts. So you can edit
  `ModsConfig.xml` safely while RimSort is open.
- The small hazard runs the *other* way. After your edit, the view in RimSort is stale. A later Save would write the old
  list over your edit.
- The whole mitigation is one sentence to the owner: *"RimSort is open, hit Refresh."*

### Verifying RimSort is pointed at the right folders

If a mod never appears in RimSort, the cause is usually a scan path and not the mod. Read the paths from
`C:\Users\Mandrake\AppData\Local\RimSort\settings.json`, under `instances`, at the name in `current_instance`:

```bash
python3 -c "
import json; d=json.load(open('/mnt/c/Users/Mandrake/AppData/Local/RimSort/settings.json'))
c=d['instances'][d['current_instance']]
[print(f'{k:16} = {c.get(k)}') for k in ('game_folder','config_folder','local_folder','workshop_folder')]"
```

- `local_folder` must be `<RimWorld>\Mods`. `workshop_folder` must be `steamapps\workshop\content\294100`.
- **These two have been swapped here before.** The symptom is that hand-authored mods are invisible, even when their
  `About.xml` is correct.
- Verify that RimSort scans the folder that you write to, before you debug the mod.

### Load-order rules: User Rules, and why `loadBottom` is not `loadAfter`

**Local rules go in User Rules: `C:\Users\Mandrake\AppData\Local\RimSort\dbs\userRules.json`.** User Rules is the
personal layer, and it is always writable.

- A User Rule is keyed by `packageId`. A rename of the `packageId` orphans the rule (§4a).

⚠️ **Do not put local rules in Community Rules.**

- If the source of that database is not configured, RimSort discards the save and shows **no error** on the screen. The
  rule appears to save, and the rule is gone when you open the editor again. The only trace is a warning in
  `C:\Users\Mandrake\AppData\Local\RimSort\Logs\RimSort.log`.
- If the source is a git repository, RimSort refreshes it at startup, and a local change does not last. The source here
  is a git repository now.

**A patch mod belongs immediately after the mod it patches.** The defs of the target must already be loaded when your
patch runs.

- Express the position as `loadAfter` with the packageId of the target.
- **"Just after the thing it modifies" is the correct placement, and it is a *relative* claim.** After the target is
  what counts; a Sort does not put the two side by side. An absolute claim such as "last" fails (next section).

🔴 **`loadBottom` and `loadAfter` are two different mechanisms, and the one you want is `loadAfter`.** These facts come
from RimSort's own code, v1.13.1, the version installed here:

- `loadAfter` compiles to a real edge in `deps_graph`. `loadBefore` compiles to the same edge, read from the other side.
- `loadBottom` compiles to no edge. `loadBottom` compiles only to membership in `tier_three_mods`
  (`app/models/metadata/metadata_structure.py`).
- The sort splits the active list into **four tiers, sorts each tier independently, and concatenates the tiers**
  (`app/controllers/sort_controller.py`). `loadBottom` mods are in the last tier. `loadTop` mods are in the second tier.
- ⚠️ **The tiers spread.** Each mod that loads after a bottom mod goes to the bottom tier also. Each mod that a top mod
  loads after goes up with it. Both rules follow the whole chain.
- Each tier drops the edges that point outside the tier: `full_graph.get(mod_id, set()) & tier_mods` in
  `app/sort/dependencies.py`. Because the tiers spread first, no edge between two active mods is violated in the result.

The rules give these results:

| rules on mod X | result |
|---|---|
| **`loadBottom` + `loadAfter Y`** (Y not at the bottom) | X lands after Y. The `loadBottom` did not defeat the `loadAfter`. The `loadAfter` was **redundant**. |
| **`loadBottom` + `loadBefore Y`** | X lands before Y. Y goes to the bottom with X, although nobody asked for that. |
| **`loadTop` + `loadAfter Y`** | X lands after Y. Y goes to the top with X. |
| `loadBottom` on X and on its target Y, no edge | The tie-break decides (next section). X can land above Y. |

Three things do remove a `loadAfter` edge:

- The target is not installed or not active. RimSort drops the edge and says nothing.
- A chain goes through an inactive mod. If A loads after B, B loads after C, and B is inactive, nothing orders A and C.
- The edges form a circle. RimSort shows the dialog "Unable to Sort" and abandons the sort.

**So: to place a mod after its target, write `loadAfter` and leave `loadBottom` off.** `loadBottom` cannot express
"after Y" at all — it only says "last". The next section says why "last" is worthless.

### 🔴 "Load at end" does not scale, because everyone claims it

**Far too many mods declare that they load last for "last" to mean anything.** Patch mods, compatibility shims,
framework add-ons and our own mods all claim the bottom of the list. From inside any one of them, the bottom looks
safe.

**A constraint asserted by everyone is a constraint satisfied by no one.**

- When a dozen mods ask for the end, RimSort cannot honour them all, so it must break the tie.
- `sorting_algorithm` here is **Topological**. Inside a tier, the mods with no unmet edge come first. Inside each such
  level, RimSort sorts by the **name of the mod**, alphabetically. Your intent is not an input.
- The result is stable enough to look deliberate, and arbitrary enough to be wrong.

**So your patch can land at the bottom, as you asked, and still be above the mod it patches.** That mod also asked for
the bottom and won the tie. RimSort obeyed the rule and missed the intent. RimSort does not show this failure: it
shows a sorted list with a green light.

**`loadAfter` does not have this problem.**

- `loadAfter` names a specific mod. So `loadAfter` constrains a *pair*, and it does not compete for an absolute
  position.
- Ten mods can each load after their own target with no contention. `loadAfter` promises after, not next to.
- Reserve `loadBottom` for the genuine case: a mod that must observe the fully assembled game, like a def dumper. Then
  expect to share the bottom with other mods, and expect to order that group by hand.

### RimSort's "all clear" is a starting point, not the final order

⚠️ **Expect to correct the order by hand after the owner reports "all clear" from RimSort, and budget time for that.**

- A clean sort means that *no rule was violated and no declared dependency is missing*.
- A clean sort does not mean that the order is correct for your test. RimSort knows only the constraints that someone
  wrote down.
- Two gaps stay: the "load at end" collisions, and each `modDependencies` entry, which carries no order (end of this
  section).

Treat a green RimSort as **"nothing is provably broken"**. Then do the pass that RimSort cannot do for you:

- For each mod under test, find the mod that it patches. Confirm that the mod under test sits **after** its target. Read
  the order out of `ModsConfig.xml`, not out of the RimSort panel.
- Correct a wrong place by hand. Then **encode the fix as a `loadAfter` User Rule**, so the next Sort keeps it. A
  hand-drag with no rule lasts only until someone clicks Sort.
- **Save**, then verify again from the file.

Do this pass before the launch. If you find a mis-ordered patch *after* a load, you pay for the whole load again.

⚠️ **`modDependencies` in `About.xml` does NOT imply load order.** One RimSort setting would make it imply order
(`use_moddependencies_as_loadTheseBefore`). That setting is **off** here.

- A mod can declare a dependency, load *before* it, and die with `ReflectionTypeLoadException` /
  `Could not resolve type with token`.
- When a dependency must load first, say so explicitly in **both** `userRules.json` and the resulting `ModsConfig.xml`
  order.

---

## 3. RimWorld does **not** rewrite `ModsConfig.xml` on exit

**Closing RimWorld writes nothing to the mod list.** A session with no in-game change of the list ends without a write.

RimWorld writes `ModsConfig.xml` in these cases only (game source 1.6: `ModsConfig`, `Page_ModsConfig`,
`Dialog_ModMismatch`, `PlayDataLoader`):

- **In-game**, the mod menu: you save a changed list.
- **In-game**, the mod-mismatch dialog: you choose the mods of the save.
- **At a start**, one of these four: the file is missing; the file is from another minor version of the game; the list
  holds a folder name in place of a packageId; the game sees a DLC for the first time.
- **After a failed load**: the recovery reset writes Core and the DLCs only (`skills/rimworld-load-round/SKILL.md` §0).

Three consequences:

- **No close of the game overwrites a mid-session edit of `ModsConfig.xml`.** There is no "shutdown window" to race. The
  running game does not see your edit. The next start reads it.
- **If the file moved, something wrote it.** The writers are RimWorld in the cases above, RimSort (§2), another
  window, or one of our tools. Examples of our tools: `modset_builder.py`, `modlist_swap.py`, `modcheck run <Mod>`,
  `loadsweep/`, a test run, and `sync_mod_state.py --apply` (§5a, the `<version>` only). Who drives the game now:
  `python3 src/RimMandrake/rimflow/game_lock.py query ArchBig`.
- 🔴 **Do not block on RimSort, and never ask whether it is open. Owner's ruling, 2026-08-15:** *"You NEVER have to ask
  if RimSort is open. It does not autosave, and I will never save without asking. Nobody blocks on RimSort or game close
  for config files of any kind."*
  - RimSort writes only on an owner action (§2), and the owner announces each Save. So two writers do not collide
    unasked.
  - Write the file. After that, the view in RimSort is stale. Say *"RimSort is open, hit Refresh"* and move on.
  - `modset_builder.py` still refuses a write while its game runs (`skills/rimworld-load-round/SKILL.md` §4). Then use
    ArchSmall, or stop that game if you hold it.

**While the game is up, disk state is not authoritative about the running game.** The running list is in memory, and the
game holds the folders open.

- Before you make a claim about mod state, find out if the game runs:
  `python3 src/RimMandrake/Utils/game_instance.py status`.
- The cheap tell is the mtime of `Player.log` against the mtime of `ModsConfig.xml`. Report what the timestamps imply.
  Do not assert a state.

---

## 4. Steam changes the **content**, never the **list** — and lags while the game runs

A subscribe and an unsubscribe are Steam operations on folders. Steam does not know that `ModsConfig.xml` exists.

| you do | disk | the list | net effect at next launch |
|---|---|---|---|
| **Subscribe** | folder appears under `294100\<id>\` | **unchanged** | the mod is present but **inactive**: it does not load until you add it to the list (in RimSort, add it and **Save**) |
| **Unsubscribe** | folder is deleted | **unchanged** | the entry is **listed but missing**: the mod does not load, and RimWorld drops the entry in memory |

**"Listed but missing" is the more dangerous of the two.**

- RimWorld names a dropped entry only in its verbose log. So nothing tells you. The entry stays in the file until
  something writes the list again.
- A tool that compares *listed* against *exists* disagrees with a tool that trusts the list. Both look authoritative.
- Reconcile after every unsubscribe: Refresh in RimSort, remove the dead entries, Save.

🔴 **Do subscription changes with the game DOWN.** While RimWorld runs:

- **Steam will not delete a folder the game holds open.** So a folder that persists during a live session proves nothing
  about the subscription.
- **Downloads stall, arrive slowly, or do not apply until the game exits.** Expect a delay at best, and a wait for the
  exit at worst.
- So a mod that you subscribe to mid-session can be **absent from disk** when you look. A mod that you unsubscribe from
  mid-session is **still on disk**. Neither is a bug. Do not debug either one. The game holds the files.

⚠️ **A subscription to a Workshop item that Steam has since removed can never download.**

- The symptom is a stable `Created WorkshopItem for <id> but there is no folder for it` at every launch.
- The problem is in the *account*, not in the game. An unsubscribe is the only fix. A verify of the local files does not
  help.

🔴 **Steam's own "Game already running" lock can get stuck after RimWorld dies silently** (no clean process exit).

- The symptom: `tasklist.exe` shows no `RimWorldWin64` process, and Steam still refuses to launch the game.
- The fix: shut the STEAM CLIENT down fully and start it again (`steam.exe -shutdown`, wait, start `steam.exe`). A
  second launch of the game alone does nothing.

### Comparing the list against disk: three traps in a list census

Traps 1 and 2 bite any script that walks the mod roots, reads each `About/About.xml`, and compares the ids with
`<activeMods>`. Either trap alone turns a clean set into false missing mods. Trap 3 bites any count of the list.

1. 🔴 **`<packageId>` is NOT unique inside an `About.xml`.** A naive `re.search(r'<packageId>(.*?)</packageId>')` returns
   the **first** match. In most modern mods that is the id of a **dependency** inside `<modDependencies>`, not the mod's
   own id.
   - Alpha Biomes is the clean example. Its `...\workshop\content\294100\1841354677\About\About.xml` lists
     `brrainz.harmony`, then `OskarPotocki.VanillaFactionsExpanded.Core`, and only *then* its own `sarg.alphabiomes`.
     So a regex scan reports Alpha Biomes absent while it is on disk.
   - **Fix: take the direct child only**: `ET.parse(ax).getroot().find('packageId')` on `<ModMetaData>`.

2. 🔴 **Core and the DLCs are not under `Mods\`.** Core and the DLCs are in the data directory of the game:
   `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\{Core,Royalty,Ideology,Biotech,Anomaly,Odyssey}`.
   - A census without that root reports **six** false missing hits: `ludeon.rimworld` and the five `ludeon.rimworld.*`
     expansions, near the top of `<activeMods>`.
   - A census must walk **three** roots: `...\steamapps\workshop\content\294100\`, `...\common\RimWorld\Mods\` (local
     mods), and `...\common\RimWorld\Data\`.
   - Related: `<knownExpansions>` holds the **five DLCs only**. Core is not in that element. The five DLC ids are
     the source of the recurring five-mod gap in counts (trap 3).

3. 🔴 **Never count `<li>` without scoping it to `<activeMods>`.** The five ids in `<knownExpansions>` are ALSO in
   `<activeMods>`. So a count of every `<li>` in the file is too high by exactly the DLC count.
   - `grep -c` counts matching LINES. The line layout depends on the program that wrote the file last. So `grep -c` is
     also wrong, in a different way on each layout: one layout gave **6** for 575 mods.
   - **Parse it and read `activeMods`:**

   ```python
   len(ET.parse(cfg).getroot().find("activeMods"))
   ```

---

## 4a. A packageId rename leaves every SAVED mod list a landmine

A rename of a packageId also invalidates every saved copy of the list. These files hold bare ids:

- `ModsConfig.FULL.LATEST.xml` and `ModsConfig.MINIMAL.xml` (`infrastructure/state/modlists/`);
- RimSort's own `dbs/userRules.json` and `dbs/ignore.json`.

🔴 **RimWorld drops an unrecognised id at startup silently, and the `activeMods` COUNT in the file never changes.**

- The content of the dropped mod does not load. There is no error and no red text.
- A count of `activeMods` sees no change.
- `modlist_swap.py --status` compares the live ids with the saved ids. If nobody updated any list, it reads FULL or
  MINIMAL. If only one side was updated, it reads UNRECOGNISED. UNRECOGNISED is the exact same word that the tool
  prints when the owner adds a genuinely new mod. So neither reading is evidence about a rename.
- The old id in `userRules.json` matches nothing. The next Sort loses that rule.

**After any rename, resolve every id in every saved list against every installed `About/About.xml` packageId.** Do not
check only the live file. Evidence: `RENAME_VERIFY_WINDOW_1`.

### A list-merge dedupe must keep the DESTINATION's own slot for a shared id

Some tools merge two mod lists and drop duplicate ids. Such a tool must keep the entry of the **destination** list, not
simply the first occurrence that it reads.

- Position in a merged list is load order, not bookkeeping. A naive set-union silently reorders the list.
- A first-occurrence dedupe once moved the load-last patch mods to mid-order and aborted the whole load
  (`MOD_CONSOLIDATION_SPRINT_1`).

---

## 5. The safe ordering

Follow this order. Each step depends on a result of the previous step that is already on disk. Steps 3 to 6 use RimSort.
An agent without RimSort edits `ModsConfig.xml` and `userRules.json` directly, and then says *"RimSort is open, hit
Refresh."* (§3).

1. **Game DOWN, if a Steam change is due.** Measure it; do not assume it: `python3
   src/RimMandrake/Utils/game_instance.py status`. Steam changes are unreliable while the game runs (§4). An edit of
   the list never waits for the game to close (§3).
2. **Do the Steam subscribes and unsubscribes.** Let them finish. Watch for the folders to appear or vanish under
   `294100\`.
3. **Refresh in RimSort.** Its view is stale now, because you changed the disk.
4. **Reconcile the list against disk.** Add each newly subscribed mod. Remove each entry whose folder is gone. This step
   turns a Steam change into a *list* change. Nothing else does that for you.
5. **Set the order, and do not stop at "all clear".** Sort. Then do the manual pass. For every mod that you will test,
   confirm the order in the file.
   The mod must sit *after* the mod it patches. Correct what is wrong by hand. Then **encode each fix as a
   `loadAfter` User Rule**, so the next Sort does not undo the fix (§2).
6. 🔴 **Click Save.** Nothing that you did in RimSort before this point is on disk. Closing the window is not saving.
7. **Verify from the file, not the UI.** Count `activeMods`, and check that the mtime moved:

   ```bash
   MC="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml"
   python3 -c "import xml.etree.ElementTree as ET,sys;print(len(ET.parse(sys.argv[1]).getroot().find('activeMods')))" "$MC"
   stat -c %y "$MC"
   ```

   ⚠️ Count `activeMods` specifically (§4 trap 3). **Print the number; never quote a remembered one.**
8. 🔴 **Decide on the mod-state sync. The decision is the last thing before launch.** See §5a.
9. **Then, and only then, spend the load.** Go to `skills/rimworld-load-round/SKILL.md`.

**Announce the change if you are not the only window.** Another window or a test run can write the same file. A blind
write destroys a re-sort in progress. Look who drives the game: `python3 src/RimMandrake/rimflow/game_lock.py query
ArchBig`. If another window holds it, tell that window, or use ArchSmall. Do not wait. `modset_builder.py` needs the
hold. The `ModsConfig.xml` duties (snapshot, sweep, announce) are in `infrastructure/agents/CHARTER.md` §The expensive
list.

---

## 5a. The mod-state sync — decide it, log it, never hide an unexplained mismatch

Three records each keep their own copy of *"which mods, which build"*. Nothing keeps the three in step:

| file | what it records |
|---|---|
| `Config/ModsConfig.xml` `<version>` | the build the list was written for |
| `Config/LastPlayedVersion.txt` | the build the game last ran as |
| `Saves/*.rws` `<meta>` | `gameVersion` **and the full mod list** |

When a save disagrees with the live list, RimWorld raises the mod-mismatch dialog (the long "these were added /
removed" list). Sometimes **we** caused the difference on purpose: a deploy, a cut of content, an edit of the list.
Then the dialog is noise to the human, and worse than noise to a tool. Every check that joins a save with the live set
reports a difference that everyone already understands. That teaches everyone to skim past the real differences.

```bash
python3 skills/rimworld-start-prep/scripts/sync_mod_state.py            # plan
python3 skills/rimworld-start-prep/scripts/sync_mod_state.py --apply    # write
```

- Without a flag, the script only plans. There is no `--plan` flag.
- ⚠️ The script reads ArchBig's paths only. By default `--apply` writes **every** save in `Saves`, the canonical saves
  included. Name the saves with `--saves "<name>"`, or pass `--saves none` for the two Config files only.
  `infrastructure/agents/CHARTER.md` (savegame writes) binds a canonical save.
- The script backs each file up beside the original before it writes.
- The script refuses while any `RimWorldWin64.exe` runs, ArchSmall included. If `game_instance.py status` shows that
  ArchBig is down and only ArchSmall runs, use `--force-running`.

**Decide `--apply` yourself, and log it** (`design/RimMandrake/delegation_policy.md`;
`--why "delegated: technical"`). Two conditions apply:

- The list has stopped moving (§5 step 8).
- You can say why the N mods of the saves differ from the M mods of the live list. Whether the difference is
  understood is a judgement, and only an understood difference may be silenced.

⛔ **Never `--apply` to make an UNEXPLAINED mismatch go away.**

- The dialog is the only cheap warning that a save and the mod list have parted company. Silence the dialog when you
  already know why they differ. Investigate when you do not know.
- The sync repairs nothing. If a removed mod supplied defs that the save references, the save loader (Scribe) reports
  an error: `Could not load reference to <def>`. No list edit fixes that (`skills/rimworld-savegame`).

🔴 **The build stamp comes from what the GAME WROTE, not from `Version.txt`.**

- `Version.txt` ships with the install and does not track the runtime rev. `Version.txt` can read `1.6.4871 rev590`
  while every file that the engine writes reads `rev591`.
- The script reads the `gameVersion` of the newest DefDump manifest. The script uses `Version.txt` in two cases only.
  Either there is no manifest, or the game has not run since a patch and `Version.txt` is newer.
- The script **refuses** to write a lower rev over a higher rev in a save. Such a write makes the very mismatch that the
  script must remove.

---

## 6. Fast triage: "the change didn't take"

Work down this table before you form any hypothesis. The answer is nearly always in the first three rows.

| what you see | first thing to suspect |
|---|---|
| Mod is on disk but does not load | Someone subscribed and nobody added the mod to the list. Steam does not write the list (§4) |
| Mod was unsubscribed but is still listed / still in the folder | Nothing removes the entry but you. The game was probably up and held the folder (§4) |
| Load order is right in RimSort, wrong in game | Nobody clicked **Save** (§2) |
| Your reorder vanished | RimSort was closed without Save, **or** someone saved a stale view over your order (§2, §3) |
| Your `ModsConfig.xml` edit vanished | Not the exit of the game. Suspect a tool, another window, a stale RimSort Save, or a start case of RimWorld (§3) |
| The list holds Core only, or Core and the DLCs only | The recovery reset after a failed load (§3), or RimSort's clear-mods action (§2). Look for `ModsConfig.xml.backup` beside the list, and look whether the `Mods` folder is empty |
| A hand-authored mod never appears in RimSort at all | `local_folder` / `workshop_folder` are swapped in the settings (§2) |
| A rule saved and then was gone | The rule went into **Community Rules**, with no configured source or with a git source (§2) |
| A patch loads before the mod it patches | No `loadAfter` edge exists: both mods asked for the bottom and the tie-break went the wrong way; or `modDependencies` was trusted for order; or the rule names an id that is not active (§2, §4a) |
| RimSort said "all clear" and the test still behaved as if the patch never applied | A clean sort only proves that no *declared* rule was broken. Verify the order of the pair in `ModsConfig.xml` by hand (§2) |
| A hand-drag reverted after the next Sort | Nobody wrote it down as a User Rule (§2) |
| `no folder for it` every launch | Steam removed the Workshop item. Unsubscribe is the only fix (§4) |

---

## Keeping this skill honest

This project once believed two wrong claims on this subject: the rewrite on exit, and the lost `loadAfter` edge
([references/history.md](references/history.md)). **When a decision rests on a claim here and a cheap test exists,
test the claim.** An mtime comparison costs nothing, and it caught the first error.

If something surprises you, file a lesson. A fresh-context curation session moves the lesson into the file. The index of
the trap files is `skills/rimworld-modding/references/traps.md`. Write the symptom, the cause, the fix and
**"recurs when"**. The home is `skills/rimworld-modding/references/traps-mods-and-managers.md`:

```
python3 src/RimMandrake/Utils/lessons.py add "…" --home skills/rimworld-modding/references/traps-mods-and-managers.md
```

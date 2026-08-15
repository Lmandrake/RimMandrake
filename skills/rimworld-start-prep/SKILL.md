---
name: rimworld-start-prep
description: Getting the mod list and load order into the state you actually intend BEFORE RimWorld launches — the three uncoordinated writers (RimWorld, RimSort, Steam) that never tell each other. Covers why RimSort needs Refresh to see the disk and Save to write it (closing the window writes nothing), why RimWorld does NOT rewrite ModsConfig.xml on exit, why a Steam subscribe or unsubscribe changes disk folders but not the mod list, why Steam stalls or defers while the game is running, why "load at end" fails once every mod claims it and a patch belongs just after the mod it patches, why RimSort's "all clear" still needs a manual ordering pass, and the safe ordering that avoids all of it. Use this whenever mods are being added, removed, subscribed, unsubscribed, reordered or re-sorted, before any load, when a change "didn't take", when a mod is listed but missing or present but inactive, when a patch appears not to apply, or when anyone is about to reason about load order, User Rules or ModsConfig.xml at all.
---

# Preparing for a RimWorld start

A cold load costs **~23–30 minutes** and there is one game shared by five seats. The
single most expensive way to spend one is to launch with a mod list that is not the
list you thought you had. This skill is about the twenty minutes *before* the launch.

**For how to spend the load once it is running** — batching, decision strings, log
harvesting — that is `skills/rimworld-load-round/SKILL.md`, and it starts where this
one ends. **For getting your own authored files into the game's Mods folder**, that
is `skills/rimworld-deploy/SKILL.md`. This skill is only about the *list* and the
*order*.

---

## 1. The mental model: three writers, two truths, no conversation

Almost every "the change didn't take" in this project is one of three programs being
assumed to have done something it does not do. They are not coordinated, they do not
notify each other, and none of them is wrong — they simply own different things.

There are **two** pieces of state, and they answer different questions:

| | what it is | the question it answers |
|---|---|---|
| **The list** | `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` | *which* mods, in *what order* |
| **The content** | `…\steamapps\workshop\content\294100\<id>\` and `…\common\RimWorld\Mods\<name>\` | what is actually **on disk** to load |

And **three** writers, each touching only part of it:

| writer | writes the list? | writes the content? | when |
|---|---|---|---|
| **RimWorld** | only on an **in-game** mod-menu change | no — but holds files **open** while running | never on exit (§3) |
| **RimSort** | only when you click **Save** | no | never on close (§2) |
| **Steam** | 🔴 **never** | yes — downloads and deletes folders | on sub/unsub, but deferred while the game runs (§4) |

**The trap is always the same shape: a writer that owns one column being credited with
the other.** Steam removing a mod does not remove it from the list. RimWorld exiting
does not save your reorder. RimSort showing you a tidy order does not mean the order is
on disk. Hold this table in mind and the rest of this file is mostly detail.

---

## 2. RimSort: **Refresh** reads, **Save** writes, and closing does neither

RimSort keeps its own in-memory view of the list. That view is not the file, and the
two drift in both directions.

**→ Refresh (may be labelled Reload) pulls disk into RimSort.**
Click it after *anything* external changed: a Steam subscribe or unsubscribe, a deploy,
another seat editing `ModsConfig.xml`, or RimWorld itself writing the list after an
in-game change. Without it you are looking at a photograph.

**→ Save pushes RimSort into the file.** This is the only moment `ModsConfig.xml` is
written by RimSort.

🔴 **Sorting is not saving, and closing the window is not saving.** Clicking **Sort**
rearranges the *view*. Dragging mods rearranges the *view*. If you close RimSort — or
leave it open and launch the game — without clicking **Save**, none of it happened.
This is the single most common way an afternoon of load-order work evaporates, and it
does so silently: there is no prompt, no "unsaved changes" warning, nothing in a log.

⚠️ **RimSort's filesystem watchdog is ON** (`watchdog_toggle: true`), so the view
*sometimes* appears to update itself. That inconsistency is worse than it never
updating, because it teaches you to trust a view that is only usually fresh. **Click
Refresh anyway.** It is free.

⛔ **"Close RimSort first" is never a precondition for anything.** RimSort holds no
lock and writes nothing until Save, so editing `ModsConfig.xml` while it is open is
safe. The hazard runs the *other* way and is small: after your external edit, RimSort's
view is stale, so a later Save would write the old list back over you. The whole
mitigation is one sentence to the owner — *"RimSort is open, hit Refresh."*

### Verifying RimSort is pointed at the right folders

A mod that never appears is usually a scan-path problem, not a mod problem. These are
the values that must hold (read from `C:\Users\Mandrake\AppData\Local\RimSort\settings.json`,
under `instances` → the name in `current_instance`):

```bash
python3 -c "
import json; d=json.load(open('/mnt/c/Users/Mandrake/AppData/Local/RimSort/settings.json'))
c=d['instances'][d['current_instance']]
[print(f'{k:16} = {c.get(k)}') for k in ('game_folder','config_folder','local_folder','workshop_folder')]"
```

`local_folder` must be `<RimWorld>\Mods` and `workshop_folder` must be
`steamapps\workshop\content\294100`. **These two have been swapped here before**, and
the symptom is that hand-authored mods are invisible no matter how correct their
`About.xml` is. Verify the manager is looking where you are writing before debugging
the mod.

### Load-order rules: User Rules, and why `loadBottom` fights `loadAfter`

`C:\Users\Mandrake\AppData\Local\RimSort\dbs\userRules.json` is the personal,
always-writable rules layer, and it is where local rules belong.

⚠️ **Do not put local rules in Community Rules.** That database's source can be
unconfigured, and when it is, the save is discarded **with no error** — the rule
appears to save and is simply gone on reopen.

**A patch mod belongs immediately after the mod it patches.** That is the whole point
of a rule: your patch has to see the target's defs already loaded. Express it as
`loadAfter` naming the target's packageId. **"Just after the thing it modifies" is the
correct placement and it is a *relative* claim** — which is why the absolute one fails.

🔴 **`loadBottom: true` defeats `loadAfter`.** `loadBottom` sinks the mod to the very
end of the order, which is a *stronger* constraint than "after X" — so the `loadAfter`
list is satisfied trivially and exerts no placement force at all. A rule carrying both
does not place the mod after its target; it dumps it at the bottom and the `loadAfter`
entries become decoration. **Use one or the other**, and prefer `loadAfter`.

### 🔴 "Load at end" does not scale, because everyone claims it

This is the deeper reason to prefer `loadAfter`, and it is worth understanding rather
than memorising. **Far too many mods declare that they load last for "last" to mean
anything.** Every patch mod, every compatibility shim, every framework add-on, and
every one of our own Jawa mods reaches for the bottom of the list, because from inside
any one of them the bottom looks like the safe answer.

**A constraint asserted by everyone is a constraint satisfied by no one.** Once a
dozen mods all demand the end, the sorter cannot honour them all — it must break the
tie, and *how* it breaks it is not something you specified and not something you
control. `sorting_algorithm` here is **Topological**, so the tie-break falls out of
graph traversal order and incidental input ordering. The result is stable enough to
look deliberate and arbitrary enough to be wrong.

**So your patch can land at the bottom, exactly as requested, and still be above the
mod it patches** — because that mod also asked for the bottom and happened to win the
tie. The rule was obeyed; the intent was not. This failure is invisible in RimSort,
which will happily show you a sorted list with a green light on it.

**`loadAfter` does not have this problem.** It names a specific mod, so it constrains a
*pair* rather than competing for a scarce absolute position. Ten mods can each sit just
after their own target with no contention at all. Reserve `loadBottom` for the genuine
case — something that must observe the fully assembled game, like a def dumper — and
even then expect to share the bottom with others and to have to order that group by
hand.

### RimSort's "all clear" is a starting point, not the final order

⚠️ **Expect to tweak the order manually after the owner reports "all clear" from
RimSort, and budget for it.** A clean sort means *no rule was violated and no declared
dependency is missing*. It does not mean the order is correct for what you are about to
test — the sorter only knows the constraints someone bothered to write down, and the
gaps are exactly the "load at end" collisions above plus every `modDependencies` edge
that carries no ordering (see below).

Treat a green RimSort as **"nothing is provably broken"**, then do the pass it cannot
do for you:

- For each mod under test, find the mod it patches and confirm it sits **after** it —
  read the order out of `ModsConfig.xml`, not out of the RimSort panel.
- Drag what is wrong into place by hand, then **encode the fix as a `loadAfter` User
  Rule** so the next sort preserves it. A hand-drag that is not written down as a rule
  survives exactly until someone clicks Sort.
- **Save**, then re-verify from the file.

Doing this before the launch is what makes the test meaningful. Discovering a
mis-ordered patch *after* a load costs the whole ~23–30 minutes again.

⚠️ **`modDependencies` in `About.xml` does NOT imply load order**, and the setting that
would make it imply order (`use_moddependencies_as_loadTheseBefore`) is **off** here.
A mod can declare a dependency, load *before* it, and die with
`ReflectionTypeLoadException` / `Could not resolve type with token`. When a dependency
must load first, say so explicitly in **both** `userRules.json` and the resulting
`ModsConfig.xml` order.

---

## 3. RimWorld does **not** rewrite `ModsConfig.xml` on exit

This one was documented backwards in this project for a long time and cost real debug
cycles, so it is stated flatly: **closing RimWorld writes nothing to the mod list.**

RimWorld writes `ModsConfig.xml` when the list changes **in-game**, through the mod
menu. That is the only trigger. A session where you changed nothing in-game ends
without touching the file.

**Measured 2026-08-13**, which is why we now believe it: at game exit `Player.log`'s
last write was **10:04:55** while `ModsConfig.xml`'s mtime was **10:01** — *older than
the exit*. The same file then changed at **16:41:39 with no game running at all**.

Three consequences worth having:

- **A mid-session edit to `ModsConfig.xml` is not overwritten at close.** There is no
  "shutdown window" to race, and nothing to protect your edit from.
- **The only writers of that file are a seat, or the owner via RimSort.** If it moved,
  one of those did it.
- 🔴 **Do not block on RimSort, and never ask whether it is open. Owner's ruling,
  2026-08-15:** *"You NEVER have to ask if RimSort is open. It does not autosave, and I
  will never save without asking. Nobody blocks on RimSort or game close for config
  files of any kind."* RimSort writes only on a Save the owner will announce, so the
  concurrent-writer collision this section used to warn about cannot happen unasked.
  Write the file. After you do, its view is stale — say *"RimSort is open, hit
  Refresh"* and move on.

**While the game is up, disk state is not authoritative** — the list lives in memory
and the folders are held open. Establish whether the game is running before making any
claim about mod state. The cheap tell is `Player.log`'s mtime against
`ModsConfig.xml`'s; report what the timestamps imply rather than asserting a state.

---

## 4. Steam changes the **content**, never the **list** — and lags while the game runs

Subscribing and unsubscribing are Steam operations on folders. They do not know
`ModsConfig.xml` exists.

| you do | disk | the list | net effect at next launch |
|---|---|---|---|
| **Subscribe** | folder appears under `294100\<id>\` | **unchanged** | mod is present but **inactive** — it will not load until you add it in RimSort and **Save** |
| **Unsubscribe** | folder is deleted | **unchanged** | entry is **listed but missing** — RimWorld complains at launch and the mod obviously does not load |

**"Listed but missing" is the more dangerous of the two**, because tooling that compares
*listed* against *exists* will disagree with tooling that trusts the list, and both look
authoritative. Reconcile after every unsubscribe: Refresh in RimSort, remove the dead
entries, Save.

🔴 **Do subscription changes with the game DOWN.** While RimWorld is running:

- **Steam will not delete a folder the game holds open.** The folder persisting during
  a live session proves nothing about subscription state.
- **Downloads stall, arrive slowly, or do not apply until the game exits.** Expect the
  operation to be laggy at best and deferred entirely at worst.
- So a subscribe you make mid-session may simply **not be on disk** when you look, and
  an unsubscribe you make mid-session will **still be on disk**. Neither is a bug and
  neither is worth debugging — it is the game holding files.

⚠️ **A subscription to a Workshop item Steam has since removed can never download.** The
symptom is a stable `Created WorkshopItem for <id> but there is no folder for it` every
launch. It is an *account* state problem, not a game state problem — unsubscribe is the
only fix, and no amount of verifying local files will touch it.

### Comparing the list against disk: two traps that manufacture false "missing" hits

Both bite any script that walks the mod roots, reads each `About/About.xml` and
set-compares the ids against `<activeMods>`. Each one on its own turns a clean set into
dozens of phantom missing mods.

1. 🔴 **`<packageId>` is NOT unique inside an `About.xml`.** A naive
   `re.search(r'<packageId>(.*?)</packageId>')` returns the **first** match, which in
   most modern mods is a **dependency's** id inside `<modDependencies>`, not the mod's
   own. Alpha Biomes is the clean example: its
   `...\workshop\content\294100\1841354677\About\About.xml` lists `brrainz.harmony`,
   then `OskarPotocki.VanillaFactionsExpanded.Core`, and only *then* its own
   `sarg.alphabiomes` — so a regex scan reports Alpha Biomes absent while it sits
   plainly on disk.
   **Fix: take the direct child only** —
   `ET.parse(ax).getroot().find('packageId')` on `<ModMetaData>`. Correcting this alone
   took one census from dozens of "missing" mods down to one.

2. 🔴 **Core and the DLCs are not under `Mods\`.** They live in the game's data
   directory: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\{Core,Royalty,Ideology,Biotech,Anomaly,Odyssey}`.
   Omitting that root manufactures **six** false missing hits — `ludeon.rimworld` and
   the five `ludeon.rimworld.*` expansions, which sit at the very top of `<activeMods>`.
   A census must walk **three** roots: `...\steamapps\workshop\content\294100\`,
   `...\common\RimWorld\Mods\` (local mods), and `...\common\RimWorld\Data\`.
   Related: `<knownExpansions>` holds the **five DLCs only** — Core is not in it, which
   is the source of the recurring five-mod arithmetic gap noted in §5 step 7.

3. 🔴 **Never count `<li>` without scoping it to `<activeMods>`.** `<knownExpansions>`
   holds five ids that are ALSO in `<activeMods>`, so the file has 580 `<li>` elements
   for 575 active mods — an overcount of exactly the DLC count. And the file is only
   **12 lines**, so the two obvious greps are wrong in opposite directions: `grep -c`
   counts matching LINES and returns **6**; `grep -o '<li>' | wc -l` returns **580**.
   Measured 2026-08-15. **Parse it and read `activeMods`:**

   ```python
   len(ET.parse(cfg).getroot().find("activeMods"))
   ```

---

## 5. The safe ordering

Follow this and none of the above can bite. The ordering exists because each step
depends on the previous one having actually landed on disk.

1. **Game DOWN.** Confirm it, do not assume it — compare `Player.log`'s mtime to now.
   Every subsequent step is unreliable while it runs.
2. **Do the Steam subscribes and unsubscribes.** Let them finish; watch for the folders
   to actually appear or vanish under `294100\`.
3. **Refresh in RimSort.** Its view is stale by definition now — you just changed disk
   underneath it.
4. **Reconcile the list against disk.** Add newly subscribed mods; remove entries whose
   folders are gone. This is the step that converts a Steam change into a *list* change,
   and nothing else will do it for you.
5. **Set the order — and do not stop at "all clear".** Sort, then do the manual pass:
   for every mod you are about to test, confirm it sits *after* the mod it patches.
   Fix what is wrong by hand, then **encode each fix as a `loadAfter` User Rule** so the
   next Sort does not undo it. `loadAfter` names its target and always beats a crowd of
   mods all claiming the bottom (§2).
6. 🔴 **Click Save.** Nothing before this point is on disk. Closing the window is not
   saving.
7. **Verify from the file, not the UI** — count `activeMods`, check the mtime moved:

   ```bash
   MC="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml"
   python3 -c "import xml.etree.ElementTree as ET,sys;print(len(ET.parse(sys.argv[1]).getroot().find('activeMods')))" "$MC"
   stat -c %y "$MC"
   ```

   ⚠️ Count `activeMods` specifically. `grep -c "<li>"` over-counts by exactly the
   **5 `knownExpansions`**, and that five-mod gap has been mistaken for a real
   discrepancy before. **Print the number; never quote a remembered one** — the
   literals that used to sit here went 12 mods stale.
8. 🔴 **OFFER THE MOD-STATE SYNC — this is the last thing before launch.** See §5a.
9. **Then, and only then, spend the load** — hand off to
   `skills/rimworld-load-round/SKILL.md`.

---

## 5a. The mod-state sync — offer it, do not run it unasked

Three files each keep their own copy of *"which mods, which build"*, and nothing
keeps them in step:

| file | what it records |
|---|---|
| `Config/ModsConfig.xml` `<version>` | the build the list was written for |
| `Config/LastPlayedVersion.txt` | the build the game last ran as |
| `Saves/*.rws` `<meta>` | `gameVersion` **and the full mod list** |

When the saves disagree with the live list, RimWorld raises the mod-mismatch
dialog — the long "these were added / removed" wall. Whenever the divergence is
one **we** caused on purpose (a deploy, a descope, a list edit), that dialog is
noise to the human, and worse than noise to tooling: every check that joins a
save against the live set reports a difference that is expected and already
understood, which teaches everyone to skim past the real ones.

```bash
python3 skills/rimworld-start-prep/scripts/sync_mod_state.py            # plan
python3 skills/rimworld-start-prep/scripts/sync_mod_state.py --apply    # write
```

Dry-run by default — running it bare **is** the plan. There is no `--plan` flag.

**Ask the owner before running it with `--apply`.** It is a one-line question at
the point in §5 where the list has stopped moving: *"the saves record N mods and
the live list has M — sync them so the mismatch dialog stays quiet?"* It is their
call, because silencing that dialog is a judgement about whether the difference
is understood.

⛔ **Never `--apply` to make an UNEXPLAINED mismatch go away.** The dialog is the
only cheap warning that a save and the mod list have parted company. Silence it
when you already know why they differ; investigate when you do not. And it does
not repair anything — if a removed mod supplied defs the save references, you get
`Could not load reference to <def>` from Scribe instead, and no list edit fixes
that (`skills/rimworld-savegame`).

🔴 **The build stamp comes from the RUNNING GAME, not `Version.txt`.** Measured
2026-08-15: `Version.txt` read `1.6.4871 rev590` while the DefDump manifest and
all six saves — every file the engine itself writes — read `rev591`. `Version.txt`
ships with the install and does not track the runtime rev. The tool prefers the
runtime stamp and **refuses** to write a lower rev over a higher one, because
doing so manufactures the very mismatch it is meant to remove.

**Announce it if you are not the only seat.** Five seats share one working tree and one
game install. A re-sort in progress is exactly the thing another seat's blind write
destroys.

---

## 6. Fast triage: "the change didn't take"

Work down this table before forming any hypothesis. The answer is nearly always in the
first three rows.

| what you see | first thing to suspect |
|---|---|
| Mod is on disk but does not load | Subscribed but never added to the list — Steam does not write the list (§4) |
| Mod was unsubscribed but is still listed / still in the folder | Nothing removes the entry but you; and the game was probably up, holding the folder (§4) |
| Load order is right in RimSort, wrong in game | **Save** was never clicked (§2) |
| Your reorder vanished | Closed RimSort without Save, **or** another seat saved a stale view over you (§2, §3) |
| Your `ModsConfig.xml` edit vanished | Not the game — it does not write on exit. A seat, or a stale RimSort Save (§3) |
| A hand-authored mod never appears in RimSort at all | `local_folder` / `workshop_folder` swapped in settings (§2) |
| A rule saved and then was gone | It went into **Community Rules** with no configured source (§2) |
| A patch loads before the mod it patches | `loadBottom` is overriding `loadAfter`; or both mods asked for the bottom and the tie-break went the wrong way; or `modDependencies` was trusted for ordering (§2) |
| RimSort said "all clear" and the test still behaved as if the patch never applied | A clean sort only proves no *declared* rule was broken. Verify the pair order in `ModsConfig.xml` by hand (§2) |
| A hand-drag reverted after the next Sort | It was never written down as a User Rule (§2) |
| `no folder for it` every launch | Workshop item deleted upstream; unsubscribe is the only fix (§4) |

---

## Keeping this skill honest

The measurements in §3 corrected a claim this project had documented as settled and
believed for weeks. **When a claim here is load-bearing and you have a cheap way to
test it, test it** — an mtime comparison costs nothing and it is what caught the
rewrite-on-exit error. If something surprises you, append it to
`skills/rimworld-modding/references/traps-mods-and-managers.md` with symptom, cause,
fix and **"recurs when"**, and add the title to the index in `traps.md` in the same
commit.

<!-- status: live -->
# Rebuilding the keeper world, by hand

_DECIDE, 2026-08-21, at the owner's instruction — *"Write it now, while the steps are still
true."* Every command below was checked against the tool as it exists today, not
transcribed from the night's transcript._

> ⛔ **THIS IS A REDRAFT PROCEDURE, NOT A GENERATOR.** There is ONE map (owner, 2026-08-18).
> Nothing here may become a script that rolls a second planet, and **no seed or parameter
> may be exposed that would let it.** If you find yourself adding a knob, stop.

🔑 **Why it exists.** The keeper world was built on 2026-08-21 between 01:06 and 01:43 by a
sequence of commands that lived in a chat transcript and nowhere else. There is no worldgen
feature in any version, so **the owner rebuilding it by hand is the only route that will
ever exist** — and a keeper you cannot redraft is a keeper you cannot fix.

**The artifact this produces:** `world/WORLDMAP_gen.rws`, ~5.1 MB, world-only.
⚠️ **A save that weighs ~19.7 MB has a MAP in it and is the wrong thing.** Size is the
cheapest check you have.

---

## Before you start

| | |
|---|---|
| mod list | **578**, the owner's full stack. ⛔ Not the minimal list — the minimal list cannot place mod content |
| inputs | `world/ASHKARR_WORLDMAP_tiles.csv` · `..._settlements.csv` · `..._meta.json` — **the paint.** They are the authority; the save is downstream of them |
| the picture to match | `world/view/ASHKARR_WORLDMAP.biome.equirect.png` |
| bridge | CHECK's. One driver at a time |

⭐ **A fresh def dump is nearly free while you are loading anyway.** Arm it by writing `all`
into
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\dump_request.txt`.
⚠️ **The marker is NOT consumed by the run — delete it afterwards**, or every subsequent
load re-dumps.

---

## 1. Load on the 578-mod stack

Nothing to decide. Wait for the main menu.

## 2. 🔴 Configure Factions, by hand. This is the irreversible step.

**`infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` is the screen.** 21 untick / 4 keep,
plus Section 4b — *our own factions, each at least 1*.

🔴 **Permanent at world creation. A faction absent here is absent from every player's game
forever**, and the only remedy is regenerating, which discards everything after this step.

⚠️ **Check `SLATE_KEEPS_CONFIGURABLE_1` has shipped before you trust the screen.**
`JawaFactionSlate/Patches/OnlyOurFactions.xml` zeroes `maxConfigurableAtWorldCreation`,
which does **not** cap a faction — it removes it from
`FactionGenerator.ConfigurableFactions` entirely, so the row is not on the page and cannot
be added back. Until that item lands, four checklist rows are missing from the screen the
checklist is ticked on.

## 3. Generate, and save world-only

No map. Confirm the file is **~5 MB, not ~20 MB**.

## 4. ⏳ Create the `Pirate` faction by hand — *and check whether you still need to*

```
jawa/faction_create   defName=Pirate      # defaults to dryRun=true; read the plan, then dryRun=false
jawa/faction_name_set action=clear        # it arrives with a generated name; clearing falls through to the def label
```

🔑 **Why worldgen skips it.** Biotech's `PirateWaster` declares `replacesFaction` at
`Pirate`, so `Page_CreateWorldParams` strips `Pirate` from the default faction list. Without
this step the four Blackstar settlements have no owner, and **stage 5 refuses all 72 rather
than placing 68** — it is all-or-nothing by design.

🔴 **THIS STEP HAS AN EXPIRY DATE. Delete it when `PIRATE_VESSEL_RESTORED_1` ships.** That
item removes `replacesFaction` from `PirateWaster` and zeroes its inherited
`requiredCountAtGameStart`, after which `Pirate` appears on the Configure Factions screen
like any other faction and creating it by hand would be creating a duplicate.
⇒ **Before running this step, check whether `Pirate` was on the screen at step 2. If it
was, skip step 4 entirely.**

## 5. Stamp the paint

```
python.exe src/RimMandrake/Utils/w9_run.py            # dry run — this IS the default
python.exe src/RimMandrake/Utils/w9_run.py --apply    # for real
```

⚠️ **There is no `--dry` flag.** Dry is what you get by omitting `--apply`.
⚠️ Run it under **Windows `python.exe`**, not WSL's `python3`.

**Seven stages, and the ORDER is engine fact rather than taste** — mutators clear *after*
the biome repaint because the repaint is what strands them, and features go last:

| | stage |
|---|---|
| 1 | tiles — biome, elevation, temperature, rainfall, hilliness |
| 2 | links — **rivers then roads, file order matters** |
| 3 | clear the marine mutators the repaint stranded |
| 4 | landmarks |
| 4b | the derived mutators |
| 5 | settlements — ⛔ **all 72 or none** |
| 6 | named regions |

⚠️ **Other flags exist and are not conveniences.** `--despite-map` proceeds with a map
instantiated and makes everything measured unattributable; `--despite-abort` proceeds
through a failed load. **Neither belongs in a keeper run.**

## 6. Rename the twelve dice-named factions

They generate with random names. `jawa/faction_name_set`.
⭐ Once `FACTION_FIXEDNAME_ELEVEN_1` ships, eleven of the twelve carry `fixedName` and this
step shrinks to whatever is left.

## 7. Commit, lint, and **LOOK**

```
jawa/world_commit          # ⛔ without this, nothing you changed is visible
```

Then screenshot the planet and **put it beside
`world/view/ASHKARR_WORLDMAP.biome.equirect.png`**. 🔑 *A number that says the world is fine
while the picture shows compass circles is the number being wrong.* Looking is the check;
the lint is the sanity test underneath it.

✅ ~~Known unresolved: the Scald is not counting as water~~ **FIXED IN THE PAINT,
2026-08-21** (`bd5dad0`). Its 312 tiles were at +1411 m and the engine counts water as
`elevation <= 0`; they are now at −30 m like the two seas, water reads exactly 8.14%, and 32
false cliffs went with it — they existed because the lake surface stood a kilometre above the
ground beside it. ⇒ **a redraft from today's paint does not reproduce it.**
⏳ The relief render has not been looked at since — `SCALD_RELIEF_RENDER_LOOK_1`.

## 8. Back the save up into the repo, and force it

```
git add -f world/WORLDMAP_gen.rws
```

⚠️ **`*.rws` is gitignored, so a plain `git add` silently does nothing.**
🔴 **The keeper lived for an hour in exactly one Steam-Cloud-synced folder before anyone
noticed.** One disk and a cloud sync is not a backup; it is a single point of failure with
latency.

---

## What "done" looks like

- `world/WORLDMAP_gen.rws` exists, ~5.1 MB, **tracked in git**
- stage 5 reported **72 of 72** settlements, not 68
- no faction on the map carries a generated name
- the screenshot and the equirect render show the same planet
- `dump_request.txt` deleted

⛔ **If any step failed, do not patch around it in the live world.** Fix the input — the
paint, the checklist, the defs — and redraft. The CSVs are the authority; the save is
derived. That is the whole reason this document is short.

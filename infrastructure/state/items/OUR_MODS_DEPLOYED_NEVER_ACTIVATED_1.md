# OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1 — built, deployed, and never switched on

## what is wrong

MEASURED 2026-09-21 by parsing the live `ModsConfig.xml`
(`ET.parse(p).find("activeMods")` — ⛔ never scanned; `grep -c '<li>'` returns 48 where
the truth is 618):

| mod | packageId | in repo | deployed to the game's Mods folder | **in `ModsConfig.xml`** |
|---|---|---|---|---|
| `AshkarrFlora` | `mandrake.rut.ashkarrflora` | ✅ | ✅ | 🔴 **NO** |
| `GelatinousSlime` | `mandrake.rm.gelatinousslime` | ✅ | ✅ | 🔴 **NO** |

Both are fully authored and sitting in
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\`. Neither loads.
**Their content is completely inert.**

## the live consequence, which is not cosmetic

`RUT_Fuzz` and `RUT_Staggerseed` are `MayRequire`-guarded on `mandrake.rut.ashkarrflora`.
A `MayRequire` naming a mod that is not active is silently skipped — no error, no log line.

🔴 **`RUT_Fuzz` carries commonality 0.9 — the HEAVIEST row in the AridShrubland table.**
The plant that should dominate that biome never spawns, and the biome quietly runs on its
remaining rows. This is the *"zero rows is a failure, not a footnote"* shape: the roster
reads healthy and the game plays a different one.

⚠️ `GelatinousSlime` holds the Titanoslime, which is built and deployed but has never been
live-tested (`TITANOSLIME_SLIME_BIOME_1`). Activating it and testing it are the same step.

## 🔑 this is a RECURRING failure mode, not a one-off

`ENVHAZARDS_NEVER_ACTIVATED_1` was exactly this — a mod built and never activated — and it
was closed **the same day this was filed**. That makes three instances.

⇒ The gap is structural: **`deploy_custom_mods.py` writes files but does not, and should
not, touch the mod list**, so "deployed" and "active" are separate states with nothing
reconciling them. Nothing in the workflow asks *"is this mod actually switched on?"*
⚠️ `deploy_custom_mods.py` already PRINTS `mandrake.rm.gelatinousslime not enabled in
ModsConfig` — the information is there and nobody reads it. Worth a check that FAILS
rather than a line that scrolls past.

## spec

1. Decide whether each mod should be in the list (this is the owner's call — a mod-list
   change is a Charter expensive-list action, and `GelatinousSlime` ships untested content).
2. If yes, add them with a correct load-order position. ⚠️ Read the `rimworld-start-prep`
   skill first — RimWorld, RimSort and Steam are three uncoordinated writers, and "load at
   end" fails once every mod claims it. A patch belongs just after the mod it patches.
3. Add a reconciliation check: every mod folder under `src/` with an `About.xml` is either
   in `ModsConfig.xml` or named in `DEPLOY_HOLD.txt` with a reason.

## verify

The check reports zero unexplained deployed-but-inactive mods, and a live load shows
`RUT_Fuzz` present in AridShrubland.

## criteria

No mod we authored is sitting deployed and switched off without a recorded reason.

## ⛔ not done here, deliberately

`ModsConfig.xml` was **not edited**. It is the live mod list, the other window was
mid-verification on the running game, and `ModsConfig` describes the NEXT load — so a
change now would silently alter their next one.

## 🔴 Owner ruling, 2026-09-21 (BENCH, question card)

**Activate BOTH** — `AshkarrFlora` and `GelatinousSlime` go into `ModsConfig.xml` at the
correct load position. `RUT_Fuzz` (0.9, the heaviest AridShrubland row) starts spawning.

⚠️ `GelatinousSlime` renders magenta until its art lands — that is the missing-texture
colour, not a defect, and is not a reason to hold the activation.
⚠️ A cold load is the cost of proving this. Sequence it with whatever else is waiting on a
load rather than spending one on it alone.


## 🔴 RE-MEASURED 2026-09-21 by BENCH — half of this item's premise is no longer true

Instrument: `ET.parse(ModsConfig.xml).find("activeMods")` on the live file
(`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`).
⛔ Never `grep -c '<li>'` this file — it returns 48 where the truth is 619.

| | state now |
|---|---|
| **`mandrake.rut.ashkarrflora`** | ✅ **ACTIVE.** It is in the live list of **619**. |
| **GelatinousSlime** | ❌ still absent under any spelling (`gelatinousslime`, `slime`). |

⇒ 🔴 **The claim that `RUT_Fuzz` never spawns is FALSE as of today.** AshkarrFlora is
loaded, so the heaviest AridShrubland row is live. Only GelatinousSlime is still inert.
⚠️ The live file's mtime is 2026-09-20 21:30 PDT, which is AFTER this item was written, so
the item was probably true when filed and something activated AshkarrFlora since. Either
way it is not true now, and the owner was told the stronger version.

### Why the remaining activation was NOT done on his ruling

He ruled **"activate both"**. One is already done. The other was deliberately deferred:
FOUNDRY holds the bridge and `modset_builder.py` swaps this exact file per test tier, so
editing it mid-swap risks destroying another window's live test list. Nothing is lost by
waiting — `ModsConfig.xml` only describes the NEXT load, and he separately ruled that the
next cold load is a single batched one.

**NEXT (one act, when the bridge is free):** add `mandrake.rut.gelatinousslime` to
`activeMods` at the correct load position, parse-verify the count went 619 → 620, and put
it on the cold-load run sheet. ⚠️ It renders magenta until its art lands — the
missing-texture colour, not a defect.


## ✅ DONE 2026-09-21 — his ruling is fully discharged

The bridge freed and the game went down, which is the window this needed.

- **`mandrake.rm.gelatinousslime` added to `activeMods`**, immediately after
  `mandrake.rut.ashkarrflora` (our biome content sits together there).
- **Verified by parse, not by eye:** activeMods **619 → 620**; byte size 20825 → 20861, a
  delta of exactly 36 = the length of the inserted `<li>` element; CRLF count unchanged.
  ⚠️ The whole list is ONE line, so a line-based check would have reported nothing.
- Backup written alongside the live file as `ModsConfig.xml.bak-pre-gelatinousslime-<utc>`.

**Also deployed in the same window** (all reported `VERIFIED in sync`, plan-first then
`--apply`): `Pyrelands` (3 files, incl. the renamed `FireEcologyHook.dll`),
`PyrelandsMechanics`, `FlowWorks`, `GelatinousSlime`. Those were the builds blocked by the
running game — the Pyrelands rename (`84d42c63b`) and the Titanoslime permanent-growth
change (`8b9483b2e`).

⏸️ **Nothing is proven until a load.** Per his sequencing ruling the next cold load is a
single batched one — see `COLD_LOAD_RUN_SHEET_4`. This item can close on that load.

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

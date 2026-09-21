# DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1 — tables shipped before the species

## what happened

The desert biome rewire (`fda35ff14` + `96c1d9b81`) repointed 68 `wildAnimals`
and `wildPlants` entries at our `RSW_` desert-port defs. Those defs live in
**SWBestiary, which is not deployed.** `UtinniPatches` was deployed anyway.

MEASURED 2026-09-20 against the deployed mod folders (not the repo):
**18 refs in the deployed biome tables resolved to no deployed def** — every
wild plant of both biomes, plus `RSW_Sandstrider`, `RSW_Cindermite`,
`RSW_Spineroller`, `RSW_Sandhorn`, `RSW_Dunestalker`, `RSW_Ferroclaw`,
`RSW_Sandmaw`, `RSW_Tuskcoil`, `RSW_Stareling`, `RSW_Voltmaw`.

The running game was not affected — it loaded the tables at 17:06Z and the
deploy landed at 17:28Z. **The next cold load was the first that would have hit
it**, which is why `Player.log` has zero hits for these names.

## 🔴 the reasoning error, recorded because it will be made again

BENCH deployed the tables while deliberately holding SWBestiary, and justified
it out loud: *"the `MayRequire` guards mean the rows skip quietly while
SWBestiary is absent, instead of dangling."*

**That is false. `MayRequire` tests whether the MOD is ACTIVE, not whether the
DEF is PRESENT.** SWBestiary is active in `ModsConfig.xml` as an older deployed
build, so every guard passed and all 18 refs were kept and failed to resolve.

The guards are still correct and still worth having — they protect against the
mod being disabled. They do **not** protect against a stale deployed build of an
enabled mod, and nothing does except deploying the two together.

## what has been done

1. ✅ **The deployed copies were reverted by hand** to their pre-`fda35ff14`
   content (donor defNames), taken from git. Re-measured after: **0 unguarded
   dangling refs in the deployed tables.** The next cold load is safe.
2. ✅ **Both files added to `src/DEPLOY_HOLD.txt`** so the deploy tool will not
   ship them alone again. The hold text carries the reasoning error above.

⚠️ The deployed copies are therefore **hand-edited and behind the repo** — the
deploy tool reports them HELD, not in sync. That is deliberate, not drift.

## 🔴 RE-MEASURED 2026-09-20 — SWBestiary IS DEPLOYED, and the figure is now 3

The prose above says SWBestiary "is not deployed". **That is no longer true.**
`Mods/SWBestiary/About/About.xml` carries `mandrake.rsw.swbestiary` on disk, and
15 of the original 18 dangling names now resolve there (`RSW_Cindermite`,
`RSW_Sandstrider` and the rest, all in `Defs/DesertPort/RSW_DesertPortMisc_Races.xml`).

**Three still dangle, and they are a LIVE deploy gap, not a stale one:**
`RSW_GreatDevourer`, `RSW_Groundrunner`, `RSW_MatureFleshbeast`. All three exist in
the repo at `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/`, none is in
`DEPLOY_HOLD.txt`, and `deploy_custom_mods.py --mod SWBestiary` reports them as
plain drift (`+`) alongside `RSW_AADesertPort_Bodies.xml` and
`RSW_GreatDevourerEggs.xml`. They are the `DRUM_LURE_PREDATOR_BUILD_1` build,
which FOUNDRY has claimed with live verification owed.

⛔ **BENCH did not deploy them.** The game is RUNNING on FOUNDRY's 14-mod test tier
with FOUNDRY holding the bridge; deploying into their flight test is theirs to
time, not BENCH's to force.

## what is still owed

**NOTHING — CLOSED 2026-09-20 (BENCH), MEASURED.** Both halves landed in the same
sitting the item demanded, with the game DOWN:

- `SWBestiary` (defs + `RimMandrakeBeastMechanicsRSW.dll`) reports **in sync**,
  2410 files, 96 held — the 5-file gap (`RSW_GreatDevourer`, `RSW_Groundrunner`,
  `RSW_MatureFleshbeast`, `RSW_AADesertPort_Bodies.xml`, `RSW_GreatDevourerEggs.xml`)
  is closed.
- Both desert biome-table holds are lifted in `src/DEPLOY_HOLD.txt` (line 406), and
  the 14 drifted `UtinniPatches` biome files — 13 `RUT_*` BiomeDefs plus
  `Patches/BiomeFlora_Ashkarr.xml` — were deployed together and verified in sync.
- `selftest_deployed_biome_refs.py` re-run against the NEW deployed content:
  **499 deployed entries checked, 0 unresolved; 463 repo entries checked, 0
  WOULD-FAIL-ON-DEPLOY.** The repo-side figure was 3 before this sitting.

⚠️ **The deployed defs need a restart to take.** RimWorld parses defs only at
startup; the 14 files are on disk but not in any running game.

## Watch out

- ⚠️ **An unresolved ref in `wildAnimals` is cited by three items as "a known
  crash"**, but the review could find no item or doc recording the MECHANISM —
  only the consequence. Treat it as at least "the species never spawns" and do
  not upgrade it to "crash" in writing without evidence.
- ⚠️ **Deploying is not enough on its own.** 78 of SWBestiary's defs still have
  no art and will render as pink placeholders; that is
  `DESERT_PORT_PLACEHOLDER_ART_1` and the artpipe queue, not this item.

## verify

With both holds lifted and SWBestiary deployed: zero biome-table entries in the
deployed `UtinniPatches` resolve to nothing across the deployed mod folders, and
the new selftest asserts it in the `run_selftests.py` N/N.

## criteria

A biome table and the species it names can never ship apart again.

# Biome sprint: live run order (one launch serves every suite), 2026-10-16

For the BENCH round on the `biomes_sprint` tier (kickoff packet
`D:\Luke\dev\RimMandrake\design\RimMandrake\biome_sprint_kickoff_2026-10-15.md`, shared lines M1-M7). Whoever runs it
must hold the bridge (`rimflow bridge take --for "biome sprint round"`). FOUNDRY held it when this was written, so it
is the plan, not a record. Every command runs from the seat clone; `python.exe` for anything that calls the bridge.
Load the `live-debugging-proof-harness` skill before step 4.

## 0. Before launch (offline, about 10 min)

1. `git pull --ff-only`. Run all four offline preflights. Each must show only O-MANIFEST and O-SITE as UNMEASURED (no FAIL
   apart from the known Cauldron fleck art):
   `python3 src/RimMandrake/{Cauldron/preflight_cauldron,Contagion/preflight_contagion,LeaningScrub/preflight_leaningscrub,ExplosiveGrowth/preflight_explosivegrowth}.py`
2. If O-DEPLOY is stale, deploy the composite with the game closed (companion DLLs cannot be written while it runs):
   `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes` (read the plan, refuse another seat's lines),
   then `--apply`. Deploy the pilot mods (FlowWorks, GSS, Pyrelands mechanics) the same way if their plans show lines.
   Re-run step 1: O-DEPLOY PASS, and O-TEX PASS except `RM_TreeMartyr`/`RM_TwistingThornwood` (fleck art,
   `CAULDRON_FLECKS_FILL_SEVEN_STILL_BLANK`).
3. Check the JawaBench companion test profile: its expiry must lie beyond now + 8 h (plan X5; it expired mid-run twice).
4. `python3 src/RimMandrake/Utils/modset_builder.py --tier biomes_sprint` should give 22 mods with no refusals. Back up
   `ModsConfig.xml`, then `--apply`. Record the Player.log byte offset before launch.

## 1. Launch once (about 3-5 min on 22 mods)

`./game --why "biome sprint round on biomes_sprint" loading`. Read the FIRST exception in Player.log, not the loudest.
Write down the strings that decide the round before launch:
- `[RM ExplosiveGrowth] N plant defs soak … Everyday bands: M plant defs scaled …` (X1: present, N and M > 0);
- `[RM Cauldron] assay fleck overlays not on disk yet:` (expected until the art lands, and the ONLY Cauldron texture line);
- no `Could not resolve cross-reference` / `Could not load reference` naming `RM_`/`RSW_`/`RUT_`; no `sarg.alphaanimals`.

## 2. Build the three saved sites (about 30-40 min, each once and never overwritten)

The order follows build risk: the plainest recipe first.
1. `python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load calm`: the calm site was built 10-15 and its reload
   was never read back (registry has no `loadVerified`). ExplosiveGrowth's suite uses it.
2. `… test_site_saves.py build cauldron`: 250x250 RM_Cauldron patch on a scratch world. At step 8 the census
   needs ≥ 1 each of Suush, Vexxiss, Zisska, Eskith. Also note the ruin-kit pieces and the vents the fresh map
   placed: this is the only fresh Cauldron mapgen in the round (`CAULDRON_SUITE_WIDEN_RUINS_STILL_UNREAD`).
3. `… test_site_saves.py build leaningscrub`: step 8b locks the Lean heading, and step 10 must read the same heading
   within 0.01° after reload (`LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY`).
4. `… test_site_saves.py build contagion`: save only with the sky calm (8b: BurnActive False), per
   `CONTAGION_SITE_BUILD_SKY_STAYS_CALM`.
Each build backs up `Saves/` first and writes the registry. If any site's step 7 or 8 is not clean, record why and go
on to the next site; never hand-fix a site to make it pass.

## 3. Pilot guards first (M6, about 25 min)

They show the load is sound before biome failures can be blamed on it.
- GSS: `python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots` on the calm save.
- FlowWorks: `python.exe src/RimMandrake/FlowWorks/northstar/validation_v2.py --live` on the calm save. ⚠️ If the
  litres migration (`LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS`) has landed, a changed row count is expected: compare it
  against its new `required_checks`, not the 61/61 from 10-15.
- Pyrelands: the registry load is `northstar_site.py --site 1 --fingerprint 417df172fdb5 --tag calm --reload-only --tile 5`.
  The fingerprint is pinned. A mismatch refuses the load (plan X9) and costs a site rebuild (`test_site_saves.py build
  pyrelands`), never a wrong result.

## 4. Biome suites, one per loaded site (about 4-5 h)

`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod <Mod> --plan src/RimMandrake/<Mod>/northstar_plan.py`
after `test_site_saves.py load <site>`. The driver's own preflight puts settings at shipped defaults and turns the
storyteller off.

| order | suite | site | rows (O-SUITE) | precondition |
|---|---|---|---:|---|
| 1 | Cauldron | `cauldron` | 73 | none. Filter-Works/ruins/Oomo have no rows yet; the falter tell is timed against about 1 in-game hour (ruled) |
| 2 | LeaningScrub | `leaningscrub` | 85 | the Lean rows need FOUNDRY's walk-line components; until they exist the site only proves the heading lock |
| 3 | ExplosiveGrowth | `calm` | 59 | 8-38 °C at the map centre (its preflight). `scope_native_only` will read UNMEASURED here: expected, see step 5 |
| 4 | Contagion | `contagion` | 80 | **blocked** until `CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK` (FOUNDRY) lands: `northstar_site.py` refuses an RM_Contagion map. If it has not landed, skip and say so |

After each suite: read the FIRST exception, classify every FAIL/UNMEASURED as MOD, SITE or HARNESS, and record only a
full live run (`modcheck record`; `--only` partials are refused). File MOD findings for FOUNDRY at once; fix HARNESS
findings offline after the round, never mid-run.

## 5. The one second load: ExplosiveGrowth scope (about 5 min)

With the campaign layer (`mandrake.rut.patches`) loaded, every biome is in scope, so `scope_native_only` cannot be
seen on `biomes_sprint`. Close the game, run `modset_builder.py --tier explosivegrowth_solo --apply`, launch (Baroque
Biomes plus the bridge, a minimal list), start a temperate quicktest, and run only that chain. Record it on
`EXPLOSIVE_SCOPE_ROW_PROVE_NEEDS_QUIET_LIST` (S0-8).

## 6. Close out

Restore the owner's `ModsConfig.xml` from the step-0 backup (`--restore`), then `rimflow bridge release` and run
`rimflow verify` per suite against the round's HEAD. Commit the registry `src/RimMandrake/Utils/modcheck/test_site_saves.json`
and the modcheck records by explicit path, then `./publish`.

## Not in this round

- X2 perf gate (ExplosiveGrowth on a jungle-density saved map): no such site is declared yet. It needs a Greentide,
  Miasma or Fever Wood site and the owner's S0-6 figure, so it goes to round 2.
- X3 soak routes in Greentide, Miasma and Fever Wood (wet-ambient x10): the same site question as X2.
- Review saves (S2) and any flyer look: those need the owner present.

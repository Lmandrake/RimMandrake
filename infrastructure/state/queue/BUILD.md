# BUILD inbox.

## B-V2 v2 ideas go to `design/V2_DREAMS.md` — append them yourself
row:      infra
spec:     Any idea for new content that is not v1 is appended to the END of
          `design/V2_DREAMS.md`. You have a standing right to append there directly:
          no permission, no routing through DECIDE, no queue item asking for it, no
          format and no field contract. Never queue v2 work and never leave it as a
          `[v2]` tag in a working doc.
verify:   read the header of `design/V2_DREAMS.md` once; it says the same thing.
criteria: EMPTY — that file is not a queue and nothing in it is scheduled.
state:    ready

## B0 Deploy the 30-tool companion at the next down game
row:      7
spec:     `src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll`,
          md5 `d7e7c6c1`, 30 `jawa/` tools. **`--gm` REQUIRED** or `fire_incident`
          and `send_letter` are stripped off the game copy. Game must be DOWN.
          Deploy `JawaSeaShaper.dll` SOLO in the same window — repo `b7730027`
          vs deployed `82b48e53` — it cannot be written while RimWorld runs.
verify:   md5 of the deployed DLL equals `d7e7c6c1`, and `fire_incident` +
          `send_letter` are present in the deployed bytes (`strings -a -el`).
criteria: `rimbridge/list_tools` counts 30 `jawa/` names.
state:    ready

## B1 BridgeTools 30-tool build and deploy — `--gm` is REQUIRED
row:      7
spec:     `cd /mnt/d/Luke/dev/Rimworld; python.exe src/RimMandrake/bridgetools/build.py --gm --apply`. Game must be DOWN — the DLL is locked while it runs and the write fails `OSError 22` (the refusal is safe, it cannot truncate). Without `--gm` the build STRIPS `jawa/fire_incident` and `jawa/send_letter` off the game copy (30 tools -> 28). One-command form: `./src/RimMandrake/Utils/shutdown_deploy.sh [--yes]` runs S8 -> S1 -> S9 in order and refuses while RimWorld is running.
verify:   `D="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/BridgeTools/JawaBench/JawaBench.BridgeTools.dll"`; `md5sum "$D"` expect `d7e7c6c1...`; `strings -a "$D" | grep -oE 'jawa/[a-z_]+' | sort -u | wc -l` expect **30**; both `--gm` canaries `jawa/fire_incident` and `jawa/send_letter` present. `--apply` REBUILDS before deploying, so a rebuild legitimately produces different bytes — gate on the canaries and the count, not on the md5. Census expectation derives from `.cs` ONLY: `grep -rhoE '"jawa/[a-z_]+"' --include='*.cs' src/RimMandrake/bridgetools/` (without the include it returns one too many — `prove_new_tools.py:112` has `[Tool("jawa/x")]` inside a comment). `strings -a` proves a NAME only; use `strings -a -el` to prove a method-body message shipped (UTF-16LE in the `#US` heap).
criteria: five tools respond live — `jawa/set_faction_relation` (unblocks v1 L3), `jawa/inspect_string` (reads `Thing.GetInspectString()`: `WarningThrusterInside`, `ThrusterBlockedBy`, power, breakdown), `jawa/world_stats` unit fix (`perimeterTiles`, `raggedness` from tiles, `centroidLatNorm`), `jawa/ideo_of`, `jawa/biome_probe`. `TicksGameSafe()` rides along: def reads must work at `programState: Entry` instead of throwing a bare NRE on every tool at the main menu.
state:    ready

## B2 JawaSeaShaper.dll deploy — SOLO, its own load
row:      7
spec:     `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaSeaShaper --apply`. Repo md5 `b7730027a639`; deployed/loaded md5 `82b48e53e668`, mtime 08-13 23:57:29. Game DOWN (loaded and locked). A MOD assembly poisons attribution for anything loaded beside it — do not batch it with a load meant to prove something else.
verify:   deployed md5 == `b7730027a639`.
criteria: the arc-distance and elongation work committed in `c3ee8e7` is present in the running game. S1 is rescoped: it PARTITIONS, it does not write the sea — vanilla already produces 1–2 huge masses with no puddles (`bodiesTotal == bodiesOverMinSize`, n=4) and never 3 bodies; a cut adds boundary tiles without adding area.
state:    ready

## B8 `gravship_flight_invariants.md` §11 is WRONG ON BOTH BRANCHES
row:      infra
spec:     Correct §11 of `gravship_flight_invariants.md` to the measured facts. The export holds **zero thrusters, zero tanks, zero consoles**. The format has **no roof field**, but roofs are derivable: GravshipExport regenerates them at import by flood-fill (`Patch_Sketch_GetSuggestedRoofCells_Postfix.cs:45-85`) => **4,049 of 4,057 substructure cells roofed, every standable cell indoors**. There is **no stern re-lay**: the cost is ONE `GravshipHull` cell per small thruster (two per large), because `ThrusterBase` is `holdsRoof true` + `fillPercent 1` and seals the room exactly as the wall it replaces. Nine sites at x41–49, z131/132; the aft strip (x,133) is off-deck.
verify:   §11 states those measurements and marks the roof map as DERIVED (the mod's own algorithm re-run), not observed.
criteria: EMPTY
state:    ready

## B21 `loadset_fingerprint()` must compare listed against exists
row:      infra
spec:     The `ModsConfig.xml` listed-but-missing trap in code form: `loadset_fingerprint()` compares *listed* against *exists*.
verify:   a synthetic `ModsConfig.xml` listing a packageId that is not on disk is reported, not silently passed.
criteria: EMPTY
state:    ready

## B22 `validate_patch.py` — an op in `<nomatch>` with the test's own xpath is statically dead
row:      infra
spec:     The mirror of O8 and the opposite verdict: reaching `<nomatch>` proves the test matched NOTHING, so an identical-xpath op there can never do anything. Provable WITHOUT `--defs`; today it is only caught as a 0-match ERROR when defs are loaded. `<nomatch>` must stay an ERROR — unlike the `<match>` branch, which `_guarded_by_identical_test()` correctly downgrades to info.
verify:   a synthetic `<nomatch>` case is flagged with no `--defs`; `DroidsAreMachines.xml` still reports OK (0 errors, 2 warnings).
criteria: EMPTY
state:    ready

## B23 Write the three expected-failure signatures before the worldgen session
row:      7
spec:     Write the expected-failure signatures into `EXPECTED_FAILURES` BEFORE the worldgen load. A duplicate costs nothing; a missed one costs a load.
verify:   the signatures exist in `EXPECTED_FAILURES` before launch.
criteria: EMPTY
state:    ready

## B25 The game-down mod-list batch — one pass before the next launch
row:      infra
spec:     (a) Pin the 6 `loadBottom`+`loadAfter` userRules — order is correct today but rides a tie-break, not a constraint; `loadBottom` outranks `loadAfter`, keep it only on `rimdefdump`. (b) Run `src/RimMandrake/Utils/refresh.py` (wants the game down). (c) **O-v2 Cherry Picker** — remove mechanoid defs AND the `Mechanoid` faction; answer three things: does the game still load · does `Samael.NPCMechsAndAnimals` survive and keep its ANIMALS half (`Patches/NPC_Mechs.xml`, 13 ops into `Empire`/`Outlander*`/`Pirate*`/`TradersGuild`) · is that mod configurable. Do NOT remove Alpha Mechs (`sarg.alphamechs`). `matathias.ruthlessmechanoids` is NOT a mech mod (it is the gravship pursuer redirect) — leave it on. REPORT, do not resolve: Alpha Mechs hangs off `FactionDef[defName="Mechanoid"]/pawnGroupMakers`, so cutting that faction takes its raids too. (d) **O-v3** — enable `vanillaexpanded.vwel` (ws `1989352844`, installed and inactive) and dump its weapon `ThingDef`s in TWO SEPARATE tiers: `salvaged` (pistol/rifle/shotgun/sniper + `unstable` projectile variants) and `ultratech` (incl. a laser sword and a tesla gun). The split is load-bearing for the design (`design/Jawa/worldbuilding/ship_legacy_armoury.md`).
verify:   read `ModsConfig.xml`'s mtime before writing — RimSort writes it too, and it moved twice in twenty minutes with the game down.
criteria: the game reaches the main menu with the new list; the two weapon tiers exist as separate dumps.
state:    ready

## B26 Remove `mandrake.missingartfixes`
row:      infra
spec:     Already dropped from `ModsConfig.xml`; all 7 textures are md5-identical to the per-donor successors and the blocking dependency is cleared. Remove the deployed copy under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\` and the repo folder.
verify:   neither path exists.
criteria: EMPTY
state:    ready

## B27 Rebuild the skill zips at hand-off
row:      infra
spec:     `python3 src/RimMandrake/Utils/package_skill.py --all`. Editing `skills/<name>/` is not shipping it — Claude Code installs from a `.skill` zip and those are gitignored, so a fresh clone has none. `skills/rimworld-quests.skill` (65 KB) is one that exists only on disk.
verify:   read the EXIT CODE and the named failure list, never the directory listing — a failure leaves its own zip stale beside fresh ones.
criteria: EMPTY
state:    ready

## B34 Correct the "More Slavery Stuff (Continued)" workshop ID in the design docs
row:      infra
spec:     WS `3530586159` is cited as adopted in several design docs but is NOT installed — a grep of all 1246 workshop `About.xml` files matches only the original `2896845138`, which is active and supplies every `GarryFlowers_` def in use.
verify:   grep of the design docs returns no `3530586159`.
criteria: EMPTY
state:    ready

## B35 Execute the restructure to option B
row:      infra
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` — ten stages, ONE commit each, lowest-risk first. Stage 9 (`skills/`) is owner-gated and may never run. §3's seven unplaced items need a ruling before stage 4.
verify:   run `src/RimMandrake/Utils/check_refs.py` and `src/RimMandrake/Utils/doc_budget.py` after EVERY stage; §8 names the check that proves a stage landed whole.
criteria: EMPTY
state:    blocked

## B36 Deferred renames
row:      infra
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` §7. `JawaBench.BridgeTools` -> `RimMandrake.Bridge` (14 tracked files, 4 identities including the deploy folder). The `jawa/<tool>` namespace: 35 tracked files at once, canonically 17 `[Tool]` attributes in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`, 3 of the 35 being generated JSON. The five `Jawa*` mod folders. All five packageIds ARE active in `ModsConfig.xml` (lines 560–571 of 575) => a load-order edit at a specific slot plus a RimSort rules edit, not a `sed`.
verify:   `check_refs.py` clean; `ModsConfig.xml` slots preserved.
criteria: the game loads with the renamed mods at the same load positions.
state:    blocked

## B37 Two save-citation sweeps
row:      infra
spec:     (1) The prisoner `interactionMode` finding in `TODO_v2.md` — the save it rested on is gone (`acc3261`) and the file was compacted from 1,144+ lines to 350, so its line citation points at nothing. Find it BY TEXT, mark it measured-and-unreproducible, do not delete it. (2) `save_authoring_pipeline.md:141` and `rimworld_file_lore.md` anchor the whole `.rws` teardown to `~/GDrive/Personal/Rimworld/observed/2026-08-13_pre-restructure/savegame/03_Gravtasm__starting_save.rws`; `~/GDrive` does not exist in this WSL at all — the directory is absent, not the file. Establish whether that path is Windows-side, another machine, or dead, then correct it or mark the teardown as a record whose source artifact is unavailable. Do not delete the lore.
verify:   neither file cites a path that does not resolve.
criteria: EMPTY
state:    ready

## B39 The mod freeze — reconcile the decision docs against the live 585
row:      0
spec:     The frozen baseline is measured and in `V1_CHAIN.md` §0: `activeMods`
          585, loaded 585, zero listed-but-missing, zero loaded-but-unlisted.
          Do NOT re-audit 585 mods. Emit ONE table of DIVERGENCES only, joining
          the live `activeMods` list from
          `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`
          against every verdict in `design/Jawa/mods/forbidden_mods.md`,
          `required_mods.md`, `cherry_picker_killlist.md` and `armoury_keeplist.md`.
          Columns: `packageId | mod name | doc verdict | which doc + line | live
          state (active / installed-inactive / absent)`. A row appears ONLY where
          a doc verdict disagrees with the live state.
          Two divergences are already ruled and must appear resolved, not open:
          KotOR is KEPT (`required_mods.md`'s DECLINE is stale), and
          `lee.theforce.lightsaber` is active and loaded (`cherrypick_inbox.md`'s
          "not installed" is stale).
          Write it to `design/Jawa/mods/MOD_FREEZE.md`. Do not change
          `ModsConfig.xml` — this item decides nothing, it surfaces the list
          DECIDE rules on.
verify:   `MOD_FREEZE.md` exists; every row cites a doc and a line; the row count
          is stated; re-running the join reproduces the same set.
criteria: none — offline only. Nothing to see in a live game.
state:    ready

## B40 Graft the Outer Rim Imperial kinds onto vanilla `Empire`
row:      9
spec:     Per `V1_CHAIN.md` R15. Re-point
          `src/Jawa/Jawa_Patches/Patches/ImperialDesertDirectorate.xml` from
          `FactionDef[defName="OuterRim_GalacticEmpire"]` to
          `FactionDef[defName="Empire"]`, and patch that def's COMBAT
          `pawnGroupMakers` options to the Outer Rim Imperial kinds —
          `OuterRim_ImpDeathTrooper`, `OuterRim_ImpISBAgent`,
          `OuterRim_ImpRangeTrooper`, `OuterRim_ImpStormArty`,
          `OuterRim_ImpStormIncinerator`, `OuterRim_ImpStormJump`. Leave the
          Trader and Settlement groupMakers alone. Set `leaderTitle` to
          `Emperor` (R11, replacing `Sector Director`) and add
          `fixedName` `Galactic Empire` — `NamerFactionEmpire` otherwise
          generates a random name and the world must say Galactic Empire.
          Vanilla `Empire` measures `settlementGenerationWeight 1` against
          `OuterRim_GalacticEmpire`'s 0.3, which is why the Directorate held one
          settlement to the Fallen Dominion's four.
          ⚠️ Both mods are active so the kinds resolve, but wrap each `<li>` in
          the correct `MayRequire` for the Outer Rim packageId — an unwrapped
          defName from a disabled mod is a silent no-op.
verify:   `validate_patch.py --defs` scoped to the active list, 0 errors; the
          xpath matches `Empire` and not `OuterRim_GalacticEmpire`; every
          `OuterRim_Imp*` defName resolves in the live dump.
criteria: the Empire raids with stormtroopers, not cataphracts, and the faction
          reads `Galactic Empire` with an `Emperor`. 🔴 This REDOES v1 row 1,
          which was closed on a label seen live on the abandoned vessel.
state:    ready

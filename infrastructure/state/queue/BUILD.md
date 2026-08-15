# BUILD inbox.

## B-V2 Park any v2 idea in design/V2_DREAMS.md yourself — no permission needed
row:      doctrine
spec:     Any idea for new content that is not v1 is appended to the END of
          `design/V2_DREAMS.md`. You have a standing right to append there directly:
          no permission, no routing through DECIDE, no queue item asking for it, no
          format and no field contract. Never queue v2 work and never leave it as a
          `[v2]` tag in a working doc.
verify:   read the header of `design/V2_DREAMS.md` once; it says the same thing.
criteria: EMPTY — that file is not a queue and nothing in it is scheduled.
state:    ready

## B0 Install the 30 new bridge tools (game must be closed)
row:      10
spec:     `src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll`,
          md5 `d7e7c6c1`, 30 `jawa/` tools. **`--gm` REQUIRED** or `fire_incident`
          and `send_letter` are stripped off the game copy. Game must be DOWN.
          Deploy `JawaSeaShaper.dll` SOLO in the same window — repo `b7730027`
          vs deployed `82b48e53` — it cannot be written while RimWorld runs.
verify:   md5 of the deployed DLL equals `d7e7c6c1`, and `fire_incident` +
          `send_letter` are present in the deployed bytes (`strings -a -el`).
criteria: `rimbridge/list_tools` counts 30 `jawa/` names.
state:    ready

## B1 Build and install the bridge tools — without --gm, two tools vanish
row:      10
spec:     `cd /mnt/d/Luke/dev/Rimworld; python.exe src/RimMandrake/bridgetools/build.py --gm --apply`. Game must be DOWN — the DLL is locked while it runs and the write fails `OSError 22` (the refusal is safe, it cannot truncate). Without `--gm` the build STRIPS `jawa/fire_incident` and `jawa/send_letter` off the game copy (30 tools -> 28). One-command form: `./src/RimMandrake/Utils/shutdown_deploy.sh [--yes]` runs S8 -> S1 -> S9 in order and refuses while RimWorld is running.
verify:   `D="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/BridgeTools/JawaBench/JawaBench.BridgeTools.dll"`; `md5sum "$D"` expect `d7e7c6c1...`; `strings -a "$D" | grep -oE 'jawa/[a-z_]+' | sort -u | wc -l` expect **30**; both `--gm` canaries `jawa/fire_incident` and `jawa/send_letter` present. `--apply` REBUILDS before deploying, so a rebuild legitimately produces different bytes — gate on the canaries and the count, not on the md5. Census expectation derives from `.cs` ONLY: `grep -rhoE '"jawa/[a-z_]+"' --include='*.cs' src/RimMandrake/bridgetools/` (without the include it returns one too many — `prove_new_tools.py:112` has `[Tool("jawa/x")]` inside a comment). `strings -a` proves a NAME only; use `strings -a -el` to prove a method-body message shipped (UTF-16LE in the `#US` heap).
criteria: five tools respond live — `jawa/set_faction_relation` (unblocks v1 L3), `jawa/inspect_string` (reads `Thing.GetInspectString()`: `WarningThrusterInside`, `ThrusterBlockedBy`, power, breakdown), `jawa/world_stats` unit fix (`perimeterTiles`, `raggedness` from tiles, `centroidLatNorm`), `jawa/ideo_of`, `jawa/biome_probe`. `TicksGameSafe()` rides along: def reads must work at `programState: Entry` instead of throwing a bare NRE on every tool at the main menu.
state:    ready

## B8 Correct the gravship doc — its thruster section is wrong and is guiding plans
row:      repo
spec:     Correct §11 of `gravship_flight_invariants.md` to the measured facts. The export holds **zero thrusters, zero tanks, zero consoles**. The format has **no roof field**, but roofs are derivable: GravshipExport regenerates them at import by flood-fill (`Patch_Sketch_GetSuggestedRoofCells_Postfix.cs:45-85`) => **4,049 of 4,057 substructure cells roofed, every standable cell indoors**. There is **no stern re-lay**: the cost is ONE `GravshipHull` cell per small thruster (two per large), because `ThrusterBase` is `holdsRoof true` + `fillPercent 1` and seals the room exactly as the wall it replaces. Nine sites at x41–49, z131/132; the aft strip (x,133) is off-deck.
verify:   §11 states those measurements and marks the roof map as DERIVED (the mod's own algorithm re-run), not observed.
criteria: EMPTY
state:    done

## B21 Make our mod checker notice a mod that is listed but not installed
row:      tooling
spec:     The `ModsConfig.xml` listed-but-missing trap in code form: `loadset_fingerprint()` compares *listed* against *exists*.
verify:   a synthetic `ModsConfig.xml` listing a packageId that is not on disk is reported, not silently passed.
criteria: EMPTY
state:    done

## B22 Teach the patch validator to spot a rule that can never fire
row:      tooling
spec:     The mirror of O8 and the opposite verdict: reaching `<nomatch>` proves the test matched NOTHING, so an identical-xpath op there can never do anything. Provable WITHOUT `--defs`; today it is only caught as a 0-match ERROR when defs are loaded. `<nomatch>` must stay an ERROR — unlike the `<match>` branch, which `_guarded_by_identical_test()` correctly downgrades to info.
verify:   a synthetic `<nomatch>` case is flagged with no `--defs`; `DroidsAreMachines.xml` still reports OK (0 errors, 2 warnings).
criteria: EMPTY
state:    done

## B23 Pre-record three known errors so they don't alarm anyone during worldgen
row:      10
spec:     Write the expected-failure signatures into `EXPECTED_FAILURES` BEFORE the worldgen load. A duplicate costs nothing; a missed one costs a load.
verify:   the signatures exist in `EXPECTED_FAILURES` before launch.
criteria: EMPTY
state:    ready

## B25 Mod-list chores to do in one pass while the game is closed
row:      0
spec:     (a) Pin the 6 `loadBottom`+`loadAfter` userRules — order is correct today but rides a tie-break, not a constraint; `loadBottom` outranks `loadAfter`, keep it only on `rimdefdump`. (b) Run `src/RimMandrake/Utils/refresh.py` (wants the game down). (c) **O-v2 Cherry Picker** — remove mechanoid defs AND the `Mechanoid` faction; answer three things: does the game still load · does `Samael.NPCMechsAndAnimals` survive and keep its ANIMALS half (`Patches/NPC_Mechs.xml`, 13 ops into `Empire`/`Outlander*`/`Pirate*`/`TradersGuild`) · is that mod configurable. Do NOT remove Alpha Mechs (`sarg.alphamechs`). `matathias.ruthlessmechanoids` is NOT a mech mod (it is the gravship pursuer redirect) — leave it on. REPORT, do not resolve: Alpha Mechs hangs off `FactionDef[defName="Mechanoid"]/pawnGroupMakers`, so cutting that faction takes its raids too. (d) **O-v3** — enable `vanillaexpanded.vwel` (ws `1989352844`, installed and inactive) and dump its weapon `ThingDef`s in TWO SEPARATE tiers: `salvaged` (pistol/rifle/shotgun/sniper + `unstable` projectile variants) and `ultratech` (incl. a laser sword and a tesla gun). The split is load-bearing for the design (`design/Jawa/worldbuilding/ship_legacy_armoury.md`).
verify:   read `ModsConfig.xml`'s mtime before writing — RimSort writes it too, and it moved twice in twenty minutes with the game down.
criteria: the game reaches the main menu with the new list; the two weapon tiers exist as separate dumps.
state:    ready

## B26 Delete the retired art-fix mod now that its replacements ship
row:      repo
spec:     Already dropped from `ModsConfig.xml`; all 7 textures are md5-identical to the per-donor successors and the blocking dependency is cleared. Remove the deployed copy under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\` and the repo folder.
verify:   neither path exists.
criteria: EMPTY
state:    done

## B27 Repackage the skills — editing the folder does not ship them
row:      tooling
spec:     `python3 src/RimMandrake/Utils/package_skill.py --all`. Editing `skills/<name>/` is not shipping it — Claude Code installs from a `.skill` zip and those are gitignored, so a fresh clone has none. `skills/rimworld-quests.skill` (65 KB) is one that exists only on disk.
verify:   read the EXIT CODE and the named failure list, never the directory listing — a failure leaves its own zip stale beside fresh ones.
criteria: EMPTY
state:    done

## B34 Fix a wrong mod ID cited across the design docs
row:      repo
spec:     WS `3530586159` is cited as adopted in several design docs but is NOT installed — a grep of all 1246 workshop `About.xml` files matches only the original `2896845138`, which is active and supplies every `GarryFlowers_` def in use.
verify:   grep of the design docs returns no `3530586159`.
criteria: EMPTY
state:    done

## B35 Move the repo to the agreed folder layout, one stage per commit
row:      repo
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` — ten stages, ONE commit each, lowest-risk first. Stage 9 (`skills/`) is owner-gated and may never run. §3's seven unplaced items need a ruling before stage 4.
verify:   run `src/RimMandrake/Utils/check_refs.py` and `src/RimMandrake/Utils/doc_budget.py` after EVERY stage; §8 names the check that proves a stage landed whole.
criteria: EMPTY
state:    blocked

## B36 Rename the mods and tool namespace — 35 files and the load order
row:      repo
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` §7. `JawaBench.BridgeTools` -> `RimMandrake.Bridge` (14 tracked files, 4 identities including the deploy folder). The `jawa/<tool>` namespace: 35 tracked files at once, canonically 17 `[Tool]` attributes in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`, 3 of the 35 being generated JSON. The five `Jawa*` mod folders. All five packageIds ARE active in `ModsConfig.xml` (lines 560–571 of 575) => a load-order edit at a specific slot plus a RimSort rules edit, not a `sed`.
verify:   `check_refs.py` clean; `ModsConfig.xml` slots preserved.
criteria: the game loads with the renamed mods at the same load positions.
state:    blocked

## B37 Two docs cite files that no longer exist — find or retire the evidence
row:      repo
spec:     (1) The prisoner `interactionMode` finding in `TODO_v2.md` — the save it rested on is gone (`acc3261`) and the file was compacted from 1,144+ lines to 350, so its line citation points at nothing. Find it BY TEXT, mark it measured-and-unreproducible, do not delete it. (2) `save_authoring_pipeline.md:141` and `rimworld_file_lore.md` anchor the whole `.rws` teardown to `~/GDrive/Personal/Rimworld/observed/2026-08-13_pre-restructure/savegame/03_Gravtasm__starting_save.rws`; `~/GDrive` does not exist in this WSL at all — the directory is absent, not the file. Establish whether that path is Windows-side, another machine, or dead, then correct it or mark the teardown as a record whose source artifact is unavailable. Do not delete the lore.
verify:   neither file cites a path that does not resolve.
criteria: EMPTY
state:    ready

## B39 List every place a design doc disagrees with the frozen mod list
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

## B40 Give the Empire stormtroopers instead of medieval knights
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

## B41 Turn vanilla outlanders into the Homestead Defense League
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 3. A `PatchOperation` on
          `FactionDef[defName="OutlanderCivil"]`, NOT a new def. Patch only the fields
          that section lists. ⛔ Do NOT touch `pawnGroupMakers`, `factionNameMaker`
          or the raid curves — they are inherited and already balanced.
          raidsForbidden true is the mechanism (R2), NOT a precept. Weight 1.9.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; the xpath matches `OutlanderCivil` and nothing else; every `<li>` naming
          a def from another mod carries the correct `MayRequire`.
criteria: the faction reads as Homestead Defense League in the world faction list, with the
          leaderTitle from the spec.
state:    ready

## B42 Turn vanilla tribes into the Deep Desert Tribes, and add a water raid
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 4. A `PatchOperation` on
          `FactionDef[defName="TribeCivil"]`, NOT a new def. Patch only the fields
          that section lists. ⛔ Do NOT touch `pawnGroupMakers`, `factionNameMaker`
          or the raid curves — they are inherited and already balanced.
          ADD one Combat group: the water raid - fast, light, targets containers, disengages once loaded. Vanilla has no equivalent and it is the faction's signature.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; the xpath matches `TribeCivil` and nothing else; every `<li>` naming
          a def from another mod carries the correct `MayRequire`.
criteria: the faction reads as Deep Desert Tribes in the world faction list, with the
          leaderTitle from the spec.
state:    ready

## B43 Turn vanilla pirates into the Blackstar Company
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 10. A `PatchOperation` on
          `FactionDef[defName="Pirate"]`, NOT a new def. Patch only the fields
          that section lists. ⛔ Do NOT touch `pawnGroupMakers`, `factionNameMaker`
          or the raid curves — they are inherited and already balanced.
          KEEP permanentEnemy true - the vessel default. The dossier says No; R12 amends pillar 5 instead, because patching it false guts the vanilla raid economy.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; the xpath matches `Pirate` and nothing else; every `<li>` naming
          a def from another mod carries the correct `MayRequire`.
criteria: the faction reads as Blackstar Company in the world faction list, with the
          leaderTitle from the spec.
state:    ready

## B45 Create the Hutt Cartel as a new faction
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 2 for every field value, plus its "Namers and icons"
          and "pawnGroupMakers" tables for this faction. Model:
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`.
          Fill EVERY group in the contract — identity · generation · naming · art
          · hostility · pawns. A missing `factionNameMaker`, `factionIconPath`
          or `colorSpectrum` is a broken faction screen, not a cosmetic gap —
          `colorSpectrum` values are in the spec's R22 table.
          ⛔ OMIT the ideo group (R23) unless this faction is the Hutt Cartel,
          whose text is already authored. It lands in a second pass from D18 and
          MUST be in before the worldgen click. `basicMemberKind` is OPTIONAL
          (R21) — do not invent one.
          🪤 `combatPower 99999` kinds are legal in `traders`/`carriers`/`guards`
          and POISON in `options`. `minTotalPoints` does not exist.
          `PawnGenOption` has exactly `kind` and `selectionWeight`.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; every `kind` named in a `pawnGroupMaker` resolves in the live def
          dump; `factionNameMaker` and `factionIconPath` are non-null.
criteria: the faction generates settlements at worldgen and its pawns spawn as
          the named kinds.
state:    ready

## B46 Create the Free Droid Enclaves as a new faction
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 5 for every field value, plus its "Namers and icons"
          and "pawnGroupMakers" tables for this faction. Model:
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`.
          Fill EVERY group in the contract — identity · generation · naming · art
          · hostility · pawns. A missing `factionNameMaker`, `factionIconPath`
          or `colorSpectrum` is a broken faction screen, not a cosmetic gap —
          `colorSpectrum` values are in the spec's R22 table.
          ⛔ OMIT the ideo group (R23) unless this faction is the Hutt Cartel,
          whose text is already authored. It lands in a second pass from D18 and
          MUST be in before the worldgen click. `basicMemberKind` is OPTIONAL
          (R21) — do not invent one.
          🪤 `combatPower 99999` kinds are legal in `traders`/`carriers`/`guards`
          and POISON in `options`. `minTotalPoints` does not exist.
          `PawnGenOption` has exactly `kind` and `selectionWeight`.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; every `kind` named in a `pawnGroupMaker` resolves in the live def
          dump; `factionNameMaker` and `factionIconPath` are non-null.
criteria: the faction generates settlements at worldgen and its pawns spawn as
          the named kinds.
state:    ready

## B47 Create the Wildsteam Clan as a new faction
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 6 for every field value, plus its "Namers and icons"
          and "pawnGroupMakers" tables for this faction. Model:
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`.
          Fill EVERY group in the contract — identity · generation · naming · art
          · hostility · pawns. A missing `factionNameMaker`, `factionIconPath`
          or `colorSpectrum` is a broken faction screen, not a cosmetic gap —
          `colorSpectrum` values are in the spec's R22 table.
          ⛔ OMIT the ideo group (R23) unless this faction is the Hutt Cartel,
          whose text is already authored. It lands in a second pass from D18 and
          MUST be in before the worldgen click. `basicMemberKind` is OPTIONAL
          (R21) — do not invent one.
          🪤 `combatPower 99999` kinds are legal in `traders`/`carriers`/`guards`
          and POISON in `options`. `minTotalPoints` does not exist.
          `PawnGenOption` has exactly `kind` and `selectionWeight`.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; every `kind` named in a `pawnGroupMaker` resolves in the live def
          dump; `factionNameMaker` and `factionIconPath` are non-null.
criteria: the faction generates settlements at worldgen and its pawns spawn as
          the named kinds.
state:    ready

## B48 Create the Deepwater Compact as a new faction
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 7 for every field value, plus its "Namers and icons"
          and "pawnGroupMakers" tables for this faction. Model:
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`.
          Fill EVERY group in the contract — identity · generation · naming · art
          · hostility · pawns. A missing `factionNameMaker`, `factionIconPath`
          or `colorSpectrum` is a broken faction screen, not a cosmetic gap —
          `colorSpectrum` values are in the spec's R22 table.
          ⛔ OMIT the ideo group (R23) unless this faction is the Hutt Cartel,
          whose text is already authored. It lands in a second pass from D18 and
          MUST be in before the worldgen click. `basicMemberKind` is OPTIONAL
          (R21) — do not invent one.
          🪤 `combatPower 99999` kinds are legal in `traders`/`carriers`/`guards`
          and POISON in `options`. `minTotalPoints` does not exist.
          `PawnGenOption` has exactly `kind` and `selectionWeight`.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; every `kind` named in a `pawnGroupMaker` resolves in the live def
          dump; `factionNameMaker` and `factionIconPath` are non-null.
criteria: the faction generates settlements at worldgen and its pawns spawn as
          the named kinds.
state:    ready

## B49 Create the Geonosian Foundry Hive as a new faction
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 8 for every field value, plus its "Namers and icons"
          and "pawnGroupMakers" tables for this faction. Model:
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`.
          Fill EVERY group in the contract — identity · generation · naming · art
          · hostility · pawns. A missing `factionNameMaker`, `factionIconPath`
          or `colorSpectrum` is a broken faction screen, not a cosmetic gap —
          `colorSpectrum` values are in the spec's R22 table.
          ⛔ OMIT the ideo group (R23) unless this faction is the Hutt Cartel,
          whose text is already authored. It lands in a second pass from D18 and
          MUST be in before the worldgen click. `basicMemberKind` is OPTIONAL
          (R21) — do not invent one.
          🪤 `combatPower 99999` kinds are legal in `traders`/`carriers`/`guards`
          and POISON in `options`. `minTotalPoints` does not exist.
          `PawnGenOption` has exactly `kind` and `selectionWeight`.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; every `kind` named in a `pawnGroupMaker` resolves in the live def
          dump; `factionNameMaker` and `factionIconPath` are non-null.
criteria: the faction generates settlements at worldgen and its pawns spawn as
          the named kinds.
state:    ready

## B50 Create the Ascendant Helix as a new faction
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 9 for every field value, plus its "Namers and icons"
          and "pawnGroupMakers" tables for this faction. Model:
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`.
          Fill EVERY group in the contract — identity · generation · naming · art
          · hostility · pawns. A missing `factionNameMaker`, `factionIconPath`
          or `colorSpectrum` is a broken faction screen, not a cosmetic gap —
          `colorSpectrum` values are in the spec's R22 table.
          ⛔ OMIT the ideo group (R23) unless this faction is the Hutt Cartel,
          whose text is already authored. It lands in a second pass from D18 and
          MUST be in before the worldgen click. `basicMemberKind` is OPTIONAL
          (R21) — do not invent one.
          🪤 `combatPower 99999` kinds are legal in `traders`/`carriers`/`guards`
          and POISON in `options`. `minTotalPoints` does not exist.
          `PawnGenOption` has exactly `kind` and `selectionWeight`.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; every `kind` named in a `pawnGroupMaker` resolves in the live def
          dump; `factionNameMaker` and `factionIconPath` are non-null.
criteria: the faction generates settlements at worldgen and its pawns spawn as
          the named kinds.
state:    ready

## B51 Create the Junkers as a new faction
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` section 12 for every field value, plus its "Namers and icons"
          and "pawnGroupMakers" tables for this faction. Model:
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`.
          Fill EVERY group in the contract — identity · generation · naming · art
          · hostility · pawns. A missing `factionNameMaker`, `factionIconPath`
          or `colorSpectrum` is a broken faction screen, not a cosmetic gap —
          `colorSpectrum` values are in the spec's R22 table.
          ⛔ OMIT the ideo group (R23) unless this faction is the Hutt Cartel,
          whose text is already authored. It lands in a second pass from D18 and
          MUST be in before the worldgen click. `basicMemberKind` is OPTIONAL
          (R21) — do not invent one.
          🪤 `combatPower 99999` kinds are legal in `traders`/`carriers`/`guards`
          and POISON in `options`. `minTotalPoints` does not exist.
          `PawnGenOption` has exactly `kind` and `selectionWeight`.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; every `kind` named in a `pawnGroupMaker` resolves in the live def
          dump; `factionNameMaker` and `factionIconPath` are non-null.
criteria: the faction generates settlements at worldgen and its pawns spawn as
          the named kinds.
state:    ready

## B44 Rename vanilla mechanoids to fit the setting
row:      9
spec:     `design/Jawa/worldbuilding/FACTION_SPEC.md` sections 13 and 14. Two `PatchOperation`s: `label` and
          `description` on `FactionDef[defName="Mechanoid"]` and
          `FactionDef[defName="Insect"]`. NOTHING ELSE.
          🔴 `hidden true` and `settlementGenerationWeight 0` on `Mechanoid` are
          CORRECT and stay — the Forgotten Arsenal is "a what, not a who".
          Both inherit their `pawnGroupMakers` wholesale.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; the diff touches exactly two fields per def.
criteria: the two factions read by their campaign names wherever they appear.
state:    ready

## B52 Fix our one existing faction — wrong name, six fields missing
row:      9
spec:     `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`, per `design/Jawa/worldbuilding/FACTION_SPEC.md`
          section 11. Change `label` "Jawa tribes" -> **"Jawa Trade Moot"** (R8
          retired the old name; R19 keeps the defName because it is deployed).
          Change `ParentName` `FactionBase` -> `TribeBase` (R24): the bare
          abstract supplies NONE of the naming or art fields and `TribeBase`
          supplies six of them.
          ADD what `TribeBase` still does not give: `humanlikeFaction`,
          `factionNameMaker` `NamerFactionTribal`, `settlementNameMaker`
          `NamerSettlementTribal`, `factionIconPath`
          `OuterRim/WorldObjects/MoistureFarmers`, `colorSpectrum` — and
          `basicMemberKind` is OPTIONAL (R21), so five fields, not six.
          ✅ SETTLED by BUILD: the group makers were always correct —
          `Combat`/`Peaceful`/`Trader` are `kindDef` (a `PawnGroupKindDef`) and
          the options always named our kinds. The three tribal kinds had never
          spawned for a different reason: all four pawn kinds named vanilla
          DEFNAMES as `ParentName` and were silently discarded at load. Fixed in
          `c06e89e`; CHECK C31 proves it on the next cold load.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs` scoped to the active list, 0 errors; all six fields present and non-null; the three Jawa_Tribal_* kinds
          appear in the group options.
criteria: Jawa Trade Moot settlements generate and spawn our tribal kinds.
state:    ready

## B53 Create 48 pawn types so raids field roles, not one flat kind
row:      7
spec:     `design/Jawa/worldbuilding/pawnkind_roster.md` — 48 kinds, 12 factions
          x Grunt/Heavy/Specialist/Leader, naming `Jawa_<Faction>_<Role>`.
          🔴 REQUIRED, not optional (R20): every donor kind is a flat species
          kind at `combatPower 40` — `OuterRim_Nikto`, `OuterRim_Wookiee`,
          `OuterRim_Geonosian`. There is no lieutenant, elite or specialist to
          borrow, so the dossiers' group compositions cannot be expressed
          without these.
          BLOCKED ON CHAIN STEP 3: `weaponTags` and `apparelRequired` are a
          selection from the surviving item set and cannot be invented. The
          roster says so itself and declined to guess them.
          `combatPower` is unset on all 48 and must be assigned.
verify:   `validate_patch.py --defs` 0 errors; every `weaponTags` string appears
          on at least one live weapon def; every `apparelRequired` defName
          resolves.
criteria: each faction's raids field the intended roles, not one flat kind.
state:    blocked

## B54 Add the faith text to the eleven factions, before worldgen
row:      6
spec:     `design/Jawa/worldbuilding/faction_religions_spec.md`. All eleven
          entries now carry an `### The engine-visible text` block with literal
          `<ideoName>` and `<ideoDescription>`. Copy them VERBATIM — they are the
          only strings the engine renders.
          `deityPresets` is required on entries 1 (two gods), 2 (one) and 3 (one)
          and FORBIDDEN on 4-11, whose structures carry `deityCount 0`.
          Add to each faction alongside `fixedIdeo` true, its `forcedMemes` from
          the entry's shell table, and `requiredPreceptsOnly` per that table.
          Never set `hiddenIdeo` — it suppresses the description entirely.
          Section 12 (Jawa) is deliberately empty; the player faith ships as
          `src/Jawa/ideoligion/The Salvation.rid`.
          ⚠️ Entry 5 (Free Droid Enclaves) may not run if the droid race is not
          Humanlike. Check before adding it; the other ten are unaffected.
verify:   `python3 src/RimMandrake/Utils/validate_ideoligion.py <xml>` VALID for
          each; then eyeball EVERY `<li>` for its `MayRequire` by hand — the
          validator reports a missing one as INFO only, and an unwrapped defName
          from a disabled mod is a silent no-op.
criteria: `jawa/ideo_of` reads the eleven back and the names and descriptions
          match the spec. 🔴 MUST land before the worldgen click — an ideo is
          generated once at world creation and cannot be retrofitted.
state:    ready

## B55 Build the campaign start — fixed map, fixed ship, fixed pawns
row:      12
spec:     `design/Jawa/worldbuilding/SCENARIO_SPEC.md`. The scenario is a SAVED
          GAME, not a `ScenarioDef` (R25) — no ScenPart can force named pawns
          with authored skills, and the owner is already shipping the world as a
          save. One artifact carries map, ship and crew.
          Your half, once the owner has made and saved the world:
          (a) place `design/Jawa/worldbuilding/ship_build/exported/Gravship_v1.xml`
              on the landing map;
          (b) 🔴 replay the layout's `terrainDef` cells through
              `jawa/set_terrain_batch` — floors do NOT come with a mid-game
              Sketch spawn and nothing errors when they are missing;
          (c) author the SIX founders with Character Editor to the exact
              skills, traits, passions, ages, workDisables and gear in the spec;
          (d) set the starting stock listed there — salvage-thin, no advanced
              components, no glitterworld medicine, no turrets.
verify:   all six pawns are `MandrakeJawa`, carry the robe and hood, and match
          the spec's skill and trait lines exactly; the deck has its floors.
criteria: the save loads into a playable colony aboard the ship. This IS chain
          step 12 and it is the artifact v1 ships.
state:    blocked

## B2 Install the ocean-shaping mod on its own, so blame stays clear
row:      v2
spec:     —
verify:   —
criteria: —
state:    dropped — Worldgen is manual (owner, 2026-08-14) and the sea left v1. Full text in `design/V2_DREAMS.md`.

## B6 Deploy the MandrakeJawa xenotype and indigenous-tribe set
row:      4
spec:     —
verify:   —
criteria: —
state:    dropped — The item claimed the set was undeployed; it was already deployed and verified. Live half carried by CHECK C31.

## B56 🔴 Five authored Jawa FactionDefs are DEAD — `<li>` in a dictionary-keyed field
row:      9
spec:     Found in the 2026-08-15 cold load. `xenotypeChances` is a DICTIONARY-KEYED
          field: the element name IS the xenotype defName. Five files use the `<li>`
          list shape instead, so `XenotypeChance.LoadDataFromXmlCustom` calls
          `ParseFloat` on a null string and the **entire FactionDef is discarded**.
          Log: `Exception loading def from file <X>.xml:
          System.ArgumentNullException: Value cannot be null. Parameter name: s`,
          stack `Single.Parse -> ParseHelper.ParseFloat ->
          XenotypeChance.LoadDataFromXmlCustom -> ParseAndReturnDef_RimWorld_FactionDef`.
          Affected, in `src/Jawa/Jawa_Patches/Defs/FactionDefs/` (li-entry counts):
          `JawaAscendantHelix.xml` 8 · `JawaHuttCartel.xml` 8 · `JawaJunkers.xml` 8 ·
          `JawaDeepwaterCompact.xml` 7 · `JawaWildsteamClan.xml` 6.
          `JawaTribes.xml`, `JawaFreeDroidEnclaves.xml` and
          `JawaGeonosianFoundryHive.xml` have zero `<li>` under `xenotypeChances`
          and do NOT throw — that correlation is the proof.
          FIX — rewrite each entry from
            `<li MayRequire="btd.xenotyperemix.starwars"><xenotype>RimMandrakeNikto</xenotype><chance>0.300</chance></li>`
          to
            `<RimMandrakeNikto MayRequire="btd.xenotyperemix.starwars">0.300</RimMandrakeNikto>`
          `MayRequire` is an attribute and rides on the keyed element unchanged.
          See `skills/rimworld-modding/SKILL.md` §4 — this is the documented
          most-destructive mistake, and `references/patch-operations.md` §11.
          INTRODUCED BY `16f838b` (2026-08-14 23:52, "R27: the seven factions field
          their own species, not Hussars"). The 23:11 load before it shows zero Jawa
          faction exceptions.
          ⚠️ IT ALSO COSTS LOAD TIME. `ordpus.logafterdeferror` dumps ~19,613
          "Possible Matches" lines per unattributable error: 5 × 19,613 ≈ 98,000 of
          this load's 99,700 lines and ~8 MB written to C: with per-line flush.
          Previous load: 34 Possible Matches, 15,280 lines. Fixing the five defs
          removes ~98% of the log volume as well as restoring the factions.
verify:   `python3 skills/rimworld-modding/scripts/validate_patch.py` on each of the
          five, pointed at the mod ROOT so it scans `Defs/`. Then re-deploy and grep
          the next Player.log: zero `Exception loading def from file Jawa*.xml`.
criteria: All 8 Jawa factions resolve live — `jawa/get_def` or the def dump returns a
          FactionDef for each of the five, where today it returns nothing.
state:    dropped — Mechanitors are cut from the campaign entirely (owner, 2026-08-15), so the empty `Autopistol` tag has no consumer left. `AM_Scavenger` is Ancient urban ruins' own kind and rides that mod's content.

## B56 Give the Mechanitor a blaster — the autopistol is gone
row:      1
spec:     Chain step 1 cut 74 conventional firearms into Cherry Picker, including
          Core's `Gun_Autopistol`. That empties the vanilla `Autopistol` weapon
          tag, and three pawn kinds ask for it: `Mechanitor` and
          `Mechanitor_Basic` (Biotech) and `AM_Scavenger` (Ancient urban ruins).
          **A pawn kind whose only weapon tag resolves to nothing spawns
          unarmed**, silently.
          Fix: `PatchOperationAdd` the tag `Autopistol` onto
          `ThingDef[defName="guy762_bpistol"]`'s `weaponTags` — KotOR's generic
          blaster pistol, already the weak-tier sidearm. Wrap the op in
          `MayRequire="guy762.kotorweapons"`.
          ⇒ Mechanitors arrive carrying a blaster pistol, which is better fiction
          than an autopistol was.
          ⚠️ Four other tags were emptied — `AM`, `AMGuns`, `AMHP`, `PKM` — but
          all belong to Ancient urban ruins' own kinds (`AncientSoldierBoss`,
          `AncientSoldierBossN`, `AncientMallGuards`). Those spawn only inside
          that mod's own content. Report if you see them unarmed; do not fix
          pre-emptively.
verify:   `validate_patch.py --defs` 0 errors; `guy762_bpistol` carries
          `Autopistol` in the live dump; no other def claims that tag.
criteria: a Mechanitor event spawns its pawn holding a blaster pistol, not
          empty-handed.
state:    ready

## B57 The lasso becomes a strength gene, not a weapon anyone can pick up
row:      5
spec:     Owner design, 2026-08-15. Lassos are absurdly strong for melee pawns.
          Gate them by WHO IS WEARING one, not by who may equip one — RimWorld
          has no xenotype restriction for apparel (the whole vocabulary across
          886 apparel defs is `gender`, `developmentalStageFilter`,
          `slaveApparel`, `mechanitorApparel`; there is no `requiredGene`).
          THE SHAPE: a Jawa can pull someone a few tiles — a RESCUE tool, mostly
          for yanking a friend out of danger. A Wookiee can pull someone from far
          away, into a pummelling. Same item, different wearer.
          The lassos are apparel from `Melee Animation` — waist slot, layer
          `AM_Hip`, tag `Lasso`, `equipmentType` None — so they cost no weapon
          slot. That is part of why they are strong.

          (a) LOWER THE BASELINE. `StatDef[defName="AM_GrappleRadius"]`
              `defaultBaseValue` **10 -> 4**. Four tiles is a rescue pull.
              Leave `minValue 1`.
          (b) SHRINK THE TIER LADDER so material is not the deciding factor:
              `AM_LassoCloth`        `AM_GrappleRadius` +0   (add the offset explicitly; it currently has NONE)
              `AM_LassoDevilstrand`  +8 -> **+2**
              🔴 `AM_LassoHyperwave` is CUT from v1 (owner, 2026-08-15) — two
              tiers only. Do not patch it; it will not load.
          (c) AUTHOR THE GENE — `Jawa_Gene_PowerfulGrapple`, in
              `src/Jawa/Jawa_Patches/Defs/GeneDefs/`. Model it on Biotech's
              `MeleeDamage_Strong` (same `statOffsets` shape).
                  statOffsets: AM_GrappleRadius +12
                               AM_GrappleSpeed  +0.5
                               AM_GrappleCooldown -8
              label "mighty grapple"; description in the campaign's voice.
              ⚠️ `AM_GrappleSpeed` is capped at `maxValue 10` and
              `AM_GrappleCooldown` at `minValue 0.5` — do not exceed either.
          ⇒ RESULT: Jawa with either lasso reaches 4-6 tiles. A carrier of the gene
            reaches 16-20. The GENE is the deciding term, which is the design.
          🔴 DO NOT ATTACH THE GENE TO ANY XENOTYPE. Authoring it is yours;
          deciding who carries it is `D23`, which rebuilds our xenotype set.
          Default intent on record: Wookiee and Wookiee-kin (Yttakin) certainly;
          other large, strong races are the owner's call.
          ⚠️ Wrap every op touching a `Melee Animation` or Biotech def in the
          correct `MayRequire` — an unwrapped defName from a disabled mod is a
          silent no-op.
verify:   `validate_patch.py --defs` 0 errors; the three lassos read the new
          offsets in the live dump; `Jawa_Gene_PowerfulGrapple` resolves and its
          three stat offsets are present.
criteria: a Jawa wearing a lasso pulls a pawn ~4 tiles; a gene-carrier pulls one
          from ~16. Both readable from the pawn's stat panel.
state:    ready

## B58 🔴 `OuterRim_Jawa` no longer exists — our patches still target it
row:      7
spec:     Found in the 2026-08-15 08:12 load harvest. Switching the three donor
          mods off and `mandrake.starwarsraces` on RENAMED the Jawa pawn kinds and
          xenotypes. The old names survive nowhere as defs — only as dangling
          references inside `InteractionDef.json`.
          LIVE NAMES, from the 08:09:57 def dump at 576 mods:
            PawnKindDef  `RimMandrake_Jawa` · `RimMandrake_JawaTribal` ·
                         `RimMandrakeJawa_Kind`
            XenotypeDef  `RimMandrakeJawa` · `MandrakeJawa`
          GONE: `OuterRim_Jawa`, `OuterRim_JawaTribal`.
          WHAT ACTUALLY FAILED THIS LOAD (Player.log :804-:807):
            `PatchOperationAdd(xpath="/Defs/PawnKindDef[defName="OuterRim_Jawa"]")`
            — Failed to find a node with the given xpath, then the enclosing
            `PatchOperationConditional(.../apparelRequired)` errored in `<nomatch>`.
            Source: `Jawa_Patches/Patches/SpeciesStartingGear_Tuning.xml`.
          ⇒ **Jawa starting-gear tuning did not apply.** That feeds chain step 12,
          the campaign start.
          Files naming the dead defName, all needing the audit:
          `Jawa_Patches/Patches/SpeciesStartingGear_Tuning.xml` ·
          `Jawa_Patches/Patches/JawaXenotype_Repoint.xml` ·
          `Jawa_Patches/Defs/FactionDefs/JawaJunkers.xml` · and 10 files under
          `JawaVoice/Patches/` (interactions, insults, romance, prisoners, etc).
          ⚠️ JawaVoice's ops still report at baseline 2, so check whether its
          references are guarded or silently doing nothing — a no-op logs nothing.
verify:   `grep -rl OuterRim_Jawa src/Jawa/` returns only prose/About files, and
          `validate_patch.py --defnames <the 08-15 dump>` reports 0 errors on the
          three Jawa_Patches files.
criteria: Next load's harvest shows `Jawa_Patches ops` back at baseline 0, and a
          spawned Jawa carries the tuned starting gear.
state:    ready

## B59 The MegafaunaYield fix did not apply — its FindMod guard missed
row:      infra
spec:     `Jawa_Doctrine/Patches/MegafaunaYield.xml`:
          `PatchOperationFindMod(Dark Ages : Beasts and Monsters) failed`
          (Player.log :796-:802, 2026-08-15 load). That mod is not in the 576-mod
          list, so the yield fix is inert. Decide whether the mod is meant to be
          absent — in which case the patch should be retired or its guard made
          silent — or whether it was dropped by mistake and should come back.
          Harvest calls this "THE must-confirm", so it has been believed to work.
verify:   Either the file is gone, or its guard no longer fails against the live
          list.
criteria: Harvest shows `MegafaunaYield fix` at baseline.
state:    ready

## B60 Make every plant on the planet grow freakishly fast
row:      2
spec:     `design/Jawa/worldbuilding/PLANT_GROWTH_SPEC.md` is the authority; the
          load-bearing points, so you need not open it to start:
          **R-G1 — one Harmony postfix, not an XML sweep.** `PatchOperation`s
          cannot do arithmetic (there is no `PatchOperationMultiply`), so XML
          means writing a literal `growDays` on all 566 plant defs, brittle and
          blind to any plant a mod adds later. Instead ONE postfix on
          `Verse.Plant.GrowthRate` multiplying `__result` — it catches every
          plant from every mod and is one line to tune or revert. The boosted
          number must show in the inspect string, not the base one.
          ⚠️ **Verify the Harmony target against the assembly before writing the
          patch** — `strings -a -el` on `Assembly-CSharp.dll`, per the project's
          standing rule never to guess a member. The spec says `GrowthRate` is a
          property getter in 1.6; do not take that on trust. If it is not the
          single funnel, target whatever `GrowthPerTick` consumes.
          **R-G2 — three bands, as named constants in ONE config class**, not
          scattered literals: default (wild plants and crops) **x4.0**, trees
          **x2.5** (wood must stay a decision), terminator/poison-forest biomes
          **x0.4**. The owner will tune these after seeing them move, and tuning
          must not mean recompiling. ⛔ Do NOT exempt player crops — the fiction
          is planetary, and the limit on farming here is WATER, not time.
          **R-G3 — the postfix is biome-aware**, and the terminator biome set is
          a `List<string>` in the same config, NOT a hard-coded defName.
          `PoisonForest` and its Advanced Biomes relatives are the current
          candidates; DECIDE supplies the final roster, and it must be able to
          change without a rebuild.
          **R-G5 — a named exempt list in the same config**, reasoning visible
          beside the multipliers: `Plant_TreeAnima` (ritual pacing, not botany),
          `Plant_TreeGauranlen` and the dryad economy, `Plant_Ambrosia`, plus
          anything a quest or ritual times against and any plant already under
          ~1 `growDays`.
          🔴 **R-G1 ships NOW; R-G4 WAITS.** The second lever is XML on
          `BiomeDef.wildPlantRegrowDays` (divide by ~4, to agree with R-G2) and
          it is blocked on the owner's biome cut list — patching a biome about
          to be cut is wasted work. Both levers are ultimately required: fast
          growth without fast regrowth burns the savanna once and leaves it
          black.
          SHIPPED: `src/Jawa/JawaPlantGrowth/` (`mandrake.jawaplantgrowth`).
          R-G1 only; R-G4 still blocked on the biome cut list.
          🔴 NOT DEPLOYED — RimWorld was running and the DLL cannot be written to
          a locked game folder. Needs `deploy_custom_mods.py --mod JawaPlantGrowth
          --apply` in a shutdown window plus a ModsConfig entry AFTER
          `brrainz.harmony`. Live half is CHECK C38.
verify:   Per R-G6, all of it inside a ~90 s quicktest — do NOT wait for a cold
          load. Wild grass visibly regrows within a session and a sown crop
          reaches harvest in roughly a quarter of its usual time. A tree does
          NOT keep pace with the grass (that is the x2.5 band working). 🔴 The
          check most likely to be skipped, and the one that proves the
          biome-aware branch actually runs: on a terminator/poison-forest map
          growth is visibly **SLOWER** than vanilla, not faster. The anima tree
          is unchanged. No error on load and no per-tick performance regression
          on a large map — a getter postfix runs extremely often.
criteria: vegetation reads as obtrusively powerful rather than as a balance
          tweak.
state:    done

## B61 Make the frozen Ancients look Rakatan
row:      4
spec:     `design/Jawa/worldbuilding/ANCIENTS_AS_RAKATA_SPEC.md` is the authority;
          the load-bearing points, so you need not open it to start:
          **The owner has ruled the ancient sleepers ARE the Rakata**
          (`the_forgotten_war.md` R-W2 ③ / R-W5). Vanilla's Ancients generate as
          plain humans, so the whole beat lands on a pawn that looks like a pirate.
          This is an APPEARANCE change to PAWNS only.
          🔴 **R-A1 — the xenotype is `RimMandrakeRakata`, NOT `RimMandrakeRakata`.**
          `RimMandrakeRakata` does not exist in ANY def type anywhere in the live dump —
          zero grep hits, control `RimMandrakeRakata` hits 7 files. `FACTION_SPEC.md`
          R27 and `the_forgotten_war.md` R-W3 both name it; both are broken
          references and DECIDE is fixing them. If you see `RimMandrakeRakata` while
          working it is a bug to report, never a name to use.
          **R-A2 — six pawn kinds.** Mandatory: `AncientSoldier` (Core) and
          `AncientSoldier_Leader` (Odyssey). Also in scope, guarded on
          `Ancient urban ruins`: `AncientSoldierBoss`, `AncientSoldierBossN`,
          `AncientMallGuards`, `AncientSlaughter` — all four carry
          `defaultFactionDef AncientsHostile`, same faction and same fiction, and
          two Rakatan pawns beside four human ones reads as a bug. Do NOT touch
          `ABYautja_Ancient`, `BS_Troll_Simple_Ancient`, `QP_AncientShaman`,
          `VRE_AncientFungoid` — unrelated content that merely matches the string.
          **R-A3 — `RimMandrakeRakata` at chance `1.0`, alone, PLUS
          `useFactionXenotypes false`.** All six are `true` today and the faction
          fallback is not empty: `Ancients` carries `DV_Avaloi 0.15` and
          `AncientsHostile` `DV_Avaloi 0.10`, injected by `det.avaloi`. One ancient
          soldier in ten is already an Avaloi.
          🔴 **R-A4 — TWO XML TRAPS, BOTH ALREADY SHIPPED BROKEN IN THIS REPO.**
          (a) `xenotypeChances` is DICTIONARY-KEYED: the element name IS the
          defName. The `<li><xenotype>…</xenotype><chance>…</chance></li>` shape
          makes `ParseFloat` throw on null and **the whole Def is discarded** —
          that is B56, which killed five Jawa FactionDefs. Write
          `<RimMandrakeRakata MayRequire="mandrake.starwarsraces">1.0</RimMandrakeRakata>`.
          ⚠️ **`FACTION_SPEC.md` R27's own worked example uses the `<li>` shape and
          is WRONG — do not copy it.** Vanilla `PawnKinds_Spacer.xml` is the model.
          (b) 🔴 **`xenotypeSet` INHERITS — a child's list is APPENDED to the
          parent's, not substituted** (R24a + R27, already shipped broken once).
          Live proof: `AncientSoldierBoss` is declared `<PawnKindDef Name="AMBossBase">`
          carrying `Neanderthal 0.03`, and `AncientSoldierBossN` is
          `ParentName="AMBossBase"` with no set of its own. Patch it without
          `Inherit="False"` and you ship a pawn that is 97% Rakatan and 3%
          Neanderthal — no crash, no log line, just SOMETIMES right. Put
          `Inherit="False"` on **both** `<xenotypeSet>` and `<xenotypeChances>`;
          it is a harmless no-op where there is no parent.
          **R-A4 (op shape) — Remove-then-Add, not Add.** `AncientSoldier` and
          `AncientSoldier_Leader` have NO `<xenotypeSet>` node in source; three
          others do; and `xylthixlm.races.titan` is already patching
          `AncientSlaughter` (it resolves live with a `XylTitan 0.025` that is not
          in the mod's own file). Use a `PatchOperationSequence` per kind:
          `PatchOperationRemove` on `…/xenotypeSet` with `<success>Always</success>`,
          then `PatchOperationAdd`. `mandrake.jawa.patches` loads after all of them,
          so our Remove runs last and wins.
          **R-A5 — also patch the two faction defs** `Ancients` and
          `AncientsHostile`, same shape. Catch-all for kinds we did not enumerate,
          and it removes the Avaloi. Belt-and-braces: if it is dropped the six
          kinds must still work.
          **R-A6 — guards, and a guard that "passes" proves nothing.**
          `MayRequire` takes a packageId (`mandrake.starwarsraces`,
          `Ludeon.RimWorld.Odyssey`); `PatchOperationFindMod` takes the display
          name (`Ancient urban ruins`). Standing project fact: FindMod and
          Conditional BOTH return true on no match, so **"no errors in the log" is
          NOT a pass** — only the def dump reading back, then a pawn on a map.
          **R-A7 — NOT a faction change.** `Ancients` is hidden,
          settlementGenerationWeight 0, canMakeRandomly false and cannot host a
          faction (FACTION_SPEC R9). ⛔ Do not touch `hidden`,
          `settlementGenerationWeight`, `canMakeRandomly`, `permanentEnemy` or any
          relations field. The faction patch touches `xenotypeSet` and nothing else.
          **R-A8 — appearance only.** These kinds drive ancient danger,
          cryptosleep caskets and quests. ⛔ Do not alter `combatPower`,
          `apparelMoney`/`apparelTags`, `weaponMoney`/`weaponTags`,
          `techHediffs*`, `itemQuality`, traits, backstory filters, `race` or
          `defaultFactionDef`. **The diff per kind is exactly two things.**
          ⚠️ DO report one number: the aggregate `statOffsets`/`statFactors`/
          `capMods` across the 21 genes. `combatPower` is static and will not
          follow. Report it here; DECIDE rules, you do not change it.
          **R-A9 — labels stay as they are.** Whether "ancient soldier" becomes
          something Rakatan is 🟡 the owner's call and would be a SEPARATE item.
          Ship the no-change default.
          **R-A10 — one new file**,
          `src/Jawa/Jawa_Patches/Patches/AncientsAreRakata.xml`. Do not edit an
          existing patch. Writing it is not deploying it —
          `deploy_custom_mods.py --mod Jawa_Patches --plan` then `--apply`.
          ✅ **GRAPHICS ARE ALREADY PROVEN ON DISK — do not re-derive.** All 21
          genes resolve. The two appearance-bearing ones are real art under our own
          mod: `RimMandrake_RakatanHead` forces `HeadTypeDef RimMandrake_Rakatan`
          whose three sides are on disk (`…/Heads/Rakatan/Normal_{south,east,north}.png`,
          20.5/18.3/17.2 KB), and `RimMandrake_Body_gaunt` maps via
          `RimMandrake_FurDef_gaunt` to `…/SWX/Pawn/BodyType/Gaunt_{south,east,north}.png`.
          The three `Outland_Skin_*` genes are `skinColorOverride` — colour only,
          no texture needed, and that is the healthy state. `Hair_BaldOnly` and
          `Beard_NoBeardOnly` are tag filters and declare no body art by design.
          The other 12 are stat/psychic/diet genes and all 12 icons resolve too.
          ⚠️ `RimMandrake_FurDef_gaunt` has `noGraphic: true` — **do not chase
          it**; all 30 FurDefs in the stack carry it, including Biotech's own.
verify:   🔴 A quicktest, ~90 s. Do NOT call a cold load — nothing here needs
          worldgen. Four tiers, all required.
          **T1 the def changed.** `refresh.py`, then read back:
          `AncientSoldier.xenotypeSet.xenotypeChances` == exactly ONE entry,
          `RimMandrakeRakata` at 1.0 — **not two**; `useFactionXenotypes` false;
          same for the other five; `Ancients`/`AncientsHostile` no longer list
          `DV_Avaloi`. 🔴 **`AncientSoldierBossN` is the canary** — it is the one
          with the Neanderthal-carrying parent. Two entries means the R27 trap bit
          again.
          **T2 it generates.** Spawn ≥5 `AncientSoldier` via the bridge. Every one
          Rakata; none Baseliner, Neanderthal, Hussar or Avaloi. Five, not one — a
          3% contaminant does not show in a sample of one.
          **T3 it RENDERS, and this one cannot be skipped.** Look at the pawn with
          eyes: Rakatan head not a vanilla human head, no pink/blank placeholder,
          skin one of the three browns/oranges, gaunt silhouette. Screenshot and
          put the path in this item. A file existing on disk is not this check.
          **T4 nothing else moved.** Gear roll unchanged, an ancient danger room
          opens and populates normally, zero `Exception loading def from file
          AncientsAreRakata.xml` and zero `Could not resolve cross-reference`
          naming `RimMandrakeRakata`.
          Validator: `validate_patch.py` on the new file pointed at the mod ROOT,
          with BOTH `--live` and `--defs`.
          📌 If T1 is clean but T2/T3 show a non-Rakatan, suspect
          `bs.xenotypespawncontrol` first — a runtime override leaves the dump
          looking perfect.
criteria: the player cracks an ancient cryptosleep casket and what climbs out is
          visibly not human, and the encounter plays exactly as it did before.
state:    ready

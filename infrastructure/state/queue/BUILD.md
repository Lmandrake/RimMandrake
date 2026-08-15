# BUILD inbox.

## B-V2 Park any v2 idea in design/V2_DREAMS.md yourself — no permission needed
row:      infra
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
row:      infra
spec:     Correct §11 of `gravship_flight_invariants.md` to the measured facts. The export holds **zero thrusters, zero tanks, zero consoles**. The format has **no roof field**, but roofs are derivable: GravshipExport regenerates them at import by flood-fill (`Patch_Sketch_GetSuggestedRoofCells_Postfix.cs:45-85`) => **4,049 of 4,057 substructure cells roofed, every standable cell indoors**. There is **no stern re-lay**: the cost is ONE `GravshipHull` cell per small thruster (two per large), because `ThrusterBase` is `holdsRoof true` + `fillPercent 1` and seals the room exactly as the wall it replaces. Nine sites at x41–49, z131/132; the aft strip (x,133) is off-deck.
verify:   §11 states those measurements and marks the roof map as DERIVED (the mod's own algorithm re-run), not observed.
criteria: EMPTY
state:    ready

## B21 Make our mod checker notice a mod that is listed but not installed
row:      infra
spec:     The `ModsConfig.xml` listed-but-missing trap in code form: `loadset_fingerprint()` compares *listed* against *exists*.
verify:   a synthetic `ModsConfig.xml` listing a packageId that is not on disk is reported, not silently passed.
criteria: EMPTY
state:    done

## B22 Teach the patch validator to spot a rule that can never fire
row:      infra
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
row:      infra
spec:     (a) Pin the 6 `loadBottom`+`loadAfter` userRules — order is correct today but rides a tie-break, not a constraint; `loadBottom` outranks `loadAfter`, keep it only on `rimdefdump`. (b) Run `src/RimMandrake/Utils/refresh.py` (wants the game down). (c) **O-v2 Cherry Picker** — remove mechanoid defs AND the `Mechanoid` faction; answer three things: does the game still load · does `Samael.NPCMechsAndAnimals` survive and keep its ANIMALS half (`Patches/NPC_Mechs.xml`, 13 ops into `Empire`/`Outlander*`/`Pirate*`/`TradersGuild`) · is that mod configurable. Do NOT remove Alpha Mechs (`sarg.alphamechs`). `matathias.ruthlessmechanoids` is NOT a mech mod (it is the gravship pursuer redirect) — leave it on. REPORT, do not resolve: Alpha Mechs hangs off `FactionDef[defName="Mechanoid"]/pawnGroupMakers`, so cutting that faction takes its raids too. (d) **O-v3** — enable `vanillaexpanded.vwel` (ws `1989352844`, installed and inactive) and dump its weapon `ThingDef`s in TWO SEPARATE tiers: `salvaged` (pistol/rifle/shotgun/sniper + `unstable` projectile variants) and `ultratech` (incl. a laser sword and a tesla gun). The split is load-bearing for the design (`design/Jawa/worldbuilding/ship_legacy_armoury.md`).
verify:   read `ModsConfig.xml`'s mtime before writing — RimSort writes it too, and it moved twice in twenty minutes with the game down.
criteria: the game reaches the main menu with the new list; the two weapon tiers exist as separate dumps.
state:    ready

## B26 Delete the retired art-fix mod now that its replacements ship
row:      infra
spec:     Already dropped from `ModsConfig.xml`; all 7 textures are md5-identical to the per-donor successors and the blocking dependency is cleared. Remove the deployed copy under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\` and the repo folder.
verify:   neither path exists.
criteria: EMPTY
state:    ready

## B27 Repackage the skills — editing the folder does not ship them
row:      infra
spec:     `python3 src/RimMandrake/Utils/package_skill.py --all`. Editing `skills/<name>/` is not shipping it — Claude Code installs from a `.skill` zip and those are gitignored, so a fresh clone has none. `skills/rimworld-quests.skill` (65 KB) is one that exists only on disk.
verify:   read the EXIT CODE and the named failure list, never the directory listing — a failure leaves its own zip stale beside fresh ones.
criteria: EMPTY
state:    done

## B34 Fix a wrong mod ID cited across the design docs
row:      infra
spec:     WS `3530586159` is cited as adopted in several design docs but is NOT installed — a grep of all 1246 workshop `About.xml` files matches only the original `2896845138`, which is active and supplies every `GarryFlowers_` def in use.
verify:   grep of the design docs returns no `3530586159`.
criteria: EMPTY
state:    done

## B35 Move the repo to the agreed folder layout, one stage per commit
row:      infra
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` — ten stages, ONE commit each, lowest-risk first. Stage 9 (`skills/`) is owner-gated and may never run. §3's seven unplaced items need a ruling before stage 4.
verify:   run `src/RimMandrake/Utils/check_refs.py` and `src/RimMandrake/Utils/doc_budget.py` after EVERY stage; §8 names the check that proves a stage landed whole.
criteria: EMPTY
state:    blocked

## B36 Rename the mods and tool namespace — 35 files and the load order
row:      infra
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` §7. `JawaBench.BridgeTools` -> `RimMandrake.Bridge` (14 tracked files, 4 identities including the deploy folder). The `jawa/<tool>` namespace: 35 tracked files at once, canonically 17 `[Tool]` attributes in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`, 3 of the 35 being generated JSON. The five `Jawa*` mod folders. All five packageIds ARE active in `ModsConfig.xml` (lines 560–571 of 575) => a load-order edit at a specific slot plus a RimSort rules edit, not a `sed`.
verify:   `check_refs.py` clean; `ModsConfig.xml` slots preserved.
criteria: the game loads with the renamed mods at the same load positions.
state:    blocked

## B37 Two docs cite files that no longer exist — find or retire the evidence
row:      infra
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

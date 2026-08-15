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
verify:   md5 of the deployed DLL equals `d7e7c6c1`, and `fire_incident` +
          `send_letter` are present in the deployed bytes (`strings -a -el`).
criteria: `rimbridge/list_tools` counts 30 `jawa/` names.
state:    done — deployed 2026-08-15 by B1's build; see CHECK.md. md5 is
          `f0d4e6e7`, NOT `d7e7c6c1`: `--apply` rebuilds at the current commit,
          so this verify's md5 clause is unsatisfiable by design. B1 supersedes
          it — gate on the count and the two canaries.

## B1 Build and install the bridge tools — without --gm, two tools vanish
row:      10
spec:     `cd /mnt/d/Luke/dev/Rimworld; python.exe src/RimMandrake/bridgetools/build.py --gm --apply`. Game must be DOWN — the DLL is locked while it runs and the write fails `OSError 22` (the refusal is safe, it cannot truncate). Without `--gm` the build STRIPS `jawa/fire_incident` and `jawa/send_letter` off the game copy (30 tools -> 28). One-command form: `./src/RimMandrake/Utils/shutdown_deploy.sh [--yes]` runs S8 -> S1 -> S9 in order and refuses while RimWorld is running.
verify:   `D="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/BridgeTools/JawaBench/JawaBench.BridgeTools.dll"`; `md5sum "$D"` expect `d7e7c6c1...`; `strings -a "$D" | grep -oE 'jawa/[a-z_]+' | sort -u | wc -l` expect **30**; both `--gm` canaries `jawa/fire_incident` and `jawa/send_letter` present. `--apply` REBUILDS before deploying, so a rebuild legitimately produces different bytes — gate on the canaries and the count, not on the md5. Census expectation derives from `.cs` ONLY: `grep -rhoE '"jawa/[a-z_]+"' --include='*.cs' src/RimMandrake/bridgetools/` (without the include it returns one too many — `prove_new_tools.py:112` has `[Tool("jawa/x")]` inside a comment). `strings -a` proves a NAME only; use `strings -a -el` to prove a method-body message shipped (UTF-16LE in the `#US` heap).
criteria: five tools respond live — `jawa/set_faction_relation` (unblocks v1 L3), `jawa/inspect_string` (reads `Thing.GetInspectString()`: `WarningThrusterInside`, `ThrusterBlockedBy`, power, breakdown), `jawa/world_stats` unit fix (`perimeterTiles`, `raggedness` from tiles, `centroidLatNorm`), `jawa/ideo_of`, `jawa/biome_probe`. `TicksGameSafe()` rides along: def reads must work at `programState: Entry` instead of throwing a bare NRE on every tool at the main menu.
state:    done — offline verify passed 2026-08-15; criteria are live and belong to CHECK.

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
state:    done 2026-08-15 15:52, `6572c85` — but NOT as written. The spec says
          "the worldgen load"; worldgen is the owner's and is not scheduled, so the
          signatures went into a NEW block **§3**, for the deploy-window load that is
          launching now. §2 (worldgen) keeps its own S7/S8 and stays OPEN.
          🔴 §3's T4 REVERSES §2's S8 on one row: with `btd.xenotyperemix.starwars`,
          `guy762.starwarsxenotypes` and `neronix17.outerrim.galacticdiversity` all
          absent from `<activeMods>`, a `BTD_`/`guy762_`/`OuterRim_` crossref is a
          C36 FAILURE, not a benign line. S8 called it harmless when the donors were
          installed. Anyone reading S8 for this load will mis-triage it.

## B25 Mod-list chores to do in one pass while the game is closed
row:      0
spec:     (a) Pin the 6 `loadBottom`+`loadAfter` userRules — order is correct today but rides a tie-break, not a constraint; `loadBottom` outranks `loadAfter`, keep it only on `rimdefdump`. (b) Run `src/RimMandrake/Utils/refresh.py` (wants the game down). (c) ⛔ **DEPRECATED — owner's ruling 2026-08-15: "We are keeping the mechanoids. Deprecate any action about turning mechanoids off."** Do not run it, do not revive it, do not re-derive it from the O-v2 line in any other doc. The former spec (Cherry Picker removal of the mechanoid defs and the `Mechanoid` faction) is dead; the guards it carried are now moot but were: keep Alpha Mechs `sarg.alphamechs`, and `matathias.ruthlessmechanoids` is the gravship pursuer redirect, not a mech mod. Per-mech ART curation against `design/Jawa/worldbuilding/review/mech_register.html` is a SEPARATE question and is still the owner's to make — this ruling kills the wholesale cut, not that review. (d) **O-v3** — enable `vanillaexpanded.vwel` (ws `1989352844`, installed and inactive) and dump its weapon `ThingDef`s in TWO SEPARATE tiers: `salvaged` (pistol/rifle/shotgun/sniper + `unstable` projectile variants) and `ultratech` (incl. a laser sword and a tesla gun). The split is load-bearing for the design (`design/Jawa/worldbuilding/ship_legacy_armoury.md`).
verify:   ~~read `ModsConfig.xml`'s mtime before writing~~ — RETIRED by the owner
          2026-08-15 (`0460ee4`, now in CLAUDE.md): *"You NEVER have to ask if
          RimSort is open. It does not autosave, and I will never save without
          asking. Nobody blocks on RimSort or game close for config files of any
          kind."* Write it, game up or down. Assemblies are the only thing that
          needs the game down, because the OS locks them.
          Real verify: `ModsConfig.xml` parses, the activeMods count moves by
          exactly the intended delta, and zero listed-but-missing
          (`src/RimMandrake/Utils/check_load.py`).
criteria: the game reaches the main menu with the new list; the two weapon tiers exist as separate dumps.
state:    ready — (b) DONE 2026-08-15 (`4c2ddf8`): offline artefacts stamped at
          fingerprint `7256c128a43117a5`. Two restructure faults fixed to get
          there; see the commit. 🔴 **Run `refresh.py` under `python.exe`, not
          `python3`** — WSL's python3 is PEP-668 externally-managed and has no
          Pillow, so the contact-sheet step exits 1; the Windows interpreter has
          Pillow 12.3.0. The live DefDump is still STALE and needs the load.
          🔴 (b) re-run 2026-08-15 15:51, AFTER this window's list edit, per
          NEXT_RELOAD §1.0 step 6: listed 575, resolved 575/575. Live dump is
          STALE against the new set (+`mandrake.jawaplantgrowth`,
          −`com.yayo.yayoani.continued`, −`regrowth.botr.boilingforest`) and
          `dump_request.txt` is armed `all`, so this startup refreshes it.
          🔴 **The old hold reason on (a)/(d) was WRONG and is deleted** — it read
          "the owner has not said whether RimSort is open". The owner ruled
          2026-08-15 that NOTHING blocks on RimSort or on the game for a config
          file (POLICY.md). (a) is not held, it is simply POST-LOAD work
          (NEXT_RELOAD §9). (d) enables a mod and is a list change nobody has
          scheduled into this window — it needs DECIDE, not a window.
          Also done this window: `com.yayo.yayoani.continued` removed from
          `<activeMods>`, 576 → 575 (the standing §1b change). ⚠️ The file spells
          it lowercase `yayoani`; a case-sensitive grep for `yayoAni` reports it
          absent when it is live. (c) untouched, and dead by owner's ruling.

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
          **575**, loaded 575, zero listed-but-missing, zero loaded-but-unlisted
          (553 workshop · 16 local · 6 Core+DLC, re-measured 2026-08-15).
          ⚠️ This spec said **585** until 2026-08-15; that number is dead —
          585 − 11 + 1 = 575, every one attributable to a commit in `V1_CHAIN.md`.
          Do NOT re-audit 575 mods. Emit ONE table of DIVERGENCES only, joining
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
state:    blocked — **but the reason changed 2026-08-15 and the hard blocker is GONE.**
unblock:  🔴 **OWNER FROZE THE CHERRYPICK AND CLOSED CHAIN STEP 1.** The stated blocker
          above — *"`weaponTags` and `apparelRequired` are a selection from the surviving
          item set and cannot be invented"* — **no longer holds. That set is now FIXED**
          (1,308 Cherry Picker keys; armour, weapons, items and beasts all done) and
          nothing further will cut from it. There is no longer a risk that authoring
          these 48 kinds today is invalidated by a later category pass.
          ⇒ What remains is chain step 2/3 work over a frozen set — a balance pass and a
          tag assignment — **not a discovery problem**. `combatPower` is still unset on
          all 48 and still must be assigned; that was always ours, not the cherrypick's.
          ⚠️ **I am not flipping this to `ready` myself**: step 3's artifact (which tags a
          `PawnKindDef` actually consumes) is still unwritten, and BUILD bounces items
          whose spec would have to be guessed. **DECIDE owes step 3's spec, then this
          goes ready.** Filed so nobody re-derives the old blocker and re-parks it.

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
state:    DONE 2026-08-15 — both halves. CHECK collected the live half off this
          load (575 mods, 1.6.4871 rev591): **zero** `Exception loading def from
          file Jawa*.xml`, and **8/8** faction defNames resolve via
          `jawa/get_def defType=FactionDef`. The log's only two def-load exceptions
          are third-party (`ElectricTorches_DarkAgesCrypts_Thoughts.xml`) and are
          the already-known baseline.
          ⛔ **SCOPED, and do not let it close wider than its evidence:** this is a
          QUICKTEST map. It proves the five FactionDefs LOAD. It says nothing about
          which factions a generated world contains — that is C17's roster check and
          it needs the real worldgen run. See the note below on required counts.
          🔴 **This state line previously read "dropped — Mechanitors are cut…",
          which is B65's ruling written into B56's slot.** It is not B56's. Anyone
          reading it concluded the five dead factions were abandoned; they were
          repaired the same day. Corrected 2026-08-15 by BUILD.
          OFFLINE VERIFY (2026-08-15, game down): **zero `<li>` under
          `xenotypeChances` in all 8 files**, and the 8 deployed copies under
          `…\Mods\Jawa_Patches\Defs\FactionDefs\` are **byte-identical to the repo**
          (md5, all 8). So the load-time discard should be gone.
          LIVE HALF, this load: zero `Exception loading def from file Jawa*.xml`,
          and all 8 defNames resolve. Expect the log to shrink ~98% with it.
          🔴 **DO NOT read faction ABSENCE FROM THE WORLD as this bug returning** —
          a def that loads and a faction that gets generated are different
          questions. Only `Jawa_IndigenousTribes` carries
          `requiredCountAtGameStart`; the other seven default to a count of 0.
          Filed to DECIDE as `seven-factions-have-no-required-count-9c4e17`.

## B65 Give the Mechanitor a blaster — the autopistol is gone
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
state:    fixed offline + deployed 2026-08-15. **Live half needs the NEXT load** —
          defs parse only at startup, so the running game still has the old file.
          🔴 **THE SPEC ABOVE IS WRONG ON ITS CENTRAL FACT and it sent two seats
          the wrong way. "That mod is not in the 576-mod list" — it IS.**
          `Dark Ages : Beasts and Monsters` = `Van.Beasts`, active. And an ABSENT
          mod could not have produced that line at all: `PatchOperationFindMod`
          returns TRUE when no listed mod is active. **A FindMod that FAILS is
          proof the mod is PRESENT and something inside its `<match>` broke.**
          ROOT CAUSE — `DA_Taraal` is `ParentName="DA_BaseTaraal"` and declares no
          `<statBases>` of its own. Patches run against RAW XML, before
          inheritance, so the generated
          `<nomatch><PatchOperationAdd xpath=".../DA_Taraal/statBases">` matched
          nothing, returned false, and **took the whole enclosing
          PatchOperationSequence down with it.** It was op 13 of 14, so
          `DA_SnowTaraal` never got patched either.
          THE GENERATOR'S BLIND SPOT, which is the reusable part: it decided a def
          had `statBases` by reading the **resolved** def dump, where an inherited
          block is indistinguishable from an owned one. Now gated on the def's own
          node (`ds.of_type("ThingDef") … r.own.find("statBases")`).
          ⚖️ `DA_Taraal` is SKIPPED, not patched. Adding a `<statBases>` to a child
          would need the parent-merge rule to be certain, and it is not worth
          guessing with a live animal's MoveSpeed on the answer. One def keeps
          vanilla yield; every other def in the file is unaffected.
          ALSO FIXED, same commit: the generator wrote CRLF under `python.exe` and
          LF under `python3`, so a regeneration produced a **29,191-line phantom
          diff**. `newline=""` pins it.
          REGENERATED: 1,249 ops in 37 mod groups, 0 validator errors. The diff
          also drops four mods that have left the load set (Vanilla Animals
          Expanded, Grimstone : Beasts, Giant Snake, ReGrowth: Boiling) — verified
          absent from `<activeMods>`, so that is the patch catching up, not a
          regression.
          📌 For B22: `validate_patch.py` already WARNs on this exact shape
          ("inner xpath differs from the conditional test") 1,145 times and cannot
          tell the safe case from the fatal one. With raw-XML defs it could — that
          is the check that would have caught this before the load.

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
          `deploy_custom_mods.py --mod Jawa_Patches` (dry run) then `--apply`.
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

<!-- PARKED FINDING from BUILD, 2026-08-15, on the biomeConfigs half of this item.
     Investigated to here and stopped at WRAP; this is where to resume.

     SYMPTOM (DECIDE measured): src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml
     is rejected at load with 28 XML format errors, so all 24 biome scoreOffsets
     do nothing.

     FIRST HYPOTHESIS, and it is probably WRONG: our file writes biomeConfigs
     dictionary-keyed, `<ExtremeDesert><scoreOffset>12</scoreOffset></ExtremeDesert>`,
     and RimWorld list fields need `<li>` entries. That is the exact inverse of
     the xenotypeChances trap, so it was the obvious suspect.

     WHAT THE EVIDENCE ACTUALLY SAYS: no other mod in the 576-mod set writes a
     <biomeConfigs> element at all, so there is no worked example to copy. And
     `strings -a` over the owning assembly
     (workshop/294100/3631364335/Assemblies/AlienWorlds.TidallyLocked.dll)
     finds `PlanetTypeDef` but NEITHER `biomeConfigs` NOR `scoreOffset`.
     Field names live in the #Strings heap and should be visible there.
     ⇒ The stronger hypothesis is that THE FIELD DOES NOT EXIST on this def in
     this version - in which case no amount of reshaping the XML will help and
     the offsets need a different mechanism entirely.

     NEXT STEP, cheapest first: decompile or ilspy that DLL and read PlanetTypeDef's
     real fields. Do NOT reshape the XML until the field is confirmed to exist -
     that would be fixing the spelling of a word the parser never wanted.
     Note `strings -a` proves a NAME only; a UTF-16 method body needs `-a -el`. -->

## B63 Two settings would silently give us the wrong planet — fix before worldgen
row:      12
spec:     `design/Jawa/worldbuilding/SCENARIO_SETTINGS_SPEC.md` is the authority.
          It sorts EVERY game-creation setting into three buckets and the split is
          the point: **(A) authored as FILES** — yours, fixable on a reload;
          **(B) 🔴 CLICKED AT WORLD CREATION and permanent** — the owner's, and
          getting one wrong costs a new campaign plus a ~25-30 min cold load;
          **(C) changeable in an existing save** — note and move on. Put the
          bucket letter on anything you quote from it.

          🔴 **TWO BLOCKERS, both bucket A, both with a bucket B deadline.
          Measured 2026-08-15. Neither is theoretical.**

          (1) **THE PLANET TYPE IS NOT SELECTED AND THERE IS NO BUTTON FOR IT ON
          THE WORLD PAGE.** `ferny.Worldbuilder` is NOT in `<activeMods>`, so the
          Alien Worlds Framework runs its `Standalone` backend and the planet-type
          selector is a radio list in **Mod settings**, not a world preset on the
          generation page (DLL string `Planet type for new worlds:`).
          `AlienWorldsSettings.selectedPlanetType` defaults to `"Default"` and
          **no `Mod_3626210061_*.xml` exists anywhere in
          `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\`**
          (all 85 entries listed, zero matches). ⇒ **A world generated today is
          the ordinary vanilla planet** — no tidal lock, no
          `avgTempByLatitudeCurve`, no `biomeBlacklist` — and it generates without
          one error line. The safe route is the owner setting it in the mod
          settings window and screenshotting it; a pre-written settings file is
          allowed but its FILENAME IS DERIVED, so it only counts once the settings
          page reads it back.

          (2) **THE BIOME MIX IS DEAD.**
          `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml` writes
          `biomeConfigs` in the dictionary-keyed shorthand
          (`<Desert><scoreOffset>12</scoreOffset></Desert>`). `Player.log`
          lines 1052-1079 of the 11:03 load carry 28 copies of
          `XML format error: List item found with name <X> that is not <li>, and
          which does not have a custom XML loader method, in <biomeConfigs>`.
          The live def reads `biomeConfigs: []` while `biomeBlacklist` holds all
          29 entries — **the blacklist works, all 24 abundance/rarity offsets do
          nothing.** The field is `Dictionary<string, BiomeConfig>` (framework
          source, `…\294100\3626210061\Source\PlanetTypeDef.cs`) with no custom
          loader, so it needs
          `<li><key>Desert</key><value><scoreOffset>12</scoreOffset></value></li>`
          — the shape vanilla uses for `AnimationDef.keyframeParts`.
          🪤 **This is B56 in reverse**: there the `<li>` shape was wrong on a
          keyed field, here the keyed shape is wrong on a real dictionary. Read
          the declared type; never pattern-match off another def.
          ⛔ **KEEP `<biomes>` EMPTY.** `scoreOffset` is applied in
          `PlanetTypeManager.GetBiomeScorePostfix` and only tests
          `ContainsKey` — the `<biomes>` membership check guards
          `defFields`/`texture`/`workerClass` only. Expect up to 24 harmless
          `contains key X, which isn't present in <biomes>. Skipping.` warnings
          after the fix and do NOT silence them by populating `<biomes>`, which
          would exclude `Space`, `Orbit`, `Underground` and every pocket map.
          🔴 Biome scoring runs once, in `WorldGenStep_Terrain`. Chain step 8 is
          recorded done and ratified; its scoring half has never run.

          **THE ANOMALY RULING, and it is world-creation-permanent.** The
          playstyle is `AnomalyPlaystyleDef` — exactly three defs, `Standard` ·
          `AmbientHorror` · `Disabled`. **`AmbientHorror` with the threat slider
          at 0%** keeps study, the anomaly research tab, the codex and tome
          trading alive while nothing auto-spawns, and skips the
          `minAnomalyThreatLevel` gate so `PitGate`/`FleshmassHeart` can still be
          fired deliberately. `Disabled` — which `WORLDGEN_RUN.md` §2.E still
          records — kills all of that.
          🔴 **It is settable ONLY at world creation**: the "Anomaly settings…"
          button is drawn inside a `ProgramState.Entry` guard and is simply absent
          in an existing save. The threat slider afterwards needs CUSTOM
          difficulty. ⇒ **Custom difficulty is MANDATORY, not a preference** —
          `overrideAnomalyThreatsFraction` is not a `DifficultyDef` field at all
          (absent from all 10 live defs) and lives only on the runtime
          `Difficulty` object, in the save's `<customDifficulty>`.
          ⛔ **Author NO `DifficultyDef` and NO `ScenarioDef`.** Patching
          `Custom` is pointless (vanilla's own comment: values "aren't used when
          Custom is selected"), a new preset has `isCustom false` and loses the
          slider, and `Scenario.standardAnomalyPlaystyleOnly` on any scenario we
          ship would grey out everything but `Standard`.
          A save embeds its whole scenario and does not reference the ScenarioDef,
          so ongoing ScenParts (`PermanentGameCondition`, `StatFactor`,
          `DisableIncident`, `DisableQuest`, `CreateIncident`) go into the save's
          `<parts>` — and `Rule_Disallow*` needs its `<rules>` entry too.

          **DOC CORRECTIONS YOU OWN:**
          - `infrastructure/state/EXPECTED_FAILURES_next_load.md` S5 records
            `AnomalyFrequency_None/_VeryRare/_Rare/_Balanced/_Intense/_Overwhelming`
            as playstyle **defNames**. 🔴 They are TRANSLATION KEYS —
            `…\Data\Anomaly\Languages\English\Keyed\Misc_Gameplay.xml:499-504`,
            the frequency slider's labels. S5's pass condition is unsatisfiable as
            written. Expect `AmbientHorror`, plus a second grep for
            `overrideAnomalyThreatsFraction` = 0.
          - `infrastructure/state/WORLDGEN_RUN.md` §2.E → `AmbientHorror` + 0.
            Its §2.A also assumes the planet type is chosen at the page; it is not.
          - Strike "disable enemy flee%" from `setup_checklist.md` §1,
            `concept.md:66` and
            `Gravship_Campaign_Planning_Discussion_2026-08-02.md:1420`. No such
            field exists on `DifficultyDef` and no `Difficulty_*Flee*` keyed
            string exists anywhere; fleeing is decided in code.
          🔴 **THE PLANET'S NAME CANNOT BE TYPED ANYWHERE.** The owner's NAMES
          ruling (`SCENARIO_SPEC.md`, `f88b2ac`) makes the planet **`Ash'karr`**
          ("The Sundered"), the scenario **`Flight of the Utinni`** and the ship
          **`The Utinni`**. `Page_CreateWorldParams` has NO world-name field —
          `WorldInfo.name` is generated from Core's `RulePackDef` `NamerWorld` and
          scribed as `<world><info><name>` (an observed save reads `Al Graffias`).
          ⇒ Either patch `RulePackDef[defName="NamerWorld"]` **before** the
          worldgen click, or edit `<world><info><name>` in the finished save.
          Prefer the patch; it also renames throwaway dev worlds, which is how you
          know it landed.
          ⚠️ **The apostrophe, checked rather than assumed:** legal unescaped in
          XML text and in double-quoted attributes, so `[defName="X"]` xpaths are
          safe — but 🔴 **never put it in a defName or a translation key**, keep it
          to `label`/`fixedName`/player-facing text, and **never retype the
          string**: `’` (U+2019) reads identically and compares unequal. Save
          filenames derive from the COLONY name, not the world name, so that path
          is clear today.
          **`Flight of the Utinni`** is player-facing and lives in the save's
          embedded `<scenario><name>` — spelled once, identically everywhere.
          **Put "The Sundered" in `ScenPart_GameStartDialog`**; it is already in
          the keep list, it is the only part carrying prose, and if it is not in
          the opening narration the translation never reaches the player.
          REPORT, do not resolve: `SeaIce` is on our blacklist while the Tidally
          Locked mod's own C# rewrites `BiomeWorker_SeaIce.GetScore` to spread it;
          and `Player.log:1080` `[Def Error]: TidallyLocked … Parsed 0.3 as int.`
verify:   `validate_patch.py` on `JawaWorld_BiomeMix.xml` with `--defs`, 0 errors.
          After the next load: `grep -c "not <li>.*biomeConfigs" <Player.log>`
          returns **0** where today it returns 28; then `refresh.py` and the live
          `PlanetTypeDef.json` entry for `TidallyLocked` reads **24**
          `biomeConfigs` entries AND 29 `biomeBlacklist` entries. 🔴 The blacklist
          alone is NOT a pass — that is exactly the state that hid this bug.
          The settings page reads *tidally locked world*. No `ScenarioDef` and no
          `DifficultyDef` exist under `src/`.
          Names: `grep -o "<name>Ash.karr</name>" <the .rws>` matches AND the
          matched byte is `U+0027`, not `U+2019`; `grep -rn "Ash" src/` shows the
          apostrophe in no defName and no translation key.
criteria: the generated world is on the tidally locked planet type with the
          intended biome mix, the world is named `Ash'karr`, the opening dialog
          says "The Sundered", and the save reads back `AmbientHorror` with the
          anomaly threat fraction at 0.
state:    ready

## B62 Put desert creatures in the other four animal-drawn vehicles
row:      2
spec:     Generalise the eopie sled (`4f3afc7`) to every remaining animal-drawn
          vehicle. Owner: *"do the same thing you just did to the dog sled across
          all the primitive transports that currently show horses, cows, and other
          terrestrial animals. Feel free to pick other Star Wars appropriate desert
          creatures as needed."* All work lands in the existing mod
          `src/Jawa/DesertVehicleReskin/` (`mandrake.desertvehiclereskin`).
          🔵 **OFFLINE. Needs no game to author.** Deploying it needs a window plus
          a look — C41.

          ### The scope is exactly four vehicles, and the test is a def tag
          Alpha Vehicles - Neolithic (ws `3028675048`, `sarg.alphavehiclesneolithic`)
          ships 12 vehicles. Exactly five carry the stat value `AV_TractionAnimal`
          — Chariot, WarChariot, CoveredCarriage, OxCart, DogSled — and those five
          are exactly the five with an animal drawn into the texture. DogSled is
          done. ⛔ Do NOT identify them by "the mask has a black region": seven of
          twelve have one and five of those have no animal (Balloon's is its
          envelope, Hwacha's the rocket bundle, OutriggerCanoe's hull and sail,
          Palanquin's canopy, RowBoat's oars). Hwacha, Palanquin, Rickshaw and
          Wheelbarrow are human-powered; Balloon is Air; RowBoat and OutriggerCanoe
          are Sea. Nothing outside the four is in scope.

          ### 🔴 THE TEXPATH TABLE — THREE defs share each path, not two
          The sled taught us that art by PATH reaches every def naming that path
          while COLOUR is per-def. The sled fix found two defs. **There are three.**
          `Vehicles.VehicleBuildDef` — the architect-menu blueprint — carries its
          OWN `<label>` and `<description>` and was never patched on the sled, so
          the build menu still reads "Dog Sled … pulled by four trained dogs …
          over ice and through snow". Fix that here too.

          | texPath (all under `Things/Vehicles/Land/Tier0/`) | def type | defName | owning mod | `<color>` |
          |---|---|---|---|---|
          | `Chariot/AV_Chariot` | Vehicles.VehicleDef | `AV_Chariot` | sarg.alphavehiclesneolithic | (192,146,94) |
          | | Vehicles.VehicleBuildDef | `AV_Chariot_Blueprint` | sarg.alphavehiclesneolithic | none |
          | | ThingDef | `VFEPD_Chariot` | VanillaExpanded.VFEPropsandDecor | (192,146,94) |
          | `CoveredCarriage/AV_CoveredCarriage` | Vehicles.VehicleDef | `AV_CoveredCarriage` | sarg… | (80,63,32) |
          | | Vehicles.VehicleBuildDef | `AV_CoveredCarriage_Blueprint` | sarg… | none |
          | | ThingDef | `VFEPD_CoveredCarriage` | VFEPropsandDecor | (80,63,32) |
          | `OxCart/AV_OxCart` | Vehicles.VehicleDef | `AV_OxCart` | sarg… | (58,41,10) |
          | | Vehicles.VehicleBuildDef | `AV_OxCart_Blueprint` | sarg… | none |
          | | ThingDef | `VFEPD_OxCart` | VFEPropsandDecor | (58,41,10) |
          | `WarChariot/AV_WarChariot` | Vehicles.VehicleDef | `AV_WarChariot` | sarg… | (192,146,94) |
          | | Vehicles.VehicleBuildDef | `AV_WarChariot_Blueprint` | sarg… | none |
          | | ThingDef | `VFEPD_WarChariot` | VFEPropsandDecor | (192,146,94) |
          | `DogSled/AV_DogSled` | Vehicles.VehicleBuildDef | `AV_DogSled_Blueprint` | sarg… | none — **the gap the sled left** |

          ⇒ **13 defs. All 13 need a label and a description.**
          🔴 **No colour patch is needed for any of the four — the vehicle and its
          VFEPD twin already carry identical `<color>`.** The sled diverged only
          because WE repainted the vehicle and not the prop. So the rule that
          matters: **if you change a vehicle's `<color>`, you MUST change its
          `VFEPD_*` twin in the same file, or you reproduce the sled bug exactly.**
          The donor colours are already tan/brown and the art pass alone answers
          the brief — **default: leave all four `<color>` triples alone.**
          ⚠️ The VFEPD props declare only `<color>`; no `colorTwo`/`colorThree`. With
          a two-value mask only `<color>` reaches a pixel, so the pair still match.
          ⚠️ `VehicleBuildDef` has no `<color>` and no `<shaderType>` at all, so the
          under-construction building renders the raw PNG untinted. Pre-existing,
          not ours; out of scope.
          ⚠️ The VFEPD props exist only while AV Neolithic is active — they live in
          `…/2102143149/1.6/Mods/AlphaVehiclesNeolithic/` behind an
          `IfModActive="sarg.alphavehiclesneolithic"` LoadFolders gate.

          ### Creature assignment
          All four creatures below are **real, active PawnKindDefs** in
          `Mlie.StarWarsAnimalCollection` (ws `3497316713`), so every one has a live
          in-game sprite to work from. ⚠️ **Its art is in an AssetBundle, not loose
          PNGs** — `…/3497316713/AssetBundles/Mlie_StarWarsAnimalCollection`, assets
          named `swanimals/<Name>/<Name>_south`. Extract with
          `skills/reading-rimworld-graphics`; there is no `Textures/swanimals/` dir.

          | vehicle | donor art shows | assign | why | art cost |
          |---|---|---|---|---|
          | `AV_OxCart` | **2 oxen**, yoked abreast, horned, humped, white/grey | **BANTHA ×2** (`Bantha`, `swanimals/Bantha/BanthaW_south`) | Tatooine's heavy hauler and the clans' measure of wealth; a barrel dray is what a bantha is for | **CHEAPEST — repose, not redraw.** Horns, hump and broad muzzle already in the silhouette; recolour to matted brown and curl the horns back |
          | `AV_Chariot` | **1 horse**, chocolate, dead ahead of the pole | **DEWBACK ×1** (`Dewback`, `swanimals/Dewback/Dewback_south`) | light fast cart that needs hard ground; the dewback is the one desert beast that runs | cheap — smallest animal share (28%), south symmetric to 2 px |
          | `AV_WarChariot` | **2 horses**, black/charcoal | **DEWBACK ×2** | Tusken and sandtrooper war mount; a bow platform behind a pair is the Tatooine raid image | **reuses the Chariot's dewback body** at two instances in a darker palette — the two chariots amortise one animal build |
          | `AV_CoveredCarriage` | **2 horses**, chestnut, abreast | **RONTO ×2** (`Ronto`, `swanimals/Ronto/Ronto_south`) | the Mos Eisley draft beast; a loaded covered wagon behind a ronto pair is the most on-the-nose cargo image on the planet | most work — reptilian slab body, long neck, small head is a real body swap |
          | `AV_DogSled` | done | eopie | — | — |

          ⛔ **Eopie is spent — do not reassign it.** `Blurrg` also exists locally
          (`swanimals/Blurrg/Blurrg_south`) and is the documented substitute if any
          assignment above is rejected.

          ### Labels and descriptions — 13 defs
          In-character prose first, then the donor's own game facts in the donor's
          `<color=#bb8f04>` markup. **Blueprint gets the vehicle's description
          verbatim** (the donor does the same). **Prop gets a "gone still" rewrite**
          and the label suffix ` (prop)`, per `EopieSled_Identity.xml`.
          ⛔ **Do not change `fuelType`.** All four are `Hay`; the `Fuel type:` line
          must keep matching the def or the description lies.

          | def | label |
          |---|---|
          | `AV_Chariot`, `AV_Chariot_Blueprint` | `dewback cart` |
          | `VFEPD_Chariot` | `dewback cart (prop)` |
          | `AV_CoveredCarriage`, `AV_CoveredCarriage_Blueprint` | `ronto wagon` |
          | `VFEPD_CoveredCarriage` | `ronto wagon (prop)` |
          | `AV_OxCart`, `AV_OxCart_Blueprint` | `bantha dray` |
          | `VFEPD_OxCart` | `bantha dray (prop)` |
          | `AV_WarChariot`, `AV_WarChariot_Blueprint` | `dewback war cart` |
          | `VFEPD_WarChariot` | `dewback war cart (prop)` |
          | `AV_DogSled_Blueprint` | `eopie sled` |

          Descriptions, ready to paste (`\n` literal, `&lt;` escaped, as the donor
          writes them):

          **`AV_Chariot`** — A light two-wheeled cart and one dewback in the shafts.
          The lizard does the work; the cart is a standing box, a wheel either side
          and a pole.\n\nA dewback will run. Not far, and not at midday, but it will
          run, which no bantha does. It is placid, incurious, and stubborn about
          exactly one thing — being asked to walk on soft sand. Keep to hardpan and
          salt flat and it is the fastest thing on the pan that burns no fuel. Off
          the packed ground the wheels sink, the dewback plants itself, and it will
          not be argued with.\n\nCrew: Driver x1 · Fuel type: Hay

          **`AV_CoveredCarriage`** — Two rontos in harness and a box wagon under a
          canvas hood, slung on leather strapping so the passengers arrive able to
          stand.\n\nA ronto is a grey slab of an animal with a small head at the end
          of a long neck and no opinion about anything. They spook — a droid
          stepping out at the wrong moment will put one through a market stall — but
          in open country nothing is steadier, and a pair will carry a loaded wagon
          and three people between settlements without stopping to be
          admired.\n\nCrew: Driver x1, Passenger x3 · Fuel type: Hay

          **`AV_OxCart`** — A flatbed dray stacked with casks, and two banthas in the
          yoke.\n\nBanthas are the reason anything heavy moves on this world. Hide
          matted into rope, horns that spiral back over the skull and are used for
          shoving rather than goring, and a complete indifference to heat. A pair
          will drag across open sand a load that would bury a wheeled cart anywhere
          else. The clans count their wealth in them.\n\nThey want water, and a great
          deal of it. Everything else they find themselves.\n\nCrew: Driver x1 ·
          Fuel type: Hay

          **`AV_WarChariot`** — An armoured fighting car on a wide axle, two dewbacks
          in the traces, and a bowman standing where the floor is
          reinforced.\n\nThe driver's whole job is the reins and the ground ahead;
          the archer's is everything else. It works because a dewback holds a
          straight line under noise that would turn a bantha, and because a moving
          platform at the edge of bow range is a problem an infantry line cannot
          easily solve.\n\nCrew: Driver x1, Archer x1 · Fuel type: Hay

          ⚠️ Drop the donor's warning and offroad-scolding paragraphs; the offroad
          fact is folded into the prose above where it earns its place.

          ### Patch mechanics — carry all four from the sled
          1. **Art overrides by PATH.** Ship a PNG at the donor's own texPath inside
             `src/Jawa/DesertVehicleReskin/Textures/` and it wins. Needs
             `_south` `_north` `_east` **and** the `_southm` `_northm` `_eastm`
             masks. ⚠️ The donor's suffix convention is `AV_OxCart_southm`, the `m`
             appended to the facing, never `_south_m`.
          2. **One `PatchOperationFindMod` per owning mod**, each with
             `MayRequire` — `sarg.alphavehiclesneolithic` for the VehicleDef and
             VehicleBuildDef, `VanillaExpanded.VFEPropsandDecor` for the ThingDef —
             so an absent mod is a silent no-op, not a red error.
          3. xpath roots are the literal element names:
             `/Defs/Vehicles.VehicleDef[defName="AV_OxCart"]/label`,
             `/Defs/Vehicles.VehicleBuildDef[defName="AV_OxCart_Blueprint"]/label`,
             `/Defs/ThingDef[defName="VFEPD_OxCart"]/label`.
          4. Suggested files, one per vehicle beside the existing two:
             `Patches/DewbackCart_Identity.xml`, `RontoWagon_Identity.xml`,
             `BanthaDray_Identity.xml`, `DewbackWarCart_Identity.xml`, and the
             one-operation `Patches/EopieSledBlueprint_Identity.xml`.

          ### Health-tab component labels — the second half nobody sees coming
          The defs carry animal-named damage components. The health tab will say
          "Left Ox" over a picture of a bantha. `<label>` only:
          `AV_OxCart` `LeftOx`→`Left Bantha`, `RightOx`→`Right Bantha` ·
          `AV_Chariot` `Horse`→`Dewback` ·
          `AV_CoveredCarriage` `LeftHorse`→`Left Ronto`, `RightHorse`→`Right Ronto` ·
          `AV_WarChariot` `LeftHorse`→`Left Dewback`, `RightHorse`→`Right Dewback` ·
          `AV_DogSled` `FrontLeftDog`/`FrontRightDog`/`RearLeftDog`/`RearRightDog`
          → `Front Left Eopie` etc.
          xpath: `/Defs/Vehicles.VehicleDef[defName="AV_OxCart"]/components/li[key="LeftOx"]/label`
          ⛔ **Never touch `<key>`** — it is the runtime identifier and is referenced
          by `hitbox`, `tags`, `categories` and by saved games.
          ⛔ Leave `fleshType` (`AV_WoodenAndOxVehicle` …) and the impact SoundDefs
          alone; they are defNames, invisible to the player, and renaming them is a
          cross-reference risk for zero gain.

          ### The art work — 24 PNGs, and the measurements are already done
          4 vehicles × 3 facings × (art + mask) = **24 files, all 512×512**.
          🔵 **Do not author `_west`** — Vehicles.Graphic_Vehicle auto-mirrors east.
          🔵 **`src/Jawa/DesertVehicleReskin/Source/GEOMETRY.md` already holds the
          measured build sheet for all four** — animal bounding boxes per facing,
          inter-animal gaps, hitch bands, mask insets. Read it before touching a
          pixel; re-measuring is the expensive part and it is already paid for.
          The load-bearing lines from it:
          - **The mask is not a segmentation map.** The black region is the animal's
            interior fill; its 4–6 px keyline is tagged RED. **Dilate black outward
            by 8 px**, and **filter connected components ≥600 px first** or
            CoveredCarriage's black-tagged wheel rims get erased with the horses.
          - **Three facings have NO isolated hitch band** and must use the dilated
            stencil rather than the cheap "erase past the hitch" route:
            🔴 `Chariot/north` (pole painted over the animal's back),
            🔴 `CoveredCarriage/north` (canvas abuts the horses at y 198),
            🔴 `WarChariot/north` (car front abuts animal black at y 276).
          - **OxCart north/south ox halves are exact mirrors (10,514 px each)** — the
            cheapest single conversion in the set. `OxCart/east` is the odd one: the
            two oxen stack front-to-back and their silhouettes MERGE.
          - **Chariot's three black bboxes overstate the animal** — a 4–17 px rein is
            tagged black and trails 77 cols across the cart. Filter rows by black
            count ≥18 px.
          - **WarChariot's `AV_ArcherTurret.png`** is a separate 128×128 Cutout layer,
            never tinted, rotatable at radius ~59.8 px; on **north** the swept disc
            reaches ~23 px into the animal region over x 196–316.
          - **Keep every row outside the animal band pixel-identical.** Driver
            draw-offsets are hard-coded per vehicle; move the cart body on the canvas
            and the driver sprite floats.

          **The build scripts do NOT generalise as code; the METHOD does.**
          `Source/build_eopie_sled_{south,north,east}.py` are 200–275 lines of
          constants measured off one vehicle. Copy the template per vehicle per
          facing — 12 scripts — reusing verbatim: (a) copy rows outside the animal
          band; (b) erase by dilated component-filtered mask; (c) composite a
          generated animal pair; (d) re-draw the traces onto measured attachment
          fractions; (e) **emit a strictly two-value mask — RED over vehicle and
          rigging, BLACK over the animal** — which is what keeps the beast immune to
          the def's `<color>`. Reuse `Source/preview_tint.py` and
          `Source/review_sheet.py` unchanged.
          New animal art goes through `skills/generating-rimworld-sprites`
          (`scripts/conform_sprite.py`, `scripts/validate_sprite.py`) with the same
          two-reference recipe the eopie used: the extracted bundle sprite for the
          creature and palette, and the donor's own cropped team for the overhead
          projection, harness language and line weight. Commit the generated animal
          to `Source/art/` so the build is reproducible without the image model.
          🔴 Neither donor's pixels are ever composited into an output — reference
          only. Nothing of theirs is redistributed.

          ### Finally
          Update `src/Jawa/DesertVehicleReskin/About/About.xml` — its description
          still says "no defs are touched, no patches are applied" (already false
          since `4f3afc7`) and "seven of the donor's vehicles are untouched".
          Keep `loadAfter sarg.alphavehiclesneolithic`: these are loose PNGs at the
          same path and RimWorld resolves loose-vs-loose by load order, so loading
          before the donor makes every texture in this mod invisible.
verify:   OFFLINE, no game:
          (a) `python3 skills/rimworld-modding/scripts/validate_patch.py` over each
              new file in `src/Jawa/DesertVehicleReskin/Patches/` with BOTH `--live`
              and `--defs`; every xpath resolves to exactly the count expected —
              **13 label hits and 13 description hits across the five files**, not
              12 and not 14.
          (b) `python3 skills/generating-rimworld-sprites/scripts/validate_sprite.py`
              passes on all 24 PNGs: 512×512, real alpha, subject inside the donor's
              own footprint.
          (c) Per PNG pair, a script assertion: every row of the art OUTSIDE the
              animal bbox recorded in `GEOMETRY.md` is byte-identical to the donor's,
              and the emitted mask contains exactly two colour values.
          (d) `grep -c` in the finished patch files returns **0** for the strings
              `Horse`, `Ox`, `Dog` outside of `<key>` elements.
criteria: on a desert world every primitive transport in the vehicles menu is
          pulled by something that belongs on it, and nothing in its name,
          description or health tab still says horse, ox or dog.
state:    deferred to v2 — owner, 2026-08-15: *"defer adding any additional art to
          B62 for v2. Leave it just as is and keep deployed."*
          ⛔ Do NOT touch `src/Jawa/DesertVehicleReskin/`. The eopie sled ships as
          deployed and stays deployed; `mandrake.desertvehiclereskin` stays in
          `<activeMods>` at 541.
          ⇒ **CHECK C41 is not collectable in v1 at all** — it needs 24 PNGs and the
          mod has 12, all of them the sled. It is not "waiting for a load"; it is
          waiting for v2. Whoever owns C41 should park it, not re-book it.
          🔴 **One defect this leaves LIVE and it is not art.** The five
          `Vehicles.VehicleBuildDef` blueprints were never patched, so the architect
          menu still reads *"Dog Sled … pulled by four trained dogs … over ice and
          through snow"* for a vehicle that is now an eopie sled — on a desert
          world. That is a label-and-description fix on 13 defs, pure XML, no art,
          and it is the visible half of a mod we are shipping. **Not actioned: the
          owner said leave it as is, and this seat does not reinterpret that as
          licence to edit the mod.** Raise it as its own item if it should ship.
          Parked in `design/V2_DREAMS.md`.

## B64 Build our own boiling water and boiling rain, then drop ReGrowth: Boiling
row:      8
spec:     Full spec: `design/Jawa/mods/REGROWTH_BOILING_LIFT_SPEC.md`. Read it —
          the load-bearing points, inline:

          **DECIDE ruled route (b): AUTHOR OUR OWN, drop the donor mod.** Not
          route (a) reference-the-donor. The reason it is not close: **every C#
          class the effects need survives the drop.** The burn payload is
          `VEF.Weathers.WeatherEffectsExtension` — Vanilla Expanded Framework,
          ACTIVE — not a ReGrowth class. The steam splashes are
          `ReGrowthCore.WeatherExtension_FogMotes` / `WeatherOverlay_FogMotes`
          and the beach terrain is `RG_HotSpringSand`, all in **ReGrowth: Core**,
          which stays ACTIVE for Biomes! Polluted Lands and Comigo's Greater
          Swamps. So dropping `regrowth.botr.boilingforest` costs us **no class,
          no texture and no terrain we want**. Route (a) would have dragged 41
          defs to reach 10, including 14 unwanted plants (three of them SOWABLE,
          so they appear in the growing-zone selector whether or not the cut
          biome ever generates) — ~17 more Cherry Picker entries on top of 1308.
          🔴 Licensing did NOT enter the decision: this is a private playthrough,
          nothing is published.

          🔴 **The donor's boiling water terrain does NOTHING.** Measured off the
          live def dump, not the XML: the six `BoilingWater*` defs differ from
          vanilla water in exactly three fields — `glowColor (2,154,229)`,
          `glowRadius 2`, and a label reading "**spectral**". Identical
          `pathCost`, identical `extinguishesFire`, `traversedThought SoakingWet`,
          `burnDamage 0`, and the **same vanilla texture** (`Terrain/Surfaces/
          WaterShallowRamp`). No hediff, no damage, no heat, no pathing cost.
          🔴 And in OUR stack it is strictly WORSE than vanilla water: it lacks
          the `dbh_water` tag (Dubs Bad Hygiene ACTIVE — **not a drinking source**)
          and lacks `Biomes_PlantControl`. Painting rivers with it would quietly
          break drinking water on a world whose design is that water is currency.
          ⭐ The levers that make hot water hot are vanilla: `TerrainDef.burnDamage`
          + `burnIntervalTicks`, bracketed by Odyssey's `HotSpring` (0/0) and
          `LavaShallow` (3/120). No C# needed.

          **The weather burn is real but tiny.** Present in the live def via a
          `ModSettingsFramework.PatchOperationModOption` (resolves because
          `0ModSettingsFramework.dll` ships inside ReGrowth Core): `Burn`
          0.1–0.5, every 300–600 ticks, to **10%** of pawns, flesh only, outdoors
          only, `killsPlants false`. That is ~4 damage per pawn per game day — a
          scratch. Our defs triple the damage and raise
          `percentOfPawnsToDealDamage` to 0.35.
          🔴 And `commonalityRainfallFactor` bottoms out at `(0, 0)`, reaching 1
          only at rainfall 1300 — **as-shipped these weathers would never roll on
          any Sekkoth tile.** Re-anchor near `(0,1)`/`(500,1)` or the whole
          feature silently does nothing.

          **What to build**, all in `src/Jawa/Jawa_Patches` (it has `Defs/` and
          `Patches/` and loads LAST in ModsConfig, after every biome mod):
          (1) `Defs/TerrainDefs/Terrain_ScaldWater.xml` — six `Jawa_ScaldWater*`
              defs (Shallow/Deep/MovingShallow/MovingChestDeep/OceanShallow/
              OceanDeep). Keep the donor's cyan `glowColor (2,154,229)` +
              `glowRadius 2`; add `burnDamage 1`/`burnIntervalTicks 300` shallow
              and moving, `2`/`240` deep and chest-deep; `traversedThought
              HotSpring`; `avoidWander true`; 🔴 **carry the `dbh_water` tag on
              all six**; keep `extinguishesFire true`; `Saltwater` + `Ocean` tag
              on the two ocean defs.
          (2) `Defs/WeatherDefs/Weather_Scald.xml` — THREE weathers only:
              `Jawa_ScaldDrizzle`, `Jawa_ScaldRain`, `Jawa_ScaldFog`. All
              `isBad true`. Payload = one `VEF.Weathers.WeatherEffectsExtension`
              + `VEF.Weathers.WeatherOverlay_Effects`, plus the two ReGrowth Core
              fog-mote classes guarded `MayRequire="regrowth.botr.core"`.
          (3) `Patches/Biomes_ScaldWater.xml` — assign the scald terrains via
              `waterShallowTerrain` / `waterDeepTerrain` /
              `waterMovingShallowTerrain` / `waterMovingChestDeepTerrain` to:
              `IronScruff_PrimordialGeysers`, `Volcano`, `LavaField`,
              `AB_PyroclasticConflagration` (all six slots each), and
              `ZBiome_DesertOasis` + `COMIGO_GreaterSwamp_Tropical` (shallow and
              deep only — the standing pool steams, the through-river is already
              cooling). Lowland `Desert`/`ExtremeDesert`/`ZBiome_Badlands`/
              `ZBiome_Grasslands` stay ORDINARY water: per R-H1/R-H7 the water is
              potable again by the time it reaches the desert rivers, and keeping
              the effect rare is what makes it read.
              ⚠️ `PatchOperationAdd` where the biome has no such field,
              `PatchOperationReplace` where it does — four of the six already set
              some of these and the wrong operation fails SILENTLY.
          (4) `Patches/Biomes_ScaldWeather.xml` — scald weather to the only two
              rain-canon places on the planet (R-H1: rain falls only at the
              greatest altitudes): `AB_OcularForest` (drizzle 6 / rain 8 / fog 4 —
              R-H7's near-perpetual high-valley rain), `IronScruff_PrimordialGeysers`
              (4/3/3), `Volcano` (2/2/1). Each operation must ALSO remove the
              vanilla `Rain` / `RainyThunderstorm` / `FoggyRain` / `TorrentialRain`
              / `Blizzard` entries it replaces. **Nothing else gets any.**
          (5) Remove `regrowth.botr.boilingforest` from ModsConfig via
              `skills/rimworld-start-prep`. 🔴 **Do NOT remove
              `regrowth.botr.core`** — this build depends on it and so do two
              other active mods.
          (6) Deploy `Jawa_Patches` with a bare `deploy_custom_mods.py --mod Jawa_Patches` first.

          🔴 **TWO TRAPS, both of which look right and are wrong:**
          (a) **DO NOT touch `AB_OcularForest`'s water terrain.** It already
              overrides all four slots with Alpha Biomes' `GU_RedWater*`, which IS
              R-H7's red-flowing water verbatim. Overwriting it deletes the
              best-fitting terrain we own. Ocular forest gets WEATHER only.
          (b) **The donor's thunderstorm is NOT lifted.**
              `RG_BoilingRainyThunderstorm` has `rainRate 1` and its own
              description says the rain puts the fires out. R-H4's Pyrelands need
              DRY thunderstorms — a wet one in `ZBiome_Grasslands` would
              extinguish the standing burn the whole savanna design rests on.
              Vanilla `DryThunderstorm` (`rainRate 0`) already exists and
              `ZBiome_Grasslands` already carries it at commonality 2; raising
              that number is a separate item. Write no thunderstorm here.

          **NOT lifted** and why: the 14 plants (`RG_Plant_TreeBoilingBirch`,
          `RG_Plant_BoilingTreePine`, `RG_Plant_SpikedBoilingTreePine` — the
          coniferous and deciduous trees the owner does not want — plus the
          grasses/moss/bush/brambles/berry/cushion/flowers/edaku); the 3 items and
          the leaf filth; `RG_Owlbeast` and its corpse/meat/eggs/sounds (already
          cut); the `RG_BoilingForest` BiomeDef (cut by owner's ruling — nothing
          here revives it); the `RG_BoilingSettings` category and its two sliders.
          `RG_HotSpringSand` is not lifted because it does not need to be — it
          lives in ReGrowth Core; reference it by name for `lakeBeachTerrain` /
          `riverbankTerrain` on the geyser and volcano tiles.

          ⚠️ Nothing here touches `ZBiome_Grasslands`. R-H4's dry-thunderstorm
          raise and R-H1's global rain-stripping are separate owed items — do not
          fold them in.
verify:   OFFLINE, no game load:
          (a) `python3 skills/rimworld-modding/scripts/validate_patch.py` over BOTH
              new patch files with BOTH `--live` and `--defs`. Exact counts:
              **24 terrain hits** (6 biomes x 4 fields) and **3 biomes** in the
              weather file. Not 23, not 25. A patch that matches nothing logs
              nothing.
          (b) `grep -c dbh_water Terrain_ScaldWater.xml` returns **6**.
          (c) `grep -c Thunderstorm Weather_Scald.xml` returns **0**, and
              `rainRate` is > 0 in all three weathers.
          (d) `grep "RG_"` across everything BUILD writes returns only the three
              permitted references: `regrowth.botr.core` in a `MayRequire`, and
              `RG_HotSpringSand` in the beach/riverbank fields.
          (e) After the next load: `python3 src/RimMandrake/Utils/refresh.py`, then
              confirm the nine `Jawa_Scald*` defs resolve WITH their burn fields,
              and that `AB_OcularForest.waterShallowTerrain` still reads
              **`GU_RedWaterShallow`**.
criteria: a pawn who wades a river in the geyser fields or on a volcano gets
          burned and knows why; a pawn caught in the open in an ocular-forest
          valley runs for cover; every other tile on the planet is as dry as R-H1
          says it is; the Pyrelands still burn because no wet storm was ever added
          to them; and `regrowth.botr.boilingforest` is gone from the mod list with
          no red error at load.
state:    ready

## queue-ids-become-names-7f3a2c
row:      infra
spec:     Owner's ruling, 2026-08-15: **project queues stop using numbers.** An
          item gets a unique NAME instead — meaningful, and free to carry a
          pseudo-random suffix to guarantee uniqueness, exactly as this item does.

          WHY, measured today. Four seats append to two queue files with no
          locking, and a number that is free when you read it is taken by the
          time you write:
            · `B60` — filed by DECIDE for plant growth while BUILD was using it
              in a commit subject for the xenotype picker fix.
            · `B61` — DECIDE filed "Ancients as Rakata" while a BUILD subagent
              was mid-flight writing a different B61. Caught only because a
              cross-session message arrived in time; it would otherwise have
              overwritten a peer's item.
            · `B63` — DECIDE filed it TWICE from two of its own agents racing.
            · `B56` — duplicated for longer than a day before anyone noticed.
          ⇒ Three of those four were caught by luck or by a human reading a
          message, not by any check. The failure is silent: a blind write drops
          a peer's item and nothing reports it, because the file still parses
          and still looks full.

          🔴 A NAME CANNOT COLLIDE BY ACCIDENT. Two agents inventing an item on
          the same subject produce different names; two agents counting produce
          the same number. That is the whole argument.

          WHAT CHANGES:
          1. `infrastructure/agents/POLICY.md` — the item-format block, which
             currently shows `## <ID>`. Say: unique name, kebab-case, suffix to
             disambiguate, never a number.
          2. The `Closes:` trailer takes the name verbatim. `derive_matrix.py`
             reads those trailers out of git and is the reason IDs matter at all
             — confirm it does not parse or sort on a numeric ID before shipping.
          3. Existing numbered items are NOT renamed. They close under the ID
             they were filed with, or the trailer stops resolving. New items
             only.
          ⛔ Do NOT renumber history to make it tidy. A `Closes: B58` in a pushed
          commit is the durable record that the work happened; breaking it to
          gain consistency loses the thing the convention exists to protect.
verify:   POLICY.md states the naming rule; `derive_matrix.py` still resolves a
          mixed queue of numbered legacy items and named new ones — run it and
          paste the output showing both kinds resolving; and a grep of both queue
          files finds no duplicate name.
criteria: EMPTY — offline, no game needed.
state:    done — `derive_matrix.py`'s `CLOSES_RE` was `[A-Z][A-Z0-9-]*` and would
          have silently ignored every named trailer; widened to accept both. Rule
          in POLICY.md, echoed in DECIDE.md and BUILD.md.


## mod-list-shows-descoped-removals-9c4e12
row:      10
spec:     Owner broadcast, 2026-08-15: *"Game is down, offline work may begin. Stage
          the next game load and prepare additional content. Ensure the mod list shows
          the many removed mods correctly (BUILD)."* Relayed by REP with the state
          measured at relay time, so you do not re-measure the settled half:

          ALREADY CORRECT — live `ModsConfig.xml` (mtime 2026-08-15 11:58:30, 575
          active) and `deployed/config/v1_freeze/ModsConfig.xml` are IDENTICAL,
          including order, and 0 listed packageIds are missing from disk. All six
          Descoped rows of `design/Jawa/mods/CHERRYPICK_AGENDA.md` are absent from
          both: `VanillaExpanded.VanillaAnimalsExpanded`, `zal.giantsnake`,
          `regrowth.botr.boilingforest`, `guppyfacesarecute.skunks`,
          `abrolo.grimstone.beasts`, `redmattis.sapientanimals`.

          WHAT IS NOT DONE, and is this item:
          1. ✅ **ANSWERED — OWNER 2026-08-15: they stay INACTIVE BUT SUBSCRIBED, and
             this half is CLOSED.** Do not unsubscribe them and do not file an item to.
             ⚠️ The hazard the line below described is real and is now ACCEPTED, not
             fixed: a RimSort re-sort or a Steam action can re-add them with no warning.
             ⇒ The mitigation is the freeze copy, not unsubscribing — `ModsConfig.xml`
             and the freeze must stay identical, which item 2's verify already checks.
          2. Their defs are gone but references to them are not. Pre-record the
             `Could not resolve cross-reference` signatures the next load will throw
             into `infrastructure/state/EXPECTED_FAILURES_next_load.md` BEFORE launch —
             a missed one costs a load, a duplicate costs nothing.
          3. `RG_BoilingForest` and the six `BoilingWater*` terrains are named by
             B64 as replaced by our own authoring; confirm nothing still points at
             the dead defNames.
          🔴 Game is DOWN and confirmed down (`tasklist.exe`, no `RimWorldWin64.exe`),
          so this is the window. But `ModsConfig.xml` was written at 11:58 today and
          REP has asked the owner whether RimSort is open — read its mtime again
          immediately before any write, per NEXT_RELOAD §1b.
verify:   `ModsConfig.xml` live and freeze still identical after your pass; the six
          packageIds absent from both; every signature you expect from the removals
          present in `EXPECTED_FAILURES_next_load.md` before the load is called.
criteria: the next load throws no unexpected `Could not resolve cross-reference` that
          traces to one of the six removed mods.
state:    ready

## B66 🔴 Two generator defects, one regenerate — RIDE THIS WINDOW or lose a load
row:      9
spec:     🔴 **OWNER RULING 2026-08-15, AND IT IS PART (c) OF THIS ITEM — do it FIRST,
          because it changes what a correct run produces:**
          *"Remove any genes from our implementation of the xenotypes that aren't
          supported in our mod at this time. We will investigate what to do later."*

          ⇒ **STRIP the unresolvable gene; BUILD the species.** `pick_species` currently
          SKIPS a species when any gene fails `_gene_exists` — that is the behaviour being
          overturned. **No species is ever dropped for a gene again.** Filter `glist`
          instead of `continue`-ing, and keep `skipped` for causes that are not genes.

          **The complete set, measured by DECIDE at `e4d6040` — 4 genes, 6 species, one
          bad gene each. Enumerated in full; the skip message's `missing[:3]` truncation
          is hiding nothing.**

          | gene to strip | species |
          |---|---|
          | `Force_Gene_LatentForceUser` | Ithorian · KelDor · Mirialan |
          | `OuterRim_ForceAdept` | SithMassassi |
          | `OuterRim_ForceInsensitive` | Rakata |
          | `guy762_AbilityGene_cloak` | Defel |

          ✅ Measured safe — no species empties and **none loses its head-forcing gene**:
          Defel 18→17, Ithorian 16→15, KelDor 15→14, Mirialan 11→10, Rakata 7→6,
          SithMassassi 14→13. (Mirialan and SithMassassi have no head-forcer before OR
          after — pre-existing, D-CHK2's finding, not caused by this.)
          ⇒ Roster **57 → 63** of 64 buildable. ⚠️ **Herglic stays out** — "source carries
          no genes", a different cause, still unmeasured. Do not let the recovery hide it.

          📌 **Emit the strip list as generator OUTPUT** — one printed line per stripped
          gene per species — so the record is produced by the run and cannot drift from
          what shipped. That print IS the input to the later investigation.
          ⛔ **Do NOT widen `donor_xml_files` to index `AdditionalMods` in this item.** I
          directed that earlier to rescue Defel's cloak gene; the owner's ruling strips it
          instead, so the widening moved to the later investigation. Real finding, wrong
          moment.
          ⛔ **`_guard_species_regression` stays and is not weakened.** This ruling makes
          the catalogue GROW, so the guard should never fire — if it does, stop.

          ─────────────────────────────────────────────────────────────────────────────
          (a) and (b) below were routed 2026-08-15 from CHECK's D-CHK2 and D-CHK3.
          ⚠️ **"One file, one re-run, one redeploy" was DECIDE's framing and it was
          WRONG** — that premise is what sent a partial run at a mod live in `ModsConfig`.
          BUILD was right to stop and escalate. Treat (a), (b) and (c) as three changes
          to one file that share a single redeploy, not as one trivial regenerate.
          do not split them and pay the deploy twice.
          File: `src/RimMandrake/Utils/gen_races_mod.py`.
          Mod:  `src/Jawa/RimMandrake_StarWarsRaces` (`mandrake.starwarsraces`).
          ⏱️ **Pure XML + loose PNGs, no assembly.** It needs no shutdown window of
          its own, but it MUST be regenerated and redeployed before the game relaunches
          or `NEXT_RELOAD.md` §5 L0 photographs four species that are magenta for a
          reason we already know, and the next load re-asks a question answered today.

          (a) **THE PATH-REWRITE LIST IS INCOMPLETE — 19 defs, 27 dead paths.**
          `TEXFIELDS` at `gen_races_mod.py:148` and `TEXCONTAINERS` at `:151` are the
          whole list, and four families are missing from it:
            · `texPathFemale`                    — add to `TEXFIELDS`
            · `backgroundPathEndogenes`          — add to `TEXFIELDS`
            · `backgroundPathXenogenes`          — add to `TEXFIELDS`
            · `<Male>` / `<Female>` **inside** a `BigAndSmall.PawnExtension` `headPaths`
              — NOT a flat field; `TEXCONTAINERS` handles `<li>` children only, so this
              needs the container walk to descend into named children too
          Plus one hand path outside the generator:
            · `Pawn/HeadAttachments/gand/mask_yuun` in
              `src/Jawa/RimMandrake_StarWarsRaces/Defs/Misc/SW_Support.xml`
          🔑 **The texture copier is driven from the SAME list** (`copy_textures`,
          `:597`, fed by `texhits` from `rewrite`, `:478`). A field it does not rewrite
          is a texture it never copied — so three of these need the ART copied as well,
          not just the path fixed:
          | path | art state | action |
          |---|---|---|
          | `Pawn/HeadType/gand/gand`, selkath heads | 6 files PRESENT | rewrite path only |
          | `OuterRim/Genes/Headbone/ChagrianF` | NOT copied | rewrite **and** copy |
          | `Pawn/HeadAttachments/gand/mask_yuun` | NOT copied | rewrite **and** copy |
          | `YellowEyes_Female` | NOT copied | rewrite **and** copy |
          | `OuterRim/GeneIcons/*BG` | NOT copied | rewrite **and** copy |
          The donors still hold every file — e.g.
          `2980427615/Common_Old/Textures/OuterRim/Genes/Headbone/ChagrianF_east.png`,
          `2915192253/Textures/Pawn/HeadAttachments/gand/mask_yuun_east.png`. Nothing
          is lost, only unmigrated.

          (b) **69 PawnKindDefs are missing `initialResistanceRange`.**
          `write_pawnkinds` (`:821`) emits each kind with `ParentName="BasePlayerPawnKind"`,
          which does not supply it, so every load throws
          `Config error in RimMandrake<Species>_Kind: initial resistance range is
          undefined for humanlike pawn kind.` — **69 lines, three quarters of the whole
          stack's 93 config errors.** Not only noise: it is what a prisoner's recruitment
          resistance rolls from, so the capture path is unset for all 70 species.
          Fix: one `ET.SubElement(e, "initialResistanceRange").text = "10~20"` beside the
          existing `apparelMoney` line at `:831`. `10~20` is vanilla's humanlike value —
          use it; this is not a balance decision and must not become one.
          ⚠️ **Check `write_rescued_kinds` (`:769`) too.** It emits the 16 Galactic
          Diversity `RimMandrake_<Species>` kinds. The error text names `_Kind`, so those
          16 are probably clean — confirm rather than assume, and fix if not.
verify:   OFFLINE, all three before deploying:
          1. `python3 src/RimMandrake/Utils/gen_races_mod.py` re-derives the mod and
             prints `references that die 0` / `dangling texture paths 0`.
          2. No def field in the regenerated mod holds a path beginning `Pawn/`,
             `OuterRim/`, `UI/` or `Genes/` **without** the `RimMandrakeSW/` prefix:
             `grep -rhoE '>(Pawn|OuterRim|UI|Genes)/[^<]*<' src/Jawa/RimMandrake_StarWarsRaces/Defs/`
             returns nothing.
          3. Every path the generator now rewrites has a PNG behind it in
             `src/Jawa/RimMandrake_StarWarsRaces/Textures/` — the file count rises from
             713. A rewritten path with no art is the SAME magenta box wearing a new name.
          Then bare `deploy_custom_mods.py --mod RimMandrake_StarWarsRaces`, read the
          plan, then `--apply`.
          🔴 **STOP — the "one re-run" this item is built on is not possible today.
          See the state line. Do not run the generator expecting output.**
criteria: LIVE, on the load this window precedes — folded into `NEXT_RELOAD.md` §5 L0:
          · `grep -c "Failed to find any textures at" Player.log` returns **0**.
            🔴 That is the string. `Could not load UnityEngine.Texture2D` returns zero
            hits and is the wrong grep.
          · `grep -c "initial resistance range is undefined" Player.log` returns **0**.
          · A **female** `RimMandrakeChagrian`, a `RimMandrakeGand`, a `RimMandrakeSelkath`
            and the Gand's `mask_yuun` all render a head rather than a magenta box.
            ⚠️ **Gendered fields make this look intermittent** — male Chagrians already
            render because their `texPaths` WERE rewritten. **Do not test one sex and
            call a species clean.**
state:    🔴 BLOCKED 2026-08-15 — code fixes landed (`e4d6040`), REGENERATE REFUSED.
          The item's premise — *"one file, one re-run and one redeploy"* — is false
          today, and the reason is worth more than the item.

          DONE in `e4d6040`, all three code fixes, none deployed:
          · (a) `texPathFemale`, `backgroundPathEndogenes`, `backgroundPathXenogenes`
            added to `TEXFIELDS`; `headPaths` and `texturePaths` to `TEXCONTAINERS`.
            The spec said `mask_yuun` needed a HAND edit "outside the generator" —
            it does not: `SW_Support.xml` IS generated (`gen_races_mod.py:899` is
            its default target), so `texturePaths` covers it. The spec also warned
            `TEXCONTAINERS` handles `<li>` only; it does not — the walk takes every
            child, which is exactly why `headPaths`' `<Male>`/`<Female>` work.
          · (b) `initialResistanceRange` `10~20` added to `write_pawnkinds`.
            `write_rescued_kinds` NOT changed — unverified, because the run that
            would confirm it cannot complete.
          · (c) NOT IN THE SPEC: `_is_donor_gene` fixes a `KeyError: 'GS_Primitive'`
            that stopped the generator DEAD. `main` looked genes up in the dump with
            a bare `g[n]`; the donors' genes left the dump when the donors left the
            list.

          🔴 WHY IT IS BLOCKED, and this is the finding: `pick_species` reads its
          species from the DUMP and — unlike `_gene_exists`, whose docstring
          anticipates exactly this — has **no on-disk fallback**. With the donors
          switched off it builds **57 species where the mod ships 69**, losing
          Herglic, Defel, Ithorian, KelDor, Mirialan, Rakata, SithMassassi and
          others. **The `KeyError` was the only thing preventing that from being
          written and deployed over a mod live at slot 562.** Fixing the crash
          removed the accident, so `_guard_species_regression` now refuses to write
          a smaller catalogue. A partial run DID overwrite six def files at 57
          species before the guard existed; reverted, and HEAD is 69.

          TO UNBLOCK, pick one — both are DECIDE's call, not mine:
          1. Give `pick_species` the disk fallback `_gene_exists` already has.
             Offline, no load, and it removes the donor dependency permanently —
             which is the whole point of this mod. **Recommended.**
          2. Re-enable `guy762.starwarsxenotypes` + `neronix17.outerrim.galacticdiversity`,
             take a dump with them active, regenerate, switch them off again.
             Costs a load and restores the dependency this mod exists to break.

          ⚠️ Until then the four magenta species STAY magenta. That is now a known,
          explained state — CHECK should record it, not re-investigate it.

## B67 🔴 ~1,300 owner cherrypick judgements exist on one disk, ignored by git
row:      1
spec:     Routed by DECIDE 2026-08-15 from measuring D27. **Offline, no game, and it
          should be the first thing done in this window because it is pure loss risk.**

          (a) **COMMIT THE DECISION RECORD.** `.gitignore:181` ignores
          `observed/inventory/` wholesale under the comment *"Derived: regenerated in
          seconds by animal_inventory.py / *_contact_sheet.py"*. That is true of the
          678 MB of contact-sheet PNGs and CSVs and **false of seven files**:
            `observed/inventory/decisions_animals.json`    (1,239 defs, 338 cut)
            `observed/inventory/decisions_weapons.json`    (  799 defs, 183 cut)
            `observed/inventory/decisions_apparel.json`    (  820 defs, 132 cut)
            `observed/inventory/decisions_items.json`
            `observed/inventory/decisions_buildings.json`
            `observed/inventory/decisions_biomes.json`
            `observed/inventory/decisions_plants.json`
          **160 KB in total.** They are the owner's keep/cut calls, made by hand
          through `cherrypick_review.py`. No machine regenerates them — that is
          exactly the CLAUDE.md test for what must be committed.
          🔑 **The cuts are already durable; the KEEPS are not.**
          `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml` is tracked
          (`6efe834`) and holds all 1,308 cut keys. It records nothing about what was
          examined and kept. Lose this folder and no one can tell "the owner looked at
          this and kept it" from "nobody has reviewed this yet" across five categories
          — which means the whole cherrypick gets re-run.
          FIX: a negation line, **not** un-ignoring the folder. Keep the 678 MB out.
            ```
            observed/inventory/
            !observed/inventory/decisions_*.json
            ```
          Then commit the seven files by explicit path and push. Correct the stale
          comment above line 181 while you are in there — it is what made this
          invisible.

          (b) **`cherrypick_build.py` DOES NOT READ THEM.** It validates a
          hand-authored `KEYS` list of ~24 entries (Anomaly + GravTech) against the
          live def dump and writes the settings file. The deployed config holds
          **1,308** keys. ⇒ 1,284 of them were written past the validator that exists
          to check them, so **no key in the live cut list has ever been checked
          against a def dump**. A cut whose key is misspelled is silently inert, and
          the def dump cannot see it either — a cut that WORKED is absent from the
          dump, so "not in the dump" is not evidence of anything.
          FIX: `cherrypick_build.py` reads `observed/inventory/decisions_*.json`,
          unions their `cut` lists with the hand-authored `KEYS`, validates every key
          against the def dump, and writes the settings file. Report unresolvable keys
          by name; do not drop them silently.
          ⛔ **Do not change what is currently cut.** This is a validation pass over a
          list the owner already ratified — if the validator disagrees with a key,
          REPORT it, and it goes to `queue/HUMAN.md`. Silently correcting an owner's
          content decision is not yours or mine.
verify:   (a) `git check-ignore -v observed/inventory/decisions_weapons.json` returns
          nothing; `git ls-files observed/inventory/` lists exactly the seven JSONs and
          no PNG; `du -ch` on what you committed is under 200 KB.
          (b) `python3 src/RimMandrake/Utils/cherrypick_build.py` regenerates a settings
          file whose `<li>` count is **1,308** and which is byte-identical to
          `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml`. 🔴 **Any
          other count is a defect in the new code, not a correction to the list** —
          the freeze copy and the live config already agree at 1,308 and are the
          reference, not the output.
criteria: none — offline. Nothing here touches the game and nothing waits on a load.
state:    ready

## drive-the-batched-deploy-pass-8ad4f1
row:      10
spec:     Owner's answers, relayed by CHECK via REP, 2026-08-15. **The deploy pass is
          yours** — REP does not touch deploys, and B0/B1 today were already yours.

          1. **The window is LONG and open-ended.** No relaunch imminent. Spend it on
             ASSEMBLIES first, since those are the only things that ever needed it.
          2. **Deploy the whole parked set, batched — owner picked "all of them":**
             `C36` (donors off, a `ModsConfig.xml` change and therefore no longer
             window-gated at all), `C38` (JawaPlantGrowth, fast growth), `C39` (eopie
             sled), `C41` (four animal-drawn transports). `B0`+`B1` are already closed.
             One deploy pass, one load proves them all. Order and per-deploy traps are
             the manifest at `infrastructure/state/NEXT_RELOAD.md` §1.0 — assemblies
             SOLO, never a new DLL in a mixed batch, or attribution is poisoned for
             everything beside it.
          3. 🔴 **Every deploy lands in `queue/CHECK.md` with a validation plan and a
             NON-EMPTY `criteria:`.** Owner: things you deploy are supposed to land in
             CHECK's queue for testing and checkoff, and it should REQUIRE checkoff.
             CHECK refuses a bare item on policy, so a missing `criteria:` costs you a
             round trip. This is POLICY.md's existing rule, reaffirmed by the owner.
          4. **CHECK is waiting on the D-CHK2 generator fix from you** — Gand, Selkath,
             female Chagrian, Jawa mask. They stay magenta until it lands and redeploys,
             and CHECK does not want them misread as a Facial Animation failure at the
             next load. Get it into this pass.

          FYI, no action: C37 is resolved. The disfigurement was many races, not one;
          CHECK verified the deployed FA config game-down (156 entries, 69
          `Human-RimMandrake*`, 69 XenotypeDefs shipped, zero species unprotected) and
          committed `aa25203`. The "70" in the docs is off by one — 69 is measured.
verify:   `deploy_custom_mods.py --mod <name>` (bare = dry run) read before every `--apply`, one
          mod named per call, never bare; and every deployed mod has an item in
          `queue/CHECK.md` with a non-empty `criteria:` before you call the pass done.
criteria: CHECK accepts all four items without bouncing one for an empty field, and the
          next load attributes each result to exactly one deploy.
state:    ready

## cut-the-boiling-biome-reference-4e2b90
row:      10
spec:     🔴 **Owner, 2026-08-15: "WE ARE NOT USING BOILING BIOME."** That closes the
          question CHECK flagged and BUILD parked. Remove the `RG_BoilingForest` entry at
          `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml:140`
          (`<RG_BoilingForest><scoreOffset>-4</scoreOffset></RG_BoilingForest>`). It is
          the only BOTR reference left in `Jawa_Patches`, its mod
          (`regrowth.botr.boilingforest`) no longer loads, and it is a no-op in game that
          validates clean because the def is still in the 576-mod dump.
          Do NOT go further on the strength of this: `src/Jawa/Jawa_Doctrine/About/About.xml`
          names the mod in **loadAfter**, not `modDependencies`, which exerts no
          constraint on an inactive mod and logs nothing — leave it. The mod folder stays
          on disk, unlisted not unsubscribed.
verify:   `grep -rn "RG_BoilingForest\|BoilingWater\|regrowth.botr.boilingforest" src/Jawa/`
          returns only the harmless `loadAfter` line in `Jawa_Doctrine/About/About.xml`;
          `validate_patch.py` on `JawaWorld_BiomeMix.xml` still reports OK.
criteria: no `Could not resolve cross-reference` naming an `RG_` biome at the next load,
          and the biome mix behaves as authored with the entry gone.
state:    ready

## repoint-salvation-rid-provenance-at-the-live-set-7d3c11
row:      10
spec:     🔴 **Owner asked for this directly, 2026-08-15: "Can you modify Salvation.rid to
          match our current mod configuration?"** Routed by REP with the diff already
          measured, so no rediscovery.

          `src/Jawa/ideoligion/The Salvation.rid` is `<savedideo>` with two blocks. Only
          `meta` changes. `ideo` — 5 memes, **101 precept entries**, culture, style — is
          NOT touched by this item.

          `meta` holds three PARALLEL 585-entry lists that must stay index-aligned:
          `modIds`, `modSteamIds` (7 of 585 non-zero; the rest are `0`), `modNames`.
          Measured against live `ModsConfig.xml` (575 active):
          - **11 in the file that no longer load:** `zal.giantsnake`,
            `abrolo.grimstone.beasts`, `rah.rvte`, `guppyfacesarecute.skunks`,
            `vanillaexpanded.vanillaanimalsexpanded`,
            `honeybadger.wallmountedturretsversiontwo`, `regrowth.botr.boilingforest`,
            `redmattis.sapientanimals`, `neronix17.outerrim.galacticdiversity`,
            `guy762.starwarsxenotypes`, `btd.xenotyperemix.starwars`
          - **2 live mods absent from it:** `mandrake.starwarsraces`,
            `mandrake.jawaplantgrowth` (deployed today)
          - **Order does not match either**, so rebuild the lists from `activeMods` order
            rather than patching entries in place. Names and steam ids come from each
            mod's `About/About.xml` + `About/PublishedFileId.txt`; a local mod has no
            PublishedFileId and takes `0`, which is why 578 of them are `0`.
          Also `meta/gameVersion` is `1.6.4871 rev591`; live `ModsConfig` reads rev590.
          Say which you wrote and why.

          ⚠️ **State plainly in the commit that this is PROVENANCE ONLY.** The block is
          what drives RimWorld's "made with mods you do not have" warning. Rewriting it
          silences that warning without touching a single precept — and under C42 the 82
          precepts are UNMEASURED, so that warning is currently the only signal we have
          that something in this artifact is stale. It is not a fix and must not be
          recorded as one.
verify:   the three lists are 575 long, index-aligned, in `activeMods` order; the file
          still parses as XML; `ideo` is byte-identical to `b206272` apart from nothing —
          diff it and prove only `meta` moved.
criteria: the ideoligion loads with no missing-mod warning AND C42's precept count is
          unchanged by this edit — if precepts change, this item did something it should
          not have.
state:    done 2026-08-15 — PROVENANCE ONLY, `ideo` byte-identical (101 precepts,
          5 memes, unchanged). Three lists rebuilt from live `activeMods` order:
          **576, not the 575 this spec says** — it was written before
          `mandrake.jawaplantgrowth` deployed today. Spec also named 2 absent mods;
          there were **3** (it missed `HalituisAmaricanous.gravtechbigcannons`) and
          12 dead, not 11.
          🔑 `modSteamIds` comes from `About.xml` `<steamAppId>`, NOT
          `PublishedFileId.txt` as the spec says. Measured: that reproduces the
          file's own 7 non-zero ids exactly; PublishedFileId would have put a
          number in ~553 rows that RimWorld writes as `0`.
          🔑 `gameVersion` LEFT at `1.6.4871 rev591` deliberately. Live ModsConfig
          reads rev590, but rev590 is the stale side — `Version.txt` is stamped at
          install and every file the engine writes (DefDump manifest, all six
          saves, this file) reads rev591.
          ⚠️ 19 empty `<li>` reported by the validator PRE-EXIST and sit in `ideo`,
          not `meta`. Not introduced here, not fixed here.


## nomatch-add-assumes-a-container-that-may-be-inherited-7b1e4c
row:      tooling
spec:     The sequel to B22, and a different case from it. B22 catches a `<nomatch>`
          whose xpath is IDENTICAL to the test — provably dead, no `--defs` needed.
          This is the case where the `<nomatch>` `PatchOperationAdd` targets the
          **parent container** of the test xpath, which is the legitimate
          add-if-missing idiom and therefore only a WARN today:
            test:  /Defs/ThingDef[defName="X"]/statBases/MeatAmount
            inner: /Defs/ThingDef[defName="X"]/statBases
          🔴 It is fatal exactly when the def **inherits** that container instead of
          declaring it. Patches run on RAW XML, so the Add matches nothing, returns
          false, and `PatchOperationSequence` stops — every op after it in the block
          silently never runs. Cost us `DA_Taraal` + `DA_SnowTaraal` and one load's
          worth of wrong diagnosis (B59).
          THE CHECK: with defs loaded from RAW XML (not a resolved dump, which
          cannot tell inherited from owned), resolve the inner xpath's container
          against the def's OWN node. Absent ⇒ ERROR, not WARN.
          ⚠️ **This warning currently fires 1,145 times on one file.** A warning that
          fires a thousand times is not a warning — whatever shape the fix takes, it
          has to end with the fatal cases distinguishable from the safe ones, or the
          signal stays buried exactly where it was buried this time.
verify:   a synthetic def that inherits `<statBases>` is flagged ERROR with raw-XML
          defs; a def that declares its own stays at WARN or better; the count on
          `Jawa_Doctrine/Patches/MegafaunaYield.xml` drops from 1,145.
criteria: `validate_patch.py` on `src/Jawa/Jawa_Doctrine` names any def whose
          add-if-missing container is inherited, and names no def whose is owned.
state:    ready

## bridge-cannot-order-a-melee-attack-3f8c21
raised:   2026-08-15 CHECK, after C43 failed to collect on a live quicktest map.
ask:      One bridge verb that issues an ATTACK job — `JobDefOf.AttackMelee` against a
          named target (and ideally `AttackStatic` for ranged). Everything else needed to
          stage a combat observation already exists; this is the only missing piece.
why:      There is no way to make a pawn swing on command. Measured, not assumed:
          · a DRAFTED colonist holds at `Wait_Combat` indefinitely;
          · `jawa/order_pawn` issues a GOTO whether given `targetId` or the enemy's cell;
          · pawns from `jawa/spawn_pawn` carry **no lord**, so hostiles idle forever;
          · `Actions\Spawn large enemy raid` + 5,600 stepped ticks never produced an
            engagement at the drafted pawn.
          So any item whose criterion is "what does X look like DURING an attack" is
          uncollectable unattended today — C43 is the first, and it will not be the last.
scope:    ⛔ I am not designing it. Named here because CHECK found the gap, per POLICY.
          The equip half is already solved and needs nothing:
          `Actions\Equip primary (selected)...\<WeaponDefName>` after `select_pawn`.

## sled-tint-loses-to-the-vehicle-pattern-4d90ae
row:      2
from:     C39's colour failure (CHECK, `412f5c3`). Diagnosed offline by BUILD
          2026-08-15 — CAUSE (b), and the mechanism is named.
spec:     🔴 **DIAGNOSIS, not a build order. The owner has said to leave
          `DesertVehicleReskin` exactly as deployed, so NOTHING here is actioned
          until he says otherwise.**
          C39 photographed the prop warm BROWN and the vehicle TEAL. CHECK offered
          two candidates and declined to choose. It is (b) — the tint reaches
          `AV_DogSled` and is overridden — and the override has a name:

              <graphicData>
                <shaderType>CutoutComplexPattern</shaderType>
                <pattern>AV_Pattern_Wood</pattern>      <-- THIS
              </graphicData>

          in the donor,
          `…\294100\3028675048\1.6\Defs\VehicleDefs\Tier0\DogSled\DogSled_VehiclePawn.xml`.
          🔴 **A Vehicle Framework `<pattern>` REPLACES the mask.** Under
          `CutoutComplexPattern` the RGB regions that decide where colorOne /
          colorTwo / colorThree land come from the PatternDef's texture
          (`Vehicles.PatternDef AV_Pattern_Wood`, `path` =
          `Patterns/WoodGrain/AV_Pattern_Wood`, and it carries **no colours of its
          own** — it is pure mask), **not** from the `_m.png` we ship beside the art.
          ⇒ `DogSledTint_Brown.xml`'s central assumption is void for the vehicle.
          Its header states *"only `<color>` can actually reach a pixel under OUR
          mask — colorTwo and colorThree have no green/blue region to act on."*
          Under the wood-grain pattern they have plenty, so all three of our browns
          land in tiled regions we never designed, and the mix is the teal.
          WHY THE PROP IS FINE AND THIS IS THE WHOLE MIRROR: `VFEPD_DogSled` is a
          plain `ThingDef` with a `<color>` and **no pattern**, so our shipped mask
          governs and the tint lands. Same patch, two rendering paths.
          THE CANDIDATE FIX (unbuilt, untested): patch `<pattern>` on `AV_DogSled`
          to VF's solid/default pattern so our two-value mask governs again, rather
          than touching the colour triple, which is already correct.
          ⚠️ Verify before building: the `PatternDefs.xml` that defines
          `AV_Pattern_Wood` lives ONLY under the donor's `1.5/` folder, not `1.6/`.
          Confirm through `LoadFolders.xml` that 1.5 is loaded for 1.6 before
          concluding anything about which pattern defs exist at runtime.
verify:   EMPTY — nothing to verify until the owner reopens the mod.
criteria: EMPTY
state:    🔴 DEAD — not blocked, not deferred. **Owner's ruling 2026-08-15: "Accept
          the dog sled as-is. No further testing."** C39 CLOSED (`fddb832`).
          ⇒ **The teal vehicle is the SHIPPED LOOK, not a defect.** Nothing above is
          work waiting for a window; the "candidate fix" is not to be built. The
          diagnosis is kept only as the explanation of *why what shipped looks the
          way it does*, so nobody re-opens it as a bug in six weeks.
          ⛔ Do not chase the tint.

## gand-and-chagrian-missing-artwork-5d2a09
raised:   2026-08-15 CHECK, from the owner examining the 70-race grid live on the
          scratch quicktest map.
finding:  THREE species named across two separate looks, and the pair is NOT the same
          both times — record all three, do not collapse them:
            `RimMandrakeGand`      — named BOTH times. The solid one.
            `RimMandrakeChagrian`  — named on the owner's OWN earlier grid (the one he
                                     saved as `racetest`), NOT on mine.
            `RimMandrakeSelkath`   — named on MY 70-race grid, NOT on his.
          Owner's words, in order: *"Gand and Chagrian have missing artwork, but most now
          look good."* then, on the new grid: *"Gand and Selkath show missing art in your
          new grid."*
          ⚠️ Two grids, two different second names. Either the fault is not deterministic
          per species, or one of the two was a misread at a glance — **check all three**,
          and do not assume Chagrian is clean because the second look did not name it.
          All SPAWN fine — 70/70 xenotypes spawned, so this is art only, not defs or genes.
scope:    ⛔ Not triaged and not diagnosed by me — the owner looked, I am recording it.
          Whether it is a texPath that does not resolve, a missing PNG, or a head/body
          type with no graphic is BUILD's to find.
⚠️ do not assume the log will show it:
          `texture path failures` read **0 = baseline 0** in this load's harvest, and
          that check fires ONLY when ALL directions are missing — a partial set is
          silent. A clean log is not evidence against this finding.
note:     Owner's verdict on the rest of the grid was positive — *"most now look good"* —
          so this is two exceptions in 70, not a systemic art problem.

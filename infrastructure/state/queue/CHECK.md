# CHECK inbox.

## C-V2 Park any v2 idea in design/V2_DREAMS.md yourself — no permission needed
row:      doctrine
spec:     Any idea for new content that is not v1 — including one a live session
          suggests — is appended to the END of `design/V2_DREAMS.md`. You have a
          standing right to append there directly: no permission, no routing through
          DECIDE, no queue item asking for it, no format and no field contract.
          Never queue v2 work.
verify:   read the header of `design/V2_DREAMS.md` once; it says the same thing.
criteria: EMPTY — that file is not a queue and nothing in it is scheduled.
state:    ready


## C1 Run the bridge tools that were built but never once called
row:      tooling
spec:     `python.exe src/RimMandrake/bridgetools/prove_new_tools.py --pawns` covers `jawa/set_pawn_rotation`, `jawa/set_pawn_style`, `jawa/set_pawn_xenotype` and `xenotype=` on `spawn_pawn` (`7b8d5b7`, `e60197a`). Also deployed and never called: `jawa/get_defs`, `jawa/fire_quest`, `jawa/list_things` (`3adedbc`), `jawa/clear_ui` (`9a5b6fe`), the vehicle route in `spawn_batch` (`9a5b6fe`, routes `Vehicles.VehicleDef` through `Vehicles.VehicleSpawner.SpawnVehicleRandomized` by reflection — `ThingMaker` leaves `vehiclePather`/`ignition`/`drawTracker`/`kindDef` null), and the roof pair `set_roof_batch`/`get_roof_batch`. `jawa/world_stats` WAS called and its answer was discarded by a harness `NameError` (fixed `3e17731`) — re-run it. Do not compose calls at a live console: run `python.exe src/RimMandrake/bridgetools/load_session.py --phase any|fresh` (`--selftest` needs no game); it writes one ledger to `observed\<date>_load_session.md` and tracks LITTER, from which the release message is written.
verify:   EMPTY
criteria: each tool returns success on a live map; `world_stats` returns `{ tiles, pct, perimeter, raggedness, centroidLat }`. A capability is announced to peers when it has RUN, not when it has compiled.
state:    doing
result:   2026-08-15 CHECK. EVERY never-run tool has now RUN on a live map:
          jawa/world_stats PASS · jawa/get_roof_batch PASS · jawa/set_roof_batch PASS
          (None -> RoofConstructed -> reverted, each verified by read-back) ·
          jawa/fire_quest PASS (Jawa_TheClaim registered as quest 0, State=NotYetAccepted,
          800 points) · the spawn_batch VEHICLE route PASS · plus get_defs,
          set_pawn_xenotype, list_things, clear_ui and inspect_string earlier.
          🔑 set_roof_batch takes `ops` ("RoofConstructed:x,z,w,h"), NOT rects+roof.
          Passing rects+roof returns "ops is required" - a clean refusal, not a silent
          no-op, and get_roof_batch's own `ops` output feeds straight back in as the undo.
          🔑 A VEHICLE spawned by spawn_batch arrives as a PAWN. jawa/list_things saw
          NOTHING at the cell; jawa/list_pawns shows AV_DogSled_PawnKind at (72,72).
          Checking list_things alone would have read as a silent failure.
          🔴 CRITERION NOT MET, so this stays open: world_stats does NOT return
          { tiles, pct, perimeter, raggedness, centroidLat }. Live keys are
          tilesTotal, waterTiles, waterPct, landPct, coastalTiles, bodiesOverMinSize,
          bodiesTotal, minBodySize, largestBodyPct, bodies, bodiesListed, biomes,
          previewOnly, seedString, planetCoverage, overallRainfall, overallTemperature.
          NO perimeter, NO raggedness, NO centroidLat. C16's gate needs those three and
          cannot be scored until the deployed tool emits them - BUILD's to answer.

park:     2026-08-15 PARTIAL PARK. The pawn-APPEARANCE trio (set_pawn_rotation / set_pawn_style /
          set_pawn_xenotype) and `xenotype=` on spawn_pawn are racial - hold them until the new
          races land, then prove them against those. The REST of C1 is unaffected and still
          live: jawa/fire_quest, set_roof_batch/get_roof_batch, the spawn_batch vehicle route,
          and the world_stats re-run.

note:     2026-08-14 CHECK. Ran load_session.py --phase any: 30 items, 4 failed, 14 awaiting eyes; ledger observed/2026-08-14_load_session.md. get_defs, set_pawn_xenotype, list_things, clear_ui now RUN live. Still unrun: fire_quest, set_roof_batch/get_roof_batch, the spawn_batch vehicle route. Two harness items die on UnicodeEncodeError (charmap) before asserting - A6 Cherry Picker and P5 VAEA_Apparel_ToolBelt - so those are UNMEASURED, not passed. 14 screenshots need a human look.

## C17 At worldgen, untick the 21 factions that break the fiction
row:      10
spec:     `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` (`c269c6a`) — 21 untick / 6 keep, ratified, committed and UNSPENT. Executed by unticking factions on vanilla's Configure Factions page DURING the worldgen run; that page is seen ONCE and there is no fixing it afterwards without regenerating the world. Four rulings ride in the file header: R1 dangling refs, R2 Rebel Alliance stays suppressed, R3 vanilla `Empire` is a KEEP, R4 rough-outlander floor. There is no file we can write to suppress a faction — Faction Control's `density` is a CLUMPING RADIUS (`__result = dist < fd.Density;`), not a count, and the English key "setting to 0 disables the faction" is a pre-1.3 leftover. Before calling any missing faction a defect, grep `Jawa_Patches/` for its defName.
verify:   EMPTY
criteria: the generated world's faction roster matches the keep list. A quicktest map's roster PROVES NOTHING — a debug quicktest never visits the Configure Factions page, so every faction is present by default. State which map any census came from. Prior scale, from the deleted world: 53 factions across 107 settlements, of which the fiction-breakers held ~34.
state:    ready


## C21 Follow The Claim quest to an end — registering is not finishing
row:      13
spec:     Spawn `Jawa_ClaimRumour` (`Jawa_ClaimRumour.xml:89-91` hands out `Jawa_TheClaim`, `rootMinPoints 0`), read it, and follow the quest to resolution. The quest already REGISTERS via `jawa/fire_quest questDef=Jawa_TheClaim points=800` — id 0, "The Claim", `State=NotYetAccepted`, `questCountAfter 1`, challengeRating 1, expiry 256,099 ticks, every field read back off `Find.QuestManager` after the call. The in-world-item route needs `rimworld/right_click_cell`, which is measured broken.
verify:   EMPTY
criteria: the quest fires from the rumour and RESOLVES — registration is not resolution.
state:    blocked

## C31 Confirm our four Jawa pawn types actually spawn
row:      7
spec:     From BUILD B6. `Jawa_Colonist`, `Jawa_Tribal_Scavenger`, `Jawa_Tribal_Slinger`,
          `Jawa_Tribal_Elder` shipped with `ParentName` pointing at vanilla DEFNAMES
          (`Colonist`, `Tribal_Berserker`, `Tribal_Archer`, `Tribal_ChiefMelee`), none of
          which carry a `Name=`. All four were discarded at load with nothing in the log,
          taking every `pawnGroupMakers` entry in `JawaTribes.xml` with them. Repointed to
          `BasePlayerPawnKind` (Colonist's own body restated inline), `TribalWarriorBase`,
          `TribalArcherBase`, `TribalChiefBase` — `c06e89e`, deployed, needs a COLD LOAD.
criteria: a Jawa colonist and an indigenous tribal spawn as `MandrakeJawa`; no other Jawa
          xenotype generates; the `Jawa_IndigenousTribes` faction produces a non-empty
          raider group. Read the four defNames back with `jawa/get_defs` — absence is the
          failure mode, and it is silent.
state:    blocked
park:     2026-08-15 OWNER: PARKED. A whole new range of RimMandrake Star Wars races is about to land. Do not verify racial state against the CURRENT stack - any result is about to be invalidated, and inherited pre-existing racial content especially. Re-base this item on the new mod when it ships, then re-run.
          Already banked and NOT to be redone: the four kinds generate 24/24 as MandrakeJawa. Only the untested raider-group criterion carries forward.

note:     2026-08-15 CHECK, live on the post-deploy map.
          ✅ CRITERION 1+2 PASS: spawned 6 of each of the four kinds, 24/24 generated
          as xenotype `MandrakeJawa` - Jawa_Colonist, Jawa_Tribal_Scavenger,
          Jawa_Tribal_Slinger, Jawa_Tribal_Elder. The c06e89e repoint works end to end;
          defs resolve AND generate.
          ⚠️ CRITERION "no other Jawa xenotype generates" is NOT SETTLED, and my earlier
          claim that it was "unmet by construction" is withdrawn. Facts: the six
          OnlyMandrakeJawa.xml patch ops DO die at load (PatchOperationAddOrReplace is
          not a real type, 12 log lines) - but the intended end state may hold anyway.
          On this load `OuterRim_Jawa` and `guy762_xenotype_jawa` DO NOT EXIST, and
          `BTD_Jawa` already reads factionlessGenerationWeight 0.0 / canGenerateAsCombatant
          False. The read does not discriminate: `MandrakeJawa`, which MUST generate,
          reads the same 0.0/False. ⇒ needs a generation-based test, not a field read.
          ⏳ CRITERION "Jawa_IndigenousTribes produces a non-empty raider group" untested -
          needs a raid fired at a live colony, which is an owner call.

note:     2026-08-15 CHECK. DEF HALF PASSES on the post-deploy cold load: all four
          resolve via jawa/get_defs at the MAIN MENU, before any map existed -
          Jawa_Colonist, Jawa_Tribal_Scavenger, Jawa_Tribal_Slinger, Jawa_Tribal_Elder,
          all race=Human. The repoint in c06e89e took. REMAINING (needs a map): they
          must actually GENERATE as MandrakeJawa, no other Jawa xenotype may generate,
          and Jawa_IndigenousTribes must produce a non-empty raider group.

## C34 You hold the live bridge at all times — standing rule
row:      doctrine
spec:     Owner ruling 2026-08-14. `infrastructure/agents/CHECK.md` updated: the
          Live Bridge is yours with no window in which another seat holds it, and
          `infrastructure/state/status/game.json` is yours to keep true. Stamp it
          on every transition — game up, state change, game down. Fields:
          state (PLAYABLE|LOADING|DOWN) · by: CHECK · at: epoch · note · left · lease.
          Its stale `by: BRIDGE` is already corrected to CHECK; `at` is still
          1786744923 and the note still reads "BRIDGE idle" — restamp it yourself.
verify:   `python3 -c "import json;d=json.load(open('infrastructure/state/status/game.json'));print(d['by'],d['state'],d['at'])"`
          shows CHECK, a current state, and an `at` you wrote.
criteria: The board's GAME panel matches the real game across one up→down
          transition, and does not flag STALE while the process is resident.
state:    doing
note:     2026-08-14 CHECK. Restamped: `by CHECK`, `at 1786770877` (was BRIDGE's
          1786744923), note no longer "BRIDGE idle", and `left` refreshed — the old
          one claimed "0 pawns" when the map now has Alex (PlayerColony), plus the
          moved thruster bank and the rewired power net. `verify:` PASSES
          (`CHECK PLAYABLE 1786770877`). **Not done:** the criteria needs one
          up→down transition and the game is still up, so the DOWN half is unproven.
          Stays `doing` until I stamp it down and the panel agrees.

## C15 Finish measuring the ocean — 3 of 7 seeds still unread
row:      v2
spec:     —
verify:   —
criteria: —
state:    dropped — Worldgen is manual and the sea left v1. Full text in `design/V2_DREAMS.md`.

## C16 Score the ocean against its spec
row:      v2
spec:     —
verify:   —
criteria: —
state:    dropped — Worldgen is manual and the sea left v1. Full text in `design/V2_DREAMS.md`.

## C35 Confirm the faction xenotype sets read back as Star Wars species
row:      9
spec:     Per `FACTION_SPEC.md` R27. Six factions had `xenotypeSet` INHERITED
          from their vanilla abstract before the fix — `OutlanderFactionBase`
          ships five vanilla xenotypes, `PirateBandBase` nine. On the next live
          game, read each faction back and confirm no member generates as
          Hussar, Dirtmole, Genie, Neanderthal, Starjack, Waster, Pigskin or
          Impid.
          ⚠️ Also verify the `BTD_` prefix actually resolves. Three packs ship
          overlapping xenotypes and BTD Remix dedups at LOAD, so a disk-derived
          name is not proof. `BTD_Jawa` surviving while `OuterRim_Jawa` does not
          is the measured precedent this rests on; if a `BTD_*` name is missing,
          the fallback is `guy762_xenotype_*`, never `OuterRim_*`.
verify:   none — live read only.
criteria: `jawa/get_def defType=FactionDef` on each of the six shows only the
          intended species; a spawned member of each is visibly the right race.
          🔴 A def dump is DISK, not RUNTIME — only the live game settles this.
state:    blocked
park:     2026-08-15 OWNER: PARKED. A whole new range of RimMandrake Star Wars races is about to land. Do not verify racial state against the CURRENT stack - any result is about to be invalidated, and inherited pre-existing racial content especially. Re-base this item on the new mod when it ships, then re-run.

## C36 Prove the races mod stands with all three donor mods switched off
row:      9
spec:     New standalone mod `src/Jawa/RimMandrake_StarWarsRaces` (packageId
          `mandrake.starwarsraces`), generated by
          `src/RimMandrake/Utils/gen_races_mod.py`. 69 XenotypeDefs, 69
          PawnKindDefs (`RimMandrake<Species>_Kind`), 109 GeneDefs, 118
          HeadTypeDefs, 22 abstracts, 43 support defs, 712 PNGs. Contains no
          assembly. Deploy it, then switch OFF `guy762.StarWarsXenotypes`,
          `Neronix17.OuterRim.GalacticDiversity` and `BTD.XenotypeRemix.StarWars`
          and load.
          ⚠️ Nothing has been deployed. The repo copy is not what the game loads.
verify:   `python3 src/RimMandrake/Utils/gen_races_mod.py` re-derives the mod and
          prints `references that die 0` / `dangling texture paths 0`.
          `validate_patch.py` on the mod: 0 errors.
criteria: With the three donors off, the log carries no `Could not resolve
          cross-reference` naming a `guy762_`, `OuterRim_` or `BTD_` def, and no
          `Could not find type named`. Spawn one pawn per species from the
          `_Kind` defs and confirm each renders a head and eyes rather than a
          bald vanilla human. The Jawa (`MandrakeJawa`) must still roll three
          glowing eye colours, all three now from
          `RimMandrakeSW/Jawa/jawaeyes_glow`.
          NAMES AND PAWN KINDS ARE NOW IN SCOPE FOR THIS SAME LOAD. The mod owns
          48 RulePackDefs and their word lists under
          `Languages/English/Strings/RimMandrakeSWNames/`, and 50 of the 69
          species carry a `nameMaker`; check a spawned Twi'lek, Wookiee and Jawa
          get species names rather than vanilla ones. It also owns 16 Galactic
          Diversity pawn kinds as `RimMandrake_<Species>` / `_<Species>Tribal`,
          which every Jawa_Patches FactionDef now fields instead of the
          `OuterRim_` originals, so a raid or trade caravan from Wildsteam Clan,
          Deepwater Compact, Ascendant Helix, Hutt Cartel, Junkers or Geonosian
          Foundry Hive must arrive as the right species and not as an empty
          group.
state:    ready

## C37 VALIDATION PLAN — can we spawn all 70 RimMandrake races?
row:      9
spec:     The owner is NOT playing this load. The whole test is: open debug mode
          and spawn one of every `RimMandrake*` xenotype. Wiring them into
          factions and worldgen is a later job; do not test that here.

          WHAT SHIPPED, and it is a first load for all of it:
          `mandrake.starwarsraces` (866 files) — 70 XenotypeDefs, 87 PawnKindDefs,
          114 genes, 104 head types, 48 RulePackDefs, 140 name word-lists,
          713 textures. 🔴 The three donor mods it replaces are SWITCHED OFF:
          `btd.xenotyperemix.starwars`, `guy762.starwarsxenotypes`,
          `neronix17.outerrim.galacticdiversity`. activeMods 578.

          THE ROUTE, exact. Either works; the bridge one is cheaper:
            bridge:  `jawa/spawn_pawn` kindDef=`Colonist` x=<X> z=<Z>
                     faction=`PlayerColony` xenotype=`RimMandrake<Species>`
                     ⚠️ OMITTING `faction` SPAWNS INTO **Empire, HOSTILE** —
                     and Empire is now a permanent enemy. Always pass it.
            dev:     Debug actions -> `Actions\Spawn Pawn...\<PawnKindDef>`,
                     using the 69 `RimMandrake<Species>_Kind` defs, which exist
                     for exactly this and take the xenotype with them.
          The 70 defNames are in
          `src/Jawa/RimMandrake_StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`
          (plus `MandrakeJawa`). `lineup.json` in the repo root has a working grid
          layout from a previous run.

verify:   🔴 PREDICTION, written before the look: **70 of 70 spawn, and each pawn
          renders as its species rather than a bare human.** Positive observations,
          not absences:
          1. the pawn EXISTS and its xenotype reads back as the one requested
             (`jawa/list_pawns`, or click it and read the Bio tab);
          2. it does not look like a baseliner — the species-specific part is on
             screen: Ithorian hammerhead, Chagrian lethorns, Trandoshan scales,
             Gungan eyestalks, Lasat ears and yellow eyes;
          3. it has a NAME from its own namer, not a vanilla human name. 51 of the
             70 carry one — the other 19 correctly fall through to vanilla, so a
             vanilla name is only a failure on one of the 51.
          Screenshot the grid. `jawa/clear_ui` FIRST or the debug window sits on
          the subject.

          HOW THIS CHECK LIES — four ways, all seen this week:
          - **A dangling gene degrades quietly.** A species missing one gene still
            spawns and still looks broadly right; only the specific feature is
            gone. So check the FEATURE named above, not merely that a pawn appeared.
          - **A missing head type falls back to a human head** with the rest of the
            genes still applied — the pawn looks odd rather than absent, and reads
            as art we should improve rather than a broken reference.
          - **Deployed is not live.** All of this was written to the game folder
            while the previous process was running. If the process did not restart
            after 07:35, it is testing the OLD content. Compare the Mods folder
            mtime against the process StartTime before believing any result.
          - **The def dump is disk, not runtime.** `RimMandrake*` present in a dump
            does not mean present in the process — a mod's Harmony patch can delete
            defs at load, which is exactly what BTD was doing to these species
            until today.

criteria: 70 of 70 spawn with the right xenotype and a species-appropriate body.
          A species that spawns as a plain human is a FAILURE — name it. A species
          that fails to spawn at all is a worse failure — name it and quote the
          log line. Report the failures by defName; do not summarise as a count.
          NOT IN SCOPE, deliberately: faction generation, worldgen, raids, whether
          any of them appear organically. 37 of the 70 are named by no faction and
          `factionlessGenerationWeight` is 0 on all of them, so NONE of this is
          expected to occur in normal play yet. That is the later wiring job.
state:    doing
spawned:  2026-08-15 CHECK. 70 OF 70 SPECIES SPAWN with the right xenotype.
          The 5 that missed the first pass (MandrakeJawa, Abednedo, Anzati, Bith,
          Mirialan) ALL came back correct on re-spawn, which confirms the owner's
          early-game substitution artifact rather than any mod defect: RimWorld
          substitutes plain colonists until the 8-colonist quota is met, and the map
          showed exactly 8 Baseliners with 4 of the 5 in the first 6 spawn slots.
          ⇒ NEVER name a species as failing to generate from ONE spawn pass.
          🔴 THE ART FAILURE IS FACIAL ANIMATION, not the gene migration. FA overdraws
          the face; its per-xenotype opt-out is keyed by defName and every one of the 86
          entries still read Human-BTD_* / Human-OuterRim* / Human-guy762_*, so all 70
          renamed species were unprotected at once. Fixed: 70 Human-RimMandrake* entries
          added (86 -> 156), both sides committed under deployed/config/. NEEDS A RESTART.
          Full mechanism written into skills/rimworld-xenotypes SKILL.md 3b.
          ⚠️ My earlier head-gene diagnosis is DEMOTED to secondary: the Rodian snoot
          ships and is wired (HeadAttachments/rodian) - FA was covering it. Still true
          separately: 5 species have no head or face genes at all (Arkanian, Chiss,
          Echani, Kaleesh, Zeltron) and Rodian's only head-TYPE forcer is the generic
          Outland_ScaleSkin. Re-judge both AFTER the FA fix is live.

result:   2026-08-15 CHECK. ROOT CAUSE FOUND for the wrong-looking pawns.

          WHAT PASSES (measured, not assumed):
          - Gate 1: process started 07:56:41, AFTER ModsConfig 07:47:12. Valid load.
          - 70 of 70 XenotypeDefs resolve IN THE RUNNING PROCESS. No BTD-style
            runtime deletion. The donors-off configuration works.
          - 33 of 33 genes the offline scan could not see resolve live.
          - 112 RimMandrake_* genes referenced, 113 defined. Zero dangling.
          - Zero species depend on a gene from a switched-off mod.
          - 65 of 70 species spawned on the map first try.

          🔴 ROOT CAUSE OF THE ART FAILURES — gen_races_mod.py read the WRONG SOURCE.
          Its docstring says "Source preference BTD, then SWX, then Outer Rim", and it
          picks with `src = next((c for c in cand if c and c in x))` where `x` is the
          LIVE DEF DUMP. That dump was taken with BTD ACTIVE, and BTD's whole job is
          deleting the SWX and Outer Rim duplicates. So the alternatives were already
          gone from `x`: the fallback could never fire, and EVERY species was composed
          from BTD's gene list. BTD's lists are missing head-TYPE genes the other
          donors carried.
          Evidence, read off the donors' own XML on disk:
            BTD_Rodian             30 genes  head: guy762_Headbone_rodian          (bone only)
            guy762_xenotype_rodian 15 genes  head: guy762_Head_rodian + Headbone   (the snoot)
            OuterRim_Iridonian     head: OuterRim_IridonianHead
            BTD  Iridonian         head: guy762_Headbone_zabrak                    (bone only)

          🔴 IMPACT A — 10 of 69 have NO head-forcing gene at all, so they render with a
          plain human head. Asked the RUNNING game for forcedHeadTypes on all 414 genes
          our xenotypes reference; 41 force a head. The 10 without:
            RimMandrakeAnzati, RimMandrakeArkanian, RimMandrakeChagrian,
            RimMandrakeDevaronian, RimMandrakeEchani, RimMandrakeFalleen,
            RimMandrakeIridonian, RimMandrakeKaleesh, RimMandrakeYoderForceGremlin,
            RimMandrakeZeltron
          🔴 IMPACT B — WORSE, because it looks deliberate. RimMandrakeRodian DOES force
          a head, but the forcing gene is `Outland_ScaleSkin` -> head type
          `Outland_ScaleSkin` (Things/Pawn/Humanlike/Heads/Scaleskin/Normal): a GENERIC
          reptile head from Outland Genetics, not a Rodian one. Owner's words: "where's
          their snoot". Any species whose only head-forcer is a generic donor gene is in
          this class and a headless-count alone will not find it.

          RULED OUT, so nobody re-checks them: textures (Hutt's Male/Female_FatHead PNGs
          all present at the exact path the def names, 713 deployed); missing defs;
          dangling genes; and the three switched-off donors taking anything with them.

          ⚠️ NOT a defect: early spawns are substituted with plain colonists until the
          8-colonist quota is met - owner's warning, and the map showed exactly 8
          Baseliners with 4 of the 5 absent species sitting in the first 6 spawn slots.
          A species missing from ONE spawn pass is not evidence. Re-spawn after the
          quota fills before naming any species as failing to generate.

## C38 VALIDATION PLAN — planetary fast growth, and the terminator case that proves it
row:      2
spec:     Ships `mandrake.jawaplantgrowth` (`src/Jawa/JawaPlantGrowth/`), a NEW
          assembly: one Harmony postfix on the `Plant.GrowthRate` **getter**
          multiplying `__result`. Three bands, biome-aware, in that order:
          terminator biome -> x0.4, else tree -> x2.5, else -> x4.0.
          🔴 It scales the COMPOSITE `GrowthRate`, not a `GrowthRateFactor_*`, so
          light/temperature/fertility/drought penalties still apply and the
          terminator case genuinely lands BELOW vanilla.
          Every number, the terminator biome roster and the exempt list are in
          `src/Jawa/JawaPlantGrowth/Defs/JawaPlantGrowthSettings.xml` and are read
          at startup — retuning is an XML edit and a restart, never a rebuild.
          Terminator roster today: `PoisonForest` only (Advanced Biomes
          (Continued), `mlie.advancedbiomes`, active). Exempt in EVERY biome:
          `Plant_TreeAnima`, `Plant_TreeGauranlen`, `Plant_Ambrosia`, and any plant
          whose `growDays` is under 1.0.
          ⛔ Player crops are NOT exempt, by spec. The limit on farming here is
          WATER, not time.
          R-G4 (`BiomeDef.wildPlantRegrowDays`) is NOT in this drop — it is blocked
          on the owner's biome cut list. Wild plants will grow fast but will NOT
          repopulate a burnt map any faster yet. Do not read that as a failure.
          ⚠️ NOT DEPLOYED. RimWorld was running, so the DLL could not be written to
          `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`. It needs
          `deploy_custom_mods.py --mod JawaPlantGrowth --apply` in a shutdown
          window, and `mandrake.jawaplantgrowth` added to ModsConfig AFTER
          `brrainz.harmony`, before this can be checked at all.

verify:   ITEM     Plant growth is x4.0 wild/crop, x2.5 tree, x0.4 on PoisonForest
          SEE      The plant inspect pane's growth-rate readout (it is computed
                   from the same getter we patch, so it shows the boosted number),
                   plus the one-line startup message
                   `[JawaPlantGrowth] scaling <N> plant defs (default x4, tree
                   x2.5), <M> exempt, 1 terminator biome(s) at x0.4.`
          ROUTE    Quicktest map (~90 s, per R-G6 — do NOT spend a cold load).
                   1. Temperate/arid quicktest. Spawn `Plant_Corn` and
                      `Plant_TreeOak` side by side on fertile soil, note growth %
                      on each, run 1 in-game day, read both again.
                   2. NEW quicktest on `PoisonForest` (Advanced Biomes). Same two
                      plants, same day. This is a SECOND map — a biome branch
                      cannot be tested by walking across the first one.
                   3. Spawn `Plant_TreeAnima` on map 1 and read its rate.
          PREDICT  Written before the look, as ratios against the same plant on the
                   same map with the mod off — but the cheap in-run form is the
                   ratio BETWEEN plants, which needs no vanilla baseline:
                   - corn `growDays` 11.3 -> reaches harvest in ~2.8 days
                   - oak `growDays` 30 -> ~12 days, so after one day the corn is
                     ~36% grown and the oak ~8%. **The corn must be roughly 4x the
                     oak's growth percentage.** Anything near 1x means the tree
                     band is not firing.
                   - 🔴 On PoisonForest the corn gains ~10% in that same day —
                     LESS than the ~36% on map 1 and less than the ~8.8% vanilla
                     would give. Slower, not faster. This is the check most likely
                     to be skipped and the only one that proves the biome branch
                     runs at all.
                   - `Plant_TreeAnima` growth % after one day matches an unpatched
                     anima tree: ~4% (25 growDays), NOT 10%.
          CLOSE    All four numbers land in band on ONE pass — NOT chasing: the
                   exact percentages (fertility, light and temperature move them),
                   wild-plant REPOPULATION rate (that is R-G4 and it did not ship),
                   or the Gauranlen/ambrosia exemptions (same mechanism as anima).
          RIDE     🔴 solo. A new assembly. If the load comes up wrong, nothing
                   separates the DLL from anything shipped beside it.
          LIES     Four ways this produces a false pass:
                   - **The postfix never bound.** `GrowthRate` is a PROPERTY; a
                     Harmony patch that misses its target throws at PatchAll, but a
                     mod that failed to LOAD is silent. The startup message above
                     is the only positive evidence the assembly ran — if it is
                     absent, everything below it is meaningless and the answer is
                     "not deployed / not in ModsConfig", not "no effect".
                   - **The plant was dormant.** The postfix returns early on
                     `__result <= 0` (night, out of temperature band, unlit). A
                     0% reading is not evidence of anything. Read growth in
                     daylight, in season.
                   - **Reading ONE map.** x4 and x0.4 look identical if you only
                     ever see one biome — both are just "a number". The
                     terminator claim needs the second map, generated fresh.
                   - **Confusing growth with regrowth.** A burnt PoisonForest that
                     stays bare proves nothing about this patch;
                     `wildPlantRegrowDays` is untouched until R-G4 ships.
criteria: vegetation reads as obtrusively powerful rather than as a balance tweak.
state:    blocked — needs a shutdown window to deploy, then a live game

## C39 The eopie sled reads and renders as ours, on BOTH defs
row:      9
spec:     `4f3afc7`. `DesertVehicleReskin` now renames and rewrites
          `AV_DogSled` (Alpha Vehicles - Neolithic) and `VFEPD_DogSled` (VFE
          Props and Decor), and tints the PROP, which was never tinted before.
          Route: dev-mode spawn each, or find the sled in the vehicles build menu
          and the prop under Props and Decor. Deploy first; not deployed as of
          this writing.
verify:   PREDICTION before the look: the vehicle reads **"eopie sled"** with a
          description opening "Two eopies in harness", ending in Crew: Driver x1
          and Fuel type: Kibble, and NO warning paragraph. The prop reads
          **"eopie sled (prop)"**. 🔴 The one that matters: **the prop and the
          vehicle are the SAME COLOUR** — warm brown, not grey. Put them side by
          side in one screenshot; that comparison is the test.
          HOW IT LIES: the art reaches both defs by texPath override whether or
          not our patch ran, so correct ART is not evidence the patch applied —
          only the LABEL and the prop's COLOUR are. A grey prop beside a brown
          vehicle means the prop half no-opped.
criteria: both labels changed, both the same brown, warning text gone.
state:    blocked — needs deploy

## C40 Three Jawa fixes that only a load can prove
row:      9
spec:     Deployed but unproven, all needing a fresh load:
          (a) `291aebf` `MandrakeJawa` `canGenerateAsCombatant` false -> true.
              It was invented when the def was written and is not in the owner's
              .xtp. A Jawa faction could not generate a fighter.
          (b) `6ed888e` `JawaGeonosianFoundryHive` — its xenotype entry was gated
              on `btd.xenotyperemix.starwars`, which is now OFF, so the node was
              dropped and the faction's `xenotypeChances` was empty.
          (c) `5bb9f5c` B58 — starting gear and every JawaVoice rule named
              `OuterRim_Jawa`, a defName that stopped existing when Galactic
              Diversity was switched off.
verify:   PREDICTIONS, each a positive observation:
          (a) spawn `Jawa_Tribal_Scavenger` ×6 — all six are MandrakeJawa AND
              are armed fighters, not civilians.
          (b) spawn a Geonosian Foundry Hive pawn — it is a Geonosian, NOT a
              plain baseliner. An empty `xenotypeChances` yields baseliners and
              looks like a content gap rather than a dropped node.
          (c) a Jawa spawns WEARING the robe and hood (`guy762_Robes_jawa`,
              `guy762_JawaHood` — both from KotOR Weapons, which stays active),
              and a Jawa social interaction produces a Jawa voice line rather
              than a vanilla one.
          HOW IT LIES: (c)'s gear defs live in a mod we KEPT, so their presence
          in the dump proves nothing about whether our patch found its target —
          the pawn wearing them is the only evidence.
criteria: six armed Jawa; a Geonosian that is not a baseliner; a robed Jawa that
          speaks in its own voice.
state:    blocked — needs a load


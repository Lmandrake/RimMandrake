# CHECK inbox.

## C-V2 Park any v2 idea in design/V2_DREAMS.md yourself — no permission needed
row:      infra
spec:     Any idea for new content that is not v1 — including one a live session
          suggests — is appended to the END of `design/V2_DREAMS.md`. You have a
          standing right to append there directly: no permission, no routing through
          DECIDE, no queue item asking for it, no format and no field contract.
          Never queue v2 work.
verify:   read the header of `design/V2_DREAMS.md` once; it says the same thing.
criteria: EMPTY — that file is not a queue and nothing in it is scheduled.
state:    ready


## C1 Run the bridge tools that were built but never once called
row:      infra
spec:     `python.exe src/RimMandrake/bridgetools/prove_new_tools.py --pawns` covers `jawa/set_pawn_rotation`, `jawa/set_pawn_style`, `jawa/set_pawn_xenotype` and `xenotype=` on `spawn_pawn` (`7b8d5b7`, `e60197a`). Also deployed and never called: `jawa/get_defs`, `jawa/fire_quest`, `jawa/list_things` (`3adedbc`), `jawa/clear_ui` (`9a5b6fe`), the vehicle route in `spawn_batch` (`9a5b6fe`, routes `Vehicles.VehicleDef` through `Vehicles.VehicleSpawner.SpawnVehicleRandomized` by reflection — `ThingMaker` leaves `vehiclePather`/`ignition`/`drawTracker`/`kindDef` null), and the roof pair `set_roof_batch`/`get_roof_batch`. `jawa/world_stats` WAS called and its answer was discarded by a harness `NameError` (fixed `3e17731`) — re-run it. Do not compose calls at a live console: run `python.exe src/RimMandrake/bridgetools/load_session.py --phase any|fresh` (`--selftest` needs no game); it writes one ledger to `observed\<date>_load_session.md` and tracks LITTER, from which the release message is written.
verify:   EMPTY
criteria: each tool returns success on a live map; `world_stats` returns `{ tiles, pct, perimeter, raggedness, centroidLat }`. A capability is announced to peers when it has RUN, not when it has compiled.
state:    doing
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
state:    ready

## C33 Confirm our only faction actually loads into the game
row:      9
spec:     Our ONE shipped `FactionDef` is absent from the live def dump
          (2026-08-14T21:10Z, 87 FactionDefs). Not a defect: the game launched
          01:03:26 and `JawaTribes.xml` deployed 01:13, so the running process
          never read it. Repo and deployed copies are md5-identical
          (`720989cdbee5b7fb430278e1c5145bf5`), `ParentName="FactionBase"`,
          `mandrake.jawa.patches` is active. It has simply never been loaded.
          On the next cold load, before anything else mutates the game: confirm
          `Jawa_IndigenousTribes` is in the def database and its three referenced
          pawn kinds (`Jawa_Tribal_Scavenger`, `Jawa_Tribal_Slinger`,
          `Jawa_Tribal_Elder`) resolve.
verify:   none — this is a live read only.
criteria: `jawa/get_def defType=FactionDef defName=Jawa_IndigenousTribes` returns
          the def, and its `pawnGroupMakers` options resolve to real kinds.
          🔴 It is the TEMPLATE for the other 11-13 factions. If it does not
          load, every dossier authored against it is authored against nothing —
          so this runs BEFORE the faction build, not after.
state:    ready

## C34 You hold the live bridge at all times — standing rule
row:      infra
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
state:    ready

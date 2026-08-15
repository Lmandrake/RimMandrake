# DECIDE inbox.

## D-CRIT ⭐ Read before sequencing — the ocean gates worldgen, which gates two rows
row:      10
spec:     ROWS 2 AND 7 ARE ONE CHAIN, NOT TWO PROBLEMS.
          Row 7 (ordinary worldgen) is blocked on the sea: the generator produces
          43-55% scattered ocean against a spec of ~25% in three bodies. Ocean is an
          elevation rule at worldgen step 0; no slider reaches it. `JawaSeaShaper.dll`
          is our intervention and is NOT DEPLOYED.
          Row 2 (faction exclusion) is one screen seen ONCE during that same
          worldgen run — `WORLDGEN_FACTION_CHECKLIST.md`, ratified, 21 untick / 6 keep.
          It needs no build at all. It closes as a side effect of row 7 happening.
          ⇒ THE ORDER IS FIXED:
            B0 deploy (30-tool build + SeaShaper, game DOWN)
            -> measure the sea on DISPOSABLE quicktest worlds (no campaign click)
            -> tune SeaShaper until the 5-part gate passes
            -> ONE real worldgen run, which closes rows 7 AND 2 together.
          ⚠️ Sea gate requirements 3 and 4 are MISCALIBRATED until the `world_stats`
          unit fix ships inside B0 — `centroidLat` is degrees against a spec written
          as a 0.35-0.65 fraction, and `raggedness` counts tile edges where the spec
          means tiles with a land neighbour. Requirements 1 and 2 are readable now.
          ⚠️ `waterPct 25.0` was one seed. Seed `sickle` read 16.74. It is a mode,
          not a constant — never accept a world on a single reading.
verify:   —
criteria: —
state:    ready

## D1 Fill in the items whose spec or test is still blank
row:      infra
spec:     32 fields across the migrated items are literally EMPTY because the old
          notes did not say. BUILD and CHECK will bounce every one of them. Work
          down by value, not by ID order. Start with the items blocking rows 4 and 2.
verify:   No item in `queue/BUILD.md` has an EMPTY `spec:` or `verify:`.
criteria: —
state:    ready

## D10 Owner: cut the four Predator factions from the world?
row:      10
spec:     Four Yautja factions own **14 settlements** between them — `ABYautjaBadBloodClan` (5), `ABYautjaBerserkClan` (4), `ABYautjaClan` (4), `ABYautjaModderClan` (1) — the single largest non-Star-Wars presence on the map. Two SEPARATE levers, not interchangeable: **the four FACTIONS** can be unticked at worldgen (free, reversible, no mod change, already on `WORLDGEN_FACTION_CHECKLIST.md`); **the XENOTYPE MOD** `[AB] Xenotype: Yautja` (`biotechrace.yautja.alleyballey`, ws `3536839586`) is a separate decision — removing it costs a game-down window and risks `Could not resolve cross-reference`. The mod owns all 14 `Exception getting Verse.Graphic_Multi at :` errors (one malformed `<bodyGraphicData>` at `PawnKinds_BaseAbstract.xml:60`, 7 kinds x 2 lifeStages) but those errors are HARMLESS and waived — do not let them do work they cannot do. If the mod goes, BUILD B24 loses its mid-tier reference (Yautja blade, AP 0.60). Recommendation on file: untick the four factions, keep the mod installed.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D16 Seven files have no home in the new layout — decide where
row:      infra
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` §3 lists seven unplaced items that need a ruling before stage 4; stage 9 (`skills/`) is owner-gated and may never run. Both block BUILD B35.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D19 Design how the campaign starts — no document exists
row:      12
spec:     Chain step 12 has no doc anywhere in `design/`. It is the first thing
          the player touches: starting pawns, starting gear, the gravship, the
          landing. Needs `jawa_crew_personas.md`'s five founders (Nekko Vok,
          Tobb Nkik, Griz Utinn, Yeku, Wim Ateeka) resolved into either
          PawnKindDefs or hand-authored save state — that choice was never made.
          Depends on chain steps 2, 7 and 11.
verify:   a design doc exists naming the scenario mechanism (ScenarioDef vs a
          shipped save), the starting pawns, and the starting gear.
criteria: the campaign starts as designed rather than as a vanilla crashlanding.
state:    ready

## D-CHK1 The pilot console is UNREACHABLE — v1's NoPathToPilotConsole gate FAILS live
row:      unassigned
spec:     Filed by CHECK 2026-08-14 from the C1 harness (`observed/2026-08-14_load_session.md`).
          **A2 FAIL: 0 of 1 colonists reach `PilotConsole44499` at (129,149)**
          (`pathEndMode=InteractionCell`). **A4 FAIL** independently confirms the cause is
          reachability, not the order tool: `jawa/order_pawn` moved Alex (116,146) -> (116,146)
          over 245 ticks with `canReach=False`. A4b passed, so the pawn was left undrafted and
          at home — nothing is stuck.
          **Not caused by this session's edits.** The only passability change CHECK made was
          swapping 4 west-wall thrusters for `GravshipHull`; both are impassable buildings, so
          the wall was never open there. The 201 added conduits do not block. The ship has just
          **2 `Door`s for an 86x133 hull**, which is the obvious suspect.
          This is the gate `facts/LIVE.md` records as previously SKIPPED for want of a ThingID
          source — `jawa/list_things` now supplies it, so the gate finally ran, and it fails.
verify:   `jawa/order_pawn` a colonist to (129,149) and read `canReach` back; or re-run
          `load_session.py --phase any` and read A2/A4.
criteria: DECIDE's call — this is a SHIP DESIGN question (interior circulation and door
          placement), not a bridge defect. CHECK does not redesign it.
state:    ready

## D20 You inherit every sign-off the retired seats held
row:      0
spec:     Owner ruling 2026-08-14: VISION's and PROJECT's ratification authority
          passes to DECIDE. Live docs still gate on a seat that cannot sign:
          `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` :3, :124, :126, :169,
          :230, :379 ("If VISION has not signed off, do not execute the untick
          list"); `infrastructure/state/EXPECTED_FAILURES_next_load.md` :163, :248,
          :307, :324; `infrastructure/state/WORLDGEN_RUN.md` :29, :30, :32, :53,
          :63, :69, :72 (owner column assigns steps to CREATE/BRIDGE/OPS);
          `design/V2_DREAMS.md` :386-397, :401, :430, :509, :543, :618, :633, :650
          (routing table headed [PROJECT], [CREATE], [WORLD/OPS], [VISION]).
          Past-tense attributions are history — leave them. Rewrite only the
          conditions and owner columns that must be actionable by a live seat.
verify:   `grep -rn "VISION\|PROJECT\|OPS\|CREATE\|BRIDGE" ` over those four files
          returns only past-tense provenance, no unassignable gate or owner cell.
criteria: none — offline.
state:    ready

## D21 Rule on CREATE_TEST_PLAN.md: still useful, rewrite, or retire
row:      0
spec:     `infrastructure/state/CREATE_TEST_PLAN.md`, 20,435 B. Written by the
          retired CREATE seat about BRIDGE driving; cites `V1_SCOPE.md`'s gate as
          authority, which `V1_CHAIN.md` superseded. NOT orphaned — `:267` tells
          readers to file at the deleted `queue/CREATE.md`, live code
          `src/RimMandrake/bridgetools/load_session.py` references it, and
          `design/V2_DREAMS.md` C23 says to run it with nine pre-flight
          corrections that lived in the deleted `AGENT_BRIDGE_state.md`
          (recover: `git show edaa1bb^:infrastructure/state/AGENT_BRIDGE_state.md`).
          Owner's call 2026-08-14: DECIDE reviews whether it is still useful and
          whether it needs rewriting. If it survives, it is CHECK's file.
verify:   Either the file carries a current-authority header and an owning seat,
          or it is gone and its 8 referencing files no longer cite it.
criteria: none — offline.
state:    ready

## D22 Prune NEXT_RELOAD.md — 657 lines against a 400 budget
row:      0
spec:     `infrastructure/state/NEXT_RELOAD.md`. Over budget per
          `python3 src/RimMandrake/Utils/doc_budget.py`. At least one claim is
          already contradicted by `src/RimMandrake/bridgetools/execute_ship_plan.py:54`.
          Three dangling refs at :161, :228, :652 point at deleted queues
          (`queue/OPS.md:127`, `queue/BRIDGE.md`, `queue/CREATE.md` C11).
          Pruning means deciding what still matters for the next load, which is a
          scope call — owner assigned it here 2026-08-14 rather than to a cleanup
          pass. Raising the budget instead is a legitimate outcome; say so if it is
          the answer.
verify:   `doc_budget.py` reports NEXT_RELOAD.md ok, or DOC_BUDGET.md records why
          its budget was raised.
criteria: none — offline.
state:    ready

## D2 Owner: may we generate throwaway worlds purely to measure?
row:      v2
spec:     —
verify:   —
criteria: —
state:    dropped — Answered — the owner makes and saves the world by hand, so nothing needs measuring.

## D4 The world is half ocean against a quarter by design — pick a fix
row:      v2
spec:     —
verify:   —
criteria: —
state:    dropped — Worldgen is manual; the owner picks a world he likes by eye. Full text in `design/V2_DREAMS.md`.

## D24 Four rules died with `agents_def.md` — re-home them or repeal them
row:      0
spec:     `infrastructure/agents_def.md` was dissolved into `POLICY.md` (deleted at
          `edaa1bb`), but five numbered rules did not make the crossing and four
          live docs still cite them. One of the five is already answered below. `POLICY.md` has no rule numbers, so a citation
          cannot simply be repointed. Recover the source with
          `git show edaa1bb^:infrastructure/agents_def.md`.
          ✅ **Map protection is REPEALED — owner 2026-08-15, do not re-home it.**
          Recorded in `OWNER_DECISIONS.md` and `POLICY.md`: nothing outside the
          repo is precious. Two live docs still order a reader to read the old
          rule at a source that is gone — strike those citations:
          `design/Jawa/worldbuilding/row8_build_order.md` :41-43 and
          `infrastructure/state/CREATE_TEST_PLAN.md` :165-168.
          Four rules remain to re-home or repeal: rule 1 taking the bridge is announced
          (`row8_build_order.md:88-89`); rule 1b live means a map exists
          (`wait_for_live.py:6`, citation already dropped, substance kept);
          rule 1c whoever holds the bridge may create and destroy dev colonies at
          will (`skills/rimworld-debug-testing/SKILL.md:19`); rule 0.5 never ignore
          a problem, especially one that is not yours (`infrastructure/DOC_BUDGET.md:198`,
          named PROJECT as the drainer of `[?]` filings — needs a seat as well as a path).
          Anything about the live game lands on CHECK, per the 2026-08-14 ruling.
verify:   Each of the five is either written into `POLICY.md`/`CHECK.md` or recorded
          as repealed in `OWNER_DECISIONS.md`, and the four citing docs point at
          something that exists. `check_refs.py` no longer reports :198.
criteria: none — offline.
state:    ready

## D23 Build our own xenotype set instead of cherrypicking three packs
row:      1
spec:     Owner ruling 2026-08-15: *"For the races, we likely want to simply
          create our own out of the amalgam of whatever's there so we're in total
          control."*
          ⇒ Xenotypes are NOT a cherrypick row. Three packs ship overlapping
          Star Wars species — `btd.xenotyperemix.starwars` (70),
          `guy762.starwarsxenotypes` (58),
          `neronix17.outerrim.galacticdiversity` (44) — and BTD Remix dedups at
          LOAD, so which survives is not fully under our control. That is the
          problem this ruling solves.
          Owed: a `design/Jawa/worldbuilding/XENOTYPE_SPEC.md` naming the species
          the campaign contains, each as OUR OWN `XenotypeDef` assembled from the
          genes those packs already ship, with the donors' versions stood down by
          zeroed generation weight rather than deleted (the pattern already used
          for the three Jawa xenotypes in `OnlyMandrakeJawa.xml`).
          ⚠️ Scope check before designing: `FACTION_SPEC.md` R27 currently names
          31 `BTD_*` xenotypes across seven factions. Our own set must cover at
          least those, or R27 gets rewritten to match a smaller set.
          ⚠️ `MandrakeJawa` is already ours and is the worked example.
verify:   every species named in `FACTION_SPEC.md` R27 resolves to a def we own.
criteria: no faction member generates as a donor-pack xenotype.
state:    ready

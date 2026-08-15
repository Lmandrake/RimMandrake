# DECIDE inbox.

## D0 Give every queue item a chain step so the board can place it
row:      infra
spec:     Items in `queue/BUILD.md` and `queue/CHECK.md` migrated without a `row:`
          and land in an `unassigned` bucket. Read each, add `row: <n>` from
          `V1.md`. Mechanical; no judgement about scope needed. Rows 1,3,5,6,8 are
          closed — items touching them are almost certainly stale, delete rather
          than assign.
verify:   `python3 src/RimMandrake/Utils/derive_matrix.py` reports 0 unassigned.
criteria: —
state:    done

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

## D2 Owner: may we generate throwaway worlds purely to measure?
row:      10
spec:     `OWNER_DECISIONS.md`. All technical prerequisites are closed; a quicktest already builds a FULL world (119,904 tiles, `waterPct 25.0`, 2 bodies, `previewOnly:false`, 127 ms), so the sea gate and the worldgen click-path can be rehearsed on disposable worlds without opening the once-only Configure Factions screen.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D4 The world is half ocean against a quarter by design — pick a fix
row:      10
spec:     Measured on three real saves: 43% / 49% / 55% Ocean. The thirst-world identity exists in our documents and nowhere else. Ocean is an elevation rule written at worldgen step 0, so the rainfall slider cannot remove one tile, and no active mod manages water. Three routes, none needing a new dependency: **WorldEdit 2.0** (already active), a custom `WorldGenStep`, or BiomesKit's unused hooks. `faction_world_spec.md`, last section. This contradicts the Three Waters ruling by ~100x.
verify:   EMPTY
criteria: EMPTY
state:    blocked

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

## D18 Write the text for nine faiths that currently have only a name
row:      6
spec:     `design/Jawa/worldbuilding/faction_religions_spec.md`. Entries 1, 2 and
          3 have authored `ideoName` + `ideoDescription` + `deityPresets`.
          Entries 4-11 have a NAME and nothing else. The file's own heading says
          THE TEXT IS THE PRODUCT — `ideoName`, `ideoDescription` and the deity
          name/type pairs are the only strings the engine renders.
          Owed: the Sun-Debt · the Continuity Protocol · the Green Oath · the
          Balance · Meckgin · the Ascendant Genome · the Contract · The Weight
          — and entry 3 needs its `ideoDescription`.
          Section 12 (Jawa) stays deliberately empty; the player faith ships as
          `src/Jawa/ideoligion/The Salvation.rid`.
          ⚠️ Free Droid Enclaves' faith may not run if the droid race is not
          Humanlike — settle that before authoring entry 5.
verify:   every entry 1-11 has a non-empty `ideoName` and `ideoDescription`, and
          a `deityPresets` block wherever its structure has `deityCount > 0`.
criteria: `jawa/ideo_of` reads the eleven back and they match the spec.
state:    done

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

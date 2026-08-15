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
row:      doctrine
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
row:      repo
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


### ROOT CAUSE FOUND — 2026-08-15, CHECK, via `jawa/inspect_string`

**The grav engine chamber has no door.** The whole ship has exactly **2 doors** —
(115,58) and (82,136) — both on the outer hull, neither anywhere near the engine.
The octagonal chamber holding `GravEngine` (126,149), `PilotConsole` (129,149) and
`ChemfuelTank` (126,151) is walled from z=143 to z=158 with **zero** doors in it.

Alex is NOT immobile: all four one-cell moves succeeded. He simply cannot path in.
Ordered to (126,144), (126,146) and (126,148) — the chamber's south nook and
interior — he returned `0 moved at all` each time after ~900 ticks. The apparent
doorway at (126,144) is a dead nook: (126,143) behind it is hull.

**This is bigger than the console gate.** An uninspected grav engine is inert, so
every thruster and the console all read "Not connected to grav engine", and
`Gravship range` is 0. Sealing the engine in therefore disables the entire ship,
not just the console interaction. One door into that chamber plausibly clears the
thrusters, the console AND the engine inspection at once.

⇒ DECIDE's call: where the door goes. CHECK does not author the hull.
## D20 You inherit every sign-off the retired seats held
row:      0
spec:     🔴 **The authoritative retired-seat mapping, owner 2026-08-15. Use this
          verbatim; earlier looser wording sent CREATE/OPS to CHECK and all of
          PROJECT to DECIDE, and both are wrong:**

              VISION  -> DECIDE
              PROJECT -> DECIDE, EXCEPT some small elements which go to REP
              CREATE  -> BUILD
              OPS     -> BUILD
              BRIDGE  -> CHECK

          The PROJECT split, since it is the only one that needs judgement: REP is
          the human's interface and owns the status board,
          `infrastructure/state/status_matrix.json`,
          `infrastructure/state/queue/HUMAN.md` and `infrastructure/state/MODE`.
          PROJECT was "technical writer + IA, MVP seat". So a PROJECT
          responsibility about REPORTING TO THE HUMAN, the board, or status
          presentation goes to REP; a PROJECT responsibility about scope,
          sequencing, specs or document architecture goes to DECIDE. Where a
          PROJECT reference is ambiguous, file it in `queue/HUMAN.md` rather than
          guessing.

          Live docs still gate on a seat that cannot sign:
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
          repo is precious. Both docs that ordered a reader to the dead source are
          already struck (`row8_build_order.md`, `CREATE_TEST_PLAN.md`).
          ✅ **Every dangling citation is repointed** — no live doc now sends a
          reader to the deleted `agents_def.md`. Only the rules are unhomed:
          rule 1, taking the bridge is announced — probably dead, CHECK holds the
          bridge at all times per C34, so confirm and repeal; rule 1b, live means a
          map exists — substance kept in `wait_for_live.py`; rule 1c, the bridge
          holder may create and destroy dev colonies at will — now cited to
          `POLICY.md` §"Nothing outside the repo is precious", which is a superset,
          confirm that is the home; rule 0.5, never ignore a problem, especially one
          that is not yours — `DOC_BUDGET.md` now files to `queue/HUMAN.md`, i.e.
          REP, since reporting-to-the-human is the half of PROJECT that went to REP
          (D20); the rule itself still needs writing into `POLICY.md`.
          Anything about the live game lands on CHECK, per the 2026-08-14 ruling.
verify:   Each of the five is either written into `POLICY.md`/`CHECK.md` or recorded
          as repealed in `OWNER_DECISIONS.md`. The citation half is done — no live
          doc cites the deleted file and `check_refs.py` agrees.
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

## D25 A spec shipped a fabricated XML sample, and the validator called it clean
row:      9
spec:     B56 killed five FactionDefs for a day. Root cause is not the XML — BUILD
          fixed that in `fe6b460`. It is two upstream holes, both still open.
          **1. `design/Jawa/worldbuilding/FACTION_SPEC.md` R27 still carries the bad
          sample.** It gives `<li><xenotype>X</xenotype><chance>Y</chance></li>` as
          literal XML and claims it was "read from the live `Ancients` def". It was
          not — that shape appears NOWHERE in the game; every vanilla
          `xenotypeChances` (Biotech Neanderthal/Yttakin, Anomaly mutant and Horaxian
          kinds) is dictionary-keyed. A false provenance claim is worse than no
          sample, because it defeats the one habit that would have caught it. Strike
          or correct the sample, and audit R1-R27 for any other XML block claiming a
          provenance it does not have.
          **2. `skills/rimworld-modding/scripts/validate_patch.py` cannot see SHAPE.**
          BUILD ran it at the mod root and at `Defs/FactionDefs/` and got `0 errors`
          both times, identically before and after the fix. Its banner is honest —
          "NOT SCANNED: field names, field types, value ranges" — but a validator
          that returns 0 errors on a def the engine will discard reports a safety it
          never checked. Decide whether it gains a shape check (compare each node's
          child shape against the same field in a shipped def: `<li>` list vs keyed
          element) or whether its output is re-worded so a clean run stops reading as
          "this will load".
          **3. `check_refs.py` has the opposite failure and it BLOCKS a gate.** A
          queue item that names its own deliverable — B39's `design/Jawa/mods/MOD_FREEZE.md`,
          D23's `design/Jawa/worldbuilding/XENOTYPE_SPEC.md` — cites a path that is
          correct and does not exist YET. check_refs calls that BROKEN, so B36's
          `verify:` ("check_refs clean") can never pass while any item is open. It
          also just rose 8 → 9 when `beb5036` filed another such item, i.e. filing
          work makes the gate worse. Decide the idiom: an explicit marker on a
          not-yet-written deliverable, an exemption for paths inside `queue/`, or
          drop the clean-run requirement from B36. The code change lands on BUILD;
          the idiom is yours.
          This is DECIDE's because `design/` and `skills/` are yours; the XML was
          BUILD's and is already closed.
verify:   R27 no longer shows an unverified sample; the validator either flags a
          keyed field given `<li>` children or stops implying a clean run predicts
          loading; and `check_refs.py --all` can reach 0 BROKEN with items open.
criteria: none — offline.
state:    ready

## D26 The Eyeling becomes the Jawa clan's pet — v1
row:      12
spec:     Owner, 2026-08-15, from the animal contact sheet: *"AA_Eyeling MUST be
          made into a star-wars-style pet for the starting Jawa clan to keep!"*
          `AA_Eyeling` (Alpha Animals). This is a v1 CONCEPT, not `[v2]`.
          Owed by DECIDE, in this order:
          (a) a name and one line of fiction that makes it read Star Wars rather
              than Alpha Animals — the sprite stays, the identity changes. A
              rename is a `PatchOperationReplace` on `label` plus `description`;
              art is untouched, so this costs nothing to try.
          (b) whether it is bonded to a NAMED founder or unowned in the starting
              save. `SCENARIO_SPEC.md` gives Yeku `Animals 5` and a pack animal —
              if the Eyeling is his, that slot is already there.
          (c) trainability and whether it fights. Read its shipped
              `race/trainability` and `wildness` first; do not invent them.
          (d) where it appears in the wild, into
              `design/Jawa/worldbuilding/fauna_placement.md` — a clan pet the
              player can never find a second one of is a dead end.
          ⚠️ It must be in the STARTING SAVE, so it lands with `B55` (the campaign
          start) and therefore before the owner's world is finished.
verify:   `AA_Eyeling` is not in the Cherry Picker cut list; the rename patch
          validates; the name and fiction are written into `SCENARIO_SPEC.md`.
criteria: the clan starts with the pet, and it reads as belonging to this
          campaign rather than to Alpha Animals.
state:    ready

## D27 Run the cherrypick with the owner, category by category
row:      1
spec:     `design/Jawa/mods/CHERRYPICK_AGENDA.md` is the running agenda and
          records what is done, held and descoped. Method is settled: build a
          contact sheet from the defs, present clusters with the principle first,
          attribute every row to its mod, and cut only what the owner names.
          Creatures are DONE — six sheets, 336 Cherry Picker keys, plus Sapient
          Animals descoped (1,073 defs). Weapons and apparel sheets are built.
          Remaining categories in `CHERRYPICK_AGENDA.md`: weapons · armour ·
          items · buildings · plants · mechs · drugs · incidents · traits ·
          ideology styles.
          ⚠️ Cuts are inert until the next game start, and a cut that worked is
          ABSENT from the def dump — never validate old entries against it.
verify:   the live Cherry Picker config and
          `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml` agree
          after every batch.
criteria: the campaign's content reads as one setting rather than 584 mods.
state:    doing

## D28 Second pass on the xenotypes, once they are actually spawning
row:      7
spec:     Owner, 2026-08-15. **Gated: do not start until every pawn kind spawns
          using our own xenotypes** — that is chain step 4 landing and step 7
          consuming it (`D23`, and the `PawnKindDef` work that follows). The
          reason for the gate is that a genome is only judgeable once you can see
          what it produces; revising one on paper first is guesswork that gets
          redone.
          Once the gate opens, five passes over the set:
          (a) **Revise the genomes.** The first cut was assembled to make pawns
              exist at all. Now they exist, so the question changes to whether
              each gene earns its place and whether the metabolic and complexity
              costs are ones we chose rather than inherited.
          (b) **Audit the sizes.** Body size is where amalgamated races go wrong
              most visibly — a Wookiee that reads as a tall human, a Jawa that
              reads as a child rather than a small adult. Check it against what
              actually renders, not against the field value.
          (c) **Massively improve the text.** Labels, descriptions and gene
              descriptions carry the setting more than any other field, and
              inherited donor-mod prose is the loudest way a stack of 500 mods
              announces itself. This is the largest of the five and the one most
              likely to be underestimated.
          (d) **Pick the graphical-improvement candidates.** Not all of them —
              name the few where better art would change how the campaign reads,
              and hand those to `generating-rimworld-sprites`. Read
              `design/Jawa/mods/repurposed_graphics.md` before commissioning
              anything.
          (e) **Cherrypick out the rest.** A xenotype that is fine but not part of
              THIS campaign gets cut here.
          ⚠️ **(e) is a Utinni cut, not a RimMandrake deletion.** The split is the
          point: `design/` decides what this campaign contains, and cutting a
          xenotype from the Utinni campaign must not remove it from the toolkit
          or from the def set other campaigns could draw on. Cut via Cherry
          Picker, which is per-config and reversible — never by deleting defs.
verify:   every surviving xenotype has authored text rather than donor-mod prose;
          sizes checked against a rendered pawn; the cut list is in Cherry Picker
          and `deployed/config/v1_freeze/`; the graphics candidates are named in a
          BUILD item rather than left as an intention.
criteria: the roster reads as one authored set of species, and nothing in it is
          there merely because a donor mod shipped it.
state:    blocked — waiting on the pawn kinds to spawn with our xenotypes (`D23`
          and chain step 7).

## D-CHK2 Magenta heads: the generator's path-rewrite list is incomplete
row:      unassigned
spec:     Filed by CHECK 2026-08-15, live on the 70-species map. BUILD's fix, in
          `gen_races_mod.py` — CHECK does not author src/.

          SYMPTOM: a magenta box with a red X where the head should be. Confirmed by
          eye on Nikolaus (`RimMandrakeGand`) and Yoko (`RimMandrakeChagrian`); bodies
          render fine, neighbouring species render fine, both pawns alive and undowned.

          🔴 THE LOG NAMES IT, but NOT under the string you would grep for. The class is
          **`Failed to find any textures at <path> while constructing Multi(...)`** — not
          "Could not load UnityEngine.Texture2D", which returns ZERO hits. Three entries:
            Failed to find any textures at OuterRim/Genes/Headbone/ChagrianF
            Failed to find any textures at Pawn/HeadType/gand/gand
            Failed to find any textures at Pawn/HeadAttachments/gand/mask_yuun
          Every one is missing the `RimMandrakeSW/...` prefix.

          ROOT CAUSE: the generator re-namespaces the COMMON path fields (`texPath`,
          `graphicPath`, `texPaths`, most `iconPath`) and misses a family of others.
          19 defs carry 27 un-namespaced paths, all missing at runtime. The fields it
          misses:
            · `texPathFemale`                      (gendered variant - Chagrian, fishmouth, GS_Eyes_Yellow)
            · `<Male>` / `<Female>` inside a `BigAndSmall.PawnExtension` `headPaths`  (gand, selkath)
            · `backgroundPathEndogenes` / `backgroundPathXenogenes`
            · a handful of plain `iconPath`
          plus `Pawn/HeadAttachments/gand/mask_yuun` in `Defs/Misc/SW_Support.xml`.

          🔑 AND THE SAME MISS COSTS THE ART. The texture copier is driven from that
          same path list, so a field it does not rewrite is a texture it never copies:
            gand, selkath heads      path wrong, ART PRESENT (6 files) -> rewrite path only
            ChagrianF                path wrong, ART NOT COPIED        -> rewrite AND copy
            mask_yuun                path wrong, ART NOT COPIED        -> rewrite AND copy
            YellowEyes_Female        path wrong, ART NOT COPIED        -> rewrite AND copy
            OuterRim/GeneIcons/*BG   path wrong, ART NOT COPIED        -> rewrite AND copy
          The donors still hold all of it — e.g. `2980427615/Common_Old/Textures/OuterRim/
          Genes/Headbone/ChagrianF_east.png`, `2915192253/Textures/Pawn/HeadAttachments/
          gand/mask_yuun_east.png` — so nothing is lost, only unmigrated.

          ⚠️ Gendered fields make this look intermittent: male Chagrians render (their
          `texPaths` WERE rewritten), female Chagrians go magenta. Do not test one sex
          and call a species clean.
verify:   grep the log for `Failed to find any textures at` after the next load; zero
          lines is the pass. Offline: no def field should hold a path starting
          `Pawn/`, `OuterRim/`, `UI/` or `Genes/` without the `RimMandrakeSW/` prefix.
criteria: DECIDE routes; the fix is BUILD's in gen_races_mod.py, then a re-run and redeploy.
state:    ready

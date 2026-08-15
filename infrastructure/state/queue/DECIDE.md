# DECIDE inbox.

## D-CRIT ⭐ Read before sequencing — worldgen is the owner's, and the sea is v2
row:      10
spec:     🔴 SUPERSEDED 2026-08-15 (DECIDE). This item used to say the ocean gated
          worldgen and that `JawaSeaShaper.dll` had to be deployed and tuned before
          rows 2 and 7 could close. **That is no longer the order.** The owner ruled
          worldgen MANUAL on 2026-08-14: he builds a world he likes, saves it, and we
          ship it as a fixed resource. `V1.md` step 10 and the eight-gate table both
          carry the ruling; B2, C15 and C16 were dropped under it and their text sits
          in `design/V2_DREAMS.md`.
          ⇒ **The sea-shaping work is `[v2]`. Do not deploy or tune `JawaSeaShaper.dll`,
          and do not spend a shutdown window on it.** No seat runs campaign worldgen.
          WHAT ACTUALLY STANDS from the old item:
          - Rows 2 and 7 are still ONE event, and it is still the owner's single
            worldgen run. Row 2 needs no build: `WORLDGEN_FACTION_CHECKLIST.md` is
            ratified (21 untick / 6 keep) and is one screen he ticks during that run.
          - ⇒ **Chain steps 6 and 9 must be SHIPPED AND LIVE BEFORE he generates.**
            Factions and ideos are read once at world creation and cannot be
            retrofitted. That is B40–B54, and it is now the real gate on row 7.
          - ⚠️ `waterPct 25.0` was one seed; seed `sickle` read 16.74. If the sea is
            ever measured again it is a mode, not a constant — never accept a world
            on a single reading. Kept because it is a measurement, not a plan.
verify:   no queue item schedules a SeaShaper deploy or a campaign worldgen run.
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
state:    done — SCENARIO_SPEC.md now names the mechanism (a saved game, R25), all
          six founders and the starting stock. That is the verify condition met.

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
state:    done — 2026-08-15. **RULING: it KEEPS, unchanged, and it is CHECK's file.**
          The two defects this item describes were already fixed by `8abb5d1` before
          the item was read: it cites `V1_CHAIN.md` at line 8 and **never mentions
          `V1_SCOPE.md`** (zero hits), and `:267` points at `Terrain_Floors.xml`, not
          a deleted queue — the filing instruction is at `:308` and names
          `queue/CHECK.md`, which exists. Every path in the file resolves.
          It is load-bearing at six sites, `NEXT_RELOAD.md:322` and
          `src/RimMandrake/bridgetools/load_session.py:548,700,704` among them.
          **Part 5 is the only record in the repo of which SINGLE facing is broken
          per parked art-fix mod** — Cerean mane SOUTH, Saurid frill NORTH (the
          donor's `CenterFrill8_north-.png` trailing-hyphen typo), ToolBelt WEST
          (753 B against 16,945 B east). Disk-verified, non-obvious, expensive to
          re-derive. Deleting it would also cost the 9 pre-flight corrections and
          the false-pass checklist. No rewrite is owed.

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
state:    done — 2026-08-15. The 657-line premise was already stale; the file was
          pruned to 318 before this item was read. `doc_budget.py` now reports
          **378 / 400 ok**, and that is AFTER today's rewrite added §1.0 and six
          live items. All three dangling queue refs (`queue/OPS.md`,
          `queue/BRIDGE.md`, `queue/CREATE.md`) are gone. The budget stands as
          written; it did not need raising. ⚠️ The one live ref out of this file is
          `CREATE_TEST_PLAN.md` Part 5 at §7 — that is D21's ruling, not this one.

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
measured: 2026-08-15 DECIDE, and **this item's own spec above understates what is
          already done.** The live config and the freeze copy both hold **1,308**
          `<li>` keys and are identical — 1,284 `ThingDef`, 8 `IncidentDef`, 7
          `PawnKindDef`, 2 `RecipeDef`, 2 `GeneDef`. Five categories are decided and
          LIVE, not "next":
            weapons    799 defs   616 keep / **183 cut**
            apparel    820 defs   688 keep / **132 cut**
            animals  1,239 defs   901 keep / **338 cut**
            items · buildings · biomes — decision files exist and are non-empty
          Records: `observed/inventory/decisions_<category>.json`, written by
          `src/RimMandrake/Utils/cherrypick_review.py` (HTTP review page, autosaves).
          Sheets: `observed/inventory/sheets_weapons/`, `sheets_apparel/`.
          🔴 **TWO DEFECTS FOUND WHILE MEASURING, both routed to BUILD as B67:**
          1. `observed/inventory/` is **gitignored** (`.gitignore:181`, comment
             "Derived: regenerated in seconds"). That comment is TRUE of the 678 MB
             of contact sheets and **FALSE of the seven decision files** — those are
             ~1,300 owner keep/cut judgements and no machine regenerates them.
             The **cuts** survive in the committed freeze XML; the **keeps** exist
             nowhere else, so losing the folder makes "kept deliberately"
             indistinguishable from "never reviewed" across five categories.
          2. `cherrypick_build.py` validates a hand-authored `KEYS` list of ~24
             entries (Anomaly + GravTech) and **nothing reads the decision files**.
             The deployed 1,308 keys were written past the validator that exists to
             check them, so no key in the live cut list has been checked against the
             def dump. `--defs` validation for step 1 is currently a no-op.
          ⇒ `V1.md` step 1 corrected. `design/Jawa/mods/CHERRYPICK_AGENDA.md` still
          reads "No list exists at all today" for armour and leaves weapons and
          apparel unticked; it is the agenda for the owner session and correcting it
          is part of this item, not a separate one.

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

## D-CHK3 All 69 RimMandrake pawn kinds log a config error at every load
row:      unassigned
spec:     Filed by CHECK 2026-08-15 from the live log, 7,726 lines, process 07:56:41.

          `Config error in RimMandrake<Species>_Kind: initial resistance range is
          undefined for humanlike pawn kind.` — **69 of them, one per species.** They
          are 69 of the log's 93 config errors, i.e. three quarters of all config noise
          on this stack is ours.

          `initialResistanceRange` is what a prisoner's recruitment resistance is rolled
          from. Undefined on a humanlike kind means every captured pawn of these species
          starts from an unset value — so this is not only log noise, it is the prisoner
          and recruitment path for all 70 species.

          Vanilla humanlike kinds set it (e.g. `<initialResistanceRange>10~20</...>`).
          The generator emits the kinds without it. One line per kind in
          `gen_races_mod.py`'s PawnKindDef writer fixes all 69.
verify:   after a regenerate + redeploy + load: `grep -c "initial resistance range is
          undefined" Player.log` returns 0.
criteria: BUILD's fix in the generator, not a hand-edit of 69 defs.
state:    ready

## D29 Ash'karr's world is not safe to generate yet — two silent blockers
row:      10
spec:     🔴 **BLOCKS WORLDGEN. Both fail SILENTLY — a bad world generates with no
          error line, and step 10 is irreversible.** Found 2026-08-15 by the
          scenario-settings sweep and verified by DECIDE directly.
          (a) **The planet type has never been selected.** `7f.alienworlds` and
              `7f.alienworlds.tidallylocked` are ACTIVE, but **no planet-type
              config file exists anywhere in `Config\`** and `selectedPlanetType`
              still reads `Default`. `ferny.Worldbuilder` is not active, so the
              selector is a radio list in MOD SETTINGS, not a button on the world
              page. A world made today is an ordinary vanilla planet — no tidal
              lock, no `avgTempByLatitudeCurve`, no rainfall curve, no biome
              blacklist. **Every ruling R-H0..R-H10 assumes that curve.**
          (b) **The biome mix is dead.** `JawaWorld_BiomeMix.xml` writes
              `biomeConfigs` in dictionary-keyed shorthand; the log carries **28**
              `XML format error: List item found with name X that is not <li>`
              (confirmed: `ExtremeDesert`, `Desert`) and the live def reads
              `biomeConfigs: []`. The blacklist half works, so all 24 abundance
              offsets fail behind a patch that looks fine. **This is B56's bug
              again**, and biome scoring runs ONCE, at worldgen.
          Also recorded wrong and owed a fix: `WORLDGEN_RUN.md` §2.E says the
          Anomaly playstyle is `Disabled` — it must be **`AmbientHorror`**, which
          keeps study/research/codex alive; and `EXPECTED_FAILURES` S5 expects a
          translation key where the save writes a defName.
          BUILD holds the buildable half as **B63**. (a) is an owner click.
verify:   a planet-type config file exists naming the tidally locked type; zero
          `is not <li>` errors from the biome mix; `WORLDGEN_RUN.md` §2.E reads
          `AmbientHorror`.
criteria: the world the owner generates is the world these documents describe.
state:    ready

## D30 Six rulings the next session must get from the owner
row:      0
spec:     Parked 2026-08-15. None block each other; all block something.
          **Worldgen-critical, answer before step 10:**
          (1) **What carries the Pyrelands?** Vanilla `Savanna` and `Grasslands`
              are cut and `ZBiome_Grasslands` ("stormy savanna") is kept. If
              deliberate this is ideal — it already carries `DryThunderstorm` at
              commonality 2. If not, the cut must be reversed.
              (`biome_review_comments.md` §1)
          (2) **The three wet biomes** — `AB_FeraliskInfestedJungle`,
              `AB_MiasmicMangrove`, `COMIGO_GreaterSwamp_Tropical` — are fine as
              R-H1's narrow flood margin and wrong as regions. Needs a placement
              ruling, not a patch.
          (3) **`Glowforest` as the LIVING half of the nightside glow?** R-H6c
              left alive-vs-mineral open; taking it gives that band two textures.
          **Not worldgen-critical:**
          (4) **`BTD_Jawa` → which def?** Two live Jawa xenotypes, each holding a
              different half of the clan's canon (`FACTION_SPEC.md` R28a). 16
              references left deliberately unpointed. This is `D23`'s merge.
          (5) **Confirm `RimMandrakeRakata` as the ancient enemy** — DECIDE
              proposed it (`the_forgotten_war.md` R-W3); the owner names it.
          (6) **The Rust Cathedral's hazards and the Enclave goodwill cost must be
              set TOGETHER** (`the_forgotten_war.md` R-W4), and R-H10's biome
              temperature edits REOPEN chain step 8, which is ratified — that
              needs a ruling rather than a patch.
verify:   each of the six is either answered in a design doc or explicitly
          re-parked with a reason.
criteria: none — offline.
state:    ready

## stage-the-next-load-and-more-content-4b7e05
row:      10
spec:     Owner broadcast, 2026-08-15, relayed by REP: *"Game is down, offline work may
          begin. Stage the next game load and prepare additional content. Ensure the
          mod list shows the many removed mods correctly (BUILD)."*

          Game confirmed DOWN (`tasklist.exe`, no `RimWorldWin64.exe`). The shutdown
          window is OPEN, which is the only window for the deploy-gated items —
          `queue/BUILD.md` B0 and B1 both say "game must be DOWN" and have been
          waiting on exactly this.

          Two halves, both yours:
          1. STAGE THE LOAD. `infrastructure/state/NEXT_RELOAD.md` is assembled by you.
             Order it, make every item name the call that produces its evidence, and
             sweep the seat queues for anything `blocked — needs a live game`
             (CHECK's C37 70-race lineup is parked waiting on a load).
          2. PREPARE ADDITIONAL CONTENT. Spec it and feed BUILD. The mod-list half is
             the owner's explicit assignment to BUILD and is filed there as
             `mod-list-shows-descoped-removals-9c4e12`; it is already measured correct,
             so do not re-spec it.
verify:   `NEXT_RELOAD.md` is ordered top-to-bottom with a call named per item, and no
          item in it is one the down-window makes unnecessary.
criteria: the load answers every question staged in it; nothing needs a second load
          that could have ridden this one.
state:    ready

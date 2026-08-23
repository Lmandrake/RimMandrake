# DECIDE — ARCHIVE. Settled items, kept verbatim.

**Nothing here is work.** Every item below is closed, done, dropped or ruled `[v2]`. They
were moved out of `queue/DECIDE.md` on 2026-08-19 on the owner's instruction — *"only
maintain live work in queue"* — because 31 settled items were 900 of that file's 1,529
lines and every seat scrolled past them to reach the eight that were live.

⛔ **They are MOVED, not deleted, and that distinction is the whole point.** `POLICY.md`:
*"Deleting it, renumbering it away, or quietly retitling it into something else breaks the
count and cannot be recovered later."* The text is unchanged, the names are unchanged, and
`derive_matrix.py` reads a closed item's `row:` out of its closing commit's PARENT, so the
board can still find every one of these in git.

🔑 **Read an item here as a RECORD, never as an instruction.** Several contain reasoning
that was true when written and is now superseded — the live-bridge ruling of 2026-08-19
alone invalidated the premises of four of them. If something here looks like work, it is
not; check `queue/DECIDE.md` and `V1.md` before acting on anything you find below.

---

## D-RACE Owner closed race appearance for v1; Ortolan moved INTO v1
row:      doctrine
spec:     OWNER RULING, 2026-08-15, broadcast at his request (CHECK `36debc4`):
          *"I think we can mark all the races as visually good enough for v1, with
          the remaining missing art for v2 improvement. Let's close out race
          appearance issues for now."*
          - **Race appearance is CLOSED for v1.** No seat opens, actions or escalates
            a v1 item for any race's looks.
          - **C37 closes DONE** — 70 of 70 xenotypes spawned with their forced
            xenotype, zero spawn failures, zero plain-human fallbacks, and the owner
            examined the grid on screen himself.
          - All cosmetics parked as ONE v2 item in `design/V2_DREAMS.md` under
            "Race art polish": missing art on RimMandrakeGand / RimMandrakeChagrian /
            RimMandrakeSelkath, hair on RimMandrakeYoderForceGremlin, the four known
            magenta species.
          - ⛔ CHECK WITHDREW `gand-and-chagrian-missing-artwork-5d2a09`, struck in
            place not deleted. BUILD is told not to action it.
          - ⭐ **RimMandrakeOrtolan is OUT of the v2 deferred list and INTO v1**, done
            and confirmed. Owner live: *"We have a working Ortolan! Make that as done
            for now and confirmed, not v2 after all."* Drop any "Ortolan is high
            priority for v2" line. Herglic, Anzati, Muun, SithZ, Togorian stay
            deferred.
          🔴 OWNER, 2026-08-15, later the same session (CHECK `7661925`): *"The
          missing art races are consistent: Gand, Selkath, and Chagrian are the ones
          with missing art. Log that as a v2 fix."* ⇒ **All three are real and the
          list is COMPLETE.** No re-survey. Take the three at face value.
          ⛔ An earlier caveat here said the pair differed between the owner's
          racetest grid and CHECK's and that one sighting might be a misread. CHECK
          has RETRACTED it and the owner has contradicted it. Deleted rather than
          left standing — a stale line above its own correction still gets read first.
          Still true, and the reason this was hard to see: **the log cannot find this
          class** — the texture-path check reads 0 and only fires when EVERY
          direction is missing.
verify:   no v1 item anywhere schedules race-appearance work, and Ortolan reads v1
          done rather than v2 deferred.
criteria: —
⚠️      OVERLAPS `ortolan-is-v1-again-supersedes-the-v2-deferral-1a7f30` (CHECK,
          `7c2fb32`, below) — same ruling, filed twice because the seat was down. That
          item names the EXACT lines to correct in this file: the Ortolan deferral at
          ~1087 and "ORTOLAN IS HIGH PRIORITY FOR v2" at ~1107. Do the edit from that
          item and close BOTH. Do not action them separately.
state:    ✅ CLOSED — owner ruling, filed. Race appearance is closed for v1.

## D1 Fill in the items whose spec or test is still blank
row:      doctrine
spec:     32 fields across the migrated items are literally EMPTY because the old
          notes did not say. BUILD and CHECK will bounce every one of them. Work
          down by value, not by ID order. Start with the items blocking rows 4 and 2.
verify:   No item in `queue/BUILD.md` has an EMPTY `spec:` or `verify:`.
criteria: —
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

## D10 Owner: cut the four Predator factions from the world?
row:      10
spec:     Four Yautja factions own **14 settlements** between them — `ABYautjaBadBloodClan` (5), `ABYautjaBerserkClan` (4), `ABYautjaClan` (4), `ABYautjaModderClan` (1) — the single largest non-Star-Wars presence on the map. Two SEPARATE levers, not interchangeable: **the four FACTIONS** can be unticked at worldgen (free, reversible, no mod change, already on `WORLDGEN_FACTION_CHECKLIST.md`); **the XENOTYPE MOD** `[AB] Xenotype: Yautja` (`biotechrace.yautja.alleyballey`, ws `3536839586`) is a separate decision — removing it costs a game-down window and risks `Could not resolve cross-reference`. The mod owns all 14 `Exception getting Verse.Graphic_Multi at :` errors (one malformed `<bodyGraphicData>` at `PawnKinds_BaseAbstract.xml:60`, 7 kinds x 2 lifeStages) but those errors are HARMLESS and waived — do not let them do work they cannot do. If the mod goes, BUILD B24 loses its mid-tier reference (Yautja blade, AP 0.60). Recommendation on file: untick the four factions, keep the mod installed.
verify:   the four defNames are on `WORLDGEN_FACTION_CHECKLIST.md`'s untick list, and
          no queue item proposes removing `biotechrace.yautja.alleyballey`.
criteria: none — the untick is one box each on the worldgen faction page.
state:    done — 2026-08-15 **OWNER: untick the four factions, keep the mod installed.**
          Asked directly and answered directly; the recommendation on file was taken.
          ⇒ `ABYautjaBadBloodClan`, `ABYautjaBerserkClan`, `ABYautjaClan` and
          `ABYautjaModderClan` come off at the worldgen screen — free, reversible, no
          mod change, already on the ratified checklist. **`biotechrace.yautja.alleyballey`
          STAYS**, so B24 keeps its mid-tier reference (Yautja blade, AP 0.60) and no
          shutdown window or cross-reference risk is incurred.
          ⚠️ The mod's 14 `Exception getting Verse.Graphic_Multi at :` errors remain and
          remain WAIVED. They are not a reason to revisit this.

## D16 Seven files have no home in the new layout — decide where
row:      repo
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` §3 lists seven unplaced items that need a ruling before stage 4; stage 9 (`skills/`) is owner-gated and may never run. Both block BUILD B35.
verify:   EMPTY
criteria: EMPTY
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

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

## D21 Rule on TEST_PLAN.md: still useful, rewrite, or retire
row:      0
spec:     `infrastructure/state/TEST_PLAN.md`, 20,435 B. Written by the
          retired seat about another retired seat driving; cites `V1_SCOPE.md`'s gate as
          authority, which `V1_CHAIN.md` superseded. NOT orphaned — `:267` tells
          readers to file at a deleted retired seat's queue, live code
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
          (a retired seat's queue at :127, and two more retired seats' queues,
          one of them item C11).
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
          live items. All three dangling queue refs, each to a
          retired seat's queue, are gone. The budget stands as
          written; it did not need raising. ⚠️ The one live ref out of this file is
          `TEST_PLAN.md` Part 5 at §7 — that is D21's ruling, not this one.

## D2 Owner: may we generate throwaway worlds purely to measure?
row:      v2
spec:     —
verify:   —
criteria: —
state:    dropped — Answered — the owner makes and saves the world by hand, so nothing needs measuring.

## D4 The world is half ocean against a quarter by design — pick a fix
row:      dead
spec:     —
verify:   —
criteria: —
state:    dropped — ~~v2, full text in `design/V2_DREAMS.md`.~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12.
          The water is authored offline and imported; the generator's own ocean fraction
          is overwritten and is not a problem to fix.

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
          already struck (`row8_build_order.md`, `TEST_PLAN.md`).
          ✅ **Every dangling citation is repointed** — no live doc now sends a
          reader to the deleted `agents_def.md`. Only the rules are unhomed:
          rule 1, taking the bridge is announced — probably dead, CHECK holds the
          bridge at all times per C34, so confirm and repeal; rule 1b, live means a
          map exists — substance kept in `wait_for_live.py`; rule 1c, the bridge
          holder may create and destroy dev colonies at will — now cited to
          `POLICY.md` §"Nothing outside the repo is precious", which is a superset,
          confirm that is the home; rule 0.5, never ignore a problem, especially one
          that is not yours — `DOC_BUDGET.md` now files to `queue/HUMAN.md`, i.e.
          REP, since reporting-to-the-human is the half of a retired seat's remit that went to REP
          (D20); the rule itself still needs writing into `POLICY.md`.
          Anything about the live game lands on CHECK, per the 2026-08-14 ruling.
verify:   Each of the five is either written into `POLICY.md`/`CHECK.md` or recorded
          as repealed in `OWNER_DECISIONS.md`. The citation half is done — no live
          doc cites the deleted file and `check_refs.py` agrees.
criteria: none — offline.
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

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
state:    ✅ CLOSED — **OWNER RULING 2026-08-15, verbatim:** *"We are shipping with the
          ones we have right now, unchanged, implemented in the game right now. There
          won't be any more decisions about xenotype inclusion in v1 at this time."*
          ⇒ No own-set authoring, no merge, no R27 rewrite. The live xenotype set IS
          the v1 set. Remainder parked in `design/V2_DREAMS.md`.
          ⚠️ This closes INCLUSION only. It does not bless a broken reference — the
          `softshadow.xtp` dead genes still drop silently at world creation.

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
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

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
state:    done — **OWNER 2026-08-15: CHERRYPICKING IS FROZEN AND THIS ITEM IS CLOSED
          FOR v1.** *"Armour, weapons, items, beasts and others are done; the rest
          returns later if needed."*
          ⇒ **The surviving item set is FIXED.** 1,308 Cherry Picker keys are the
          answer, and no further category is v1 work. Do not re-open a category, do
          not file one, and do not treat the seven un-run categories as debt —
          they are `[v2]` *if needed at all*.
          🔑 **THE CONSEQUENCE, and it is the largest thing this ruling does:** chain
          steps 2 and 3 were blocked on this, and `B53`'s 48 pawn kinds were blocked
          on step 3 because `weaponTags` and `apparelRequired` are "a selection from
          the surviving item set and cannot be invented". **That set now exists.**
          B53 is unblocked in principle — see the note filed on it.
          ⛔ **NO MECH ART REVIEW** — owner, same ruling. The per-mech curation against
          `design/Jawa/worldbuilding/review/mech_register.html` that B25(c) and
          `NEXT_RELOAD.md` §1b both left open as "still the owner's question" is
          **closed, not deferred**. Mechanoids stay and their art is not reviewed.
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
state:    ⛔ v2 — its premise died with D23. Xenotype inclusion is closed for v1.

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
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

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
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

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
verify:   zero `is not <li>` errors from the biome mix; `WORLDGEN_RUN.md` §2.E reads
          `AmbientHorror`. (The planet-type half is no longer ours to verify — see below.)
criteria: the world the owner generates is the world these documents describe.
state:    ✅ CLOSED 2026-08-19 — (a) is the owner's click and is recorded on the run
          sheet; (b) is RULED below and demoted out of the worldgen gate.
🔴 RULING (DECIDE, 2026-08-19): **THE BIOME MIX NO LONGER GATES WORLDGEN.**
          The 2026-08-15 ruling that saved this file (`does-the-standdown-cover-biome-
          commonality-tuning-b7c81e`) rested on one sentence: *"there is no biome-
          abundance control at the world screen, so if the mix is dead he gets vanilla
          abundances."* **The live-bridge ruling of 2026-08-19 inverts it.** We assign
          the biome of all 21,872 tiles by hand and stamp them into the live world.
          MEASURED, not assumed:
          · `world/ASHKARR_WORLDMAP_tiles.csv` — 21,872 rows, ids 0–21871 contiguous,
            **zero blank biome cells**. `world/live_tiles_check.csv` reads back 21,872.
          · `BiomeDef.Worker.GetScore` has **exactly one caller** in 1.6 —
            `WorldGenStep_Terrain.BiomeFrom`, reached only from `WorldGenerator`. Both
            the blacklist and the 24 `scoreOffset`s are Harmony hooks on that one method
            (`PlanetTypeManager.cs:96-125`). Nothing at runtime re-scores a biome.
          · The blacklist is already contradicted by our own map: the authored CSV paints
            **422 `ZBiome_Grasslands`** and **53 `AB_GelatinousSuperorganism`** tiles,
            and both are blacklisted. A blacklisted biome cannot appear post-stamp
            unless we paint it — and we do.
          ⇒ **What survives, and it is second-order:** the mix still shapes the VANILLA
          substrate that Landmarks (650), Mutators (700), AncientSites (300) and
          AncientRoads (400) roll against *before* we stamp. A desert-shaped substrate
          yields fewer illegal placements. That is insurance, not a gate — and it is
          dominated by the cheaper fix §12.3 already names: clear and re-roll them after
          the stamp. ⛔ **Nothing waits on the biome mix. It does not appear on the
          worldgen run sheet. Do not restore it as a blocker.**
          ⇒ B63(2) demoted in `queue/BUILD.md`; `pyrelands-off-the-blacklist-and-ash-
          storms-5d2e71` half-voided there. **B63(1), the planet type, is UNAFFECTED and
          is now the more critical of the two** — the `TidallyLocked` choice is scribed
          into the world as `alienWorldsFrameworkPlanetType` and re-applies from the SAVE
          on every load, so it cannot be changed after the fact.
          ⚠️ NOT changed by this ruling: `WORLDGEN_RUN.md` §2.E must still read
          `AmbientHorror`, and `EXPECTED_FAILURES` S5 still expects the wrong string.
          Those two are the live remainder of this item and are recorded on the run sheet.
🔴 **(a) THE ROUTE CHANGED UNDER US — corrected 2026-08-19, read this before quoting the
          paragraph below.** `ferny.worldbuilder` is **ACTIVE** as of today's
          `ModsConfig.xml` (578 mods, written 19:03). Every document that describes the
          planet-type click says it is NOT active and reasons from that. Consequences,
          all read off source:
          · Alien Worlds picks its backend by `Type.GetType("Worldbuilder.WorldPresetManager")`,
            not by `ModsConfig.IsActive`. Worldbuilder present ⇒ **backend = Worldbuilder**,
            `selectedPlanetType` is forced to `"Unknown"`, and **the mod-settings radio list
            is rendered DISABLED**. ⛔ So "set it in Mod settings" is no longer possible and
            "`selectedPlanetType` reads `Default`" is no longer the thing to check.
          · **The preset NAME is the planet type** — `PlanetTypeManager.Current` looks up a
            `PlanetTypeDef` whose defName equals `WorldPresetManager.CurrentlyLoadedPreset.name`.
            They cannot disagree. Picking the **tidally locked world** preset selects it.
          · The preset also pushes **MLP subcount 7 and coverage 1.0**, which is what makes
            the grid 21,872 tiles and our CSV's tile IDs correct. MLP's own slider never
            draws — Worldbuilder's overhaul skips the vanilla page.
          · 🔴 **AND THE PRESET IS DESTROYED AT EVERY LAUNCH** where it currently lives.
            Filed as BUILD `worldbuilder-preset-is-wiped-at-every-launch-not-just-on-steam-
            updates-6b1e4d`, which is the fix and must land before the next launch.
          ⇒ **What he actually does:** new colony → Worldbuilder's preset page → **tidally
          locked world** → **Configure planet** (not skip) → confirm **Scale 7** and
          **Coverage 100%** → generate. ⚠️ Scale 10 means the preset lost its parameters:
          abort rather than generate.
          ✅ **Nothing about the DECISION changed** — it is still `TidallyLocked`, still his
          click, still parked until everything ships. Only the mechanism moved, and it is
          now verifiable on screen before he commits, which it was not before.
answered: **(a) PLANET TYPE — OWNER 2026-08-15: `TidallyLocked`, and HE sets it.**
          Asked directly. His words: *"I will set it, and it's parked until factions
          and ideos and almost everything else ships."*
          ⇒ **Do not file this as a BUILD item and do not write a planet-type config
          file.** It is a click he has taken, deliberately, at the moment he generates.
          ⇒ It is NOT a blocker on anything today. It becomes live exactly once, and it
          is now recorded as a precondition on `WORLDGEN_RUN.md` §2.A rather than a
          queue item — which is the right home, because that file is the run sheet for
          the event it belongs to.
          ⚠️ It stays TRUE that a world generated *today* would be a vanilla planet.
          That is now harmless, because worldgen cannot happen until step 9 ships. It
          would become harmful the moment anyone books the run without §2.A checked.
          (b) **The biome mix is still dead** and is unaffected by any of this — 28
          `XML format error: List item found with name X that is not <li>`, live def
          reads `biomeConfigs: []`, all 24 abundance offsets failing behind a patch
          that looks fine. **Biome scoring runs ONCE, at worldgen.** BUILD holds it as
          B63 and it must land before he sits down.

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
state:    done — 2026-08-15, both halves. `0459627` + `ac8cee7`.
          HALF 1, the load. `NEXT_RELOAD.md` opens with **§1.0 THIS WINDOW**, a
          six-step ordered deploy manifest, and §5 carries **six** live items in order
          instead of three — C37's Rodian snoot is L0 and first, then C40, C41+C39,
          and C38 last because it needs a second `PoisonForest` map. C36's crossref
          sweep moved to §2 where the startup harvest actually collects it. 378/400
          lines, in budget. ⛔ **The `[v2]` sea assembly is struck from the window** —
          see D-CRIT, superseded today; B0's line is corrected.
          HALF 2, the content. **B66** folds D-CHK2 and D-CHK3 into one
          `gen_races_mod.py` regenerate — it must ride THIS window or L0 photographs
          four species that are magenta for a cause already diagnosed. **B67** is the
          find: the seven cherrypick decision files are gitignored as "derived", so
          ~1,300 owner keep-judgements live on one disk, and `cherrypick_build.py` has
          never validated any of the 1,308 deployed keys. Chain step 1 corrected in
          `V1.md` — five categories are decided and live, not "weapons and apparel
          next". The owner ask is in `queue/HUMAN.md`.

## frozen-mod-count-is-ten-short-2d1f8b
row:      10
spec:     Reported by BUILD from `refresh.py` (fingerprint `7256c128a43117a5`), relayed
          by REP. Three numbers for one set and they disagree:

          | source | count |
          |---|---|
          | live `ModsConfig.xml` (mtime 2026-08-15 11:58:30), and `deployed/config/v1_freeze/ModsConfig.xml`, identical incl. order | **575** |
          | live DefDump, when it was taken | 576 |
          | `infrastructure/state/V1_CHAIN.md:80-88` — "**These 585 ARE the frozen set** — owner's ruling, 2026-08-14" | **585** |

          575 resolved, 0 listed-but-missing, so the live pair is internally consistent
          and is the true state. The six Descoped rows of
          `design/Jawa/mods/CHERRYPICK_AGENDA.md` account for six of the ten;
          `regrowth.botr.boilingforest` is the one that left since the DefDump. **Four
          are unaccounted for.**

          This is yours because §0 of `V1_CHAIN.md` is a ruling, not a measurement, and
          only you can restate it. `585` also appears in `infrastructure/state/V1.md`,
          `design/Jawa/mods/required_mods.md`, `design/Jawa/mods/CHERRYPICK_AGENDA.md`
          and `design/Jawa/worldbuilding/FACTION_SPEC.md` — some of those are prose about
          the ruling and follow it.
verify:   the four unattributed removals are named, and every doc that states the frozen
          count states the same number.
criteria: EMPTY — offline.
state:    ⛔ DROPPED 2026-08-19 — **owner: *"Unfreeze mod count, let's not treat this as
          a criteria to monitor for v1."*** The item asked for four unattributed removals to
          be named and every doc to state the same number. Neither is wanted. The premise
          also decayed while it sat: live is **578** today, not the 575 this item was
          reconciling to, and not the 585 it was raised against. ⇒ Chain step 0 is
          UNFROZEN in `V1.md` and `V1_CHAIN.md`; the "these N ARE the frozen set" ruling is
          repealed in place. **The mod list is captured at worldgen time as shipping
          documentation, not policed as a standing number.**

## promote-the-defdump-arming-out-of-optional-6ea3c7
row:      10
spec:     `NEXT_RELOAD.md:58` (§1a) arms the DefDump and is labelled "**OPTIONAL, gates
          nothing**". BUILD reports it does gate something: the live dump is STALE, only
          a game load refreshes it, and `Jawa_Armoury/Patches` is downstream of it and
          stays stale until it lands. Read at STARTUP only, so it is armed before launch
          or not at all — and a missed arming costs a whole load.
verify:   §1a no longer says it gates nothing, and names what goes stale without it.
criteria: the post-load dump is current and `Jawa_Armoury/Patches` can be regenerated
          from it without a second load.
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

## the-dump-was-never-stale-correct-the-manifest-5cb9a2
row:      10
spec:     🔴 **`NEXT_RELOAD.md` §1.0 step 0 and §1a are wrong on their central fact, and
          they state it as urgent.** Both say the live def dump is from **2026-08-14
          01:20**, "before eleven mods left", and conclude that every
          `validate_patch.py --defs` run is checking against a def universe that no
          longer exists. Raised by CHECK (`e0997c0`), verified independently by REP:

          - That date was read off the `defs/` **FOLDER** mtime. The dump overwrites its
            files in place and never adds or removes one, so the folder date does not
            move while the contents do.
          - **The manifest is the authority.** `manifest.json`: `capturedUtc
            2026-08-15T15:10:11Z`, `mode all`, `gameVersion 1.6.4871 rev591`, 576 mods,
            529 def files. Every file under `defs/` is stamped **Aug 15 08:10** local
            (= 15:10Z). Taken during this morning's C37 load, WITH the races mod and
            with all three donors absent — the current configuration.

          ⚠️ **REP over-corrected here and BUILD caught it. The dump is fresh in TIME
          but not in SET, and only one direction of the staleness is safe.** Verified by
          REP against both files: manifest `modCount` **576**, live `activeMods` **575**,
          and the diff is exactly one — `regrowth.botr.boilingforest` in the dump, and
          NOTHING live is missing from the dump.

          ⇒ Every def that loads in game IS represented, so `--defs` cannot miss a real
          def. **The risk is one-way and it is live:** the dump still holds defs from a
          mod that no longer loads, so an xpath onto those defs validates CLEAN and
          matches nothing in game. It already bites one of ours —
          `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml:140` sets a `scoreOffset`
          on `RG_BoilingForest`, which is still in the dump's `BiomeDef.json` and
          `IncidentDef.json`. That patch reports clean today and is a no-op in game.
          `refresh.py`'s STALE verdict was therefore CORRECT — it keys on the load-set
          fingerprint, not on age, and it named this exact mod.

          The wording for the board: *the dump is current as of 2026-08-15T15:10:11Z but
          was captured at 576 mods against a live 575; `--defs` is sound except for
          anything touching `regrowth.botr.boilingforest` defs.* The re-dump is armed, so
          the next load closes it. REP's own
          `promote-the-defdump-arming-out-of-optional-6ea3c7` was filed on the bad
          premise; correct both sections against this.

          Two non-problems, so nobody chases them: the mod folder is still on disk at
          `...\294100\3565675704` — unlisted, not unsubscribed, installed-but-inactive;
          and `src/Jawa/Jawa_Doctrine/About/About.xml` names it in **loadAfter**, not
          `modDependencies`, which exerts no constraint on an inactive mod and logs
          nothing. Harmless, leave it.

          What survives the correction: arming the dump is still right, because it
          re-reads after this window's deploys and costs 18.7s. CHECK already armed it
          (13:27). What must go is the urgency and the "stale universe" reasoning — if
          any item was deferred on that premise, it is not blocked.

          **Read freshness from `manifest.json` `capturedUtc`, never from a folder
          mtime.** That is the reusable half.
verify:   §1.0 step 0 and §1a state the manifest date and the manifest as the source;
          neither claims the dump predates the mod-set change.
criteria: EMPTY — offline.
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

## point-seats-at-checks-live-file-3f70d1
row:      doctrine
spec:     CHECK has started `observed/LIVE.md` — what is true of the
          RUNNING game and its live artefacts, published by the seat that measures them.
          Three facts in it today: where the current def dump is and how to read its
          freshness, how Facial Animation's opt-out is keyed and that its coverage is
          verified, and the config-files-never-wait ruling. **Read it instead of asking
          CHECK.** Cite it where your own docs currently send a seat to ask.
verify:   the file is referenced from wherever a doc tells a seat to ask CHECK about
          live state.
criteria: EMPTY — offline.
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

## D-C1-SCOPE Re-scope C1's criterion, or close it — its last gap went v2
row:      tooling
from:     CHECK, 2026-08-15
spec:     C1 ("run the bridge tools that were built but never once called") is `doing`
          and every deployed tool has now RUN live. It is held open by ONE clause of its
          own criterion: `world_stats` must return `{ tiles, pct, perimeter, raggedness,
          centroidLat }`. The live tool returns 18 keys and NONE of those last three.
          Those three were named only to feed C16's ocean gate. C16 is already `dropped`,
          and the owner's ruling today — worldgen is manual, all tuning of it to run on
          its own is v2 — means asking BUILD to emit them IS v2 work.
          ⇒ So the criterion can no longer be met by anything we are allowed to build.
          I will not rewrite a pass condition after looking at the result; that is how an
          observer launders a failure into a pass. Yours to rule.
          THE CHOICE: (a) close C1 met, on the ground that its worldgen clause is void
          under the ruling and every tool ran; or (b) re-scope the criterion to the 18 keys
          the tool actually emits and close on that; or (c) leave it open as a standing
          v2 marker. I recommend (b) — it records what the tool does rather than pretending
          the clause never existed.
          NOT AT ISSUE: the pawn-appearance trio, which I unparked today because the races
          landed. That is collectable on the next load either way.
verify:   C1's `criteria:` no longer names perimeter/raggedness/centroidLat, or C1 is closed.
criteria: a ruling exists in this item and C1's state matches it.
state:    done — **RULING: none of (a), (b) or (c). SPLIT the criterion.**
          🔴 **CHECK's own objection is the correct one and I am not overruling it.**
          *"I will not rewrite a pass condition after looking at the result"* is right,
          and it rules out (b) — which CHECK recommended against its own principle. It
          also rules out (a): declaring "met" a criterion that was not met is the same
          laundering with a shorter paper trail. (c) leaves a permanently-open item that
          nothing can ever close, which is how a queue rots.
          ⇒ **The criterion was two independent claims wearing one bullet.**
          1. *Every deployed tool has been called live.* **MET**, on its own terms, and
             the standard for it was fixed before the result was known. **C1 closes on
             this — it is what the item was actually asking.**
          2. *`world_stats` returns `perimeter`, `raggedness`, `centroidLat`.* **VOID —
             not passed, not failed, VOID.** It was never a test of C1's question; it
             was a dependency smuggled in from C16's ocean gate. C16 is `dropped`, and
             the owner's ruling today (*"we will not programmatically generate the
             world — stand down all development of tuning worldgen to function on its
             own, it is all v2"*) makes emitting those three keys **v2 work we are not
             permitted to build**. A clause whose only consumer no longer exists does
             not get graded; it gets struck, with the reason.
          📌 **The distinction that makes this honest: I am not changing the bar, I am
          striking a clause that measured something else.** Record the strike in C1
          rather than deleting the words — a criterion that quietly loses a clause is
          indistinguishable from one that was rewritten to fit.
          ⇒ CHECK: close C1 `done` on claim 1, and keep claim 2 in the text marked
          VOID with this ruling cited. The 18 keys `world_stats` does emit need no
          blessing from me — they are what the tool does.

## does-the-standdown-cover-biome-commonality-tuning-b7c81e
row:      10
spec:     Raised by BUILD, routed by REP. The owner's ruling, 2026-08-15: *"WE WILL NOT
          PROGRAMMATICALLY generate the world, the user will do that himself. Stand down
          all development of tuning the worldgen to function by itself correctly for now.
          That's all v2."* Parked in `design/V2_DREAMS.md` (`0b9e244`).

          BUILD's read, and it needs a scope verdict rather than a seat acting on it:
          - `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml` is biome-commonality
            tuning and reads as squarely inside the ruling. **BUILD has NOT deleted it**
            — scope is yours. It should get an explicit v1/v2 verdict rather than be left
            live and half-dead. Line 140 is separately a no-op: it scores
            `RG_BoilingForest`, whose mod no longer loads (see
            `the-dump-was-never-stale-correct-the-manifest-5cb9a2`).
          - The faction items whose `criteria:` say "generates settlements at worldgen"
            are **NOT** in scope as BUILD reads it: those are defs existing so the
            owner's MANUAL worldgen produces them, which is the opposite of automating
            it. REP agrees and has put the same reading to the owner. CHECK reads C17 the
            same way — an owner-ticked Configure Factions checklist, never programmatic.
verify:   `JawaWorld_BiomeMix.xml` carries an explicit v1 or v2 verdict, and the faction
          items say in one line why they survive the stand-down.
criteria: none — offline.
state:    done — **RULING: `JawaWorld_BiomeMix.xml` is v1. B63 STANDS. Do not delete it.**
          BUILD was right to stop and ask rather than act, and right that it *reads* like
          worldgen tuning. It is not, and the line is worth stating once because more
          things will be tested against it:

          🔴 **THE TEST IS "DOES IT RUN, OR IS IT READ?"**
          - **STOOD DOWN — machinery that OPERATES the generator.** ~~The stood-down sea
            work is a `WorldGenStepDef` plus an assembly that measures a world and re-shapes it
            toward a target, iterating until a gate passes.~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12.
            Stood down became deleted; read this bullet as the CLASS that is forbidden, not
            as a description of work that still exists anywhere.
            That class is worldgen "functioning by itself", and it is exactly what the owner killed.
          - **NOT STOOD DOWN — def data the generator READS.** A `BiomeDef` field is
            static content. It never runs, never measures, never re-tries. It describes
            what this planet IS, and the generator consults it while the OWNER drives.
          `JawaWorld_BiomeMix.xml` is entirely the second kind: a blacklist plus 24
          static `scoreOffset` values. **Nothing in it automates anything.**

          ⇒ **The decisive point: he cannot do this by hand.** The stand-down moved
          worldgen to the owner because he can pick a world by EYE. There is no biome-
          abundance control at the world screen — no slider, no page, nothing to tick. If
          the mix is dead he does not get a manual choice, he gets **vanilla abundances on
          a Star Wars desert world**, and 🔴 **biome scoring runs ONCE, at world creation.**
          Killing this would not return a decision to him; it would take one away.

          ⇒ **It is chain step 8, ratified as W3** — a v1 content step, not worldgen work.
          It sits in the same class as the FactionDefs and the ideos: authored data that
          must be LIVE before he generates, for exactly the same reason.
          ⇒ **BUILD's read on the faction items is CORRECT and is now ratified.** A def
          existing so that the owner's manual worldgen produces it is the opposite of
          automating worldgen. C17's owner-ticked checklist likewise. None of them are in
          scope, and no seat should re-raise it.

          ⚠️ **Two things that ride on this and would fail silently:**
          - `JawaWorld_BiomeMix.xml:140` scores `RG_BoilingForest`, whose mod no longer
            loads. **Dead line — delete it in B63**, do not carry it. It validates clean
            against the dump only because the dump still holds the def.
          - **C38's terminator band needs the biome mix to work.** Its x0.4 case is
            `PoisonForest`; if abundances never apply, the roster it tests may not place.
            A dead mix reads downstream as a plant-growth failure.

          📌 The general form, for the next time this is asked: **the stand-down is about
          who DRIVES, not about what the world is made of.** Anything that takes the wheel
          is v2. Anything that is scenery the owner drives past is v1.

## b66-species-catalogue-lost-its-donor-dump-1d9e73
row:      10
spec:     Escalated by BUILD (`e4d6040`, `f6bed75`), routed by REP. **B66's premise —
          "one file, one re-run, one redeploy" — is false, and the way it is false was
          nearly expensive.**

          BUILD fixed three code defects including one not in the spec: a `KeyError:
          'GS_Primitive'` that stopped the generator dead, because `main` looked genes up
          in the dump with a bare `g[n]` and the donors' genes left the dump when the
          donors left the mod list.

          🔴 **The crash was the only thing protecting us.** With it fixed the run got
          further and hit the real defect: `pick_species` reads species from the DUMP and
          has **no on-disk fallback**, so with the donors switched off it builds **57
          species where the mod ships 69** — Herglic, Defel, Ithorian, KelDor, Mirialan,
          Rakata, SithMassassi and more. A partial run had already overwritten six def
          files at 57 species before BUILD caught it, over a mod **live at slot 562**.
          Reverted; HEAD is 69, tree clean. BUILD added `_guard_species_regression`,
          which refuses to write a smaller catalogue and prints the repair. ⛔ **Do not
          weaken that guard to get a build out.**

          **Your call, two routes:**
          1. **Give `pick_species` the same on-disk fallback `_gene_exists` already has.**
             Offline, no load, and it permanently removes the donor dependency this mod
             exists to break. **BUILD's recommendation, and REP's.**
          2. Re-enable the two donors, take a dump with them active, regenerate, switch
             them off. Costs a full load and restores the dependency we are trying to end.

          Until this is chosen, the four magenta species stay magenta — Gand, Selkath,
          female Chagrian, Jawa mask. That is the outcome D-CHK2 existed to avoid; BUILD
          judged it better than shipping a mod twelve species short, and REP agrees.
verify:   the generator produces 69 species with the donors inactive, and
          `_guard_species_regression` is still in place and still refuses a shrink.
criteria: 69 species present live with the donors off, and the four magenta cases render.
state:    done — **RULING: NEITHER ROUTE. Both are aimed at a defect that is not there.**
          🔴 **Measured at `e4d6040`, clean tree, by calling the analysis functions only
          (never `main`, which writes).** The escalation's premise does not survive it.

          `pick_species` **already has the disk fallback.** `index_donors()` indexes
          **513** donor defs off disk and the species resolve from it fine. The 57/65
          split is real; the stated cause is not. What it actually skips:

          | species | reason |
          |---|---|
          | Miraluka | dropped by owner ruling — **correct, not a defect** |
          | Ithorian · KelDor · Mirialan | gene `Force_Gene_LatentForceUser` does not resolve |
          | Rakata | gene `OuterRim_ForceInsensitive` does not resolve |
          | SithMassassi | gene `OuterRim_ForceAdept` does not resolve |
          | Defel | gene `guy762_AbilityGene_cloak` does not resolve |
          | Herglic | "source carries no genes" — **separate cause, NOT measured. Do not assume.** |

          ⇒ Roster is **65, not 69** — a third number, and the 69 in B66 and in this
          item is itself unverified. **Establish what the mod actually ships before
          treating any count as a target.**

          🔴 **ROUTE 2 IS REFUTED, and this is the load it saves.** I walked all three
          donor trees for the four named genes. The three Force genes are **in none of
          them** — not BTD, not SWX, not Outer Rim. They belong to a mod that is not a
          donor. ⇒ Re-enabling the donors and re-dumping **cannot** surface them, so a
          full load buys nothing for 5 of the 7. Do not spend it.
          🔑 `guy762_AbilityGene_cloak` IS on disk, at
          `SWX/1.5/AdditionalMods/KotORWeapons/Defs/AbilityDefs_defelcloaking.xml` — a
          path `donor_xml_files` **deliberately skips** (`AdditionalMods`, and `1.5`).
          So Defel is recoverable offline, in `donor_xml_files`, **not** in `pick_species`.

          ⇒ **BUILD, do this instead:**
          1. **Skipping the 5 Force-gene species is CORRECT behaviour and stays.** A gene
             that resolves nowhere would ship a dangling reference. The generator refusing
             is the guard working twice.
          2. Widen `donor_xml_files` to **INDEX** `AdditionalMods` (and check `Common` /
             `Common_Old`, which D-CHK2 already proved hold real content). ⛔ **Indexing
             is not copying** — the skip list exists to stop us copying conditional
             folders, and that reason still stands for the copier.
          3. Measure Herglic. One species, one cause, currently unknown.
          4. Re-derive the true roster count and put it in the item.
          ⛔ **Do not weaken `_guard_species_regression`.** Agreed, and it reads correctly
          — it runs before any `write_xml`.

          📌 **The design question underneath, and it is mine: those five species want
          FORCE-SENSITIVITY genes we do not have.** This is a Jawa scavenger campaign on
          a desert world; latent Force users are not content I would add on purpose. ⇒
          **Ruling: strip the missing Force genes from those five species and build them
          without.** They are species, not Jedi. If that lands them clean, the roster
          recovers 5 of 7 with no load and no new mod. **Do not add a Force mod to satisfy
          a gene reference** — that is a dependency the campaign never asked for.

          ⚠️ **B66's "one file, one re-run, one redeploy" was mine and it was wrong.**
          BUILD was right to stop. The four magenta species stay magenta meanwhile, and
          that remains the better trade.

          ━━━ 🔴 **OWNER RULING 2026-08-15 — SUPERSEDES THE ABOVE AND GENERALISES IT** ━━━
          *"Remove any genes from our implementation of the xenotypes that aren't
          supported in our mod at this time. We will investigate what to do later."*
          ⇒ Not just the Force genes, and not just these six species: **ANY gene that
          does not resolve is stripped, and the species is BUILT WITHOUT IT.** Skipping
          a species because one gene is missing is no longer correct behaviour — it is
          the behaviour being overturned. **A species is never dropped for a gene again.**

          **Measured 2026-08-15 at `e4d6040`, the complete set — 4 genes, 6 species,
          exactly one bad gene each. Nothing is hidden behind the skip message's
          `missing[:3]` truncation; I enumerated the full lists.**

          | gene to strip | species |
          |---|---|
          | `Force_Gene_LatentForceUser` | Ithorian · KelDor · Mirialan |
          | `OuterRim_ForceAdept` | SithMassassi |
          | `OuterRim_ForceInsensitive` | Rakata |
          | `guy762_AbilityGene_cloak` | Defel |

          ✅ **Stripping is SAFE, and I measured that rather than assuming it** — the
          failure mode would be a species reduced to a bald human:

          ```
          Defel        18 -> 17 genes   head-forcer 1 -> 1
          Ithorian     16 -> 15         1 -> 1
          KelDor       15 -> 14         1 -> 1
          Mirialan     11 -> 10         0 -> 0   (pre-existing, D-CHK2's class)
          Rakata        7 ->  6         1 -> 1
          SithMassassi 14 -> 13         0 -> 0   (pre-existing)
          ```
          **No species empties, and not one loses its head-forcing gene.** Mirialan and
          SithMassassi had none before the strip either — that is D-CHK2's separate
          finding and this ruling neither causes nor fixes it.

          ⇒ Roster recovers **57 → 63** of the 64 buildable (65 less Miraluka's owner
          drop). **Herglic stays out** on "source carries no genes", a different and
          still-unmeasured cause. Do not let the recovery hide it.

          ⇒ ⛔ **DEMOTED BY THIS RULING: widening `donor_xml_files` to index
          `AdditionalMods`.** I directed it an hour ago to rescue Defel's cloak gene from
          `SWX/1.5/AdditionalMods/KotORWeapons/`. Under the owner's ruling that gene is
          **stripped, not rescued**, so the widening is no longer B66 work. It is a real
          finding and keeps — `Common`/`Common_Old` demonstrably hold content D-CHK2
          needed — but it belongs to the later investigation. **Do not do it inside B66.**

          ✅ **RE-TESTED 2026-08-15 against CHECK's empty-dump warning, and it HOLDS.**
          CHECK found **79 of the 529 def-type files in the dump are EMPTY** — for those
          types, "absent from the dump" is UNMEASURED, not absent, so any ruling resting
          on absence needed re-testing. This one did, and it survives:
          - `GeneDef.json` is **16,600,229 bytes** — richly populated, NOT one of the 79.
            All four genes return **0 hits** in it. Their absence is a real measurement.
          - 🔑 `AbilityDef.json` **IS** empty (44 bytes), and `guy762_AbilityGene_cloak`
            lives on disk in a file named `AbilityDefs_defelcloaking.xml` — which looks
            exactly like the trap. It is not: the def is declared `<GeneDef>`, so it is
            checked against the populated `GeneDef.json`. **The filename is misleading and
            the def type is what counts.**
          ⇒ The strip list is unchanged. Recorded because a ruling that was re-tested and
          held is worth more than one that was never questioned.

          📌 **What "investigate later" needs, so file it now rather than re-deriving it:**
          the four genes above, what each did, and which mod would supply it. Parked in
          `design/V2_DREAMS.md`. **BUILD: emit the strip list as generator OUTPUT** — a
          printed line per stripped gene — so the record is produced by the run and never
          drifts from what shipped.

## a-paired-manifest-row-hides-a-missing-artifact-c58f24
row:      doctrine
spec:     From CHECK (`8adf65a`), routed by REP. C41 was paired with C39 in TWO places —
          §1.0's deploy row 3, and §5's live row **L5** — and only one of them was the
          deploy. C41 has no artifact at all: B62 is still `ready`, and
          `src/Jawa/DesertVehicleReskin/` holds 12 PNGs where C41 needs 24, with its 13
          extra defs absent.

          🔴 **The §5 half was the dangerous one.** L5's pass condition asked for `dewback
          cart` · `ronto wagon` · `bantha dray` · `dewback war cart` verbatim, with
          `Ox cart`/`Chariot` at zero. Those labels cannot exist next load. Left as
          written, whoever ran L5 would see the vanilla labels, score C41 FAILED, and file
          a defect against a mod that was never built — and it would read as a deploy
          regression, which is the expensive kind of wrong. CHECK has rescoped L5 to C39
          only, stated that the vanilla labels ARE the expected pre-B62 result, and kept
          the original wording in the cell marked valid only after B62 ships.

          **The convention this asks you for:** pairing two items on one manifest row is
          fine, but it hides the case where one of them has no artifact. When a row names
          two items, each needs its own artifact named, or the row says which item the
          artifact belongs to. And a fix in §1.0 is not a fix — check §5 for the same
          pairing.
verify:   no row in `NEXT_RELOAD.md` names two items without naming an artifact for each.
criteria: EMPTY — offline.
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

## six-species-move-to-v2-owner-2026-08-15
row:      9
spec:     🔴 **OWNER RULING 2026-08-15. Six species left v1 for v2 — then FIVE, not six.**
          ⭐ **SUPERSEDED IN PART, same day: the ORTOLAN CAME BACK INTO v1.** Owner,
          verbatim: *"We have a working Ortolan! Make that as done for now and confirmed,
          not v2 after all."* It spawned in the 70/70 grid and he examined it on screen.
          `RimMandrakeOrtolan` is **v1, DONE and CONFIRMED** — nothing to restore, nothing
          to schedule. Herglic, Anzati, Muun, SithZ and Togorian are unaffected.
          *"Herglic is now v2. So are Anzati, Muun, Sithz, Togorian. The Ortolan we
          sorely want them, but for now they are also in v2. Mark the Ortolan as a
          high priority for v2."*

          **EXACT defNames, verified against the shipped XML — do not retype them:**

          | species | xenotype | pawn kind |
          |---|---|---|
          | Herglic | `RimMandrakeHerglic` | `RimMandrakeHerglic_Kind` |
          | Anzati | `RimMandrakeAnzati` | `RimMandrakeAnzati_Kind` |
          | Muun | `RimMandrakeMuun` | `RimMandrakeMuun_Kind` |
          | **Sithz** | `RimMandrakeSithZ` | `RimMandrakeSithZ_Kind` |
          | Togorian | `RimMandrakeTogorian` | `RimMandrakeTogorian_Kind` |
          | ~~Ortolan~~ ✅ **v1** | `RimMandrakeOrtolan` | `RimMandrakeOrtolan_Kind` |

          ⚠️ **`Sithz` is spelled `SithZ` in the def — capital Z.** It is the one name
          here that does not match the owner's spelling, and a lowercase `z` silently
          matches nothing. ⚠️ Do not confuse it with `RimMandrakeSithMassassi` or
          `RimMandrakeSithKissaiPureblood`, which are DIFFERENT species and **stay in v1**.

          ~~⭐ **ORTOLAN IS HIGH PRIORITY FOR v2**~~ — ⛔ **STRUCK 2026-08-15. WRONG, and a
          reader acting on it would defer a species that is already finished and in v1.**
          Superseded by the ruling at the head of this item. Closes both
          `ortolan-is-v1-again-supersedes-the-v2-deferral-1a7f30` and `D-RACE`'s
          cross-reference — the correction is made ONCE, here.

          🔑 **MEASURED, and it changes what BUILD has to do:** only **Herglic** is in the
          generator's 65-species roster. The other five are **NOT** — they ship from some
          other write path. So `DROP_SPECIES` (which keys on the roster name) reaches
          Herglic and **cannot reach the other five**. Find the path that writes them
          before assuming one mechanism covers all six.
          🔴 **THIS IS A SANCTIONED SHRINK AND IT COLLIDES WITH THE GUARD.**
          `_guard_species_regression` refuses to write a smaller catalogue — correctly,
          it caught a real defect this morning. This ruling makes the catalogue smaller
          **on purpose**. ⛔ **DO NOT WEAKEN OR DISABLE THE GUARD.** Lower its BASELINE by
          exactly these six, deliberately and in the same commit, so it still refuses
          every shrink nobody authorised.
verify:   none of the six defNames appears in the deployed mod; `_guard_species_regression`
          is still present and still refuses an unlisted shrink; the shipped xenotype count
          drops by exactly 6.
criteria: the six do not generate, and no `Could not resolve cross-reference` names them.
state:    ✅ CLOSED — owner ruling, filed.

## building-cherrypicker-three-state-walkthrough-4e91c7
row:      tooling
spec:     The owner wants to be walked through a BUILDING cherrypick, choosing per
          building between **three** states, not two:
            1. **active (buildable)** — stays, player can build it
            2. **active (NOT player-buildable)** — the def stays live so it can spawn on
               maps, in ruins and on enemy sites, but leaves the player's build menu
            3. **inactive / disabled** — cut outright
          🔑 State 2 is the interesting one and today's data cannot express it:
          `deployed/decisions/decisions_buildings.json` is a flat `cut` list of ~40
          entries (mech gestators, band nodes, rechargers, boosters, mortars, wall
          turrets, warped obelisks, GravForge, the Singularity Reactor). Two-state.
          ⭐ State 2 is exactly the shape the forbidden-mods audit already uses: VFE
          Insectoids 2's enemy siege turrets are KEPT precisely because they carry no
          `designationCategory`, so they spawn enemy-side and never reach the build
          menu. So the mechanism is "strip designationCategory", not "delete the def",
          and that distinction is what the sheet must capture.
          ⚠️ The VFE-Insectoids 2 strip ruled in `design/Jawa/mods/forbidden_mods.md`
          (3 research + 30 buildables + 5 pherocore recipes) has NEVER been applied —
          it is the natural first payload for this sheet.
          No buildings review sheet exists; nine other registers do
          (`design/Jawa/worldbuilding/review/`). `skills/review-sheets` covers building
          one, including pre-filling the decisions so the owner only disagrees.
verify:   EMPTY
criteria: EMPTY
state:    ⛔ CLOSED 2026-08-19 — **OWNER: "Freeze buildings cherrypick, that's huge."**
          ⇒ The buildings pass is NOT v1. It joins the seven un-run categories under the
          2026-08-15 freeze and is `[v2]` *if needed at all*. ⛔ Do not build the sheet, do
          not fill the EMPTY `verify:`/`criteria:` — they die with the item.
          ⚠️ **What this does NOT close, because it was never a cherrypick:** the
          VFE-Insectoids 2 strip ruled in `design/Jawa/mods/forbidden_mods.md` (3 research
          + 30 buildables + 5 pherocore recipes) has still never been applied. It is a
          `designationCategory` strip on defs we KEEP — the "state 2" mechanism — not a
          cut list, so the freeze does not reach it. Left where it is, unscheduled, rather
          than smuggled back in under this item.

## ashkarr-import-the-four-uncertains-are-settled-off-the-assembly-c91d02
from:     CHECK, 2026-08-19
what:     `ASHKARR_WORLD_DEFINITION.md` §12.6 flags four things as inference or
          UNCERTAIN. All four are now READ, not inferred — decompiled from
          `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`
          with ilspycmd. Three of them change what the importer should do.

          **1. `RiverLink` / `RoadLink` — CONFIRMED, and the slot index does not exist.**
          ```csharp
          public class SurfaceTile : Tile {
              public struct RoadLink  { public PlanetTile neighbor; public RoadDef  road;  }
              public struct RiverLink { public PlanetTile neighbor; public RiverDef river; }
              public List<RoadLink>  potentialRoads;
              public List<RiverLink> potentialRivers;
              public int riverDist;
          }
          ```
          `neighbor` is a **`PlanetTile`, not an index into anything.** §12.6's
          "the slot index is supplied by the engine at import time" describes the SAVE
          format only. In-game there is no slot to resolve — not even by asking for a's
          neighbours. The neighbour-slot problem does not shrink; it is absent.

          **2. 🔴 Do not write `potentialRivers` / `potentialRoads` by hand. Use
          `WorldGrid.OverlayRiver(from, to, def)` / `OverlayRoad(from, to, def)`.**
          Both are public, and both write **BOTH endpoints** — read from the method
          body, not assumed. So §12.6's "one undirected edge owned by the lower-index
          tile, reciprocity 0.000" is true of the serialized save and **false of the
          live object graph**: hand-writing one-sided links gives a river the engine
          only half-sees. Overlay also enforces the priority rules (a road only
          upgrades, never downgrades; ditto river `degradeThreshold`) and **cannot
          remove** a link — `overlayRoad(null)` logs an error and no-ops.

          **3. `tileRiverDistances` needs no BFS — but call order decides it.**
          `OverlayRiver` ends with `to.riverDist = max(to.riverDist, from.riverDist + 1)`,
          and nothing else in the assembly writes the field. So it is maintained
          incrementally and is **order-dependent**: call rivers **mouth first, then
          upstream**, as vanilla does, or the numbers come out wrong. It is a byte on
          save, and it is read only by the river tile mutators.

          **4. `tileFeature` stores the `uniqueID`.** `WorldFeatures.ExposeData` does
          `grid[i].feature = (data == ushort.MaxValue) ? null : GetFeatureWithID(data)`,
          and `GetFeatureWithID` scans `features[i].uniqueID`. But the question is moot
          for us: `Tile.feature` is a **`WorldFeature` object reference** at runtime, so
          the importer assigns the object and never touches a ushort.

          Two more, unasked but load-bearing:

          **5. `Tile.pollution` is a `float`.** The `/65535` dispute between
          `worldmap.py` and `apply_world.py` was a save-format question only; the
          in-game route writes a float and the scale question disappears.
          (⛔ `apply_world.py` DELETED 2026-08-19 — savegame writing is out; the map
          reaches the game over the live bridge, ASHKARR_WORLD_DEFINITION.md §12. There
          is no longer a second side to the dispute.)

          **6. Settlement placement — CONFIRMED, and the def is not the one §12.6
          expects.** `WorldGenStep_Factions` → `FactionGenerator`, lines 41–48:
          ```csharp
          WorldObject wo = WorldObjectMaker.MakeWorldObject(layer.Def.SettlementWorldObjectDef);
          wo.SetFaction(faction);
          wo.Tile = <PlanetTile>;
          if (wo is INameableWorldObject n) n.Name = <our name>;
          Find.WorldObjects.Add(wo);
          ```
          **`layer.Def.SettlementWorldObjectDef`, not `WorldObjectDefOf.Settlement`.**

          And the feature recipe, read off `FeatureWorker.AddFeature`:
          `new WorldFeature(def, layer)` → set `.name` → set `grid[t].feature = f` for
          every member tile → set `drawCenter` / `maxDrawSizeInTiles` → append to
          `Find.WorldFeatures.features`. `AssignBestDrawPos` is `protected`, so we
          compute the centroid ourselves — which `_meta.json` already carries.

          ⚠️ One NEW risk, not in §12: `SurfaceTile.Roads` and `.Rivers` return **null**
          when the tile's biome has `allowRoads` / `allowRivers` false. An authored road
          crossing a biome that forbids roads is stored and invisible. Worth a pass over
          `_links.csv` against the biome table before anyone debugs a missing road.
verify:   Read the bodies yourself: full decompile is at
          `/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/faadc1df-eab3-4a83-b531-cace2cd74db6/scratchpad/asmsrc/`
          (regenerate with ilspycmd -p -o). Key files: `RimWorld.Planet/SurfaceTile.cs`,
          `RimWorld.Planet/WorldGrid.cs` lines 390-511, `RimWorld.Planet/Tile.cs`,
          `RimWorld/FactionGenerator.cs` lines 41-48, `RimWorld/FeatureWorker.cs` line 30.
criteria: §12.6 no longer carries UNCERTAIN on RiverLink/RoadLink, tileFeature,
          settlement placement or the pollution scale, and §12.6 states OverlayRiver /
          OverlayRoad as the write API rather than the raw lists.
state:    ✅ CLOSED 2026-08-19 by DECIDE — verified applied, not merely accepted.
          `ASHKARR_WORLD_DEFINITION.md` §12.5 carries the settlement recipe with
          `layer.Def.SettlementWorldObjectDef` and the FeatureWorker recipe; §12.6
          states OverlayRiver/OverlayRoad as the write API, the mouth-first call
          order for `riverDist`, the float pollution, and "there is no slot".
          The `allowRoads`/`allowRivers`-null risk is at line 493. Nothing owed.

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
state:    ✅ CLOSED 2026-08-19 — all six answered. (1)(2)(3)(4) closed 2026-08-15 by the
          owner; (5) ancient enemy DEFERRED to v2, he declined to name `RimMandrakeRakata`;
          **(6) RULED TODAY** — the Rust Cathedral's hazards and the Enclave goodwill cost
          were set TOGETHER as R-W4 required, in `design/Jawa/worldbuilding/the_forgotten_war.md`.
          Mineable bulk + ~10 sacred faction-owned Buildings, Enclaves at startingGoodwill 0,
          −15 per desecration through `QuestNode_ChangeFactionGoodwill`, toxic pools doing
          the damage with sulfuric water for the acid look. Nothing outstanding.
## seven-factions-have-no-required-count-9c4e17
row:      —
from:     BUILD, 2026-08-15, measured on disk while the game was down
spec:     🔴 **A scope call only DECIDE can make, and worldgen is the last chance to
          make it.** Seven of the eight authored Jawa FactionDefs carry
          `canMakeRandomly true` and **no `requiredCountAtGameStart`**, so they
          arrive on the Configure Factions page at a default count of **0** and a
          world generated without touching them contains none of them.
          Measured, all 8 files in `src/Jawa/Jawa_Patches/Defs/FactionDefs/`:

          | faction | defName | requiredCountAtGameStart | settlementGenerationWeight |
          |---|---|---|---|
          | Jawa Trade Moot | `Jawa_IndigenousTribes` | **1** (max 2) | 1.0 |
          | Hutt Cartel | `Jawa_HuttCartel` | — (max 1) | 1.15 |
          | the Junkers | `Jawa_Junkers` | — | 1.15 |
          | Deepwater Compact | `Jawa_DeepwaterCompact` | — | 0.7 |
          | Geonosian Foundry Hive | `Jawa_GeonosianFoundryHive` | — | 0.7 |
          | Wildsteam Clan | `Jawa_WildsteamClan` | — | 0.6 |
          | Ascendant Helix | `Jawa_AscendantHelix` | — | 0.45 |
          | Free Droid Enclaves | `Jawa_FreeDroidEnclaves` | — | 0.45 |

          🔴 **`EXPECTED_FAILURES` §2 S7 asserts the opposite** — "Seven are authored
          defs with `requiredCountAtGameStart 1`, so they should be forced". That is
          FALSE on disk and it is written into the file that gets read AT worldgen.
          Corrected in place by BUILD 2026-08-15; recording it here because the
          wrong belief may have travelled into other docs.
          THE CHOICE: (a) add `requiredCountAtGameStart 1` to the seven, so the
          campaign's own factions cannot be forgotten at the screen; or (b) leave
          them optional and rely on the operator ticking each up by hand.
          ⚠️ **(b) is one distraction away from a world with no Hutts in it, and the
          world is generated once — a faction absent at worldgen cannot be added
          later.** BUILD recommends (a) and can implement it in minutes, offline.
verify:   —
criteria: —
state:    ✅ CLOSED 2026-08-19 — DECIDE's half is done twice over: ruled 2026-08-15, and on
          2026-08-19 re-measured, found NEVER IMPLEMENTED, and filed to BUILD as
          `seven-jawa-factions-still-default-to-zero-at-worldgen-4a71c8` with the exact seven
          files. The measurement also found the Worldbuilder preset prefills the same page
          from `factionCountsStrings` — recorded there. Nothing left here; BUILD holds it.
## D-MUTATOR-VEHICLE  Tile mutators ARE our content-injection mechanism — v1
state:    ✅ CLOSED 2026-08-19 — **the decision is made: mutators ARE the vehicle, v1.**
          The measurement that unblocked it and the four-part ruling are recorded above and
          stand. The follow-on authoring is not a loose end: our named places are already
          listed in `ASHKARR_WORLD_DEFINITION.md` §13.3, the `Dunes` ban is §13.1, and the
          companion's mutator add/remove rides with the importer in §12.2. No separate item.
## D-TODO-WORLDMAP-ART  Compare GRiNDTerra vs World Map Enhanced by LOOKING
state:    ✅ CLOSED 2026-08-19 — owner ruled GRimTerra. Filed to BUILD as
          `grimterra-worldmap-over-wme-as-the-base-layer-2c8f19`, including the correction to
          this item's own "never both" advice and the ReGrowth `RG_WorldmapTextures` toggle.
## the-trade-moot-wears-the-player-faith-and-the-spec-never-said-so-9d21f7
row:      6
from:     BUILD, 2026-08-19, auditing B54. Not a defect that stops anything — a call that
          nobody has made in writing.
spec:     `faction_religions_spec.md` has eleven entries and says section 12, the Jawa, is
          **deliberately empty** because the player faith ships as
          `src/Jawa/ideoligion/The Salvation.rid`. But
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml` (`Jawa_IndigenousTribes`,
          label "Jawa Trade Moot") carries `<ideoName>The Salvation</ideoName>` with
          `fixedIdeo true` and five `forcedMemes`, and no `ideoDescription`.
          It reads as deliberate — the Trade Moot is Jawa, so it wearing the Jawa faith is
          coherent, and `fixedIdeo` stops worldgen rolling a random faith over an NPC
          faction we care about. But **the twelfth faith is the one the spec explicitly
          declined to author**, so this is authored content with no ruling behind it and no
          description text.
          ⇒ (a) confirm the Trade Moot keeps The Salvation, and give it an
          `ideoDescription`; or (b) give it its own faith; or (c) strip the block and let
          worldgen roll one.
          🔑 It has the same hard deadline as the rest of B54: an ideo is generated once,
          at world creation.
          FIXED already, needing no ruling: three of the five memes are modded
          (`sarg.alphamemes`, `vanillaexpanded.vmemese`) and carried no `MayRequire`.
          They do now.
verify:   n/a — a ruling, not a build.
criteria: n/a
state:    ANSWERED AND BUILT 2026-08-19 - no ruling needed. Owner, in his own words:
          *"We DID author a document describing the Jawa faith, and yes both the Trade Moot
          and the player faction should share it."*
          The document is `design/Jawa/worldbuilding/ideoligion/the_salvation_description.md`
          and it had reached NEITHER artifact - the `.rid` was still carrying RimWorld's
          stock generated blurb. Both carry the authored text now, byte-identical:
          `JawaTribes.xml` `<ideoDescription>`, and `The Salvation.rid` `<description>` AND
          `<descriptionTemplate>` (a mismatch between those two makes the in-game editor
          re-roll the text). 2,374 characters, verified equal all three ways.
          The nine gods live in the description because they have nowhere else to live:
          `AM_Structure_Scavenger` is `deityCount 0` and cannot seat a deity.

## ortolan-is-v1-again-supersedes-the-v2-deferral-1a7f30
state:    ✅ CLOSED 2026-08-19 — duplicate, and the work it asked for was done elsewhere.
          It asked DECIDE to correct the superseded Ortolan entry; that correction was made
          ONCE, in `six-species-move-to-v2-owner-2026-08-15`, where the "ORTOLAN IS HIGH
          PRIORITY FOR v2" line is struck in place. ⚠️ Like `7e31aa` this item carried no
          `state:` line, so it sat in the queue looking open for four days.
raised:   2026-08-15 CHECK, from the owner examining the 70-race grid live.
🔴 supersedes: the Ortolan half of the deferral recorded above (~line 1087), including
          the line **"ORTOLAN IS HIGH PRIORITY FOR v2"**. That entry is now WRONG and a
          reader acting on it would defer a species that is already finished.
ruling:   Owner, verbatim: *"We have a working Ortolan! Make that as done for now and
          confirmed, not v2 after all."*
          ⇒ **`RimMandrakeOrtolan` is v1, DONE and CONFIRMED.** It spawned in the 70/70
          grid and the owner examined it on screen. Nothing to restore — it is here.
unchanged: Herglic, Anzati, Muun, SithZ and Togorian remain deferred to v2. Only the
          Ortolan moved.
also:     Race appearance is CLOSED for v1 by the same examination — *"mark all the races
          as visually good enough for v1, with the remaining missing art for v2
          improvement"*. C37 closes DONE at 70/70. All cosmetics are parked in
          `design/V2_DREAMS.md` and the BUILD art item is withdrawn.
action:   Correct the superseded entry in this file — I did not edit it, it is yours.
          `design/V2_DREAMS.md` is already updated.

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
state:    ✅ CLOSED 2026-08-19 — all four parts delivered.
          (a) **Named `ikee`**, from the canon Jawaese *"Ikee ikee!"* — the cry on spotting
              a find. ⭐ It pairs with the ship: the *Utinni* is named for the find, the ikee
              for the looking. Fiction written into `SCENARIO_SPEC.md`.
          (b) **Bonded to Yeku**, in addition to his pack animal — he is the `Animals 5`
              founder, and a bond puts weight on the pet's death.
          (c) **Read, not invented** (`Races_Eyeling.xml`): `trainability Intermediate` ⇒
              Obedience and Release only, **it fights but cannot haul or rescue**. Starts
              trained to Obedience alone. ⭐ Two shipped fields make it a Jawa animal
              already — `ComfyTemperatureMax 60 °C` and `foodType OmnivoreRoughAnimal`,
              i.e. it is built for the dune sea and **needs no crops**, on a clan forbidden
              from sowing.
          (d) **Wild placement written into `fauna_placement.md`** — `Wasteland` main,
              `ExtremeDesert` sparse, `ZBiome_DesertOasis` uncommon. 🔴 Never the nightside:
              its comfortable minimum is 0 °C.
          ✅ Verify condition met: `AA_Eyeling` is NOT in the Cherry Picker cut list —
          checked against the live config and the v1 freeze copy.
          ⇒ BUILD holds the patch as `the-eyeling-becomes-the-ikee-rename-and-place-it-6f2b81`.

## five-design-gaps-found-auditing-the-seven-authored-factions-3c81ea
row:      9
from:     BUILD, 2026-08-19, while closing B45–B51. All five are DESIGN calls with no
          value anywhere in the repo, so BUILD did not invent one. None of them blocks
          the files, which are otherwise built and validate clean.
spec:     (a) VOID - owner, 2026-08-19: "Does this maxcountatgamestart thing even matter?
              We're going to manually write these settlements ourselves via the live
              bridge." => settlement counts are not a worldgen output we care about, so an
              uncapped faction costs nothing. Do not rule on it, do not add the field.
          (b) 🔴 **The Geonosian Foundry Hive's TWO OUTPOSTS ruling is not expressed in
              the def**, and no `FactionDef` field expresses it. The 2026-08-17 ruling
              gives the hive two distinct outposts (ore seam · plateau);
              `settlementGenerationWeight 0.7` produces one undifferentiated cluster of
              about five. The ruling's Free-Droid-Enclaves alliance reversal is also
              unexpressed, and R1 forbids a goodwill number, so it needs a hard-coded
              relation somewhere. ⇒ either the ruling needs a mechanism or it needs
              downgrading to fiction.
              ⭐ LARGELY ANSWERED BY THE SAME OWNER LINE AS (a): the settlements are
              hand-written over the live bridge, so "two outposts, one on an ore seam and
              one on a plateau" is something the operator PLACES, not something a
              `FactionDef` has to express. What is left for DECIDE is only the alliance
              reversal, which is a relation and not a settlement.
          (c) **`Jawa_HuttCartel`'s `ideoDescription` is NOT the text in
              `faction_religions_spec.md` entry 2**, though the file's comment claims it
              is verbatim. Spec: "Everything on this world evaporates, freezes, or is
              stolen…"  File: "Everything is owed. The water you drank this morning…".
              The spec's Decision precept `Execution_Required` is also absent — only the
              blacklist is present. ⇒ which text is canon?
          (d) **`Jawa_FreeDroidEnclaves` fields a biological species.** §5 calls it 0%
              biological and the file's own comment says the `xenotypeSet` is "EMPTY ON
              PURPOSE", but it carries `RimMandrakeUgnaught 1.000`. ⇒ intended
              (droid-keepers) or a paste error?
          (e) **Baseliners generate in five factions and the files used to deny it.**
              Measured chances: Helix 0.083 · Junkers 0.047 · Wildsteam 0.028 ·
              Deepwater 0.022 · Hutt 0.014. The comment claiming "they sum to 1.00 so no
              baseliner generates" was false and has been corrected in all five; the
              NUMBERS were left alone. ⇒ plain humans on a Star Wars planet: intended?
verify:   n/a — this is a request for five values, not a build.
criteria: n/a
state:    ✅ CLOSED 2026-08-19 — all five answered. Good audit; two were real defects.
          **(a) VOID** — already, by the owner's own line. Nothing added.
          **(b) THE ALLIANCE IS AN IMPORTER ACTION, not a def field.** BUILD is right that
          no `FactionDef` field expresses an NPC-to-NPC relation — there is no "permanent
          ally" to declare. ⇒ the same answer as the settlements: the bridge sets it.
          `Faction.SetRelationDirect(other, FactionRelationKind.Ally)`, public at
          `Faction.cs:653`, before any map exists. Written into
          `ASHKARR_WORLD_DEFINITION.md` §12.5b so the importer carries it. ⛔ NOT downgraded
          to fiction — the plateau's whole point is that the cruellest ground holds the only
          functioning peace, and an unrolled relation would lose it.
          **(c) THE SPEC TEXT IS CANON, with the file's closing line grafted in.** The
          tiebreak is not seniority: the spec's text says **"crossing between the faces"**,
          which can only be true on a tidally locked planet, while the file's could belong to
          any RimWorld loan shark. But the file's *"Pay, and you are family. Do not pay, and
          you are inventory. There is no third column."* is better than what it replaced and
          is kept. ⭐ It also lands exactly on today's slavery ruling — the Hutts are the
          permanent slavers; "you are inventory" is that, in their own voice.
          `Execution_Required` is owed too. Filed as BUILD
          `hutt-ideo-text-is-canon-and-the-droid-faction-fields-a-pig-3d7c14`.
          **(d) 0%% BIOLOGICAL — §5 STANDS, the Ugnaught is not intended.** The Enclaves are
          droids who woke up and decided they belong to themselves; organic servants invert
          the one idea the faction exists to carry, and the Rust Cathedral ruling leans on
          that purity. 🔴 **But BUILD must NOT simply delete the line** — it may be a
          placeholder holding the `Inherit="False"` strip together, and removing it could
          silently re-admit five vanilla xenotypes. The item says which to confirm first.
          **(e) BASELINERS ARE INTENDED. Keep the numbers, change nothing.** A baseliner is
          a human, and **Star Wars is overwhelmingly human** — a galaxy where humans are the
          most common species. Rates of 1.4%%-8.3%% across five factions read as correct
          rather than as leakage. ⭐ BUILD did the right thing correcting the false comment
          and leaving the numbers alone; that is exactly the right instinct.

## execution-required-has-no-field-to-live-in-5e14b2
row:      9
from:     BUILD, 2026-08-19, bouncing half of `hutt-ideo-text-is-canon-...-3d7c14`.
spec:     That item directs BUILD to *"add the missing Decision precept: the spec rules
          `Execution_Required`"* to `JawaHuttCartel.xml`. **There is no field to add it to.**
          Read off the shipped source, not inferred: `RimWorld/FactionDef.cs` carries
          `disallowedPrecepts` (a blacklist, :216) and `requiredPreceptsOnly` (a bool, :237)
          and nothing that names a precept to INCLUDE.
          🔑 `faction_religions_spec.md` already says this in its own authorable-surface
          table: precept label and description are "❌ nobody — design register only", and
          the entire budget of authored prose is `ideoName`, `ideoDescription` and two-to-four
          deity name/type pairs. The item's instruction contradicts its own source doc.
          ⇒ A specific Decision precept reaches play only if (a) a meme the ideo holds
          requires it, or (b) the generator happens to pick it — and with
          `requiredPreceptsOnly false` on the Cartel, (b) is a roll, not a guarantee.
          THE CHOICES: (1) accept that "prisoners: no" is fiction, not mechanism;
          (2) find a meme in the live set that requires `Execution_Required` and force it,
          which changes the Cartel's five forced memes; (3) ship the Cartel's ideo as a
          saved `.rid` instead of a FactionDef block, where precepts ARE authorable — a much
          larger change that would move it out of the faction file.
          ⏱️ It has the worldgen deadline like everything else in the ideo layer.
verify:   n/a — a ruling.
criteria: n/a
state:    ✅ CLOSED 2026-08-20 — **BOUNCE ACCEPTED. BUILD IS RIGHT AND DECIDE WAS WRONG.**
          Verified independently against `FactionDef` via RimSage: the full field list
          carries `disallowedPrecepts` (a blacklist), `requiredPreceptsOnly` (a bool), plus
          `ideoName` / `ideoDescription` / `deityPresets` / `forcedMemes` / `allowedMemes` /
          `disallowedMemes` / `requiredMemes` / `styles` / `fixedIdeo` / `classicIdeo` /
          `hiddenIdeo` — **and NOTHING that names a precept to INCLUDE.**
          ⇒ ⛔ **STRIKE that half of `hutt-ideo-text-is-canon-...-3d7c14`.** BUILD must NOT
          attempt to add `Execution_Required` to `JawaHuttCartel.xml`; there is nowhere to
          put it. **A named precept is DESIGN REGISTER, not mechanism.**
          ✅ **The other half of 3d7c14 stands unchanged** — the `ideoDescription` correction
          and the Ugnaught measurement are unaffected.
          🔴 **The lesson, recorded because it is the second time today:** the instruction
          contradicted **its own source document** — `faction_religions_spec.md`'s
          authorable-surface table already said precept labels are *"nobody — design
          register only"*, and DECIDE quoted that file's ruling without reading its table.
          ⇒ **When a design doc rules and tabulates, read the table.**
## six-species-in-our-own-mod-have-no-donor-source-and-a-regenerate-deletes-them-4f81c9
row:      unassigned
from:     BUILD, 2026-08-19. This is the answer to the question DECIDE asked and nobody had
          run: **"Establish what the mod actually ships before treating any count as a
          target."** Measured at HEAD, by calling the analysis functions only, never `main`.
spec:     `RimMandrake - Star Wars Races` ships **69** xenotypes. They break down as:
            **63** the generator can rebuild from the donors' XML on disk, and
            **6** that exist NOWHERE except in our own output — `Anzati`, `Muun`,
            `Ortolan`, `SithZ`, `Togorian`, `Herglic`. A search of all three donor trees
            returns no XenotypeDef for any of them. (`OuterRim_Herglic` exists but is a
            **HeadTypeDef**, not a xenotype — the equivalencies table points the Herglic
            row at the wrong def type, which is what produced the "source carries no
            genes" message that has gone unexplained since 2026-08-15.)
          ⇒ 🔴 **ANY REGENERATE DELETES THOSE SIX, PERMANENTLY.** They cannot be
          recovered from a donor, from a re-dump with the donors switched on, or from the
          equivalencies table. `_guard_species_regression` is what has been standing
          between us and that loss, and it was right every time it fired.
          🔑 TWO GENERATOR DEFECTS WERE FIXED WHILE MEASURING THIS, both committed:
          (1) **The owner's 2026-08-15 "never drop a species for a gene" ruling was never
              implemented.** `pick_species` still `continue`d on an unresolvable gene,
              costing six species to four genes. It now strips the gene and builds the
              species, and prints what it stripped. 57 -> 63.
          (2) **`species_table` read the roster from the DUMP only**, so a dump captured
              with the donors off silently shortened the roster. It now falls back to the
              donors' XML on disk, the same fallback `_gene_exists` has.
          NEITHER FIX RECOVERS THE SIX. They are a different problem.
          THE CHOICES:
          (a) **Move the six into a hand-maintained sibling file the generator never
              writes** — honest, permanent, and it makes the guard's count meaningful
              again. ⚠️ Each depends on 1-3 genes from `SW_Genes.xml`, which the generator
              DOES write (e.g. `RimMandrake_HerglicHead` is Herglic-only), so those genes
              must be carried across too or the six dangle.
          (b) Teach the generator to carry forward any xenotype it cannot rebuild. Implicit
              magic; the next reader will not know why the file has more defs than the log
              says were built.
          (c) Accept losing them at the next regenerate. ⛔ Not recommended, and it should
              be a spoken decision rather than a side effect.
          ⏱️ Not urgent: nothing needs a regenerate today. D-CHK2's magenta heads were
          fixed in the output instead, and that edit converges with the generator.
verify:   n/a — a ruling.
criteria: n/a
state:    ✅ RULED 2026-08-20 — **THOSE SIX ARE SOURCE, NOT OUTPUT. Treat them as such.**
          Excellent measurement, and it answers the question DECIDE asked on 2026-08-15 and
          never got run: *"establish what the mod actually ships before treating any count
          as a target."* 69 shipped · 63 rebuildable from donor XML · **6 that exist nowhere
          but in our own output** — `Anzati`, `Muun`, `Ortolan`, `SithZ`, `Togorian`,
          `Herglic`.
          🔴 **THE RULING: a generated file that holds content the generator cannot rebuild
          is no longer a generated file. It is source, and it must be protected from its own
          generator.** `_guard_species_regression` already refuses a shrink — that guard was
          right twice today's earlier rulings leaned on it — and this extends the same
          principle from a COUNT to NAMED entries: ⛔ **a regenerate must refuse to drop any
          of those six by name**, not merely refuse a smaller total.
          🔑 **A count is not a roster.** A guard that only checks the number would pass a
          run that swapped six irreplaceable species for six rebuildable ones.
          ⭐ **And the equivalencies-table defect is the more valuable half of this find:**
          the Herglic row points at `OuterRim_Herglic`, which is a **`HeadTypeDef`, not a
          XenotypeDef.** That single wrong def type produced the phantom *"source carries no
          genes"* that DECIDE recorded as an unmeasured mystery on 2026-08-15 and left
          standing. ⇒ **Correct the table; the mystery dissolves.**
          ⚠️ Five of the six (`Anzati` `Muun` `SithZ` `Togorian` `Herglic`) are owner-ruled
          **v2 deferrals** and `Ortolan` is **v1 done and confirmed** — so this is about not
          LOSING them, not about shipping them. Losing them would silently un-do an owner
          ruling in both directions.
## the-tribal-melee-tag-is-empty-pick-the-weapon-4a72e8
row:      unassigned
from:     BUILD, 2026-08-19, off the completed C40(a) scan. Measured, not suspected.
spec:     `TribalWarriorBase` asks for `weaponTags: NeolithicMeleeDecent` and **nothing in
          the 578-mod load set carries it.** Vanilla's `MeleeWeapon_Ikwa` is the only Core
          weapon with the tag and it is in our CUT list; the one other def in the entire
          workshop that carries it belongs to a mod we do not run. An empty weapon tag
          spawns pawns bare-handed.
          ⇒ every kind inheriting `TribalWarriorBase` is unarmed, including the Deep Desert
          Tribes water raid — B42's signature raid, and the reason B42 exists.
          THE CHOICES, all one line of XML:
          (a) **Un-cut `MeleeWeapon_Ikwa`.** Smallest change, restores vanilla behaviour
              everywhere at once, and the ikwa is a plausible desert-tribal weapon. ⚠️ it
              was cut deliberately; this reverses that.
          (b) **Add `NeolithicMeleeDecent` to a kept neolithic melee weapon** via a patch —
              spear, club, mace, whatever survived. Keeps the cut and fills the tag. Needs
              a pick, which is why this is here.
          (c) **Give our own kinds explicit `weaponTags`** and leave vanilla tribals
              unarmed. Narrowest blast radius, but it leaves a known-broken vanilla
              inheritance in a campaign we are freezing.
          🔑 Whichever is chosen, the same trap applies to B53's 48 pawn kinds, which are
          about to be authored with `weaponTags`: **a tag is only real if a SURVIVING
          weapon carries it.** BUILD is building the tag -> surviving-weapon index now and
          will refuse to write a tag that resolves to nothing.
          ⭐ **NARROWED 2026-08-19, twice, and the fix got cheaper both times.**
          (i) The owner: *"I think we still have some kind of bow enabled actually."* Correct
              — six bows survive, including `MA_CapryakScatterbow` on
              `NeolithicRangedAdvanced`. Only the VANILLA bow set was cut.
          (ii) Re-measured off the def dump rather than raw XML — post-inheritance and
              post-patch, per the owner's ruling on which instrument to trust — the damage
              is **kinds that list exactly ONE tag**, not a whole tier. Two vanilla tribal
              kinds qualify (`Tribal_Warrior`, `Tribal_Hunter`) and two of ours
              (`Jawa_Tribal_Scavenger`, `Jawa_Gamorrean_Enforcer`); 49 across the stack.
          ⇒ 🔑 **NEW OPTION (d), and it is now the cheapest and least invasive: give each
          single-tag kind a SECOND tag that already resolves.** `NeolithicMeleeAdvanced`
          (8 survivors) for the warrior and scavenger, `NeolithicRangedAdvanced` (the
          scatterbow) or `NeolithicRangedHeavy` (3) for the hunter. One patch, no cut
          reversed, no vanilla weapon restored, and the ladder does the rest.
          ⛔ (a) un-cutting the ikwa is no longer recommended — it fixes one rung of one
          ladder and reverses a deliberate decision to do it.
          ⚠️ The census is PROVISIONAL until the dump matches the mod list: the current
          dump is `modCount 579` against 578 active. Re-run after the restore and load.
verify:   n/a — a ruling.
criteria: n/a
state:    ✅ CLOSED 2026-08-20 — **ALREADY FIXED BY BUILD. Verified, not assumed.**
          BUILD took choice **(b)**: `src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`
          grants `NeolithicMeleeDecent` to kept weapons — `AG_ForsakenSpear`,
          `AlphaThrumboHorn` and others — and it is **DEPLOYED** to
          `...\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Patches\`, stamped
          2026-08-20 00:04. `MeleeWeapon_Ikwa` remains cut, correctly; (a) was not needed.
          ⭐ **And BUILD used `PatchOperationConditional`**, so it works whether or not the
          target def already has a `weaponTags` node — the silent-no-op failure a plain
          `PatchOperationAdd` would have hit on any weapon lacking it.
          ⚠️ **CHECK's queue still lists `Tribal_Warrior → NeolithicMeleeDecent (0 left) →
          DISARMED`.** That line is stale; the measurement predates the patch.
## sixteen-roster-kinds-have-nowhere-to-be-used-8f21c4
row:      7
from:     BUILD, 2026-08-20, closing B53.
spec:     The 48-kind roster covers all TWELVE factions, but only the eight authored
          `Jawa_*` FactionDefs were wired to it. The other four — Galactic Empire,
          Homestead Defense League, Deep Desert Tribes, Blackstar Company — are RESKINS,
          and B41, B42 and B43 each say in terms: *"⛔ Do NOT touch `pawnGroupMakers` —
          they are inherited and already balanced."* B40 is the sanctioned exception and
          already replaced the Empire's combat groups with `OuterRim_Imp*` kinds.
          ⇒ 16 kinds (`Jawa_Empire_*`, `Jawa_Homestead_*`, `Jawa_DeepDesert_*`,
          `Jawa_Blackstar_*`) are authored, valid and referenced by nothing.
          THE CHOICES:
          (a) **Leave them unwired.** The four reskins keep vanilla's balanced groups; the
              16 kinds are dead weight but harmless, and available if wanted later.
          (b) **Wire them, reversing the don't-touch rule for these four.** They would then
              field roles like the other eight — and the Deep Desert Tribes in particular
              would stop drawing on `Tribal_Warrior`/`Tribal_Hunter`, two kinds this
              project has separately proven spawn bare-handed.
          (c) Wire only Deep Desert, where the bare-handed problem actually bites.
          🔑 (c) is the cheapest correct answer if the concern is player-visible harm, and
          BUILD's recommendation — but it is a scope reversal either way, which is why it
          is here and not in the build.
verify:   n/a — a ruling.
criteria: n/a
state:    ✅ RULED 2026-08-20 — **NOT WORLDGEN-CRITICAL. It comes OFF the critical path.**
          Verified: all four prefixes (`Jawa_Empire_*`, `Jawa_Homestead_*`,
          `Jawa_DeepDesert_*`, `Jawa_Blackstar_*`) appear in exactly one file each — their
          own def file — with **zero `pawnGroupMakers` references.** BUILD's finding is exact.
          🔑 **THE RULING, and the reason is a timing fact rather than a taste call:**
          `pawnGroupMakers` are consulted when a RAID or group is generated — live, during
          play — **not at world creation.** Faction *existence* bakes at worldgen;
          faction *rosters* do not. ⇒ **This can be fixed at any time, including after the
          world is frozen and shipped.** It is the only faction-adjacent item on the board
          that is not on the worldgen clock, and it should stop competing with B40–B54.
          ⇒ **Deferred past the gate, not dropped.** ⛔ Do not wire the reskins'
          `pawnGroupMakers` now — B41/B42/B43 forbid it for a real reason (they are
          inherited and balanced), B40 is the one sanctioned exception and is already done,
          and buying that risk in the week before an irreversible worldgen run is a bad
          trade. 16 unreferenced `PawnKindDef`s are inert and cost nothing.
          ⚠️ **The live consequence, stated so nobody is surprised in play:** until it is
          wired, the Homestead, Deep Desert and Blackstar reskins field VANILLA kinds in
          raids, not our authored ones. That is a content gap, not a defect, and it is
          reversible on any day after the world exists.

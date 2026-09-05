<!-- status: live — written by the Fable seat at the close of the 2026-08-30 handoff sprint (FABLE_HANDOFF_SPRINT_1). Audience: the Opus 5 (or any successor) seat continuing this work. -->
# Handoff — continuing the Salvation layer without Fable

_Fable access ends 2026-08-31 evening. This sprint converted every taste-heavy
open question into ruled canon, finished prose, or a verified spike, so what
remains is execution. This file is the map. It states what IS, what each
workstream needs next, and the short list that genuinely needs the owner._

## Reading order (cold start)

1. `salvation_engine_review.md` — the RULINGS table first. Every decision of
   2026-08-30 is there; the findings below it are the arguments. **Nothing in
   the rulings is re-litigable without the owner.**
2. `divine_satiation_engine.md` — the canon of record: pantheon blocks, §8b
   audit, the nine matrix pages (curse columns already re-specced under the
   F10 law), folk practice, 3×3, attenuation, reign politics, balance-keeper
   lane — all landed.
3. `salvation_engine_build_spec.md` — M0–M5 milestones. Build M0 first; it
   ships alone (satiation + signed letters, no fronts, no curses).
4. `narrator_corpus/` — frame + three triad files: FINISHED prose for every
   letter class, all nine voices. Treat as shipping text, not drafts: extend
   in each file's own register, never flatten. The livery table in
   `narrator_frame.md` is authoritative for F9 signatures.
5. The satellite specs: `god_intercession_spec.md` ·
   `devotional_sacrifice_catalog.md` · `divine_dilemma_events.md` ·
   `first_contact_chains.md` · `trap_renaissance_spec.md` ·
   `covered_pit_traps_spec.md` · `worldbuilding/colony_visibility_stat.md`
   (peer-authored; Annex A holds the source-VERIFIED mechanism) ·
   `worldbuilding/sacred_sites_pass_1.md` (peer-authored) ·
   `research_normalization_principles.md`.
6. `src/RimMandrake/Spikes/README.md` — three compile-clean proofs with
   VERIFIED symbol lines and the quicktest questions FOUNDRY must answer.

## The five laws that must survive the model change

These are the judgment calls a successor is most likely to erode by accident:

1. **F10 — a curse ENACTS the god's want, never inversion.** If you author a
   new curse and it reads as "punishment", it is wrong. M/L curses carry
   their exit-verb inside the prose, priced in the god's own currency.
2. **F9 — no unsigned act.** Every divine effect routes through the
   signature kit (toll, light, livery). The build spec enforces this
   structurally (letters only via the SignatureDispatcher) — keep it so.
3. **Contact before bill; foreboding before L.** A god introduces himself
   before he charges; L-tier acts are foreshadowed by their toll. Veiled
   discovery (F4) depends on this.
4. **§19.5 — no material parachutes.** Boons are opportunity/mood/events.
   Three legal borderlines were ruled deliberately (Ohm-L, Oomo-L,
   Mob'Unloo-L); do not extrapolate from them.
5. **Manage gods against each other, never head-on** (F13 intercession;
   exposure = Ozzik − Ishko). And the fall-triad never blurs: Zizzik
   celebrates the mechanism, Ozzik mourns the loss, Sh'kaar is the
   inevitability.

Also: **the RimMandrake moniker on everything that ships** — "Jawa" is lore
vocabulary only (memory + covered_pit_traps_spec §9).

## Per-workstream: what's next, and what it needs

| Workstream | State | Next act | Needs human? |
|---|---|---|---|
| Engine build (M0) | spec + corpus complete | FOUNDRY builds M0 per build spec; every Harmony target marked VERIFY must be read in source first (rimsage) — never trusted from the spec | No — until M2's owner questions |
| Narrator corpus | nine voices shipped | wire into M0 letter dispatch; author judgement-verdict + Council lines once the scorecard/rite specs exist (flagged in triad files) | Owner should READ the corpus once for voice approval |
| Visibility dial | spec + Annex A verified | build as its own small mod (safe core first per its §5); Spike 3 is the patch skeleton | Curve endpoints + global-vs-threat-scoped fork (owner, listed in its §6) |
| Pits (RIMMANDRAKE_PITS_BUILD_1, FOUNDRY queue) | spec ruled; Spikes 1+2 prove the tricks | build core mod; spawn-mass quicktest matrix first | No |
| Trap renaissance | spec ruled | absorption patches (ion mine, capture net unlock, gas rows); primitive tier after pits core exists | Minify whitelist curation = a review-sheet for the owner |
| Sacred sites | peer spec shipped | verify the flagged Ishko dark-landmark gap against the ~46 unused LandmarkDefs; then placement is the OWNER authoring the map | Placement is his |
| Research normalization | principles doc | gated "after the droids land"; when it opens, run the census its §4 demands before any surgery | Tech-ceiling + theology-lock rulings |
| Dilemmas / chains / catalog / intercession | specced | become content defs inside M3–M5; text exists, wiring doesn't | No |

## Door rulings — owner, 2026-08-30, on his way out (AUTHORITATIVE)

- **The engine mod's name is `RimMandrake Ninefold`.**
- **Curse severity: survivable events only.** An L curse delivers a situation
  — lethal if mishandled, never a scripted named-colonist death.
- **The "Ask the Hutts" bark in triad_fall.md STAYS** — the seed for the
  ledger arc is deliberate.
- **FOUR folk gestures promote to micro-mechanics** (he chose all four
  offered, superseding the promote-3 mark in the engine doc): Zizzik's decoy
  (placeable broken thing per room, ties to the slumber), Ta'Baa's
  leaving-bag (tiny buildable, eases the rooted-clock, speeds evacuation),
  Sh'kaar's shade-line pause (pawn hesitation animation at light
  boundaries), Mob'Unloo's set-it-down (no direct handoffs — build last,
  it touches item-transfer jobs).

## What genuinely needs the owner (the remaining list)

1. Read the Narrator corpus once — approve or correct the nine voices.
2. Engine build spec §OPEN-FOR-OWNER, remaining: UI diegesis level, reign
   pacing, first-contact order override.
3. Visibility §6: difficulty curve endpoints; threat-scoped vs global
   patching; does a returned-to tile remember its Visibility.
4. Minify whitelist/denylist — **the review-sheet is READY, he just clicks:**
   `Transient/minify_whitelist_sheet.html` (257 prefilled rows; decisions save
   to `worldbuilding/data/minify_whitelist_decisions.json`). Note the reframe:
   MinifyEverything is in the stack, so the denylist carve-out matters as much
   as the whitelist (trap_renaissance_spec §2b).
5. Sacred-site placement on THE map (his pen, with worldview.py).

## Sprint tail (added after the door rulings, same day)

Door rulings propagated into the build spec and engine doc ·
`folk_gesture_mechanics.md` (four promoted gestures, with the set-it-down
demotion clause) · `narrator_corpus/judgement_and_council.md` (verdicts,
arrival clauses, compère tissue, the chorus barks — the voice layer is now
complete end to end) · the minify census CSV committed under
`worldbuilding/data/`.

## Process notes for the successor seat

- The queue/ledger runs through `rimflow` (see CLAUDE.md); peer windows ship
  work concurrently — **re-read the queue and `git log` before starting
  anything from this list** (this sprint nearly duplicated two items a peer
  had already shipped the same day).
- FOUNDRY holds the bridge. Specs here deliberately specify tests without
  running them.
- Numbers marked TUNE are first-guesses; the tuning protocol is the
  throwaway-save rig named in the build spec and the Visibility spec.
- When a ruling here conflicts with anything older, this sprint's docs win —
  supersession pointers were written into `divine_satiation_engine.md`
  (§3c, §4, §4c, §4d) already; extend that discipline.

## Reboot addendum — 2026-08-31, end of the Fable window (read this before the table above)

The per-workstream table above is one day stale. What changed on the 31st:

- **THE RENAME IS DONE.** Phase 2 executed: all mods live under
  `src/{RimMandrake,RimStarWars,RimUtinni}/` with `mandrake.<tier>.<name>`
  ids, `RM_/RSW_/RUT_` prefixes, nested namespaces; game side redeployed and
  ModsConfig swapped. `naming_lint.py` = the gate (1 expected SPLIT
  violation). 🔴 **The def dump is STALE against the new names — nothing
  that reads the dump is trustworthy until RENAME_VERIFY_WINDOW_1 runs at
  the next game-up** (refresh, re-fingerprint, validate_patch, magenta
  sweep, minimal-list load). Phase 3 = JAWA_PATCHES_SPLIT_1.
- **The ruling backlog is EMPTY.** Seven cards on the 31st: Ninefold M0
  CALLED (provisional corpus — the owner redlines live letters, felt-only
  diegesis, max-reign forces challenge, emergent first contact); Visibility
  build called (threat-scoped, desert-remembers tile memory); beast Laws
  2/3/4 ruled (engine mass, quicktest coefficient, armor-absorption hide);
  stolen turrets redeploy degraded.
- **Trap §2b re-scoped by the owner**: battlefield capture of enemy
  defenses (traps lifted intact, sandbags, turrets, fuel nodes) — the old
  minify whitelist sheet is DEAD, deleted, category rule instead.
- **New spec families since the table**: the seas program (`the_seas.md`,
  `depths_concept.md` — three lanes, waterline patch item filed), beast
  normalization (`worldbuilding/beast_normalization_spec.md`, four laws),
  graffiti (`graffiti_spec.md` — five families + the shaming tier;
  SUPERSEDE-now ruled over the spec's companion recommendation), structure
  injection roster (promises/whispers, `structure_injection_roster.md`),
  covered pits (ruled, build item queued), pantheon slide art committed.
- **Build queue for FOUNDRY** (all offline-startable): NINEFOLD_ENGINE_M0_1 ·
  COLONY_VISIBILITY_BUILD_1 · RIMMANDRAKE_PITS_BUILD_1 ·
  GRAFFITI_FRAMEWORK_BUILD_1 · BEAST_DANGER_NORMALIZATION_1 ·
  TILE_STRUCTURE_DESIGNS_1 · SEAS_WATERLINE_PASS_1 · JAWA_PATCHES_SPLIT_1 ·
  ISHKO_DARK_LANDMARKS_1 · DEPTHS_ODYSSEY_VERIFY_1 · DUMP_DRAWSIZE_CAPTURE_1 ·
  SELFTEST_DRIFT_REPAIR_1. Gated on game-up: RENAME_VERIFY_WINDOW_1 (RUN
  FIRST), the muffalo coefficient quicktest, the Odyssey source read.
- **Needs the owner's hands only**: corpus redline on live M0 text ·
  sea-monster art session (SW_SEA_MONSTERS_ART_1) · sacred-site placement ·
  RESEARCH_TREE_NORMALIZATION_1 (still gated on droids).
- Process cautions that bit this window: a directory-scoped commit swept
  selftest-built game DLLs into the public repo (amended out; bin/obj now
  ignored); peers ship queue work without claiming — git log before starting
  anything.

## Second reboot addendum — 2026-08-31, the last Fable sitting (BENCH)

The owner spent the final window on spec-out ("what could Fable spec while we
retain access" — the ranked plan is `design/FABLE_WINDOW_PROPOSITION.md`) and
ruled everything put to him via question cards. **Ten specs delivered, closed
and pushed; nothing below is open design — it is execution.**

- **The Depths went from concept to executable**: `depths_concept.md` v2
  (owner's second seed: conductive fluid, weapon malfunction, oxygen, drag,
  adapted races NOT Jawa, Deepwater faction, Empire bolt-hole) + two donor
  surveys (§10 + `mods/underwater_donor_scan_2026-08-31.md`) + FOUNDRY's
  source read (clone-job verdict) + `worldbuilding/depths_build_spec_v1.md`
  (RULED: independent `RM_PressureRating`; sight cap rides NWN fog).
- **Fog of war RULED, Route B**: CAI 5000's combat AI + NWN Real FoW with
  CAI's fog off; `memegoddess.searchanddestroy` DROPPED. Evidence:
  `mods/cai_fog_deep_dive_2026-08-31.md` (CAI unlicensed → pattern-only; NWN
  Apache-2.0 both ends; pawn sight never glow-driven — lamp-cone needs one
  scoped Harmony clamp). Execution: `FOW_ROUTE_B_INTEGRATION_1` (FOUNDRY).
- **Specs shipped and their items CLOSED**: sarlacc
  (`worldbuilding/sarlacc_spec.md` — tentacles must be PAWNS, pocket-map
  nesting legal, AmbientHorror+Custom is a WORLD-CREATION DEADLINE for the
  scenario spec) · Nine Voices (`RimMandrake/nine_voices_cast_bible.md`; old
  Part A persona is dead outright — nobody's; Ohm is one of nine, the ship-mind is the Narrator) · research taxonomy
  (`research_tree_taxonomy.md` + FOUR canon rulings at
  `research_tree.taxonomy_ruled`: seven tabs, Research Reinvented KEPT AS
  SUBSTRATE — it already co-writes 448/515 rows, theology decoupled, Ultra
  reachable priced brutally / colony techLevel INDUSTRIAL) · Oracle LLM
  wiring (`RimMandrake/llm_ingame_wiring_spec.md`; RULED cloud key, budgets
  3/1/2, experiment-first → `ORACLE_EXPERIMENT_SPIKE_1`) · dust storms /
  boiling water / visible growth / scraggly flora (specs in their item
  files; Tornado.cs is the devil skeleton, boiling water is pure defs,
  growth is 10%-quantized+cultivated-only, the rainbow flora is named and
  `AB_RockyCrags` grows tundra by mistake) · Cantina Kitchen
  (`cantina_kitchen_spec.md`) · Tusken water raid (item file; steal-and-leave
  is mostly SHIPPED — register corrected) · race regen
  (`race_regen_architecture.md` — invert the generator, byte-parity
  acceptance).
- **Register corrections made in place** (do not re-derive): V2_DREAMS
  sarlacc unknowns MEASURED (heart surface-only; PitGate siteable-with-C#);
  V2_DREAMS Tusken entry corrected; `llm_voice_preauthoring.md` Part A
  superseded + Part B's RimDialogue measured ABSENT from disk (RimTalk is
  subscribed instead).
- **Awaits the owner only**: sea-monster mockup picks (18 PNGs + 6 sheets in
  `Transient/sea_monsters_mockups/`, regeneration prompts preserved in the
  item file) · the outgrown-mod audit sitting (7 examine candidates) · the
  Depths concept ratification line · RESEARCH_TREE gate ("after the droids
  land").
- **Standing practice added 2026-08-31**: decisions go to the owner as
  AskUserQuestion CARDS, free text always open (his words: "Ask me question
  cards but let me always respond freely if needed").
- Codex imagegen note: calls can run 3–7 min and the WSL-side timeout kill
  leaves the Windows codex.exe running — files land AFTER the wrapper
  reports failure. Check the output dir before re-rolling.

## Third reboot addendum — 2026-09-01, BENCH (supersedes the "awaits the owner" list above)

- **Three reviews are IN PROGRESS for the owner tonight; keep them fresh.**
  1. Proposal suite (125 rows) — the sidecar server DIES with this session;
     on wake, restart it and hand him the NEW url+token:
     `cd design/Jawa/worldbuilding/review && python3 ~/.claude/skills/review-sheets/assets/serve_sheet.py --sheet proposal_suite_review.html --decisions proposal_suite_review.decisions.json --no-open`
     The decisions file is committed with `touchedCount: 3` (savedAt
     2026-09-01T15:24Z) — the page merges per row, his rows are safe. When he
     says done: `--status`/`--overrides`, read overrules AS A GROUP, then
     convert verdicts into items under PROPOSAL_SUITE_REVIEW_1.
  2. Pawn-flavor phase-2 register (497 rows, FS-Access file link) — verify
     the `savedAt`/touched stamp on its decisions file before consuming;
     0/497 touched at last check is NOT a completed review.
  3. Livestock picks — three sheets in `Transient/livestock_mockups/`
     (`SHEET_onnik/karrask/moornak.png`); he names one index per animal;
     generator `src/RimStarWars/Livestock/art/gen_livestock_mockups.py`.
- **Sea-monster picks are RULED: keep ALL 18 as separate creatures**, BENCH
  chooses alignment (SW-source variants). Only execution remains
  (`SW_SEA_MONSTERS_ART_1`).
- **Outgrown audit is RULED and applied**: Betures + Minotaur + RIMMSqol
  dropped from the live ModsConfig and `modlists/ModsConfig.FULL.LATEST.xml`;
  Astronomy/Stealing/WASDed kept. Next cold load's first string:
  `wildAnimals` counts at authored size (~29, not 1024) ⇒ closes
  WILD_ANIMALS_PADDED_LISTS_1 and triggers cast-biome EXCLUSIVITY (ruled).
- **Ownership fabric ruled and specced** (`ownership_settlement_spec.md`,
  canon `ownership_fabric`, two mods) — items filed for FOUNDRY.
- **Green-lit and filed**: FIRE_ECOLOGY_LOOP_1 (built, live-deployed, owner
  ruled LEAVE LIVE; hook fixes noted on the item), WEATHER_SUITE_SLICE_1
  (built offline, awaits live pass), LIVESTOCK_STARTER_TRIO_1 (mockup round
  first). Everything else in `design/Jawa/proposals/` waits on the sheet.
- **Research normalization sitting RULED** (`research_tree_taxonomy.md` §7,
  canon `research_tree.sitting_ruled/chains_ruled/tech_gating_ruled`); the
  448-techprint stamp is REAL but UNATTRIBUTED (RR does not write it) —
  re-measure owed to FOUNDRY; manifest lacks an `access_class` column.
- Owner's two in-game eyeball checks still owed: Salvagers absent from the
  faction UI; ISEKAI trait degree labels.

## Fourth reboot addendum — 2026-09-01 evening, BENCH (supersedes the third's review list)

- **Proposal suite: 19 owner rulings are IN the decisions file and BAKED into the
  page** (`proposal_suite_review.html`, `fd5223d3`). Two `cut`s: `gas:tar-interplay`
  (real) and `gas:tanker-economy` (note reads as a correction — treat as v1 with the
  correction unless he says otherwise). **Owed:** bank the 19 notes into
  `tar_pits_deep_design.md` / `propane_gas_deep_design.md` / `fire_ecology_deep_design.md`
  as "what IS", then items under PROPOSAL_SUITE_REVIEW_1. Read them as a group first:
  canal-flow is ruled *RimMandrake-tier general mechanic*, not Utinni.
- ⛔ **Sheet plumbing lesson, paid twice tonight:** a Save-As link picker TRUNCATES the
  decisions file on "Replace" before the page reads it (19 rows → 3; recovered from
  git). Every remaining sheet using `showSaveFilePicker` must switch to
  `showOpenFilePicker`; `check_sheet.py` passes a sheet with no decisions file on disk
  and with empty `sheetPath`/`decisionsPath` — three LESSONS_INBOX lines filed.
- **Forsaken Crags fauna: RULED, all three approved** (Cindermare, Skarnix, Tellurox);
  decisions frozen `decidedBy: owner-said`. **Tellurox = livestock genetically modified
  by the Helix faction** (owner's words); FOUNDRY ports the three names into RUT_ defs.
- **Techprint stamp attributed**: Configurable Techprints
  (`com.makeitso.configurabletechprints`), 455/522 projects; NOT Research Reinvented
  (no such symbol in either live RR DLL). Items noted; `research_manifest_validate.py`
  check 7 corrected. TECHPRINT_FACTION_GATING_1 now routes through that mod's settings.
- **Pawn flavor phase 2**: all 1,783 rows approved (owner-said); PAWN_FLAVOR_PHASE2_APPLY_1
  shipped by FOUNDRY tonight; PAWN_FLAVOR_SILENT_NONAPPLY_1 closed.
- **Dungeons rulings recorded** (`dungeons_arc_spec.md` §0/§2.7/§3.9): thaw = QuestNode +
  map trigger; power core = vanilla `AIPersonaCore`; vaults 325×325; V5 = new organic
  landmark. 13 straddle rows of the split map confirmed at proposed tiers.
- **Transient/ is TRACKED AND PUSHED (standing rule)** — the owner reviews from another
  machine. Two sweeps tonight removed ~165 MB; remaining `fire*/diag*/check*.py` are
  2.7-day fire-ecology debug scripts, leave until they pass 3 days. Review dir lost 13
  outmoded sheets + `art_biomes/`.
- Still owed to the owner: nothing blocking. FOUNDRY released the bridge and stamped
  seat-ready; four live passes authorized.

## Correction — 2026-09-04, FOUNDRY (supersedes the proposal-suite status above)

⛔ **Do not restart the sidecar server or regenerate `proposal_suite_review.html`'s
prefill** — the third reboot addendum's instructions above are stale. The sitting
completed and `PROPOSAL_SUITE_REVIEW_1` closed at `46edfb7e` (2026-09-02T06:34:28Z).
`proposal_suite_review.decisions.json` is `frozen: true` (124/125 rows touched,
posture prefill-ships — the untouched row keeps its pre-filled ladder position, it
is not pending): 13 cuts, 101 v1, 6 v2, 5 dream. Source of truth and current status:
`design/Jawa/proposals/README.md`. Remaining work is banking the frozen verdicts
into the deep-design docs and per-proposal build items, never re-opening the sheet.

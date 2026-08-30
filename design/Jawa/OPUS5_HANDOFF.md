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

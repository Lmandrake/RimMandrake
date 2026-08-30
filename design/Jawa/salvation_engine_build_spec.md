<!-- status: draft — Fable handoff sprint 2026-08-30, item FABLE_HANDOFF_SPRINT_1; owner has ratified the SHAPE (card-session rulings in salvation_engine_review.md); numbers are first-guess, marked TUNE -->
# The Salvation Engine — build spec

_This is the document the mod is constructed FROM. Canon: `divine_satiation_engine.md`
(the pantheon of record + the matrix). Rulings: `salvation_engine_review.md` (RULINGS
table). Sibling specs: `god_intercession_spec.md`, `devotional_sacrifice_catalog.md`,
`divine_dilemma_events.md`, `first_contact_chains.md`, `colony_visibility_stat_spec.md`,
`trap_renaissance_spec.md`. Text source: `design/Jawa/narrator_corpus/`. Naming: the
**RimMandrake moniker** on everything that ships (`RimMandrake_Salvation`, `RM_*`
defNames) — "Jawa" appears only in player-facing lore text._

**The one-sentence architecture: a deterministic bookkeeping core that only ever
reads the game and sends letters, wrapped around a small, separately-toggleable
edge that injects incidents.** If the edge breaks, the religion still runs — felt
through letters, gestures, and mood — because the core never depends on the edge.

---

## 1. Architecture — safe core / fragile edge (§9 of the engine doc, kept)

**SAFE CORE (build first, ships alone as M0–M2):**
- A `GameComponent` (`RM_SalvationEngine`) holding all state (§2), ticking clocks,
  receiving event signals (§6), rolling invocations (§4), and dispatching **text
  and gestures only**: letters from the pre-authored corpus, light/sound cues,
  mood thoughts (ThoughtDefs), and stat offsets that ride existing systems
  (StatParts, ThoughtWorkers — no incident injection).
- **v1 has NO LLM.** Every line of prose comes from `design/Jawa/narrator_corpus/`
  keyed `(god, occasion, tier)`. The corpus is data (Keyed/DefModExtension or a
  simple keyed-string table); the engine never composes sentences, it selects them.
- Deterministic and replay-safe: same state + same event stream ⇒ same outputs,
  except where a seeded Rand roll is explicit (participation, mood walk).

**FRAGILE EDGE (build last, behind a mod setting, default ON but severable):**
- Injected incidents: L curses that fire raids/breakdowns, L boons that fire
  opportunity events, dilemma choice-letters, challenge events, the controlled
  waking. Every edge feature degrades to a letters-only fallback if its hook
  fails (the §9 fallback ruling) — **write the fallback into each feature, not
  as an afterthought.**

## 2. Data model (all Scribe'd, §9 below)

Per god (×9), a `GodState`:
- `satiation` int −100…+100. Bands: Exalted +60 · Content +20 · Neutral ±19 ·
  Slighted −20 · Wrathful −60 (canon §1). No drift to baseline.
- `mood` int −100…+100, hidden random walk. **F8 RULED: mood is weather —
  NEVER rendered as a number or bar.** It surfaces ONLY through the gesture
  dispatcher (§2b) and Narrator adjectives baked into letter selection
  (each corpus letter family has calm/sour variants; selection reads mood).
  Walk: every 60k ticks (1 day) `mood += N(0, σ_god)` clamped, σ per the §2
  temperament table (Ishko low ~4, Zizzik/Ohm high ~12). TUNE.
- `veiled` bool — F4: starts true for all nine; flips at first contact (§8).
- `grievance` int ≥0 — F14 watchers: accrues while another god fronts and this
  god is Slighted-or-worse (+1/day, +3 if Wrathful. TUNE). Resets on his own
  reign or a successful intercession by him.
- `shield` — intercession state per `god_intercession_spec.md`: earned-standing
  float, patience counter, open-debt flag.
- `firstContactDone`, `lastReignTick`, per-god `signatureKit` ref (§4d).

Colony-level:
- `front: GodRef|null` + `reignStartTick` + `reignDeeds` ledger (the current
  reign's demand progress + taboo record).
- `decadence` int — rises per consecutive reign by the same god (F14): each
  repeat reign, boon tier rolls −1 step, demand tier +1 step. TUNE.
- **The four clocks** (one-directional, never zeroed by satiation alone):
  - `zizzikBank` — grows per "quiet day" (no breakdown, no mental break,
    +1; perfectly ordered day +2. TUNE). Spent by THE WAKING (curse L),
    shrunk by devotions (`devotional_sacrifice_catalog.md`), spendable by the
    controlled-waking rite (shaped M instead of unshaped L).
  - `shkaarMeter` — +per violent battle participated in (scaled by bodycount);
    − slow decay only during true peace; − per calming verb (death not yours).
  - `tabaaRootClock` — +1/day landed on the same tile; resets on launch.
  - `ozzikPride` — + per ambition act (§8b weights); vents via Unburdening/
    dedication; **exposure = max(0, ozzikPride − ishkoStanding)** — F13
    Option C RULED: pride covered by discipline is survivable pride.
- `visibility` — READ from the Colony Visibility stat (own spec/mod); the
  engine writes contributions to it and reads the composite. Integration
  point only; do not duplicate its math here.
- `shipMapId` — attenuation anchor (§7).

### 2b. The gesture dispatcher (Mood-as-weather made real)
A small scheduler that, at most once per ~4 hours game-time per god (front god
~4× as often — "loudest"), emits an ambient micro-effect from the god's
signature kit when his mood crosses thresholds: a lamp flicker in his palette,
a door hesitation, a hum change, a one-line Narrator murmur (Messages, not
letters). Gestures are COSMETIC — never mechanical. This is the only window
onto mood, by ruling; build it in M1, not later, because mood without gestures
is invisible dice (the exact frustration F8 exists to prevent).

## 3. Front selection & reigns

- **Judgement at landing (the chapter rite):** on gravship landing, aggregate
  the per-map deed ledger (every §8b delta recorded since the last landing,
  summed per god). The scorecard letter (Narrator corpus, judgement family)
  reports the top movers. **Front = highest effective standing among unveiled
  gods** where `effective = satiation + w_m·mood + w_g·grievance` (w_m≈0.3,
  w_g≈0.5. TUNE), with two overrides: a god whose L-curse fired unanswered
  since last landing takes precedence (his matter is unfinished); the two
  evil gods front only via their own meters (Zizzik: post-WAKING aftermath
  reign; Sh'kaar: meter above threshold — dreaded dispensations, never
  routine picks).
- **Reign length:** until the next landing (the loop is the liturgy — the
  2026-08-29 sketch, ratified direction). Mid-reign flip ONLY via
  reign-breaker taboo (matrix L taboos) or a won challenge.
- **Challenges (F14):** when any non-front god's `grievance` crosses threshold
  (TUNE ~15), fire a challenge choice-letter: **yield** (front changes, small
  tribute demand, peaceful) or **hold** (challenger's next curse tier
  pre-armed +1). Decadence (§2) independently thins repeat reigns so parking
  a favorite is possible but ever more expensive — ruled: possible at
  escalating cost, never forbidden.

## 4. Invocation rules (the reign engine)

Roll cadence: one invocation opportunity per game-day per relevant god (front
god always; non-front gods only on their own extreme events). TUNE.

- **(a) Boons** — front god only, from his matrix page. Tier odds scale with
  band (Content: mostly S; Exalted: M common, L possible) × decadence penalty.
- **(b) Demands** — issued at reign start (S) and mid-reign (M/L), tracked in
  `reignDeeds`; met demands raise satiation and next-boon tier; unmet demands
  age into grievance, not instant curses (a god asks before he takes).
- **(c) Taboos** — event-checked, not polled; an L taboo is the reign-breaker.
- **(d) Curses** — **F10 LAW (ruled): only from the re-specced curse columns**
  (engine doc matrix, re-specced 2026-08-30) — a curse ENACTS the god's want
  against your interest; every M/L carries its exit-verb, and the engine
  TRACKS the exit condition and lifts the curse the tick it is met (the lift
  gets its own corpus line — relief must be as signed as wrath).
- **Participation bias (§5, kept exactly):** pleased gods act often, angry
  gods rarely-but-memorably, neutral gods never. Implement as tier-odds
  tables per band, not ad-hoc ifs.
- **(d2) Signature dispatch (F9, ruled + "even more"):** every invocation
  routes through one `SignatureDispatcher.Play(god, weight)`: the god's toll
  sound (**tolls repeat by tier: S×1, M×2–3, L×several, with foreboding lead
  time before L events** — the owner's explicit ask), light palette shift,
  letter livery. NO UNSIGNED ACT — enforced structurally: the letter/incident
  API is only reachable through the dispatcher.
- **Foreboding:** L-tier anything is telegraphed 6–24h game-time ahead
  (TUNE) by escalating gestures + one dread letter. Contact-before-bill (§8)
  and foreboding-before-L are the two hard politeness laws of the engine.

## 5. Intercession (per `god_intercession_spec.md`, F13 ruled)

- Shield earned by devotion-while-content (standing accrues; the **begging
  rule**: offerings made after a curse's foreboding begins count zero and
  offend). When a curse would fire and an eligible intercessor (per that
  spec's table) has standing ≥ cost: curse cancelled or downgraded, the
  warning-look letter plays (corpus, intercession family), a debt-to-
  intercessor opens (a demand on his behalf), his patience decrements.
- Ozzik intercedes cheapest and adds `ozzikPride` each time (the trap
  extended into the safety system — keep this exact asymmetry).
- Exposure arithmetic already in §2 (pride − Ishko standing).

## 6. Event wiring (the §8b rows → code)

One static `RM_Signals` facade; everything below posts `(rowId, map, payload)`
to the engine. Hook families — candidate classes named where known, **VERIFY
means: confirm against the live 1.6 DLL via rimsage/decompile before coding;
never trust this table as measured**:

| Row family | Hook type | Candidate | Status |
|---|---|---|---|
| Repair completed | Harmony postfix | `JobDriver_Repair` toil finish / `Building.HitPoints` restored | VERIFY |
| Deconstruct/scrap repairable | Harmony prefix | `Building.Destroy(DestroyMode.Deconstruct)` | VERIFY |
| Research finished | Harmony postfix | `ResearchManager.FinishProject` | VERIFY (name stable across versions) |
| Construction (new hi-tech) | Harmony postfix | `Frame.CompleteConstruction`, filter by techLevel/defName list | VERIFY |
| Trade completed | Harmony postfix | `TradeDeal.TryExecute` | VERIFY |
| Mental break | Harmony postfix | `MentalStateHandler.TryStartMentalState` | VERIFY |
| Breakdown | Harmony postfix | `CompBreakdownable.DoBreakdown` | VERIFY |
| Raid arrival | Harmony postfix | `IncidentWorker_RaidEnemy.TryExecuteWorker` | VERIFY |
| Kill/death (contextual §6 judging) | Harmony postfix | `Pawn.Kill` — read dinfo for cause/light/cover | VERIFY |
| Battle participation (Sh'kaar meter) | poll + postfix | lord toil / `Pawn_MindState.lastCombatantTick` aggregation | VERIFY — hardest row; accept approximation |
| Birth / marriage / lovin' | ritual outcome + Harmony | `RitualOutcomeEffectWorker.Apply`; lovin' via `JobDriver_Lovin` postfix | VERIFY |
| Launch / landing | Odyssey gravship | gravship launch/arrive method (Odyssey assembly) | VERIFY — M2 gate |
| Eclipse/flare/weather | poll | `GameConditionManager` daily scan | known-safe |
| Threat points (F12 replace-not-stack) | Harmony | `StorytellerUtility.DefaultThreatPointsNow` | VERIFY — owned by Visibility spec |
| Prisoner acts (capture/sell/emancipate/death-match) | Harmony + ritual | `Pawn_GuestTracker` transitions; death-match via ritual def | VERIFY |
| Theft/caught (trap+minify layer) | our own mods post directly | `RM_Signals` | ours |

Rows not wired in a milestone simply don't move gods — the engine must be
row-incomplete-safe from day one (missing signal = silence, never error).

## 7. Attenuation (F2, ruled)

Full engine (boons/demands/taboos/curses/gestures) runs **only on the ship's
map** (`shipMapId`: the map containing the gravship / home). Caravans and
other maps: deed deltas still RECORDED (the gods see; the ledger is global),
but expression is letters-only, no invocations. Identify the ship map by the
gravship's parent map each landing — VERIFY the Odyssey handle; fallback:
`Find.AnyPlayerHomeMap` with an explicit TODO.

## 8. First-contact scheduler (F4 + F15)

- All nine `veiled` at start. A veiled god accrues satiation silently; when a
  chain trigger from `first_contact_chains.md` fires (each chain names its
  trigger), run the authored five-beat sequence, unveil, mark contact.
- **One unveiling at a time**, min 1 day between (queue by trigger order);
  **contact-before-bill law:** a veiled god may never curse; if his first
  signal would be a curse, the contact chain fires instead and the bill waits.
- Dilemma options for veiled gods are hidden (ruled in the dilemma spec).

## 9. Save shape

`GameComponent.ExposeData`: Scribe the nine `GodState` structs, colony fields,
clocks, reign ledger, contact queue, active curses with their exit conditions
(as tag strings, not closures), corpus-cooldown memory (no letter repeats
within N days). Everything is plain ints/bools/defName strings — **no refs to
Things** (survives any map loss). Version-stamp the component for migration.

## 10. Build milestones (each independently shippable; test on the 22-second minimal list — FOUNDRY has the bridge, so these are specs for THEIR runs, not instructions to run now)

- **M0 — Ledger + letters.** GodStates, §6 rows for the five easiest hooks
  (research, trade, breakdown, mental break, weather), satiation moving,
  first-contact chains firing, corpus letters dispatching with livery.
  NO fronts, no curses. TEST: dev-spawn events; assert satiation deltas match
  §8b table; assert no letter fires unsigned; assert veiled→contact ordering.
- **M1 — Gestures + mood.** The walk + gesture dispatcher + calm/sour letter
  variants. TEST: force mood extremes via debug gizmo; observe gesture cadence.
- **M2 — Fronts + judgement.** Landing scorecard, front selection, reigns,
  demands, decadence. Needs the launch/landing hook. TEST: scripted two-launch
  session; assert scorecard sums equal ledger; assert front = argmax rule.
- **M3 — Curses + boons + exit-verbs** (fragile edge begins). Foreboding
  pipeline, exit tracking, letters-only fallback flag. TEST: force each god's
  S/M curse; assert exit-verb lifts; assert L foreboding lead time.
- **M4 — Intercession + challenges + controlled waking.**
- **M5 — Dilemma events + delight tier** (Ishko delivers, lure hooks) + the
  Visibility integration when that mod lands.

## 11. OPEN-FOR-OWNER (genuinely his, everything else is TUNE)

1. ~~Severity ceiling~~ ✅ **RULED (door ruling, 2026-08-30): survivable
   events only** — an L curse delivers a situation, lethal if mishandled,
   never a scripted named-colonist death.
2. **Diegesis level of the UI:** are the nine satiation bands ever shown as a
   panel (even post-contact), or only ever felt through letters/gestures/the
   hologram room? (The review leans diegetic; the call is his.)
3. **Reign pacing feel:** reign-per-landing is ratified direction, but long
   sits make long reigns — does a max reign length force a challenge?
4. ~~Mod name~~ ✅ **RULED (door ruling, 2026-08-30): `RimMandrake Ninefold`.**
5. **First-contact order override:** the chains doc proposes encounter order;
   he may want a scripted first god for campaign start.

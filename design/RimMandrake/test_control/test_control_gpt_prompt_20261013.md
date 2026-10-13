# Task: what should a live-game test harness WATCH, and what else should it INSTALL, so test runs stay controlled?

## Context
RimWorld 1.6 (Unity/Mono, ~600 mods on the owner's list, a 23-mod test tier for validation; all five DLCs always loaded). LLM agents drive the live game through a "bridge" (RimBridgeServer plus our JawaBench companion DLL, which can add Harmony hooks and new bridge tools). Validation / north-star suites run scripted rows (spawn a thing, step N ticks, read a state, PASS/FAIL/UNMEASURED). An external telemetry stack (VictoriaMetrics + SQLite + Grafana + RimPulse alerts) already ingests TPS, tick-stage timings, world-pawn count, bridge-call timings, deploy/change events and host metrics.

## Why we are asking again
Attached is your 2026-10-10 review of our "map awareness" design, what FOUNDRY actually built from it, and the new ticket. Your review kept on-demand scene reports primary and deferred any cadence recorder "until a measured gap remains". The gap is now measured:
- 2026-10-13, pass 7: a site builder warped the game clock ~10 days forward (to reach mid-summer noon) on a populated map. The whole test colony died. No instrument noticed; the owner saw RimWorld's "you've let all your colonists die" letter on screen. The same warp also decayed the ash the test then sampled, turning a mod row into a false FAIL.
- Recurring: a mech cluster lands, mechs wipe the colony, while the tester waits for a colonist to come do a job and records a timeout as a FAIL.
- Recurring: a stale modal dialog silently blocks every later bridge call.
The owner's words: "for all PAWNS on the map, record their vitals as a function of time. Alive, hurt, hostile, dead, mood ... We asked that many such telemetry channels be hypothesized that would detect when conditions were 'far from bland' for testing purposes, but that this would be useful at other times." Also: "warping ahead in time like that is an EXTREMELY risky proposition in the game. Almost anything can happen."

## The owner's questions (answer both, generously — "let's get creative")
1. **So what ARE all the things we should be watching for as telemetry that would help control agent awareness of game state to enable better control of testing runs?** He named: raids, traders, mech clusters, bad weather, modal dialogs, hostile pawns. What else? Be exhaustive across RimWorld 1.6 + all DLCs (Royalty, Ideology, Biotech, Anomaly, Odyssey): incidents, game conditions, quests, letters/alerts, pawn vitals (alive/hurt/downed/hostile/dead/mood/mental state/needs), fire, temperature, infestations, map-layer/gravship transitions, time jumps, pause/speed state, UI state, log error bursts, etc. For each channel: what it detects, how to read it cheaply in Verse/RimWorld (label VERIFIED-from-knowledge / PLAUSIBLE / UNKNOWN; do not invent API names), cadence (tick-sampled series vs event), and the "far from bland" threshold that should flag a run.
2. **What other things might we install than just telemetry to help ensure controlled test runs anyway?** Prevention and control, not just observation: e.g. a "test sandbox" game mode, storyteller/incident gates, invulnerable or auto-healed test colonists, auto-dismissed modals, safe time-advance primitives that refuse when a population is at risk, map freeze/quarantine fields, snapshot-and-rollback around rows, tripwires that abort or mark a row INDETERMINATE, synthetic "witness" pawns, deterministic weather, quest suppression, faction-relation pins, etc. Rank by value / cost / risk to test validity (what a control could HIDE that a real player would see).

## Also
3. How should the observations feed a per-row verdict (CLEAN / DISRUPTED / INDETERMINATE) without false positives from the mod under test itself?
4. What is the minimal first build (a handful of channels + one or two controls) that would have caught both incidents above?
5. Three or four genuine decisions for the owner, no more.
Format: numbered sections, tables where useful, no filler.

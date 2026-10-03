# UTINNI_DISCOVERY_ACHIEVEMENTS_1 — a discovery achievements mod for the Utinni scenario

Owner, typed 2026-10-02: *"Make a ticket to create an achievement mod unique to the utinni scenario
that makes all of the discoverable content and unique mod capabilities clear so you know to discover
it and play with it. Doesn't give you any rewards it's just a helper for players to have more fun.
Could put options for players to add small rewards tied to them in options if we want. But that's
not the point. Sending out to a subagent for a design pass, ask gpt, and send it back to me for final
questions."*

## spec

1. Design pass (subagent): what counts as discoverable, how a player learns an achievement exists
   without spoilers ruining it, how unlocks are detected, where it lives in the tier grammar, and the
   Mod Settings (rewards off by default; optional small rewards).
2. GPT consult on the design, with research on achievement/discovery systems in RimWorld mods and
   similar games.
3. Owner sitting for the final questions. No build before that.

## verify

- A design doc exists with the GPT consult cited, and the owner has ruled its open questions.

## Addition 2026-10-02 (owner, typed)

*"Add to the design pass that achievements can be rewarded with Jawa lore or world lore should the
player seek that."* An unlocked achievement may reveal Jawa or world lore, opt-in for players who want it.

## Ruled 2026-10-02 21:50 PDT

Design at `design/RimMandrake/utinni_discovery_achievements_design_2026-10-02.md` (rulings table at
its end). Utinni-tier only, Utinni-ship-shaped riddle display with flip-over hints, click-through
optional lore, optional rewards off by default. Design closed; build waits on the build pause.

## Build status — 2026-10-02 (BENCH build helper, after the owner lifted the build pause)

**Built:** `src/RimUtinni/Atlas/` (`mandrake.rut.atlas`, "RimUtinni: Scavenger's Atlas", namespace
`RimMandrake.Utinni.Atlas`). Compiles (winbuild); no Harmony.
- `AtlasEntryDef`: label/description (shown once found), `riddle` (card face), `hint` (card back),
  optional `lore` + `loreVoice` (click-through), `category` (= ship region), `completion`
  (Seen/Used/Performed), `triggers`, optional `subjectPackageId`, optional `rewardThing`/`rewardCount`.
- Eleven trigger kinds, subjects resolved by NAME at runtime (absent mod reads "absent from this
  world", never an error): ThingSeen (unfogged, optional player-owned), TerrainPresent (slow cadence,
  temp terrain included), ResearchFinished, HiddenItemDiscovered (read-only; never SetDiscovered),
  PlanetLayer, GameCondition, Weather, Hediff, Signal (EndsWith; also `Atlas.Notify(tag)` for any mod by
  reflection), LoreStage (reflection on `GameComponent_LoreStage.GetStage(ladderId)`), GodUnveiled
  (reflection on `GameComponent_Ninefold.IsUnveiled`).
- `GameComponent_Atlas`: records keyed by defName string (unknown ids kept as archived), idempotent,
  first poll in a save backfills silently, `LoadedGame` re-backfills, signals via SignalManager,
  rewards future-only (only discoveries after rewards were switched on), dropped by pod.
- `MainTabWindow_Atlas` ("atlas" tab): the Utinni drawn in placeholder shapes (hull, the foreign-plated
  reaching arm, the broken dead prong, spine vanes, ventral factory pods, reliquary heart that warms as
  the Atlas fills, running lights that glow in proportion to entries found). Each entry is a lamp in
  its category's region; click a lamp for its card; click the card to flip riddle to hint (animated);
  a lit card flips to "what the riddle meant" and offers "Read the memory" (lore dialog), never pushed.
- Mod Settings: detection on/off, poll interval, hints allowed, hints name the thing, show absent
  lamps, counters, toasts, flip animation, lamp pulse, small rewards (OFF by default) + size, per-region
  on/off, reset to defaults.
- 24 entries (creatures 3, giants 4, places 3, weather 3, resources 2, crafts 4, gods 3, ship 2), every
  subject verified against src/ and the game's Data by `selftest_atlas.py` (in `run_selftests.py`).
- First script: `validation.py` + `northstar_plan.py` (mock GREEN 20/20; four injected defects each
  turn it red) and walk `design/validation_walks/RimUtinni/Atlas.md`.
- Deploy: dry run only (not deployed, not in ModsConfig).

**Owed:**
- `ATLAS_LIVE_FIRST_RUN` — NOT run live; NEXT: with the bridge free, deploy and run the suite
  (`northstar_driver/live_session.py --mod Atlas --plan src/RimUtinni/Atlas/northstar_plan.py`); expect
  to correct the debug-action path shape first (validation.py docstring lists three likely corrections).
- Owner eyes on the tab — the ship silhouette, flip feel, lore dialog; NEXT: open the Atlas tab in a
  live session with him and take his notes on the layout.
- Art (no artpipe jobs queued): a painted Utinni silhouette plate for the tab background (to replace the
  drawn shapes, same region layout), lamp sprites (dark / lit / absent), a card frame (face and back),
  a reliquary-heart glow, and optional per-entry icons shown once lit.
- Lore leaves are drafts in in-world voices, written from `design/Jawa/reconciled_lore/` without stating
  hidden truths (R25); NEXT: an authoring sitting reviews the 24 riddles, hints and leaves.
- Remaining entries: the rest of the nine gods (7), more rites (`RUT_Rites_*`), the other Antiquities
  stages, Propane Lake mechanics, Pyrelands fire front, Long Hunger, Gizka bait, sea catch/floor twins,
  ship vermin breeding, biome mechanics per the bedazzle scorecards; a signal-trigger entry once a
  mechanic emits one.
- Uncovered by the script so far: per-region toggle (list field), terrain/LoreStage/god triggers, the
  backfill-on-load path, the reward drop.

# BRIDGE_STORY_ALERT_TALE_TOOLS_1 — 5 gems from a full Find.X sweep

Filed 2026-08-29, FOUNDRY. Owner: "look more deeply... scour for any others. There
may be additional gems hiding." Method: cross-checked every static accessor on
`Verse/Find.cs` (~75 of them, the master list of every top-level game subsystem)
against the live tool surface. **43 were completely untouched.** Most are rendering/
UI internals with nothing worth exposing (WorldDebugDrawer, PawnCacheRenderer,
UniqueIDsManager, Tutor, ...); these five are real capabilities.

## Spec

New file `JawaBenchStoryTools.cs` (5 tools, all ungated):
- `jawa/alerts_list` — resolves the ORIGINAL roster's own UNCERTAIN row
  ("AlertsReadout.activeAlerts is private - list_alerts needs reflection"). One
  reflective field read; everything on `Alert` itself (`Active`, `Label`,
  `GetExplanation()`, `Priority`) is public. Answers "what does the game think is
  wrong right now", read-only.
- `jawa/tale_list` — `TaleManager.AllTalesListForReading`, public.
- `jawa/tale_record` — ⭐ **the answer to a problem this project already documented**:
  `JawaBenchPawnTools.cs`'s own header says there is NO free-text field on a Pawn,
  full stop, and that per-pawn notes would need storage built from scratch. Wrong —
  `TaleRecorder.RecordTale(def, pawn).customLabel = "..."` is exactly the mechanism
  the ENGINE ITSELF uses for its own custom-labeled tales (`GravshipUtility.
  SettleUtility` etc.). Scoped to 1-2 Pawn args on purpose — `TaleFactory.MakeRawTale`
  fills a Tale subclass's fields by matching ARG TYPES with no documented contract,
  and guessing a generic multi-type binder risked exactly the kind of wrong-guess
  this project's rules forbid. The pawn-only pattern covers most of the 90+ real
  `TaleRecorder.RecordTale` call sites grepped from source.
- `jawa/story_stats` — `StoryWatcher.statsRecord` (raid/threat/colonist-loss counts)
  + `StoryWatcher_Adaptation.AdaptDays`/`TotalThreatPointsFactor` — ⭐ the actual
  multiplier applied to every FUTURE threat's points from recent colonist losses.
  Nothing on the bridge could read this before; `jawa/weather_get`'s threat-points
  read is the storyteller's current roll, this is the adaptation factor feeding it.
- `jawa/faction_goodwill_situations` — `GoodwillSituationManager.GetSituations` etc.,
  the breakdown of WHY a faction's goodwill is capped/offset. Extends
  `jawa/faction_goodwill_check` (the number) with the reasons.

## Verify
Builds clean, 0 errors 0 warnings, first pass. 286 unique `jawa/…` names, no
duplicate alias (full-surface re-scan). **Not deployed** — game up, BENCH holds
bridge. Once deployed: `alerts_list` against a real active alert (e.g. a raid
warning); `tale_record` on a scratch pawn, confirm the customLabel sticks and
`tale_list` reads it back; `story_stats` after a colonist death, confirm
`adaptDays` moved.

## criteria
- [x] Owner directive: look deeper, scour for gems.
- [x] Full `Find.X` sweep (75 accessors), 43 untouched found, triaged for real value.
- [x] Every signature read from 1.6 source, not guessed — including the deliberate
      SCOPING-DOWN of tale_record rather than guessing a generic arg binder.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [ ] Deployed and proven live. Needs the game down, then bridge.

--- history ---

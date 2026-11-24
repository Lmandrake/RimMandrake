# BOUNDARY: the first exception of a session, Design Version 0.1.0

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFirstExceptionCore.cs` (all of it), `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFirstException.cs` (all of it).
Item: `RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY`; needs design
`design/specs/2026-11-23-bridge-v2/02_needs_design.md` §10. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_first_exception_core.py`. The live proof is
`src/RimMandrake/bridgetools/prove_three_tools.py`.

`jawa/first_exception`. The tap arms itself when the bridge registers the companion (at the main menu, after the cold
load). It listens in two places: in front of `Verse.Log.Error` and `Log.ErrorOnce`, before the game's 10,000-message
stop, and on Unity's own log callback. `action=read` returns the first exception and the first error of the session and
of the open window, each with text, stack, tick, program state and time. `action=arm` opens a new window (a scene or a
visit); the session's first is kept. `action=plant` throws a known exception, in the test profile only.

## LIMITS

- **16 different exceptions kept after the first; 256 different keys counted; 8,000 characters of text and of stack.**
  Danger: a storm of exceptions (the census has two sessions that died of one per frame) fills the memory, and a reply
  too large to read. The counts stay exact for the total.

## DOES NOT SURVIVE (not promised)

- **errors-before-the-arm.** The cold load is over when the tap arms. The reply says how many errors the game's own log
  window held then, and that the window keeps only its last messages.
- **an-exception-that-nobody-logs.** One that a mod catches in silence, or logs as a warning, is not seen.
- **a-unity-only-exception-after-the-cap.** At 10,000 messages the game turns Unity's logger off. The reply then says
  that the Unity channel may be blind. `Log.Error` is still seen.
- **an-error-text-without-the-word.** An error is an exception when it comes as a Unity exception or its text holds a
  word that ends in `Exception`. Every other error is kept as an error.

## PROMISES (each one is owed a test of the same name)

- **the-first-is-kept-through-a-flood.** The first exception stays the same entry after 20,000 later ones, and the counts
  are exact.
- **an-error-is-not-an-exception.** A plain error never takes the place of the first exception, and the first error is
  kept beside it.
- **a-new-window-keeps-the-sessions-first.** `arm` clears the window's first and not the session's.
- **not-armed-or-blind-is-never-none-seen.** A tap that is not armed reads NOT_ARMED; a blind channel reads
  NONE_SEEN_PARTIAL with its cause; NONE_SEEN only when every channel was listening.
- **one-error-counts-once.** An error that reaches both channels counts once; an `ErrorOnce` that the game keeps silent
  still counts, as silenced, and can be the first.
- **memory-is-bounded.** Kept entries, keys and text lengths stay inside the limits; what was not kept is counted.

**LIVE PROOF** (2026-11-23): ArchSmall, all rows of `prove_three_tools.py` at 9d022c7087 PASS (45 of 45 with the other two tools). On Steve1 (testq `J20261124T011611Z-348324`) the tap also caught a real exception of RM_Dustveil (`RIMMANDRAKE_FIX_THREE_WEIRD_EATERS_WITH_NO_THINK_TREE`).

Later lists beside this page: `polish.md`, `next_version.md` (none yet).

# NINEFOLD_RUNTIME_PROOF_BLOCKED_1 — partial check, deploy is stale, left doing

Ninefold compile-fix VERIFIED (ready:14, was 6); runtime firing UNPROVEN -
GameComponent.Instance null on ignoreModCompatibility loads, all hooks incl.
research silent; needs a normal-load or fresh new-game test.

## 2026-09-05 (FOUNDRY) — partial check on BENCH's live session, bridge released

Took the bridge briefly while it was free (BENCH's own restart+proof session
was already up: `Player.log` shows `[RimMandrake.Ninefold] ready: 14
event-hook patches.`, a normal load, `ticksGame: 15872`, `mapCount: 1` —
looked like an active hands-on session with the debug log window and a
minimap open, not a paused quicktest).

**Found**: zero `[Ninefold]` log lines anywhere in the whole session
(`grep` for the literal `^[Ninefold]` prefix, one hit only for the "ready: 14"
startup line). `ApplyDelta`'s own log line is gated on `Prefs.DevMode`
though — **did not confirm DevMode's actual state before concluding
anything**, so this is suggestive, not proof, of hooks staying silent. The
open `EditWindow_Log` (Debug log) window is circumstantial evidence DevMode
is on, not confirmation.

**Also found**: neither of today's two new Ninefold hooks
(`Patch_FireStarted`, `Patch_PawnDowned`, both committed after BENCH's
deploy) are in the currently-loaded DLL —
`jawa/harmony_patches typeName=FireUtility methodName=TryStartFireIn` returns
`methodCount: 0` (nothing patches it at all, not even a check that it's
absent specifically), and `MakeDowned`'s 8 real postfixes are all
third-party mods, none from `RimMandrake.Ninefold`. Expected — no redeploy
happened since those commits, and redeploying needs the game DOWN, which
this active-looking session is not a good moment to force.

**Released the bridge without redeploying or forcing a restart** — did not
want to kill what looked like an in-progress hands-on session on an
ambiguous read (see `[[map-state-is-disposable-debug]]` vs. a real session
distinction; erred toward caution here since dev windows were open,
suggesting a human at the wheel).

## Owed next
- [ ] Confirm `Prefs.DevMode` directly (a bridge read, or ask) before trusting
      the "zero log lines" finding as evidence hooks are silent — it may
      just mean DevMode is off and the log gate never fires even on
      correctly-working hooks.
- [ ] A definite non-log test: read `GameComponent_Ninefold`'s satiation
      vector directly (no tool exists for this yet — `jawa/get_defs`-style
      reflection read, or a new small tool) before and after a real kill/
      research-completion event, rather than relying on a `Prefs.DevMode`-
      gated log line at all.
- [ ] Redeploy the current DLL (has both new hooks + whatever BENCH's fix
      was) once the game is next legitimately DOWN, then re-run the above.

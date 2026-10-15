# GSS C# ratchet — BENCH, 2026-10-14

## 1. Review status (code_review_status.py check)
Start: 61/61 GSS .cs files (Source/ + SelfTest/, obj/bin excluded) already CLEAN by content hash
(last marks 2026-10-11 and later). No DIRTY file, so no reachability or review pass was owed at start.
After this pass's two edits, both files were re-reviewed in full and re-marked (section 3).

## 2. Static per-game state audit (lesson 20261015T025544Z)
GSS was already covered by `static_state_audit.md` (same folder): every GSS per-game static is listed
SAFE in the ratchet `selftest_static_game_state.py` (54/54 PASS, re-run at the end of this pass).
Re-read for this pass: `RM_MapComponent_Aerial` holds only instance tables (anchorLive, lays, drops, swings:
thingID-keyed but per Map instance, so a reload builds new ones); its statics `tapMats`/`TapPaths` are
keyed by look name (not per-game). Nothing new.

## 3. Defects fixed
- **Overhead-wire sparks ignored two Cables settings** (`Aerial/RM_MapComponent_Aerial.cs`): fallen-wire
  sparks + glow used a hard-coded cap of 24 instead of "Most sparking ends per map", and fallen-wire
  sparks/glow and power-tap clamp sparks ignored "Sparks only while the power overlay is open". Now the
  same `SparksAllowed` predicate as the cord graph and a cap from the setting (separate budget, same size).
  The Cables "Breaks and sparks" section now says so in a line.
- `GimmeSomeSlackMod.cs`: the Single-colour label clamped the colour index to a literal 4 instead of
  `ExtCordColors.Length - 1` (the slider already used the length).
No machine selftest for the spark gate (needs a live map); owed live check in live_worklist.md.

## 4. Mod Settings audit
Against CLAUDE.md "Every mod ships superb Mod Settings": PASS overall.
- One entry, two tabs (Cables 26 settings, Overhead lines 22); every setting grouped, searchable,
  per-section reset, scope tags audited ([now] everywhere; nothing touches worldgen, so no worldgen labels owed).
- Master switches for both halves; all-off degrades to vanilla art (cords) / no architect entries and hidden
  spans with power still carried (aerial). Defaults = shipped behaviour (settings_audit.py: OK, defaults match).
- Machine checks: `selftest_settings_screens.py` (GSS#Cables + GSS#Aerial mutation rows) PASS;
  `settings_audit.py` GSS row OK, no findings.

## 5. Larger gaps (listed, not fixed)
- No dependent-control greying: sub-settings stay live-looking when their master is off (Cables master,
  break readout, tapsEnabled/tapEvents -> theftGoodwill/perDay/sightRange). No SettingsKit helper for it
  exists; a kit-level feature, not a GSS fix.
- No "reset everything" button on either tab (per-section resets only; ResetToDefaults exists for probes).
- Fallen-wire shock tuning is fixed in code: ignite chance per sweep 0.35 (`RM_FallenWireShock.IgniteChancePerSweep`)
  and the knockout length are not settings; knockback is, and is still marked PROVISIONAL.

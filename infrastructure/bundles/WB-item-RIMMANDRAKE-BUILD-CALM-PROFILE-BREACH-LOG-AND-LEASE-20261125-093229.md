# WB-item-RIMMANDRAKE-BUILD-CALM-PROFILE-BREACH-LOG-AND-LEASE-20261125-093229

System: the calm profile of BRIDGE v2.0 (boundary.md §CALM PROFILE). One member.

## Done
- `RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE`: class REAL. Built at 5f1549339b: JawaBenchCalmProfileCore.cs (pure),
  JawaBenchCalmProfile.cs (Verse half, tool jawa/calm_profile), calm_profile.py (certificate lines), CalmProfileSelfTest harness,
  selftest_calm_profile.py (11 of 11, 20 plants red), prove_calm_profile.py (live, 5 rows). Red on base: the selftest file did not
  exist (ticket, 2026-11-23); each check red on its plant.

## Learned
- The certificate (live/tap_certificate_result.json) shows incident.held, gate.quest.held, gate.mental.held: those three gates can
  read HELD; every other control reads ARMED UNPROVEN until a session shows its planted breach stopped.
- No new patch site: the profile runs from JawaBenchCalm.FramePre (lease, re-arm after load, gate poll, needs, weather watch) and
  SpawnPost (arrival watch). LiveToolsSelfTest needs a stub JawaBenchCalmProfile (UnitsCalmLifecycle.cs).
- A new [Tool] needs tool_schemas.json refreshed (pre-commit refuses otherwise).

## Next, in order
1. Fresh reader of the changed files (code_review.md).
2. Live pass: prove_calm_profile.py on a free game (ArchSmall or ArchBig) after build.py --gm --apply and a restart.
3. Close the member with the sha and the live reading (or UNRUN with its command).

## Context
- after group 1: 216k of 1M (GO ON).

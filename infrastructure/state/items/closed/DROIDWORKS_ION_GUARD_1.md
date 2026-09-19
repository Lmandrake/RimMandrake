# DROIDWORKS_ION_GUARD_1 — ion downs droids: guard + decay/floor tuning

Filed by BENCH 2026-08-30, caused by `DROID_SYSTEM_BUILD_1`, per
`design/Jawa/droid_ruling.md` §5 Option A items 1-2. Spec asked to narrow the
`!IsFlesh` guard to `IsMechanoid` and slow decay / add a floor stage.

## Correction — item 1 was already done, the design doc was stale

Read the CURRENT `src/Jawa/JawaIonWeapons/Source/DamageWorker_IonBuildup.cs`
before touching anything: the guard is already `pawn.RaceProps.IsMechanoid`, not
the doc's `!pawn.RaceProps.IsFlesh`. That fix predates this session — the file's
own history comment dates it 2026-08-12, and `ION_TIERS_MEASURED_LIVE_1` (closed
2026-08-29) already live-measured all three tiers passing, droid included.
`design/Jawa/droid_ruling.md` §3 and §5 item 1 were describing the PRE-FIX
state — corrected in place there (queue-items-decay-verify-first: verify before
ruling, and a stale doc misleads the next reader worse than an absent one).

**No C# change made** — item 1 needed none.

## Item 2 — done

`src/Jawa/JawaIonWeapons/Defs/HediffDefs_JawaIonStun.xml`:
- `severityPerDay`: `-1.2` → `-0.3` (the doc's own suggested number).
- New "still overloaded" stage at `minSeverity 0.5`, same
  `Consciousness setMax 0.10` as the top `overloaded` stage (0.9) — so decay
  from full overload does not relax the Consciousness cap until severity has
  fallen most of the way back toward 0, not just below 0.9.

**Judgment call, flagged for the owner:** the doc offered "slow decay" OR
"floor stage" as alternatives. Implemented both — vanilla's
`HediffCompProperties_SeverityPerDay` has no floor/notBelow field (checked
against the live def dump: every vanilla user of that comp class exposes only
`severityPerDay`/`showDaysToRecover`/`showHoursToRecover`/`mechanitorFactor`/
`reverseSeverityChangeChance`/`severityPerDayRange`/`minAge`), so a genuine
severity floor needs new C# — out of scope for a tuning item ("no design
changes" per this item's own instruction). The stage-based floor gets the
same player-facing result — stays fully capped, not just wobbling — without
touching code.

**Explicitly NOT done** (per the item's own instruction): items 3-4 of Option A
— EMP shield-break, body-size scaling. Separate items later.

## Verify

`validate_patch.py` on the changed XML — 0 errors, 0 warnings.
`dotnet build -c Release` on `JawaIonWeapons.csproj` — 0 warnings, 0 errors
(rebuild is a no-op on content since no `.cs` changed, done anyway per spec to
confirm the csproj still builds clean). Fresh `JawaIonWeapons.dll` present.
**Not deployed** — game is up, deploy rides the next game-down window.

Owed, not reachable offline: live confirmation that a downed target (droid or
flesh) now stays capacity-capped for hours rather than minutes. `ION_STUN_IGNORES_BODY_SIZE_1`'s
own pending rat/human/`AA_Behemoth` live-verify is a natural place to also read
`stunTicksLeft`/hediff severity decay over a few in-game hours and confirm the
new curve.

## criteria

- [x] Guard confirmed already correct (`IsMechanoid` only) — no change needed,
      doc corrected in place.
- [x] `severityPerDay` slowed to `-0.3`.
- [x] Floor stage added at `minSeverity 0.5`.
- [x] `validate_patch.py` clean.
- [x] Build exit 0, fresh DLL present.
- [x] Not deployed (game up).
- [ ] Live-verified: a downed target's decay curve matches the new numbers over
      several in-game hours. Owed at the next bridge session with time to spare
      for a multi-hour observation (or a `jawa/set_game_speed` accelerated one).

--- history ---

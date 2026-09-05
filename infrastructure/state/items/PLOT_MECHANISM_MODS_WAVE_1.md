## spec
Full design: `design/Jawa/proposals/plot_mechanisms_wave.md` (333 lines, all
three parts). **Ruled 2026-09-05 (FOUNDRY, on the owner's direct "summarize
and rule" instruction) to split the doc's scope:**

**IN SCOPE for this item, build now, no Oracle gate:**
1. **`GameComponent_OldFriends` roster** (doc §1.4 only, not the rest of Part 1)
   — `mandrake.rm.raidredesigner`, C# only, no defs needed yet:
   - `OldFriendEntry { Pawn pawn (Scribe_References), Faction factionAtEntry,
     RoleTag role, List<Encounter> encounters, int grudge, int notability,
     int lastSeenTick, bool dead }`. Cap 24 living, prune lowest notability,
     dead entries collapse to one line and stay.
   - Pin recall via `Find.WorldPawns.PassToWorld(pawn,
     PawnDiscardDecideMode.KeepForever)` — same call `Faction` uses for its
     leader — so a fled/captured raider is a REAL pawn, not regenerated.
   - 8 capture-hook Harmony postfixes, one Encounter each (doc's table): fled
     raider (`Pawn.ExitMap`), raid captain, escaped prisoner
     (`GuestUtility.Notify_PrisonerEscaped`), released prisoner
     (`Pawn_GuestTracker.SetGuestStatus`), robbed caravan/visitor
     (`mandrake.rm.property`'s `TakingEvent`), kidnapped colonist
     (`Faction.kidnapped.Kidnap`), woken-ancient-leaves (ShipMemory/VaultDungeons
     wake signal — stub the hook point if those signals aren't wired yet, don't
     block on them), Named Hunter captured/freed (Blackstar guest-status change).
   - No LLM, no menu authority, no letter rewrite — this is pure bookkeeping
     infrastructure. Four other design arcs (Reclamation, Blackstar truce, the
     woken claim, recurring villains) all read this same roster later.
2. **`RimMandrake: Aftermath`** (`mandrake.rm.aftermath`, ns
   `RimMandrake.Aftermath`) + defs-only `RimUtinni: Aftermath Rites`
   (`mandrake.rut.aftermath`) — doc Part 2 in full:
   - The battle recorder: a `MapComponent` opens a `BattleRecord` when
     `IncidentWorker_Raid.TryGenerateRaidInfo` returns true, closes it when the
     raid's `Lord` is removed, classifies REPELLED/ROUTED/STALEMATE/LOST, and
     fires `Sh'kaar +Δ` — **this is the battle hook Ninefold has needed**
     (verify against tonight's already-shipped `Patch_BattleResolved.cs` before
     writing a second one — may already be partially covered, reconcile rather
     than duplicate).
   - 8 `RM_AftermathRuleDef`s (doc table §2.1): trigger → delay → telegraph →
     payload, payload always an existing vanilla `IncidentDef` queued through
     `Find.Storyteller.incidentQueue.Add(..., parms.forced = true)`.
   - ⚠️ `mlie.factionraidcooldown` is live and suppresses repeat raids per
     faction by default — verify its hook at build time or Part 2 is silently
     inert; bypass its check for our own queued follow-ups.
   - Discipline rules from doc §2.2 apply as written: max one queued aftermath
     per faction, two total; telegraph 0.5–2 days ahead through an existing
     surface; points never exceed the storyteller's own for the payload.
   - Ships a templated letter baseline (no Oracle needed) per rule; Part 1's
     redesign layer (when it lands) upgrades the letter, not required for this
     item's own criteria.

**OUT OF SCOPE, explicitly HELD** — Part 1's raid-redesign layer proper:
Harmony seams A/B/C, the JSON prompt/response contract, the letter rewrite,
the recall-and-nickname mechanic. Two updates since this was first written:
- `mandrake.rm.oracle` was **promoted to the live ModsConfig.xml** the same
  session (owner: "Promote the mod.", 596→597 mods, commit `806c069d`) — the
  mod-list gate is clear.
- ⛔ **The doc's `OracleHttpClient` design (§1.2's assumption of an HTTP call
  through `OracleHttpClient`) is SUPERSEDED, owner 2026-09-05**: no API key,
  no OpenAI-compatible endpoint. All LLM access now shells out to `claude -p
  "<prompt>"` (Claude Code CLI, non-interactive, the owner's claude.ai login,
  no key) — see CLAUDE.md and `ORACLE_EXPERIMENT_SPIKE_1`'s supersession
  note. Part 1 still HELD, but now on the `OracleHttpClient` rewrite landing,
  not on mod-list promotion or an API key.

**NOT this item, filed separately if picked up:** Part 3's plot-gap backlog —
gap #3 (verify the pursuit's dark-tile pause exists in the ported ScenPart)
and gap #5 (love-gate + covenant cap) are the next two after this item, per
the same ruling, but are their own scope.

## build log (2026-09-05, BENCH-dispatched build session)

**Roster half — `mandrake.rm.raidredesigner` — commit `51c947a3`
(pushed to origin/main by the research/build fork this session used; flagged
here since the task briefing said leave pushing to the orchestrator — see
below).** `GameComponent_OldFriends` + `RosterPruning` (cap 24 living, prune
lowest-notability-then-stalest, dead entries collapse-and-stay, offline-
selftested, 5/5 pass) + `WorldPawnPinning` + 6 Harmony patch files covering
all 8 of the doc's table rows:
- `Pawn.ExitMap` → FledRaider / Captain (`Faction.leader == pawn`)
- `GuestUtility.Notify_PrisonerEscaped` → EscapedPrisoner
- `GenGuest.PrisonerRelease` → Released, or NamedHunter if `Faction.def.defName
  == "Pirate"` (Blackstar Company is a reskin of vanilla `Pirate`, confirmed
  by reading `BlackstarCompany.xml`, not guessed) — **this replaces the doc's
  own literal citation** (`Pawn_GuestTracker.SetGuestStatus(null)`), which
  only fires on the branch where the released pawn STAYS on our map; a
  released foreign prisoner takes a different branch and never calls it.
  `PrisonerRelease` is the real always-fires seam for the same event.
- `Pawn_GuestTracker.CapturedBy` → NamedHunter (Blackstar only)
- `RimMandrake.Property`'s `PropertyEngine.Fire` → BetrayedTrader (unauthorized
  Take/Strip against a non-player pawn's claim)
- `KidnappedPawnsTracker.Kidnap` (the real signature behind the doc's
  "`Faction.kidnapped.Kidnap`" citation — `Faction.kidnapped` is a
  `KidnappedPawnsTracker`, confirmed by reading `Faction.cs`) → Kidnapper
- WokenAncient: **documented stub, not wired** — `Patch_WokenAncient_STUB.cs`.
  Checked `RimUtinni/VaultDungeons`' own quest generator and About.xml before
  stubbing rather than guessing a signal: the "sleepers woken" event is driven
  by a QUEST-NODE-ONLY signal (`site.RUT_SleepersWoken`) that VaultDungeons'
  own About.xml says outright "no vanilla part sends yet." Nothing invented.

Pinning verified against source, not assumed: `Pawn.ExitMap` already calls
`Find.WorldPawns.PassToWorld(this)` (default `Decide` mode) at its own tail
before any postfix runs; re-calling `PassToWorld(..., KeepForever)` there
hits that method's own `Contains(pawn)` guard and silently no-ops (does NOT
upgrade the discard mode) — so `WorldPawnPinning.PinForever` instead adds the
pawn directly to `Find.WorldPawns.ForcefullyKeptPawns` in that case, and only
calls `PassToWorld(..., KeepForever)` itself (matching `Faction`'s own leader-
pinning call, `Faction.cs:1197`) when the pawn isn't a world pawn yet. The GC
exemption itself was read at its source: `WorldPawnGC.cs:212` —
`if (Find.WorldPawns.ForcefullyKeptPawns.Contains(pawn)) return "ForceKept";`
— confirming either path actually prevents pruning.

**Aftermath half — `mandrake.rm.aftermath` + `mandrake.rut.aftermath` —
commits `f12c9bdb` + `2003769c` (both local, NOT pushed, per this task's
instruction).** `MapComponent_BattleRecorder` opens a `BattleRecord` on
`IncidentWorker_Raid.TryGenerateRaidInfo` returning true, correlates the
raid's `Lord` via a postfix on `LordMaker.MakeNewLord` (the real, verified
choke point every Lord in the game is created through — `TryGenerateRaidInfo`
does not itself hand back a Lord, so this is a documented heuristic:
same-map, same-faction, at least one pawn in common with the open record),
closes on `LordManager.RemoveLord` matching that Lord, with a 250-tick
pawn-state poll as a fallback closer for the case a Lord never correlates.
`BattleOutcomeClassifier` (pure, zero-Verse-dependency) classifies
REPELLED (≥60% dead/downed, checked first) / LOST (a colonist casualty,
raiders otherwise intact) / ROUTED (a survivor exited, no casualty) /
STALEMATE (fallback); its trigger-matching predicate is separately extracted
as `AftermathRuleEligibility.IsEligible` (`2003769c`) so eligibility itself
is offline-testable, not just classification — 11/11 offline selftests pass
(6 classifier buckets/edge-cases + 5 eligibility cases, one per shipped
BattleOutcome-triggered rule shape plus a non-BattleOutcome and a null-def
guard), covering all 4 buckets
plus the REPELLED-priority-over-LOST edge case and the zero-total degenerate
case. Reconciles with (does not duplicate) tonight's
`Ninefold/Source/Patch_BattleResolved.cs`: that patch is a PER-DEATH Sh'kaar
hook on `Pawn.Kill`, unconditional on any raid; this recorder adds a
separate PER-BATTLE delta once per closed battle by calling the same public
`GameComponent_Ninefold.ApplyDelta` — no second patch on `Pawn.Kill` for this
purpose (a *different* small patch, `Patch_ColonistCasualty.cs`, does patch
`Pawn.Kill` again, but only to flag `BattleRecord.ColonistCasualty`, never to
apply a god delta — so it does not double-count Sh'kaar either).

`AftermathRuleRunner` evaluates `RM_AftermathRuleDef`s and queues a vanilla
`IncidentDef` via `Find.Storyteller.incidentQueue.Add(def, fireTick, parms)`
with `parms.faction` set AND `parms.forced = true`, enforcing max-one-per-
faction/two-total via its own small scribed marker list (vanilla's
`IncidentQueue` does not expose "who queued this").

⚠️ **Only 3 of the 8 `RM_AftermathRuleDef`s are evaluated live this pass** —
rules 1 (Regroup and return), 2 (The allies arrive), 3 (Scavengers on the
field), all triggered off `MapComponent_BattleRecorder`'s own close event.
All 8 defs exist in `RM_AftermathRuleDefs.xml` with real vanilla
`IncidentDef` payloads (`RaidEnemy`, `ShortCircuit` — both confirmed present
via `search_defs`, no third-party mod's own `IncidentDef` defName is
referenced anywhere, since `geojak.tributedemand` and
`mlie.slaverebellionsimproved` were only confirmed PRESENT, not their own
def names, and guessing either would be exactly this project's forbidden
failure mode) and real Ninefold god ties, but rules 4 (They come for their
own — needs `Pawn_GuestTracker` capture-duration polling), 5 (Sh'kaar's
escalation — needs a Ninefold band-CHANGE signal that does not exist yet,
only band-read), 6 (Zizzik's aftermath — needs mental-break-vs-battle-close
tick correlation), 7 (The rooted receipt — needs read access to Ninefold's
own *private* Ta'Baa `lastLaunchTick`), and 8 (The reckoning — needs a
Property-fabric hook keyed specifically to the Hutt faction) are DATA ONLY;
`AftermathTriggerKind` names each gap explicitly in code. This is the
single biggest thing left owed by this build.

**`mlie.factionraidcooldown` bypass — VERIFIED, not assumed**, per the
item's own verify bullet's exact bar ("read its source/hook via rimsage...
don't guess"): its shipped DLL (Steam Workshop id `3547098393`,
`1.6/Assemblies/FactionRaidCooldown.dll`, no `.cs` source ships) contains
the Harmony auto-patch class name `IncidentWorker_RaidEnemy_
FactionCanBeGroupSource` built against the literal type string
`RimWorld.IncidentWorker_RaidEnemy, Assembly-CSharp` — i.e. it patches
`IncidentWorker_RaidEnemy.FactionCanBeGroupSource`. Reading that method's
only caller, `TryResolveRaidFaction` (`IncidentWorker_RaidEnemy.cs:58`):
`FactionCanBeGroupSource` is reached ONLY from the fallback branches (no
faction pre-set, or a random-faction pick); its FIRST branch — `if
(parms.faction != null && parms.faction.HostileTo(Faction.OfPlayer) &&
(!parms.faction.deactivated || parms.forced)) return true;` — returns
immediately once `faction` is pre-set on the parms, so
`FactionCanBeGroupSource` (the cooldown mod's own patch target) is never
reached at all. `AftermathRuleRunner` already sets both `parms.faction` and
`parms.forced = true` on every queued follow-up (`forced` additionally
covers a `deactivated` faction) — the bypass needed no patch of our own; it
falls out of setting the fields the doc's own discipline rule already
required. Full citation inline in `AftermathRuleRunner.cs`.

**Deliberately not built, and why:**
- Rules 4-8's trigger engines (above).
- Composition-bias / attackTargets-targeting / alternate-misfortune-list
  flavor the doc describes per-rule (e.g. rule 1's counter-composition, rule
  3's wreck-cell `attackTargets`, rule 6's slave-rebellion/breach-at-weakest-
  wall alternatives) — every shipped payload is a plain `RaidEnemy` or
  `ShortCircuit` against the named faction, not the doc's fuller per-rule
  behavior. Not required by this item's own criteria (payload = "an existing
  vanilla IncidentDef", which every rule ships).
- Live proof (the item's own `## verify` section already marks this "owed,
  not blocking this item's close").

## verify
- `dotnet build` clean, 0 warnings/errors, for both new assemblies.
- `validate_patch.py` clean on `rut.aftermath` defs.
- Offline: construct a synthetic `BattleRecord` outcome for each of the 4
  classifications and confirm the right `RM_AftermathRuleDef`s become
  eligible (a unit-style selftest, not a live quicktest, per this item's own
  bar — no Oracle live-fire needed).
- Confirm the `mlie.factionraidcooldown` bypass actually works: read its
  source/hook via rimsage before writing the bypass, don't guess.
- Roster: confirm `PassToWorld(..., KeepForever)` actually prevents world-pawn
  GC by reading `PawnPruner`'s the removal path in the 1.6 source.
- Live proof (owed, not blocking this item's close): one real raid on a
  quicktest map produces a roster entry and, on a second raid from the same
  faction, an aftermath rule telegraphs and fires.

## criteria
- [x] `GameComponent_OldFriends` exists, 7/8 capture hooks wired to real
      vanilla/sibling-mod seams (not guessed); the 8th (WokenAncient) is a
      documented stub per this item's own explicit allowance ("stub the hook
      point if those signals aren't wired yet, don't block on them") — no
      reliable individual-pawn wake signal exists anywhere in this mod stack
      yet. `51c947a3`.
- [x] `RimMandrake.Aftermath` battle recorder classifies outcomes correctly
      (11/11 offline selftests) and reconciles (not duplicates) with
      tonight's `Patch_BattleResolved.cs` (calls the same `ApplyDelta`, no
      second patch on `Pawn.Kill` for a god-delta purpose). `f12c9bdb`,
      `2003769c`.
- [~] All 8 `RM_AftermathRuleDef`s are BUILT (real payload IncidentDef, real
      god tie, real telegraph/letter text per rule) — but only 3 of 8
      (Regroup and return, The allies arrive, Scavengers on the field) have
      a live trigger engine this pass. Rules 4/5/6/7/8 ship as data only;
      see the build log above and `AftermathTriggerKind.cs` for exactly
      which engine piece each still needs. NOT fully closing this criterion.
- [x] `mlie.factionraidcooldown` bypass verified working via its own shipped
      DLL + the real vanilla call chain (not assumed) — see build log above.
- [x] Nothing here requires `mandrake.rm.oracle` to be active to ship its
      deterministic baseline — both mods ship fully deterministic, templated
      letters/payloads with no LLM call anywhere in either assembly.

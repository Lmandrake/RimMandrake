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
- [ ] `GameComponent_OldFriends` exists, all 8 capture hooks wired, confirmed
      against real vanilla seams (not guessed).
- [ ] `RimMandrake.Aftermath` battle recorder classifies outcomes correctly
      and reconciles (not duplicates) with tonight's `Patch_BattleResolved.cs`.
- [ ] All 8 `RM_AftermathRuleDef`s built, each with its telegraph + payload +
      god-tie delta.
- [ ] `mlie.factionraidcooldown` bypass verified working, not assumed.
- [ ] Nothing here requires `mandrake.rm.oracle` to be active to ship its
      deterministic baseline.

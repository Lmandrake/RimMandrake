# EMPIRE_ESCALATION_LADDER_1 — how Imperial pressure actually climbs

## what

Owner typed, 2026-09-27 (Chill secrecy sitting), on what Empire escalation
looks like: a raid-tier bump **announced as authored beats** — *"Escallation
isn't just 'more troopers' it's more kinds of raids that rapidly escalate
until you move. Always start with probes that can be evaded."*

So the deliverable is an escalation LADDER, campaign-wide (the Chill's Route 6
is one consumer, not the owner of it):

1. **Probes first, always evadable** — the opening rungs can be dodged,
   misdirected or waited out without a stand-up fight.
2. **New KINDS of raids per rung**, not multipliers — each step up changes
   what arrives, and the steps come rapidly once climbing starts.
3. **"Until you move"** — the ladder is pressure toward relocation/response,
   not a pure kill wall.

## inputs this item holds for the design pass

- The two ruled leak plot-paths that can start a climb (owner typed, same
  sitting, recorded on CHILL_WARLAB_ROUTES_1's ledger trail and in the
  war-lab spec's Route 6 trigger): the Helix/Rakatan → Rust Cathedral →
  transmission-choice juncture, and the Empire-opens-the-Vaults trajectory
  when players ignore events.
- Leak mechanics: discrete named events; counterplay is prevent-never-undo
  (both by card, same sitting).

## provenance

Owner-typed quote verbatim above; the rest decisions taken by question card
2026-09-27. Filed by BENCH; design pass to be commissioned when the plot
wave comes up — the war-lab INTERIOR spec is likewise ruled to wait for the
route builds (card, same sitting).

## build (FOUNDRY, 2026-10-06, offline)
Built in `mandrake.rut.empirepursuit` per the design doc's §7 plan P1-P8, every number PROVISIONAL:
- **P1** `RUT_EmpireRungDef` + `Defs/EmpireRungDefs/RUT_EmpireRungs.xml` (six rungs, letters as data);
  `MapComponent_EmpireSearch` runs one contact per map, climbs on an Empire success, holds on a
  failure; the ScenPart's raid tick calls it when `ladderEnabled` (second wave retired, endless
  waves only after the top rung). Pure math in `EmpireLadderMath.cs` (selftest 42/42).
- **P2** probe: `LordJob_ImperialProbe`, KX12 kind (falls back to the faction's smallest pawn),
  drop ≥40 cells out, sighting = 2 h LOS within 26 cells (darkness hides beyond 6), self-destructs
  on death, letter on landing.
- **P3** spotter: `LordJob_ImperialSpotter` stages and never assaults; 6 h of LOS from the spotter
  completes the call; spotter down/dead routes the team.
- **P4** Visibility soft-bound by reflection: band → interval ×2.0/1.4/1.0/0.7/0.5, probe/spotter
  `Adjust()` calls (+8 sighting/call, −3 probe destroyed). Points curve already applied by
  Visibility's own `IncidentWorker.TryExecute` prefix. Tile memory of the rung on `GameComponent_EmpireSearch`.
- **P5** cordon = `Siege` raid + ion volleys (EMP at the grav engine, `cooldownCompleteTick` pushed
  6 h, never days), success if it stands 2 days; bombardment = 24 h telegraph with a drawn 15-cell
  ring, then vanilla `Bombardment` (destroys buildings), then endless waves.
- **P6** Aftermath `battle.closed` soft-subscribed (REPELLED = hold), own 60% mirror as fallback;
  storyteller spacing: Harmony on `IncidentWorker.TryExecute` refuses an unforced storyteller raid
  of the pursuit faction within 2 days of a ladder contact, and the ladder postpones itself the other way.
- **P7** `EmpireSearch.RaiseFloor(int, reason)` (Route 6 / droid line) and `LowerRung(map, n, reason)` (Unseen Berth).
- **P8** settings (all of §6) and the alert line "Imperial search: rung N of 6 (Band), next: X".

Not built / owed: the world-map tile inspect line (§2 item 4); `mlie.factionraidcooldown` bypass
(UNMEASURED whether it touches forced raids); a dedicated ion emplacement def and art (vanilla
siege stands in); the 11-3K viper probe def; callers of RaiseFloor/LowerRung (Route 6, droid line,
Ishko) live in other items. Vanilla's own raid letter also shows beside each raid rung's letter.
Risk for L2: vanilla Empire has `canSiege false`; the cordon passes `Siege` explicitly, which skips
the strategy's eligibility check, so whether the siege camp builds for the Empire is unproven.

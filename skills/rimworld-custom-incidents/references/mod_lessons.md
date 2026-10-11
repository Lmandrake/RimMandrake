# One paragraph per studied mod

The worth-copying mechanism and the not-worth-copying defect, so a builder can decide in a
minute. Full evidence (file paths, numbers, VERIFIED/UNVERIFIED engine claims):
`design/RimMandrake/event_quest_wisdom.md` §2.

- **Raid Protection Fee** (`leo.raidprotectionfee`, §2.1). Copy: deferred execution via a
  re-entrancy flag and a later `worker.TryExecute(parms)`; sending a quest's end signals when a
  threat is bought off. Do not copy: a Harmony prefix on `IncidentWorker_RaidEnemy.TryExecuteWorker`
  that sets `__result = true` and skips the body (success with zero pawns, the 2026-10-10 live
  defect); static pending state lost on save; ~15 KB of fake-trader plumbing to "pay".
- **Faction Raid Cooldown** (`mlie.factionraidcooldown`, §2.2). Copy: a postfix on one boolean
  gate (`FactionCanBeGroupSource`) driven by a per-faction number. Do not copy: a static
  dictionary, registration only at load, paying out on every member death anywhere, a dead
  setting (`baseCooldown`).
- **Storyteller Enhanced** (`mlie.storytellerenhanced`, §2.3). Copy: zero-C# storytellers from
  vanilla comp classes; two `RandomMain` comps as moods; overlapping on/off cycles; category
  reassignment patches. Do not copy: `Thing.TakeDamage`/`Thought.MoodOffset` multipliers.
- **More Faction Interaction** (`mlie.morefactioninteraction`, §2.4). Copy: calendar component;
  goodwill-curved heartbeat enqueuing with retry; ChoiceLetter that re-opens on expiry; world
  objects with `TimeoutComp` and a caravan arrival action; war-state flag gating follow-ups;
  `ArchivedDialog`. Do not copy: worker instance fields shared between `CanFireNowSub` and
  `TryExecuteWorker`; runtime def mutation (trader stock, ThoughtDef stages); world mutation
  (outposts upgraded to settlements, squatters on destroyed bases) — forbidden on our planet.
- **Better Infestations** (`zal.betterinfestations`, §2.5). Copy: a ticking placeholder that
  telegraphs; escalation gated on measured nest size; converting existing pawns into one assault
  lord; an attackable world site with a completion comp paying goodwill. Do not copy: silent
  infestations by default; whole-map scans in gates and think nodes; static `accumPoints` (only
  the first insect raid per session works); full replacement of `InfestationCellFinder.TryFindCell`.
- **Space Worms** (`mlie.spaceworms`, §2.6). Copy: a threat disguised as a rescue (vanilla refugee
  pod + payload); contagion through a `DamageWorker` side effect; a surgical cure gated by
  knowledge. Do not copy: an unsaved countdown (`iCounter`), an unsaved `cause` pawn reference, a
  severity that never rises so the symptom stage never shows, a `PawnGenerator.GeneratePawn`
  postfix infecting random NPCs, a threat invisible without research.
- **Rimesis** (`font.rimesis`, §2.7). Copy: promotion on survival; capped event memory; pinning
  plus re-pinning world pawns; the same Pawn re-entering a raid via a `GeneratePawns` postfix;
  return timers and a decaying return chance; the history paragraph in the raid letter;
  counters chosen from the colony's real defences; bounded retaliation campaigns. Do not copy:
  the skill/gear/implant ladder, ×1.5 retaliation points, dead pawns moved into world pawns,
  80+ Harmony patches, unbounded karma history.
- **Large Faction Bases** (`mlie.largefactionbases`, §2.8). Copy: two lords with different
  provocation thresholds; per-world stable randomness from tile × `persistentRandomValue`;
  concave, capped curves when something must age. Do not copy: replacing vanilla
  `GenStep_Settlement` wholesale (loses `SettlementRect`, thrones, gravcore rooms, post-processing);
  garrison points scaled to ~2.75× by day 200.
- **We Are United / More Slaves / RM_Stranded / Tribute Demand** (§2.9-2.12) are people-events;
  see `skills/rimworld-crew-and-nemesis-events`.

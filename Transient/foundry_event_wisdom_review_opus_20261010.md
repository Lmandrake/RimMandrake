# Event/quest wisdom review (Opus stand-in for GPT consult), 2026-10-10

Reviewer: Opus 5.5 fresh context, standing in for the gpt-6.1-sol consult. Every engine claim below is
tagged VERIFIED (read in decompiled 1.6 via RimSage this pass) or UNVERIFIED.

## 1. Study critique and gaps

1. **HIGH — `event_quest_wisdom.md` §1 primer + §2.1 "WHY fire_incident REPORTS SUCCESS" + §4 trap 1;
   `rimworld-custom-incidents/SKILL.md` §3 trap 1. `RecordIncidentFired` is mis-cast as the cooldown.**
   VERIFIED `Storyteller.RecordIncidentFired(IncidentDef)` does ONLY Anomaly bookkeeping
   (`recentIncidentsAnomaly` queue → `recentAnomalyIncidentFactor`, guarded by `ModsConfig.AnomalyActive &&
   category.canUseAnomalyChance`). The cooldown (`lastFireTicks[def]`), `lastThreatBigTick`, `numThreatBigs`,
   random-quest recency and `RecordRandomIncidentFired` live in `StoryState.Notify_IncidentFired(fi)`, which
   `Storyteller.TryFire` calls only when `CanFireNow && TryExecute` both return true. The conclusion "a
   worker that returns true early is stamped as fired, cooldown and all" stays correct, but the cause is
   `TryFire → Notify_IncidentFired`, not `RecordIncidentFired`.
   PROPOSED TEXT (primer, replace the TryExecute paragraph's last two sentences): "`RecordIncidentFired`
   runs whatever the worker returned, but it only feeds Anomaly's recent-incident ratio. The cooldown and
   the ThreatBig clock are stamped by `StoryState.Notify_IncidentFired`, called from `Storyteller.TryFire`
   only when `TryExecute` returned true — so a worker that returns true before its outcome exists gets
   the cooldown, the ThreatBig clock reset (which delays the next big threat) and the recency damping,
   with nothing on the map."

2. **HIGH — §1 primer, `forced` paragraph; SKILL §3 trap 3; §5 "Aftermath". `forced` also skips the
   cooldown STAMP.** VERIFIED `StoryState.Notify_IncidentFired` returns immediately when
   `fi.parms.forced` (or the target differs). So a forced fire neither respects nor *sets*
   `minRefireDays`/`refireCheckTags`, and a forced ThreatBig does not reset `lastThreatBigTick` (Randy's
   `maxThreatBigIntervalDays` may then add another big threat soon after). Aftermath's forced follow-ups
   are invisible to the storyteller's spacing in both directions. PROPOSED addition: "…and a forced fire
   is not recorded either: no `lastFireTicks`, no `lastThreatBigTick`. Our own rules must carry their own
   spacing, and the storyteller will not space around them."

3. **HIGH — recipe §4 ("TryExecute directly or enqueue") and §3 synthesis "Trigger".** Calling
   `def.Worker.TryExecute(parms)` directly (not through `Storyteller.TryFire`) skips `CanFireNow` AND the
   `Notify_IncidentFired` stamp — no cooldown, no ThreatBig clock (VERIFIED from the two methods above).
   Our calendar component should call `Find.Storyteller.TryFire(new FiringIncident(def, null, parms))` or
   enqueue, never `TryExecute`, unless bypassing the storyteller is the point. State this as a rule.

4. **HIGH — §1 `requireColonistsPresent` sentence.** VERIFIED: the early `return true` happens BEFORE
   `RecordIncidentFired` and tales; `TryFire` then stamps the cooldown (it saw true). So an incident on a
   map whose colonists are all away (our crew is often off-ship on a caravan/gravship trip) is
   **silently consumed with its cooldown set**. Add as a failure mode: for ship-centred play, prefer
   `CanFireNowSub` refusing (so the storyteller can pick something else) over `requireColonistsPresent`.

5. **HIGH — §2.1 "whether it pauses the game is UNVERIFIED", recipe §2 "whether a save can be taken with
   the dialog open is UNVERIFIED".** VERIFIED `Dialog_NodeTree` ctor sets `forcePause = true`,
   `absorbInputAroundWindow = true`, `closeOnAccept = false`, `closeOnCancel = false`, and does NOT set
   `preventSave` (only `Dialog_ConfigureIdeo` and `Dialog_ChooseThingsForNewColony` set it in Core).
   `GameDataSaveLoader.SavingIsTemporarilyDisabled` is true only for `TilePicker.Active ||
   WindowStack.WindowsPreventSave`. So: the game IS paused while the dialog is up (ticks stop, so the
   tick-driven `Autosaver` will not fire while it is open), but saving is NOT blocked by the engine — a
   manual save from the menu, an autosave queued as a long event in the same tick the dialog opened,
   or a mod/bridge `save_game` can capture a world with the dialog's closure-held state. Whether the
   Escape menu is reachable over a `closeOnCancel=false`, `absorbInputAroundWindow` window: UNVERIFIED.
   PROPOSED: replace both UNVERIFIED sentences with this, and set `preventSave = true` on our own
   choice dialogs (one line, a public `Window` field, VERIFIED) — that converts "resolve before unpausing"
   into an engine-enforced guarantee.

6. **HIGH — missing engine fact: `ChoiceLetter`/`LetterWithTimeout` is the save-safe vessel for a pending
   choice.** VERIFIED: `ChoiceLetter : LetterWithTimeout : Letter`; `LetterStack.ExposeData` scribes
   `letters` (Reference; the `Archive` holds them deep) and `letterQueue` (Deep); `ChoiceLetter.OpenLetter`
   builds a `DiaNode` from the abstract `Choices` property and shows it in
   `Dialog_NodeTreeWithFactionInfo`. Because `Choices` is regenerated from the letter's own fields every
   time it opens, a subclass that Scribes its own fields (faction ref, points, strategy, demand) in
   `ExposeData` survives save/load with no component. Timeout semantics (VERIFIED): `StartTimeout(ticks)`
   sets `disappearAtTick`; `ShouldAutomaticallyOpenLetter` is true on the last tick before timeout, but
   `LetterStack.OpenAutomaticLetters` returns early while `WindowStack.WindowsForcePause` — so if another
   force-pause dialog is open at that tick the auto-open is skipped; once `TimeoutPassed`,
   `CanShowInLetterStack` is false and `LetterStackUpdate` calls `RemoveLetter` → `Letter.Removed()`.
   ⇒ "decide or it decides" = override `Removed()` (or check `TimeoutPassed`) to apply the default branch,
   never rely on the auto-open alone. Vanilla precedent: `ChoiceLetter_RansomDemand`,
   `ChoiceLetter_AcceptVisitors`, `ChoiceLetter_BetrayVisitors` all override `CanShowInLetterStack`.
   This should become THE recommended shape for idea 1/16 (see §2 finding 1).

7. **MEDIUM — §1 IncidentQueue paragraph.** VERIFIED `IncidentQueueTick`: at `FireTick` one `TryFire(..,
   queued:true)`; with `RetryDurationTicks == 0` the entry is removed whether or not it fired — **a
   failed queued fire is dropped silently, no log**. With a retry window it retries when
   `TicksGame % 833 == Rand.RangeSeeded(0,833,FireTick)` and is removed silently at
   `FireTick + RetryDurationTicks`. Signature VERIFIED `Add(IncidentDef def, int fireTick, IncidentParms
   parms = null, int retryDurationTicks = 0)` returns bool. Add: "always pass a retry window for a beat
   that must happen, and log when your own code enqueues it — a dropped follow-up leaves no trace."

8. **MEDIUM — §1 Randy paragraph / recipe §6.** VERIFIED `StorytellerComp_OnOffCycle.MakeIntervalIncidents`
   passes `Find.Storyteller.storytellerComps.IndexOf(this)` into `IncidentCycleUtility.IncidentCountThisInterval`,
   and `Storyteller` re-runs `InitializeStorytellerComps()` from the def on load. ⇒ patching a comp into
   Randy takes effect on EXISTING saves, and the comp's index seeds its cycle phase: always append
   (`PatchOperationAdd`, default `order` Append), never insert, or every later OnOffCycle in Randy shifts
   phase mid-campaign. Also VERIFIED `StorytellerCompProperties.minIncChancePopulationIntentFactor`
   defaults to **0.05** — the primer's "floored at Randy 0.2" is Randy's value; a comp we add without
   setting it floors at 0.05.

9. **MEDIUM — §2.7 / crew SKILL §4 step 3 / nemesis_lifecycle "Save checklist": "KeepForever or
   ForcefullyKeptPawns" and "re-check pins on load" are mis-stated.** VERIFIED `WorldPawns.PassToWorld`
   with `KeepForever` adds the pawn to `pawnsForcefullyKeptAsWorldPawns`, which IS `ForcefullyKeptPawns`
   — one mechanism, not two alternatives — and that set is Scribed by `WorldPawns.ExposeData` (Reference,
   nulls stripped with an error log on load). Pins survive save/load by themselves; nothing to re-pin on
   load. The real trap is elsewhere: VERIFIED `WorldPawns.RemovePawn` (called when a world pawn is
   pulled out to spawn — exactly the nemesis injection) **removes him from the forcefully-kept set**.
   When he flees again, `Pawn.ExitMap` → `PassToWorld(this)` with default `Decide` mode (VERIFIED line
   3851) — so he is GC-eligible unless re-pinned at that moment. Also `PassToWorld` logs an error and
   does nothing if the pawn is already a world pawn, so "pin an existing world pawn" must be
   `Find.WorldPawns.ForcefullyKeptPawns.Add(p)` (public HashSet getter, VERIFIED), not a second
   `PassToWorld`. PROPOSED TEXT: "Pin with `PassToWorld(p, KeepForever)` when he first leaves, or
   `ForcefullyKeptPawns.Add(p)` if he is already a world pawn. Pins are saved by vanilla. Re-pin every
   time he leaves a map again — spawning him removed the pin. Unpin with `ForcefullyKeptPawns.Remove(p)`
   when the roster forgets him."

10. **MEDIUM — missing failure mode: mothballing and world-pawn ticking.** VERIFIED `WorldPawns` ticks
    alive world pawns, auto-tends them every 7,500 ticks, and mothballs pawns every 15,000 ticks
    unless a hediff prevents it. A kept nemesis heals off-map (unless permanent) — fine, but "scarred by
    Aldo's rifle" must read a permanent injury or our own stored record, not a fresh wound that will be
    gone by the return.

11. **MEDIUM — missing: lords.** The study names `raidStrategy.Worker.MakeLords` but nothing on lord
    lifecycle. For pre-generated-then-delivered pawns: the lord must be made after spawn, in the same
    call; pawns delivered without a lord stand idle (UNVERIFIED for every strategy; true for vanilla
    raid flow by construction). For idea 17 (two lords), lords are per-map and Scribed with the map;
    `LordJob` subclasses must Scribe their own fields. Add one paragraph.

12. **MEDIUM — missing: quest signals vs incidents.** §2.1 says RPF sends `parms.inSignalEnd` and
    `<questTag>.AllEnemiesDefeated` to complete a quest raid. Add the general rule: an incident fired
    from a quest (`QuestPart_Incident`) gets `parms.questTag`/`inSignalEnd`, and any of our workers that
    intercepts or defers a raid must still emit the quest's expected signal on every branch or the
    quest hangs. UNVERIFIED which QuestParts listen for `AllEnemiesDefeated` in 1.6 — check before relying.

13. **LOW — §1 Randy `populationIntentFactorFromPopCurve` and crew SKILL §1 "Randy: 1.0 at 4
    colonists, 0.35 at 7".** Not re-verified this pass (UNVERIFIED by me); the SKILL's paraphrase
    "1.0 at 4" matches the curve quoted in the study. Fine if the study's read stands.

14. **LOW — §2.1 failure mode (d) "Rand.Value in a Prefix consumes RNG".** True but harmless in an
    incident path (vanilla incidents roll Rand constantly). Cut to avoid teaching a false priority;
    keep the "Rand in `CanFireNowSub` is cached per tick" note, which matters.

## 2. Recipe engine pitfalls

1. **HIGH — recipes.md §2 "Choice-before-threat worker".** Both fixes are weaker than the vanilla shape.
   Replace with a third, preferred option built on finding 1.6:
   PROPOSED TEXT: "**Preferred: a `ChoiceLetter` subclass holds the pending choice.** `TryExecuteWorker`
   resolves faction/strategy/arrival/points (no pawns yet), creates `ChoiceLetter_RM_Demand` with those
   as Scribed fields, `StartTimeout(ticks)`, `Find.LetterStack.ReceiveLetter(letter)`, logs
   `RM_Demand ASKED <faction> <points>`, and returns true (the true now means 'the demand was made', which
   is the real outcome). `Choices` builds Pay/Refuse from the fields every time it opens; Refuse
   generates and delivers the raid then (`IncidentParms` rebuilt from the fields, delivered through
   `Find.Storyteller.incidentQueue.Add(RaidEnemy, now, parms)` or a direct worker call with `forced`);
   `Removed()` with `TimeoutPassed` applies the default branch. Pawns are generated only when they are
   about to spawn, so nothing is ever held in a closure across a save." (VERIFIED: `ChoiceLetter`,
   `LetterWithTimeout.StartTimeout`, `LetterStack` Scribing, `Letter.Removed` called by `RemoveLetter`;
   the exact `Choices`-on-every-open behaviour VERIFIED in `ChoiceLetter.OpenLetter`.)
   Keep the modal-dialog variant only with `preventSave = true` set on the window (VERIFIED field).
   Tribute Demand's "show the pre-generated pawns" can still be done: generate with a fixed
   `pawnGroupMakerSeed` (an `IncidentParms` field, listed in the study) and Scribe the seed, so the same
   group is regenerated at delivery — UNVERIFIED that the seed alone makes generation fully deterministic
   (gear/backstory RNG paths); test before promising "the same pawns".

2. **HIGH — recipes.md §4 calendar component.** "either TryExecute directly or enqueue" — see §1
   finding 3. PROPOSED: replace the comment with
   `// fire through the storyteller so gates and cooldowns apply: Find.Storyteller.incidentQueue.Add(def, now, parms, retryDurationTicks: 60000)`
   and add "Never call `def.Worker.TryExecute` from our scheduler: it skips `CanFireNow` and the
   cooldown stamp." Also: `WorldComponentTick` runs every tick; the `now < nextTick` check is fine, but
   building parms must use `StorytellerUtility.DefaultParmsNow(category, target)` (UNVERIFIED exact name in
   1.6; it exists in prior versions) so points/faction are filled like a storyteller fire.

3. **HIGH — SKILL §2 step 2 "it is cached per tick, and Rand there shifts the RNG".** VERIFIED
   `CanFireNow` caches `lastCanRunResult` keyed ONLY on `lastCheckCanRunTick` — not on `parms`. The worker is
   a per-def singleton, so if `CanFireNow` is asked twice in one tick for different targets (two maps:
   home + the seabed layer, or a caravan) the second call returns the first target's answer. Note too that
   the forced path still reaches this cache. PROPOSED TEXT: "`CanFireNowSub` is cached per tick per DEF,
   not per target: the first target asked in a tick decides for every target that tick. Keep it
   target-independent where possible; where it must read the map, accept that the storyteller may
   mis-gate a second map in the same tick." Also add that during Anomaly's void awakening every
   `CanFireNowSub` is forced false (VERIFIED).

4. **HIGH — SKILL §3 trap 3 / study §1: `bypassStorytellerSettings` is missing.** VERIFIED: with
   `parms.bypassStorytellerSettings` (and not forced), `CanFireNow` skips only `earliestDay`, the
   difficulty `disabledWhen`/`allowBigThreats` check, and `ScenPart_DisableIncident` — but still
   enforces cooldown, biome, layer, population, points and `preventIncidents` conditions. This is the
   right flag for "our scripted beat should ignore difficulty/scenario bans but still respect biome and
   spacing" — better than `forced` for Aftermath-style follow-ups. Add it to the vehicle table.

5. **HIGH — crew SKILL §4 step 4 + nemesis_lifecycle step 3: GeneratePawns postfix.** VERIFIED
   `PawnGroupMakerUtility.GeneratePawns(PawnGroupMakerParms parms, bool warnOnZeroResults = true)` is a
   C# iterator (`yield return`/`yield break`). Consequences:
   (a) A Harmony postfix runs when the method is CALLED, before any pawn is generated; it must take
   `ref IEnumerable<Pawn> __result` and replace it with a wrapper iterator. Any side effect (removing the
   nemesis from world pawns) must happen inside the wrapper during enumeration and must be idempotent —
   a caller that enumerates twice (vanilla `GenStep_OrbitalMechhive`, `QuestNode_Root_AncientMercenaries`,
   `QuestNode_Root_OrbitalFugitive` keep the bare `IEnumerable`) would otherwise inject twice / call
   `RemovePawn` on a pawn already removed.
   (b) It is called from ~40 sites (VERIFIED list): raids (`IncidentWorker_Raid.TryGenerateRaidInfo`),
   but also `GenStep_SitePawns`, `SymbolResolver_PawnGroup` (settlement defenders), `IncidentWorker_CaravanDemand`,
   `IncidentWorker_Ambush_EnemyFaction`, `PeaceTalks`, `MapGenUtility` and many quest parts. Gating on
   "Combat group of faction F" will drop him into a site garrison or a caravan ambush. PROPOSED: set a
   scoped flag in a prefix/finalizer pair on `IncidentWorker_Raid.TryGenerateRaidInfo` (VERIFIED public
   method) and inject only while it is set.
   (c) VERIFIED `TryGenerateRaidInfo` calls `parms.raidStrategy.Worker.SpawnThreats(parms)` first and
   only falls back to `GeneratePawns` when that returns null; `RaidStrategyWorker_SiegeMechanoid` overrides
   it (only override in Core). Mechanoids are not a nemesis faction, so low risk, but say it.
   (d) Spawning him removes his world-pawn pin (§1 finding 9): re-pin on his next exit.

6. **MEDIUM — recipes.md §5 boolean-gate postfix.** Signature VERIFIED: `public override bool
   FactionCanBeGroupSource(Faction f, IncidentParms parms, bool desperate = false)` on
   `IncidentWorker_RaidEnemy`; the recipe's `Postfix(Faction f, ref bool __result)` matches parameter
   names (Harmony binds by name — keep `f`). Both selection passes VERIFIED (lines 64/68, normal then
   `desperate: true`, via `TryGetRandomFactionForCombatPawnGroupWeighted`). Add: `IncidentWorker_RaidFriendly`
   has its own override and is not affected (correct), and any modded subclass of `IncidentWorker_RaidEnemy`
   that overrides without calling base escapes the gate.

7. **MEDIUM — recipes.md §1 XML incident + SKILL step 2 "shared cooldowns".** VERIFIED
   `FiredTooRecently` tests the OTHER defs' last-fire ticks against THIS def's `minRefireDays`. So a
   shared group is asymmetric if members have different `minRefireDays`; a member with `minRefireDays` 0
   ignores the group entirely. PROPOSED: "Give every member of a cooldown group the same `minRefireDays`;
   a 0 opts that def out of the group." Also: a forced fire stamps nothing (§1 finding 2).

8. **MEDIUM — recipes.md §6 Randy patch.** Fields VERIFIED (`incident`, private `category`, `onDays`,
   `offDays`, `minSpacingDays`, `numIncidentsRange`, `forceRaidEnemyBeforeDaysPassed`,
   `acceptFractionByDaysPassedCurve`, `acceptPercentFactorPerThreatPointsCurve`,
   `acceptPercentFactorPerProgressScoreCurve`, plus base `minDaysPassed`, `allowedTargetTags`,
   `disallowedTargetTags`, `minIncChancePopulationIntentFactor`=0.05, `enableIfAnyModActive`,
   `disableIfAnyModActive`). ConfigErrors VERIFIED: incident+category both set is an error; `onDays<=0`;
   `numIncidentsRange.TrueMax<=0`; `minSpacingDays*TrueMax > onDays*0.9`. Two additions: (i) a comp with a
   fixed `incident` still calls `incident.Worker.CanFireNow(parms)` at generation — so our
   `minRefireDays`/`earliestDay` apply; (ii) append only (comp index seeds the cycle; §1 finding 8), and
   comps re-init on load so the patch hits existing saves. (`<numIncidentsRange>1</numIncidentsRange>`
   parsing as FloatRange 1~1: UNVERIFIED; write `1~1` to be safe.)

9. **MEDIUM — recipes.md §3 IncidentQueue.** Add the silent-drop behaviour (§1 finding 7) and that the
   queued `FiringIncident` carries the parms object by Deep scribe (UNVERIFIED that every `IncidentParms`
   field is Scribed — `attackTargets`, `pawnGroupMakerSeed`, `questTag` should be checked in
   `IncidentParms.ExposeData` before relying on them surviving a save in the queue).

10. **MEDIUM — crew SKILL §1 "Headcount is a gate": a third joiner path is missing.** VERIFIED
    `QuestGen_Rewards` sets reward `populationIntent` from `QuestTuning.PopIncreasingRewardWeightByPopIntentCurve
    .Evaluate(PopulationIntentForQuest)`, and `PopulationIntentForQuest` uses
    `AdjustedPopulationIncludingQuests`. So ANY vanilla quest can offer a pawn as a reward even when its
    root does not set `rootIncreasesPopulation`. If the crew cap is a hard rule, the reward path needs
    its own gate (a postfix on reward generation or reward-def removal: UNVERIFIED best target).

11. **MEDIUM — crew_mechanisms.md §1 FloatMenuOptionProvider.** VERIFIED abstract members
    `Drafted`, `Undrafted`, `Multiselect` (protected abstract getters) and `GetSingleOptionFor(Pawn
    clickedPawn, FloatMenuContext context)` (protected virtual). Add: providers are auto-discovered —
    `FloatMenuMakerMap` instantiates `typeof(FloatMenuOptionProvider).AllSubclassesNonAbstract()`
    (VERIFIED), so no def/registration; and `TargetPawnValid`/`TargetThingValid` default to
    "spawned and not self" (VERIFIED) — override `TargetPawnValid` for the kin/factionless filter so
    the option is cheaply skipped, and return a DISABLED `FloatMenuOption` with the reason for the
    narrative refusals (the WAU rule).

12. **LOW — QuestScriptDef fields named in the docs.** VERIFIED present on `QuestScriptDef`:
    `rootSelectionWeight`, `rootSelectionWeightFactorFromPointsCurve`, `rootMinPoints`,
    `rootMinProgressScore`, `rootEarliestDay`, `rootIncreasesPopulation`, `minRefireDays`, `autoAccept`,
    `expireDaysRange` (default -1~-1), `isRootSpecial`, `canGiveRoyalFavor`, `everAcceptableInSpace`.
    IncidentDef fields VERIFIED: `baseChanceWithRoyalty` (-1 default), `populationEffect`
    (`IncidentPopulationEffect`), `earliestDay`, `minPopulation`, `requireColonistsPresent`,
    `minRefireDays`, `pointsScaleable`, `tags`, `refireCheckTags`, `chanceFactorByPopulationCurve`,
    `minGreatestPopulation` (-1), `letterDef`. No naming errors found in the docs.

13. **LOW — SKILL §2 step 6 cleanup.** `PassToWorld(p, PawnDiscardDecideMode.Discard)` VERIFIED goes to
    `DiscardPawn`. Fine; add "never on a spawned pawn — `PassToWorld` logs an error and returns
    (VERIFIED)".

## 3. Idea catalogue expansion

### 3a. Existing ideas that strain a ruling

1. **MEDIUM — §6 ideas 10 and 11 (nest under the landing gear / nest in the hold) vs our
   `Infestation_PlanetwideBan.xml`.** The study's own trap 7 says bans must name every def producing the
   effect; ideas 10-11 re-introduce an insect-hive effect under a new def. Not forbidden (it is our own
   creature and a telegraphed beat), but the catalogue must say "requires the owner to carve an exception
   to the planet-wide infestation ban" or it reads as a ban bypass — exactly the BI defect the study
   condemns.
2. **MEDIUM — ideas 13 and 14 (shrine keeper, market once a season) vs the frozen-planet ruling.** Both
   say "a world object with `TimeoutComp`". Spawning a world object on a calendar is creating a site;
   the ruling allows only authored sites that *exist*. PROPOSED wording: "an authored site on a fixed
   tile that is dormant (hidden or inert) and is *activated* for N days by the calendar; nothing is
   created at a random tile." Same note for idea 12 (already says authored) and idea 19's rescue site.
3. **LOW — idea 15 "burn a rival scavenger camp".** Destroying a settlement permanently removes an
   authored world feature from the frozen planet. Flag as owner decision (allowed in vanilla, but every
   player then plays a different planet afterwards — which is fine by the rulings only if intended).
4. **LOW — idea 21 "Heat is a threat".** Fine under "one kind of heat" (vanilla HeatWave stays vanilla
   heat), but say so explicitly so nobody builds a new heat hediff for it.
5. **LOW — idea 1 demand list includes "a named part".** If the ship part is load-bearing for travel,
   losing it can soft-lock "ship or nothing" travel. Demand list must exclude parts whose loss blocks
   launch, or the beat needs a guaranteed recovery path.

### 3b. New ideas (12)

| # | idea | situation | mechanism sketch | cost | reuses |
|---|---|---|---|---|---|
| 22 | **Storm cover** | Raiders come only under a dust storm, out of the murk, for the water stores. | `CanFireNowSub` reads the map's current weather (`map.weatherManager.curWeather`, UNVERIFIED field name in 1.6) against a tag list; parms: `raidArrivalMode` EdgeWalkIn, `attackTargets` = water storage, `canTimeoutOrFlee` true when the storm ends (a small `LordToil` check or simply our MapComponent sending the flee). Qualitative: same points, worse moment. | M | gate-by-world-fact (FRC/BI), IncidentParms levers |
| 23 | **Part thieves** | A small band goes straight for the engine cradle, grabs one part, and runs. | `IncidentParms.canSteal` + `attackTargets` = the gravship's part Things; small points; letter names the part. If they escape, OldFriends records the thief and the part — the return (idea 2) can bring it back as loot. | S-M | IncidentParms levers, Rimesis memory |
| 24 | **The debt ledger** | Every credit trade with the Hutt clan adds to a visible debt; past a threshold the collector (idea 1) comes, past a second a bounty. | One Scribed per-faction number (FRC shape, fixed); thresholds enqueue idea 1 / idea 33 via `incidentQueue`. State-flag storyline. | M | MFI war flag, FRC counter |
| 25 | **Thirsty pilgrims** | A non-joining group at the ramp asks for water. Give it and they bless your name with their clan; refuse and some of them try to take it at night. | `ChoiceLetter` subclass (§2 finding 1); Give = remove water, goodwill + `HistoryEventDef`; Refuse = queue a small `canSteal` raid of the SAME group 0.5 day later via `incidentQueue` with `pawnGroupMakerSeed`. `populationEffect` None — nobody joins. | M | TD inverted, MFI queue |
| 26 | **Stowaway** | After a gravship landing, a stranger is found in the cargo hold. Shelter, sell, or space them. | RM_Stranded quest shape (lodger + priced endings), triggered from our landing hook; a hidden roll (Space Worms disguise) that the stowaway is a scout for a faction — revealed by a visible tell (they keep looking at the cradle). `rootIncreasesPopulation` honest. | M | Stranded, Space Worms |
| 27 | **Wreck rumour** | A trader sells a rumour: a ship died in the dunes two days out, and it will be picked clean within a week. | Activates a dormant authored site for N days (see 3a-2); quest with `QuestNode_Delay` timeout and a site part; competing scavengers (idea 28) as the site's threat. | M | MFI world-object timeout (authored) |
| 28 | **Rival claim** | At the wreck you are stripping, a rival scavenger crew lands: half fight, half keep stripping until hurt. | LFB two-lord pattern on a site map: one assault lord, one "salvage" lord (a `LordJob` with a harmed trigger) — qualitative, no points scaling. | M | LFB |
| 29 | **They answer your turrets** | A clan that lost men to your turrets comes back with ion/EMP grenadiers. | On raid generation for faction F with a grudge, swap `pawnKind`/one group member's weapon based on a scan of the colony's defences (Rimesis `ColonyDefenseProfile`); one swap per raid, logged in the letter. Works without a named nemesis. | M | Rimesis counter-play |
| 30 | **A price on a founder** | Kill a clan chief and a bounty letter names the colonist who did it; hunters come for that one person. | OldFriends records the killer; next raid of F gets `attackTargets` = that colonist (UNVERIFIED that `attackTargets` steers a pawn target the way it steers buildings — check the lord toil) or a duty; letter reads the history back. | M | Rimesis grudge, reversed |
| 31 | **Water caravan heartbeat** | A friendly moisture-farming clan sends a water caravan more often the better you treat them. | MFI goodwill-curved heartbeat: per-faction Scribed next-tick, interval from a curve on goodwill, enqueue `TraderCaravanArrival` with that faction and a retry window. Scarcity relief earned by diplomacy. | S-M | MFI heartbeat |
| 32 | **Quarantine order** | A friendly settlement refuses your caravan while one of your crew carries the sickness (idea 6). | `CanFireNowSub`/arrival-action check on a hediff; a `DiaNode` refusal with the reason; treat the sick to reopen trade. Consequence of idea 6, no new threat. | S | Space Worms contagion, WAU reason-for-refusal |
| 33 | **Last warning** | Before a big raid from a clan with a grievance, a messenger arrives: return what you took or else. | `ChoiceLetter` with timeout (§1 finding 6) offering to hand back a stolen/looted item; Comply cancels a queued raid (remove our own queued entry — our component holds the ref); Ignore lets it fire. A telegraph for a ThreatBig. | M | TD choice, BI telegraph, MFI re-opening letter |

**Cheapest additions:** 23, 31, 32 (S/S-M). **Best payoff:** 25 and 33 — each turns an existing threat
into a decision with the new save-safe letter shape and no new spawn logic.

## 4. Skill wording and structure

1. **HIGH — `rimworld-custom-incidents/SKILL.md` §3 trap 1 text is mis-attributed** (see §1 finding 1).
   PROPOSED REPLACEMENT: "🔴 **Returning `true` before anything happened.** `Storyteller.TryFire` stamps
   the cooldown and the ThreatBig clock (`StoryState.Notify_IncidentFired`) whenever `TryExecute` returns
   true. A worker — or a Harmony prefix setting `__result = true` — that opens a dialog and returns true
   is counted as fired with zero pawns: the Raid Protection Fee defect of 2026-10-10. Return true only
   when the true outcome is 'the player was asked', and hold the pending choice in a `ChoiceLetter`
   (recipes §2), never a closure."

2. **HIGH — same SKILL §3: add four traps, each one line** (all VERIFIED, §1/§2 above):
   - "`requireColonistsPresent` with everyone off-ship returns true doing nothing — the incident is
     consumed and its cooldown stamped. Refuse in `CanFireNowSub` instead."
   - "`CanFireNowSub` is cached per tick per DEF, not per target."
   - "`forced` fires stamp no cooldown; direct `Worker.TryExecute` calls skip gates AND stamp. Schedule
     through `incidentQueue` or `Storyteller.TryFire`."
   - "A queued incident with no retry window that fails at its tick is dropped silently."

3. **HIGH — SKILL §1 vehicle table: add two rows.**
   `| a choice the player may sit on (pay/refuse, accept/turn away) | a ChoiceLetter subclass with Scribed fields and a timeout | small |`
   `| our scripted beat should ignore difficulty/scenario bans but keep biome and spacing | parms.bypassStorytellerSettings = true (not forced) | none |`

4. **HIGH — `rimworld-crew-and-nemesis-events/SKILL.md` §4 step 3 and §5 trap 2; `nemesis_lifecycle.md`
   save checklist bullet 2.** Replace with the §1 finding 9 text. Concretely, step 3 becomes: "Keep him
   alive off-map: `PassToWorld(p, KeepForever)` when he leaves, or `Find.WorldPawns.ForcefullyKeptPawns.Add(p)`
   if he is already a world pawn (these are the same set, and vanilla saves it). **Spawning him into a
   raid removes the pin** (`WorldPawns.RemovePawn`) and his next `ExitMap` passes him back in `Decide`
   mode — re-pin on every exit. Release with `ForcefullyKeptPawns.Remove(p)` when the roster forgets
   him." Delete "re-check pins on load" (vanilla does it and logs nulls).

5. **HIGH — crew SKILL §4 step 4 and nemesis_lifecycle step 3: add the iterator + call-site scope**
   (§2 finding 5). PROPOSED one-paragraph replacement for step 3: "Postfix
   `PawnGroupMakerUtility.GeneratePawns` with `ref IEnumerable<Pawn> __result`, wrapping it in our own
   iterator — it is a C# iterator, so the postfix runs before any pawn exists. It is called from ~40
   places (sites, settlements, ambushes, quests), so inject only while a scoped flag set around
   `IncidentWorker_Raid.TryGenerateRaidInfo` is on, and make the injection idempotent (some callers
   enumerate twice). Remove him from world pawns inside the wrapper, once."

6. **MEDIUM — crew SKILL §1: add the quest-reward joiner path** (§2 finding 10) as a fourth bullet, and
   replace "an owner ruling (card C07)" with plain words: "an open owner question: may anyone join the
   crew at all (card C07)" — the card id alone is opaque to a fresh reader.

7. **MEDIUM — both SKILL descriptions are long and lead with retiring-mod names.** Mod names are
   history; triggers should be symptoms and intents. PROPOSED description for custom-incidents
   (≈600 chars): "Build our own RimWorld 1.6 incidents and storyteller pacing: an IncidentDef + worker, a
   follow-up via IncidentQueue, a pay-or-fight choice held in a ChoiceLetter, a per-faction memory that
   changes what arrives, a comp patched into vanilla Randy. Covers every CanFireNow gate, forced vs
   bypassStorytellerSettings, what stamps a cooldown, population intent, qualitative (not bigger)
   danger, save-safe pending choices, test hooks. Use for any new event, raid variant, extortion,
   visitor, disaster or pacing rule; when an incident never fires, fires twice, or 'fired' with nothing
   arriving; before patching a vanilla IncidentWorker. Quests: rimworld-quests. People events:
   rimworld-crew-and-nemesis-events." Keep the studied-mod list in the body's first paragraph.
   Same treatment for crew-and-nemesis (drop the mod list from the description, keep "nemesis, rival,
   recurring villain, recruit, kidnap, ransom, slave, crew cap, world-pawn list grows, remembered pawn
   vanished").

8. **MEDIUM — `references/recipes.md`: reorder and add.** Put the new ChoiceLetter shape as §2 (the
   single most valuable pattern per the study's own synthesis), move the modal-dialog variant under it
   as "only with `preventSave`", and fix §4's TryExecute line (§2 finding 2). Add a short §8 "What
   stamps what" table: TryFire→cooldown+ThreatBig clock (not forced); TryExecute direct→nothing;
   RecordIncidentFired→Anomaly ratio only; IncidentQueue→TryFire(queued). This one table prevents most
   of the traps.

9. **MEDIUM — `mod_lessons.md` RPF line "Copy: deferred execution via a re-entrancy flag".** RPF's flag is
   static, which the same docs forbid. Clarify: "a static re-entrancy guard is fine when it is set and
   cleared in one `try/finally` inside one call (it never spans a save); pending *choices* are not."

10. **LOW — study §2.1 "fun vs annoying" says "mid-dialog game state keeps running or is paused depending
    on window".** It is paused (VERIFIED `forcePause`). Fix the sentence; it currently teaches doubt
    where there is a fact.

11. **LOW — study §7 "GPT review disposition" placeholder.** Record that this Opus review stood in for
    the GPT consult (usage limit) and list which findings were applied; otherwise a later reader will
    assume an external consult happened.

12. **LOW — cut from SKILL §2 step 2 "and Rand there shifts the RNG"** — true but misleading priority; the
    per-def cache is the real hazard (replace with §2 finding 3 text).

## Top 5 changes

1. **Make `ChoiceLetter` (Scribed fields + timeout + `Removed()` default) the canonical pay-or-fight shape**
   in recipes §2, the SKILL vehicle table and ideas 1/16/25/33; demote the modal dialog to "only with
   `preventSave = true`" (Dialog_NodeTree force-pauses but does NOT block saving — VERIFIED).
2. **Correct the cooldown story everywhere:** `RecordIncidentFired` is Anomaly-only; the cooldown and
   ThreatBig clock come from `TryFire → StoryState.Notify_IncidentFired`, which forced fires skip and
   direct `Worker.TryExecute` calls never reach — and fix recipe §4 to schedule via `incidentQueue`/`TryFire`.
3. **Fix the world-pawn pin text:** KeepForever *is* ForcefullyKeptPawns, vanilla saves it, but spawning
   the nemesis clears it (`WorldPawns.RemovePawn`) and his next `ExitMap` is `Decide` mode — re-pin on
   every exit; drop "re-pin on load".
4. **Rewrite the GeneratePawns injection step:** iterator postfix via `ref __result` wrapper, scoped to
   `IncidentWorker_Raid.TryGenerateRaidInfo` (it has ~40 call sites incl. settlements/sites/ambushes),
   idempotent removal from world pawns.
5. **Add the four silent-failure traps** to the incidents SKILL: `requireColonistsPresent` consumes the
   incident when the crew is off-ship; `CanFireNowSub` cache is per def not per target; queued incidents
   without retry drop silently; use `bypassStorytellerSettings` rather than `forced` for scripted beats.

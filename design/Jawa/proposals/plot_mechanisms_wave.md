<!-- status: DRAFT PROPOSAL for owner review — written AFK 2026-09-05 on the owner's brief, not ruled. Design only; no code, no defs, nothing deployed. -->
# Plot mechanisms wave — the raid redesigner, aftermath hostilities, and what the plot still lacks

Grounding: `llm_driven_mods_deep_design.md` (the Oracle consumer roster and the
owner's 2026-09-02 rulings — baseline prescripted, LLM-enriched when available;
budget per real-world hour, not per game day; the LLM may later *arbitrate*
whether the game reacts, not only talk), `design/RimMandrake/llm_ingame_wiring_spec.md`
§2b (raids as a LEGAL MENU + a persisted named-antagonist roster — already law;
this doc is that section built out), `src/RimMandrake/Oracle` (the shipped
client: async `Task.Run` → `MainThreadQueue` delivery, hard timeout + one retry
on 408/429 only, kill switch, blank-key silent fallback, register-lint
validator, `godsBudgetPerDay`), `reconciled_lore/*` and `first_contact_chains.md`,
`divine_satiation_engine.md`, and the live mod list (595 active in
`ModsConfig.xml`, read 2026-09-05). The narrator is the ship's repurposed
original mind — hidden, non-egoic, a VOICE that narrates and never converses.
No god narrates; Ohm is one tenant of nine.

Three laws carried unchanged from the wiring spec and the owner's rulings, so
nothing below restates them per section: **(1) text authority or menu authority,
never free authority** — every LLM field is validated in C# and a miss ships the
prescribed default silently; **(2) the game is whole with the LLM absent** —
every mechanism here ships its deterministic baseline FIRST and the Oracle only
enriches; **(3) anti-exponential / §19.5** — nothing here is a bigger number;
danger changes in KIND (composition, arrival, who, why), never in stat.

Two facts about the shipped Oracle that every part below depends on:
- `mandrake.rm.oracle` is **not in the live 595**; it ran on the 22 s minimal
  list only (`ORACLE_EXPERIMENT_SPIKE_1`). Everything here assumes it is
  promoted to the full list before any consumer goes live.
- `OracleHttpClient` hard-codes `max_tokens: 200` and a two-string
  (system, user) shape. Part 1 returns a JSON object of ~600–900 tokens, so the
  client needs a per-call `maxTokens` and a `response_format: json_object`
  request flag (both one-line additions; the hand-rolled JSON writer already
  escapes correctly). Not a redesign — noted so nobody is surprised.

---

## PART 1 — `RimMandrake: Raid Redesigner` (`mandrake.rm.raidredesigner`)

Folder `src/RimMandrake/RaidRedesigner/`, C# namespace
`RimMandrake.RaidRedesigner`, defs `RM_*`. Campaign-agnostic mechanism.
The Ash'karr flavour — the thirteen faction register blocks, the Jawa-specific
grudge vocabulary — ships as a defs-only companion
`RimUtinni: Raid Register` (`mandrake.rut.raidregister`, `RUT_*`), so the
engine never contains a Hutt.

### 1.1 What the player feels

A raid lands. The letter is not "A group of raiders from the Junkers has
arrived, attacking immediately." It is: *"Gutter-Saw Vekk came back. You left
him for dead in the Scald wash two quadrums ago and took his casket's saw-arm
for the Press; he has a new one, and eleven friends who want to see the
machine it went into. They came up the dry channel on the west — the one your
lookouts do not watch."* The pawns match the letter: a casket-welded Junker
with Vekk's name over his head, a composition built to reach the Press, an
arrival on the west edge. Nothing else changes. No panel, no "nemesis" tab, no
meter — the ONLY new surfaces are ones the game already has: the raid letter,
the nickname over the head, the social tab (see §1.4 — vanilla writes the
relation line into the letter for free), and the Narrator's letters.

### 1.2 Hook point — verified against the 1.6 source (`mcp__rimsage`)

The raid pipeline is `IncidentWorker_RaidEnemy.TryExecuteWorker` →
`IncidentWorker_Raid.TryExecuteWorker` → `TryGenerateRaidInfo(parms, out pawns)`,
which in order: `ResolveRaidPoints` → `TryResolveRaidFaction` →
`ResolveRaidStrategy` → `TryResolveRaidArriveMode` (**skipped if
`parms.raidArrivalMode` is already set** — read from source) →
`raidStrategy.Worker.TryGenerateThreats` → `TryResolveRaidSpawnCenter` →
`parms.raidStrategy.Worker.SpawnThreats(parms)` (**virtual; returns null unless
`parms.pawnKind` is set, and null falls through to
`PawnGroupMakerUtility.GeneratePawns`**) → `Arrive` → `PostProcessSpawnedPawns`
→ `GenerateRaidLoot`; then `GetLetterText` builds the letter (arrival-mode
text + strategy text + "leader present" line) and
`PawnRelationUtility.Notify_PawnsSeenByPlayer_Letter` appends relation lines.

Three Harmony points, all prefixes on existing seams, no transpiler:

| seam | what we do there |
|---|---|
| **A. `IncidentWorker_RaidEnemy.TryExecuteWorker` prefix** | The DEFERRAL. If this `parms` carries no redesign and the Oracle is live: snapshot the parms (`ShallowCopy`), register a pending redesign keyed to the copy in `GameComponent_RaidRedesign`, fire the async Oracle call, re-queue the SAME incident via `Find.Storyteller.incidentQueue.Add(def, Find.TickManager.TicksGame + 2500, copy)` (the vanilla delayed-incident route — `IncidentQueue.Add(IncidentDef, int fireTick, IncidentParms)` exists exactly for this), and return `false` to cancel this firing. The raid simply lands an in-game hour later than the storyteller rolled; nothing announces it (`SignalForceNormalSpeedShort` only fires inside the real execution). If the redesign has not arrived when the queued copy fires, ONE more 2500-tick requeue; after that it runs vanilla. Deferral is skipped for quest raids (`parms.quest != null`), forced raids, and anything with `pawnGroupKind != Combat` — those are somebody else's story. |
| **B. `IncidentWorker_Raid.TryGenerateRaidInfo` prefix** | Apply the redesign's MENU fields onto `parms` before vanilla resolves them: `raidArrivalMode`, `raidStrategy` (verify at build that `ResolveRaidStrategy` honours a preset the way `TryResolveRaidArriveMode` provably does; if not, a postfix on `ResolveRaidStrategy` re-applies it), `spawnCenter` when the redesign chose an edge, `points` only within ±20 % of the storyteller's own. |
| **C. `RaidStrategyWorker.SpawnThreats` prefix** | Composition. When a redesign is present, build the list ourselves: `PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, faction, NonPlayer, tile, mustBeCapableOfViolence: true, …))` per composition row, plus the recalled OLD FRIENDS pulled back from `WorldPawns` (they are live `Pawn` objects, §1.4), set `parms.raidArrivalMode.Worker.Arrive(list, parms)` exactly as vanilla does, and return the list so vanilla's null-check falls through to nothing. If the composition validates to empty, return null → vanilla group maker → the redesign degrades to letter-only. |

Letter: `parms.customLetterLabel` / `customLetterText` are honoured by
`SendStandardLetter`; the redesign fills them, vanilla still appends the
relation lines. `EmpirePursuit`'s existing patch on
`IncidentWorker_RaidEnemy.FactionCanBeGroupSource` is upstream of all three
seams and untouched.

### 1.3 The prompt (what C# assembles; the LLM never receives an open question)

**System:** the wiring spec's Law block + the raiding faction's register block
from the RUT companion (one faction only, ~120 words: who they are, why they
raid, what they never do, their voice — e.g. Deep Desert Tribes: chiefless,
fast, water is the object, offworld tech is destroyed not looted, fire is a
tool; Junkers: arrive second and kill whoever arrived first, a casket is a
biography, corpses are stock; Blackstar: hostile only because someone paid,
professionals under the Code) + the Narrator's register (`narrator_corpus`),
because the letter is HIS voice describing THEM, in the second person, free to
reference unrevealed lore.

**User turn — a single JSON `DATA` block, every free-text field fenced as
inert (the wiring spec's injection rule):**
- `raid`: faction defName + display name, storyteller points, the vanilla
  strategy and arrival mode it rolled (the LLM may keep them), map edge
  options actually legal (`PawnsArrivalModeDef.Worker.CanUseWith(parms)`
  computed for each candidate), strategy options legal for this faction and
  points band, the day/hour, the map's weather.
- `menu.composition`: the faction's `pawnGroupMakers[Combat].options` as
  `{pawnKind, label, combatPower, minPoints}` rows — the ONLY kinds it may use.
- `colony_facts`: colonist count, notable defences by category (walls /
  turrets / traps / open field — booleans, not counts), the wealth band the
  storyteller already used, the last three raids' outcomes against THIS
  faction (won / lost / fled), what was taken or killed.
- `old_friends`: up to four roster candidates for THIS faction (§1.4), each a
  dossier: name, role tag, the encounter list in one line each, grudge sign.
- `wronged`: up to three things the colony did to this faction that the
  Property fabric / kidnap tracker / release log recorded (a robbed caravan, a
  released prisoner, a sold kinsman) — the LLM's "why now".

**Returns (JSON, menu authority, every field clamped in C#):**
```
{ "strategy": <one of menu>, "arrival": <one of menu>, "edge": <one of menu|null>,
  "composition": [ {"pawnKind": <menu>, "count": n}, ... ],        // Σ combatPower ≤ points band; excess rows dropped from the end
  "recall": [ <old_friend id>, ... ],                              // 0–2, subset of offered
  "captain": {"of": <old_friend id | "new">, "nick": "...", "line": "..."},   // nick ≤ 18 chars, no defNames
  "named": [ {"index": i, "nick": "...", "motive": "..."} ],       // ≤ 3 more, one-line motives, letter-only
  "letter": {"label": "...", "body": "..."} }                      // register-lint + length cap (≤ 900 chars)
```
Rejected → that field's default (vanilla strategy/arrival, vanilla group
maker, no recall, vanilla letter). One bad field never kills the others.

### 1.4 Old friends — the persistent roster of people the colony has met

`GameComponent_OldFriends` (in the RM engine): a scribed list of
`OldFriendEntry { Pawn pawn (Scribe_References), Faction factionAtEntry,
RoleTag role, List<Encounter> encounters, int grudge, int notability,
int lastSeenTick, bool dead }`. Roster cap 24 living; prune lowest
notability; dead entries collapse to one line and stay (a dead friend's
brother is the LLM's best material).

**Pinning.** A raider who leaves the map goes through `Pawn.ExitMap` →
`Find.WorldPawns.PassToWorld(this)` with the default discard mode, and the
world-pawn GC will eventually drop him. The roster pins its people with
`PassToWorld(pawn, PawnDiscardDecideMode.KeepForever)` (the same call
`Faction` uses for its leader) — so an old friend is a REAL pawn with his real
scars, missing arm, and the casket saw we took, not a regenerated lookalike.

**Capture hooks (each a postfix on a vanilla seam, each writes one Encounter):**

| moment | seam | role tag |
|---|---|---|
| a raider flees alive | `Pawn.ExitMap` postfix, hostile faction, was on a player map, raid lord active | `FLED_RAIDER`; notability += downed-and-recovered, colonist kills (`pawn.records` KillsHumanlikes delta this raid), was faction leader |
| a raid captain leaves | same, plus `Faction.leader == pawn` or our own captain flag | `CAPTAIN` |
| a prisoner escapes | `GuestUtility.Notify_PrisonerEscaped` postfix | `ESCAPED_PRISONER`, grudge high |
| a prisoner is released | `Pawn_GuestTracker.SetGuestStatus(null)` with `Released` | `RELEASED` — the one who owes us, or hates us for the mercy (the LLM decides, the dossier records only the act) |
| a caravan/visitor is robbed | `mandrake.rm.property` `TakingEvent` resolved against a non-player pawn (the fabric already records witness + confidence) | `BETRAYED_TRADER` |
| a colonist is kidnapped | `Faction.kidnapped.Kidnap` postfix — the KIDNAPPER is the friend, the victim a slot for a rescue-return | `KIDNAPPER` |
| a wandering ancient is woken and leaves | ShipMemory / VaultDungeons wake signal | `WOKEN_ANCIENT` (Part 3 — the Reclamation reads this) |
| a Named Hunter (Blackstar) is captured/freed | guest status changes on a `Blackstar` pawn | `NAMED_HUNTER` (the canon truce token) |

**Meaningful Encounters** (`sirdarkelf.meaningfulencounters`, live) lets the
player MARK a raider by hand so he recurs; a marked pawn enters the roster at
top notability. No conflict — ours is automatic, theirs is the player's thumb.
**Rumor Has It** (`mlie.rfrumorhasit`, live) tracks what visitors witnessed
for faction-relations purposes; it is a parallel memory, not the same one.

**Recall.** At seam A, C# pre-selects candidates whose CURRENT faction is the
raiding faction (Blackstar excepted: as the world's hire, a Blackstar friend may
ride with any faction the register says can pay them). The LLM picks 0–2. On
spawn the recalled pawn keeps his own kit; he gets the nickname the LLM wrote
(`pawn.Name = new NameTriple(first, nick, last)` — the over-head label) and,
the first time he is recalled, an `RM_OldEnemy` `PawnRelationDef` to the
colonist he wronged most (opinion −40 both ways, not blood, no other effect).
That single def is what makes vanilla's own
`Notify_PawnsSeenByPlayer_Letter` append *"…including Gutter-Saw Vekk, old
enemy of Griz Utinn"* to EVERY future letter he appears in, and put him on
Griz's social tab — a felt surface the engine already draws, at zero UI cost.

**Death closes the file.** A recalled friend who dies on our map writes his
last Encounter and flips `dead`; the next raid from his people may carry his
brother — a NEW pawn the LLM names in `named[]`, entered into the roster as
`KIN_OF(<dead id>)` so the thread survives one more generation and then ends.
Threads are finite by construction; the roster is not a villain generator.

### 1.5 Latency and budget

- Budget bucket `raidsPerRealHour` (default 6), **real-time**, per the
  owner's 2026-09-02 ruling — a new bucket beside `godsBudgetPerDay`, which
  should itself migrate to real-hour accounting in the same change. Over
  budget → no deferral, vanilla raid, deterministic recall (below).
- Timeout: the Oracle's 15 s × 2 attempts fits inside one 2500-tick deferral
  at 1× (41 s) and inside two at 3× (14 s each). The deferral IS the latency
  budget; nothing waits on the main thread.
- Kill switch off / no key / validator reject / timeout → identical: the raid
  fires as vanilla, on the deferred tick, with the **deterministic baseline**:
  C# alone picks the highest-grudge same-faction roster entry with p = 0.35,
  spawns him with the vanilla group, and appends a templated line —
  *"Among them: {NICK}, who {last encounter}."* Prescripted baseline, LLM
  enrichment — the owner's stated metric.

### 1.6 What it deliberately does not do

No new pawn kinds, xenotypes, gear or stats — composition is a choice among
the faction's own options at the storyteller's own points. No authored
BackstoryDefs at runtime — the "backstory" lives in the letter, the nick, the
relation line and the roster, never a def. No panel. Hutt Cartel never appears
in a raid (canon) and `raidsForbidden` factions are never offered — both fall
out of the menu, not of a special case. Quest raids and the Empire pursuit's
own arrivals pass through untouched.

---

## PART 2 — Aftermath: hostilities born of what just happened

`RimMandrake: Aftermath` (`mandrake.rm.aftermath`, ns `RimMandrake.Aftermath`)
holds the battle recorder and the rule runner; the nine-god rules live in a
defs-only `RimUtinni: Aftermath Rites` (`mandrake.rut.aftermath`) and talk to
the satiation engine through `mandrake.rm.ninefold`'s existing public surface
(`GameComponent_Ninefold.ApplyDelta(God, amount, reason)`, `GetBand(God)`,
`GetMood(God)` — read from source). Every rule is one `RM_AftermathRuleDef`:
**trigger → delay → telegraph → payload**, payload always an existing
`IncidentDef` queued through `Find.Storyteller.incidentQueue.Add(def, fireTick,
parms)` with `parms.forced = true` (⚠️ `mlie.factionraidcooldown` is live and
suppresses repeat raids per faction — our queued follow-ups must bypass its
check or the whole part is silently inert; verify its hook at build).

**The battle recorder.** A `MapComponent` opens a `BattleRecord` when
`TryGenerateRaidInfo` returns true (faction, pawns, points, arrival, tick) and
closes it when the raid's `Lord` is removed: outcome ∈ {REPELLED (≥ 60 % of
pawns dead/downed), ROUTED (survivors exited — feeds the roster), STALEMATE
(timeout/steal-and-leave), LOST (colonist deaths/kidnaps ≥ 1 and raiders
left by choice)}, plus: our dead, their dead left on the field, prisoners
taken, wreckage left. The record is the trigger source for everything below,
and it fires `Sh'kaar +Δ` — **the battle hook Ninefold currently lacks** (its
five patches are birth, deconstruct, repair, mental break, research; no
combat seam exists yet — verified by reading `Ninefold/Source`).

### 2.1 The rules

| # | rule | trigger | delay | telegraph (existing surfaces only) | payload | god tie |
|---|---|---|---|---|---|---|
| 1 | **Regroup and return** | ROUTED with ≥ 3 survivors or any roster CAPTAIN | 2–6 days | day −1: a lone scout of that faction spawns at an edge, `mindState.exitMapAfterTick` ≈ 1 h (the vanilla wanderer-leaves route), Narrator line *"Someone counted your doors today"* | same-faction raid at storyteller points, composition biased to the COUNTER of what beat them (walls → sappers/breach strategy; turrets → smoke/shield-heavy options; open-field → ambush arrival) — a menu choice, LLM-picked if Part 1 is live, C# heuristic otherwise; recalled old friends ride | Sh'kaar +; Ishko − if the scout was not killed unseen |
| 2 | **The allies arrive** | REPELLED/ROUTED faction A has a canon ally B not friendly to the player | 3–8 days | letter in B's livery: why they come | raid by B, Part 1 letter names A as the reason | — |
| | *the alliance table (v1's "fiction-only" hostilities, given exactly one mechanism)* | `RM_AlliancePairDef {a, b, weight}`: Geonosian Hive ↔ Free Droid Enclaves (formal, with trade); Junkers ← Enclaves (fuel dependency, one-way); **Blackstar ← anyone who can pay** (Hutt after a theft from them, Empire after a pursuit loss, Helix after an escaped Asset) — this is the ONLY way Blackstar is ever hostile, per canon | | | | Mob'Unloo: a Blackstar hire after a robbery is "the ledger comes due" |
| 3 | **Scavengers on the field** | ≥ 6 non-colony corpses or ≥ 3 wrecks unburied 24 h after a battle on a surface map | 1–3 days | vultures/desert scavenger animals gather (a small `AggressiveAnimals`-style spawn set to leave, not hunt); hull heat vents tick | Junkers arrive — *"scavengers who arrive second and kill whoever arrived first"* — steal-then-leave strategy, `attackTargets` = the wreck cells (vanilla `IncidentParms.attackTargets`) | Ishko: burying within a day is already his piety; Rekko − if we let repairable wreckage rot |
| 4 | **They come for their own** | prisoners of faction F held ≥ 3 days, F hostile | 4–10 days | comms chatter letter; for Blackstar an EXCHANGE offer letter instead (canon: honoured exchanges, no ransom); for Hutt a ransom demand (`geojak.tributedemand` covers extortion for goods and already ships the "pay or raid" fork — reuse its dialog, do not rewrite) | rescue raid with `attackTargets` = the prison cells; Deepwater and Homestead never (raidsForbidden) | Oomo + when kin are ransomed home the other way; Mob'Unloo reads any exchange as a deal |
| 5 | **Sh'kaar's escalation** | Sh'kaar band crosses Content, then Exalted | continuous | the signature kit: +2° aboard, bell tolls, sun glare; Narrator dread | **Content:** arrival modes lose the gentle options (edge walk-in removed from the menu — drop-in, sappers, tunnels remain), animal manhunts queue on the god's clock, Ishko's "raid that did not come" boon is suppressed. **Exalted:** ONE "the sun's regard" raid — the most-wronged faction, every living old friend of theirs recalled at once, storyteller points untouched | the escalation meter made mechanical; **calm levers** (canon): a prisoner death-match or execution → Sh'kaar −, Zizzik +; releasing a prisoner into the desert → Sh'kaar −; three battles declined (raids that timed out while we hid) → cools |
| 6 | **Zizzik's aftermath** | a mental break within 2 days after a battle while Zizzik ≥ Content (Ninefold already patches `MentalStateHandler`) | 1–4 days | chartreuse flicker, the triple rattle | one misfortune from a legal list: slave rebellion (`mlie.slaverebellionsimproved` is live — trigger its incident), a turret/power short (vanilla `ShortCircuit`), or **the returning raid breaches at our weakest wall** — C# computes the lowest-HP hull segment and sets `spawnCenter` there; a FED Zizzik's positive: 1-in-4 the returning group arrives already fighting a rival (Factional War's bystander battles cover the visual; we only choose it) | Zizzik +/− per rule |
| 7 | **The rooted receipt** | Ta'Baa's rooted clock passes a quadrum without a launch | at the tick | violet exit-lights, engine cough (the chain's kit) | not a raid: the NEXT raid against us gets the most direct arrival legal and its letter says they were told where we sit by a trader who visited; Inhabited's rumor fabric records the leak | Ta'Baa −; Mob'Unloo notes who sold us |
| 8 | **The reckoning** | a `TakingEvent` against a Hutt caravan resolves with witnesses (Property fabric) | 5–12 days | a Hutt envoy letter naming the debt | rule 2's Blackstar hire, OR `tributedemand`'s pay-or-raid fork with the Hutt as claimant | Mob'Unloo: paying is a deal (+), being caught was the sin (−) |

### 2.2 Discipline

- **Every aftermath telegraphs** 0.5–2 days ahead through a surface that
  already exists — a letter, a scout, a god's kit, a caravan's gossip. Nothing
  arrives out of nowhere twice; the player is being taught to read the sky.
- **No stacking beyond one queued aftermath per faction and two total.** A
  battle that would queue a third is simply remembered by the roster instead.
- **Attenuation** (F2): the god rules run only where the hull is; a caravan
  ambush produces a roster entry and a Narrator letter, never a god delta.
- **Points never exceed the storyteller's own** for the payload; what changes
  is who, from where, with what, and why. That is the §19.5 test passed by
  construction, not by tuning.
- With Part 1 live, every payload raid passes through the redesigner and its
  letter can SAY it is an aftermath. Without it, each rule ships a templated
  letter naming the cause — the prescripted baseline.

---

## PART 3 — Plot-gap analysis: what the plot AS WRITTEN still needs

Method: each designed arc, dungeon, quest and win path in `09_arcs_dungeons_quests.md`
(and the mechanisms the other lore files lean on) checked against (a) our 66
shipped/in-progress mods across the three tiers and (b) the 595-mod live list.
"Covered" means a mechanism exists, not that it is verified live; "partial"
names what half exists. One-line proposals only; none is ruled.

| arc / need | what the plot needs | coverage | proposal |
|---|---|---|---|
| **Pursuit spine** — Empire orbital detection, exit under a growing season, dark/covered tiles PAUSE the clock | a per-tile clock with a pause rule | `mandrake.rut.empirepursuit` (ScenPart port) covers the pursuer; **the dark-tile pause is UNVERIFIED in its source** | read `RuthlessPursuingMechanoids.cs` for a tile predicate; if absent, add a `RUT_PursuitShelter` tile test (biome dark / roofed / underwater) before anything else — the campaign's stated core loop depends on it |
| **HIDE — the third verb** (under water, in the dark) | concealment from pursuit as a mechanic; Deepwater diplomatic price for water tiles | `mandrake.rm.visibility` (colony visibility stat) — partial; GravTide was "under evaluation" 2026-08-13 and is NOT in the live list | fold visibility into the pursuit predicate (above) and drop the GravTide dependency; the verb is a stat + a tile test, not a mod |
| **Flight hardware earned mid-game** | thrusters/tank/console as a research-and-materials earn | Odyssey + `vanillaexpanded.gravship` + research retag — covered | none |
| **Rakata reversal — vaults (garrison / flesh / sleepers)** | six sited vaults, thaw-gate quest, wake/loot/leave payoff ladder | `mandrake.rut.vaultdungeons` (KCSG layouts generated), `VaultDungeons` defs — layouts only; **no QuestScriptDef, no thaw signal, no sleeper AI** | one `RUT_VaultThaw` QuestScriptDef family (per `rimworld-quests`: node tree at offer, signals to the map) — the biggest single gap between "map exists" and "arc plays" |
| **Assailant flesh dungeon** | the wordless reveal; Anomaly fleshmass toolbox used ONLY here | Anomaly content at zero except this exception; spec drafted, **nothing built** | `ASSAILANT_DUNGEON_BUILD_1` is the owner's sitting; no mechanism gap beyond the thaw quest above |
| **The woken claim the ship** | a woken sleeper challenges possession of the Utinni | **nothing** | a `WOKEN_ANCIENT` roster role (Part 1) + one QuestScriptDef: *the Claim-Conflict* — demand, refusal, departure with a grudge; feeds the Reclamation |
| **The Reclamation** (late game: every woken ancient + the Helix turn hostile, one event) | a persistent list of who was woken, a Helix flip, one authored assault, permanent neutrality after | **nothing** — and no engine tracks "everyone you ever woke" | the old-friends roster IS that list; the Reclamation is Part 2's rule 5 Exalted shape with `WOKEN_ANCIENT` + Helix as factions and a post-battle `Faction.SetRelation(neutral)`; two authored scenes after (Helix's true heart, the Cathedral's refusal) are letters |
| **Antiquities — the Recovery Raid** (sold urns persist at the buyer's settlement) | items that persist in a settlement's inventory and a raid to retrieve them | `mandrake.rut.antiquities` slice 1 (tree + items + reading loop); `Inhabited`'s `InhabitedStock` persists settlement stock — partial | an `RUT_UrnLedger` that writes each SOLD urn into the buyer's Inhabited stock and marks the settlement as the LOST-ledger target; the raid is vanilla settlement attack |
| **Antiquities — the Empire urn-hunt** | Empire raids that target urns, destroying not looting | vanilla `IncidentParms.attackTargets` exists; nothing uses it for urns | Part 2 rule: Empire raid with `attackTargets` = urn stacks, `canSteal = false`, a destroy job on reach |
| **Antiquities — the Call-Out at VOICE** (called-out ancients stand down and LEAVE) | a running hostile lord replaced by an exit lord on a signal | **nothing** | a `RUT_CallOut` ability/ritual that, for `WOKEN_ANCIENT` pawns on the map, swaps their lord to `LordJob_ExitMapBest`; the Testament urn spawns at the edge on exit |
| **Geonosian Alliance** (a protected base for ship/urn tech, until the Empire erases them) | a quest-shaped alliance + a scripted settlement destruction | `mlie.morefactioninteraction` adds diplomatic events (partial: alliances-by-event exist, not this one); `faction_semipermanent_bases_seed.md` is a seed | one QuestScriptDef with a timer; the erasure is vanilla `DestroyedSettlement` on their two sites + a Part 2 "allies arrive" fires for the Enclaves |
| **Rust Cathedral sacrilege** (~10 sacred buildings, −15 each, hysteresis −75/0) | goodwill loss for destroying faction-owned buildings on a NON-settlement map, with hysteresis | **nothing** — vanilla only penalises on settlement maps | `RM_SacredStructure` ThingComp: on destroy/deconstruct by player → `TryAffectGoodwillWith(−15)`; hysteresis is a 2-line `FactionRelationKind` rule in the same comp |
| **The Cathedral is a MIND** (favours droids, tolerates the clan because the ship vouches, grants gravtech boons at risk) | a non-faction actor with attitude | **nothing**; v2 by register | park: an Oracle consumer of the gods bucket with its own register block (the wiring spec's Sarlacc footnote pattern) |
| **Nine-claimant ship — the satiation inputs** | every god's (a) ambient channel wired | `mandrake.rm.ninefold` has 5 hooks (birth, deconstruct, repair, mental break, research). **Missing: battle (Sh'kaar), trade completed (Mob'Unloo), launch/rooted clock (Ta'Baa), coupling (Oomo — birth only), ambush-from-cover / unseen (Ishko), droid online (Ohm), scrapping-the-REPAIRABLE (Rekko — deconstruct fires on everything)** | Part 2's recorder supplies battle; add `TradeDeal.TryExecute` postfix, a launch/rooted tick, `Lovin` job postfix, a fog/unseen check at raid close, Droidworks' power-on signal, and `ListerBuildingsRepairable` membership at deconstruct — seven small patches, one item |
| **First-contact chains** (nine unveilings, five beats each, signature kits) | nine scripted incident chains + toll sounds + light palettes + letter liveries | **nothing built**; sounds and letter defs unauthored | one `RUT_FirstContact` IncidentDef per god gated on Ninefold band + a `veiled` flag; kits are SoundDefs + a hull-light Comp — after the inputs above exist, or the chains fire on nothing |
| **Boons and curses matrix** (extreme-band outcomes as opportunity/mood/narration) | a per-god effect table keyed on band | Ninefold tracks bands; **no effect layer** | `RUT_GodEffectDef` rows (thought / incident-queue bias / letter) run by a Ninefold band-change signal; §19.5-legal by def shape (no item field exists) |
| **The pantheon-wide actuator seizure / restraining bolts on the ship** | a starved front god seizes doors/lights; bolts as the clan's answer | **nothing** | v2; the hull-light Comp above is the substrate |
| **Succession clock** (Nekko Vok ages; harsh covenant; active-clan cap 5–7; overflow fosters out; honourable exile of the spent) | an active-roster cap with a foster-out verb and an exile rite | `vanillaexpanded.outposts` covers "foster out" as a place; **no cap, no exile rite** | `RUT_ClanCovenant`: a soft cap thought (over-cap → Ta'Baa/Oomo mood pressure) + one Ideology ritual "the Unburdening" that moves a pawn to an outpost with honour |
| **Love-gate** (the clan does not recruit; membership by romance; slaves naturalise through love) | recruitment blocked; a slave→colonist route gated on a romantic relation | Romance/Intimacy mods live; `mandrake.rsw.jawarules` scope unverified; **no gate** | `RUT_LoveGate`: a Harmony guard on recruit/emancipate that requires a Lover/Spouse relation with a clan member for non-hatched pawns; one ritual "the Taking-In" as the ceremony |
| **The mood economy** (any Jawa's death grieves the clan — even an enemy's — every Jawa acquired is a celebration) | bespoke ThoughtDefs keyed on xenotype | **hand-authored work still owed** | four ThoughtDefs on `MandrakeJawa` death/acquire with scaled stages; no mechanism gap, just authoring |
| **Cold Nursery** (eggs ruin above 32 °C) | temperature-gated egg viability | `mandrake.rut.birthhatchdemo` — a DEMO | promote the demo's ruin rule to the real hatch pipeline; verify the 32 °C constant is read, not hard-coded twice |
| **Droid-theft heist** (secret of manufacture stolen from an enclave, one-time unlock, Griz's arc) | a quest whose reward is a research unlock held at a hostile site | `com.makeitso.configurabletechprints` is live (techprint gating); Droidworks platform in build | the secret IS a techprint item placed at one Enclave settlement via Inhabited stock; the quest is "The Claim" shape with a settlement target |
| **"The Claim" v1 quest** (wreck, timer, race) | a race-to-a-wreck quest | `mandrake.rm.salvageclaim` + `mandrake.rm.strandedquest` exist — status of the timer/race unverified | verify both play end-to-end on a quicktest; if the RACE (a rival caravan walking) is missing, that is the gap |
| **Strangers are situations** | joiners stay on; enslave or love-gate | vanilla + slavery mods — covered | none |
| **Tusken water raid** (steal-and-leave) | a raid strategy that takes water and leaves | vanilla `StealThenLeave`-family strategies exist; **water as a steal target does not** | v2 as ruled; Part 2's `attackTargets` = water containers is the one-liner when the time comes |
| **Blackstar truce token** (free a Named Hunter — the only lever on a permanent enemy) | remembering WHICH Blackstar pawn was captured and freed, and a goodwill route on a `permanentEnemy` | **nothing** | the roster's `NAMED_HUNTER` role + Part 2 rule 4's exchange letter; the "truce" is a faction-wide raid-cooldown flag, not goodwill (vanilla forbids goodwill on permanent enemies) |
| **Hutt tribute demands** | pay-or-raid extortion | `geojak.tributedemand` + `leo.raidprotectionfee` — covered twice; **pick one** | keep Tribute Demand (faction-appropriate forces, arrival modes); cut Raid Protection Fee via Cherry Picker to avoid two extortion letters a season |
| **Shop CUSTOMER layer** (visitors bring broken droids) | a quest pack on top of Droidworks | **nothing**; ruled "pack on top" | after Droidworks lands; Inhabited cast pawns are the customers |
| **Inhabited** (named residents the world remembers) | built | `mandrake.rm.inhabited` + `rut.inhabited` — v1 code, casts authored | none; it is the substrate Parts 1–2 lean on |
| **Win path — grand coalition** | inter-faction diplomacy the player can broker | `mlie.morefactioninteraction` (partial: faction events, no player-brokered alliance) | v2 as ruled; note MFI as the base, not a new mod |
| **Win path — Hutt ledger** | a debt ledger with the Hutts that can be paid down | **nothing beyond goodwill** | v2; Mob'Unloo's ledger and the Hutt's are the same number — one `RUT_Ledger` GameComponent when the time comes |
| **Narrator voice in v1** (pre-authored letters, "Previously on…" recap) | letter corpus + a per-load recap | `narrator_corpus/` exists; Oracle spike on the minimal list only; **no recap consumer** | promote Oracle to the live list; the recap is the cheapest consumer in the roster and needs no LLM to ship its baseline |
| **Sarlacc, They! ant nests, Force powers, water currency** | v2 gravity wells | v2 by ruling | none here |

### The five most critical gaps, in order

1. **The vault thaw quest family** — six vault maps exist as layouts and NOTHING
   makes them play; the reversal, the sleepers, the claim-conflict and the
   Reclamation all hang off it.
2. **Ninefold's missing inputs** — four gods have no ambient channel at all
   (Sh'kaar, Mob'Unloo, Ta'Baa, Ohm), so the first-contact chains, the
   boons/curses matrix and Part 2's god rules would fire on a number that never
   moves. Seven small patches; one item.
3. **The pursuit's dark-tile pause** — stated as the core loop's rule, unverified
   in the ported ScenPart; if absent, the "decide what to leave behind" rhythm
   does not exist yet.
4. **A memory of people** — the Reclamation, the Blackstar truce, the woken
   claim, recurring villains and the Testament all need the same thing: a
   persistent roster of encountered NPCs. Part 1's `GameComponent_OldFriends`
   is that roster; it is the one piece of infrastructure four arcs share.
5. **The love-gate and the covenant cap** — the clan's two defining social
   rules ("does not recruit", "5–7 aboard") have no enforcement, so a normal
   RimWorld colony can still grow out of the fiction in a season.

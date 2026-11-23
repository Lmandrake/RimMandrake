---
name: rimworld-crew-and-nemesis-events
description: Design and build RimWorld 1.6 events about PEOPLE for a small fixed crew — who may join (a stranger, a castaway, a relative, a bought slave, a quest reward), who is taken (a demanded or kidnapped colonist), and who comes back (an escaped raider who returns named, remembers who wounded him and counters the colony's defences; a faction that retaliates for a razed camp), built on our GameComponent_OldFriends roster. Covers keeping headcount honest (populationEffect, rootIncreasesPopulation, population intent, slaves and quest lodgers in threat points), recruit verbs with a shown chance and a reason for every refusal, keeping an off-map pawn alive (world-pawn pinning, re-pin on every exit because spawning unpins, cap and release), injecting the SAME pawn back into a raid, return timers and decaying return chance, letters that read the history back, and save/load traps. Use whenever someone wants a recruit/join/rescue/kidnap/ransom/slave event, a nemesis, a recurring villain or rival, a named NPC who remembers, a "they come for their own" or retaliation raid, or asks how OldFriends could drive raids; and when a remembered pawn vanished after a save, a joiner event ignores the crew cap, or the world-pawn list keeps growing. For incident plumbing in general use rimworld-custom-incidents; for QuestScriptDef authoring use rimworld-quests.
---

# Crew and nemesis events

The crew starts as six fixed founders. The crew stays between 3 and 8 people. So every event about people is
an event about *that number* and about *names*.

The lessons come from four mods: We Are United, More Slaves, Rimesis and Tribute Demand. Our own quest RM_Stranded is
the fifth source. The owner retired We Are United, More Slaves and Rimesis. Tribute Demand stays.

- The study and its evidence: `design/RimMandrake/event_quest_wisdom.md` (§2.7 is Rimesis; §2.9-2.12 are the crew mods
  and our quest).
- Engine plumbing (how an incident fires): the skill `rimworld-custom-incidents`.
- Corrected lines and the evidence for each correction: `references/history.md`.

VERIFIED means that someone checked the claim against the decompiled 1.6 source through RimSage. UNVERIFIED means that
nobody checked the claim.

## 1. Headcount is a gate you must opt into

Population intent is the number by which the storyteller makes joiners rarer as the crew grows.

- **Incidents.** If an `IncidentDef` adds a person, set its `populationEffect` (IncreaseHard, IncreaseMedium or
  IncreaseEasy). If you leave `populationEffect` unset, population intent never sees the incident. The intent factor of
  Randy is 1.0 at 4 colonists, 0.35 at 7 and 0 at 11. The floor of the chance factor is 0.2.
- **Quests.** If a `QuestScriptDef` can end with a new colonist, set `rootIncreasesPopulation`. Then
  `NaturalRandomQuestChooser` puts the quest in the population pool. The survivor in RM_Stranded can be recruited, but
  RM_Stranded does not set `rootIncreasesPopulation`. Before RM_Stranded ships, decide: set the flag, or close the
  recruit branch.
- **Traders.** A stock generator that sells people keeps three vanilla checks: `respectPopulationIntent`, the ideology
  check and the temporary-faction check. More Slaves dropped all three.
- **Threat points.** Free colonists count fully, slaves count ×0.75, and quest lodgers do not count (VERIFIED). So a
  guest does not make raids bigger. A bought slave makes raids a little bigger.
- **Quest rewards are a third path.** Vanilla reward generation can offer a pawn by population intent. Vanilla can do
  that even when the root of the quest does not set `rootIncreasesPopulation` (VERIFIED). A hard crew cap needs its own
  gate on this path. The best Harmony target for that gate is UNVERIFIED.
- **Who may join.** The owner answered card C07 (crew growth) on 2026-10-10. He retired We Are United and More Slaves. He
  asked for our own custom quests that do the same, so a quest of ours may add a person. Our RM_Stranded stays on the mod list; no confirmation
  of his about RM_Stranded is on record. Build the crew-growth gate, and each join path behind it, as a setting. Then a later
  answer changes a setting and needs no rewrite.

## 2. Joining: make it an earned, readable verb

Copy the shape of We Are United, in this order:

1. **A float-menu verb.** In 1.6, use a `FloatMenuOptionProvider` or a narrow patch. Do not put a comp on every pawn.
2. **A validator.** The validator **returns a reason string for every refusal**.
3. **A JobDriver.** The recruiter goes to the target, waits with a progress bar, and then rolls.
4. **The vanilla result.** Call `InteractionWorker_RecruitAttempt.DoRecruit`. Then the letter, the thought, the tale and
   the `Recruited` signal of the quest all come free.

Rules for the roll:

- Show the chance to the player.
- Derive the chance from relations, opinion and Social skill.
- Clamp the number that you display.
- Keep our own cooldown in a component. Do not borrow the animal-training timer.
- Restrict the targets by the story: kin, or pawns with no faction. This limit also stops the poaching of faction pawns.

## 3. Losing someone: price it, and make it recoverable

Tribute Demand can demand a colonist. The person demand has weight 0.15 of 1.8, about 8% of rolls. A colonist is a
candidate only when there are two or more; a prisoner is always a candidate. Tribute Demand hands the person to the
`kidnapped` tracker of the faction.

On a crew of six, the loss of one person is a major event of the campaign. So make the loss deliberate:

- Use our own demand list.
- Send a letter that names the person who is taken.
- Give the player a rescue path.

Our `GameComponent_OldFriends` records the *kidnapper* when a raider carries a colonist off (`Patch_ColonistKidnapped`).
The summary of that record names the victim. The patch records nothing when the kidnapper is null. Tribute Demand calls
`Kidnap(pawn, null)`, and so does the vanilla caravan demand. The `kidnapped` tracker holds the person, but
OldFriends has no entry and vanilla sends no kidnap letter. A demand of ours has two routes:

- Pass a named envoy with a faction as the kidnapper. Then the patch records the envoy, and vanilla sends its letter. The
  patch does not pin the envoy, so pin him when he is off the map.
- Keep the null kidnapper. Then send our own letter. If OldFriends must remember the demander, call `RecordEncounter` with
  the envoy or the faction leader. A faction can have no leader. Never pass null or the victim.

## 4. The one who got away (nemesis recipe, cheapest version)

Rimesis is 248 files. About five fields and three hooks make the story.

1. **Promote on survival, not at random.** Promote a raider who reaches the map edge after his group lost half its
   members, with no colonist near. That raider becomes known. Promote at most one raider per raid.
2. **Remember a few facts.** Keep the pawn reference, the faction, deathCount and returnCount, and
   eligibleReturnTick. Keep the last killer, the weapon and the lost part. Cap the events per record. Never evict the
   founding event.
3. **Keep him alive off-map.**
   - When he first leaves, call `PassToWorld(p, PawnDiscardDecideMode.KeepForever)`.
   - If he is already a world pawn, call `Find.WorldPawns.ForcefullyKeptPawns.Add(p)`.
   - Both calls fill one set, and vanilla saves that set. `WorldPawnPinning.PinForever` in OldFriends does exactly this.
   - **Spawning him clears the pin** (`WorldPawns.RemovePawn`). His next `ExitMap` passes him back in `Decide` mode. So
     re-pin him on every exit.
   - When the roster forgets him, release him with `ForcefullyKeptPawns.Remove(p)`. Otherwise the world-pawn list grows
     forever.
4. **Bring the same Pawn back.**
   - `PawnGroupMakerUtility.GeneratePawns` is a C# iterator. About 40 places call the iterator (~40): raids, but also
     sites, settlements, ambushes and quests.
   - Postfix `GeneratePawns` with `ref IEnumerable<Pawn> __result`. Wrap the result in our own iterator.
   - Set a flag around `IncidentWorker_Raid.TryGenerateRaidInfo` (prefix + finalizer). Inject only while the flag is on.
   - Inside the wrapper, remove him from world pawns once, because some callers enumerate twice.
   - Yield the *same object*. Then his identity, scars and relations persist.
   - Return him only if his faction is hostile, he is not captured, and his timer passed.
   - Rotate by returnCount: the lowest count returns first. Return at most one or two per raid.
5. **Grow qualitatively.** Pick a counter to what the colony actually has. Examples: EMP against turrets, a sapper
   against walls, a grudge against the colonist who shot him. Do not inflate skills or points. For the same reason,
   the ordinary return multiplier of Rimesis for points is 1.0.
6. **Letter the history back**: "returns, scarred by Aldo's rifle in the left leg." The player reads their own story
   back: that is the payoff. A silent return is wasted.
7. **Death is final eventually.** Let the return chance decay. Then make the death permanent, with its own letter.
   Infinite resurrection becomes stat inflation by other means.

## 5. Traps

- 🔴 **Pawn references that are not Scribed** come back null after load. Examples: the field `cause` of Space Worms, and
  any pawn that a lambda holds. Put every pawn that you need later in `Scribe_References` on a component. Make the
  world keep the pawn itself: pin the pawn (§4 step 3).
- 🔴 **A pawn passed to world with default discard mode is garbage-collectable.** Spawning a pinned pawn also unpins the
  pawn. Vanilla passes fleeing raiders in `Decide` mode (VERIFIED `Pawn.ExitMap`). Pin the pawn at the moment you decide
  to keep the pawn. Pin again at every exit.
- **World pawns heal off-map.** The game ticks, auto-tends and mothballs world pawns. A wound will be gone by the return. So
  "scarred" must read a permanent injury or our own stored record.
- **Moving a dead pawn into world pawns** is the resurrection trick of Rimesis. The trick confuses every other mod that
  scans the dead. Prefer the fresh return of a raider whom you kept alive.
  - Vanilla `ResurrectionUtility` takes only a dead pawn (VERIFIED `TryResurrect`). So if a dead raider must return,
    resurrect him first, with `ResurrectionParams` `dontSpawn` set. Then pass the living pawn to the world.
    Without `dontSpawn`, the pawn spawns where the corpse lies, and `PassToWorld` refuses a spawned pawn. Our mods have
    not run this order.
- **Iterator-wrapping `GeneratePawns`** collides with any other mod that does the same. Keep one owner of raid
  composition: ours.
- **Unbounded rosters** grow with every raider, every encounter and every karma event. Cap the roster and prune by
  notability, as OldFriends does (24 living entries by default).
- **Joiners that bypass the gate** of §1 skip population intent and the crew cap.
- **Statics.** A nemesis plan that a static dictionary caches survives quit-to-menu into the next save.

## 6. Pointers

- `references/nemesis_lifecycle.md` — what OldFriends already has, and the build order for the return. The order is
  eligibility, selection, injection, counter-play, letter, death, retaliation. The file ends with the save checklist. The
  numbers of Rimesis itself are in the study, §2.7.
- `references/crew_mechanisms.md` — the validator and the chance formula of We Are United, the stock generator of More
  Slaves. That file also holds the demand roll of Tribute Demand and the priced branches of RM_Stranded.

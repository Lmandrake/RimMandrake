---
name: rimworld-crew-and-nemesis-events
description: Design and build RimWorld 1.6 events about PEOPLE for a small fixed crew — who may join (a stranger, a castaway, a relative, a bought slave), who is taken (a demanded or kidnapped colonist), and who comes back (an escaped raider who returns named, remembers who wounded him and counters the colony's defences; a faction that retaliates for a razed camp). Distilled from studying We Are United, More Slaves, Rimesis, Tribute Demand and our own RM_Stranded quest before they retire, and from our GameComponent_OldFriends roster. Covers keeping headcount honest (populationEffect, rootIncreasesPopulation, population intent, slaves and quest lodgers in threat points), recruit verbs with a shown chance and a reason for every refusal, keeping an off-map pawn alive (world-pawn pinning, re-pin on load, cap and release), injecting the SAME pawn back into a raid, return timers and decaying return chance, letters that read the history back, and save/load traps. Use whenever someone wants a recruit/join/rescue/kidnap/ransom/slave event, a recurring villain or rival, a named NPC who remembers, a "they come for their own" or retaliation raid, or asks how OldFriends could drive raids; and when a remembered pawn vanished after a save, a joiner event ignores the crew cap, or the world-pawn list keeps growing. For incident plumbing in general use rimworld-custom-incidents; for QuestScriptDef authoring use rimworld-quests.
---

# Crew and nemesis events

The crew is six fixed founders, kept between 3 and 8. Every event about people is
therefore an event about *that number* and about *names*. Study and evidence:
`design/RimMandrake/event_quest_wisdom.md` (§2.7 Rimesis, §2.9-2.12 the crew mods and
our quest). Engine plumbing: `rimworld-custom-incidents`.

## 1. Headcount is a gate you must opt into

- An `IncidentDef` that adds a person sets `populationEffect` (IncreaseHard/Medium/Easy).
  Without it, the storyteller's population intent (Randy: 1.0 at 4 colonists, 0.35 at 7,
  0 at 11, floor 0.2) never sees it.
- A `QuestScriptDef` that can end with a new colonist sets `rootIncreasesPopulation`, so
  `NaturalRandomQuestChooser` puts it in the population pool. RM_Stranded can be recruited
  and does not set it: decide which before shipping.
- A stock generator that sells people keeps vanilla's `respectPopulationIntent` and its
  ideology and temporary-faction checks (More Slaves dropped all three).
- Threat points: free colonists count fully, slaves ×0.75, quest lodgers not at all
  (VERIFIED). Hosting a guest does not make raids bigger; buying slaves does, a little.
- Whether a person may join at all is an owner ruling (card C07). Build the gate so either
  answer is a setting, not a rewrite.

## 2. Joining: make it an earned, readable verb

The We Are United shape is the one to copy: a float-menu verb (1.6:
`FloatMenuOptionProvider`, or a narrow patch — not a comp on every pawn) → a validator that
**returns a reason string for every refusal** → a JobDriver (go to, wait with a progress bar,
roll) → vanilla `InteractionWorker_RecruitAttempt.DoRecruit` so the letter, thought, tale and
the quest's `Recruited` signal all come free. Show the chance; derive it from relations,
opinion and Social skill; clamp what you display; keep our own cooldown in a component
rather than borrowing the animal-training timer. Restrict targets narratively (kin, or the
factionless), which also stops poaching faction pawns.

## 3. Losing someone: price it, and make it recoverable

Tribute Demand can demand a colonist (15% of rolls when there are two or more) and hands
them to the faction's `kidnapped` tracker. On a crew of six that is a campaign beat, so make
it deliberate: our own demand list, a letter that names who, and a rescue path — our
`GameComponent_OldFriends` already records kidnappings (`Patch_ColonistKidnapped`).

## 4. The one who got away (nemesis recipe, cheapest version)

Rimesis is 248 files; the part that makes the story is about five fields and three hooks.

1. **Promote on survival, not at random.** A raider who reaches the edge after his group
   lost half its members, with no colonist near, becomes known. One promotion per raid.
2. **Remember a few facts**: pawn ref, faction, deathCount/returnCount, last killer + weapon +
   lost part, eligibleReturnTick. Cap events per record and never evict the founding one.
3. **Keep him alive off-map**: `Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever)`
   (what OldFriends uses) or `ForcefullyKeptPawns`; **re-check pins on load**; release pins when
   the roster forgets him, or the world-pawn list grows forever.
4. **Bring the same Pawn back**: a postfix on `PawnGroupMakerUtility.GeneratePawns` for the
   Combat group of that faction, removing him from world pawns and yielding the *same object*
   (identity, scars, relations persist). Gate: hostile faction, not captured, timer passed;
   rotate by returnCount; at most one or two per raid.
5. **Grow qualitatively**: pick a counter to what the colony actually has (EMP against turrets,
   a sapper against walls, a grudge against the colonist who shot him), not skill or point
   inflation. Rimesis's own point factors stay near 1.0 for this reason.
6. **Letter the history back**: "returns, scarred by Aldo's rifle in the left leg." Reading
   your own story is the payoff; a silent return is wasted.
7. **Death is final eventually**: decaying return chance, then a permanent death with its own
   letter. Infinite resurrection becomes stat inflation by other means.

## 5. Traps

- 🔴 **Pawn references that are not Scribed** come back null after load (Space Worms'
  `cause`; any lambda-held pawn). Every pawn you need later is `Scribe_References` on a
  component, and the pawn itself is kept by the world.
- 🔴 **A pawn passed to world with default discard mode is garbage-collectable.** Fleeing
  raiders are passed with the default mode (VERIFIED `Pawn.ExitMap`); pin the ones you mean to
  keep, at the moment you decide.
- **Moving a dead pawn into world pawns** (Rimesis' resurrection trick) confuses every other
  mod that scans the dead; prefer a fresh return or vanilla `ResurrectionUtility` on a pawn
  you kept alive.
- **Iterator-wrapping `GeneratePawns`** collides with any other mod that does the same; keep
  one owner of raid composition (ours).
- **Unbounded rosters** (every raider, every encounter, karma events): cap and prune by
  notability, as OldFriends does (24 living entries by default).
- **Joiners that bypass the gate** (above). And statics: a nemesis plan cached in a static
  dictionary survives quit-to-menu into the next save.

## 6. Pointers

- `references/nemesis_lifecycle.md` — what OldFriends already has, and the build order for
  the return (eligibility, selection, injection, counter-play, letter, death, retaliation)
  with its save checklist. Rimesis' own numbers are in the study doc §2.7.
- `references/crew_mechanisms.md` — We Are United's validator and chance formula, More
  Slaves' stock generator, Tribute Demand's demand roll, RM_Stranded's priced branches.

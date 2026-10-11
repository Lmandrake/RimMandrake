# Crew mechanisms: who joins, who is sold, who is taken

Evidence and numbers: `design/RimMandrake/event_quest_wisdom.md` §2.9 (We Are United), §2.10
(More Slaves), §2.11 (RM_Stranded), §2.12 (Tribute Demand). This file is the reusable shape of
each. Sketches; re-read every engine type named.

## 1. A social verb with a shown chance (We Are United, rebuilt)

- **Entry point.** A 1.6 `FloatMenuOptionProvider` subclass (VERIFIED abstract class: override
  `Drafted`, `Undrafted`, `Multiselect`, then `GetSingleOptionFor(Pawn clickedPawn, FloatMenuContext context)`).
  We Are United instead adds a `ThingComp` to every pawn via `ThingDef[@Name="BasePawn"]/comps`;
  the provider is narrower and costs nothing on non-pawns.
- **Validator returns a reason for every refusal** and the option is shown disabled with it.
  WAU's checks are a good list: recruiter is ours and not a slave; target not ours; target is kin
  (`relations.RelatedPawns`) or factionless; reservable; no enemy within 40 cells; both can talk
  and do social work; recruitable; not on cooldown; not hostile.
- **JobDriver**: go to the target, force the target to wait, wait with a progress bar, roll.
- **Chance** (WAU): `relations (importance / max importance × 0.25, summed) + opinion/100 × 0.5 +
  Social/20 × 0.5`, clamped. Show the clamped value in a mote and the breakdown in the tooltip.
- **Consequence**: `InteractionWorker_RecruitAttempt.DoRecruit(recruiter, target, ...)` gives the
  letter, thought, tale, record and the quest `Recruited` signal (VERIFIED by the study).
- **Cooldown**: our own per-pawn next-allowed tick in a Scribed component (WAU borrows the
  animal-training timer, which other interactions reset).
- **Crew-size gate**: refuse with a reason when the crew is at the configured maximum.

## 2. Selling people (More Slaves, rebuilt)

Subclass `StockGenerator` for one trader kind of ours; insert it with a `PatchOperationAdd` scoped
to that `TraderKindDef` defName; keep vanilla's three checks that More Slaves dropped
(`respectPopulationIntent` against `StorytellerUtilityPopulation.PopulationIntent`, the faction's
ideology approving slavery, and excluding temporary factions). Read the count from one place.
Buying adds threat points at ×0.75 per slave (VERIFIED) — small, but not zero.

## 3. A person to shelter (RM_Stranded)

The quest is the template for "a person, a clock, a priced choice":
`QuestNode_GeneratePawn addToList lodgers` → `QuestNode_PawnsArrive joinPlayer=false` →
`QuestNode_LeaveOnCleanup` → `QuestNode_Delay isQuestTimeout` → success siblings before the End →
one `QuestNode_Signal` per `lodgers.Recruited/.Enslaved/.Arrested/.Destroyed/.LeftMap` with its
own letter and goodwill price and a `HistoryEventDef` reason. Quest lodgers do not add threat
points. If the recruit branch stays, set `rootIncreasesPopulation`.

## 4. A person demanded (Tribute Demand)

Its demand roll (of weight 1.8): 0.15 colonist-or-prisoner (only with ≥2 free colonists), 0.15
animals (up to 60%, priciest first), else items worth 5-20% of colony value clamped 300-35,000,
chosen by `(value/mass)^2`. Giving a person calls `faction.kidnapped.Kidnap(pawn, null)`. For
us: build our own demand list (scarce goods first), make "a person" an explicit authored option,
and pair it with a rescue path — OldFriends' `Patch_ColonistKidnapped` already records the
event, and a rescue `QuestScriptDef` can target the faction's authored site.

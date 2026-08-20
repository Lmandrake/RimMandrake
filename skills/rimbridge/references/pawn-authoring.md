# Pawn authoring — the 14 deep-edit tools

```
READ     pawn_get                      ⬅ reports levelRaw AND levelEffective
IDENTITY set_pawn_identity · set_pawn_backstory · pawn_traits · set_pawn_skill
         set_pawn_appearance
LOADOUT  pawn_gear · pawn_health · pawn_need
ALLEGIANCE set_pawn_faction · set_pawn_ideo · pawn_relations · pawn_genes · set_pawn_age
```

## 🔴 NOTES DO NOT EXIST

There is **no free-text note field** on `Pawn` or any `Pawn_*Tracker` in 1.6/Odyssey.
`Pawn` is not `IRenameable`, there is no `Dialog_Note`, and `Pawn_RecordsTracker` is a
numeric `DefMap<RecordDef,float>`.

**The only writable free text is `pawn.story.Title`.** Anything richer must be storage we
build (a `GameComponent` keyed by pawn id). **Do not fake it.**

## The traps, in the order they will bite

Full catalogue in `silent-failures.md`. The pawn-specific ones:

1. **Backstory refreshes NOTHING** — four calls needed, and the game's own debug tool runs
   one of them.
2. **`GainTrait` checks no conflicts and there is no trait cap** — `pawn_traits` refuses by
   default and takes `force=true` for a deliberate stack.
3. **`SkillRecord.Level` adds aptitudes** — validate against `levelRaw`.
4. **`AddEquipment` no-ops on an occupied primary slot** — `pawn_gear` calls `MakeRoomFor`
   and reports what it displaced.
5. **`DebugSetAge` is FORWARD-ONLY** — `set_pawn_age` refuses a backwards age and explains;
   `allowBackwards=true` uses the raw setter and says plainly that **every
   `BirthdayBiological` is skipped**.
6. **Age changes do not fix body type** — the tool reports `bodyTypeMismatch`.
7. **Social thoughts need an `otherPawn`** or are dropped silently.
8. **Only 9 of 41 relations are storable** — `Sibling` and `Child` are *implied*.

## Things that ARE safe

* ✅ **`pawn.SetFaction`** is self-refreshing and does a great deal: lord `Notify_PawnLost`,
  `jobs.StopAll`, drafter, guest status, mapPawns re/de-registration, needs, relations, the
  colonist bar, surgery bills, `ChangeKind`. Prefer `RecruitUtility.Recruit` for
  prisoner/guest → player: it also unlocks apparel and replaces royal titles.
* ✅ **`GainTrait` / `RemoveTrait`** self-refresh work types, skill disables, aptitudes,
  situational thoughts, granted abilities and graphics.
* ✅ **`genes.AddGene` / `RemoveGene`** self-refresh everything via `Notify_GenesChanged`.
* ✅ **`apparel.Wear`** enforces `CanWearTogether`, drops conflicts and refreshes graphics.
* ⭐ **A bionic needs no RecipeDef and no surgeon**: `health.RestorePart(part)` then
  `health.AddHediff(def, part)` — what `Recipe_InstallArtificialBodyPart` does with a null
  billDoer.

## Things that are destructive

* 🔴 **`health.RestorePart` is RECURSIVE** into child parts, wipes their hediffs and does
  not drop what it removed. `pawn_health` gates it behind `confirmDestructive=true`.
* ⚠️ **`SetIdeo` randomises certainty**, unclaims ideo-forbidden beds, may strip spouse and
  bond relations, and can send a letter. `Certainty`'s setter is private — use
  `OffsetCertainty`.

## Making pawns that LIVE somewhere

`LordMaker.MakeNewLord(faction, new LordJob_DefendPoint(centre, wanderR, defendR,
isCaravanSendable:false, addFleeToil:false), map, pawns)` — one toil, **zero transitions**,
so nothing can turn them hostile on their own. They already eat, sleep, socialise and do
work jobs near the point.

⛔ **Do NOT use `LordJob_DefendBase`** — a `Trigger_ChanceOnTickInterval(2500, 0.03f)` turns
it into an assault unprompted.
⛔ **A duty without a lord is inert** (`ThinkNode_ConditionalHasLordDuty`).
🔴 **Farming is blocked three ways** for non-colonists. Full analysis and 36 scene templates:
`design/Jawa/bridge/LIVING_NPC_TEMPLATES.md`.

## Psychic, pregnancy, mental states, romance and social events

`pawn_psychic` · `pawn_pregnancy` · `pawn_mental` · `pawn_romance` ·
`social_list` · `social_gathering_start` · `social_marry` · `ritual_start` · `social_cancel`

* 🔴 **`ChangePsylinkLevel` never reads its offset on the first call** — it creates the
  hediff at level 1 and returns. One call can only ever reach 1.
* 🔴 **Gestation IS the hediff Severity.** 1.0 begins labour next tick.
* 🔴 **`TryStartMentalState` returns false silently.** `BerserkPermanent` never recovers alone.
* 🔴 **Opinion is purely computed** — a bare relation change produces **no thought**. A
  memory is the only lever. Proven: breakup left opinion at 70/**−5**.
* 🔴 **`MarriageCeremonyUtility.Married` ≠ the ceremony.** Married() is instant and skips the
  party; the ceremony calls it from inside its own job. `TryStartMarriageCeremony`
  **ignores its second argument** — the **Fiance** relation is mandatory.
* 🔴 **Funerals are NOT Ideology-only** — `FuneralBase` is `<classic>true</classic>`.
* ⭐ **Gathering attendees self-join.** The lord starts with zero pawns; never assign them.
* ⚠️ A quicktest can spawn mid-assault, which blocks every social event.

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
- **`Outputs\Thoughts` is global, not per-pawn.** The bridge debug action `Outputs\Thoughts` prints a GLOBAL ThoughtDef reference table (defName/stages/mood values); selecting a different pawn first does not change it. No bridge tool exposes one pawn's live situational-thought state, so verify mood mechanisms (e.g. a gene's `nullifyingGenes`) from engine source: `Thought.MoodOffset()` checks `ThoughtUtility.ThoughtNullified()` for every `Thought` subclass.
- **`jawa/pawn_health remove` with `bodyPart`** can answer "no hediff on Leg" for a hediff listed on Leg; removing by def alone worked.
- **A spawned test "worker" can be incapable of the work type.** `jawa/set_work_priority` answers `success=false` for a disabled type, and a script that ignores it reads an idle pawn as a MOD FAIL: check the result and respawn. It is also a no-op for the number when `Find.PlaySettings.useWorkPriorities` is off (a fresh debug map): every active work type reads 3, so "Hauling 0" does NOT turn the work off. Read the reply's `manualPrioritiesOn` and treat a row depending on work being off as unproven until a tool enables manual priorities.
- **`jawa/pawn_refresh_needs` fills NOTHING** (it only re-walks which needs exist): a "calm the colony" step built on it let the quicktest colony starve through a day. Set levels with `jawa/pawn_need action=need need=Food level=1` (and Rest/Joy/Mood...).
- **`jawa/set_draft` on a colony mech says "no overseer" as a GUESS** whenever `MechanitorUtility.CanDraftMech` refuses (e.g. out of command range): read the overseer from `jawa/inspect_string` ("Overseer: <name>") or the mechanitor's right-click ("Disconnect from"). `jawa/ordered_job jobDef=ControlMech targetAId=<mech>` on a `Mechanitor_Basic` is a working route to a controlled colony mech.
- **`jawa/spawn_pawn` of an animal with no `faction` arg spawned it into faction Mechanoid (hostile).** Pass `faction="none"` for a wild animal. And a bridge print truncated at N chars then grepped reads a pawn as ABSENT: list pawns through a full-list reader (`live_batch tools/ids.py`), never a truncated dump.
- **Apparel stats are quality-scaled.** An apparel stat a hazard clock reads (`HazardTargeting.SumApparelStat` -> `GetStatValue`) is scaled by Core's `StatPart_Quality` for every `ArmorRating_*` stat (awful x0.60 .. legendary x1.80). Size a "floor at protection 1.0" garment by the AWFUL factor (base >= 1/0.6), not the def number, or a poor coat silently runs 3-5x faster. `jawa/pawn_gear` wear is quality-rolled unless `quality=` is passed.

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
- **HealthScale postfix check without a max-HP tool.** Pain is a vanilla HealthScale consumer (`Hediff_Injury.PainOffset` divides by it): same injuries, swell on vs off, `painTotal` ratio = scale x any stage `painFactor` (measured x5.97 = 3 x 1/0.5 for the dhoggur swell). `Mass` and `CarryingCapacity` in `jawa/pawn_stats` prove a BodySize postfix the same way.

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
- **A pawn spawned with `jawa/spawn_pawn` for a non-player faction has no lord**, and its first job is Goto the map edge: a "witness" leaves sight range within ~200 ticks. Hold it with `jawa/lord_defend_spawn pawns=<ids> point=<cell> wanderRadius=2 addFleeToil=false`. Strays from an earlier attempt keep walking through the next scene: sweep for victim-faction pawns before a no-witness control.

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

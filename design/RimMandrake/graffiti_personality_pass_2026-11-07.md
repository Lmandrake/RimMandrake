# Graffiti personality pass, 2026-11-07

Asked for by the owner on 2026-11-07, design only. His words:

> "Take a moment to consider the many personality types and how this would interact with them. Sociopaths wouldn't feel any mood change or care, while sensitive types might get extra mood debuffs or buffs as results. Clean freaks might get extra debuffs and have a mood break that makes them compulsively clean graffitti marks. Do a design pass entirely focused on all of the existing personality traits and quirks and types and how they should interact with this mod."
He chose "Scale it with temper" for the confront fight chance, and asked that art skill go into a mark's effect (quoted in full in `ralph/PROMPT.md`).
Every number marked (P) is a proposal for the loop to tune in play. Other numbers were read from the frozen official dump (OFFICIAL-2026-08-29, game 1.6.4871, 584 mods) or the 1.6 decompile, or from the Graffiti code at commit `9ebbed0ed4`.

## 1. The result in six lines

- One table in XML, read by one helper, gives each person their own temperament. Almost nothing here is per-trait code.
- Psychopaths feel nothing, answer nothing, and will clean anything.
- There is no vanilla "sensitive" or "clean freak". Sensitive becomes Nervous and Volatile. Clean freak becomes Neurotic, and only Very Neurotic breaks over it. Mods fill in the literal versions where installed.
- Today's confront chance reads the wrong person's temper. It is rolled on the painter's traits. The fix also brings the rate down from 0.75.
- Art skill uses vanilla's own quality roll. Craft and meaning are two separate thoughts, so a brilliant slander hurts and pleases at once, and the pawn's needs tab shows both.
- BUILD NOW is 17 files: 3 new and 14 edited.

## 2. His words, and which real thing each one means

Measured: official TraitDefs are Core 43, Anomaly 6, Biotech 2; Royalty, Ideology and Odyssey have none. Mods add 215 more.

| His word | Real thing | Fit | Gap |
|---|---|---|---|
| Sociopath | `Psychopath` ("no empathy"), plus `Inhumanized` hediff (Anomaly) | exact | none |
| Sensitive | `Nerves` -1 nervous, -2 volatile | closest | **No vanilla trait means emotionally sensitive.** `PsychicSensitivity` shares only the word; it is about psychic power, so it stays out. `TorturedArtist` is a partial match for art. Optional mods: Hypersensitive (`Megachuv`, businburg.businfeatures), `VTE_Anxious` |
| Clean freak | `Neurotic` 1 neurotic, 2 very neurotic ("likes to have things squared away") | closest | **No vanilla trait and no official precept means cleanliness.** Optional mods are the literal version: `VTE_Neat`, `RT_Tidy`, `Hygienic` 1 and 2 |

Neurotic also raises break risk in vanilla (+.08, +.14 threshold), which suits a person who can break over paint.

## 3. What already happens (do not rebuild)

| Trait or state | Today, in `RM_GraffitiKernel` and `GraffitiSocial` |
|---|---|
| Kind | Refuses to paint mockery or insult. As subject, shrugs off (+2). As witness, disapproves. Never mock-paints an enemy |
| Psychopath | Skips memorial, jest and beauty readings only. **Still** feels mockery, tribute, sacred signs, tags, unease, the enemy claim and destroyed work. This is the gap against his anchor |
| Abrasive, Bloodlust, Brawler | The `hot` flag: more confronts and answers |
| Violent-disabled | Cannot confront |
| Artistic 5+, not Artistic-disabled | `goodHand`, may answer with a reply |
| Lover, friend (20+), enemy (-15 or below), hated (-30 or below) | Decide the reaction, from opinion rather than traits. So `DislikesMen`, `DislikesWomen`, `AnnoyingVoice`, `CreepyBreathing`, `Beauty` and the rest already reach reactions through opinion |
| Ideoligion | Devotion reads as same or different only |

## 4. The table: how it works

New def `RM_GraffitiTemperamentDef` holds rows keyed by a trait and degree, a gene, a hediff or a precept. Keys are strings resolved once at load with `GetNamedSilentFail`, so a row for an absent mod is inert and needs no patch. A selftest checks every name and degree against the frozen dump, because a silent miss must not stay a typo. Suppressed traits and inactive genes count for nothing.

| Field | Default | Meaning | Clamp after multiplying all rows (P) |
|---|---|---|---|
| `numb` | false | Feels nothing, never answers, never refuses cleaning | wins over all |
| `bad` | 1 | Multiplies negative meaning thoughts, mood and opinion (mockery, jealousy, offended, enemy tag, destroyed work) | 0 to 1.5 |
| `good` | 1 | Multiplies positive meaning thoughts, mood and opinion (tribute, memorial, jest, sacred sign, friend's tag) | 0 to 1.5 |
| `fine`, `ugly` | 1 | Multiply the two craft thoughts separately (fine art, ugly mark). The table's `craft` column fills both unless it says which | 0 to 1.5 |
| `temper` | 1 | Fight table multiplier, section 7 | 0 to 4 with the vanilla field |
| `paint` | 1 | Multiplies the chance of autonomous painting in `JoyGiver_PaintGraffiti` and `JobGiver_IdleTag`. What gets painted is untouched | 0 to 2 |
| `lean` | none | `scrub`, `reply` or `nothing`: replaces a confront or a deface in `AnswerOf` | |
| `offended` | 1 | Multiplies `Offended` and `Heretic` only. Rows keyed by `IdeoDiversity_*`: Abhorrent 1.5 down to Exalted 0 | 0 to 1.5 |
| `neat` | 0 | 1 is the mess thought; 2 adds the break, section 8 | highest row wins |

So the "reads as" of the brief reduces to numbers on the same reactions: mockery, enemy tag and a hostile sacred sign read through `bad`; tribute, memorial and a friendly sacred sign through `good`; beautiful piece through `fine`; ugly mark through `ugly`.

The route is vanilla's. One helper, `GraffitiTemperament.Give(pawn, thought, other, reach)`, replaces the direct memory calls in `GraffitiSocial`. It builds the memory with `ThoughtMaker`, sets `moodPowerFactor`, scales the `opinionOffset` that `Init` filled in, then submits. Situational thoughts go through the virtual `ThoughtWorker.MoodMultiplier`.

Stack limits need care. At its limit, `Thought_Memory.TryMergeWithExistingMemory` renews the oldest and throws the new one away, factor and stage included (1.6 decompile). So at the limit `Give` keeps the stronger of the two: it removes the weaker and adds the stronger, or lets vanilla renew. `Thought_MemorySocial` never merges; the oldest for that pawn falls off. Numb holds in three places. Every Graffiti ThoughtDef gets `<nullifyingTraits>` Psychopath, the way 96 official thoughts do, and `<nullifyingHediffs>` Inhumanized, so `MemoryThoughtHandler` refuses the memory and situational thoughts stop too. `ReactionOf` returns nothing. `AddGrudge` refuses a numb pawn and drops any grudge they already hold, because `Notify_WentOver` makes grudges without going through `ReactionOf`.

## 5. BUILD NOW rows

Blank means the default. "Answers" means the existing `AnswerOf` table unless stated. Temper shows the table value; `Bloodlust` also carries its vanilla field.

| Trait, degree | bad | good | craft | temper | paint | Answers | Why a player nods |
|---|---|---|---|---|---|---|---|
| `Psychopath` | numb | | | | 0 | Nothing. Never refuses to clean | Paints only by order or in a spree. No empathy, so the wall is just a wall. Others still hate him for what he paints |
| `Inhumanized` (hediff) | numb | | | | 0 | Nothing | Same reason, Anomaly's route |
| `Kind` | | | | .25 | | Lean scrub | Keeps today's behaviour. Would rather clean than shout |
| `Bloodlust` | | | | 1 (field 4) | | Today's | The vanilla field makes it the fight table's top row |
| `Abrasive` | | | | 1.5 | 1.5 | Today's | Says what he thinks, on walls too |
| `Brawler` | | | | 1.5 | | Today's | Settles it with fists |
| `Wimp` | | | | .5 | | Lean scrub | Would rather not be hit |
| `Nerves` 2 iron-willed; 1 steadfast | .7; .85 | | | .6; .8 | | Today's | Hard to rattle; steady |
| `Nerves` -1 nervous | 1.25 | 1.25 | 1.25 | 1.2 | | Today's | **Sensitive anchor.** Feels more both ways |
| `Nerves` -2 volatile | 1.5 | 1.5 | 1.5 | 1.5 | | Today's; counts as hot | **Sensitive anchor.** Everything lands hard, including the good |
| `NaturalMood` 2 sanguine; 1 optimist | .75; .9 | 1.25; 1.1 | | | | Today's | Sees the best; same, gently |
| `NaturalMood` -1 pessimist; -2 depressive | 1.1; 1.25 | .9; .75 | | | | Today's | Takes it badly; takes it worse |
| `Neurotic` 1 | | | .5 on fine art | | | Lean scrub | **Clean freak anchor.** `neat` 1: minds the mess, does not break over it |
| `Neurotic` 2 | 1.1 | | .5 on fine art | | | Lean scrub | **Clean freak anchor.** `neat` 2: the mess and the break |
| `Ascetic` | | | 0 | | | Today's | Vanilla already nullifies `Pretty` and `Ugly` for him. Art leaves him cold; meaning does not |
| `TorturedArtist` | 1.25 | 1.25 | 1.25 | | 1.5 | Lean reply | "Alienated and misunderstood". Answers in paint when he can |
| `Joyous` (Anomaly) | .75 | 1.25 | | | | Today's | Takes things lightly and warms easily |
| `Industriousness` -1 lazy; -2 slothful | | | | | .75; .5 | Today's | Won't bother; really won't bother |

Genes that behave like personality:

| Gene | Row | Why |
|---|---|---|
| `Mood_Sanguine`, `Mood_Optimist`, `Mood_Pessimist`, `Mood_Depressive` | Same as the `NaturalMood` degree | Same temperament by a different route |
| `Aggression_DeadCalm` | No row. Vanilla factor 0 makes the fight impossible | "Never start social fights" |
| `Aggression_Aggressive` (2), `Aggression_HyperAggressive` (3) | No row. Vanilla factor is in the formula; counts as hot from it | Read from the same field |
| `KindInstinct`, `KindInstinct_Astrogene` | No row. They force `Kind` | Inherited |
| `ViolenceDisabled` | No row. Existing check, and vanilla refuses the fight | |
| `RimMandrake_statgene_compliant` (.25), and mod genes with a factor | No row. Vanilla field | Picked up automatically |

Xenotypes need no rows. Measured: nothing on the 12 official xenotypes acts as personality apart from these genes.

Optional mod rows, inert when the mod is absent. Only the literal versions of his two words go in now; the rest of the catalogue is LATER.

| Mod trait (package) | Row | Why |
|---|---|---|
| `VTE_Neat` (vanillaexpanded.vanillatraitsexpanded), `RT_Tidy` (sierra.rt.generaltraits), `Hygienic` 2 germaphobe (dubwise.dubsbadhygiene.lite) | `neat` 2, `fine` .5, lean scrub | The literal clean freak |
| `Hygienic` 1 | `neat` 1, `fine` .5, lean scrub | Likes things clean, stops short of a break |
| `VTE_Anxious`, `Megachuv` | bad 1.25, good 1.25 | The literal sensitive |

## 6. Traits with nothing to add

Inventing effects here would only be noise. These feel a mark like anyone, through opinion when that matters.

| Group | Traits |
|---|---|
| Body, skill, memory, appetite | `Nimble`, `SpeedOffset`, `Tough`, `Delicate`, `BodyMastery`, `Immunity`, `ShootingAccuracy`, `FastLearner`, `SlowLearner`, `TooSmart`, `GreatMemory`, `PerfectMemory`, `Gourmand`, `QuickSleeper`, `NightOwl`, `Cannibal`, `DrugDesire`, all degrees |
| Love | `Gay`, `Bisexual`, `Asexual`. The lover flag already covers them |
| Opinion only | `DislikesMen`, `DislikesWomen`, `AnnoyingVoice`, `CreepyBreathing`, `Beauty` all degrees |
| Beliefs about bodies | `Nudist`, `Transhumanist`, `BodyPurist` |
| Other | `Greedy`, `Masochist` (vanilla ties it to pain, not shame), `Undergrounder`, `Recluse`, `Industriousness` 1 and 2, `PsychicSensitivity` all degrees (psychic, not emotional; see section 2) |
| Own break rules | `Pyromaniac` (only fire breaks) and `VoidFascination` (only liberating entities). `theOnlyAllowedMentalBreaks` already blocks both Graffiti breaks |

Royalty has no traits. Titles only matter as disabled work: a Duke cannot scrub, a rule the answers and the break must obey through `WorkTagIsDisabled`.
Ideoligion roles: `IdeoRole_ProductionSpecialist` already raises quality through vanilla's roll, so a specialist paints better with no row. Backstories: nothing real depends on them, so they stay out. Inspirations: only `Inspired_Creativity` matters (section 9). Every other break and inspiration has nothing to add.

## 7. Fight chance scales with temper

Vanilla (`Pawn_InteractionsTracker`): `TryInteractWith` rolls on the **recipient**. `SocialFightChance` is base × capacities × hediffs × recipient's opinion of the initiator × the recipient's trait `socialFightChanceFactor` × age gap × slave .5 × both pawns' gene factors. Vanilla insult base is .04, slight .005.

`RM_Graffiti_Confront` has base .75, and the recipient of a confront is the painter. **So today a Bloodlust painter nearly always fights when confronted, and a Bloodlust confronter counts for nothing.** Only genes reach the confronter's side. That is the actual defect behind "0.75".
Proposed: set the def's base to 0 so vanilla never rolls it, keep the talk, then roll ourselves after `TryInteractWith`, in `JobDriver_ConfrontPainter`. Start from the **confronter's** own vanilla chance:

```
P = min(.85, 3 × C × t)                                        (3 and .85 are P)
C = confronter.interactions.SocialFightChance(Insult, painter)
    (his opinion of the painter, his unsuppressed traits, capacities, hediffs, age gap, slave factor, both pawns' genes)
t = the table's temper column for the confronter, clamped 0 to 4
```

Both directions must pass `SocialFightPossible`, and the same guards as `CheckSocialFightStart` apply: `DebugSettings.enableRandomMentalStates`, a mood need, no tutorial. On a hit, `painter.interactions.StartSocialFight(confronter)`. `3` makes it three vanilla insults, because a confrontation over a named slur is more than an insult. `C` clamps at 1, which is far above the cap, so nothing is lost. The `hot` flag becomes `t × his trait and gene factors >= 1.5`.

Worked, with confronter's opinion -30 (vanilla factor 1.9):

| Confronter | P |
|---|---|
| Ordinary | .23 |
| Wimp | .11 |
| Kind | .06 |
| Abrasive, Brawler or Volatile | .34 |
| Aggressive gene (2) | .46 |
| Bloodlust (vanilla field 4) | .85 (cap) |
| Ordinary at neutral opinion; dead calm gene | .12; 0, impossible |

Colony cap (P): a confrontation always happens as a row, but at most one Graffiti fight per 15 days for the whole game, saved in a `GameComponent` and spent only on a real fight. Per map, three maps would allow six in 30 days. That keeps the review's bill of two true for Graffiti's own fights; ordinary fights caused by new hatred fall under the opinion cap in section 10 instead. The player still sees the shouting and the thought. A fight then always has two named people and one named wall, and our message says so, because vanilla's fight log line only fires inside its own roll.

## 8. Clean freaks and the compulsive cleaning break

Extra debuff (P): a pawn with `neat` finding a mark that is not their own gains `RM_Graffiti_Mess`: -2 at `neat` 1, -3 at `neat` 2, one day, one stack, and at most once per 3 days for that pawn however many marks there are. One new awful mark a day must not hold a neat pawn at -4 for a month.

**`RM_GraffitiCompulsiveCleaningBreak`** (`MentalBreakDef`, intensity Minor, baseCommonality 1 (P), `workerClass` below). How often it is picked depends on what else is eligible, so tune it in play.
**`MentalBreakWorker_GraffitiCleaning : MentalBreakWorker`.** `requiredTrait` takes one trait only, and clean freaks are several, so a small subclass is needed.

- `BreakCanOccur`: base check, `neat` 2, able to do Cleaning (also checked in the job), one or more reachable marks in the Home area, and no Graffiti break in the last 15 days (P). The painting spree gets its own small worker with only the cooldown. They share a saved cooldown utility, never the eligibility.
**`RM_GraffitiCompulsiveCleaningState`** (`MentalStateDef`), written out in full in XML, since `ParentName` does not carry the spree's settings: colonists only, `requiredCapacities` Manipulation, `moodRecoveryThought` Catharsis, letter on start. Minimum 7500 ticks, maximum 15000 (P). The scrub count is saved.
**Think tree** copies the spree's tree: food and rest, then `JobGiver_GraffitiCompulsiveClean`, then `JobGiver_WanderColony`. The giver picks the nearest reachable mark in the Home area of **any** kind, whoever painted it, and uses the existing scrub job. `AutoCleanProtection` guards only ambient cleaning, so it does not stop this.
**It ends** at max ticks, or when no reachable marks remain, or after 6 successful scrubs (P), and those last two end it at once even inside the minimum: six scrubs take about 2,520 ticks. The cap stops one break erasing a colony's whole history.
**His refusal rule.** "If a person hates the subject, they will refuse to clean the insult" holds for ordinary cleaning. During this state it is waived: a break isn't a choice, and that irony is the story. Scrubbing a mockery still bonds subject and cleaner, per his pick. So a neurotic who hates someone can end up rescuing them.

**Cleaning what people cared about.** Quality alone does not make a mark dear. `Filth_Mark` saves a new `valuedBy` set, filled only when a reader had a positive reaction to this mark, because `readBy` is just a timestamp. When the state removes a mark, each colonist in `valuedBy` gains `RM_Graffiti_ScrubbedWhatIDear`: mood -3, one day, and opinion of the cleaner -5, twenty days (P), one stack per pair. The tribute's subject and a mourner count as valuing it. A mockery's subject never does, so rescuing a victim costs nothing with them. The painter takes only the existing `ScrubbedMyWork` and `Scrubbed`, never this one as well. The message names the mark and the cleaner. A lure is erased too, per his Lures pick ("totally cleaning it would"), and the letter says so.

## 9. Art skill

Today a mark's beauty is fixed by its ThingDef (-2 to -8), skill does nothing, and no mark has a quality.

**Skill to craft.** At `MakeMark`, call `QualityUtility.GenerateQualityCreatedByPawn(pawn, SkillDefOf.Artistic, consumeInspiration)`, and save the result in `Filth_Mark`, with a saved `hasCraft` flag so an old save's marks keep their def beauty instead of reading as Awful. That is vanilla's sculpture curve, with Production Specialist's bonus and inspiration included. `JobDriver_PaintGraffiti` passes whether the job was ordered: ordered paint uses `Inspired_Creativity`; autonomous and spree paint do not, so no one's inspiration is wasted on a tag. A mark with no maker has no craft. Legendary needs inspiration or a role, as vanilla has it.

**Repainting.** Same-def placement thickens the existing filth, and `MakeMark` then overwrites its maker and subject while keeping its readers and `defaced`. So same-def placement becomes a fresh artwork: new craft, cleared `readBy`, `valuedBy` and `defaced`.

Rolled with vanilla's constants (200k simulated, % of marks):

| Artistic | Awful | Poor | Normal | Good | Excellent | Masterwork |
|---|---|---|---|---|---|---|
| 0 | 64 | 30 | 5 | 0 | 0 | 0 |
| 3 | 9 | 51 | 33 | 6 | 0 | 0 |
| 5 | 2 | 35 | 47 | 15 | 1 | 0 |
| 8 | 0 | 9 | 51 | 34 | 6 | 0 |
| 12 | 0 | 1 | 25 | 53 | 21 | 1 |
| 20 | 0 | 0 | 2 | 37 | 51 | 9 |

**Craft to effect (all P).**

| Craft | Net beauty in the room | Viewer thought | Meaning `reach` | Compare |
|---|---|---|---|---|
| Awful | -6 | `RM_Graffiti_UglyMark` -2 | .75 | Roofed dirt is -4.5 |
| Poor | -2.5 | `RM_Graffiti_UglyMark` -1 | .85 | |
| Normal | 0 | none | 1 | Just a mark |
| Good | +3 | `RM_Graffiti_FineArt` +1 | 1.1 | |
| Excellent | +8 | `RM_Graffiti_FineArt` +2 | 1.2 | |
| Masterwork | +18 | `RM_Graffiti_FineArt` +3 | 1.35 | |
| Legendary | +30 | `RM_Graffiti_FineArt` +4 | 1.5 | A normal small sculpture is +50 |

`reach` multiplies the meaning thoughts, mood and opinion. A clumsy insult is laughed off, and a great one sticks. Craft is evaluated in `Reads` before the meaning check, because `Reads` returns early when meaning has no reaction and a neutral tag must still be judged as paint. Both craft thoughts are one day, one stack, first read only, and a higher stage replaces a lower through `Give`. Own work gives no craft thought. Luminous Pigments need only a later multiplier on net beauty, a one-line slot to leave open and not build.

**Into the room.** `Thing.GetBeauty(bool outside)` is virtual (1.6 decompile, `Thing.cs`), so `Filth_Mark` overrides it and needs no Harmony. Vanilla's `CellBeauty` multiplies filth under a roof by .3, so the override divides by .3 when roofed, to make the table's "net" true indoors and outdoors. One shared calculation feeds the override and the inspect line. The info card's stat still shows the def's value; look at that live and decide. Check live too that room stats pick up a mark's craft once it is rolled, and dirty them if not. Existing Beauty stat values stay as the no-maker fallback. Cleanliness stays as it is.

⚠️ **Trap against his Walls pick.** `CellBeauty` keeps only `Fillage.Full` things when a cell holds one. Marks today sit at `Position` on the floor cell beside the wall, so they count. If "keep marks on the wall tile" ever moves `Position` onto the wall cell, their beauty silently becomes zero. His pick is about what dies with the wall and where it draws, so keep `Position` on the floor cell or carry beauty another way.
Room effect in a 40-cell room (`RoomStatWorker_Beauty` is sum / 40). Impressiveness assumes beauty 1 before paint, 500 wealth, 40 space stat, clean. These are estimated by vanilla's formula, so measure them live before keeping this table. `RoomHoldsEnough` allows 3 marks here.

| Marks | Room beauty change | Impressiveness | Note |
|---|---|---|---|
| None | | 43 decent | |
| 3 Awful | -.45 | 36 mediocre | A stage down |
| 3 Masterwork | +1.35 | 51 slightly impressive | A stage up |

The environment need barely moves: three awful marks give level about .355 against the ugly threshold of .35, because level is .4 + average × .1, using the room's average as a stand-in for the cells actually sampled. So the craft thought does the mood, and paint cannot quietly become a permanent tax through the need.

**Combined, worked (P).** Subject of a mockery, ordinary temperament:

| Painter | Craft | Beauty | Subject's mood | Subject's opinion of painter | A witnessing enemy of the subject |
|---|---|---|---|---|---|
| Artistic 0 | Awful | -6 | Humiliated -6, ugly -2 = -8 | -22 | Gleeful +2, ugly -2 = 0 |
| Artistic 8 | Normal | 0 | Humiliated -8 | -30 | Gleeful +3 |
| Artistic 12 | Excellent | +8 | Humiliated -9.6, fine art +2 = -7.6 | -36 | Gleeful +3.6, fine art +2 = +5.6 |
| Inspired master | Legendary | +30 | Humiliated -12, fine art +4 = -8 | -45 | Gleeful +4.5, fine art +4 = +8 (at the ceiling) |

The legendary slander is the owner's sentence in numbers: the needs tab says "Humiliated -12" above "A fine piece +4", the victim is furious at the painter (-45), and the room is more beautiful for it. An awful memorial still moves the grieving at 75%.
Other readers: a Neurotic before a legendary tribute gets Mess -2 and fine art +2 (`fine` .5), so about neutral. An Ascetic gets no craft thought at all but the meaning in full. Sensitive stays sensitive at the top: the same legendary slander nets -8 ordinary, -10 nervous (-15, +5), -12 volatile (-18, +6).

## 10. Staying bounded in a 20-pawn colony

| Bound (P) | Where | Protects against |
|---|---|---|
| Temperament clamps at 1.5, `reach` at 1.5, so one thought is at most ×2.25, and only a Volatile victim of an inspired master gets there (-18) | `Give` | Rows stacking without limit |
| Two separate mood budgets. Negative Graffiti memories stay within -8, or -12 as a named mockery's subject, each × the pawn's `bad`. Positive stay within +8 × `good`. A new thought shrinks to fit. Positives never pay for negatives, so an expiring fine art cannot uncover a breach, and summing single offsets only overstates vanilla's stacked total | `Give` | A wall of many marks |
| Opinion: all negative Graffiti opinion from one pawn of one other is capped at -30, or -45 for the named victim. `WhatTheWallSays` becomes one stack per pair, his pick. It targets the subject, and two legendary ones would cross into enemy from neutral | `Give`, ThoughtDefs | -73 from `PaintedMe` alone, more with `reach`; gossip making enemies |
| His Rereads pick: first read gives the full effect, later reads no opinion or grudge, and only the subject keeps a small reminder. **Not yet built:** `ReadAgainTicks` is still 1.5 days at head. Every new thought obeys it, with saved one-time reads | `Filth_Mark`, `GraffitiSocial` | Standing marks as a tax |
| `paint` clamps at 2 and stays under existing room limits | Joy and idle givers | Abrasive colony covering every wall |
| Fights one per 15 days; Graffiti breaks one per 15 days; both per game | section 7, 8 | Fight and break storms |

Who counts (P). Prisoners and slaves read and feel, and neither confronts nor paints on their own. Autonomous subjects stay free colonists, as today. Children read and feel, and no one autonomously paints mockery of a child. These are decisions the current `Look` makes by accident.

Spirals, and what stops each:

**Paint, mood, spree, paint:** a spree is a break and shares the 15-day cooldown. `RoomHoldsEnough` and `AlreadySaid` limit its marks. Readers feel each mark once. **Cleaner rage:** a break scrubs loved pieces, people get cross, someone else's mood falls. The source depletes (at most 6 marks), the thought is one stack per pair at -5, and another break waits for the cooldown. **Fight, hate, mockery, fight:** a fight lowers opinion, so more mockery, so more answers. One standing grudge per pawn, a day's answer cooldown, one Graffiti fight per 15 days, and the opinion cap.

Worst honest case: 20 pawns all read one master's slander. The subject sits at -8 for three days, -12 if volatile. Friends lose 2 to 3 for a day, offset by fine art. Enemies gain up to 8 for a day. Those who disapprove think less of the painter, and those who gossip think less of the subject, each once. Then it stops, apart from the subject's small reminder while the mark stands. The review's `ordinary_colony_social_bill` is the test: 90% of pawn-days within 3 mood, at most 2 fights and 2 breaks in 30 days. I would change one number: all pawn-days within 8 **except the subject of a named mockery**, allowed 12 × `bad`, since the owner wants sensitive types to feel more.

## 11. BUILD NOW, in files

| # | File | Change |
|---|---|---|
| 1 | new `Source/GraffitiTemperament.cs` | Def class, lookup, `Give` with budgets and stack handling, saved cooldowns `GameComponent` |
| 2 | new `Defs/TemperamentDefs_Graffiti.xml` | The table of section 5 |
| 3 | new `Source/GraffitiCompulsiveClean.cs` | Two break workers, state class, job giver, the dear-work response |
| 4 | `Source/GraffitiSocial.cs` | Use `Give`; craft in `Reads`; `valuedBy`; `numb` in `AddGrudge`; `hot` from table; who counts; one-time reads |
| 5 | `Source/Kernel/RM_GraffitiKernel.cs` | `numb` in `ReactionOf`; `lean` in `AnswerOf`; pure `ConfrontChance`, `ReachOf`, budget maths |
| 6 | `Source/Filth_Mark.cs` | Saved craft, `hasCraft`, `valuedBy`; `GetBeauty` override; inspect line; same-def is a fresh artwork |
| 7 | `Source/JobDrivers_AnswerMark.cs` | Our roll after the talk, guards, fight message, game cap |
| 8 to 10 | `Source/JobDriver_PaintGraffiti.cs`; `Source/JoyGiver_PaintGraffiti.cs`; `Source/JobGiver_IdleTag.cs` | Pass "ordered" to the roll; `paint` on autonomous chance |
| 11 | `Defs/ThoughtDefs_Graffiti.xml` | Psychopath and Inhumanized nullifiers everywhere; `UglyMark`, `FineArt`, `Mess`, `ScrubbedWhatIDear`; gossip one stack |
| 12 to 14 | `Defs/MentalStateDefs_Graffiti.xml`; `Defs/ThinkTreeDefs_Graffiti.xml`; `Defs/SocialDefs_Graffiti.xml` | New break, state, workers on both breaks; cleaning tree; confront base 0 |
| 15 to 17 | `Source/Graffiti.csproj`; `SelfTest/GraffitiFuzz.cs`; `validation.py` | New sources; kernel bounds and table names against the dump; claims for the new bars |

Only `numb`, `Give`, the kernel functions and the break are code. A new trait in future is one XML row.

## 12. LATER

| Row | Idea | Why not now |
|---|---|---|
| Mod catalogue | `VTE_Slob`, `RT_Messy`, `Hygienic` -1 and -2 (`ugly` 0); `BS_InsultProof` (bad 0); `BS_Gentle` (temper .25, scrub); `VTE_Desensitized` (bad, good .5); `VTE_Perfectionist`, `VTE_Snob` (craft 1.5); `VTE_Vengeful` (temper, paint 1.5); `VTE_Rebel`, `Gossip` (paint); `RT_EasilyAmused`, `VTE_FunLoving` (good 1.25); `RT_ConstantlyBemused`, `VTE_WorldWeary` (bad .75); `AM_Ahimsa` (temper 0); `Peacemaker` (temper .5) | One XML row each, once the table proves itself. Mods with a vanilla fight field need no row |
| `IdeoRole_Moralist` | Paints Devotion more; offended more | Role logic, not a trait row |
| `AM_Art_Desired`, `AM_ArtQuality_Expected` (sarg.alphamemes), `VME_Junk_Beautiful` | Art precepts make craft count double; junk is beautiful | Optional mods |
| `Jealous`, `Beauty` degrees | Jealous of a fine tribute to another, beyond today's lover case; mocking the vain or ugly stings differently | Needs a new reaction |
| `Disturbing`, `Occultist`, `NightOwl` | Paints upsetting ideas, reads occult sigils, prefers painting at night | Needs art and marks, or a time check |
| `InsultingSpree`, `TargetedInsultingSpree`, `TargetedTantrum` | Targets the painter of a standing mockery | Vanilla patches |
| Royal titles | Mockery of a noble stings more | Needs titles on the viewer |
| A painter's own pride | Bad work upsets `VTE_Perfectionist`; a masterwork gives pride | After the craft works |

## 13. Tests worth trying

Proposals for the loop, so improve them. A selftest on the kernel, a live check on the game: a colonist with Psychopath as a mockery's subject shows zero Graffiti thoughts and no answer, even when someone paints over his work; two painters of Artistic 0 and 18 paint in the same bare room, and the inspect line, room beauty row and needs tab differ as this table says; a Very Neurotic with marks present forced into the break scrubs a tribute, and the tribute's subject shows the new thought naming the cleaner; a Bloodlust and a Kind confronter over the same mark, many times, give different fight rates near the table; a stronger memory arriving at the stack limit wins and keeps its factor; an old save's marks keep their old beauty; the game loads Core-only with every optional row inert.

## 14. What GPT changed

One independent challenge, 12 findings. I checked each against the 1.6 decompile and the code at the loop's head.

| GPT said | Check | What changed |
|---|---|---|
| Wallet lets positives pay for negatives; opinion uncapped; `LostFace` targets the subject, not the painter | True | One-sided budgets; per-pair cap; gossip one stack; my "painter takes one hit" was wrong |
| "First read only, existing" is false; merge drops the incoming factor and stage | Both true, read in 1.6 and at head | Reads marked as to build, mess limited per pawn, `valuedBy`; `Give` keeps the stronger |
| Cleaner punished for rescuing the victim; "same worker" limits sprees to clean freaks | True | Attachment only, victim excluded, -15 to -5; separate workers, shared cooldown, written-out state |
| `paint` on the wrong decision; `Notify_WentOver` escapes numb | True | `paint` moved to the givers; numb in `AddGrudge`; `nullifyingHediffs` |
| Craft misses neutral marks; same-def repaint rerolls an old mark | True | Craft before the meaning check; fresh artwork; `hasCraft` |
| `GetBeauty` may not be virtual | **False**, it is | Kept; live checks for the info card and room stats |
| Cap reverses sensitivity; `craft` too coarse | True | Cap replaced by two clamps; `fine` and `ugly` |
| Fight formula double-counts opinion, skips guards, cap per map | True | Confronter's vanilla chance × table; guards; per game |
| Settle who counts and tolerance now; defer the mod catalogue | Accepted | Moved both ways. File count 14 to 17 |

Not taken: compulsory cleaning only for literal neat traits. His word was clean freak and vanilla's closest is Neurotic, so Very Neurotic keeps the break and plain Neurotic only minds the mess. Ascetic stays unmoved by craft, and Nervous stays both quick to break and more affected; those are characterisation, not claims. Removing Graffiti from a running save stays unpromised, as today.

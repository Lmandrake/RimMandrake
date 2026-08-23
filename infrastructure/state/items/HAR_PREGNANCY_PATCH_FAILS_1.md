# HAR_PREGNANCY_PATCH_FAILS_1 Humanoid Alien Races' fertility patch failed to apply; cross-species rules are off

## spec

From `D:\Luke\dev\Rimworld\observed\logs\2026-08-23_Player.log.final`, around line 5026:

```
Error during patching RimWorld.PregnancyUtility :: Verse.AcceptanceReport CanEverProduceChild(Pawn, Pawn)
System.Exception: Wrong null argument: brtrue NULL
  ... at AlienRace.AlienHarmony.Patch
```

Humanoid Alien Races' `CanEverProduceChildTranspiler` emitted a branch with a null
operand, so Harmony threw and **both** the transpiler and the postfix on that method
were dropped. HAR's other 277 patches applied.

`PregnancyUtility.CanEverProduceChild` is what gates who can conceive with whom. With
HAR's patch gone, the game falls back to vanilla's answer for every pair.

## Why it lands on DECIDE rather than BUILD

It is a third-party mod's bug in a third-party mod's assembly — we do not fix it. What
needs deciding is whether we care, and that turns on something only this project knows:
**we field 69 humanlike species.** If cross-species fertility was ever going to be a
rule of this campaign — Twi'lek and human, Wookiee and anything — it is currently not
being enforced, and the failure is silent in play.

Three answers, and any of them closes this:

1. **Do not care.** Reproduction is not a mechanic this campaign leans on. Close it,
   and put the log line in the known-noise list so it stops being rediscovered.
2. **Care, and accept vanilla's answer.** Establish what vanilla actually permits
   between our xenotypes, write it down, and design around it.
3. **Care, and chase it.** Check whether HAR has a newer build, or whether another mod
   in the stack is transpiling the same method first and breaking HAR's IL match.
   Expensive, and the payoff is a rule nobody has yet asked for.

Recommendation: **1**, unless a design doc already assumes cross-species children.
Somebody who knows `design/Jawa/` should say so before this is closed.

## verify

Whichever answer: the outcome is written where a reader hits it — either the
known-noise list, or the ruling that says vanilla fertility is what this campaign uses.

## Watch out

- ⚠️ This reading is from a load that began 00:12 today. It proves what that process
  held. A later mod-list change could make it appear or vanish without anyone touching
  HAR.
- The identification of HAR as owner is CONFIRMED from the stack frame
  (`AlienRace.AlienHarmony.Patch`). Which mod's IL it collided with, if any, is
  UNMEASURED — nobody has looked.
- Filed by REP from a log reading. No game test was run.

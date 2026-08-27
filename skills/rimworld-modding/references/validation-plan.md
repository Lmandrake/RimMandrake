# The validation plan — what you owe whoever holds the game

Open this when you are writing the plan, or when you are about to hand over
anything you cannot check yourself. `§` numbers below point into `SKILL.md`.

---

## 🔴 SIZE THE PLAN TO WHAT THE CHECK COSTS — owner, 2026-08-26

*"I think we're generating busy-work unnecessarily."* He is right, and it was
measured the day he said it: four handovers in one session carried **784 words** of
plan for four bridge calls that prove in about a minute each. Trimmed to the three
things a person holding the game cannot reconstruct, they came to **187**. Nothing
was lost.

**The seven labelled fields below are for a check that rides an EXPENSIVE COLD
LOAD.** They are not a template to fill in. Most handovers are not that:

| what the check costs | what you owe |
|---|---|
| a bridge call, or a 22-second minimal load | **three lines** — the call, the expected reading, how a pass could be false |
| a full cold load on the big list | the seven fields, because that look is expensive and unrepeatable |

⛔ **`RIDE` is not a per-item field.** "Batch or solo", and which window the work
rides, is ONE fact about the release — it lives once in
`infrastructure/state/NEXT_RELOAD.md`. Restating it per item is the busy-work: it
appeared five times in one session, worded five different ways, saying the same thing.

⛔ **Do not write `ITEM` and `SEE` as separate fields from the heading and the
prediction.** They restate them. If the heading names the tool and the prediction
names the reading, both are noise.

✅ **What survives at every size, because only the author knows it:** the exact call,
the prediction as a number or string, and **how the check LIES.** If you write only
one thing, write the last.

## Why it ships in the same commit

Anything you author and cannot check yourself — a def, a patch, an assembly —
ends with a validation plan **in the same commit**. Not on request: without one the
person holding the game invents a check, and theirs will not carry your prediction.

⚠️ **The old justification here said "a cold load costs 23–30 minutes" and that is
what oversized this document.** It is still true of the full list and it is NOT the
common case: `rimworld-load-round` measures a 13-mod minimal list at **22 seconds**,
and a companion tool proves in about a minute. Price the plan against the load it
will actually ride.

🔴 **Name a positive observation, never "no error".** "No `Patch operation …
failed` line" is an absence, and §7 ranks absences last. Name the thing on
screen: the animal on the wildlife tab, `MoveSpeed` at 4.6 in the stat readout.

**Give the exact route** — defName, dev-mode spawner path, bridge call with its
arguments. ⚠️ If the route needs a tool that does not exist yet, file it as
*blocked on the tool*; do not queue it for a load it cannot survive.

**Write the prediction BEFORE the look**, as a number or a string: *two*
`wildBiomes` children, not "fewer". Without it you rationalise the panel.

**Close on one observation, and name the minutia you are not chasing** — the
icon, the translation key, the second biome.

**Say batch or solo** (§2). A new assembly goes solo: if the load comes up wrong
nobody can separate the DLL from the three def changes beside it.

**Say how this check LIES.** Four false passes that cost real cycles here:
- **The conditional never ran.** A `PatchOperationConditional` in a mod that loads
  *before* the mod it patches matches nothing, no-ops, and **prints no log line at
  all** — so "clean log" and "patch applied" are indistinguishable. Load order
  decides whether the check is even meaningful; assert the index (§5b).
- **The consumer is stale.** The file is right and the game never read it —
  RimWorld reads defs **once, at startup**. "Deployed" and "live" are different
  claims (§6b), and the mtime against the process StartTime is the evidence.
- **The instrument cannot see it.** `jawa/get_def` returns `extra: null` for def
  types it does not model, which reads as *the field is absent*. Membership
  questions go to the def dump, never to the probe (as per `traps-tooling.md`).
- **A map-gen def checked on an old map.** A `GenStepDef` changes nothing until a
  map is *generated after the load*; loading a save re-runs no GenStep, so a
  correct fix reads as a third failure (§6b; as per `traps-diagnosis.md`).

### The shape to hand over

```
ITEM     <what is being validated>
SEE      <the positive observation>
ROUTE    <exact call / defName / click path>
PREDICT  <number or string, before the look>
CLOSE    <the bar> — NOT chasing: <the minutia deliberately skipped>
RIDE     batch | solo (<why, if solo>)
LIES     <how this check produces a false pass>
```

Seven lines. If it does not fit, the item is really two items. Worked, for a
`PatchOperationRemove` against a spawn table:

```
ITEM     Armadillo dropped from Desert spawns (Jawa_Patches/Biomes.xml)
SEE      A freshly generated Desert map's wildlife tab lists no Armadillo, and
         the live def dump shows 2 children under race/wildBiomes
ROUTE    Load -> refresh the def dump -> read ThingDef Armadillo -> generate a
         NEW Desert map (an existing save re-runs no GenStep) and open Wildlife
PREDICT  exactly 2 wildBiomes children — was 3 (Desert, AridShrubland,
         TropicalSwamp)
CLOSE    The dump shows 2 — NOT chasing: Armadillos already spawned on old maps
RIDE     batch — pure XML, validated clean, named log string to grep
LIES     Remove deletes EVERY match (§4), so "Desert is gone" is also what a
         too-greedy xpath looks like. Count the survivors, not the removal.
```

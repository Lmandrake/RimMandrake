## spec

🔴 **A decision only the owner can make: is "the Jawa are bad at farming" a PENALTY or a
PROHIBITION?** Measured live 2026-08-23 03:4x — right now it is a penalty, and nothing
stops a Jawa farming.

| clause the play test asks for | mechanism | result |
|---|---|---|
| a Jawa **cannot create a growing zone** | none | ❌ **it can** |
| a Jawa **cannot sow a hydroponics basin** | none | ❌ **it can** |
| a Jawa **cannot mine by hand** | `RimMandrake_Jawa_MiningDisabled` → `disabledWorkTags: Mining` | ✅ `Mining disabled=True` on the pawn |

**Read off a spawned `Jawa_Colonist` forced to `MandrakeJawa`, against a Baseliner
colonist as control:** Jawa `Mining disabled=True`, control `Mining disabled=False`,
Jawa **`Plants disabled=False`**.

### Why the plant half has no teeth

`Growing` and `PlantCutting` carry `workTags: ManualSkilled, Commoner, PlantWork,
AllWork`. **`PlantWork`, not `Mining`** — so the one gene that bans mining cannot touch
them. The only plant-side change is `AptitudeTerrible_Plants`, which is **−8 aptitude**:
a Jawa is bad at it, slow at it, and entirely allowed to do it.

⭐ **This is not a build defect and must not be filed as one.** `JAWA_WORK_BANS_PLAY_TEST_1`
forecast it in writing before the test ran — *"(1) has no mechanism at all: the
`Rule_DisallowDesignator` was struck and `AptitudeTerrible_Plants` is only −8 aptitude, so
a Jawa CAN still make a growing zone. Expect (1) to FAIL and treat that as a spec question
for the owner."* The prediction was correct. What is missing is a ruling, not a fix.

### The two roads, so the answer is a choice and not an essay

- **PENALTY (status quo).** Jawa farm badly and slowly. Nothing to build. The scenario's
  flavour carries the idea and the mechanics do not enforce it.
- **PROHIBITION.** Needs a second gene disabling the `PlantWork` **tag**, mirroring the
  mining one. ⚠️ That is a blunt instrument: `PlantWork` also covers **harvesting, cutting
  plants and chopping trees**, which clauses (5) of the play test explicitly wants Jawa to
  KEEP. A tag-level ban would take those away too, so a prohibition needs a narrower
  mechanism than the mining ban used, and someone has to find one.

## verify

- The owner has answered penalty or prohibition, and the answer is written in
  `design/Jawa/` where the scenario spec can cite it.
- If prohibition: a Jawa cannot sow, and CAN still harvest, cut and chop — both halves
  demonstrated on a live pawn.

## criteria

`JAWA_WORK_BANS_PLAY_TEST_1` clause (1) has a defined expected outcome, so the next
person to run it knows whether a Jawa making a growing zone is a pass or a fail.

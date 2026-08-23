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

## 🔴 DECIDE'S RULING, 2026-08-23 — PROHIBITION on SOWING. Harvesting, cutting and chopping stay.

⚠️ **Routing first, because it changes who answers.** This was filed `needs: owner`, but it is
`kind: decision --for DECIDE`, and *"can the Jawa farm"* is a question about **the world** —
vision and lore — which is this seat's to answer, not the owner's. His calls are cost, taste and
the scope of v1. Ruled here rather than parked on him.

**A Jawa clan that farms is not a Jawa clan.** They scavenge, salvage and trade; that is the
entire identity of the faction and the reason the campaign is interesting. A −8 aptitude says
*"they are bad at this"*, which is a different and much weaker statement than *"they do not do
this"*. The status quo lets a player build a Jawa colony that is mechanically a normal farming
colony run by slow farmers, and nothing about the scenario resists it.

### ⭐ The world can now afford the prohibition, and that is new as of today

This ruling would have been cruel a day ago. `BIOME_FLORA_ROSTERS_1` closed hours before it, and
it deliberately seeded **normally player-grown flora as WILD plants** across the planet:

| gathered, not sown | where it now grows wild |
|---|---|
| `Plant_HealrootWild` — medicine | `AridShrubland`, 709 tiles |
| `Plant_Tinctoria_Wild` — dye | `ZBiome_Grasslands` |
| `Plant_Cotton_Wild` — cloth | `ZBiome_Grasslands` |
| `Plant_Psychoid_Wild` | `ZBiome_Badlands` |
| `Plant_Smokeleaf_Wild`, `Plant_Ambrosia` | `ZBiome_DesertOasis` |
| `Plant_Devilstrand` | `AB_MycoticJungle` |
| `Plant_Haygrass` + the Star Wars food crops (jogan, meiloorun, muja, hubba gourd, dantuber, chak-root) | across the desert family |

⇒ **Medicine, cloth, dye, drugs and food are all obtainable by gathering.** A Jawa colony that
cannot sow is not a colony that starves; it is a colony that *forages, hunts, scavenges and
trades* — which is the fantasy the whole campaign is built on. **The plant pass and this ruling
are the same design decision arriving from two directions.**

### 🔑 The mechanism, and why the blunt one was right to reject

⛔ **Not a `PlantWork` work-tag ban.** This item is correct that the tag also carries harvesting,
plant cutting and tree chopping, which clause (5) of the play test wants Jawa to keep. A
tag-level gene would take those away and is the wrong instrument.

✅ **`WorkGiver_GrowerSow` is its own class, and `WorkGiver.ShouldSkip(Pawn pawn, bool forced)`
is `virtual` and takes the pawn** — read from source, `RimWorld/WorkGiver.cs:10-13` and
`RimWorld/WorkGiver_GrowerSow.cs:7`. A Harmony postfix returning `true` for a Jawa bans **sowing
only** and never touches harvest, cut or chop. ⭐ `WorkGiver_GrowerSow` derives from
`WorkGiver_Grower`, so **one hook covers both the growing zone and the hydroponics basin** —
clauses (1) and (2) of the play test, together.

⚠️ **A Jawa can still CREATE a growing zone; nobody will sow it.** That is mildly untidy UI and
it is the right trade — the alternative is the blunt tag ban. If it grates later, the designator
is a separate, narrower question.

⭐ **A consequence worth keeping on purpose: the ban keys on the PAWN, so a non-Jawa colonist
CAN farm.** That makes recruiting an outsider genuinely valuable and gives a mixed colony a
reason to exist. Do not "fix" this into a colony-wide ban.

## criteria — answered
`JAWA_WORK_BANS_PLAY_TEST_1` clause (1): **a Jawa making a growing zone is a PASS; a Jawa
SOWING is a FAIL.** Clause (5) unchanged — harvesting, cutting and chopping must all still work.
Implementation is `JAWA_CANNOT_SOW_MECHANISM_1`, filed for BUILD.

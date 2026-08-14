# Faction Stage 2 — gap audit

_PROJECT, 2026-08-13. Faction roster Stage 2 (`infrastructure/state/queue/VISION.md` **V9**). Offline audit of
`faction_roster_v2.md` against the live `FactionDef` surface. **Stage 2 was
specified as a gap audit, not an authoring pass** — nothing here proposes a value._

---

## 🔴 Read this before spending any time on the table below

**V1_SCOPE.md line 57 defers almost all of it to v2.** v1 is **one** authored
faction — the Imperial Desert Directorate, *label-level reskin only* (name, leader
title, colour). Explicitly v2: **the other 11 dossiers, `pawnGroupMakers`, memes,
ideoligions, the relations matrix.**

**And v1's faction row is already built.** `src/Jawa/Jawa_Patches/Patches/ImperialDesertDirectorate.xml`
(`27a3cfe`) sets `label`, `fixedName`, `leaderTitle` and `colorSpectrum`
(`RGB(74,84,96)` / `RGB(108,118,128)`), and the repo copy is **byte-identical to
the deployed game copy**. Its only open item is the scope gate itself — *seen
working in-game once*.

So this audit's product is a **v2 backlog**, plus **one v1-relevant discrepancy**
(below). It should not pull time away from the v1 burn-down.

---

## The one v1-relevant finding

⚠️ **The shipped patch and the roster disagree on the leader title.** The roster
says **"Sector governor"** (`faction_roster_v2.md:571`); the deployed patch says
**`<leaderTitle>Sector Director</leaderTitle>`**. Both are defensible; they are not
the same string, and the patch is what players see. **Decide which is canon and
make the other match** — the roster is the spec, so the cheap fix is to correct
whichever is wrong rather than let the pair drift.

---

## Method, and one trap it exposed

**"125 `FactionDef` fields" is not a checklist.** The def dump serialises every
field on the type whether or not an author set it, so all 88 live `FactionDef`s
"have" `canPsychicRitualSiege`. Filtering to fields whose values actually **vary**
across the 88 gives **92 of 125** as the real decision surface; the other 33 are
fields every faction in the game leaves at default.

This is WORLD's *registered ≠ available* trap (`d6927fd`) in a new place, and it
matters: an audit against 125 fields invents 33 fields of work nobody needs.

The 92 were grouped into **8 checks** rather than audited loose, because the
authoring cost concentrates in a few: `pawnGroupMakers` (43 distinct shapes across
the 88 live defs), `xenotypeSet` (38), `basicMemberKind` (27), `backstoryFilters`
(26), `requiredMemes` (19).

| | Group | Fields |
|---|---|---|
| A | Identity/display | `pawnSingular`, `pawnsPlural`, `leaderTitle`, `fixedName`, `factionIconPath`, `colorSpectrum`, `settlementTexturePath`, `categoryTag` |
| B | World placement | `requiredCountAtGameStart`, `maxCountAtGameStart`, `settlementGenerationWeight`, `maxConfigurableAtWorldCreation`, `startingCountAtWorldCreation`, `displayInFactionSelection`, `canMakeRandomly`, `hidden` |
| C | Relations | `naturalEnemy`, `permanentEnemy`, `permanentEnemyToEveryoneExceptPlayer`, `mustStartOneEnemy`, `hostileToFactionlessHumanlikes`, `raidsForbidden` |
| D | Combat/raids | `pawnGroupMakers`, `basicMemberKind`, `fixedLeaderKinds`, `earliestRaidDays`, `maxPawnCostPerTotalPointsCurve`, `raidLootMaker`, `canSiege`, `canStageAttacks`, `techLevel`, `allowedArrivalTemperatureRange` |
| E | Races/genes | `xenotypeSet`, `allowedCultures`, `backstoryFilters`, `backstoryCategories` |
| F | Ideology | `requiredMemes`, `disallowedMemes`, `allowedMemes`, `forcedMemes`, `structureMemeWeights`, `disallowedPrecepts`, `fixedIdeo`, `deityPresets` |
| G | Trade/tech | `caravanTraderKinds`, `baseTraderKinds`, `visitorTraderKinds`, `orbitalTraderKinds`, `canRequestTraders`, `apparelStuffFilter`, `startingResearchTags` |
| H | Naming | `factionNameMaker`, `settlementNameMaker` |

---

## Readiness — 12 factions, not 10

⚠️ **The roster holds TWELVE factions.** `infrastructure/state/queue/VISION.md` **V9** and `AGENT_PROJECT_state.md`
both said ten. **11. Indigenous Jawa Clans** (line 1809) and **12. Junker
Scrap-Warrens** (line 1932) were added later and several global sections were
never updated to match — which is the direct cause of defect **D5** below.

| # | Faction | A | B | C | D | E | F | G | H | Ready |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Hutt Cartel Confederacy | ~ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 7/8 |
| 2 | **Imperial Desert Directorate** *(v1)* | ~ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 7/8 |
| 3 | Outer-Rim Homestead Compact | ~ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ❌ | 7/8 |
| 4 | Tusken Sand Clans | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 6/8 |
| 5 | Free Droid Enclaves | ❌ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ❌ | 6/8 |
| 6 | Wookiee Freeholds | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 6/8 |
| 7 | Aquifer League | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 6/8 |
| 8 | Geonosian Foundry Hive | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | 5/8 |
| 9 | Arkanian–Kaminoan Consortium | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 6/8 |
| 10 | Bounty Hunters' Compact | ❌ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ❌ | 6/8 |
| 11 | Indigenous Jawa Clans | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | 5/8 |
| 12 | Junker Scrap-Warrens | ❌ | ⚠️ | ⚠️ | ✅ | ✅ | ❌ | ✅ | ❌ | 5/8 |

`~` = partially decided (leader title only). `⚠️` = decided but carrying a defect below.

**Two gaps are systematic, not per-faction:**

- **H (naming) is 0/12.** `grep -niE 'namemaker|name maker|naming convention'`
  over all 2,510 lines returns **nothing**. Every faction will fall back to
  vanilla name makers — Hutt kajidics and Tusken clans drawing RimWorld tribal and
  outlander names. **v2**, but it is a twelve-faction gap that no queue names.
- **A (identity/display) is fully decided for none.** Factions 1–3 have a leader
  title; nothing else in the group is set anywhere.
- **`humanlikeFaction` appears 0 times in the roster.** Harmless for the ten
  humanlike factions, load-bearing for **8 Geonosian** (insectoid hive) and
  **5 Free Droid** (droids).

---

## Verified defects — all six confirmed at source

Each was read at the cited line before being written here. The subagents that
found them also produced five findings that did **not** survive checking; those
are listed after, so nobody re-finds them.

**D1 — Homestead raid frequency contradicts Global system 9.** `:300` reads
*"Homestead / Aquifer / Wookiee never raid (Rw 0)"*; `:675` reads
*"Raid frequency | Very low"*. Non-zero vs never. Whoever authors the def must pick.

**D2 — Homestead ideology structure is an unresolved either/or.** `:712` reads
*"Structure: Abstract theist or ideological"* — literally both. Blocks
`deityPresets`, which exists only on the theist branch.

**D3 — Geonosian species has no implementation decision.** `:1403` sets
*"Preferred xenotypes: Geonosian"*, a precept that must bind to a defined
**xenotype**, while Global system 3 (`:183`) sources Geonosian from the separate
**race inventory**. Xenotype and race-mod species are different objects; the
roster never picks. Blocks group E. Compare `5 Free Droid`, which *does* flag its
equivalent question at `:1009` **and rules a fallback** — that is the pattern
D3 should follow.

**D4 — the Bounty Hunter racial table still contradicts a correction already
landed above it.** `:1655` states *"`Kaleesh` is the ONLY dry-capable species of
the six"* — the verified result recorded in `1bcd3b0` / `4c48aee`. The racial
table 40 lines below still labels **Zabrak, Bothan, Devaronian, Chiss and
Umbaran** as *"Dry-capable"*, and the gene table at `:1648-1649` explicitly marks
Chiss and Umbaran **heat-INTOLERANT**. **The correction was written into the prose
and the data table it corrected was left stale** — same shape as trap 45, in a
different file. Anyone authoring from the table gets the wrong answer.

**D5 — the roster denies the existence of a faction it contains.** `:2330` reads
*"no NPC faction generates Jawa members"* and `:2353` reads *"Every installed race
is used at least once across the **ten** NPC factions, except Jawa, which is
reserved for the player"* — while **11. Indigenous Jawa Clans** (`:1809`) is an NPC
faction whose roster is 78% + 12% Jawa. The species-coverage section was never
updated when factions 11–12 were added; note it still says **ten**.

**D6 — a second permanent enemy contradicts design pillar 5.** `:105` reads
*"One permanent enemy only. The Imperial Directorate. Everything else can
eventually be negotiated with, so the mid-game always has a wedge."* The Junkers
are `Permanent enemy | Yes` (`:1992`) and *"Permanently hostile faction; no trade"*
(`:2309`). **This is a design decision, not a typo** — either the pillar now
describes two, or the Junkers should be negotiable. Owner's call; it changes what
the mid-game wedge is.

### Discarded — checked and NOT defects

Recorded so they are not re-found:

1. **Imperial 10-vs-3 settlements** — already reconciled at `:522`; the 10 is the
   fiction total across surface and orbital layers. This is the P1 fix in `4db4048`.
2. **Kaminoan absent from the Geonosian weight table** — Global system 4 (`:209`)
   blesses race override at pawn-kind level. Its enumerated list is incomplete, not
   contradictory.
3. **Aquifer charge rifle** — mitigated in-document by the officers-and-relic-gear
   exception at `:1222`.
4. **Hutt ↔ Free Droid "transactional" vs the endgame wildcard** — a starting
   relation versus a player-driven branch outcome (`:915`). Not a data conflict.
5. **Geonosian "two leaders"** — `:1404`'s Arch-overseer is an *ideology role*, a
   different object from the `FactionDef` leader. The real issue is narrower and is
   worth recording: the Hive Queen is **immobile** (`:1379`, `:1385`) *and* the
   settlement leader, which does not fit `leaderForceGenerateNewPawn` /
   `generateNewLeaderFromMapMembersOnly`, both of which assume an ordinary pawn.

---

## What this changes

- **Nothing for v1.** The one authored faction is built, deployed and byte-identical
  in the game copy; it waits on the in-game sighting gate, not on this audit.
- **D4 and D5 are cheap and should be fixed regardless of v1/v2** — both are stale
  data that will mislead whoever authors from it, and neither needs a game load.
- **D6 needs the owner**, because it is a design pillar, not a value.
- **D1, D2, D3 are v2 authoring blockers** — file against the v2 faction work, not
  the v1 burn-down.

**Method note worth keeping:** four subagents produced 11 candidate contradictions;
**6 survived verification against the source lines and 5 did not.** The fan-out is
good at locating candidate seams and unreliable at judging them. Budget the
verification pass — it is not optional, and it is where the finding is actually made.

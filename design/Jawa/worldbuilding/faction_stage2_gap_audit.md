# Faction Stage 2 — gap audit

_PROJECT, 2026-08-13. Faction roster Stage 2 (now `design/V2_DREAMS.md` **B20**). Offline audit of
`faction_roster_v2.md` against the live `FactionDef` surface. **Stage 2 was
specified as a gap audit, not an authoring pass** — nothing here proposes a value._

---

## 🔴 Read this before spending any time on the table below

v1 defers almost all of it to v2. v1 is **one** authored
faction — the Galactic Empire, *label-level reskin only* (name, leader
title, colour). 🔴 **NO LONGER v2 — all of it is v1 and DEPLOYED: the 11 dossiers, `pawnGroupMakers`, memes,
ideoligions, the relations matrix.**

🔴 **v1's faction row is NOT done — the patch is on the wrong vessel.**
`src/Jawa/Jawa_Patches/Patches/ImperialDesertDirectorate.xml` (`27a3cfe`) sets
`label`, `fixedName`, `leaderTitle` and `colorSpectrum` (`RGB(74,84,96)` /
`RGB(108,118,128)`) on **`OuterRim_GalacticEmpire`**, a mod def. The Galactic
Empire's vessel is **vanilla `Empire`** (R10). **Re-point the patch**, set
`leaderTitle` to `Emperor` (R11), and re-run the in-game sighting gate.

So this audit's product is a **v2 backlog**, plus **one v1-relevant discrepancy**
(below). It should not pull time away from the v1 burn-down.

---

## The one v1-relevant finding — DISPOSED

✅ **The leader title is `Emperor`.** *(R11.)* "Sector governor" and "Sector
Director" are both retired from the Empire; **`Director` belongs to the Ascendant
Helix**. The shipped patch says `Sector Director` and is wrong — and it dies with
R10 anyway, since it targets `OuterRim_GalacticEmpire` and the Empire's vessel is
vanilla `Empire`. **Re-point the patch and set `leaderTitle` to `Emperor`.**

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

⚠️ **The roster holds TWELVE factions.** The Stage 2 brief (now `design/V2_DREAMS.md`
**B20**) and the retired `AGENT_PROJECT_state.md` both said ten. **11. Jawa Trade Moot** (line 1809) and **12. Junker
Scrap-Warrens** (line 1932) were added later and several global sections were
never updated to match — which is the direct cause of defect **D5** below.

| # | Faction | A | B | C | D | E | F | G | H | Ready |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Hutt Cartel | ~ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 7/8 |
| 2 | **the Galactic Empire** *(v1)* | ~ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 7/8 |
| 3 | Homestead Defense League | ~ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ❌ | 7/8 |
| 4 | Deep Desert Tribes | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 6/8 |
| 5 | Free Droid Enclaves | ❌ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ❌ | 6/8 |
| 6 | Wildsteam Clan | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 6/8 |
| 7 | Deepwater Compact | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 6/8 |
| 8 | Geonosian Foundry Hive | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | 5/8 |
| 9 | Ascendant Helix | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 6/8 |
| 10 | Blackstar Company | ❌ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ❌ | 6/8 |
| 11 | Jawa Trade Moot | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | 5/8 |
| 12 | the Junkers | ❌ | ⚠️ | ⚠️ | ✅ | ✅ | ❌ | ✅ | ❌ | 5/8 |

`~` = partially decided (leader title only). `⚠️` = decided but carrying a defect below.

**Two gaps are systematic, not per-faction:**

- **H (naming) is 0/12.** `grep -niE 'namemaker|name maker|naming convention'`
  over all 2,510 lines returns **nothing**. Every faction will fall back to
  vanilla name makers — Hutt kajidics and Tusken clans drawing RimWorld tribal and
  outlander names. **v2**, but it is a twelve-faction gap that no queue names.
- **A (identity/display) is fully decided for none.** Factions 1–3 have a leader
  title; nothing else in the group is set anywhere.
- **`humanlikeFaction` must be set explicitly on every faction** *(R3)*. It appears
  0 times in the roster today. Harmless-looking for the ten humanlike factions and
  **load-bearing for 8 Geonosian** (insectoid hive) and **5 Free Droid** (droids).

---

## Verified defects — all six confirmed at source, all six DISPOSED

**DECIDE's rulings, 2026-08-14 (R13).** Each outcome below is settled and written
into `faction_roster_v2.md`; nothing here is open.

Each was read at the cited line before being written here. The subagents that
found them also produced five findings that did **not** survive checking; those
are listed after, so nobody re-finds them.

**D1 — Homestead raid frequency. ✅ DISPOSED → `raidsForbidden: true`.** The field
exists; "Very low" is struck. `VME_Raiding_Abhorrent` may stay as flavour but is
not the mechanism.

**D2 — Homestead ideology structure. ✅ DISPOSED → `Structure_TheistAbstract`,
deity *the Withdrawn*.** The theist branch is taken, so `deityPresets` is
unblocked. This also separates the Covenant from the secular Deepwater Compact —
the 24% Jaccard overlap is answered by the split, not by a cut.

**D3 — Geonosian species. ✅ DISPOSED → `xenotypeSet` + `PawnKindDef` xenotype
chances.** **There is no XML route to `PreferredXenotype`**, so the precept
ambition is dropped. Geonosian dominance is carried by the `xenotypeSet` field on
the `FactionDef` (which exists) plus per-`PawnKindDef` xenotype chances. Group E
is unblocked.

**D4 — the Blackstar Company racial table. ✅ DISPOSED → the stale dry-capable
rows are gone; `Kaleesh` only.** The roster's mixture table now reads *Neutral* /
*Heat-intolerant* against the genes, and `faction_stage3_buildable_spec.md` §0b
and §2.10 were corrected to match. The finding as originally written: `:1655` states *"`Kaleesh` is the ONLY dry-capable species of
the six"* — the verified result recorded in `1bcd3b0` / `4c48aee`. The racial
table 40 lines below still labels **Zabrak, Bothan, Devaronian, Chiss and
Umbaran** as *"Dry-capable"*, and the gene table at `:1648-1649` explicitly marks
Chiss and Umbaran **heat-INTOLERANT**. **The correction was written into the prose
and the data table it corrected was left stale** — the same shape as a failure
already recorded, as per the trap file, in a different file. Anyone authoring from the table gets the wrong answer.

**D5 — "ten NPC factions". ✅ DISPOSED → twelve.** Global system 9's purpose note
and the species-coverage section both say twelve, and the Jawa Trade Moot is named
as the one NPC faction that generates Jawa. The finding as originally written:
`:2330` reads
*"no NPC faction generates Jawa members"* and `:2353` reads *"Every installed race
is used at least once across the **ten** NPC factions, except Jawa, which is
reserved for the player"* — while **11. Jawa Trade Moot** (`:1809`) is an NPC
faction whose roster is 78% + 12% Jawa. The species-coverage section was never
updated when factions 11–12 were added; note it still says **ten**.

**D6 — a second permanent enemy. ✅ DISPOSED by R12 → pillar 5 is amended to "one
permanent enemy among the AUTHORED factions".** Vanilla `Pirate` ships
`permanentEnemy: true` and Blackstar Company reskins it; patching that false would
gut the vanilla raid economy for no gain, so Blackstar keeps it. **The Galactic
Empire is the authored permanent enemy, and the Junkers lose theirs** — hostile on
sight, bribable, not permanent. The finding as originally written: `:105` reads
*"One permanent enemy only. The Galactic Empire. Everything else can
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
3. **Deepwater Compact charge rifle** — mitigated in-document by the officers-and-relic-gear
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

- 🔴 **v1's faction row has to be redone.** `ImperialDesertDirectorate.xml` targets
  `OuterRim_GalacticEmpire`; the Galactic Empire's vessel is **vanilla `Empire`**
  (R10). The patch was closed on a label seen live on a vessel we are abandoning.
- **D1–D6 are all disposed** and written into `faction_roster_v2.md`. None of them
  needs a game load and none is waiting on the owner.
- **The remaining v2 blocker is `pawnGroupMakers`**, written nowhere for any
  faction, plus H (naming), which is 0/12.

**Method note worth keeping:** four subagents produced 11 candidate contradictions;
**6 survived verification against the source lines and 5 did not.** The fan-out is
good at locating candidate seams and unreliable at judging them. Budget the
verification pass — it is not optional, and it is where the finding is actually made.

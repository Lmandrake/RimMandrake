# Faction doc cluster — maintenance-cost audit, 2026-08-20

_Analysis only. Nothing was changed. The metric is **how many documents a seat must
open and edit to record ONE new fact about one faction** — not disk, not line count._

**Scope read:** `faction_roster_v2.md` · `FACTION_SPEC.md` · `faction_world_spec.md` ·
`faction_stage3_buildable_spec.md` · `faction_equipment_guidance.md` ·
`faction_religions.md` · `faction_religions_spec.md` · `pawnkind_roster.md` ·
`force_users_build_spec.md`. Two neighbours had to be pulled in because they hold the
same facts: `ASHKARR_WORLD_DEFINITION.md` §7 and `src/RimMandrake/Utils/ashkarr_settle.py`.

## The headline

> **16 of the 17 recurring fact-classes in this cluster are stated in two or more
> documents.** Only one — `colorSpectrum` — has a single home. Multiplied across the
> 13 factions, that is roughly **190 individual fact statements maintained in
> duplicate**, and today's reading found **9 places where the duplicates have already
> drifted apart**, five of them against the *shipped def*.

---

## 1. Fact-location matrix

`R` = `faction_roster_v2.md` · `S` = `FACTION_SPEC.md` · `W` = `faction_world_spec.md` ·
`B3` = `faction_stage3_buildable_spec.md` · `EQ` = `faction_equipment_guidance.md` ·
`RS` = `faction_religions_spec.md` · `RG` = `faction_religions.md` ·
`PK` = `pawnkind_roster.md` · `FU` = `force_users_build_spec.md` ·
`AW` = `ASHKARR_WORLD_DEFINITION.md` · `PY` = `ashkarr_settle.py` · `XML` = the shipped def.

| # | fact-class | stated in | copies | status |
|---|---|---|---:|---|
| 1 | which factions exist (12 / 14 / 13) | R:31,35 · S:32 · W:28,49 · B3 · RS:1150 · RG · PK:10 · EQ:27 | **8** | ⚠️ three different counts in circulation (12 / 13 / 14), each correct under its own definition, none of which is stated where the number is |
| 2 | vessel (PATCH-vanilla vs AUTHORED) | R:566,719… · S:36-48 · W:56 · B3:190-200 · FU:612,919 | **5** | 🔴 **drifted — see C1** |
| 3 | `defName` | S:36-48 · AW:210 · PY:PLAN() | **3** | agree |
| 4 | settlement count, per faction | R (per-dossier) · S (weight comments) · W:56 · AW:210 · PY | **5** | agree per-faction; 🔴 **totals disagree — C2** |
| 5 | settlement TOTAL for the planet | R:364 (**64**) · W:32,190 (**72**) · AW:210 (**72**) | **3** | 🔴 **C2** |
| 6 | `settlementGenerationWeight` | S only | 1 | ✅ single-homed |
| 7 | goodwill toward player | R (per-dossier) · W:51-64 | **2** | agree (both mark it `[v2]`/cut) |
| 8 | `permanentEnemy` | R:103 · S:112,315… · W:34 · B3:274,437 · XML | **5** | 🔴 **drifted — C3** |
| 9 | `techLevel` | R · S · B3 | **3** | 🔴 **drifted — C4** |
| 10 | `leaderTitle` | S · W:91-104 · B3 · XML | **4** | 🔴 **drifted — C5** |
| 11 | named leader | W:45-56 only | 1 | ✅ single-homed (but see C5) |
| 12 | `colorSpectrum` | S:513-521 (R22) | **1** | ✅ **the only clean fact in the cluster** |
| 13 | xenotype / racial mixture | R (per-dossier) · W:312-338 · B3:240+ · S:633-764 (R27/R28) | **4** | 🔴 **drifted hard — C6** |
| 14 | pawn kinds / the 4 roles | PK · EQ:38 · S:365-500 · R ("Pawn-group patterns") · B3 | **5** | agree on shape; PK is the executable one |
| 15 | equipment / weaponTags / money | EQ:150+ · PK:31 · R ("Typical equipment") · B3 | **4** | EQ and PK agree; R is prose-only |
| 16 | religion NAME (`ideoName`) | RG · RS · R ("Belief system") · S:47,318 · XML | **5** | 🔴 **worst in the cluster — C7** |
| 17 | memes / precepts | RG · RS · R | **3** | 🔴 **drifted — C8** |
| 18 | Jedi / Sith placement | R:6-18,229-239 · FU:1219+ · S:107,250 | **3** | agree (R's header ruling reconciles it) |

---

## 2. What each document is actually FOR

| file | its real job | verdict |
|---|---|---|
| `faction_roster_v2.md` (2,579 ln) | **three documents in one trench coat.** ① a rulings header + 10 "Global systems" (lines 1–398), ② twelve narrative dossiers (399–2,365), ③ an implementation checklist, species-coverage audit and a salvaged 2026-08-06 GM appendix (2,366–2,579) | **split at the seams** — lines 398 and 2,365 |
| `FACTION_SPEC.md` (830 ln) | **the engine layer.** Says so itself: *"where they disagree about a FIELD, this file wins"*. Holds R16–R28, the only `colorSpectrum` table, the only defName table | ✅ **keep — this is the spine** |
| `faction_world_spec.md` (593 ln) | states the desired end state. **§4 onward is self-marked `🔴 SUPERSEDED, 2026-08-19`** (~410 of 593 lines, 70%) — latitude-band geography plus a worldgen-era ocean study, both dead under the no-worldgen ruling | **harvest §1-3 + §7, retire the rest** |
| `faction_stage3_buildable_spec.md` (542 ln) | a 2026-08-13 translation of the roster into engine terms — **predates the 08-13 canon-name ruling and the whole xenotype repair (R28)**. It is the *only* file that flips Junkers `permanentEnemy` to true | 🔴 **stale rival to `FACTION_SPEC.md`; same job, older facts** |
| `faction_equipment_guidance.md` (178 ln) | the *reasoning* behind the pawn-kind design (equipment lives on `PawnKindDef`; per-faction-by-role; the 4 roles) | **fold into `pawnkind_roster.md`** |
| `pawnkind_roster.md` (171 ln) | **a machine input.** `src/RimMandrake/Utils/gen_pawnkind_roster.py` parses it and writes `Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml` | 🔒 **do not merge — format is load-bearing** |
| `faction_religions.md` (271 ln) | seed prose for the eleven religions | **redundant — fully superseded, and wrong in places the spec corrects** |
| `faction_religions_spec.md` (1,153 ln) | **a machine input.** `validate_ideoligion.py --md` and `design_doc_render.py` both read it | 🔒 **do not merge** |
| `force_users_build_spec.md` (1,245 ln) | `[v2]` research pass on two uninstalled mods + the owner's NPC-only ruling | ✅ **keep standalone** — self-contained, and mostly IL/mod evidence nothing else holds |

---

## 3. 🔴 CONTRADICTIONS — live bugs, in severity order

### C7 · The religion names. **8 of 11 disagree, and 5 contradict the shipped def.**

The single worst finding. `faction_roster_v2.md`'s "Belief system" headings are the
**pre-2026-08-14 names** and were never updated when the religions were reworked.

| faction | `faction_religions_spec.md` | `faction_roster_v2.md` | **shipped `<ideoName>`** | who is wrong |
|---|---|---|---|---|
| Hutt Cartel | "the Reckoning of Debts" `RS:311` | "The Ledger of Power" `R:479` | `the Reckoning of Debts` — `JawaHuttCartel.xml:97` | 🔴 **R** |
| Geonosian Foundry Hive | "Meckgin" `RS:844` | "The Foundry Mandate" `R:1453` | `Meckgin` — `JawaGeonosianFoundryHive.xml:99` | 🔴 **R** |
| Wildsteam Clan | "the Green Oath" `RS:721` | "The Oath of Root and Kin" `R:1169` | `the Green Oath` — `JawaWildsteamClan.xml:83` | 🔴 **R** |
| Deepwater Compact | "the Balance" `RS:780` | "The Compact of Shared Water" `R:1306` | `the Balance` — `JawaDeepwaterCompact.xml:81` | 🔴 **R** |
| Galactic Empire | "The Rising Order" `RS:183` | "The Doctrine of Ordered Dominion" `R:612` | *(vanilla `Empire`, unpatched)* | 🔴 **R** |
| Deep Desert Tribes | "the Sun-Debt" `RS:558` | "The Covenant of Sand and Blood" `R:888` | *(patch, no ideoName)* | 🔴 **R** |
| Blackstar Company | "the Contract" `RS:965` | "The Compact of the Mark" `R:1794` | *(patch, no ideoName)* | 🔴 **R** |
| **the Junkers** | heading: "no doctrine, only the ladder" `RS:1039` **but its own XML body says** `<ideoName>the Weight</ideoName>` `RS:1055` | "The Weight" `R:2106` | `the Weight` — `JawaJunkers.xml:84` | 🔴 **RS heading, and `S:47`** |

⚠️ **The Junkers row is the proof that "the spec always wins" is not a safe merge rule.**
`FACTION_SPEC.md:47` copied the spec's *heading* into its faction table as if it were the
name — `| 12 | the Junkers | Jawa_Junkers | authored | no doctrine, only the ladder |` —
and `design/Jawa/bridge/INHABITED_DESIGN.md:497` has already had to correct itself for
doing the same. **Three documents propagated one bad heading.**
`FACTION_SPEC.md:318` also writes `ideoName The Weight` where the def is lowercase `the Weight`.

### C1 · The Empire's vessel — recorded five ways, two still wrong

Owner ruled: *"OuterRim_GalacticEmpire is no longer in the game, we patch Empire."*

| where | what it says | |
|---|---|---|
| `src/Jawa/Jawa_Patches/Patches/ImperialDesertDirectorate.xml:10-15` | *"THE VESSEL CHANGED… It now patches VANILLA `Empire`"* | ✅ correct |
| `FACTION_SPEC.md:36,101` | PATCH vanilla `Empire` | ✅ correct |
| `faction_roster_v2.md:566` | vanilla `Empire` | ✅ correct |
| `src/Jawa/Jawa_Patches/About/About.xml:32` | *"reskins **OuterRim_GalacticEmpire** into the Imperial Desert Directorate"* | 🔴 **stale — wrong def AND wrong faction name** |
| `design/V2_DREAMS.md:176` | *"`jawa/set_faction_relation` make **`OuterRim_GalacticEmpire`** hostile → `fire_incident … faction=OuterRim_GalacticEmpire`"* | 🔴 **stale — a run sheet that will execute against a def the owner removed** |
| `design/Jawa/force_users_build_spec.md:919` | live xpath `FactionDef[defName="OuterRim_GalacticEmpire"]/pawnGroupMakers/…` | ⚠️ stale, but `:791-792` strikes it through and records the ruling |

### C2 · Planet settlement total — **64 vs 72**
- `faction_roster_v2.md:364` — Strategic-balance table, **Total = 64**
- `faction_world_spec.md:32` — *"~**72** settlements across a large planet"*; `:190` *"72 holdings"*
- `ASHKARR_WORLD_DEFINITION.md:210` — *"Factions — **72** settlements"*

The gap is explained (64 predates the Trade Moot and Junkers, and uses the Empire's
**10** orbital-fiction figure instead of its **3** real surface seats) — **but neither
document states the reconciliation**, so either number can be read straight and be wrong.
Live measurement disagrees with both: `worldgen_interactive_def.md:663` records **66**.

### C3 · Junkers `permanentEnemy` — a spec that overrides an owner's ruling
- **FALSE** — `faction_roster_v2.md:103`, `:2061` *("owner's ruling 2026-08-13; hostile-but-bribable")* · `FACTION_SPEC.md:315` · `faction_world_spec.md` leader table · `JawaJunkers.xml:56`
- 🔴 **TRUE** — `faction_stage3_buildable_spec.md:437` *"permanentEnemy true // reviled, no diplomacy"* (and `naturalEnemy true`, `:438`)

`JawaJunkers.xml:14` even carries the warning: *"`permanentEnemy` MUST BE RESTATED FALSE.
`PirateBandBase` sets it TRUE."* A builder following B3 would undo the owner.

### C4 · Homestead `techLevel` — `faction_roster_v2.md:718` **Industrial** vs `faction_stage3_buildable_spec.md:292` **Ultra**

### C5 · `leaderTitle`, three factions
| faction | canon (`W:91-104`, "owner's canon 2026-08-13") + `S` | `faction_stage3_buildable_spec.md` |
|---|---|---|
| Homestead | "High Marshal" `S:154` | "councilman (unchanged — already correct)" `B3:296` |
| Jawa Trade Moot | "Prime Trader" `S:294` **vs** "First Bargainer" `W:45,98` | — 🔴 *S and W disagree with each other* |
| Blackstar | "Captain" `S:281` | "boss → guildmaster" `B3:415` |

### C6 · Xenotype mixtures — B3 is a different planet
`faction_roster_v2.md` and `faction_world_spec.md:318-321` **agree exactly** (Hutt Cartel
Nikto 22 / Gamorrean 18 / Rodian 11 …). `faction_stage3_buildable_spec.md:258-260` gives
**Nikto ~45%**, drops Rodian/Trandoshan/Aqualish/Pyke/Devaronian/Herglic entirely, and
`:281` puts **Zeltron in the Empire** where the roster has it in the Cartel. `:313` makes
the Deep Desert Tribes **~100% Tusken**, dropping three species. And `FACTION_SPEC.md:376`
finds B3's own numbers unbuildable: *"**Weequay ZERO** — the dossier's 16% has no kind."*

### C8 · Memes and precepts, roster vs spec
- Empire structure: `R:613` **"Ideological"** vs `RS` **`Structure_TheistEmbodied`**
- Hutt Cartel: `R:487` **"Slavery | Honorable"** vs `RS:472` *"`_Honorable` conflicts with `Guilty`"* ⇒ `Slavery_Acceptable`; `R:486` **"Charity | None"** vs `RS:~442` *"a positive charity precept is **unavoidable**"*
- Deep Desert Tribes: `R:900` **"Execution | Respected if guilty"** vs `RS:611` **`Execution_Required`**

### C9 · Faction count — 12 / 13 / 14 all in use
`R:31` twelve · `R:35` *"Fourteen stand on the map; twelve carry dossiers"* · `S:32` **The 14 factions** · `W:28` fourteen/twelve · `PK:10` twelve · `EQ:27` 12 · `RS:1150` twelve. Each is defensible; none of the short forms says which definition it is using.

---

## 4. Proposed target shape

**9 files → 6.** Three disappear; one is split; the spine is named once.

| # | target file | absorbs | what it costs |
|---|---|---|---|
| 1 | **`FACTION_SPEC.md`** — *the one engine layer.* Every FIELD: defName · vessel · settlement count + weight · `permanentEnemy` · `techLevel` · `leaderTitle` + **named leader** · `colorSpectrum` · `ideoName` (verbatim from the shipped def) · xenotype mixture | `faction_stage3_buildable_spec.md` (entire) · `faction_world_spec.md` §§1-3 (the reskin-vs-authored ruling + leader canon) · `faction_roster_v2.md` §§Global-systems-7,8,10 | **high, and unavoidable.** B3's field values must be *adjudicated*, not pasted — six of them are stale (C3–C6). Budget one careful pass per faction |
| 2 | **`faction_roster_v2.md`** — *fiction only.* Dossiers + Global systems 1-6, 9. **Every engine number and every religion name deleted, replaced with a pointer to (1) and (3)** | keeps its own lines 1-398 and 399-2,365 | **low.** Deletion, not reconciliation — that is what makes it the best trade |
| 3 | **`faction_religions_spec.md`** — unchanged, still the ideoligion source of truth | `faction_religions.md` (delete: fully superseded, and wrong at `RG:43`, `RG:60`) | **low.** But fix the Junkers heading first (C7) |
| 4 | **`pawnkind_roster.md`** — unchanged shape, generator input | `faction_equipment_guidance.md` as a *rationale preamble* above the generated table | **low.** EQ has exactly **one** inbound reference — from `pawnkind_roster.md` itself. ⚠️ the preamble must sit outside whatever region `gen_pawnkind_roster.py` parses |
| 5 | **`ASHKARR_WORLD_DEFINITION.md` §7** — unchanged: *where* each holding sits (tile-level) | — | none. Placement is a different job from field values; keeping it separate is correct |
| 6 | **`force_users_build_spec.md`** — unchanged, `[v2]`, standalone | — | none |
| ✂️ | **retire** `faction_world_spec.md` | §4-end is already self-marked `🔴 SUPERSEDED, 2026-08-19` (70% of the file); §§1-3 + §7 move to (1) | **medium.** `src/RimMandrake/Utils/ashkarr_settle.py:34` names it in a comment; `V1_CHAIN.md` ×2, `ASHKARR_WORLD_DEFINITION.md` ×3, `V2_DREAMS.md` ×2, `hiding_the_gravship.md` ×2 all cite it — all as *"superseded by"*, so the citations survive a tombstone |
| ✂️ | **retire** `faction_stage3_buildable_spec.md` | into (1) | **low inbound cost** — 5 refs, all internal to this cluster + `V1_CHAIN.md` |
| ✂️ | **delete** `faction_religions.md` | into (3) | ⚠️ **6 inbound refs incl. `validate_ideoligion.py` and 4 skill reference files** — check each before deleting |

**Cost per new fact, before and after:**

| record one new fact about one faction | today | after |
|---|---|---|
| a field value (goodwill, techLevel, leaderTitle) | **3-5 files** | **1** (`FACTION_SPEC.md`) |
| a religion name | **5 files** | **1** (`faction_religions_spec.md`) → def |
| a settlement count | **5 files + 1 script** | **2** (count in `FACTION_SPEC.md`, tile in `AW` §7) |
| a xenotype mixture | **4 files** | **1** |

### ⭐ The single highest-value merge

> **`faction_stage3_buildable_spec.md` → `FACTION_SPEC.md`.**

**Why it wins:** it is the only merge that *removes a source of wrong answers* rather
than merely tidying. B3 is the sole dissenting voice on **five** of the drifted facts
(C3 Junkers `permanentEnemy`, C4 Homestead `techLevel`, C5 three `leaderTitle`s, C6 the
whole xenotype layer) and it is stale on every one of them — it predates the 2026-08-13
canon ruling and the R28 xenotype repair. It also *duplicates FACTION_SPEC's declared
job*: both are "the buildable spec", and the project has two of them.

**What it costs:** ~540 lines, but the work is **adjudication, not concatenation** — for
each of the 12 factions, decide which value survives, and B3 loses on every field checked
so far. Budget the real cost as *twelve rulings*, not twelve copy-pastes. Two things in
B3 must be carried across verbatim, not summarised: **§0a, the BTD REMIX xenotype-family
decision** (measured: 70 species / 20.5 genes avg / max 34, against `guy762` 58/15.6/30
and Outer Rim 44/8.3/18), and **§6, the conceded "EXISTENCE ≠ SPAWNABILITY" review**.

**What it saves:** a builder reading `FACTION_SPEC.md` today can still be overruled by a
peer reading B3 — and would ship a permanently-hostile Junkers faction against an explicit
owner ruling. The merge closes that.

---

## 5. ⛔ DO-NOT-MERGE — these survive verbatim or not at all

| what | where | why |
|---|---|---|
| **`pawnkind_roster.md` as a whole file** | — | 🔒 `src/RimMandrake/Utils/gen_pawnkind_roster.py` **parses it and writes real XML** to `src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`. Its markdown *shape* is an interface |
| **`faction_religions_spec.md` as a whole file** | — | 🔒 `validate_ideoligion.py --md` and `design_doc_render.py:447` both read it by path. Renaming or restructuring breaks two tools |
| **Owner's Force ruling** | `force_users_build_spec.md:1219-1245` | *"The player never becomes a Force user. Not late, not rarely, not as a reward."* Plus its build consequence — the xenotype must be unrecruitable and unbreedable |
| **Owner's vessel ruling** | quoted at `force_users_build_spec.md:792`, `mods/required_mods.md:774` | *"OuterRim_GalacticEmpire is no longer in the game, we patch Empire."* C1 shows it is still not fully propagated |
| **Owner's reskin-vs-author ruling** | `faction_world_spec.md:13-15` | *"We keep and reskin/rename factions only when they are wired into specific game events or functions we can't change… no inheriting strange stuff."* Must move to `FACTION_SPEC.md` word for word before `faction_world_spec.md` is retired |
| **Owner's big-and-sparse ruling** | `faction_world_spec.md:17-19` | *"It should be a BIG world but the settlements are quite sparse…"* Same |
| **Owner's canon leaders and titles** | `faction_world_spec.md:45-56, 91-104` | 🔴 dated *"owner's canon, 2026-08-13"*, and the **only** home of all twelve named leaders. Losing this loses irreplaceable authored content |
| **Owner's Junkers ruling** | `faction_roster_v2.md:2061`, `FACTION_SPEC.md:315` | *"hostile-but-bribable"* — B3 already contradicts it (C3); the merge must not import B3's version |
| **Owner's Junkers siting ruling** | `ASHKARR_WORLD_DEFINITION.md:220` | 🔴 2026-08-18, explicitly *"a new ruling"* not present in any earlier doc |
| **Rulings R16-R28** | `FACTION_SPEC.md:10-30, 553-764` | R24a (child list appends), R27 (`xenotypeSet` inherit trap), R28 (every `BTD_*` name broken, repaired 2026-08-15) are measured findings that cost a load each |
| **R16/R17/R18/R19 rationale** | `FACTION_SPEC.md:12-30` | R19 in particular: keep `Jawa_IndigenousTribes` because *"renaming a live defName risks the world and buys nothing"* |
| **The measured ocean study** | `faction_world_spec.md:509-560` | Three real saves with tile counts (43.1% / 49.1% / 55.3%) and the `WaterCovered = elevation <= 0` finding. **Superseded as guidance, still evidence** — tombstone it, do not delete |
| **B3 §0a xenotype-family measurement** | `faction_stage3_buildable_spec.md:16-60` | 70/58/44 species counts across three mod families, measured against the 574-mod dump |
| **B3 §6 EXISTENCE ≠ SPAWNABILITY** | `faction_stage3_buildable_spec.md:500+` | A conceded review; the correction is the value |
| **`ashkarr_settle.py`'s PLAN()** | `src/RimMandrake/Utils/ashkarr_settle.py:41-110` | A run sheet that **executes**. Its per-faction counts and masks must not be edited to match a doc; the doc gets edited to match it, or the world moves |

---

## 6. Fix these regardless of whether anything merges

1. 🔴 **`faction_roster_v2.md`'s eight stale religion names** (C7) — five contradict a shipped `<ideoName>`.
2. 🔴 **`FACTION_SPEC.md:47`** — `no doctrine, only the ladder` is the *characterisation*; the name is `the Weight`. Already corrected once downstream at `INHABITED_DESIGN.md:497`.
3. 🔴 **`FACTION_SPEC.md:318`** — `The Weight` vs the def's lowercase `the Weight`.
4. 🔴 **`faction_religions_spec.md:1039`** — heading disagrees with its own XML body at `:1055`.
5. 🔴 **`design/V2_DREAMS.md:176`** — a run sheet still firing raids at `OuterRim_GalacticEmpire`.
6. 🔴 **`src/Jawa/Jawa_Patches/About/About.xml:32`** — still describes the patch as reskinning `OuterRim_GalacticEmpire` into the "Imperial Desert Directorate"; both are now wrong.
7. ⚠️ **`faction_stage3_buildable_spec.md:437`** — `permanentEnemy true` against an owner ruling. If the merge is not done today, put a 🔴 superseded banner on this file.
8. ⚠️ **Reconcile 64 / 66 / 72** (C2) in whichever file survives, and say which definition each number uses.

# The rubric — judging a religion

_Cited by `SKILL.md` §5. Every count here was measured 2026-08-14 against the live
dump (`2026-08-14T08:20:26Z, game 1.6.4871 rev591` — 136 memes · 685 precepts · 41
styles · 585 active mods) and the eleven religions in
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`._

## 1. Two verdicts. Never merge them.

**VALIDITY** answers *does this religion exist?* — mechanical, falsifiable, binary.
**INTEREST** answers *would a player notice?* — counted, out of 18.

🔴 **A single merged "quality" score destroys the only information either carries.**
It cannot distinguish *a brilliant design with one `exclusionTag` collision* (fix:
delete a meme, five minutes) from *a mechanically perfect religion nobody meets*
(fix: redesign). Measured: Blackstar is `INVALID` on one `conflictingMemes` line and
the Junkers on two — but Blackstar scores 8/18 and the Junkers 2/18. One is a typo,
the other a design decision; a merged score ranks them adjacent.

**Verdict form, exactly:**

```
VALID/INVALID · interest N/18 · <one sentence naming the single thing that would most improve it>
```

**Sentence rule:** `INVALID` → name the validity fix. `VALID` → name the cheapest
lift on the lowest-scoring axis. Never both.

## 2. VALIDITY — you do not judge this, you run it

```bash
python3 src/RimMandrake/Utils/validate_ideoligion.py --md design/Jawa/worldbuilding/faction_religions_spec.md
python3 src/RimMandrake/Utils/validate_ideoligion.py --xml <FactionDefs.xml>   # or a directory
```

Exit 0 = `VALID`. Any `🔴 ERROR` = `INVALID`. `WARN`/`INFO` never change it.

🔴 **`INVALID` is not a low score. It is the statement that the religion the document
describes does not exist.** An exclusion collision does not degrade a religion — the
generator drops a meme and builds something else, silently. Still score interest (it
says whether the fix is worth making), but **never write "strong despite minor
validity issues". Report one line per error, verbatim from the script:**

```
🔴 ERROR precept/conflicting-meme     Apostasy_Horrible lists ['Guilty'] in conflictingMemes — hard exclusion
```

**Baseline: 2 of 11 are VALID** — faction 6 (Wildsteam) and faction 7 (Compact). The
other nine carry 1–3 errors, dominated by `precept/required-meme` (10 occurrences).

## 3. INTEREST — six axes, 0–3 each, 18 total

**Every axis has a stated measurement. If you can score one by feel, you scored the
wrong thing.** Reproduce every count with §6.

🔴 **The ceiling is encounters per campaign, not prose.** Two caps, applied after
summing: **FRICTION 0 → total capped at 6/18** (axes 2–6 describe the shape of
something never met); **FRICTION 0 and VISIBILITY 0 → capped at 3/18**.

### Axis 1 · FRICTION — how often does it fire?

*How many distinct in-play events does this doctrine hook?*

**Measure.** Per precept, count distinct `eventDef` values across its `comps` in
`PreceptDef.json`, **capped at 4 per precept**; sum. The cap exists because the
`Charity_*` family alone carries 16–17 `eventDef`s (every beggar, refugee-pod and
pilgrim quest variant) — `Charity_Worthwhile` supplies 16 of the Ascendant Helix's
17 raw events, 94%, and would otherwise decide the axis alone.

| score | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **capped events** | 0 | 1–5 | 6–12 | 13+ |

**Top:** faction 3 Homestead — **16**. **Bottom:** faction 11 Junkers — **0**; seven
of its eight precepts have `comps: []`, including `Cannibalism_Acceptable`,
`Corpses_DontCare`, `Execution_DontCare` and `Slavery_Acceptable`.

### Axis 2 · COLLISION — does it contradict the player?

*On how many things the Jawa clan actually does does it take the opposite side?*

**Measure.** The **player-contact issue set** is fixed — nine `IssueDef`s where the
clan's practice is settled in
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\restraining_bolt_doctrine.md` and
`design/Jawa/worldbuilding/ideoligion/APPROVED.md`:

| issue | the clan's side |
|---|---|
| `Slavery` | **takes it** — restraint-bolt labour is the economy |
| `Charity` | **low** — "begging is contemptible; beggars are enslavement fodder" |
| `Raiding` | **takes it** — scavengers strip wrecks and holdings |
| `Cannibalism` | **abhorrent** for organics; droid salvage is free |
| `Corpses` / `OrganUse` | **salvage** — the discarded is the resource |
| `IdeoDiversity` | holds one fixed faith |
| `Proselytizing` | will be preached at |
| `TreeCutting` / `Mining` | extracts by reflex |
| `Nomadic` | the gravship moves |

Count the religion's precepts taking the **opposite** side on one of those nine. **A
contradicting precept counts double if it carries a `PreceptComp_UnwillingToDo*` comp
or `impact: High`** — those bind an actor rather than nudge a mood.

| score | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **contradictions** | 0 | 1–2 | 3–4 | 5+ |

**Top:** faction 6 Wildsteam — **7** (`TreeCutting_Prohibited` High+refusal ×2,
`KillingInnocentAnimals_Abhorrent` High+2 refusals ×2, `Slavery_Abhorrent` refusal
×2, `Mining_Disapproved` ×1). **Bottom:** factions 8 Geonosian and 2 Hutt — **0
each**. Every position Meckgin takes (`Slavery_Honorable`, `OrganUse_Acceptable`,
`Corpses_DontCare`, `Execution_DontCare`) is the side the clan is already on. The
Foundry Hive never disagrees with the player about anything.

### Axis 3 · VISIBILITY — without opening the ideo tab

*How many channels reach a player who never reads a religion?*

**Measure.** Count the **four channels** the religion lights up; score = count, 4 → 3.

1. **Visual** — `Σ len(thingDefStyles)` across its `StyleCategoryDef`s **≥ 80**
   (roster median 83; range 0–163).
2. **Behaviour toward the player** — a non-neutral `Raiding`/`VME_Raiding_*` or
   `IdeoDiversity_*` precept. `IdeoDiversity_Standard` is neutral and does not count.
3. **Refusal** — ≥ 1 `PreceptComp_UnwillingToDo*` in the precept set.
4. **Preaching** — a `Proselytizing_*` or `Conversion_*` precept.

⚠️ **Report the raw style total whenever it lands within 10% of 80** — that
threshold is a measured median, not a law.

**Top:** faction 1 Empire — **3**: 125 style things (`VME_Authoritarian` 47 +
`Techist` 78), `IdeoDiversity_Abhorrent`, `Proselytizing_Frequently`. **Bottom:**
faction 11 Junkers — **0**: `AM_Scavenger` 60 (under threshold), no raiding or
diversity position, no refusal, no preaching. ⚠️ Faction 7 Compact scores its visual
channel 0 for a reason worth naming — `VME_SecularSpirituality` has
`thingDefStyles: []`, so its only style category renders nothing at all.

### Axis 4 · DISTINCTNESS — the name-blind test, scored

*Could this be swapped with its neighbour and nobody notice?*

**Measure, two terms. (a)** Max pairwise Jaccard `J` on `memes ∪ precepts` against
every other religion in the roster — the validator's `distinctiveness()`.

| score | 3 | 2 | 1 | 0 |
|---|---|---|---|---|
| **max J** | ≤ 12% | 13–24% | 25–33% | ≥ 34% |

**(b) −1** if the nearest neighbour holds the **same side on ≥ 3 issues from the
player-contact set** above. Floor 0.

Roster max-J: Empire 8% · Wildsteam 8% · Tuskens 9% · Droids 18% · Helix 18% ·
Geonosian 19% · Junkers 19% · Hutt 20% · Blackstar 20% · Homestead 24% · Compact 24%.
Median across all 55 pairs: **4.0%**.

**Top:** faction 6 Wildsteam — 8%, sharing only `NaturePrimacy` and
`Structure_Animist` with the Deep Desert Tribes, no penalty → **3**. **Bottom:**
factions 3 and 7 — 24% with each other (band 2) and sharing `Slavery_Abhorrent`,
`VME_Raiding_Abhorrent` and `IdeoDiversity_Standard`, three contact positions on the
same side → both **1**.

#### The name-blind procedure — run it, do not feel it

1. Run the validator over the **whole roster in one call** and read the `name-blind
   test` block (it prints pairs at J ≥ 34%). **Empty is not a pass** — compute the
   full matrix with §6 and take the top three pairs.
2. For each religion in a pair build a **contact card**: one row per precept sitting
   on the player-contact issue set, columns `issue · position · capped events ·
   impact`. **Strip every proper noun** — no faction, ideo, deity or style name.
3. Give both cards to a second reader (a peer seat is fine) and ask three questions:
   *which one raids you · which one trades with you · which one costs you goodwill,
   and for what.*
4. **The pair fails if the reader cannot assign both cards.** The failing member is
   whichever has fewer non-neutral positions on the contact set — that one is the
   decoration.
5. **Measured today, Homestead ~ Compact fails.** Both are water-primacy pacifist
   traders holding `Slavery_Abhorrent` + `VME_Raiding_Abhorrent` +
   `IdeoDiversity_Standard` + a positive `Charity`. The card-level difference reduces
   to `Ranching_Central`/`RoughLiving_Welcomed` versus
   `Fishing_Sacred`/`Apostasy_Abhorrent`. The Compact carries the extra `Apostasy`
   position, so **the Homestead is the decoration.**

### Axis 5 · DECISION or MOOD — does anything have teeth?

*Does the doctrine ever stop an action, or only move a number?*

**Measure.** `D` = (count of `PreceptComp_UnwillingToDo*` comps across the precept
set) + (count of precepts with `impact: "High"`).

| score | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **D** | 0 | 1–2 | 3–5 | 6+ |

**Top:** faction 6 Wildsteam — **8** (6 refusals + 2 High); `TreeCutting_Prohibited`
alone contributes two `UnwillingToDo` comps (`CutTree`, `VOE_JoinLoggingOutpost`).
**Bottom:** factions 1, 9, 10, 11 — **0 each**. The Empire's eight precepts contain
no refusal and no High-impact entry: the Unmoving Noon is entirely mood and goodwill.
Surfacing that about the roster's flagship religion is what the axis is for.

### Axis 6 · EXPRESSIBILITY — can the engine say it?

*How much of the written doctrine reaches the game at all?*

**Measure, two terms. (a)** Inert fraction `I` = precepts with `comps: []` ÷ precepts
listed — the validator prints it as `interest/inert`.

| score | 3 | 2 | 1 | 0 |
|---|---|---|---|---|
| **I** | 0% | ≤ 25% | ≤ 50% | > 50% |

**(b) −1** per doctrine the entry itself marks unencodable (its own ⚠️/🔴 "cannot be
written" markers). Floor 0.

**Top:** faction 10 Blackstar — `I = 0/7` → 3, minus one for the entry's own *"the
'disapproved' the fiction wanted is not encodable"* on `Charity` → **2**. Faction 7
is the roster's only other `I = 0/8`, also dropping to 2 for the unencodable Quarren
fracture. **Bottom:** faction 8 Geonosian — `I = 6/8` (75%) → 0, and it also carries
the impossible `PreferredXenotype` route → **0**. Six of Meckgin's eight precepts are
tooltips.

## 4. What this rubric deliberately does NOT score

**Do not add these back. Each was left out on purpose.**

- **Prose quality.** The Junkers' three paragraphs are the best writing in the eleven
  and the religion scores 2/18. The instrument is working.
- **Lore depth / canon fidelity.** A different review, against
  `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_roster_v2.md`.
- **Internal fictional consistency for its own sake.** A doctrine that contradicts
  itself but fires 16 events beats an airtight one that fires 2.
- **Meme impact as a rating.** `MemeDef.impact` is a *budget* — structure memes are
  all 0, roster totals run 5–9. High impact is not high quality.
- **Precept count.** All eleven list eight. It told us nothing.
- **Whether the reviewer likes it.**

## 5. Worked examples, end to end

### 5a · Strong — faction 6, Wildsteam Clan, *the Green Oath*

**VALIDITY.** `--only Wildsteam` → 0 errors; six `meme/requireOne` WARNs
(`TreeConnection` wants one of `RoughLiving_Welcomed`/`Temperature_Tough`/
`GauranlenConnection_Strong`; `AnimalPersonhood` wants a `MeatEating_*` and a
`Fishing_*`). Warnings only ⇒ **VALID**.

| axis | measurement | count | score |
|---|---|---|---|
| 1 friction | capped `eventDef`s | 10 — TreeCutting 3, KillingInnocentAnimals 2, Mining 2, Slavery 2, AnimalSlaughter 1 | **2** |
| 2 collision | contradictions, doubled | 7 — TreeCutting ×2, KillingInnocentAnimals ×2, Slavery ×2, Mining ×1 | **3** |
| 3 visibility | channels | 2 — visual 163 (`Totemic` 92 + `Animalist` 71) ✅ · behaviour ❌ · refusal 6 ✅ · preaching ❌ | **2** |
| 4 distinctness | max J | 8% vs Deep Desert Tribes; no penalty | **3** |
| 5 decision | refusals + High | 6 + 2 = 8 | **3** |
| 6 expressibility | inert fraction | 2/8 = 25% (`AnimalConnection_Strong`, `Research_Slow`); 0 markers | **2** |
| | | **total** | **15/18** |

Three axes tie at 2; visibility has the most headroom, being liftable by one precept
rather than a rewrite.

```
VALID · interest 15/18 · Add a non-neutral IdeoDiversity or Raiding position — the Oath has no channel at all that reaches a player who never cuts a tree.
```

### 5b · Weak — faction 11, the Junkers, *no doctrine, only the ladder*

Project work, well written, near the floor. **That is the point of the instrument.**

**VALIDITY.** Two errors:

```
🔴 ERROR precept/required-meme        RoughLiving_Welcomed requires one of ['TreeConnection', 'PainIsVirtue', 'AM_Monastic', 'Nomadism', 'VME_Nomad', 'VVE_Travelers']; none is in the meme set
🔴 ERROR precept/required-meme        Comfort_Ignored requires one of ['PainIsVirtue']; none is in the meme set
```

⇒ **INVALID.** The generator drops both precepts; the religion as written does not
exist.

| axis | measurement | count | score |
|---|---|---|---|
| 1 friction | capped `eventDef`s | **0** — not one precept carries an `eventDef` | **0** |
| 2 collision | contradictions, doubled | 1 — `Cannibalism_Acceptable` vs the clan's abhorrence (Low, no refusal) | **1** |
| 3 visibility | channels | 0 — `AM_Scavenger` 60 (< 80) ❌ · no raiding/diversity ❌ · no refusal ❌ · no preaching ❌ | **0** |
| 4 distinctness | max J | 19% vs Geonosian (band 2) sharing `Corpses_DontCare` + `Execution_DontCare` + same-side `Slavery` → −1 | **1** |
| 5 decision | refusals + High | 0 + 0 = 0 | **0** |
| 6 expressibility | inert fraction | 7/8 = 88% | **0** |
| | | **total** | **2/18** |

Both ceilings bite (friction 0 → cap 6; friction and visibility both 0 → cap 3) and
neither changes the number.

```
INVALID · interest 2/18 · Drop RoughLiving_Welcomed and Comfort_Ignored, whose requiredMemes the Junkers do not hold — that clears both errors at zero cost, because neither precept carries a comp anyway.
```

⚠️ **The emptiness is the design and the rubric will not reward it.** "No doctrine,
only the ladder" is a good idea about a faction; encoded as eight comp-less precepts
it produces a religion the player cannot encounter. Keep it if you want — but keep it
knowing the score, and do not argue the rubric down.

## 6. Reproducing every count

```bash
python3 - <<'EOF'
import sys, itertools
sys.path.insert(0, "src/RimMandrake/Utils")
import validate_ideoligion as V
from pathlib import Path
D = V.Dump()
rels = [r for r in V.from_markdown(Path("design/Jawa/worldbuilding/faction_religions_spec.md"), D)
        if r.get("memes") or r.get("precepts")]
f = lambda d, k: (d.get("fields") or {}).get(k)
for r in rels:                                            # axes 1, 3, 5, 6
    ps = [n for n in r["precepts"] if n in D.precepts]
    cap  = sum(min(4, len({c["eventDef"] for c in (f(D.precepts[n], "comps") or []) if c.get("eventDef")})) for n in ps)
    unw  = sum(1 for n in ps for c in (f(D.precepts[n], "comps") or []) if c["$type"].startswith("PreceptComp_UnwillingTo"))
    high = sum(1 for n in ps if f(D.precepts[n], "impact") == "High")
    sty  = sum(len(f(D.styles[s], "thingDefStyles") or []) for s in r["styles"] if s in D.styles)
    inert = [n for n in ps if not (f(D.precepts[n], "comps") or [])]
    print(f'{r["name"][:32]:34} events={cap:>3} unwill={unw} High={high} style={sty:>4} inert={len(inert)}/{len(ps)}')
for a, b in itertools.combinations(rels, 2):              # axis 4 term (a)
    A = set(a["memes"]) | set(a["precepts"]); B = set(b["memes"]) | set(b["precepts"])
    j = len(A & B) / len(A | B)
    if j >= 0.13: print(f'{j:.0%}  {a["name"][:26]} ~ {b["name"][:26]}  {sorted(A & B)}')
EOF
```

## 7. Scorecard template — copy this

```
RELIGION:  <n · faction — ideo name>
SOURCE:    <full path>            DUMP: <capturedUtc from manifest.json>

VALIDITY   validate_ideoligion.py --md <path> --only <name>
  <verbatim ERROR lines, or "0 errors">
  → VALID / INVALID

INTEREST
  axis            measurement                                        count  score
  1 friction      Σ min(4, distinct eventDefs) per precept            ___    _/3
  2 collision     contact-set contradictions (×2 if High/refusal)     ___    _/3
  3 visibility    channels: style≥80 · behaviour · refusal · preach   ___    _/3
  4 distinctness  max pairwise Jaccard (−1 if ≥3 shared positions)    ___    _/3
  5 decision      UnwillingToDo comps + High-impact precepts          ___    _/3
  6 expressible   inert fraction (−1 per unencodable doctrine)        ___    _/3
                                                            TOTAL     __/18
  ceiling?  friction 0 → cap 6   ·   friction and visibility 0 → cap 3

VERDICT
  <VALID|INVALID> · interest N/18 · <one sentence: validity fix if INVALID,
                                     else cheapest lift on the lowest axis>
```

## 8. The roster, scored — 2026-08-14 baseline

| # | religion | valid | 1 fric | 2 coll | 3 vis | 4 dist | 5 dec | 6 expr | **/18** |
|---|---|---|---|---|---|---|---|---|---|
| 6 | Wildsteam Clan | ✅ | 2 | 3 | 2 | 3 | 3 | 2 | **15** |
| 3 | Homestead Defense League | ❌ | 3 | 3 | 2 | 1 | 2 | 2 | **13** |
| 4 | Deep Desert Tribes | ❌ | 2 | 1 | 2 | 3 | 2 | 2 | **12** |
| 7 | Deepwater Compact | ✅ | 3 | 3 | 1 | 1 | 2 | 2 | **12** |
| 1 | Galactic Empire | ❌ | 2 | 1 | 3 | 3 | 0 | 2 | **11** |
| 5 | Free Droid Enclaves | ❌ | 2 | 2 | 1 | 2 | 2 | 1 | **10** |
| 10 | Blackstar Company | ❌ | 2 | 1 | 1 | 2 | 0 | 2 | **8** |
| 2 | Hutt Cartel | ❌ | 1 | 0 | 2 | 2 | 1 | 1 | **7** |
| 9 | Ascendant Helix | ❌ | 1 | 1 | 2 | 2 | 0 | 1 | **7** |
| 8 | Geonosian Foundry Hive | ❌ | 1 | 0 | 1 | 1 | 1 | 0 | **4** |
| 11 | the Junkers | ❌ | 0 | 1 | 0 | 1 | 0 | 0 | **2** |

**Recompute whenever the spec or the load order changes** — every band is keyed to
the live dump, and one mod added or removed moves the counts.

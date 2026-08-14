# validation.md — proving a religion is what the document says

Cited by `SKILL.md` §4. Two halves and they answer different questions.

| half | question | cost | authority |
|---|---|---|---|
| **offline** | is every defName legal, and is this combination *buildable*? | < 1 s | `src/RimMandrake/Utils/validate_ideoligion.py` against the live def dump |
| **`live`** (§5 below) | did the game actually **build** it? | one load, ~23–30 min | the Ideoligions tab · `Player.log` · the bridge |

🔴 **Offline can never prove the second question.** An `Ideo` is a runtime object;
XML only constrains generation. Everything the offline gate can say is "nothing
here forbids the religion you described" — never "the religion exists".

---

## 1. What the validator reads

`/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils/validate_ideoligion.py`

Ground truth is the **live def dump**, i.e. all mods resolved:
`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs/`
— `MemeDef.json`, `PreceptDef.json`, `IssueDef.json`, `StyleCategoryDef.json`,
`RitualPatternDef.json`. Missing any one of these is a hard `sys.exit` with
*"run a def dump from the live game first"*. Capture stamp is read from
`…/DefDump/manifest.json` and printed on line 1 — **read it; a stale dump is a
stale verdict.**

Active-mod set comes from
`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml`.
⚠️ `_active_mods()` walks **every** `<li>` in that file, not just `activeMods`,
so `knownExpansions` entries land in the set too (585 unique from 590 `<li>`,
measured 2026-08-14). Harmless — expansions really are active — but it is not a
strict read of `activeMods`.

Vocabulary cross-reference for humans:
`/mnt/d/Luke/dev/Rimworld/design/Jawa/worldbuilding/data/ideology_palette.md`
(136 memes · 685 precepts · 41 styles · 92 ritual patterns, same capture).

### Three input routes

| flag | accepts | populates `precepts`? | `target` |
|---|---|---|---|
| `--spec f.json` | `{"religions":[…]}` — the full model | ✅ you write them | `faction` (default) or `player` |
| `--md f.md` | the `faction_religions_spec.md` shape | ✅ from the precept tables | always `faction` |
| `--xml f.xml` *or a directory* | `FactionDef` blocks, split into **held** and **candidate** memes (§2) | ❌ **never — no XML field lists precepts** | always `faction` |

`--md` is a **best-effort extractor**, not a parser. It splits on headings
matching `^## <digits> [·.] <title>` and reads only structured table rows —
`| **structure** |`, `| **memes** |`, `| **styles** |`, `| **fixedIdeo** |`, and
three-column rows under a line containing `**precepts`. Backticked names in
prose are ignored by design. Deities are counted as
`line.count("<name>")` over the whole section — an XML snippet quoted for any
other reason inflates it.

🔴 **`--md` silently drops a meme typo that has no underscore.** The last line of
`from_markdown` keeps a name only `if n in D.memes or "_" in n`, so
`OuterRim_DroidPrimacy` survives to be reported as unknown but `Loyalisttt`
vanishes without a word. Modded names almost always contain `_`; vanilla ones
mostly do not. **Typos in vanilla meme names are invisible to `--md`.** Use
`--spec` when the answer must be complete.

---

## 2. Usage — measured 2026-08-14

```bash
cd /mnt/d/Luke/dev/Rimworld
python3 src/RimMandrake/Utils/validate_ideoligion.py --md design/Jawa/worldbuilding/faction_religions_spec.md
python3 src/RimMandrake/Utils/validate_ideoligion.py --xml <FactionDefs.xml or a dir>
python3 src/RimMandrake/Utils/validate_ideoligion.py --spec my_religion.json
```

Options: `--only <substring>` filters by religion name · `--impact-budget N`
turns the impact total into an ERROR above `N` (**pass only a measured cap**;
`DEFAULT_IMPACT_BUDGET` is deliberately `None`).

**Exit codes: `0` = no ERROR anywhere · `1` = at least one ERROR, *or* the input
yielded no religions at all.** WARN and INFO never change it. ⚠️ Piping through
`head` replaces the exit code with `head`'s — redirect to a file if you are
gating on it.

Real run, the project's eleven-religion spec (trimmed):

```
validate_ideoligion — 11 religion(s) against the live dump (2026-08-14T08:20:26Z, game 1.6.4871 rev591)
  skipped 1 empty section(s): ["12 · Jawa Gravship Expedition — the owner's"]
  136 memes · 685 precepts · 41 styles · 585 active mods

=== 1 · Galactic Empire — the Unmoving Noon — INVALID
     INFO  def/needs-mayrequire      VME_GodEmperor → MayRequire="vanillaexpanded.vmemese"  (Vanilla Ideology Expanded - Memes and Structures)
  ⚠️  WARN  deity/missing             Structure_TheistEmbodied requires 2..4 deities and none are named — the generator will invent them
  🔴 ERROR meme/exclusion            Loyalist + Supremacist all carry exclusionTag 'GroupRelation' — they cannot coexist
     INFO  meme/impact               total impact 5 over 5 memes (Structure_TheistEmbodied:0, VME_GodEmperor:1, Loyalist:1, Supremacist:1, HumanPrimacy:2)
  🔴 ERROR precept/required-meme     Proselytizing_Frequently requires one of ['Proselytizer']; none is in the meme set
  ⚠️  WARN  interest/inert            2 precept(s) with NO comps — a tooltip, not a mechanic: ['Slavery_Acceptable', 'Research_Fast']
…
2/11 VALID. INVALID: ['1 · Galactic Empire …', '2 · Hutt Cartel …', … 9 names]
```
exit **1**. Verdicts 2026-08-14: 6 (Wildsteam) and 7 (Deepwater) VALID, the other
nine INVALID; section 12 is the deliberate empty Jawa slot and is skipped.

**No FactionDef XML exists anywhere in this repo** — `grep -rl '<forcedMemes\|<fixedIdeo\|<requiredMemes\|<structureMemeWeights' --include='*.xml' .`
returns nothing (2026-08-14). The eleven religions are spec-only. The `--xml`
route was therefore exercised against vanilla:

```
$ … --xml '/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Anomaly/Defs/FactionDefs/Factions_Misc.xml'
=== Nightmare Deep  [Factions_Misc.xml] — VALID
  ⚠️  WARN  deity/structure-generates-none 1 deity(s) named on Structure_Archist, which has deityCount 0. …
     INFO  meme/impact               total impact 5 over 3 memes (Structure_Archist:0, Inhuman:3, Ritualist:2)
1/1 VALID. No errors.                                                    exit 0
```

### 🔴 HELD vs CANDIDATE — the distinction the whole `--xml` route turns on

A `FactionDef` names memes in two families that mean **opposite** things, and the
script keeps them in two buckets:

| bucket | XML fields | meaning | checked for |
|---|---|---|---|
| **held** — `rel["memes"]` | `forcedMemes` · `requiredMemes` | the religion **holds all of these at once** | everything: existence **and** coexistence |
| **candidate** — `rel["candidateMemes"]` | `allowedMemes` · `structureMemeWeights` children | a **menu the generator draws a remainder from**; entries are alternatives and are *not* expected to coexist | existence only, plus one WARN (below) |

Coexistence checks — `meme/exclusion`, `structure/multiple`,
`precept/conflicting-meme`, `meme/impact-budget` — run over **held** only.
Candidates are deduplicated against held, still resolved against the dump
(`def/unknown-meme`, `def/inactive-mod`, `def/needs-mayrequire`), because a typo
in `allowedMemes` is a real bug that silently shrinks the menu.

⚠️ **Until 2026-08-14 the two were merged, and the Empire read INVALID** on
`meme/exclusion MaleSupremacy + FemaleSupremacy … 'GenderSupremacy'` — a faction
that *constrains a generated* religion rather than authoring one. Ludeon's Empire
was never broken. Fixed; the run now reads:

```
$ … --xml '…/Data/Royalty/Defs/FactionDefs/Faction_Empire.xml'
=== Empire  [Faction_Empire.xml] — VALID
     INFO  structure/generated  no structure meme is held; the generator picks one from ['Structure_Archist'] (weighted)
     INFO  meme/impact          total impact 2 over 2 memes (Collectivist:1, Loyalist:1; + 4 candidate(s) the generator may add)
1/1 VALID. No errors.                                                    exit 0
```

Held is `{Collectivist, Loyalist}` — the `requiredMemes` — and the five
`allowedMemes` plus the one weighted structure are candidates. A faction offering
three weighted structures likewise no longer draws a false `structure/multiple`.

⇒ **`--xml` is now trustworthy on the `allowedMemes` family too.** Two things it
tells you that are *not* errors and are easy to misread: `structure/generated`
(ℹ️, the structure is the generator's to pick) and the candidate suffix on
`meme/impact` (candidate impacts are **not** summed — they never coexist).

---

## 3. The offline gate, check by check

33 finding codes, of which **17 can be ERROR**. Level in the table is the level
the code actually emits.

### Vocabulary and provenance

| code | level | proves | remedy | cannot prove |
|---|---|---|---|---|
| `def/unknown-meme` `-precept` `-style` | 🔴 | the name is in the live dump — **held and candidate memes alike**; a candidate hit is suffixed *(candidate — allowedMemes/structureMemeWeights)* | fix the name from `ideology_palette.md` | that the def is *reachable* — a def can exist and still be filtered out at generation |
| `def/inactive-mod` | 🔴 | the def's `packageId` is in `ModsConfig.xml` | enable the mod, or drop the def | ⚠️ near-unfirable in practice: the dump is *made from* the active set, so this only catches **`ModsConfig` changed since the dump was captured** |
| `def/needs-mayrequire` | ℹ️ | tells you the exact `MayRequire="…"` string to write | copy it into the `<li>` | 🔴 **it does NOT check that you wrote it.** `from_xml` reads `li.text` and never looks at attributes — a missing `MayRequire` is invisible to this script |

### Structure and deities

| code | level | proves | remedy | cannot prove |
|---|---|---|---|---|
| `structure/none` | 🔴 | exactly-one-structure rule, lower half — **only when there are no candidates at all**, i.e. a religion you authored outright | add a structure meme (35 available) | — |
| `structure/multiple` | 🔴 | upper half, over the **held** set | keep one | nothing about the candidate menu: several `structureMemeWeights` entries are a weighted pick of one (§2) |
| `structure/generated` | ℹ️ | no held structure, but a candidate menu exists — the generator picks | nothing; this is how `allowedMemes` factions work | *which* structure it will pick |
| `structure/candidate-shadowed` | ⚠️ | a held structure **and** candidate structures both present, so the weights can never apply | drop one of the two lists | which of the two you meant |
| `deity/count` | ⚠️ | named deities inside the structure's `deityCount` `IntRange` | add/remove `<deityPresets>` entries, or change structure | **WARN, not ERROR** — SKILL.md §4 implies a hard gate; it is advisory |
| `deity/missing` | ⚠️ | structure wants ≥1 and you named none | name them, or accept generated gods | whether generated names fit the fiction |
| `deity/structure-generates-none` | ⚠️ | `deityCount 0` + named deities | usually leave it — HoraxCult ships exactly this | ❓ **whether a preset on a `deityCount 0` structure actually displays.** Unresolved; it is on the §5 list |
| `deity/ok` | ℹ️ | — | — | — |

### Memes

| code | level | proves | remedy | cannot prove |
|---|---|---|---|---|
| `meme/exclusion` | 🔴 | no two **held** memes share an `exclusionTags` entry | drop one. Known real collisions: `Loyalist`+`Supremacist` (`GroupRelation`), `Transhumanist`+`VME_Fleshcrafters` (`FleshAugmentation`) | anything about candidates — two of those sharing a tag is what a menu is *for* (§2) |
| `meme/candidate-excluded` | ⚠️ | a candidate shares an `exclusionTags` entry with a **held** meme, so it can never be drawn | remove it from `allowedMemes`, or drop the held meme | whether you meant the menu entry to be dead weight. WARN by design — the game generates fine, the list is just wrong as a set |
| `meme/impact-budget` | 🔴 *(opt-in)* | total `impact` of the **held** set ≤ `N` | drop a 3-impact meme | **the real engine cap.** `MaxMemeImpact` and `MemeCountRangeAbsolute` exist as symbols in Assembly-CSharp 1.6.4871 but their values are unmeasured, so nothing is failed on a guess |
| `meme/impact` | ℹ️ | the held total and per-meme breakdown, plus a count of candidates the generator may add | — | the post-generation total. Candidate impacts are **not** summed; they are alternatives |
| `meme/requireOne` | ⚠️ | for each `requireOne` group, the spec names a member | name one, or accept the generator's pick | **the loudest and least alarming line in the output.** It is normal on almost every religion — it says *the generator chooses your doctrine here*, not that anything is wrong |

### FactionDef ConfigErrors — the two the *game* raises, mirrored offline

Added 2026-08-14. Both are real `FactionDef.ConfigErrors` in 1.6.4871, both are
ERROR here, and both need the raw lists (`allowedMemes` / `disallowedMemes` /
`requiredMemes`), which `--xml` records separately from the two meme buckets.
**Tag absent is not the same as an empty list** — the script stores `None` for an
absent tag, which is what the game tests.

| code | level | proves | remedy | cannot prove |
|---|---|---|---|---|
| `faction/both-meme-lists` | 🔴 | `disallowedMemes` and `allowedMemes` are not both defined | keep one list; a white list already excludes everything else | — |
| `faction/required-not-allowed` | 🔴 | every `requiredMemes` entry appears in `allowedMemes` | add it to `allowedMemes`, or drop it from `requiredMemes` | ⚠️ checked **only when `allowedMemes` is present** — with no white list, nothing is disallowed |

Both also appear in `Player.log` at startup (§4b) — offline is the cheaper read.

### Precepts (design artefact — see `route/precepts-unauthorable`)

| code | level | proves | remedy | cannot prove |
|---|---|---|---|---|
| `precept/conflicting-meme` | 🔴 | precept's `conflictingMemes` ∩ meme set = ∅ | drop the precept or the meme | — |
| `precept/required-meme` | 🔴 | precept's `requiredMemes` ∩ meme set ≠ ∅ | add one of the listed memes | — |
| `precept/invisible` | 🔴 | no `visible:false` precept | remove it — 33 are engine-internal | that a `visible:true` precept is *authorable* |
| `precept/npc-disabled` | 🔴 | `enabledForNPCFactions` not false (only when `target=faction`) | pick another position; 52 precepts are player-only | — |
| `precept/exclusion` | 🔴 | no two precepts share an `exclusionTags` entry | drop one | — |
| `precept/issue-duplicate` | 🔴 / ⚠️ | one position per `IssueDef`; downgraded to WARN if any precept sets `allowDuplicates` | pick one position | — |
| `precept/orphan-issue` | ⚠️ | the precept's `issue` is installed | usually a mod-version skew | — |
| `precept/count` | ℹ️ | how many count toward the precept limit | — | the limit itself is not modelled |

### Route and interest

| code | level | means |
|---|---|---|
| `route/precepts-unauthorable` | ⚠️ | fires on **every** faction religion with precepts. Not a defect — it is the reminder that `FactionDef` has no precept whitelist |
| `route/fixed-no-memes` | 🔴 | `fixedIdeo: true` with an empty meme set — the generator fills it randomly and your `fixedIdeo` bought nothing |
| `route/preceptsonly-without-fixed` | ⚠️ | `requiredPreceptsOnly` without `fixedIdeo` constrains a religion you did not author |
| `interest/live-precepts` | ℹ️ | how many precepts carry `comps` (fire thoughts), how many are `High` impact, how many produce mood or refusal |
| `interest/inert` | ⚠️ | precepts with **no comps at all** — a tooltip, not a mechanic. Feeds §5's rubric |
| *(cross-religion)* | ⚠️ | the **name-blind test**: pairwise Jaccard over memes+precepts, printed for any pair ≥ 34 % shared |

### SKILL.md §4's seven claims vs. the code

| §4 claim | status |
|---|---|
| every defName exists in the live dump | ✅ `def/unknown-*` |
| one structure meme and only one | ✅ `structure/none` · `structure/multiple` |
| no meme `exclusionTags` collision | ✅ `meme/exclusion`, over the **held** set (§2) |
| no precept `conflictingMemes` collision | ✅ `precept/conflicting-meme` |
| deity count inside `deityCount` | ⚠️ **WARN, never ERROR** — it will not turn a religion INVALID |
| no `visible:false` precept | ✅ `precept/invisible` |
| `MayRequire` on every modded def **and** its packageId active | ❌ **half.** The packageId half is `def/inactive-mod`; the *"`MayRequire` is present"* half is **not implemented** — attributes are never read |

Ten further ERROR-capable checks §4 does not mention: `def/unknown-style`,
`precept/required-meme`, `precept/npc-disabled`, `precept/exclusion`,
`precept/issue-duplicate`, `route/fixed-no-memes`, `meme/impact-budget`,
`def/inactive-mod`, `faction/both-meme-lists`, `faction/required-not-allowed`.

### What no offline check covers

- **`MayRequire` presence** (above) — the single largest hole.
- **Precept *limit*.** `countsTowardsPreceptLimit` is counted; the ceiling is not.
- **Ritual/role/style resolution.** `RitualPatternDef` is loaded and never used.
- **Whether the generator honours any of it.** That is §5.

---

## 4. live — proving the ideo was BUILT

**Three routes. One works today, one is a grep, one does not exist yet.**

### 4a. The Ideoligions tab — available today, and the only positive proof

There is a main tab window `MainTabWindow_Ideos`. Inside it, the button
`ButtonShowAllIdeoligions` → **"Show all ideoligions"**
(`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Ideology/Languages/English/Keyed/MainTabs.xml:6`)
reveals a section headed **"Faction ideoligions"** (`FactionIdeoligionSectionHeader`,
`…/Keyed/Misc_Gameplay.xml:22`). Clicking a religion opens `Dialog_Ideo`, which
lists its memes, precepts, deities and styles — the exact four things offline
cannot confirm.

Read off it, in order: **memes match `forcedMemes` exactly** (a substitution means
`fixedIdeo` did not take) → **deity names appear as written** → **styles resolved**
→ **precepts**, which you are *reading*, not verifying, because you never
specified them.

⚠️ **`hiddenIdeo: true` is the trap.** HoraxCult ships it and the field exists as
`hiddenIdeo` in Assembly-CSharp. ❓ Whether the tab filters hidden ideos out is
**unverified** — assume it does. If you need to *see* a religion on its first
load, author it without `hiddenIdeo`, confirm it, then add the flag.

**There is no dev-mode shortcut.** `Verse.DebugActionsIdeo` exists as a class, but
the only ideo debug-action label recoverable from the assembly is
`Set ideo role...`. Do not guess the rest — enumerate them live with
`rimworld/list_debug_actions` filtered on `ideo` (bridge §4) and read the labels.

### 4b. `Player.log` — cheap, and it only ever gives bad news

Harvest per `skills/rimworld-modding/references/player-log-triage.md` and
`vendor/wisdom/benign_log_errors.md` §0. Log path:
`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log`

Grep these exact strings (all verified present in Assembly-CSharp 1.6.4871 via
`strings -a -e l`):

| string | means |
|---|---|
| `Faction had no ideoligions after loading. Adding random one.` | 🔴 **the design is gone.** The loudest possible signature |
| `did not have an ideo set; assigning fallback ideo` | 🔴 same family, pawn-side |
| `Some ideoligion memes were null after loading.` | 🔴 a meme reference dropped |
| `Some ideoligion precepts were null after loading.` | 🔴 a precept reference dropped |
| `Some ideoligions were null after loading.` / `Removed null ideos` | 🔴 |
| `Ideoligion had null culture. Assigning random.` | ⚠️ |
| `Ideo has 2 memes which have conflicting ritual set requirements!` | ⚠️ a collision offline does not model |
| `No way to generate ideo symbols. Memes:` | ⚠️ |
| `Could not resolve cross-reference` | ⚠️ **read the `wanter`** — triage §3. An unwrapped modded defName lands here |
| `both disallowedMemes (black list) and allowedMemes (white list) are defined` | 🔴 `FactionDef` ConfigError — now caught offline too, `faction/both-meme-lists` |
| `has a required meme which is not allowed:` | 🔴 `FactionDef` ConfigError — now caught offline too, `faction/required-not-allowed` |

🔴 **A clean log is not proof.** The five silent modes in §5 produce **none** of
these lines. Absence of error means only "no error"; only 4a shows the ideo.

### 4c. The bridge — a real gap, not a workaround

`skills/rimbridge/SKILL.md`. The bridge can list every faction —
`jawa/list_factions`, drove live 2026-08-14, returns *defName, name, isPlayer,
hostile, goodwill, hidden* and **no ideo field**
(`/mnt/d/Luke/dev/Rimworld/src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs:4183`).
The only ideo signal anywhere in the tool surface is `factionHasIdeo` — a bare
bool, and it appears **only on the failure row of `jawa/spawn_pawn`** (same file,
`:1791`).

⏳ **`jawa/ideo_of` is requested from BRIDGE and does not exist**
(`/mnt/d/Luke/dev/Rimworld/infrastructure/state/queue/VISION.md:500`). Until it
lands, "the game built the ideoligion I specified" is read off a screenshot of
4a, by eye — it cannot be diffed. **Say "unverified", not "verified", when the
only evidence is a clean log.**

---

## 5. The silent failure modes

SKILL.md §4 names five. All produce **no red error**; the faction simply
generates something else.

| mode | symptom in game | why silent | offline check |
|---|---|---|---|
| **uninstalled defName** | faction generates without that meme; doctrine drifts | the `<li>` resolves to nothing and the list shrinks | ✅ `def/unknown-meme` / `-precept` / `-style` |
| **unwrapped `MayRequire`** | same, plus a cross-reference line if the mod is off | `MayRequire` deletes the node *before* resolution; unwrapped, it becomes a cross-ref warning nobody reads | ❌ **not checked.** `def/needs-mayrequire` tells you the string, never audits the file. Read the XML by eye |
| **meme exclusion collision** | one of the two memes is dropped at generation | `exclusionTags` is a generator filter, not a validator | ✅ `meme/exclusion` over the **held** set; a candidate colliding with a held meme is ⚠️ `meme/candidate-excluded` (§2) |
| **precept whose `requiredMemes` are absent** | the precept never appears | `PreceptMaker` skips ineligible precepts | ✅ `precept/required-meme` (and `precept/npc-disabled` for the NPC-only variant) |
| **`deityPresets` on a `deityCount 0` structure** | ❓ gods may simply not display | the structure invents none, and nothing objects to naming some | ⚠️ `deity/structure-generates-none`, WARN only — HoraxCult ships this, so it cannot be an error |

**The pattern: four of five are caught, and the one that is not — `MayRequire` —
is the one the script most looks like it is catching.**

---

## 6. Checklist — "I just authored a faction religion"

1. **Every defName came out of the palette.**
   `grep -n '<defName>' /mnt/d/Luke/dev/Rimworld/design/Jawa/worldbuilding/data/ideology_palette.md`
   — or search it for the name. Never write one from memory.
2. **Dump is fresh.** Line 1 of any run prints the capture stamp; compare against
   today and against `ModsConfig.xml`'s mtime. Stale dump ⇒ stale verdict.
3. **Run the spec form** (design intent, precepts included):
   `python3 src/RimMandrake/Utils/validate_ideoligion.py --md <spec.md> --only '<name>'`
   Fix every 🔴. Read every `meme/requireOne` ⚠️ and decide, per group, whether
   you are content to let the generator choose.
4. **Run the XML form** (what will ship):
   `python3 src/RimMandrake/Utils/validate_ideoligion.py --xml <FactionDefs.xml>`
   Expect `route/precepts-unauthorable` to be absent (XML carries no precepts) and
   `deity/*` to reflect your `<deityPresets>` count. On an `allowedMemes` faction
   expect ℹ️ `structure/generated` and a candidate count on `meme/impact` — both
   normal (§2). Every 🔴 is real; there is no longer a category to ignore.
5. **Eyeball the `MayRequire` attributes.** The script will not.
   `grep -n 'li>' <FactionDefs.xml>` — every modded defName needs
   `MayRequire="<packageId>"`, and `def/needs-mayrequire` printed the exact string.
6. **Name-blind test.** If the run's final section lists your religion in a pair
   ≥ 34 % shared, one of the two is decoration. Fix it before spending a load.
7. **Deploy.** Writing the file is not deploying it —
   `skills/rimworld-deploy/SKILL.md`. The game reads
   `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>`.
8. **Load, then grep the log** for the eleven strings in §4b before touching the
   UI. Cheap, and it rules out the loud failures.
9. 🔴 **The one thing only a game load settles — open the Ideoligions tab, click
   "Show all ideoligions", find the faction, and read its memes back.** If they
   are not exactly your `forcedMemes`, the religion in the document does not
   exist, whatever the offline gate and the log said.

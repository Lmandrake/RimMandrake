# Art resolution root cause — diagnosis (2026-10-04)

Owner: *"Please find the source of this regular 'sheet failed to find the art' problem."*

## 1. Resolver inventory

Every tool below answers "what art / canon belongs to this subject?" **independently**, with its own key and
its own reading of "no match". None of them calls another; there is no shared resolver.

| # | resolver (file:line) | subject in | joins on | on no match |
|---|---|---|---|---|
| R1 | `art_sheet.build_row` §2 (`art_sheet.py:~150`) | a texPath `res` | artpipe variant `res` == texPath (**bound**, only via `collected.jsonl`) **OR** the texPath's *folder name* (`res.split("/")[-2]`) word-matched inside the job id (**alias**) | column absent; alias columns labelled "joined by creature name only" |
| R2 | `art_sheet.build_row` §1 live (`:~125`) | texPath | every mod shipping that texPath; winner by index in the **live** `ModsConfig.xml` | a mod not in the active list gets index -1 and is labelled **"shipped, shadowed"** even when it is the only shipper |
| R3 | `art_sheet.name_render_cols` (`:625`) | defName/port/label words ≥4 chars + census `artpipe_state_jobs` | word-bounded substring of the artpipe **job id** | nothing shown |
| R4 | `art_sheet.canon_entry` (`:75`) | names | `canon_references/<dir>` **exact** dirname after stripping `RSW_/RUT_/RM_/AA_` | `{}` → sheet prints "No canon-library entry" |
| R5 | `biome_census` canon (`biome_census.py:517`) | row defNames + donors + label | `INDEX.md` defName column (exact defName), then R4 | `canon.entry = None` → sheet tier "no canon-library entry" |
| R6 | `biome_census` art (`:657`) | row defNames | `scan_def_slots` texPath of the def (body role) → R1/R2; if the def has **no texPath of ours**, a stem regex over ledger texPaths (`joined_by: "name"`) | `has_art: False` → **NO ART** in census.md (renders found only by R3 are not counted) |
| R7 | `biome_census.artpipe_jobs` (`:412`) → `artpipe_state.py find --names-only` | stem only (no label, no defName variants) | substring of `done/`, `pending/`, `_artsrc/` entry **names**, then word-boundary post-filter | empty list |
| R8 | `artpipe_state.py find` (`artpipe_state.py:73`) | free terms | substring of file **names**, and without `--names-only` substring of **job JSON content** (prompt text) | "0 hit(s)" — a content hit on a prompt that *mentions* the term (Thunderbeast → `crags_ulkhorr`) is printed as a hit |
| R9 | art ledger `backfill.step_artpipe` (`backfill.py:220`) | every `_artsrc/<job>/` | `collected.jsonl` `job_id → dest` (gives the variant a `res`) | variant stored with **`res = None`** — unbound forever; only R1-alias/R3 can ever surface it again |
| R10 | `artledger.install*` (`artledger.py:441`) | dest texPath | texPath (durable) | n/a — the *one* durable binding, but only since 2026-10-03 |
| R11 | `artpipe/make_verdict_sheet.creature_of` | registry `target` | job-id stem with `_rN` stripped | warning, row skipped |
| R12 | `artreg.derive_target` / `registry.jsonl` | job id | `<asset_key>/<facing>` reconstructed from the job id | — (the asset key is a job-family name, never a defName) |
| R13 | `canon_census.py`, `check_pseudo_sw_name.py`, `droid_canon_fill.py` | slug | canon dirname | own buckets |
| R14 | `design/Jawa/worldbuilding/review/round2/decisions_propagated.json` | creature name | owner decisions keyed by the review's own row names | n/a (historic, not consulted by R1-R7) |

**What the artpipe job record actually carries** (`done/<job>.json`): `id`, `prompt`, `facing(s)`, `reference`,
`rimflow_item_id`, `style_notes`, optional `install_to` (new). It does **not** carry a target defName or texPath
unless `install_to` was set. So the subject of a render is recoverable only from (a) `install_to`/`collected.jsonl`,
(b) its job-id naming convention, or (c) its prompt prose.

## 2. Traced examples

### 2a. RSW_WraidAlpha on the Long Shade sheet (`Transient/biome_ffar/shots/desert_top.png`)

The screenshot reads as "column A is a different creature". Traced, **column A is the right creature and column B
is the ungrounded one** — and the sheet hid the evidence that would have shown it.

1. **Same texPath, legitimately.** `RSW_Wraid` and `RSW_WraidAlpha` both draw `swanimals/Wraid/Wraid`
   (census `subjects: [RSW_Wraid, RSW_WraidAlpha]`). Column A is
   `src/RimStarWars/SWBestiary/Textures/swanimals/Wraid/Wraid_{south,east,north}.png`, ported 2026-09-18
   (`MLIE_FAUNA_ABSORPTION_1` Pass 24). Compared side by side with
   `design/RimStarWars/canon_references/wraid/wookieepedia_canon_1.webp`, it **is** a wraid: canon says
   *"pinkish-red in color … very powerful front legs … two small back legs"*, and the "bat/crab" shape is two
   huge forelegs seen from the front. It is the stylised donor sprite, not a different animal.
2. **Column B is a text-only render joined by name.** `render desert_swaca_wraid` (job
   `done/desert_swaca_wraid_east.json`, 2026-09-20, `DESERT_FAMILY_PORT_EXECUTION_1`) has `reference: None`, no
   `derive_from`, and a prompt that says only *"large reptilian creatures found on many desert planets"*. The image
   model drew a generic monitor lizard. It reaches this row through **R1-alias**: the texPath folder word `Wraid`
   appears in the job id. Nothing binds it to `swanimals/Wraid/Wraid` (`collected.jsonl` has no entry), so it is
   labelled "joined by creature name only".
3. **The canon panel said "No canon-library entry"** (false absence, R5→R4). `INDEX.md` lists only `RSW_Wraid` for
   `wraid/`, and `canon_entry("RSW_WraidAlpha")` tries the dirnames `rsw_wraidalpha` / `wraidalpha`, which do not exist.
   The wraid reference images, which would have shown at a glance that A matches canon, were never put beside the row.
   (Also a lesson: `infrastructure/state/lessons/20261004T222829Z-BENCH-art-sheet-canon-lookup-was-exact.md`.)
4. **"shipped, shadowed — SWBestiary" is a false label** (R2). Nothing shadows it, because no other mod ships that
   texPath. The census and the sheet were built while the live `ModsConfig.xml` held a **9-mod test list**
   (`inputs.load_order: "ModsConfig.xml 9 active, modified 2026-10-04 10:55"`). SWBestiary was not in it, so it
   got load index -1. With no winner, `build_row` labels every shipper "shadowed".

So the creature in A is the right one. The owner was looking at a correct sprite with no canon images beside it,
a false "shadowed" tag on it, and a wrong render beside it presented as an equal alternative.

### 2b. Blue Desert "NO ART" (lesson `20261004T220615Z-BENCH-biome-census-py-marks-row-no.md`)

`biome_census` decides `has_art` from **R6 only**, which is the def's own texPath and its ledger versions. A row
whose def points at a vanilla or donor texture, or whose renders were never collected to a texPath, has
`n_versions == 0`. The census still records the renders it found by name in `artpipe_state_jobs` (R7), but it
**does not count them** toward `has_art`. The sheet's R3 does count them. So the census and the sheet disagree
about the same row, and census.md prints the worse answer. Examples: `RM_Dorrak` → `bluedesert_dorrak`,
`RM_Krissek` → `bluedesert_krissek`, `RM_Vekkit` → `bluedesert_vekkit`, `AA_Thunderbeast` →
`bluedesert_AA_Thunderbeast_v1`.

### 2c. Giant leaf / fire lavender / heatsink fungus (2026-09-20)

The art was finished and sitting under `_artsrc/`, but none of it was bound to a def, so finding it needed a
name search. Before 2026-10-03 no job could carry `install_to`, and the 28 `collected.jsonl` records are all from
2026-10-03 or later. That leaves every earlier render (2,860 dirs) findable only by guessing its job-id spelling.

### 2d. `artpipe_state.py find Thunderbeast` → `crags_ulkhorr`

R8 without `--names-only` substring-matches the **prompt text** inside every job JSON. A prompt that *mentions* a
thunderbeast (as a comparison or a predator) is printed as a hit for that subject. The hit is labelled
"(content)", but its count goes into the same total as name hits.

## 3. Measured scale

Instrument: `python3 src/RimMandrake/Utils/art/resolution_audit.py` (read-only; committed with this doc). Input:
`Transient/biome_ffar/census.json` generated 2026-10-04T15:23 at `eeff5234d`, which has **34 Baroque biomes and
946 rows** (34, not 28: the compose set now includes the `RM_SeabedFloor_*` defs). The artpipe state dir holds
2,860 render dirs in 1,812 families and 3,289 done job records.
**Sanity probe** (the run refuses if any of these reads zero): 20 `bluedesert_*` render families ·
`desert_swaca_wraid` present · canon dir `wraid` present · 4 `anooba` name-join families · 946 rows.

### Binding coverage: the base rate behind everything else

| | count |
|---|---|
| done job records | 3,289 |
| … carrying `install_to` (target texPath) | **0** |
| … carrying `reference` or `derive_from` (grounded on an image) | 514 (16%) |
| … carrying `rimflow_item_id` | 3,289 (it names *why* the job ran, never *which def*) |
| `collected.jsonl` bindings (job → texPath) | **28**, all from 2026-10-03, none for a biome creature |
| render columns on the 946 census rows that are **bound** to the row's texPath | **0** |
| render columns that are **name-joined** | **5,619**, on 257 rows |

Every render a review sheet has shown for a biome creature was put there by a name guess.

### Class A — false absence

| id | what | rows |
|---|---|---|
| A1 | canon entry exists but the row says "no canon-library entry" | **8 rows** where a variant word hides it: `RSW_WraidAlpha`→wraid, `RSW_Plant_Chakroot_Wild` ×2→chak_root, `RSW_Plant_HubbaGourd_Wild`→hubba_gourd, `RSW_OpeeSeaKillerJuv`→opeeseakiller, `RSW_YobshrimpJuv`→yobshrimp, `RSW_FaaJuv`→faascalefish, `RSW_MeeJuv`→meescalefish. (4 more only share a texture with a canon creature; see B3.) |
| A2 | census says **NO ART** | 157 rows |
| A2a | … while the census's own `artpipe_state_jobs` lists renders for the row (it contradicts itself) | **73** |
| A2b | … where the sheet's name join finds renders (census false absence; the sheet shows them) | **58** |
| A2c | … where only a looser token search finds anything | 31, almost all noise (`grass`→`RM_Lashgrass`, `giant`→`RM_GiantSkull`). That is what name matching looks like once it gets loose enough to find more. |
| A2d | … with a texPath that resolves to vanilla/donor art the ledger never ingested | 66. The game draws a picture, but the row says NO ART. "No art *of ours*" is printed as "no art". |

### Class B — wrong or ungrounded art

| id | what | count |
|---|---|---|
| **B0** | **texPath-folder alias collision `Plant`.** `build_row` takes `res.split("/")[-2]` as the creature word. For every flora texPath `Things/Plant/<Name>` that word is **`Plant`**, which word-matches every job id containing `_plant_`. | **106 rows** (104 plants) each show the **same 49 unrelated plant renders** (`chill_plant_eldspar`, `desertportb_plant_bloddle`, …). That is **5,194 of the 5,619** name-joined columns (92%). Confirmed in the shipped sheets: `chill_plant_eldspar` appears 14× in `Transient/biome_ffar/deep_desert_sheet_2026-10-04.html`. |
| B1 | render column joined by name only (any cause) | 5,619 columns on 257 rows; 0 bound |
| B2 | one render family offered as art for >1 species | 140 families. 49 are B0; 80 are benign same-creature forms (`…catch`, `…Juv`, `…Colony`); **11 are prefix collisions**: `fuzz`→`RM_Fuzzrunner`+`RM_Fuzzviper`, `vurra`→`RM_Vurrak`, `wick`→`RM_Wickwood`, `thrummel`→`…Broodmother`/`…Warden`, `excretor`↔`desertportb_feralnerf`, `scrapnestbird`↔`whisperbird`. `biome_census.artpipe_jobs` accepts `(^|_)term` with **no right boundary**. |
| B3 | a texPath drawn by defs of *different* species, so each row shows the other's art | 134 rows / 138 texPaths, including stand-ins drawn with a canon creature's texture (`RM_Vellak` and `RM_BloodyMess` → jerba's, `RSW_VentStalker` → kinrath's, `RSW_ScrapNestBird` → whisperbird's) |
| B4 | "shipped, shadowed" on a mod that is simply absent from the live load order | 793 columns on 607 rows (the census ran against a 9-mod test `ModsConfig.xml`) |
| B5 | canon row showing a render that was generated with **no reference image** (text-only prompt, like 2a's lizard) | 68 rows, 259 columns |
| B6 | texPath attached to a donor-only row by a stem regex over ledger paths | 20 rows |

Full per-row detail: re-run with `--json <file>`.

## 4. Root causes (plain words)

1. **A render never records what it is a picture of.** An artpipe job carries a prompt and a reason
   (`rimflow_item_id`), but no target defName and no target texPath (`install_to` exists since 2026-10-03 and 0 of
   3,289 jobs use it). Everything downstream therefore has to *guess* the subject from the job id's spelling. That is
   the only reason "joined by creature name only" exists, and it is why 0 of 5,619 biome render columns are bound.
2. **Every tool guesses differently, and none shares the guess.** There are thirteen resolvers (§1) with thirteen
   keys: the texPath folder word, the stem with a prefix-only regex, defName words of 4+ chars, file-name substrings,
   prompt substrings, and exact canon dirnames. The census and the sheet resolve the same row two ways and disagree
   (A2a/A2b). A fix to one, such as today's canon-lookup patch, leaves the others wrong.
3. **The guesses have no confidence level, and "not found" is printed as "does not exist".** The sheet says
   "No canon-library entry" and the census says "NO ART" when the true statement is "my one key matched nothing".
   Bound, name-matched and nothing are not separated in what the owner sees: a name-joined lizard sits as an
   equal column beside the shipped sprite, and an empty lookup reads as a verdict.
4. **Two specific key bugs make the guessing far worse than it has to be:** the texPath *folder* used as the
   creature word (`Things/Plant/X` → `Plant`, B0, 92% of all wrong columns), and the right-unbounded job regex in
   `biome_census.artpipe_jobs` (B2 prefix collisions).
5. **Runtime labels are measured against whatever `ModsConfig.xml` happens to be live**, a test list as often
   as not, without saying so on the row (B4).
6. **Renders are generated without the canon images** (only 16% of jobs carry a reference), so the
   wrong-looking art in 2a was made wrong at generation time. The resolver only presented it.

## 5. Proposed fix

### 5.1 One resolver: `src/RimMandrake/Utils/art/subject.py`

One module, and every sheet, census and tool calls it: `art_sheet`, `biome_census`, `artpipe_state find`,
`make_verdict_sheet`, and the canon tools. It has two entry points:

```
resolve_art(subject) -> [Hit{sha|job, res, kind, confidence, evidence}] + Searched{keys, sources, counts}
resolve_canon(subject) -> Hit{entry, confidence, evidence} | None + Searched{...}
```

`subject` is a **defName** (the identity). The module derives the rest itself: `race` for a PawnKindDef, body-role
texPaths from `scan_def_slots`, the stem, variant-stripped bases (`Alpha|Juv|Juvenile|Wild|…`), donors/ports from
the census pairing, and texPath-sharing twins.

**Confidence is one of three values, shown on every column and every canon panel:**

| level | meaning | source |
|---|---|---|
| `bound` | durable record ties this picture to this texPath or defName | ledger `install` event (texPath), `collected.jsonl`, job `target_def`/`install_to`, git history of the texPath, donor extract of the texPath; for canon, `INDEX.md` defName |
| `name-matched` | a spelling match only, with the exact key that matched | job-id **whole-token** match on stem/label (never the texPath folder word, never prefix-only), variant-stripped canon dirname, twin's canon entry |
| `none` | nothing found | — |

**`none` is never rendered as absence.** It renders as *"searched: ledger by texPath `X`, 1,812 render families by
tokens {wraid, wraidalpha}, canon dirs {wraidalpha, wraid}, INDEX defNames {RSW_WraidAlpha}. 0 hits."* The row
carries the `Searched` record so the claim can be audited. Name-matched columns sit in a folded "possibly this
creature" strip under the bound columns, never as equal alternatives, and a pick on one writes a binding (5.3).
Every run includes a sanity probe, as `resolution_audit.py` does.

Runtime labels (R2) say which ModsConfig they were measured against. A mod absent from that list is labelled
"not in the measured load order (N active)", never "shadowed".

### 5.2 Bind at birth (stops the bleeding)

- `fill_queue.py` **requires** `target_def` (defName) on every creature/flora job, plus `install_to` when the texPath
  is known. It refuses a job without `target_def` unless `--no-subject "<why>"` is given (templates, glyphs).
- The job's `reference` defaults to the canon entry's images when `resolve_canon(target_def)` is `bound`. This
  fixes the generation side of 2a (B5).
- `backfill.step_artpipe` reads `target_def`/`install_to` into the variant, so the ledger knows the subject even
  before an install.

### 5.3 Backfill historic art (the 2,860 unbound renders)

Every step below is mechanical and writes a `binding` ledger event with its evidence and confidence:

1. **Byte/perceptual join**: a render whose sha, or dHash within NEAR, equals any git or live variant of a texPath
   is `bound` to that texPath. It was installed by hand, and the bytes prove it.
2. **Owner rulings**: a render the owner picked on any sheet (`*.decisions.json` via snapshot → sha) is `bound` to
   that sheet row's texPath.
3. **Job-family conventions** (`<biome>_<creature>`, `desertportb_`, `rot_`, `canon_…_v1`): token-match to
   exactly one census defName → `name-matched` with the token recorded. Two or more candidates → left unbound
   and listed, never guessed.
4. Whatever remains goes on one **binding review sheet** (render thumb, candidate defs, canon refs): the owner or an
   agent clicks the subject. Only an owner click or byte evidence gives `bound`.

### 5.4 Immediate one-line fixes, ahead of the module (for whoever owns `art_sheet.py`/`biome_census.py` now)

- `build_row`: derive the alias word from the **file stem** (`res.split("/")[-1]` minus tier prefix), never the folder.
  This removes B0, 5,194 wrong columns.
- `biome_census.artpipe_jobs`: drop the second, right-unbounded regex (B2).
- `biome_census` `has_art`: count R3 name-join hits as `name-matched` art, not NO ART (A2a/A2b).
- `canon_entry`: try the variant-stripped stem, then the texPath-sharing twin's entry (A1).

### 5.5 Estimate

| piece | size |
|---|---|
| 5.4 one-liners | ~1 h including a census + sheet re-run |
| `subject.py` + confidence/`Searched` rendering + port of `art_sheet`, `biome_census`, `artpipe_state find` | ~1 day (Opus design, Sonnet port), with a selftest that pins the 2a/2b/B0 cases |
| 5.2 bind-at-birth (`fill_queue` required field, canon reference default, backfill read) | ~half a day |
| 5.3 backfill steps 1–3 | ~half a day of script plus one ledger write. Expect steps 1–2 to bind a minority and step 3 most of the convention-named families. Step 4's sheet size is UNMEASURED until 1–3 run. |
| retire R7/R11/R12 name logic onto `subject.py`; `resolution_audit.py` becomes the regression check | ~2 h |

Total: about 2.5–3 working days. The 5.4 fixes alone remove ~92% of the wrong columns and the 58 census false
NO-ARTs today.

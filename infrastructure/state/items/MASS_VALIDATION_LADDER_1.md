# MASS_VALIDATION_LADDER_1 — batched validation ladder (L0–L4)

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-09-02. Owner's
filing (verbatim, 2026-09-02): *"I like your plan except for the human
reviewer. Please take me out of that loop so you can validate your own art
presence, etc. You don't need me to find magenta squares, don't use humans
where a screenshot will do. Anytime you can review something, just go ahead
and do so. Reserve human testing where it absolutely must be used, likely
things like gameplay, fun, overall thematic coherence, user interface
questions."*

## spec

Full ladder design: `infrastructure/VALIDATION_LADDER.md` (owner-ruled,
2026-09-01) — L0 offline / L1 resolved-live (minimal-list restart + `jawa/get_defs` +
manifest diff) / L2 behavior gauntlet (batched quicktest, art proven by
machine) / L3 Fable evaluation (art/style/thematic judgment, bridge in
Fable's own hands) / L4 human (gameplay/fun/thematic coherence/UI only).
This item builds the machinery; the ladder DOC states the design and is not
duplicated here.

## verify

Per `VALIDATION_LADDER.md`'s own `## Criteria (for MASS_VALIDATION_LADDER_1)`:
- A batch of builds validates through L2 in one bridge sitting, zero restarts.
- `jawa/get_defs` reads nested fields (stages etc.) after its upgrade.
- One manifest format, one runner; no bespoke V&V scripts per item.
- ~~One measured `hot_reload_defs` trial on the full list, owner-blessed.~~
  ⛔ **VOID — it ran 2026-09-03 and the capability was RETIRED on its result.**
- First review environment staged and reviewed by the owner.

## criteria

Same five bullets as `## verify` above — this item is done when all five are
true, not before.

## 2026-09-02 (FOUNDRY) — offline half built; everything bridge/owner-gated still open

Built while a sibling fork held the bridge for unrelated work — this pass
never touched the bridge, never restarted, never deployed the companion DLL.

**"One manifest format, one runner" — DONE, offline-proven:**
- `src/RimMandrake/Utils/expectations_manifest.py` — the format. A manifest
  is one JSON file, `{"item": "...", "checks": [{"defType", "defName",
  "path", "expected"}, ...]}`. `path` is dotted-with-brackets
  (`stages[0].label`); a path with no `.`/`[` is a SCALAR check (works
  against the live `jawa/get_defs` TODAY, scalar-only), anything else is a
  DEEP check (needs the upgrade below — reads `SKIPPED-PENDING-UPGRADE`
  until it's live, never silently attempted against data that can't serve
  it). No manifest exists yet from any prior build item this session — this
  is the format going forward, not a retrofit of already-closed items.
- `src/RimMandrake/Utils/run_expectations.py` — the one runner. `--fixture
  <json>` mode is fully offline (a hand-authored `{"DefType::defName": {...
  fields...}}` stand-in for a live deep-serialized read) — this is how a
  manifest gets iterated on and CI-checked before any game is involved.
  `--live` mode calls the real bridge (`RimBridge` from
  `rimbridge_client.py`, one `jawa/get_defs` batch call per defType, scalar
  checks only until the upgrade lands). Exit 0 = all PASS/SKIPPED-PENDING-
  UPGRADE, exit 1 = any FAIL/MISSING-DEF/PATH-ERROR/unparsable manifest.
- `src/RimMandrake/Utils/selftest_expectations_manifest.py` — 20 synthetic
  assertions (path-walking, malformed-manifest rejection, PASS/FAIL/
  MISSING-DEF/PATH-ERROR/SKIPPED-PENDING-UPGRADE all exercised against real
  fixture files, not mocked internals). `python3
  src/RimMandrake/Utils/selftest_expectations_manifest.py` — 20/20 pass.
  Fixtures: `testdata/expectations_selftest_{manifest,fixture}.json`.
  Manifests for real build items belong at
  `infrastructure/state/expectations/<ITEM_ID>.expectations.json` (new
  directory, created this pass, currently empty — no existing build item
  has been retrofitted with one yet; that's follow-on work, not required to
  close this item, which is about the MACHINERY existing).

**"`jawa/get_defs` reads nested fields" — C# WRITTEN, COMPILED, NOT DEPLOYED:**
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`
— added a `deep` parameter (default `false`, byte-identical old behaviour)
to the `jawa/get_defs` tool, and a new `DeepSerializeValue(object, int
depth)` helper. `deep=true`: a list item that is a plain object (e.g.
`ThoughtStage`) recurses into its own public fields instead of collapsing
to its bare type name; a `Def` reference still collapses to `defName`
(never expands — keeps the payload finite); depth capped at 3 to bound a
pathological object graph; a non-enumerable complex field (previously
silently DROPPED with no placeholder at all — a real, separate small bug
found while reading the old code, now also fixed under `deep=true`) is
serialized too. `deep=false` remains the exact old behaviour for every
existing caller.

Compiled: `python.exe "D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py" --gm`
(plan-only, no `--apply`) — **Build succeeded, 0 Warning(s), 0 Error(s)**,
bundle-contents check clean (ships only the one DLL). **NOT deployed** — the
game is up and a sibling fork holds the bridge; deploying needs a game-DOWN
window per `rimbridge-companion` skill (`taskkill` first, DLL is memory-
mapped while RimWorld runs). Left for whoever next has a game-down window:

```
taskkill.exe /F /IM RimWorldWin64.exe
python.exe "D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py" --gm --apply
<relaunch, then prove: call jawa/get_defs on a known ThoughtDef with
 fields=stages, deep=true, and read back stages[0].label for real>
```

**Still fully open, all bridge-gated and/or owner-gated — none attempted
this pass:**
- L2 batch-validate-in-one-sitting trial.
- The `hot_reload_defs` full-list measured trial (owner-blessed timing).
- The first staged review environment (L4, needs the owner's own eyes per
  his ruling above).
- Retrofitting any real build item (e.g. `FORSAKEN_CRAGS_PREDATORS_BUILD_1`)
  with an actual `.expectations.json` manifest — the format/runner exist,
  nothing has used them for real content yet.

Left `doing`.
# Hot-reload full-list trial: blessed in principle (owner card, 2026-09-02)

"Foundry currently has the bridge. Sorry. Need to do this later." ⇒ the trial
is authorized; run it at the next window the bridge is free — take it via
rimflow, time one hot_reload_defs on the full list, prove a def read
before/after, release. Do not re-ask; the blessing stands.

# 🔴 Hot-reload trial RESULT — full list HANGS (BENCH, 2026-09-02)

Ran the blessed trial on the full ~592-mod list. `jawa/hot_reload_defs`
returned success:true in 0.1s, then the game went UNRESPONSIVE re-loading all
defs + rebuilding render meshes; the play UI was lost (owner: "I see no
buttons"). Unrecoverable live hang, restart required. Disk unharmed (trial
marker reverted before the hang; 0 markers left). ⇒ hot-reload is a
MINIMAL-LIST tool only; the zero-restart L1 cycle in VALIDATION_LADDER.md
applies to minimal-list tool work, NOT the owner's play stack. Doctrine
corrected in rimworld-modding §2 and rimworld-load-round §0.

# ✅ Hot-reload PROVEN on minimal (BENCH, 2026-09-02)
Core Campfire description edited on disk → jawa/hot_reload_defs 0.04s →
change read back LIVE via get_defs → revert reload 0.06s clean. Zero-restart
L1 cycle confirmed for minimal-list tool work. Full-list scales to minutes
(same op); earlier "unrecoverable" claim retracted — killed too early to know.


# ⛔ HOT RELOAD RETIRED — owner's ruling, 2026-09-03

*"I recommend we give up on hot reload xml capability as unstable. … let's retire
that capability as desirable for now and possibly forever."*

The second full-list trial COMPLETED where the 2026-09-02 one was killed: ~5 minutes
of hung bridge, then a game that answered every read correctly and could not generate
a single pawn — `jawa/spawn_pawn` NRE'd on Muffalo, Hare, Colonist, Tribesperson and
Villager alike, and vanilla's own debug spawn named the cause:
`The given key 'RimWorld.HairDef' was not present in the dictionary`. The defs
themselves all still resolved, so a Type-keyed index is what the reload broke.
Evidence: `infrastructure/state/items/closed/HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1.md`.

⇒ **L1 is now: deploy → minimal-list restart (22 s) → `jawa/get_defs` → offline diff
against the expectations manifest.** The ladder loses nothing; a 22-second restart was
always most of what hot-reload was saving. `expectations_manifest.py` and its runner
are unaffected — only the step that produced the live state changed.

## 2026-09-18 (FOUNDRY, belt mode, subagent) — tally against all 5 criteria

MODE=afk this session; did not touch the owner-gated criterion. Bridge was FREE
and the game answering (`rimflow bridge who`/`rimflow game` checked first); took
it once for a short, read-only proof, released immediately after.

**1. "A batch of builds validates through L2 in one bridge sitting, zero
restarts." — STILL OPEN.** Did not attempt the L2 behavior gauntlet (spawn
everything new, step ticks, screenshot) — out of caution given the fragile
shared session (active water-terrain regression investigation, heavy
concurrent activity) and because the more urgent gap turned out to be one tier
down (see below). Did land a real **L1** batch proof: 13 checks across 4
defTypes (`ThingDef`/`PawnKindDef`/`HediffDef`), 3 bridge calls, one sitting,
zero restarts — `python.exe src/RimMandrake/Utils/run_expectations.py
--manifest infrastructure/state/expectations/FORSAKEN_CRAGS_PREDATORS_BUILD_1.expectations.json --live`.
L2 itself remains unattempted; a future session should judge session
fragility fresh before trying it.

**2. "`jawa/get_defs` reads nested fields after its upgrade." — DONE, and
exercised for real for the first time.** The upgrade has been deployed since
2026-09-04 and ad-hoc live-proved 2026-09-13, but **`run_expectations.py`'s
own `_live_defs` had never actually been run against the real bridge before
today** — only against `--fixture` stand-ins. Running it live for the first
time immediately found a real bug: `_live_defs` read `resp["rows"]`, but the
live `jawa/get_defs` response key is `"defs"` — every prior scalar-only
`--live` run had therefore silently returned zero rows (all MISSING-DEF)
instead of failing loud. Fixed (`run_expectations.py`), confirmed live.
Also wired `--live` mode to actually pass `deep=True` and a real `fields=`
list to the bridge (it previously hardcoded `allow_deep=False` and never
asked for deep fields at all, even though the C# upgrade has been live for
two weeks) — this is now the runner's only mode; there is no more
SKIPPED-PENDING-UPGRADE path.
Separately found, **fixed offline, built clean (0 warnings/errors), NOT
deployed**: `DeepSerializeValue` in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`
had no case for `System.Type` fields — every `hediffClass`/`compClass` (a
`Type`, not a `Def`) deep-serialized to an empty `{}` instead of an honest
value or an honest failure, because `Type`/`RuntimeType` expose `Name`/
`FullName` as properties, not public instance fields, so the generic
reflect-its-own-fields fallback found nothing. Confirmed live against the
running game before the fix (`HediffDef::RSW_ColdDrain#hediffClass` read back
`{}`), fixed to return the bare `Type.Name` (matching how XML/manifests
already write class names unqualified), rebuilt clean via `build.py --gm`
(plan-only — game is up, DLL is memory-mapped, did not force a deploy).
**Deploy owed at the next game-down window** (`build.py --gm --apply`); the
live manifest run after this fix will need a restart to actually prove
`hediffClass`/`compClass` come back correct — currently the one remaining
live FAIL (12/13 PASS, 1 FAIL, confirmed this session; the FAIL is exactly
this known, already-fixed-but-undeployed defect, not a mystery).

**3. "One manifest format, one runner; no bespoke V&V scripts per item." —
DONE, and the machinery got materially more correct.** Live-proving criterion
2 above surfaced that `FORSAKEN_CRAGS_PREDATORS_BUILD_1`'s own manifest — the
one existing retrofit, closed as done 2026-09-13 — was **itself wrong against
real live shape in 3 of its 13 checks**, all authored against a hand-built
fixture that never matched what `deep=true` actually returns:
- `statBases.Wildness` assumed `statBases` is a dict keyed by stat name; live
  `deep=true` returns it as an ordered `List<StatModifier>`
  (`[{"stat":"Wildness","value":1.0}, ...]`), same shape vanilla always used.
- `tools[2].extraMeleeDamages[...]` assumed index 2 was the cold-drain-grip
  tool (true of the ThingDef's OWN 3-item XML block) — the POST-INHERITANCE
  resolved list actually has 7 entries (a parent race def's claw/teeth/head
  tools come first), so the real cold-drain-grip tool is index 6, not 2.
- `comps[1].fleeSearchRadius` had the same inherited-list-position problem;
  the real `CompProperties_LightAversion` entry is index 17 of 19.

Rather than hardcode new (equally fragile) positions, extended the path DSL:
`expectations_manifest.py` now supports `[key=value]` bracket lookups
alongside bare `[N]` indices — `statBases[stat=Wildness].value`,
`tools[label=cold-drain grip].extraMeleeDamages[0].def`,
`comps[fleeExpiryTicks=600].fleeSearchRadius` — which find a list item by a
field's value instead of a position, so a future inherited-list reorder
cannot silently break the check again. `_walk_segment`/`_PATH_TOKEN`/
`_INDEX` updated; `_coerce_bracket_value` added (int/float/bool/string).
Manifest and its offline fixture both corrected to the new paths. Runner
(`_top_field`) updated to derive the right `fields=` name for a keyed path
too. `selftest_expectations_manifest.py` grew from 20 to **27/27** (7 new
cases: keyed match, keyed no-match raises, keyed-against-non-list raises,
`_top_field` for all 4 path shapes). `--fixture` run: **13/13 PASS**. `--live`
run against the real game: **12/13 PASS**, the 1 FAIL being the
already-diagnosed-and-fixed-offline `hediffClass` Type-serialize bug from
criterion 2, not a new mystery.

**4. `hot_reload_defs` full-list trial — VOID, untouched, not resurrected**
(per its own retraction above and the owner's 2026-09-03 ruling).

**5. First review environment staged and reviewed by the owner — NOT
attempted, correctly out of scope this session.** MODE=afk; this is
explicitly his own eyes per the ladder doc's L4 definition, not FOUNDRY's to
stage-and-self-grade. Genuinely still open.

**Net**: criteria 2 and 3 are DONE and now stand on a real live proof instead
of an assumed-good retrofit; criterion 1 has a real L1 (not L2) batch proof
and remains open at the L2 tier; criterion 4 stays VOID; criterion 5 remains
open, owner-gated. Left `doing` — not all 5 are satisfied, `rimflow close` not
called.

Files touched: `src/RimMandrake/Utils/run_expectations.py`,
`src/RimMandrake/Utils/expectations_manifest.py`,
`src/RimMandrake/Utils/selftest_expectations_manifest.py`,
`src/RimMandrake/Utils/testdata/FORSAKEN_CRAGS_PREDATORS_BUILD_1_fixture.json`,
`infrastructure/state/expectations/FORSAKEN_CRAGS_PREDATORS_BUILD_1.expectations.json`,
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`
(compiled clean, deploy owed at next game-down window).

# DROIDWORKS_FAMILY_LAYER_1 — chassis-family abstract layer

Filed with only a title, no body ("Rework generator output: 7 chassis-family
abstract bases between DW_Race_Base and the 57 models"). The full spec turned
out to live in the ledger event itself (`infrastructure/state/ledger/events.jsonl`,
`file` event for this ID) — OWNER RULING 2026-08-29, quoted here because the
item's own `.md` had none:

> consolidate races to chassis families. The 1:1 output (ee9c095b) stays as
> the model layer; INSERT abstract family bases: DW_Race_Base ->
> DW_Family_{Labour,Protocol,Astromech,Battle,Heavy,Probe,Power} (Name=
> abstracts, Abstract=True) -> thin concrete per-model races (defName +
> graphics + label ONLY). Move per-family shared config (DroidworksExtension
> chassisClass/powerFallPerDay/energyDensity, statBases, size norms) DOWN to
> family bases; models override only where the source race genuinely
> differed... Update gen_droidworks_defs.py to emit this shape and re-run.

## The 7-vs-6 count — resolved, not guessed

The generator's original 6 chassis buckets (`DROIDWORKS_DEF_GENERATOR_1`)
already carried an internal 7th split, just not surfaced as a bucket: within
"astromech-labour" (15 races), `ASTROMECH_SHAPED` (a hard-coded set of 5
dome/utility-cart-shaped races) already got `chassisClass=2` while the other
10 got `chassisClass=0` — both documented in `DroidworksModExtension.cs`'s
own comment: `0 labour 1 protocol 2 astromech 3 battle 4 heavy 5 probe 6
power`. The owner ruling's family list, in order — Labour, Protocol,
Astromech, Battle, Heavy, Probe, Power — matches that int-code order (0..6)
exactly. So the 7th family is **not a guess**: it's the astromech-labour
split the code already computed, finally given its own name. No new
classification judgment call was needed for any of the 57 races.

## Family defNames and tuning

`Defs/Races_Families.xml` (new, generated), each `Name="DW_Family_<X>"
ParentName="DW_Race_Base" Abstract="True"`:

| family | races | powerFallPerDay | energyDensity | chassisClass |
|---|---|---|---|---|
| DW_Family_Labour | 10 | 0.33 | 0 | 0 |
| DW_Family_Protocol | 3 | 0.033 | 0 | 1 |
| DW_Family_Astromech | 5 | 0.33 | 0 | 2 |
| DW_Family_Battle | 18 | 1.0 | 0 | 3 |
| DW_Family_Heavy | 18 | 1.0 | 2 | 4 |
| DW_Family_Probe | 2 | 1.0 | 1 | 5 |
| DW_Family_Power | 1 | 0.33 | 3 | 6 |

10+3+5+18+18+2+1 = 57, matching the source. All 57 concrete races now
`ParentName="DW_Family_<X>"` instead of the flat `DW_Race_Base`.

## What moved onto the family abstracts, and what deliberately did not

**Moved, unconditionally**: `DroidworksExtension`
(powerFallPerDay/energyDensity/chassisClass) — every race in a family already
had byte-identical values for these three fields (the family split IS the
tuning boundary), so this is a pure dedup, zero risk, zero guessing. 57
per-race `<modExtensions>` blocks collapsed to 7.

**Moved, conditionally (data-driven, not averaged)**: `baseBodySize` and
`baseHealthScale`. For each family, computed the **mode** across its
members' resolved values; only set a family default when the mode has a
genuine plurality (≥2 races share it) — a family where every value is
distinct (or n=1, like Power) gets **no** family default, and every race
keeps its own explicit value exactly as before. Where a default was set,
races matching it omit the field (inherit); races that differ keep an
explicit override. Nothing was averaged away — the generator now prints
"per-race overrides kept" counts per family/field so every kept override is
auditable, not silent:

```
DW_Family_Astromech  bodySize default=0.65  healthScale default=1.5
DW_Family_Battle     bodySize default=0.7   healthScale default=1.0
DW_Family_Heavy      bodySize default=1     healthScale default=1.0
DW_Family_Labour     bodySize default=1     healthScale default=1.0
DW_Family_Power      bodySize default=None  healthScale default=None   (n=1, no plurality possible)
DW_Family_Probe      bodySize default=0.4   healthScale default=None   (healthScale: 0.6 vs 0.8, no plurality)
DW_Family_Protocol   bodySize default=1     healthScale default=None   (healthScale: 0.8/1/2, all distinct)
```

Override counts kept (value differs from family default, so still explicit
per-race): bodySize 10/battle, 11/heavy, 8/labour, 1/astromech, 1/power,
1/protocol; healthScale 13/battle, 10/heavy, 2/labour, 2/astromech, 1/power,
2/probe, 3/protocol. Full per-race list is in the regenerated XML itself
(every override is a literal `<baseBodySize>`/`<baseHealthScale>` line still
present on that race).

**Deliberately NOT moved: `MoveSpeed`.** Many races today carry no
`<statBases><MoveSpeed>` override at all — they fall through to
`DW_Race_Base` → `Human`'s own engine-default MoveSpeed. Setting a family
default for MoveSpeed would have silently changed the *effective* speed of
every race in that family that currently has no override — exactly the kind
of undetectable regression this project's own CLAUDE.md warns about
("verify what you displaced"). MoveSpeed stays 100% per-race, unchanged from
before this item. Confirmed no data loss: `MoveSpeed>` tag count and every
individual value are byte-identical before/after (diffed).

## CompDroidDetonation decision

**Out of scope, and said so explicitly** — this item is the structural
family-layer rework, not a balance rollout. Rolling `CompDroidDetonation`
out to the other Heavy/Power/Probe-family races (the ones with
`energyDensity > 0`) stays a follow-up, exactly as `DROIDWORKS_PILOT_GONK_1`
already flagged it.

What this item DID do: taught the generator to round-trip GNK's existing
hand-wired comp instead of leaving that a manual XML patch that a future
regenerate could silently drop again — the exact trap
`DROIDWORKS_PILOT_GONK_1`'s own commit (`4c0be10a`) hit and reverted from.
Added a small, explicit `COMPS_OVERRIDE` table in the generator (one entry:
`OuterRim_GNKDroid` → its `<li Class="Droidworks.CompProperties_DroidDetonation" />`,
with the same explanatory comment carried into the generated XML). This is a
named exception, not a guess and not a rollout.

## GNK's `baseHealthScale` — extraction.json now fixed too

Decision: yes, fixed. `extraction.json`'s `OuterRim_GNKDroid` record still
said `"baseHealthScale": "UNCERTAIN"` (only the XML had been hand-patched,
by `DROIDWORKS_PILOT_GONK_1`; the other 7 sibling races' extraction.json
entries were already fixed by a later commit, `4c0be10a`, same session).
Applied the identical, already-confirmed resolution: `AsimovAutomatonBase`
and its parent `AsimovNonEnergyAutomatonBase` (workshop `3096481956`,
`Race_Bases.xml`) declare no `baseHealthScale` at all, so the engine default
1.0 is the genuine value — not a new guess, the exact same read `4c0be10a`
already did for the other 7. `extraction.json` now agrees with the
hand-patched XML, so a regenerate no longer needs a special case to reach
1.0 for GNK.

## Regenerate safety (the trap this item's brief specifically warned about)

Regenerated to a scratch path first
(`/tmp/.../scratchpad/dw_gen_test/`), never in-place. Diffed scratch output
against the committed `Defs/Races_*.xml` before touching anything real:

- `PawnKinds_*.xml`: byte-identical (untouched by this item, as expected).
- `Races_*.xml`: diffs are exactly the intended reparenting (ParentName
  `DW_Race_Base` → `DW_Family_<X>`), the modExtensions collapse, and the
  bodySize/healthScale dedup described above — confirmed by comparing tag
  counts AND exact values (not just counts) before/after for `<path>`
  (graphics), `MoveSpeed>`, `RGBA(...)` (colors), and `<defName>DW_Race_`:
  **all identical, zero data loss.**
- GNK specifically: `baseHealthScale` = `1.0` (survived, now also matches
  extraction.json), `<comps><li Class="Droidworks.CompProperties_DroidDetonation" />`
  present (survived via the new `COMPS_OVERRIDE` table) — confirmed by
  reading the regenerated block directly, not assumed.
- HeadTypeDef counts unchanged (10 OuterRim + 8 KotOR + 0 JDS, both sides).
- defName-uniqueness across the whole `Defs/` tree: 174 distinct
  `<defName>` values (one collision found — `DW_DataSpike` appears twice, in
  `JobDefs_Droidworks.xml` and `ThingDefs/Items_Droidworks.xml` — both files
  belong to the concurrently-running `DROIDWORKS_WIPE_AND_SPIKE_1`, which
  closed and committed mid-session; **not touched by this item and not
  caused by it**, flagged here for whoever owns that mod's next pass). Plus
  8 `Name="DW_..."` abstracts (`DW_Race_Base` + 7 families), all unique, no
  overlap with the defName list.

Only once this diff was clean did the scratch output get copied over the
real files.

## Def count (owner's own VERIFY line)

`Name="DW_Race_Base"` (1) + `Name="DW_Family_*"` (7) + concrete
`<AlienRace.ThingDef_AlienRace>` with a `<defName>` (57: 19 OuterRim + 22
KotOR + 16 JDS) = **65**, matching "57 concrete + 7 abstract + 1 base"
exactly.

## HAR per-kind body art bonus question

Not investigated — the item marked this "BONUS if cheap" and the scope
above (generator rework, safety diff, extraction.json fix, validation) was
already the full budget for this pass. Flagging as unanswered rather than
guessing; a real answer needs reading HAR's `alienPartGenerator` /
`bodyAddons` handling for per-PawnKind graphic overrides, which is a
separate research task.

## Validation

`skills/rimworld-modding/scripts/validate_patch.py src/Jawa/Droidworks/Defs`
against `Mods`, `workshop/content/294100`, vanilla `Data` (needed for
`DW_Race_Base`'s `ParentName="Human"`, same as every prior item in this
chain), live capture `2026-08-30T01-41-15Z` (newest available):

**0 errors, 0 warnings across all 15 `Defs/` files** (whole directory,
including the concurrently-committed `DROIDWORKS_WIPE_AND_SPIKE_1` output —
not this item's job to fix, just confirmed it doesn't break the directory-
wide pass). The only "info" notices are the pre-existing, expected class-
not-found-in-scan pattern for every `Droidworks.*` class reference (the
validator can't see the compiled companion assembly) — now also printed
once per family abstract's `DroidworksExtension` reference and once for
GNK's `CompDroidDetonation`, same class of expected notice as every prior
item in this chain, not a new defect.

## Explicitly not done here

- No deploy, `ModsConfig.xml` untouched.
- `CompDroidDetonation` rollout to the other Heavy/Power/Probe races — out
  of scope, flagged as a follow-up (again).
- HAR per-kind body art investigation — not done, flagged above.
- Nothing under `Items_Droidworks.xml`, `RecipeDefs_Droidworks.xml`,
  `JobDefs_Droidworks.xml`, or any `.cs` file touched (those belonged to
  `DROIDWORKS_WIPE_AND_SPIKE_1`, which closed independently mid-session).

## criteria

- [x] Confirmed the item's spec via the ledger `file` event (its own `.md`
      had none) before writing any code.
- [x] 7-vs-6 count resolved from the code's own existing int-code order
      (`DroidworksModExtension.cs`), not guessed — astromech-labour splits
      exactly along the generator's own `ASTROMECH_SHAPED` set.
- [x] `Defs/Races_Families.xml` generated: 7 abstracts, `Name="DW_Family_<X>"
      ParentName="DW_Race_Base" Abstract="True"`, correct tuning per family.
- [x] All 57 concrete races reparented to their family abstract.
- [x] DroidworksExtension deduped onto family abstracts (zero risk, values
      were already identical within each family).
- [x] bodySize/healthScale deduped by measured per-family mode (≥2 plurality
      only), every kept override printed/counted, nothing averaged away.
- [x] MoveSpeed deliberately left per-race — moving it risked silently
      changing races that rely on engine-default fallthrough.
- [x] extraction.json's GNK `baseHealthScale` fixed to match the already-
      hand-patched XML and the 7 sibling fixes from `4c0be10a`.
- [x] Generator taught to round-trip GNK's `CompDroidDetonation` via an
      explicit, named `COMPS_OVERRIDE` table — general rollout left as a
      flagged follow-up, not silently done or silently lost.
- [x] Regenerated to a scratch path first, diffed against committed output
      (tag counts AND exact values) before overwriting anything real — GNK's
      two hand-fixes both confirmed to have survived.
- [x] `validate_patch.py` on the whole `Defs/` dir: 0 errors, 0 warnings.
- [x] defName-uniqueness pass across the whole dir: one pre-existing
      collision found, not caused by and not owned by this item, flagged.
- [x] Def count matches the owner's own VERIFY line: 57 + 7 + 1 = 65.

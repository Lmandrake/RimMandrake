# ASHKARR_PAINTER_NAMES_DIVERGED_1 — the painter's region names no longer match the planet

## what is wrong

MEASURED 2026-09-21 against the **live** canonical world (`jawa/world_features_get`, 71
features, canonical save loaded on the full 618-mod list) versus the region-name literals
in `src/RimMandrake/Utils/ashkarr_paint.py`:

**All 10 of the painter's range/basin region names carry a `"The "` prefix that the live
planet does not.**

| painter literal | live planet |
|---|---|
| `"The Fall Line"` | `Fall Line` |
| `"The Ashfall Range"` | `Ashfall Range` |
| `"The Dew Belt"` | `Dew Belt` |
| `"The Dew Horn"` | `Dew Horn` |
| `"The Gray Crags"` | `Gray Crags` |
| `"The Twilight Crags"` | `Twilight Crags` |
| `"The Salt"` | `Salt` |
| `"The South Crags"` | 🔴 **`Sootreach`** — renamed by the owner 2026-09-08 |
| `"The Ashteeth"` | ⚠️ **absent** under either form |
| `"The Ember Sink"` | ⚠️ **absent** under either form |

## why it matters — this is a generator, not a document

The name is consumed **verbatim** as the feature name (`ashkarr_paint.py:1080`,
`features.append({"id": i, "name": name, ...})`). Nothing strips the article. So
**re-running the painter would**:

1. **rename 7 live regions** by prefixing `The `,
2. 🔴 **resurrect `The South Crags` over `Sootreach`** — silently undoing a rename the
   owner ruled on 2026-09-08 (the V24 consolidation), and
3. create two regions (`The Ashteeth`, `The Ember Sink`) that exist on the planet under
   no name at all.

🔑 This is the **FlowWorks/`fluidcanals` shape**: a ruling that lives in the docs while the
generator still emits the old value. `STALE_V24_NAMES_IN_FROZEN_SHEETS_1` corrected the
five biome sheets; this is the half that can actually write to the planet.

⛔ **Do not run `ashkarr_paint.py` until this is settled.** Same caution for
`ashkarr_settle.py`, whose `BARREN_REGIONS` set (line 96) still names `"The Venom Wood"`
— overruled to `Fuelmere`, which IS live on the planet. A barren-region test that names a
region that no longer exists silently matches nothing, so it would place settlements in a
region the owner asked to keep empty.

## what is NOT established

⚠️ **Which side is right is not decided here, and it is the owner's call**, because region
names are his (`the_one_map.md`, and the worldmap-doc rule that a naming pass happens with
him, never solo).

Three readings, and this item does not choose between them:
- the planet was hand-corrected after the painter last ran, and the painter is simply stale;
- the article was deliberately dropped in a normalisation pass nobody propagated back;
- the painter was never the source of these names at all.

⛔ **No literal was changed.** A one-line "fix" that guesses wrong renames seven regions.

## spec

1. Ask him: do region names carry `The `? (Live says no; the painter says yes, for all 10.)
2. Whatever he says, make the painter and the planet agree, and fix `South Crags` →
   `Sootreach` and `The Venom Wood` → `Fuelmere` regardless — those two are already ruled.
3. Find out what `Ashteeth` and `Ember Sink` are on the planet today, if anything.
4. Sweep both scripts for any other region-name literal.

## verify

Every region-name literal in `ashkarr_paint.py` and `ashkarr_settle.py` appears in
`jawa/world_features_get`'s live name set, exactly.

## criteria

Re-running either script would not rename, resurrect or orphan a single region.

## 🔴 Owner ruling, 2026-09-21 (BENCH, question card)

**No leading "The ". The live planet is right; the painter is wrong.**

Strip the article from all 10 region literals in `ashkarr_paint.py` (and
`ashkarr_settle.py` if it carries them) so the scripts match the planet. ⛔ Do NOT rename
any live region — the planet is not edited by this ruling. The `Sootreach` ruling stands
and `The South Crags` must not be resurrected.

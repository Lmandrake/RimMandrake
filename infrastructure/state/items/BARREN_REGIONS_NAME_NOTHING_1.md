# BARREN_REGIONS_NAME_NOTHING_1 — the keep-empty test matches nothing for 10 of 22 regions

## what is wrong

`src/RimMandrake/Utils/ashkarr_settle.py`'s `BARREN_REGIONS` is the set the settlement
placer uses to keep ground EMPTY. Its own comment:

> `⛔ Nothing is ever placed in these. The night side and the seas are meant to be blank,`
> `and the owner asked for large areas of barrenness by name.`

MEASURED 2026-09-21 against the canonical save's `<features>` block
(`CANONICAL_ASHKARR_START_2026-09-12.rws`, **71 features, 0 unnamed**, parsed offline):
**12 of the 22 entries match a real feature. 10 match nothing at all.**

`The Frostbloom` · `The Deep Bloom` · `The Coldspore` · `The Crown Rot` · `The Last Scrub` ·
`The Cold Bloom` · `The High Rot` · `The Grayrot` · `The Shoulder` · `The Last Green`

## why it matters

🔑 **It fails OPEN.** A membership test against a name no feature carries does not error and
does not warn — it simply returns false, and the placer treats that ground as fair game. So
ten areas the owner asked by name to be left blank are, as far as the placer is concerned,
not protected at all.

⛔ **`ashkarr_settle.py` must not be run until this is resolved.** It writes settlements to
the planet.

## what is NOT established

⚠️ **Why** each of the ten is absent is UNMEASURED, and the answer differs per name. Three
readings, and this item does not choose between them:

- the region was renamed and the set was never updated — the sibling case is proven:
  `The Venom Wood` → `Fuelmere` and `The Ashen Waste` → `Ashen Wastes` were exactly this,
  and were corrected under `ASHKARR_PAINTER_NAMES_DIVERGED_1`;
- the region was never authored onto the planet at all, so the entry is aspirational;
- the name belongs to a biome or a settlement rather than a world feature, and the set is
  mixing two vocabularies.

## spec

1. Resolve each of the ten against the 71 live feature names — renamed, never-authored, or
   wrong vocabulary. Say which, per name.
2. Renamed → fix the literal. Never-authored → the owner decides whether the region should
   exist; ⛔ do not invent it.
3. 🔴 **Make the failure loud.** The set should be validated against the planet's feature
   names at run time, so an entry that matches nothing REFUSES rather than silently
   un-protecting ground. That guard is the real deliverable — the ten names are today's
   instance of it.

## Watch out

- 🔴 **Read feature names from the SAVE, not from `world/ASHKARR_WORLDMAP_tiles.csv`.** That
  CSV is a record exported 2026-09-12 and is not the planet; a live bridge edit after that
  date is invisible to it.
- ⚠️ The save's `<features>` element is NESTED (`<features><features><li>`), and a
  non-greedy regex to the FIRST `</features>` yields an unparseable fragment. Take the last
  close tag.
- ⚠️ 68 of the 71 features carry no leading article but **three do** — `The Abandoned Mines`,
  `The Breaks`, `The Verge`. Do not "normalise" articles blindly.

## criteria

Every `BARREN_REGIONS` entry names a feature that exists on the planet, and an entry that
does not makes the run REFUSE instead of quietly placing settlements.

## 🔴 RESOLVED 2026-09-21 — all 10 were RENAMED, none never-authored, none wrong-vocabulary

**Every one of the ten is a live region under a later name.** Traced through git history,
not guessed: `design/Jawa/worldbuilding/named_places_draft.md` commit `8770e19f3`
(2026-08-22, the "fiction review" polish that renamed 17 Rot/Bloom/Spore/Dew-clustered
names) gives the first hop for all ten; two of them took a second hop in commit
`2174503fe` (2026-09-08, "V19: rename 4 nightside labels to match rebanded terrain",
owner-approved). Every result below was then confirmed against the live planet's
`<features>` block (71 features, same instrument as this item's own MEASURED line).

| `BARREN_REGIONS` literal | hop 1 (2026-08-22 polish) | hop 2 (2026-09-08 V19) | live name |
|---|---|---|---|
| `The Frostbloom` | The Stillwood | — | `Stillwood` |
| `The Deep Bloom` | The Blindwood | — | `Blindwood` |
| `The Coldspore` | The Ashwood | — | `Ashwood` |
| `The Crown Rot` | The Capwood | — | `Capwood` |
| `The Last Scrub` | The Thornend | Frostvein | `Frostvein` |
| `The Cold Bloom` | The Frostcaps | — | `Frostcaps` |
| `The High Rot` | The Hanging Wood | — | `Hanging Wood` |
| `The Grayrot` | The Mould March | — | `Mould Marches` (pluralised, article-drop pass `e077bb6bb`) |
| `The Shoulder` | The Coldshelf | Sunshelf | `Sunshelf` |
| `The Last Green` | The Verge | — | `The Verge` (one of the 3 that keeps its article) |

`HELIX_BARREN_OK` (the Ascendant Helix's barren-region exemption, same file) carried six
of these same stale names — `The Cold Bloom`, `The Grayrot`, `The Shoulder`,
`The Last Green`, `The High Rot`, plus the already-live `Rimewall`/`Ashen Wastes` — so it
had the identical failure and was fixed the same way in the same change.

**Code fix:** `src/RimMandrake/Utils/ashkarr_settle.py` — both literal sets rewritten to
their live names (with a comment tracing the rename chain), and a new runtime guard,
`validate_barren_regions()` (reading feature names via `live_feature_names()`, straight
from `CANONICAL_ASHKARR_START_2026-09-12.rws`'s nested `<features><features><li>` block,
never the stale tiles CSV), called at the top of `main()` before anything is computed
against either set. Any future rename that isn't propagated now makes the run REFUSE by
name instead of silently un-protecting ground. Selftest:
`src/RimMandrake/Utils/selftest_ashkarr_settle.py` (9/9), including a negative control
that poisons a copy of the real set to prove the guard isn't vacuously green.

No entry needed the owner's call — there was no never-authored name and no
wrong-vocabulary name in this ten. `ashkarr_settle.py` remains blocked from running by
its own pre-existing, unrelated staleness gate (`--i-know-its-stale`, four rules
documented stale since 2026-08-24) — this item did not touch that gate and does not
clear it.

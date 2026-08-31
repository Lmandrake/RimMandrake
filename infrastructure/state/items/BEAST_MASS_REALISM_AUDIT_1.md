## verdict

**Vanilla-wide design choice, not a bug — nothing to fix in the mass formula
or in any individual authored def.** But the audit surfaced a real, separate
gap: the modded roster this campaign actually runs goes far past Core's
240 kg ceiling, and `RIMMANDRAKE_PITS_BUILD_1`'s tuning pass only measured
against Core. That finding is relayed there (see "pits question" below), not
resolved here — this item closes clean.

## data used

`design/Jawa/worldbuilding/data/beast_census.csv` (1,022 rows, frozen dump
`1742630eb6253187`) and `beast_roster.csv` (581 actively-spawnable
PawnKindDefs, 0 cut), both from the concurrent BENCH beast fan-out
(2026-08-31). Cross-checked against `mcp__rimsage__get_def_details` for
Elephant, Human and Muffalo (Core only — RimSage's live index does not carry
Alpha Animals / Star Wars Animal Collection / other third-party mods right
now, even though `ModsConfig.xml` lists 589 active mods; that's a RimSage
indexing gap, not a campaign mod-list gap. Core rows matched exactly:
Elephant `baseBodySize=4`, `statBases/Mass=60`; Human `baseBodySize=1`,
`statBases/Mass=60`; Muffalo `baseBodySize=2.4`, `statBases/Mass=60`).

## how "mass" actually works (the key mechanism)

The census's `mass` column is the raw `statBases/Mass` **base value**, not
the effective in-game mass. `StatDef Mass` carries `StatPart_BodySize` in its
`<parts>`, which multiplies that base by the pawn's `bodySize` at read time.
So:

```
effective mass (what GetStatValue(StatDefOf.Mass) returns) = base Mass × bodySize
```

Across all 1,022 census rows, **1,019 share the identical base value of 60**
(confirmed: only 3 defs override it — see below). So mass is not an
independently authored number per creature at all; it is a single global
constant (60) times whatever bodySize the def author picked. There is
structurally no such thing as "our beast masses are wrong" independent of
bodySize — bodySize is the only dial that exists.

`60 × bodySize` also explains the anchor: Human `bodySize=1.0` → 60 kg,
almost exactly a real adult human's ~62-70 kg. The constant 60 was clearly
chosen to make the human case realistic, not to make any other species
realistic.

## the compression curve (real kg vs in-game kg, Core creatures)

| creature | bodySize | game mass (60×bs) | rough real mass | ratio (game/real) |
|---|---|---|---|---|
| Rat | 0.20 | 12 kg | ~0.3 kg | **~40× too heavy** |
| Chicken | 0.30 | 18 kg | ~2.5 kg | ~7× too heavy |
| Cat | 0.32 | 19 kg | ~4.5 kg | ~4× too heavy |
| Fox | 0.55 | 33 kg | ~5 kg | ~7× too heavy |
| Wolf (Timber) | 0.85 | 51 kg | ~40 kg | ~1.3× (close) |
| **Human** | **1.00** | **60 kg** | **~62-70 kg** | **~1.0× (anchor)** |
| Pig | 1.70 | 102 kg | ~150-200 kg | ~0.6× (compressed) |
| Bear (Grizzly) | 2.15 | 129 kg | ~250 kg | ~0.5× (compressed) |
| Muffalo / Cow / Horse | 2.40 | 144 kg | 500-800 kg | ~0.2-0.3× (compressed) |
| Rhinoceros | 3.00 | 180 kg | ~1,800 kg | ~0.1× (compressed) |
| Elephant / Megasloth / Thrumbo | 4.00 | **240 kg** | ~4,000-6,000 kg | **~0.05× (~20× compressed)** |

The curve is **not** a flat percentage of real mass, and it isn't symmetric:
small animals are inflated (a rat outweighs a real house cat), mid-size
animals (dog/goat/sheep scale) land close to real, and large animals are
increasingly compressed the bigger they get — worst at the top, exactly
where the task's suspicion (240 kg elephant) pointed. The reason is
structural, not a per-species mistake: real terrestrial animal mass spans
almost 6 orders of magnitude (0.03–6,000 kg), and Core's `bodySize` band
spans only ~40× (0.1–4.0). RimWorld deliberately maps that whole real range
onto a narrow, game-legible band — because `bodySize` also drives hitbox,
health scale, food consumption and pathing, not mass alone — and mass just
rides along at a fixed 60×. This is exactly what the concurrent
`beast_normalization_spec.md` (Law 2) already concluded from the same
mechanism ("no independent mass defect to fix... recommended: no override");
this audit independently re-derives the same mechanism from real-world
comparison and confirms it holds.

**Verdict: vanilla's compression is a deliberate 15-year-shipped gameplay
convention (bodySize legibility over mass realism), applied uniformly. Not a
bug, not something to patch.**

## our own authored creatures — checked separately

We ship **zero** animal ThingDefs. All 41 distinct mod values across the
1,022-row census are third-party (Core, DLCs, Alpha Animals, Star Wars
Animal Collection, Megafauna, etc.) — confirmed by grep across `src/Jawa/`
and `src/RimMandrake/`, which turns up only droid/humanoid `PawnKindDefs`
(`Races_Families.xml`, `Races_KotOR.xml`, `Races_OuterRim.xml`,
`Races_JDS.xml`), never a beast race.

The **one** mass-touching patch we carry is
`src/Jawa/Jawa_Patches/Patches/Ikee_Tuning.xml` (AA_Eyeling → the Jawa pet
"Ikee"), which is one of the census's 3 non-60 overrides
(`base=20`, `bodySize=0.13`). It is internally consistent with vanilla's own
convention, not a deviation from it: original Eyeling was `base=60,
bodySize=0.4` (mass-per-bodySize ratio 150); the patch sets `base=20,
bodySize=0.13` (ratio ≈154) — the same ratio, deliberately preserved, per
the patch's own comment ("a third the size carries a third the mass. 60 ->
20"). **No authoring mistake found; our one deviation from vanilla's default
mass is arithmetically faithful to vanilla's own rule.**

## the pits question — real headroom the tuning pass missed

`RIMMANDRAKE_PITS_BUILD_1` tuned its "reinforced frame" tier down from 400 kg
to 220 kg because "the heaviest thing in **Core** is 240 kg" and 400 kg was
unreachable by any single vanilla creature. That statement is true for Core,
but **not true for the modded stack this campaign actually runs.**

Cross-referencing the full 581-row active (0 cut) spawnable roster against
the census's effective mass (`base Mass × bodySize`):

- **52 actively-spawnable creatures exceed Core's 240 kg ceiling**, several
  by a wide margin: `AA_Behemoth` (Alpha Animals) **1,920 kg**,
  `GR_ArchotechCentipede` **1,200 kg**, `GreaterKraytDragon` / `Horax` /
  `JungleRancor` / `WarWyrm` (all Star Wars Animal Collection) **900 kg**,
  `KraytDragon` **720 kg**, down through a long tail to 300 kg.
- A further ~31 roster entries sit at exactly 240 kg (other mods reusing the
  same `bodySize=4` convention as Elephant/Megasloth/Thrumbo).
- Several of the heaviest are weighted into **Ash'karr's own desert/arid
  biomes** — `GreaterKraytDragon` and `KraytDragon` both carry real spawn
  weight on `ExtremeDesert`/`Desert`/`AridShrubland`; `Ronto`, `Torton`,
  `Behemoth` (SW) and others likewise favor `AridShrubland`. These are not
  theoretical long-tail mods — they're built for the biome this campaign
  plays in.
- The mass-sum trigger mechanic itself is unaffected — anything ≥220 kg
  (alone or in a group) still springs the reinforced frame exactly as
  designed. Nothing "falls through." The gap is **granularity**: a 240 kg
  elephant and a 1,920 kg Behemoth currently read identically to the trap.
  Whether the pits want a further tier to distinguish ordinary megafauna
  from true titans (a Krayt Dragon shrugging off a trap sized for an
  elephant would be good Star Wars flavor) is a genuine open design call,
  not a bug — it belongs to `RIMMANDRAKE_PITS_BUILD_1`/BENCH, not to this
  audit. Relayed there via `rimflow note`.

## recommendation

1. **No rescale of the mass formula or any individual def.** The 60×bodySize
   convention is vanilla-wide, deliberate, and internally consistent —
   changing it would ripple into hauling, caravans and every other
   mass-consuming system for a compression the whole game already treats as
   normal (per `beast_normalization_spec.md` Law 2, independently
   corroborated here).
2. **No fix needed for our own content** — we author no animals, and our one
   mass-touching patch (Ikee) already follows vanilla's own rule correctly.
3. **Pits tier granularity is a live open question, not a defect** — handed
   to `RIMMANDRAKE_PITS_BUILD_1` as data (52 roster creatures 240-1,920 kg,
   several Ash'karr-biome-weighted) for the owner/BENCH to decide whether a
   tier above "reinforced frame" is worth adding.

Closing this item — the realism question it was filed to answer is
conclusively resolved.

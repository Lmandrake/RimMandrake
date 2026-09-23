# STONEBACK_BOKKA_ART_STANDARD_1 — is the bokka's art up to modern standards?

## the ask — a question, not an order

**Owner, 2026-09-22**, sheet note on the bokka row of the identity picker:
*"Arid biome approved, make sure our art is up to modern standards."*

🔑 He asked for a **judgement**, not a regeneration. Read it that way: look at the art, decide
whether it meets the bar the newer creatures set, and regenerate only if it does not. A regen
fired without looking spends a quota-limited job and throws away art that may be fine.

## what exists — MEASURED 2026-09-22

`RSW_Stoneback` (the bokka, bodySize 0.4, our port of Biomes! Caverns' `BMT_Stoneback`) has
**three facings of our own art**, unchanged since the port landed:

```
src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_Caverns/Things/Animal/Stoneback/
    Stoneback_south.png   22,481 bytes   2026-09-11
    Stoneback_east.png    19,480 bytes   2026-09-11
    Stoneback_north.png   19,638 bytes   2026-09-11
```

Its texPath is correctly ours (`swanimals/...`), not the donor's — unlike its former
namesake, `KORRUM_ART_REGEN_1`.

## spec

1. **Look at it** against the newer creature art in the same mod, and against the bar the
   `reading-rimworld-graphics` / `generating-rimworld-sprites` skills describe — resolution,
   legibility at RimWorld's on-map scale, facing coherence (the three facings are independent
   side-profiles, per `ARTPIPE_FACING_COHERENCE_1`), and whether it reads as a small arid
   burrowing reptile rather than a generic lizard.
2. **Before queuing anything**, search `infrastructure/artpipe/done/`, `_artsrc/`,
   `registry.jsonl` and any `Transient/*.decisions.json` for existing bokka/stoneback art —
   the standing rule, and it has already caught three plants that had finished art nobody
   wired.
3. Only if it falls short: queue a regen, and put the result in front of him rather than
   swapping it in silently (cosmetic changes need his permission — they can break animated
   faces).

## 🔴 VERDICT — 2026-09-23: it FAILS, and on identity before quality

**Judged by looking at the PNGs**, not by measuring them. Verdict: *regenerate* — but the reason is
not the expected one.

### 1. 🔴 The art depicts the WRONG ANIMAL — the real defect

The three `Stoneback_*.png` show a **legless brown mound with a single dot eye**: south a rounded
cone, east a low rock-like hump. No limbs, no tail, no claws.

⇒ **Our def is a clawed, tailed quadruped.** MEASURED from the def:

| field | value | what the art shows |
|---|---|---|
| `body` | `QuadrupedAnimalWithClawsTailAndJowl` | no legs, no tail |
| `tools` | **left claw**, **right claw** | no claws |
| `description` | *"longer back legs"*, lives underground | no legs at all |
| `baseBodySize` | 0.4 | — |

🔑 **This is donor art never re-authored at the port.** It is Biomes! Caverns' `BMT_Stoneback`, a
**stone-mimic** — which is precisely what the pictures show. The def was ported and relabelled
**bokka**; the art still depicts the donor's creature. ⇒ The `texPath` being correctly ours
(`swanimals/…`) is what hid it: the *path* is ours, the *pixels* are the donor's idea.

### 2. Style — flat cartoon against painterly rendered volume

Uniform heavy black outline, radial-gradient fill, dot eye — against current art in the same folder
tree (`ShatterjawBeetle/ShatterJaw_south.png`): segmented carapace, specular highlights,
articulated serrated limbs, real volume.

### 3. ⛔ Resolution is NOT a defect — an earlier reading of this was WRONG

🔴 **Do not regenerate this for resolution.** The tempting claim was *"5 of the 8 newest sprites are
512, so 256 is sub-standard"* — a real observation and a false inference. **MEASURED across the
mod's 363 `_south.png`:** canvas does not track recency (512's median drawSize is 1.7 against
256's 1.5, both spanning the range), and **for drawSize-1 creatures it is 16 files at 256 against
2 at 512**. The bokka is drawSize 1, so 256 is the convention, agreeing with the `drawSize × 128`
ceiling `fill_queue.py` itself warns on. 🔑 Caught only because the queue emitted that advisory —
the wrong number had already been written down as evidence.

## ✅ queued — 2026-09-23

Three jobs at **256×256**, drawsize 1, priority 120:
`infrastructure/artpipe/pending/RSW_Stoneback_{south,east,north}.json`, from
`infrastructure/artpipe/art_lists/bokka_art_standard_regen.csv`. The prompt leads on **legs, claws
and tail** and explicitly rules out a rock or boulder silhouette.

⚠️ **The artpipe daemon does not run on the Mac**, so nothing generates until the Desktop runs it.
⛔ **Do not swap the result in silently** — cosmetic changes need his permission, so the new art
goes in front of him beside the old.

### 🔴 the search trap this sat behind

Searching `registry.jsonl` for the bokka finds **six rows keyed `RSW_Stoneback`**, which reads as
"art already queued". ⛔ **They are the KORRUM's jobs under a recycled defName** — all stamped
`2026-09-20T16:51:43Z` and sourced to `DESERT_FAMILY_PORT_EXECUTION_1`, the korrum's port batch.
`STONEBACK_DEFNAME_COLLISION_1` re-keyed the *files* to `RSW_Korrum_*` **without writing a registry
event**, so the registry still names a creature that no longer owns that defName. ⇒ The standing
"check for existing art first" rule returns a **false positive** here; only the rows' timestamp and
source disambiguate. 🔑 A recycled defName makes art provenance unsearchable by name alone.

## verify

A stated verdict with the reason — kept, or regenerated with the old and new side by side.
⛔ Not "regenerated because the note said make sure": that is not what he asked.

- [x] Verdict stated with the reason, reached by looking at the art.
- [ ] New art put in front of him beside the old, once the Desktop daemon has run.
- [ ] Only then swapped in, with his permission.

## criteria

The bokka looks like it belongs beside the creatures we are making now.

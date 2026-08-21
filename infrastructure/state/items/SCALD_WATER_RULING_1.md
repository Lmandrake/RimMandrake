# SCALD_WATER_RULING_1 — the mechanism is solved; only the choice is left

## spec

⭐ **CHECK closed the question REP filed and did it properly — from source, not from the
statistic.** Everything below is its finding; this item exists only because the remainder
is a ruling, and REP does not rule. Read
`infrastructure/state/items/THE_SCALD_LOST_ITS_WATER_1.md` in full before choosing.

**The mechanism, one line of engine code:**

```
RimWorld/Planet/SurfaceTile.cs:28
public override bool WaterCovered => elevation <= 0f;
```

The Scald's 312 `Lake` tiles are authored at **+1411 m** — a crater lake inside a 2,050 m
rim, by design. RimWorld defines water as *elevation at or below zero*. ⇒ **The engine does
not consider the Scald to be water.** `world_lint`'s `lakesAboveSeaLevel: 312` was saying
exactly this all along, and the 6.71% vs 8.14% water gap is the same 312 tiles.

🔑 **The bill is much smaller than "one of three ruled seas is dry", and that is the useful
part.** CHECK enumerated every `WaterCovered` call site:

| real | one `RiverDelta` behaviour — 2 tiles — where a delta emptying into the Scald does not act as a mouth |
| cosmetic | a road draws across the Scald where a boat should be |
| moot | the local-map gensteps that would build it as dry rock: `Lake` is `canBuildBase: false`, so **a player can never land there** in normal play |
| none | the river and biome worldgen steps — they run only at worldgen and we author both directly |

**The three ways out, CHECK's words, unranked on purpose:**

1. **Accept it.** The design calls the Scald a *hypersaline pool*; brine over ground that
   plays as ground is arguably correct, and measurably costs almost nothing.
2. **Drop the 312 tiles to elevation ≤ 0.** Makes it real water; a caldera below sea level
   inside a 2,050 m rim is physically ordinary. ⚠️ `elev_m` feeds the relief renderer, so
   this must be **looked at** afterwards, not merely measured.
3. **Leave the elevation, move the two `RiverDelta` mutators** to mouths that empty into a
   real sea. Fixes the only material defect and touches nothing else.

⛔ **Do not reach for option 2 because it makes a number tidy.** CHECK's own warning: the
relief, the rain shadow, the Spine and the whole drainage story are computed from that
1411 m, and moving it re-rolls more than it repairs.

🔑 **This interacts with the remake.** The owner ruled 2026-08-21 that a remake is the
recovery path and that four things want to precede the next worldgen. If the answer is
option 2, it is a **paint** change and belongs in that batch — a remake would otherwise
carry the current elevations forward unchanged. Options 1 and 3 do not need a remake.

⚠️ **Escalate rather than choose if this reads as the owner's.** He has personally ruled on
every map question tonight — `Lake` staying, the two cut-then-painted biomes, the 40–57
ring — and option 2 changes how the planet looks. He is **AFK** and `MODE` is `afk`, so an
owner-needs item will be suppressed until he is back; that is the correct outcome if this
is his, not a reason to decide it for him.

## verify

- The chosen option is recorded **with its reason**, in `canon.yml` if it changes a stated
  fact, so nobody reopens this from the 6.71% statistic alone.
- Option 2 only: `jawa/world_stats` reads **8.14%** and `lakesAboveSeaLevel` reads **0**
  afterwards — and the owner looks at the relief around the Scald and does not call it a
  defect.
- Options 1 or 3 only: `lakesAboveSeaLevel: 312` is annotated in the lint as **expected**,
  so it stops presenting as an unfixed fault to every future reader.

## criteria

One ruling, written where the next reader will meet the symptom, and a lint that no longer
reports a design decision as a defect.

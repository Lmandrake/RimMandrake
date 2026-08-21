## spec
The owner observed, 2026-08-21, that after the repaint many world tiles could not be
clicked — *"almost as though they used to be mountains (and thus unclickable) but now
aren't... and retain that lock."*

The cause is documented in `jawa/world_commit`'s own contract:

> *"it cannot fix `Tile`'s OWN private caches (`hillinessLabelCached`, `cachedMaxTemp`,
> `cachedMinTemp`, `tmpSecondaryBiome`) — those have no reset method anywhere in RimWorld
> and clear only on reload."*

🔴 **THE GAP: the bridge cannot see it.** `JawaBenchWorldTools.cs:150-151` builds the row as

    hilliness    = t.hilliness.ToString(),
    hillinessInt = (int)t.hilliness,

Both come from the **raw field**. Neither reads `HillinessLabel`, which is the cached value
the UI actually uses. So `jawa/world_tile_get` reports the tile correctly **whether or not
the cache is stale**, and a readback that looks perfect is not evidence the tile is usable.

⇒ Today the only instrument for this is a human clicking tiles and reporting. That is the
opposite of what this seat is for, and it means a whole class of repaint damage is invisible
to every automated check we have.

⚠️ **Wider than hilliness.** `cachedMaxTemp` and `cachedMinTemp` have the same shape, so any
temperature repaint has the same blind spot, and `world_lint` cannot see it either.

## verify
A companion tool reports the CACHED value beside the raw one for a tile, so a divergence is
a number rather than an anecdote. The `rimbridge-companion` skill covers the pattern and the
edit→build→deploy→test cycle; the DLL lock is free whenever the game is down.

Then, on a world where hilliness has been repainted without a reload, the two must DISAGREE
on the tiles that changed — that disagreement is the whole finding. After a reload they must
agree again.

## criteria
- a `jawa/` call returns, per tile, the raw `hilliness` AND the cached `HillinessLabel`
  (and ideally `cachedMinTemp`/`cachedMaxTemp` beside `temperature`)
- on a freshly repainted world it reports a non-zero count of tiles where they disagree
- after a save and reload the count is **0**
- ⛔ it must not silently return the raw value twice — that is the defect being fixed, and it
  would look exactly like a pass

## notes
Filed by CHECK, 2026-08-21. ⚠️ Do NOT let this block the reload test — that test is the
owner clicking, and it works today. This item exists so the SECOND time we repaint a planet,
nobody has to ask a human whether the tiles feel right.

## spec
`src/RimMandrake/Utils/ashkarr_paint.py:76-77` reads:

> *"the docs had only 'the habitable ring is ~34-57 degrees of arc' and left it open"*

🔴 **The owner ruled the ring is 40–57 on 2026-08-21** (`canon.yml >
world.habitable_ring_arc`), and ⭐ **this comment is the entire reason 34–57 was ever
canon-provisional** — it was cited as evidence in four design files, all now corrected.
Leaving it is how the losing figure comes back.

**One comment, two lines.** Keep the sentence's history, correct its claim:

```python
# ⭐ THE PLAYER'S HOME. Sited 2026-08-19; the docs had only "the habitable ring
# is ~34-57 degrees of arc" and left it open. ⚠️ THAT FIGURE WAS OVERRULED
# 2026-08-21 — the ring is 40-57 (canon.yml > world.habitable_ring_arc). The
# siting below does NOT change: arc 56.9 is inside 57 either way.
```

⛔ **Do not move the home tile.** The Setdown stays at tile 2476, arc 56.9. It reads as
*"the outer edge of the ring"* under both figures, which is exactly why the siting was never
the thing in dispute — and why this comment was weak evidence for 34–57 in the first place.
⛔ **Do not change any number the script computes.** This is a comment, and nothing in the
painter branches on the ring bounds.

## verify
- `grep -n "34-57\|34–57" src/` returns only lines that also say overruled
- the painter still sites the home at tile **2476**, arc **56.9** — if that moves, the edit
  was wrong; stop and say so

## criteria
No file in the repo asserts a habitable ring of 34–57 as current.

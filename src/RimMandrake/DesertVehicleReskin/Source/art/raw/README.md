# raw/ — the accepted model outputs, before the chroma key

These three are the **unmodified generator output** for the three shipped sled
facings, on their `#00ff00` key. The cut-and-committed versions live one level up
in `../` and are what the build scripts actually use.

**Why keep both.** Image generation is **not reproducible** — the same prompt and
the same references return a different picture every time. So a cut PNG is the
only copy of that art, and if the chroma key ever needs redoing at a different
threshold, or a facing needs a tighter crop, these raws are the only way back to
the original pixels. Re-running the generator does not recover them; it makes
something else.

Rejected attempts are deliberately **not** kept: the south stagger, the north
front-view-with-a-snout and the two procedural polygon passes are all superseded,
and what they taught is in their commit messages rather than in 6 MB of PNG.

| file | facing | note |
|---|---|---|
| `sled_south_raw.png` | south | 2nd pass; 1st was staggered diagonally |
| `sled_north_raw.png` | north | 2nd pass; 1st drew a visible muzzle on a rear view |
| `sled_east_raw.png`  | east  | 1st pass, accepted |

_CREATE, 2026-08-13 — committed at cutover, because `/tmp` is tmpfs and this is
exactly how the v4 sled art was lost eight hours earlier._

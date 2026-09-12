# NONDIV4_TEXTURE_FIX_1 — pad the textures RimWorld refuses to compress

From RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1 (2026-09-12, MEASURED): 1,578 loaded PNGs
have a dimension not divisible by 4, so `ModContentLoader` keeps them RGBA32 at
4 B/px — 2.69 GB where DXT5 would cost 0.67 GB. **~2.0 GB reclaimable, visually
lossless (pad, don't scale).**

## spec
- Start with OUR OWN mods: 190 MB of the waste is ours, 181 MB in
  `src/RimStarWars/Patches` textures — pad each offender's canvas to the next
  %4 dimension (transparent padding; texPath and silhouette unchanged —
  generating-rimworld-sprites validator applies), redeploy, and verify in-game
  art is unshifted (offsets/drawSizes can encode the old canvas).
- Census tool and offender list: the audit report's method section
  (`Transient/rimworld_memory_audit_2026-09-12.md` — shelf life! copy the
  offender list into this item or a committed data file before it ages out).
- Workshop mods' offenders are a second phase: retexture-on-absorption
  precedent, owner rules which are worth it.

## verify
Re-run the header census: 0 non-%4 textures in our own mods; RSS delta on the
next full load recorded MEASURED (expect roughly −0.2 GB from our share alone).

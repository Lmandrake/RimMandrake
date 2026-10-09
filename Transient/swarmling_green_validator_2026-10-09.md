# Swarmling green v2 east/north validator rejects (2026-10-09)

Verdict (a): legitimate miss, not a mismatch. Canvas was 256x256 on job and reference. The renders
(`D:\Luke\dev\_artpipe\_artsrc\miasma_swarmling_green_v2_{east,north}\`) are the right pose but the
abdomen sac and body came out larger: east 213x133 vs reference 200x127 (+6%); north 112x200 vs 106x192.
validate_sprite.py was not loosened.

Action: v2 east/north moved to `_withdrawn`. Filed v3 east/north (`Transient/swarmling_green_v3_rows_2026-10-09.json`)
with recolour-only, same-scale, same-bounding-box wording; owner_note verbatim. v2 south passed and stays.
If v3 also fails the same way, the fix is a downscale of the accepted render, not another prompt.

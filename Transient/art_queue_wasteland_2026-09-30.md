# Wasteland enrichment art queue, 2026-09-30

Search of done/, _artsrc/, pending/, active/, failed/, _withdrawn/, art_lists/, registry.jsonl, art_status.json and Transient/*.decisions.json (6704 files, sanity probe "korrum" found in 13) found no prior art or ruling for any of the 7 subjects. The only "waste cask" hit is the warcasket suit bay `done/RM_CaskBay.json`, a different object.

Art list: `D:\Luke\dev\Rimworld\infrastructure\artpipe\art_lists\wasteland_enrichment_2026-09-30.csv` (9 jobs, 7 subjects; the bay is 3 facings).

| subject | job id | kind |
|---|---|---|
| waste cask item | RM_WasteCask | transparent sprite 256 |
| sealed cask bay (RM_WasteCaskBay) | RM_WasteCaskBay_south/east/north | transparent building 768x512 |
| tipping pad marker (RM_WasteTippingPad) | RM_WasteTippingPad | transparent 256 |
| Middenshell track | RM_MiddenshellTrack | opaque tiling 1024 |
| Middenshell edge scar | RM_MiddenshellEdgeScar | opaque tiling 1024 |
| hot footprint filth | RM_Filth_MiddenshellFootprint | transparent decal 256 |
| shell-flake filth | RM_Filth_MiddenshellFlakes | transparent decal 256 |

Notes: defs read from origin/main (not on this worktree branch). Terrain uses an opaque hex background per the lanternstoneterrain_v1 precedent. Wiring finished art into defs/texPaths is not done here (the daemon does not wire). Terrain tint defs (0.52,0.48,0.40 / 0.30,0.30,0.24) multiply the texture, so art is painted mid-value.

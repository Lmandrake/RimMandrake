# Feverwood regen — 2026-10-07 (BENCH helper)

Source: `Transient/biome_ffar/feverwood_sheet_2026-10-05.decisions.json` (human rows = those with `at`: 38 of 44, 16 redo; re-read before filing, unchanged — savedAt 21:26:39, writeCount 128).
Method copied from `miasma_regen.md`. Built by `build_feverwood_regen_jobs.py` → `feverwood_regen_jobs.json` (68 rows → **94 jobs**).

## Status
- [x] decisions read, rows classified
- [x] canon entries read (fambaa, gelagrub); census Feverwood rows read (only those two are on his ruled rows)
- [x] existing-art search (`artpipe_state.py find`, sanity probe `korrum` = 21 hits)
- [x] jobs filed at priority 0, ids `regen_fw_*` so they sort after every `miasma_*` job at equal priority
- [x] daemon pid 441 (`artpiped.py -N 5`) running; queue positions **67–160** of 172 pending (Miasma 1–66, 5 Miasma active; 12 others at 100 behind)

## 🔴 Found: "priority 0" was silently filed as 100
`fill_queue.py` read `int(row.get("priority") or 100)` — 0 is falsy, so the whole Miasma "priority 0" wave was filed at **100**. Fixed (blank/absent → 100, explicit 0 kept; `selftest_artpipe.py` passes). The 66 still-pending Miasma jobs were rewritten in place to priority 0 (relative order unchanged; duplicate check against active/done: none).

## Jobs filed (priority 0, item BIOME_FLORAFAUNA_ART_REVIEW_1, owner notes verbatim in `owner_note` + prompt lead)
Canon (canon image attached as `canon_reference`, never `reference`; `canon` folds Visual brief + Must show into style_notes):
- **RSW_Fambaa**: `regen_fw_canon_fambaa_v1` (3, 1024px, drawSize 8). Canon `fambaa`, first image `wookieepedia_fieldguide.jpg` (the yellow-green painted plate). His note (yellow with green spots, long forward neck) wins over the entry's "brown-to-olive". His picks D/E/F (swim, juvenile, juvenile swim) are kept, so no swim job; D east is a second guidance image.
- **RSW_Gelagrub**: `regen_fw_canon_gelagrub_v1` (3, 512px, drawSize 4). Canon `gelagrub`, `wookieepedia_canon_1.webp`; Must-show 6 (rider scale) is `canon_na` because the scale comes from drawSize. Engine limits: "not yet assessed".

Invented fauna:
- **RM_Brathek**: `regen_fw_brathek_v2` (3, 256): wood-boring rasping larva, rasp plate instead of a drill, peg legs kept. No anchor, so the drill head does not carry over.
- **RM_Chellow**: `regen_fw_chellow_v2_south` (edit of `feverwood_chellow_south` with the beak removed) → `regen_fw_chellow_v2` east+north derived from it; plus `regen_fw_chellow_flying_{1..4}_v1` (12 jobs, whole-body directional frames from the new east).
- **RM_Drommath**: `regen_fw_drommath_v2` east+north derived from his liked `feverwood_drommath_south`, with no wood drawn.
- **RM_Murrelith**: `regen_fw_murrelith_v2_{east,south,north}`, per-facing edits of `feverwood_murrelith_*` to give translucent rainbow streamers; plus `regen_fw_murrelith_flying_{1..4}_v1` (12 jobs).
- **RM_Thornbug**: `regen_fw_thornbug_v2` (3, 512, drawSize 3.0 for "three cells wide"); the column A render is attached as concept guidance.

Plants, redo (3 realistic variants a/b/c each, prompted from the def description, column-B render attached as concept unless noted):
- RM_Ammeth (512, "twice as big", no anchor: A is a placeholder and B was purged) · RM_Cistrel · RM_Corvath · RM_Skimmel · RM_Sodderel · RM_Thulvane (512) · RM_Tullick · RM_Varnoth (512) · RM_Verrow · RM_Wanlith (rest 256)

Plants, chosen render kept, 2 realistic variants b/c anchored on it:
- Plant_HydenockTree_Wild (A, 512) · Plant_JoganTree_Wild (B, 512) · RM_Claithe (B) · RM_GiantLeaf (A) · RM_Halquin (B) · RM_Maulith (B) · RM_Nubrith (B) · RM_Ossagrel (A) · RM_Plennith (B) · RM_Seepril (B)
- Where he chose A but A is the flat-circle placeholder (Halquin, Maulith, Nubrith, Plennith, Seepril), the anchor is the B render he flagged in `variants`.

## Not filed (no art asked) — def/description work for BENCH
- Description rewrites: RM_Brathek (his "Redo description"), RM_Grolth ("Redo description based on image"), RM_Silloch ("regenerate description"), VFEI2_Megathrips ("Redo name and description."), RM_Skellick ("This creature is a thief.").
- Def changes his notes imply: RM_Thornbug drawSize to about 3.0; RM_Ammeth visualSizeRange doubled. Flight frames need `flyingAnimationFramePathPrefix` + count 4 on the Chellow/Murrelith PawnKindDefs. Fambaa art lives under `FambaaArtOverride`.
- Holds and cuts: Gorrameth, Lommerel, Nemmel, Skethral, Thavrik. B-pick rows with no note: Ollareth, Vaulm.
- Hydenock and jogan have no canon-library entry, so their variants anchor on the chosen render and are not canon builds.

## Already generated (did not replace the new jobs)
- `fambaa_v1` (east/north/south, done): the pre-library Fambaa, which his redo supersedes.
- `hydenocktree_v1`, `jogantree_v1`, `gapall_Plant_*_Wild_v1`: the sheet's existing tree renders.
- `giantleaf_v1`: the in-game giant leaf (column A).
- No finished art at all for gelagrub (0 hits). Every other subject's only renders are the `feverwood_*` jobs already on the sheet.

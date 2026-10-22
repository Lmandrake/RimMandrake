# facings_regen enact (BENCH art helper) — started 2026-10-21 ~23:55 PDT

Sheet: FOUNDRY Transient/biome_ffar/facings_regen_picks (2026-10-18), owner saved 23:48.
Decisions copied to bench Transient/biome_ffar/ (same name, .decisions.json).

## Step 1 — picks durable
- [x] copy foundry -> bench decisions; commit; publish — bd6dd7229847

## Step 2 — rows
- [x] RSW_Lothcat_f A — DONE: A was already live; enact --apply ingested keep ruling; fresh `art.py status` LIVE shas == snapshot col A (east 1d245186f819 north aef4042fcc14 south ef565249bb04)
- [x] RSW_OpeeSeaKiller A — DONE: A was already live; enact --apply ingested keep ruling; fresh `art.py status` LIVE shas == snapshot col A (E 7129d149b2cf N 8b4495b85a11 S 35d8b9a9b81e W 1b8f445b7dc5)
- [x] RSW_TeeMuss A — DONE: A was already live; enact --apply ingested keep ruling; fresh `art.py status` LIVE shas == snapshot col A (E 6a35577644c2 N da6687130a13 S b50fc8e9e16e)
- [ ] RSW_Strill A (already live, keep ingested) + SOUTH: artpipe job facreg2_strill_south_v1_south derive_from enact_e3474b0c_strill_v1_east (= A east sha ec565bbff9c2). RENDERING. Flip pick D = live Strill_Flying_ (no change).
- [ ] RSW_Varactyl_m redo — enact --hold (so enact's own redo, which would carry the rejected art as reference, was NOT filed); artpipe jobs facreg2_varactyl_m_v1_{east master, south+north derive_from east}, canon=varactyl + canon_1 image, owner_note verbatim. RENDERING
- [ ] RSW_Whisperbird A+B — north = B installed 279ac237c3ff (ef8cec0cad2b replaces 512px owl e6f8baecbe4a); S/E stay A. FLYING: rebuilt with flyer_cutout (still-body plate + wing layers) from the A+B grounded art as masters; config src/RimMandrake/Utils/art/flyer_cutout_sets/Whisperbird_modern.json; frames D:\ClaudeWork\rimmandrake\scratch\whisperbird_modern_flight\out. flier_body_stabilize: S/E/N LOCKED, exported-PNG body IDENTICAL, wings FLAPS. Registered as artpipe _artsrc whisperbird_modern_flying_{1..4}_{facing} (no done/ record, no daemon involvement) + backfill artpipe. NOT installed: goes to round-2 sheet. Offline only, no live flight test. Shared prefix: RSW_ScrapNestBird draws the same frames.
- [x] RSW_Yobshrimp A+B — DONE 279ac237c3ff: north = B (f5d5871467a1, art.py install --owner-said); S/E/W stay A. Note: A's west is a different-looking isopod side view from A's east; kept since he said A+B.
- [ ] followed notes cleared

## Step 3 — round-2 sheet facings_regen_round2
- [ ] built / gate / deliver / freshness / served URL

## Step 4 — audit

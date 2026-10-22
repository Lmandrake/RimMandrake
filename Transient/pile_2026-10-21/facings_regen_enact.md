# facings_regen enact (BENCH art helper) — started 2026-10-21 ~23:55 PDT

Sheet: FOUNDRY Transient/biome_ffar/facings_regen_picks (2026-10-18), owner saved 23:48.
Decisions copied to bench Transient/biome_ffar/ (same name, .decisions.json).

## Step 1 — picks durable
- [x] copy foundry -> bench decisions; commit; publish — bd6dd7229847

## Step 2 — rows
- [x] RSW_Lothcat_f A — DONE: A was already live; enact --apply ingested keep ruling; fresh `art.py status` LIVE shas == snapshot col A (east 1d245186f819 north aef4042fcc14 south ef565249bb04)
- [x] RSW_OpeeSeaKiller A — DONE: A was already live; enact --apply ingested keep ruling; fresh `art.py status` LIVE shas == snapshot col A (E 7129d149b2cf N 8b4495b85a11 S 35d8b9a9b81e W 1b8f445b7dc5)
- [x] RSW_TeeMuss A — DONE: A was already live; enact --apply ingested keep ruling; fresh `art.py status` LIVE shas == snapshot col A (E 6a35577644c2 N da6687130a13 S b50fc8e9e16e)
- [x] RSW_Strill — A live (keep ingested). SOUTH redone: artpipe facreg2_strill_south_v1_south (derive_from enact_e3474b0c_strill_v1_east = A east ec565bbff9c2; status ok, facts PASS; canon grader advisory 4/7: head carried higher than the low bulldog build). Compact front stance, legs close under the body. AWAITING HIS PICK on round 2 (col B). Flip D = live Strill_Flying_, unchanged.
- [ ] RSW_Varactyl_m — PENDING: HELD by coordinator (owner already approved Varactyls elsewhere: desert_sheet_2026-10-04 pick D 2026-10-08, VaractylV_E/F installed; coordinator tracing). Candidates rendered, NOT installed, NOT on round-2 sheet: D:\ClaudeWork\rimmandrake\artpipe\_artsrc\facreg2_varactyl_m_v1_{east,south,north} (north came out top-down) and facreg2_varactyl_m_north_v2_north. enact --hold kept; note not marked done.
- [x] RSW_Whisperbird A+B — north = B installed 279ac237c3ff (ef8cec0cad2b replaces 512px owl e6f8baecbe4a); S/E stay A. FLYING: rebuilt with flyer_cutout (still-body plate + wing layers) from the A+B grounded art as masters; config src/RimMandrake/Utils/art/flyer_cutout_sets/Whisperbird_modern.json (1336ffdd9803); frames D:\ClaudeWork\rimmandrake\scratch\whisperbird_modern_flight\out. flier_body_stabilize: S/E/N LOCKED, exported-PNG body IDENTICAL, wings FLAPS. Registered as artpipe _artsrc whisperbird_modern_flying_{1..4}_{facing} (no done/ record, no daemon) + backfill artpipe. NOT installed: AWAITING HIS PICK on round 2 (flip lane col C). Offline only, no live flight test. Shared prefix: RSW_ScrapNestBird draws the same frames.
- [x] RSW_Yobshrimp A+B — DONE 279ac237c3ff: north = B (f5d5871467a1, art.py install --owner-said); S/E/W stay A. Note: A's west is a different-looking isopod side view from A's east; kept since he said A+B.
- [x] followed notes cleared — enact --mark-done Strill/Whisperbird/Yobshrimp: moved to notes_followed; Varactyl note left open (held).

## Step 3 — round-2 sheet facings_regen_round2 (2026-10-22)
- [x] built by art_sheet.py --subjects (older renders hidden via --hide-sets, nothing purged); gate PASS; game_art deliver OK; sheet_freshness verify FRESH exit 0; served by serve_gated.py, http://localhost:44053/?t=fmT782QX4Bri3cqfETIM2A answers 200. Rows: Strill (B = new south), Whisperbird (C = modern flight frames; body and flip are separate lanes), Yobshrimp (A = the combined set, live).

## Step 4 — audit
6 of 7 rows DONE with evidence above; RSW_Varactyl_m PENDING (held by coordinator; candidates uninstalled).
